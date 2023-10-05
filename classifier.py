import logging as log
import subprocess as sp

from ivit_i import dqe_handler
from ivit_i.utils import check_dir, read_json, read_ini

def get_exec_cmd(exec_key: str, config: dict) -> str:
    
    exec_info = config[exec_key]
    assert exec_info != None, f"Unexpect exec file key ... ({exec_key})"

    cmd = f"{exec_info['exec']} {exec_info['args']}"
    log.debug('Get execute command: {}'.format(cmd))
    return cmd

def check_status(service:str, config:dict):
    return int(config[service]["enable"])

def run_service(service:str, config:dict):
    status = check_status(service, config)
    log.info('--------------------------------------------------------------------------------')
    log.info(f"SERVICE {service}: {'ON' if status else 'OFF'}.")
    log.debug('')

    if not status: return None

    try:
        cmd = get_exec_cmd( 
            exec_key=service,
            config=config)
        return sp.run(cmd, shell=True)

    except KeyboardInterrupt:
        return None

def main():
    config = read_ini("config.ini")
    # Exec
    run_service(service="aida64", config=config)    
    
    try:
        dqe_handler.main()
    except Exception as e:
        log.exception(e)
            
    key = input("\n\nPress ANY to leave ...")

if __name__ == "__main__":
    main()