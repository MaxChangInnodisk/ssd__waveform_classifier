import json
import logging as log
import os
import shutil
from datetime import datetime

import cv2
import numpy as np

from .core.models import iClassification
from .utils import NpEncoder, import_module

# --------------------------------------------------------------------------------


# class DqeModel:
#     pass


# class DqeProcess:
#     pass


# class DqeInput:
#     pass


# class DqeOuput:
#     pass


# class DqeHistoryer:
#     pass


# --------------------------------------------------------------------------------


class DqeKeywordError(Exception):
    def __init__(self, message: str = "") -> None:
        self.message = message
        super().__init__(self.message)


class DqeConfigError(Exception):
    def __init__(self, message: str = "") -> None:
        self.message = message
        super().__init__(self.message)


# --------------------------------------------------------------------------------


class DqeProcess:
    def __init__(self, module_name: str = None, module_path: str = None) -> None:
        if None in [module_name, module_path]:
            print("Using default prcoess")
            self.module_name = "default"
            self.module_path = "default"
            return

        if not os.path.exists(module_path):
            raise FileNotFoundError(f"Ensure module_path is correct ! ({module_path}) ")

        self.module_name = module_name
        self.module_path = module_path
        self.module = import_module(module_name=module_name, module_path=module_path)

        if "process" not in dir(self.module):
            raise ImportError("Ensure your custom module has 'process' function.")

        # Replace process function
        self.process = self.module.process

    def process(self, frame: np.ndarray) -> np.ndarray:
        return frame

    def print_information(self):
        print("\n[DQE Process]")
        print("* name: ", self.module_name)
        print("* path: ", self.module_path)
        print("")

    def __call__(self, frame: np.ndarray) -> np.ndarray:
        return self.process(frame)


class DqeInput:
    def __init__(self, image_path: str, dqe_process: DqeProcess) -> None:
        self.path = self._check_file(image_path)

        (
            self.name,
            self.extension,
            self.serial_number,
            self.keyword,
            self.size,
            self.speed,
        ) = self._parse_from_name(os.path.basename(self.path))

        self.dqe_process = dqe_process

        self.buffer = self._get_buffer(self.path)

    def __default_process(
        self,
        frame: np.ndarray,
        region: list = [55, 116, 669, 428],  # noqa: B006
    ) -> np.ndarray:
        croped = frame[region[1] : region[3], region[0] : region[2]]
        gray = cv2.cvtColor(croped, cv2.COLOR_BGR2GRAY)
        return cv2.merge((gray, gray, gray))

    def _check_file(self, image_path: str) -> None:
        if not os.path.exists(image_path):
            raise FileNotFoundError(f"{self.__name__}: File not found. ({image_path})")
        if not os.path.isfile(image_path):
            raise TypeError(
                f"{self.__name__}: Except the path is a file. ({image_path})"
            )
        return image_path

    def _parse_from_name(self, image_name: str) -> tuple:
        image_name, ext = os.path.splitext(image_name)
        image_name = image_name.replace("_negative", "")
        image_name = image_name.replace("_positive", "")
        info = image_name.rsplit("_", 3)
        return (image_name, ext, info[0], info[1], info[2], info[3])

    def _get_buffer(self, image_path) -> np.ndarray:
        frame = cv2.imread(image_path)
        if frame is None:
            raise FileExistsError("File broken !!!")
        return self.dqe_process(frame)

    def print_information(self):
        print("\n[DQE Input]")
        print("* path: ", self.path)
        print("* name: ", self.name)
        print("* serial_number: ", self.serial_number)
        print("* keyword: ", self.keyword)
        print("* size: ", self.size)
        print("* speed: ", self.speed)
        print("")

    def print_all(self):
        self.dqe_process.print_information()
        self.print_information()

    def show(self, wait: int = 0) -> None:
        cv2.imshow(f"{self.name}", self.buffer)
        cv2.waitKey(wait)
        cv2.destroyWindow(f"{self.name}")

    def save_buffer(self, save_path: str) -> None:
        cv2.imwrite(save_path, self.buffer)

    def copy_file(self, copy_to: str) -> None:
        shutil.copy(self.path, copy_to)


class DqeOuput:
    def __init__(self, input: DqeInput = None, output: list = []) -> None:  # noqa: B006
        """DqeInput
        - Arguments
            - input: DqeInput
            - output: the inference results from iClassification ( iVIT-I )
        """
        self.update(input=input, output=output)

    def format_date(self, timestamp) -> str:
        return datetime.strftime(timestamp, "%y%m%d%H%M")

    def print_information(self):
        print("\n[DQE Output]")
        print("* date: ", self.date)
        print("* topk: ", self.length)
        print("* detail: ", self.output)
        print("")

    def print_all(self):
        self.input.print_all()
        self.print_information()

    def update(self, input: DqeInput = None, output: list = []):  # noqa: B006
        self.input = input
        self.output = output
        self.length = len(output)
        self.datetime = datetime.now()
        self.date = self.format_date(self.datetime)

    def dump_file(self, save_to: str):
        with open(save_to, "w") as jsonfile:
            json.dump(self.output, jsonfile, indent=4, cls=NpEncoder)


class DqeModel:
    def __init__(self, config: dict):
        self.config = config
        for _key in ["detect_data_keyword", "model_path", "label_path", "threshold"]:
            if config[_key] in [None, ""]:
                raise DqeConfigError("Got empty value in config.")

        self.name = os.path.splitext(os.path.basename(config["model_path"]))[0]
        self.keyword = config["detect_data_keyword"]

        self.model = iClassification(
            model_path=config["model_path"],
            label_path=config["label_path"],
            confidence_threshold=float(config["threshold"]),
            device=config.get("device", "CPU"),
        )
        self.labels = self.model.get_labels()
        self.input_shape = self.model.model.inputs[
            self.model.model.image_blob_name
        ].shape

        # For IO
        self.input, self.output = None, None

        log.info(
            f"Initialize DqeModel. NAME: {self.name}, KEYWORD: {self.keyword}, LABELS: {len(self.labels)}"
        )

    def check_keyword(func):
        def wrap(self, *args, **kwargs):
            input_key = args[0].keyword
            model_key = self.keyword
            if input_key != model_key:
                raise DqeKeywordError(
                    f"Keyword not match !!!! Input: {input_key}, Model: {model_key}"
                )
            return func(self, *args, **kwargs)

        return wrap

    @check_keyword
    def inference(self, input: DqeInput) -> DqeOuput:
        """Do inference with DqeInput and return DqeOutput"""
        results = self.model.inference(input.buffer)

        # Store results
        self.input = input
        self.output = DqeOuput(input=input, output=results)

    @check_keyword
    def inference_callback(self, input: DqeInput, output: DqeOuput):
        output.update(input=input, output=self.model.inference(input.buffer))

    def print_information(self):
        print("[DQE Model]")
        print("* name: ", self.name)
        print("* keyword: ", self.keyword)
        print("* labels: ", self.labels)


class DqeHistoryer:
    """Generate history"""

    pass


# --------------------------------------------------------------------------------


def _test_basic_usage():
    dprocess = DqeProcess()
    dinput = DqeInput(
        image_path=r"real_datarealdata1_R_XX_YY.png", dqe_process=dprocess
    )

    dinput.print_all()
    dinput.show()


def _test_custom_process():
    # dprocess = DqeProcess(
    #     module_name="process_with_substract",
    #     module_path=r"process\process_image_with_substract_Panda.py")
    dprocess = DqeProcess(
        module_name="process_with_substract", module_path=r"process\first_time.py"
    )

    di_new = DqeInput(
        image_path=r"real_data\realdata1_R_XX_YY.png", dqe_process=dprocess
    )

    di_new.print_all()
    di_new.show()


if __name__ == "__main__":
    r"""
    python ivit_i\io_handler.py
    """
    _test_basic_usage()
    _test_custom_process()
