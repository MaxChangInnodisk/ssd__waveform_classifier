import os

ROOT = os.path.dirname(os.path.dirname(__file__))
print("ROOT: ", ROOT)

MAIN = "classifier.py"
NAME = os.path.splitext(MAIN)[0]
ICON = "classifier.ico"
DIST = "dist"
BUILD = "build"
SPEC = "*.spec"
REL = "release"

XML = rf"{ROOT}\openvino_env\Lib\site-packages\openvino\libs\plugins.xml"
LIB = rf"{ROOT}\openvino_env\Lib\site-packages\openvino\libs\*"

MAIN_PATH = os.path.join(ROOT, MAIN)
ICON_PATH = os.path.join(ROOT, os.path.join(REL, ICON))
EXEC_PATH = os.path.join(ROOT, os.path.join(DIST, f"{NAME}.exe"))

os.system(f'\
pyinstaller \
--name {NAME} \
--icon={ICON_PATH} \
--add-data "{LIB}:.\\openvino\\libs" \
--clean \
--hidden-import=codecs \
-F {MAIN_PATH}')

os.system(f"move {EXEC_PATH} {ROOT}")
# os.system(f"rmdir /s /q {BUILD} {DIST}")
# os.system(f"del {SPEC}")
