@echo off
setlocal enabledelayedexpansion

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