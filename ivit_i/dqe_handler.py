import cv2, sys, os, shutil, json, glob
import logging as log
from collections import defaultdict

try:
    from ivit_i.core.models import iClassification
    from ivit_i.utils import read_ini, get_data, check_dir, clean_dir 
    from ivit_i.dqe_io import DqeProcess, DqeInput, DqeOuput, DqeKeywordError, DqeConfigError
    from ivit_i.wmic import get_test_product

except:
    from core.models import iClassification
    from utils import read_ini, get_data, check_dir, clean_dir
    from dqe_io import DqeProcess, DqeInput, DqeOuput, DqeKeywordError, DqeConfigError
    from wmic import get_test_product

# Global
POS = "positive"
NEG = "negative"
IMG_EXT = ".jpg"
JSON_EXT = ".json"

# Model
class DqeModel(object):

    def __init__(self, config: dict):

        self.config = config
        for _key in [ "detect_data_keyword", "model_path", "label_path", "threshold" ]:
            if config[_key] in [ None, "" ]:
                raise DqeConfigError("Got empty value in config.")

        self.name = os.path.splitext(os.path.basename(config["model_path"]))[0]
        self.keyword = config["detect_data_keyword"]

        self.model = iClassification(
            model_path = config["model_path"],
            label_path = config["label_path"],
            confidence_threshold = float(config["threshold"]),
            device = config.get("device", "CPU") )
        self.labels = self.model.get_labels()

        log.info("Initialize DqeModel. NAME: {}, KEYWORD: {}, LABELS: {}".format(
            self.name, self.keyword, len(self.labels)))

    def check_keyword(func):
        def wrap(self, *args, **kwargs):
            input_key = args[0].keyword
            model_key = self.keyword
            if (input_key != model_key):
                raise DqeKeywordError("Keyword not match !!!! Input: {}, Model: {}".format(
                    input_key, model_key
                ))
            return func(self, *args, **kwargs)
        return wrap

    @check_keyword
    def inference(self, input: DqeInput, output: DqeOuput) -> DqeOuput:
        """ Do inference with DqeInput and return DqeOutput """
        results = self.model.inference(input.buffer)
        return DqeOuput(input=input, output=results)
    
    @check_keyword
    def inference_callback(self, input: DqeInput, output: DqeOuput):
        output.update(
            input=input, 
            output=self.model.inference(input.buffer))
    
    def print_information(self):
        print('[DQE Model]')
        print('* name: ', self.name)
        print('* keyword: ', self.keyword)
        print('* labels: ', self.labels)

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
                log.info(f"Update GT: {self.GT} -> {label}")
                self.GT = label
                return

        temp_gt = self.GT
        self.GT = os.path.join("OTHERS", f"{temp_gt}")
        log.info(f"Update GT: {temp_gt} -> {self.GT}")

    def compare_GT(self, dout: DqeOuput):
        _, label, score = dout.output[0]
        stats = POS if label == self.GT else NEG
        log.info(f"Comparasion Result -> Label={label} and GT={self.GT}, Result={stats.upper()}")
        return stats

    def handle_files(self, dout: DqeOuput, stats:str):
                
        # Combine Route
        pure_name = self.rename(dout=dout)
        
        image_name = f"{pure_name}.jpg"
        ground_truth_dir = os.path.join(self.GT, dout.input.keyword)
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
        dout.dump_file(ht_image.replace(IMG_EXT, JSON_EXT))

        # Current
        cu_image = image_path_helper(self.current_dir)
        dout.input.copy_file(cu_image)
        dout.dump_file(cu_image.replace(IMG_EXT, JSON_EXT))

        # Update Results
        self.results[dout.input.name]["Retrain"] = re_image
        self.results[dout.input.name]["History"] = ht_image
        self.results[dout.input.name]["Current"] = cu_image

    def __call__(self, dout: DqeOuput):
        
        log.info(f"[DQE Mission] - {self.run_times+1}")
        stats = self.compare_GT(dout)

        # Update basic information
        self.results[dout.input.name] = defaultdict()
        self.results[dout.input.name]["input_path"] = dout.input.path
        self.results[dout.input.name]["detected"] = f"{dout.output[0][1]} {dout.output[0][2]}%"
        self.results[dout.input.name]["ground truth"] = self.GT
        self.results[dout.input.name]["status"] = stats
        self.results[dout.input.name]["details"] = dout.output
        
        # File
        self.handle_files(dout=dout, stats=stats)

        # Update running times
        self.run_times += 1

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
        missions[din.keyword](dout)

    # Summary Mission
    for key in missions.keys():
    
        missions[key].print_information()
        models[key].print_information()


if __name__ == "__main__":
    main()

"""
python ivit_i\dqe_handler.py 
"""

