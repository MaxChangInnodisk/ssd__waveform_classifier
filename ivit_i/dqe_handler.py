import cv2, sys, os, shutil, json, glob
import logging as log
from collections import defaultdict
from typing import Any, Tuple, Dict, Literal

try:
    from ivit_i.common import dqe_logger
    from ivit_i.utils import read_ini, get_data, check_dir, clean_dir, write_json, copy_file
    from ivit_i.dqe_io import DqeProcess, DqeInput, DqeOuput, DqeKeywordError, DqeConfigError, DqeModel
    from ivit_i.wmic import get_test_product

except:
    from common import dqe_logger
    from utils import read_ini, get_data, check_dir, clean_dir, write_json, copy_file
    from dqe_io import DqeProcess, DqeInput, DqeOuput, DqeKeywordError, DqeConfigError, DqeModel
    from wmic import get_test_product

# Global
RK          = "R"
WK          = "W"
POS         = "positive"
NEG         = "negative"
PASS        = "PASS"
FAIL        = "FAIL"
IMG_EXT     = ".jpg"
JSON_EXT    = ".json"

def comb_name(items: list = [], sep: str="_"):
    return sep.join(items)

# GT Helper
class DqeGT():
        
    def __init__(self) -> None:
        
        target_disks = get_test_product()
        if len(target_disks) > 1:
            raise RuntimeError("The program only support one testing disk.")
        
        self.ans = target_disks[0]

    def update_by_labels(self, labels: list) -> None:
        
        for label in labels:
            if label in self.ans: 
                self.ans = label
                break
        else:
            self.ans = os.path.join("OTHERS", f"{self.ans}")
        log.warning(f'Updated ground truth: {self.ans}')

    def compare(self, label: str) -> bool:
        return label == self.ans
    
# Mission

class DqeMission():

    def __init__(self, config: dict):
        
        # Get folder
        self.ret_dir = os.path.join(config["output"]["retrain_dir"], "retrain" )
        self.his_dir = os.path.join(config["output"]["history_dir"], "history" )
        self.cur_dir = os.path.join(config["output"]["current_dir"], "current" )
        clean_dir(self.cur_dir)

        # Get target disk
        self.GT = DqeGT()

        # Logger
        self.dlog = dqe_logger(log_folder=self.his_dir)

    def verify(self, models: dict):
        """
        outputs: {
            'R': {
                'input': DqeInput,
                'output': DqeOutput ( default is [] )
            },
            'W': {...}
        }
        """

        if RK not in models or WK not in models:
            raise KeyError(f"Ensure the models has two. {len(models)}")

        if [] in [ models[RK].output, models[WK].output ]:
            raise RuntimeError(
                f"Ensure the two outputs is available." ) 

        if models[RK].labels != models[WK].labels:
            raise ValueError(
                f"The model label is not similar. ( {len(models[RK].labels)} vs. {len(models[WK].labels)} )")

    def get_retrain_path(self, status: str, din: DqeInput, dout: DqeOuput) -> str:
        
        # Combine name
        fname = comb_name( [
            dout.date, din.serial_number, din.keyword, din.size, din.speed ] )

        # Combine directory
        order_dir = [ self.ret_dir, status, din.keyword, self.GT.ans ]
        trg_dir = os.path.join(*order_dir)
        if not os.path.exists(trg_dir): os.makedirs(trg_dir)
        # print(trg_dir, fname)
        return os.path.abspath(os.path.join(trg_dir, fname))

    def get_history_path(self, status: str, din: DqeInput, dout: DqeOuput) -> str:

        # Combine name
        fname = comb_name( [
            dout.date, din.serial_number, din.keyword, din.size, din.speed, status ] )

        # Combine directory
        order_dir = [ self.his_dir, self.GT.ans, comb_name([dout.date, din.serial_number]) ]
        trg_dir = os.path.join(*order_dir)
        if not os.path.exists(trg_dir): os.makedirs(trg_dir)
        # print(trg_dir, fname)
        return os.path.abspath(os.path.join(trg_dir, fname))

    def get_current_path(self, result: str, status: str, din: DqeInput, dout: DqeOuput) -> str:
        
        # Combine name
        fname = comb_name( [
            dout.date, din.serial_number, din.keyword, din.size, din.speed, status ] )

        # Combine directory
        tmp_dir = comb_name( [
            dout.date, din.serial_number, self.GT.ans, result ] )
        trg_dir = os.path.join(self.cur_dir, tmp_dir)
        if not os.path.exists(trg_dir): os.makedirs(trg_dir)
        # print(trg_dir, fname)
        return os.path.abspath(os.path.join(trg_dir, fname))

    def mission(self, models: Dict[str, DqeModel]) -> None:
        
        # Prepare
        self.verify(models)
        self.GT.update_by_labels(models[RK].labels)
        
        # Get result
        self.result = PASS \
            if self.GT.compare(models[RK].output.output[1]) \
                and self.GT.compare(models[WK].output.output[1]) \
                    else FAIL
        
        # Log out
        self.dlog.info("-------------------------"*2)
        self.dlog.info("[Basic]")
        new_date = [ models[RK].output.date[i:i+2] for i in range(0, len(models[RK].output.date),2) ]
        self.dlog.info("Date: {}".format('/'.join(new_date[0:3])+' '+':'.join(new_date[3:])))

        # Parsing
        for key, model in models.items():

            din, dout = model.input, model.output
            stats = POS if self.GT.compare(dout.output[0][1]) else NEG

            # File Handler
            re_name = self.get_retrain_path(status=stats, din=din, dout=dout)
            cu_name = self.get_current_path(result=self.result, status=stats, din=din, dout=dout)
            hi_name = self.get_history_path(status=stats, din=din, dout=dout)
            
            # Combine result
            saved_json = {
                "status": stats,
                "name": din.name,
                "detected": f"{dout.output[0][1]}",
                "ground_truth": self.GT.ans,
                "source_path": din.path,
                "retrain_path": re_name+IMG_EXT,
                "current_path": cu_name+IMG_EXT,
                "history_path": hi_name+IMG_EXT,
                "output": dout.output,
                "model": {
                    "name": model.name,
                    "labels": model.labels,
                    "input_shape": model.input_shape
                }
            }
            
            # Save Image ( or Copy ) and Json
            for name in [ re_name, cu_name, hi_name ]:
                copy_file(din.path, name+IMG_EXT)                
                write_json(saved_json, name+JSON_EXT)

            # Log out
            self.dlog.info("")
            self.dlog.info("[Results]")
            self.dlog.info("  - SN: {}".format(din.name.split('_')[0]))
            self.dlog.info("    - {}".format(din.keyword))
            self.dlog.info("      - InputName: {}".format(saved_json["name"]))
            self.dlog.info("      - InputPath: {}".format(saved_json["source_path"]))
            self.dlog.info("      - Status: {}".format(saved_json["status"]))
            self.dlog.info("      - GroundTruth: {}".format(saved_json["ground_truth"]))
            self.dlog.info("      - Detected: {}".format(saved_json["detected"]))
            self.dlog.info("      - Retrain: {}".format(saved_json["retrain_path"]))
            self.dlog.info("      - History: {}".format(saved_json["history_path"]))
            self.dlog.info("      - Current: {}".format(saved_json["current_path"]))
            self.dlog.info("      - AI_Detail: {}".format(saved_json["output"]))

             
    def __call__(self, models: Dict[str, DqeModel]) -> Any:
        return self.mission(models)


# Testing
def _test_model_usage():

    # Params
    config_path = r"config.ini"
    image_path = r"real_data\realdata1_R_XX_YY.png"

    # Prepare Input and Output
    dprocess = DqeProcess(
        module_name="process_with_substract", 
        module_path=r"process\process_image_with_substract_Panda.py")
    
    dinput = DqeInput(image_path=image_path, dqe_process=dprocess)
    doutput = DqeOuput()

    # Load Model
    config = read_ini(config_path)
    dread = DqeModel(config["model.read"])

    # Do inference
    dread.inference_callback(dinput, doutput)
    
    # Get Result
    doutput.print_all()

# Main
def main():
    config_path = r"config.ini"
    config = read_ini(config_path)

    # Get data, ensure the image_list's length is 2
    image_list = get_data(config["input"]["keyword"], config["input"]["input_dir"])
    assert len(image_list)==2, f"Expect two images in folder, but got {len(image_list)} !"

    # Prepare process funcitno
    # dprocess = DqeProcess(
    #     module_name="process", 
    #     module_path=config["process"]["module_path"])
    dprocess = DqeProcess(
        module_name="process_with_substract", 
        module_path=r"process\first_time.py")

    # Prepare Model and Output 
    models = defaultdict()

    # Init Mission and update GT
    dmission = DqeMission(config=config)
    
    # Load Model, Output, Mission
    keywords, config_keywords = [RK, WK ], ["read", "write"]
    for model_key, config_key in zip(keywords, config_keywords):
        try:
            models[model_key] = DqeModel(config[f"model.{config_key}"])
        except DqeConfigError as err:
            log.warning("The model setting is wrong. please check again")
            # raise err

    # Do inference
    for image in image_list:
        
        # Define DqeInput and get keyword
        try:
            din = DqeInput(image_path=image, dqe_process=dprocess)
        except:
            log.warning("The input image is wrong: {}".format(image))
            continue

        # Checking models is ready
        if not (din.keyword in models): continue

        # Inference
        models[din.keyword].inference(din)

    # DQE Mission: After Inference
    dmission(models)

if __name__ == "__main__":
    main()

"""
python ivit_i\dqe_handler.py 
"""

