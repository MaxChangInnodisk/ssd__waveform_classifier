# Issue record

* SSL Certification
    ```bash
    pip config set global.trusted-host "pypi.org files.pythonhosted.org pypi.python.org"
    ```

* XY problem. ( [Ref](https://stackoverflow.com/questions/68922501/compiler-showing-struct-error-ushort-format-requires-0-number-0x7fff-2) )
    * Update date time.

* ImportError: DLL load failed while importing _pyopenvino: The specified module could not be found.
    * [Github Issue](https://github.com/openvinotoolkit/openvino/issues/18151)
    * Notice: Ensure you have already downloaded the Visual Studio Redistributable file (.exe).