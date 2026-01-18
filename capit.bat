@echo off
setlocal
title CapIT Environment Checker

:: 1. Check if Python is installed
python --version >nul 2>&1
if %errorlevel% neq 0 (
    echo [!] Python not found. Attempting to install via Winget...
    winget install -e --id Python.Python.3.11 --accept-source-agreements --accept-package-agreements
    
    :: Refresh Path for the current session
    refreshenv >nul 2>&1 || (
        echo [!] Please restart this batch file after the Python installation finishes.
        pause
        exit
    )
)

:: 2. Ensure Pip is up to date
echo [*] Checking Python environment...
python -m pip install --upgrade pip >nul 2>&1

:: 3. Install Core GUI dependencies (required to even show the window)
echo [*] Checking UI libraries...
python -m pip install customtkinter pillow ffmpeg-python >nul 2>&1

:: 4. Launch the application
echo [*] Starting CapIT...
python "%~dp0script.py"

if %errorlevel% neq 0 (
    echo.
    echo [!] CapIT crashed or encountered an error.
    pause
)