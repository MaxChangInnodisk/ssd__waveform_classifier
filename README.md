# SSD Waveform Classifier
Using iVIT to build a classifier that could classify SSD model name via wareform.

# Requriement
1. Install `Python 3.8.10` ( [Click to download](https://www.python.org/ftp/python/3.8.10/python-3.8.10-amd64.exe) )
    <details>
    <summary>Notice: have to add Python3.8 to PATH ( Screenshot )</summary>
    
    ![py-installer](docs/figures/py-3.8.10-installer.jpg)
    
    </details> 
    
2. Install [the Visual Studio Redistributable file.] (https://pypi.org/project/openvino/)
    <details>
    <summary>C++ libraries are also required for the installation on Windows</summary>
    
    ![vs-redistributable-file](docs/figures/ov-ensure-install-plugin.jpg)
    
    </details> 
    
3. Install OpenVINO via Virtualenv
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


# Test
```
cd Desktop\ssd__waveform_classifier
openvino_env\\Scripts\\activate.bat
python -c "from openvino.runtime import Core; print(Core().available_devices)"
```
