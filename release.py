import os

MAIN_PY="classifier.py"
NAME="classifier"
ICON="author-max.ico"

os.system(f"pyinstaller --onefile {MAIN_PY} --name {NAME} --icon={ICON}")
os.system(f"move {os.path.join('dist', f'{NAME}.exe')} {os.path.abspath('.')}")
os.system(f"rmdir /s /q build dist")
os.system(f"del *.spec")