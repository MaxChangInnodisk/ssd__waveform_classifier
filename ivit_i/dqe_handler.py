import cv2, sys, os, shutil, json, glob
import logging as log
from collections import defaultdict

try:
    from ivit_i.utils import read_ini, get_data, check_dir, clean_dir, write_json
    from ivit_i.dqe_io import DqeProcess, DqeInput, DqeOuput, DqeKeywordError, DqeConfigError, DqeModel
    from ivit_i.wmic import get_test_product

except:
    from utils import read_ini, get_data, check_dir, clean_dir, write_json
    from dqe_io import DqeProcess, DqeInput, DqeOuput, DqeKeywordError, DqeConfigError, DqeModel
    from wmic import get_test_product

# Global
POS = "positive"
NEG = "negative"
IMG_EXT = ".jpg"
JSON_EXT = ".json"


# Mission
class DqeMission():

    def __init__(self, config: dict):
        
        # Get folder
        self.retrain_dir = os.path.join(config["output"]["retrain_dir"], "retrain" )
        self.history_dir = os.path.join(config["output"]["history_dir"], "history" )
        self.current_dir = os.path.join(config["output"]["current_dir"], "current" )
        clean_dir(self.current_dir)

        # Get target disk
        target_disks = get_test_product()
        if len(target_disks) > 1:
            raise RuntimeError("The program only support one testing disk.")
        self.GT = target_disks[0]

        # Summary
        self.run_times = 0
        self.results = defaultdict()
        self.temp_results = defaultdict()

    def rename(self, dout: DqeOuput):
        din = dout.input
        index, label, score = dout.output[0]
        return "{date}_{sn}_{rw}_{size}_{speed}_{label}_{score}".format(
            date = dout.date,
            sn = din.serial_number,
            rw = din.keyword,
            size = din.size,
            speed = din.speed,
            label = label,
            score = round(score*100)
        )
 
    def update_GT_by_labels(self, labels: list):
        for label in labels:
            if label in self.GT:
                self.GT = label
                return

        temp_gt = self.GT
        self.GT = os.path.join("OTHERS", f"{temp_gt}")

    def compare_GT(self, dout: DqeOuput):
        _, label, score = dout.output[0]
        stats = POS if label == self.GT else NEG
        return stats
    
    def dump_results(self, dout: DqeOuput):
        
        pass

    def handle_files(self, dout: DqeOuput, stats:str):
                
        # Combine Route
        pure_name = self.rename(dout=dout)
        
        image_name = f"{pure_name}.jpg"
        ground_truth_dir = os.path.join(dout.input.keyword, self.GT)
        status_dir = os.path.join(stats, ground_truth_dir)
        
        # Helper
        def image_path_helper(target: str, status_dir:str=status_dir, fname:str=image_name):
            return os.path.join( check_dir(os.path.join(target, status_dir)), fname )

        # Retrain
        re_image = image_path_helper(self.retrain_dir)
        dout.input.save_buffer(re_image)

        # History       
        ht_image = image_path_helper(self.history_dir)
        dout.input.copy_file(ht_image)

        # Current
        cu_image = image_path_helper(self.current_dir)
        dout.input.copy_file(cu_image)

        # Update Results
        self.temp_results["retrain"] = re_image
        self.temp_results["history"] = ht_image
        self.temp_results["current"] = cu_image

        # Dump file
        for _file in [ ht_image.replace(IMG_EXT, JSON_EXT), cu_image.replace(IMG_EXT, JSON_EXT)]:
            write_json(self.temp_results, _file)

    def __call__(self, dout: DqeOuput, dmodel: DqeModel= None):
        
        stats = self.compare_GT(dout)

        # Update basic information
        self.temp_results["input_path"] = dout.input.path
        self.temp_results["detected"] = f"{dout.output[0][1]} {round(dout.output[0][2]*100)}%"
        self.temp_results["ground truth"] = self.GT
        self.temp_results["status"] = stats
        self.temp_results["details"] = dout.output
        
        # Update model information
        if dmodel:
            self.temp_results["model"] = {
                "name": dmodel.name,
                "labels": dmodel.labels,
                "input": dmodel.input_shape
            }

        # File
        self.handle_files(dout=dout, stats=stats)

        # Update running times
        self.run_times += 1
        self.results[dout.input.name] = self.temp_results 

    def print_information(self):
        print('[DQE Results]')
        for fname, fresult in self.results.items():
            print(f"* {fname}")
            for key, val in fresult.items():
                print(f"\t* {key} = {val}")


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

    # Get data
    image_list = get_data(config["input"]["keyword"], config["input"]["input_dir"])

    # Prepare process funcitno
    # dprocess = DqeProcess(
    #     module_name="process", 
    #     module_path=config["process"]["module_path"])
    dprocess = DqeProcess(
        module_name="process_with_substract", 
        module_path=r"process\first_time.py")

    # Prepare Model and Output 
    models, outputs, missions = defaultdict(), defaultdict(), defaultdict()

    # Load Model, Output, Mission
    keywords, config_keywords = ["R", "W" ], ["read", "write"]
    for model_key, config_key in zip(keywords, config_keywords):
        try:
            models[model_key] = DqeModel(config[f"model.{config_key}"])
            outputs[model_key] = DqeOuput()    

            # Init Mission and update GT
            missions[model_key] = DqeMission(config=config)
            missions[model_key].update_GT_by_labels(models[model_key].labels)

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
        dout = outputs[din.keyword]
        models[din.keyword].inference_callback(din, dout)

        # DQE Mission: After Inference
        missions[din.keyword](dout, models[din.keyword])

    # Summary Mission
    for key in missions.keys():    
        missions[key].print_information()


if __name__ == "__main__":
    main()

"""
python ivit_i\dqe_handler.py 
"""

