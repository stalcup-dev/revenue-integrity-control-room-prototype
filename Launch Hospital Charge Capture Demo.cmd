@echo off
setlocal
cd /d "%~dp0"

set "MODE=%~1"
if /I "%MODE%"=="streamlit" goto run_streamlit
if /I "%MODE%"=="react" goto run_react

echo [INFO] Launch mode not specified. Defaulting to React Surface.
goto run_react

:run_react
if exist "%~dp0Launch React Surface Demo.cmd" (
    call "%~dp0Launch React Surface Demo.cmd"
    exit /b %ERRORLEVEL%
)

echo [ERROR] React launcher not found: "%~dp0Launch React Surface Demo.cmd"
echo.
pause
exit /b 1

:run_streamlit
powershell -NoLogo -NoProfile -ExecutionPolicy Bypass -File "%~dp0scripts\launch_demo_windows.ps1"
set "EXIT_CODE=%ERRORLEVEL%"
if not "%EXIT_CODE%"=="0" if not "%EXIT_CODE%"=="130" (
    echo.
    pause
)
exit /b %EXIT_CODE%
