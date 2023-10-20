@echo off
net session >nul 2>&1

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

Net use
pause