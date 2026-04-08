@echo off
setlocal
cd /d "%~dp0"
powershell -NoLogo -NoProfile -ExecutionPolicy Bypass -File "%~dp0scripts\launch_demo_windows.ps1"
set "EXIT_CODE=%ERRORLEVEL%"
if not "%EXIT_CODE%"=="0" if not "%EXIT_CODE%"=="130" (
    echo.
    pause
)
exit /b %EXIT_CODE%
