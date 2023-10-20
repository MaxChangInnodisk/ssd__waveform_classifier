@echo off
setlocal enabledelayedexpansion

net session >nul 2>&1
if %errorLevel% == 0 (
    echo Administrator privileges detected.
) else (
    echo Requesting administrative privileges...
    goto getadmin
)
goto main

:getadmin
if exist "%temp%\getadmin.vbs" del "%temp%\getadmin.vbs"
echo Set UAC = CreateObject^("Shell.Application"^) > "%temp%\getadmin.vbs"
echo UAC.ShellExecute "%~s0", "", "", "runas", 1 >> "%temp%\getadmin.vbs"
"%temp%\getadmin.vbs"
exit /B

:main
echo Running with administrative privileges.
echo.

set "drive_letter=R:"
set "network_path=\\192.168.168.217\share"

set /p username=Enter your username:
echo.

set /p password=Enter your password:
echo.

net use %drive_letter% %network_path% /user:%username% %password%

if errorlevel 1 (
    echo Failed to map network drive.
) else (
    echo Network drive mapped successfully.
)

pause
endlocal