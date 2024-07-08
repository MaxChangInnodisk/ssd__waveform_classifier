@echo off

rem 激活OpenVINO环境
call openvino_env\Scripts\activate.bat

rem 安装PyInstaller
python -m pip install pyinstaller

rem 执行python release命令
python release\classifier.py
python release\validator.py

rem 关闭OpenVINO环境
call openvino_env\Scripts\deactivate

rem 批处理文件执行完毕
echo All tasks completed.
pause
