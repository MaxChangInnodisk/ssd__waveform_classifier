import os

ROOT=os.path.dirname(os.path.dirname(__file__))
print("ROOT: ", ROOT)

MAIN="classifier.py"
NAME="classifier"
ICON="app.ico"
DIST="dist"
BUILD="build"
SPEC="*.spec"
REL="release"

XML=r"C:\Users\DQE\Desktop\ssd__waveform_classifier\openvino_env\Lib\site-packages\openvino\libs\plugins.xml"
LIB=r"C:\Users\DQE\Desktop\ssd__waveform_classifier\openvino_env\Lib\site-packages\openvino\libs\*"

MAIN_PATH=os.path.join(ROOT, MAIN)
ICON_PATH=os.path.join(ROOT, os.path.join(REL, ICON))
EXEC_PATH=os.path.join(ROOT, os.path.join(DIST, f"{NAME}.exe"))

os.system(f"\
pyinstaller \
--name {NAME} \
--icon={ICON_PATH} \
--add-data \"{LIB}:.\\openvino\\libs\" \
--clean \
-F {MAIN_PATH}")

os.system(f"move {EXEC_PATH} {ROOT}")
# os.system(f"rmdir /s /q {BUILD} {DIST}")
# os.system(f"del {SPEC}")