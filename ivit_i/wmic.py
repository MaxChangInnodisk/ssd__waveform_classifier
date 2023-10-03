import os
import subprocess as sp
import json
import platform
import argparse

def ensure_win(func):
    def wrap(*args, **kwargs):
        assert platform.system() == "Windows", "Ensure the platform is Windows"
        return func(*args, **kwargs)
    return wrap

@ensure_win
def get_os_product():
    command = \
        "wmic /namespace:\\\\root\\microsoft\\windows\\storage path msft_disk WHERE \"BootFromDisk='true' and IsSystem='true'\" get model"
    p = sp.run(command, shell=True, capture_output=True, text=True)
    ret = p.stdout.replace('Model', '').strip()   
    return [ info.strip() for info in ret.split('\n') if info != "" ]

@ensure_win
def get_all_product():
    command = \
        "wmic diskdrive get Model"
    p = sp.run(command, shell=True, capture_output=True, text=True)
    ret = p.stdout.replace('Model', '').strip()
    return [ info.strip() for info in ret.split('\n') if info != "" ]

@ensure_win
def get_test_product():
    all_disk = get_all_product()
    os_disk = get_os_product()
    return list(set(all_disk) - set(os_disk))

def save_json_file(os_disk: list, test_disk: list, json_path: str="disk.json", write_mode:str ="w"):
    with open(json_path, write_mode) as json_file:
        json.dump({
            "os": os_disk,
            "test": test_disk
        }, json_file, indent=4)



def args_ext_check(fpath:str):
    choices = "json"
    if not fpath.endswith(choices):
        raise argparse.ArgumentTypeError("file doesn't end with one of {}".format(choices))
    return fpath

def build_args():
    parser = argparse.ArgumentParser()
    parser.add_argument("-p", "--path",
                        required=True, 
                        type=args_ext_check,
                        help="path to config.")
    return parser.parse_args()

def main(args):
    

    print("="*40)
    print("# CUSTOM WMIC PROGRAM. Created by Max")
    print("\n* Get all disks: ")
    all_disk = get_all_product()
    print(all_disk)

    print("\n* Get os disks: ")
    os_disk = get_os_product()
    print(os_disk)

    print("\n* Get testing disks")
    test_disk = get_test_product()
    print(test_disk)

    save_json_file(os_disk, test_disk, args.path)

    print("\nSaved json file -> ({})".format(args.path))    
    print("="*40)

    # input('Wait for leave ...')

if __name__ == "__main__":
    main(build_args())