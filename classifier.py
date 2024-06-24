# -*- coding: UTF-8 -*-

import logging as log
import os
import subprocess as sp

from ivit_i import dqe_handler
from ivit_i.utils import (
    check_env,
    check_status,
    ensure_folder_not_exist,
    get_exec_cmd,
    read_ini,
)

VER = "1.0.0"
LOGO = rf"""

  ____     __        ______ 
 / ___|    \ \      / / ___|
 \___ \ ____\ \ /\ / / |    
  ___) |_____\ V  V /| |___ 
 |____/       \_/\_/  \____|

            ( v{VER} )

"""


def div(title: str):
    log.info("-" * 40)
    log.info(title)


def run_aida64(service: str, config: dict):
    status = check_status(service, config)
    log.info(f"SERVICE {service}: {'ON' if status else 'OFF'}.")
    if not status:
        return

    # Verify
    ensure_folder_not_exist(config["input"]["keyword"], config["input"]["input_dir"])

    # Move to target folder
    trg_folder = os.path.abspath(os.path.dirname(config[service]["exec"]))
    config[service]["exec"] = rf'.\{os.path.basename(config[service]["exec"])}'

    exec_cmd = get_exec_cmd(exec_key=service, config=config)

    exec_cmd = f"cd {trg_folder} && {exec_cmd}"
    sp.run(exec_cmd, shell=True)


def main(config_path=r"config.ini"):
    check_env()

    # Preparing
    print(LOGO)
    config = read_ini(config_path)

    # Init Model and Verify data

    # AIDA64
    div("# AIDA64")
    run_aida64(service="aida64", config=config)

    # Inference with iVIT
    div("# INFER")
    swc = dqe_handler.SWC(config)
    swc.load()
    swc.inference()


if __name__ == "__main__":
    try:
        main()

    except KeyboardInterrupt:
        log.warning("Detected KeyboardInterrupt")

    except Exception as e:
        log.exception(e)

    key = input("\n\nPress ANY to leave ...")
