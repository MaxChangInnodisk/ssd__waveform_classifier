from ivit_i.dqe_validator import SWCForValidator
from ivit_i.utils import read_ini


def main():
    config = read_ini(config_file="validator.ini")
    swcv = SWCForValidator(config=config)
    swcv.load()
    swcv.inference()


if __name__ == "__main__":
    main()
