import subprocess as sp
import json
import argparse
from .utils import is_win

def ensure_win(func):
    """A decorator to ensure the os is windows"""
    def wrap(*args, **kwargs):
        is_win()
        return func(*args, **kwargs)
    return wrap

def get_name_from_ismart(idx):
    command = \
        r"iSMART_6.4.18\\iSMART.exe -d " + str(idx)
    p = sp.run(command, shell=True, capture_output=True, text=True)
    
    for line in p.stdout.split('\n'):
        if not 'Model Name' in line: continue
        return line.split(':', 1)[1].strip()
    raise RuntimeError('Can not find realmodel')

@ensure_win
def get_os_product():
    """
    wmic /namespace:\\root\microsoft\windows\storage path msft_disk WHERE "BootFromDisk='true' and IsSystem='true'" get Number
    """
    command = \
        "wmic /namespace:\\\\root\\microsoft\\windows\\storage path msft_disk WHERE \"BootFromDisk='true' and IsSystem='true'\" get Number"
    p = sp.run(command, shell=True, capture_output=True, text=True)
    return [ get_name_from_ismart(line.strip()) for line in p.stdout.split('\n')[1:] if line ] 

@ensure_win
def get_all_product():
    command = \
        "wmic diskdrive get Index"
    p = sp.run(command, shell=True, capture_output=True, text=True)
    return [ get_name_from_ismart(line.strip()) for line in p.stdout.split('\n')[1:] if line ]
    
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
    # main(build_args())
    print('ALL: ',get_all_product())
    print('OS: ',get_os_product())
    print('TEST: ',get_test_product())


"""
wmic /namespace:\\root\microsoft\windows\storage path msft_disk WHERE "BootFromDisk='true' and IsSystem='true'" get model
"""