@echo off
setlocal
title CapIT Launcher (Backend)

:: 1. Check if Microsoft Store Python 3.13 is installed
powershell -command "Get-AppxPackage -Name '*PythonSoftwareFoundation.Python.3.13*'" | findstr "PackageFamilyName" >nul
if %errorlevel% neq 0 (
    echo [!] Microsoft Store Python 3.13 not found.
    echo [*] Installing via Microsoft Store ID...
    
    :: Using the specific Store Product ID for Python 3.13
    winget install --id 9PNRBTZXMB4Z --source msstore --accept-source-agreements --accept-package-agreements
    
    if %errorlevel% neq 0 (
        echo [!] Winget failed. Opening the Store page for manual install...
        start ms-windows-store://pdp/?ProductId=9PNRBTZXMB4Z
        echo [!] Please click 'Install' in the Store window, then restart this script.
        pause
        exit
    )
    
    echo [*] Installation finished. Waiting for Windows to register the path...
    timeout /t 5 >nul
)

:: 2. Point directly to the Store Execution Alias
set "PYTHON_EXE=%LOCALAPPDATA%\Microsoft\WindowsApps\python3.exe"

:: 3. Double-check the alias exists
if not exist "%PYTHON_EXE%" (
    echo [!] Python was installed but the "App Alias" is disabled.
    echo [*] Opening Settings... Please turn ON 'python3.exe' and restart this script.
    start ms-settings:appsfeatures-appexecutionaliases
    pause
    exit
)

:: 4. Upgrade Pip and Install Dependencies
echo [*] Environment found. Checking libraries...
"%PYTHON_EXE%" -m pip install --upgrade pip >nul 2>&1
"%PYTHON_EXE%" -m pip install customtkinter pillow >nul 2>&1

:: 5. Launch the application
echo [*] Starting CapIT...
echo [*] Keep this window open for the application to run.
"%PYTHON_EXE%" "%~dp0script.py"

if %errorlevel% neq 0 (
    echo.
    echo [!] CapIT encountered an error.
	echo [NOTE]	CapIT does not support Windows 10 and lower.
    pause
)