import logging as log
import subprocess as sp
from ivit_i.utils import check_dir, read_json

def get_exec_cmd(exec_key: str, config: dict) -> str:
    exec_info = config.get(exec_key)
    assert exec_info != None, f"Unexpect exec file key ... ({exec_key})"

    cmd = f"{exec_info['exec']} {exec_info['args']}"
    log.warning('Get execute command: {}'.format(cmd))
    return cmd

def check_status(service:str, config:dict):
    if service in config["service"]:
        return config["service"][service]
    return 0
    
def run_service(service:str, config:dict):
    if not check_status(service, config):
        print(f"Service {service} is off.")
        return

    try:
        cmd = get_exec_cmd( 
            exec_key=service,
            config=config)
        result = sp.run(cmd, shell=True)

    except KeyboardInterrupt:
        pass

def run_ivit():
    # Run docker
    try:
        exec_command = "docker run -it --rm -w \"/workspace\" -v D:\DQE:/workspace innodiskorg/ivit-i-intel:v1.1-runtime python3 new_detect.py"
        result = sp.run(exec_command, shell=True)
    except KeyboardInterrupt:
        pass

def main():
    config = read_json("config.json")

    # Exec
    run_service(service="aida64", config=config)
    run_service(service="wmic", config=config)
    
    run_ivit()
        
if __name__ == "__main__":
    main()