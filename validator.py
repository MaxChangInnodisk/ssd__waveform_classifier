from ivit_i.dqe_validator import SWCForValidator
from ivit_i.utils import read_ini

VER = "1.1.0"
LOGO = rf"""

  ____     __        ______
 / ___|    \ \      / / ___|
 \___ \ ____\ \ /\ / / |
  ___) |_____\ V  V /| |___
 |____/       \_/\_/  \____|

            ( v{VER} )

"""


def main():
    print(LOGO)
    config = read_ini(config_file="validator.ini")
    swcv = SWCForValidator(config=config)
    swcv.load()
    swcv.inference()


if __name__ == "__main__":
    try:
        main()

    except KeyboardInterrupt:
        print("Detected KeyboardInterrupt")

    except Exception as e:
        print(e)

    key = input("\n\nPress ANY to leave ...")
