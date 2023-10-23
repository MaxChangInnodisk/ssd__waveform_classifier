# SSD Waveform Classifier ( S-WC )
Classify the SSD read/write waveform by using iVIT.
<table border="0">
 <tr>
    <td>

![Alt text](docs/figures/iVIT-T-Logo.png)
    </td>
    <td>

![Alt text](docs/figures/iVIT-I-Logo-B.png)
    </td>
 </tr>
</table>
 
# How to use?
*** Ensure all behavior execute with `Administrator`. *** 

1. Mount innodisk network device using [MapNetworkDrive.bat](./MapNetworkDrive.bat) 
    * NOTE: must execute file.
    * NOTE: check network drive is mounted using [CheckNetworkDrive.bat](./CheckNetworkDrive.bat).
1. Prepare AIDA64, Model, Process file.
1. Modify the path of each files in [`config.ini`](config.ini).
2. Launch [`classifier.exe`](classifier.exe).

![sample](./docs/figures/swc.jpg)

# Configuration

<details>
<summary>S-WC Configuration Sample</summary>
    
```INI
[aida64]
describe = The program that can generate the ssd waveform screenshot
enable = 0
exec = ..\aida64\autoConnectTool_aida64_v598_USBnonSupport_.exe
args =

[input]
describe = Input data folder
input_dir = C:\Users\DQE\Desktop\aida64
keyword = aida64v598

[output]
describe = The output directory
retrain_dir = R:\Temp\test
history_dir = R:\Temp\test
current_dir = .
logger = dqe-history.txt

[process]
describe = The image process
module_path = process\process_image_with_substract_Panda.py

[model.read]
describe = The read waveform model
model_path = model\read\AIDA64_CV2_BW_R_ALL.xml
label_path = model\read\classes.txt
threshold = 0.1
detect_data_keyword = R

[model.write]
describe = The write waveform model
model_path = model\write\IDA64_CV2_BW_W_ALL.xml
label_path = model\write\classes.txt
threshold = 0.1
detect_data_keyword = W
```

</details> 
<br>

# For Developer
* Prepare environment
    
    Using python and virtualenv to handle the project environment.
    1. Install `Python 3.8.10` ( [Click to download](https://www.python.org/ftp/python/3.8.10/python-3.8.10-amd64.exe) )
        <details>
        <summary>Notice: have to add Python3.8 to PATH ( Screenshot )</summary>
        
        ![py-installer](docs/figures/py-3.8.10-installer.jpg)
        
        </details> 
        
    2. Install [the Visual Studio Redistributable file.](https://pypi.org/project/openvino/)
        <details>
        <summary>C++ libraries are also required for the installation on Windows</summary>
        
        ![vs-redistributable-file](docs/figures/ov-ensure-install-plugin.jpg)
        
        </details> 
        
    3. Install OpenVINO with Virtualenv
        <details>
        <summary>Workflow</summary>
        
        ```bash
        # Create virtual environment
        python -m venv openvino_env
        # Launch environment
        openvino_env\\Scripts\\activate.bat
        # Install OpenVINO
        python -m pip install openvino==2022.3.0
        # Verify
        python -c "from openvino.runtime import Core; print(Core().available_devices)"
        ```
        </details> 
    4. Install another modules
        <details>
        <summary>Modules</summary>
        
        ```bash
        pip install opencv-python colorlog
        ```
        </details>

* Release

    Package python file to executable file by double click `Release.bat`.

