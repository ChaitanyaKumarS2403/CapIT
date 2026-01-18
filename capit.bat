@echo off
setlocal EnableDelayedExpansion
title CapIT Universal Bootstrapper

:: 1. Check if Python is already in PATH
python --version >nul 2>&1
if %errorlevel% == 0 goto :CHECK_LIBS

echo [!] Python not found. Starting Universal Installer...

:: 2. Use PowerShell to install Python (Compatible with Win 7, 8, 10, 11)
powershell -NoProfile -ExecutionPolicy Bypass -Command ^
    "$winget = Get-Command winget -ErrorAction SilentlyContinue;" ^
    "if ($winget) {" ^
    "  Write-Host '[*] Found Winget. Installing Python...';" ^
    "  & winget install -e --id Python.Python.3.11 --accept-source-agreements --accept-package-agreements;" ^
    "} else {" ^
    "  Write-Host '[!] Winget not found. Downloading Python Installer...';" ^
    "  $url = 'https://www.python.org/ftp/python/3.11.5/python-3.11.5-amd64.exe';" ^
    "  $out = \"$env:TEMP\python_installer.exe\";" ^
    "  Invoke-WebRequest -Uri $url -OutFile $out;" ^
    "  Write-Host '[*] Running Installer...';" ^
    "  Start-Process -FilePath $out -ArgumentList '/quiet InstallAllUsers=1 PrependPath=1' -Wait;" ^
    "  Remove-Item $out;" ^
    "}"

:: 3. Refresh environment variables without restarting CMD
echo [*] Refreshing PATH...
for /f "tokens=*" %%i in ('powershell -command "[Environment]::GetEnvironmentVariable('PATH', 'Machine') + ';' + [Environment]::GetEnvironmentVariable('PATH', 'User')"') do set "PATH=%%i"

:: 4. Verify installation
python --version >nul 2>&1
if %errorlevel% neq 0 (
    echo [!] Python installation failed or PATH not updated.
    echo Please install Python manually from python.org and restart.
    pause
    exit
)

:CHECK_LIBS
echo [*] Ensuring GUI dependencies are installed...
:: We use 'python -m pip' to ensure we use the pip associated with the found python
python -m pip install --upgrade pip
python -m pip install customtkinter pillow ffmpeg-python openai-whisper

echo [*] Launching CapIT...
python "%~dp0script.py"
if %errorlevel% neq 0 pause