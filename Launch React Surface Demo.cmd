@echo off
setlocal

cd /d "%~dp0react-surface"

where node >nul 2>nul
if errorlevel 1 (
    echo [ERROR] Node.js is not installed or not on PATH.
    echo Install Node.js LTS from https://nodejs.org and run this launcher again.
    echo.
    pause
    exit /b 1
)

where npm >nul 2>nul
if errorlevel 1 (
    echo [ERROR] npm is not available on PATH.
    echo Reinstall Node.js LTS from https://nodejs.org and run this launcher again.
    echo.
    pause
    exit /b 1
)

if not exist node_modules (
    echo [INFO] First launch detected. Installing dependencies...
    call npm ci
    if errorlevel 1 (
        echo [WARN] npm ci failed, retrying with npm install...
        call npm install
        if errorlevel 1 (
            echo [ERROR] Dependency installation failed.
            echo.
            pause
            exit /b 1
        )
    )
)

echo [INFO] Starting React Surface on http://localhost:5173 ...
call npm run dev -- --open

set "EXIT_CODE=%ERRORLEVEL%"
if not "%EXIT_CODE%"=="0" (
    echo.
    pause
)

exit /b %EXIT_CODE%
