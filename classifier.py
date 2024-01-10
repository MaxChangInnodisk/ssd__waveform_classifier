# -*- coding: UTF-8 -*-

import os
import logging as log
import subprocess as sp

from ivit_i import dqe_handler
from ivit_i.utils import check_dir, read_json, read_ini

import ctypes

VER = "1.0.0"
LOGO = f"""

  ____     __        ______ 
 / ___|    \ \      / / ___|
 \___ \ ____\ \ /\ / / |    
  ___) |_____\ V  V /| |___ 
 |____/       \_/\_/  \____|

            ( v{VER} )

"""

# 请求管理员权限运行cmd.exe
# ctypes.windll.shell32.ShellExecuteW(None, "runas", "cmd.exe", "/k", None, 1)
def is_admin():
    try:
        return ctypes.windll.shell32.IsUserAnAdmin()
    except:
        return False
    
assert is_admin(), "Ensure using Administrator ..."
    
def get_exec_cmd(exec_key: str, config: dict) -> str:
    
    exec_info = config[exec_key]
    assert exec_info != None, f"Unexpect exec file key ... ({exec_key})"

    cmd = f"{exec_info['exec']} {exec_info['args']}"
    log.debug('Get execute command: {}'.format(cmd))
    return cmd

def check_status(service:str, config:dict):
    return int(config[service]["enable"])

def run_service(service:str, config:dict, username: str=''):
    status = check_status(service, config)
    log.info('--------------------------------------------------------------------------------')
    log.info(f"SERVICE {service}: {'ON' if status else 'OFF'}.")
    log.debug('')

    if not status: return None

    try:
        # Move to target folder
        trg_folder = os.path.abspath(os.path.dirname(config[service]["exec"]))
        config[service]["exec"] = f'.\{os.path.basename(config[service]["exec"])}'

        exec_cmd = get_exec_cmd( 
            exec_key=service,
            config=config )
        
        exec_cmd = f"cd {trg_folder} && {exec_cmd}"
        sp.run(exec_cmd, shell=True)

    except KeyboardInterrupt:
        return None

def main():
    config = read_ini("config.ini")
    
    print(LOGO)
    # Exec
    run_service(service="aida64", config=config)

    try:
        # trg_folder = os.path.abspath(os.path.dirname(__file__))
        # exec_cmd = f"cd {trg_folder} && {config['ivit']['exec']}"
        # process = sp.Popen(exec_cmd, shell=True)
        # process.wait()
        dqe_handler.main()

    except Exception as e:
        log.exception(e)
            
    key = input("\n\nPress ANY to leave ...")

if __name__ == "__main__":
    main()