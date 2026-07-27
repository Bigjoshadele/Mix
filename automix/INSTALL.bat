@echo off
setlocal enabledelayedexpansion
title AutoMix Installer
color 0E

set LOGFILE=%~dp0install_log.txt
echo AutoMix install log > "%LOGFILE%"

echo ============================================
echo   AutoMix Installer
echo ============================================
echo.
echo This builds a real standalone AutoMix.exe locally. It needs an
echo internet connection to download the audio libraries once.
echo.
echo Prefer not to install Python at all? See GETTING_THE_EXE.md for a
echo way to get a pre-built .exe via GitHub instead.
echo.

REM --- Check for Python ---
where python >nul 2>nul
if errorlevel 1 (
    echo [ERROR] Python was not found on this system.
    echo.
    echo Install Python 3.10, 3.11, 3.12, or 3.13 (64-bit^) from:
    echo   https://python.org/downloads/
    echo IMPORTANT: check "Add python.exe to PATH" during install.
    echo Then run this installer again.
    echo Python not found on PATH >> "%LOGFILE%"
    pause
    exit /b 1
)

REM --- Check architecture ---
for /f "delims=" %%a in ('python -c "import platform; print(platform.architecture()[0])"') do set PYARCH=%%a
echo Detected Python architecture: %PYARCH%
echo Python architecture: %PYARCH% >> "%LOGFILE%"
if not "%PYARCH%"=="64bit" (
    echo.
    echo [ERROR] Your Python is 32-bit ^(%PYARCH%^). AutoMix's audio
    echo libraries need 64-bit Python. Install it from:
    echo   https://python.org/downloads/  ^("Windows installer (64-bit)"^)
    pause
    exit /b 1
)

for /f "tokens=2 delims= " %%v in ('python --version 2^>^&1') do set PYFULLVER=%%v
echo Detected Python %PYFULLVER%
echo Python version: %PYFULLVER% >> "%LOGFILE%"
echo.

echo [1/5] Creating virtual environment...
python -m venv "%~dp0venv" >> "%LOGFILE%" 2>&1
if errorlevel 1 (
    echo [ERROR] Failed to create virtual environment. See install_log.txt
    pause
    exit /b 1
)

echo [2/5] Installing dependencies (downloads from PyPI, a few minutes)...
"%~dp0venv\Scripts\python.exe" -m pip install --upgrade pip -q >> "%LOGFILE%" 2>&1
"%~dp0venv\Scripts\pip.exe" install -q -r "%~dp0requirements.txt" >> "%LOGFILE%" 2>&1
"%~dp0venv\Scripts\pip.exe" install -q pyinstaller >> "%LOGFILE%" 2>&1
if errorlevel 1 (
    echo [ERROR] Dependency install failed. Check install_log.txt for details.
    pause
    exit /b 1
)

echo [3/5] Verifying everything actually imports...
"%~dp0venv\Scripts\python.exe" -c "import pedalboard, numpy, scipy, soundfile, pyloudnorm, tkinter; print('All imports OK')" >> "%LOGFILE%" 2>&1
if errorlevel 1 (
    echo.
    echo [ERROR] A required library failed to import. Most common cause:
    echo missing Microsoft Visual C++ Redistributable ^(x64^). Get it free:
    echo   https://aka.ms/vs/17/release/vc_redist.x64.exe
    echo.
    echo Full error is in install_log.txt - last few lines:
    echo.
    powershell -Command "Get-Content '%LOGFILE%' -Tail 8"
    pause
    exit /b 1
)
echo Verified OK.

echo [4/5] Building standalone AutoMix.exe...
"%~dp0venv\Scripts\pyinstaller.exe" --noconfirm --onefile --windowed ^
    --name AutoMix ^
    --icon "%~dp0assets\automix.ico" ^
    --add-data "%~dp0assets;assets" ^
    --distpath "%~dp0dist" ^
    --workpath "%~dp0build" ^
    --specpath "%~dp0" ^
    "%~dp0automix_gui.py" >> "%LOGFILE%" 2>&1

if not exist "%~dp0dist\AutoMix.exe" (
    echo [ERROR] Build failed - AutoMix.exe was not created. See install_log.txt
    pause
    exit /b 1
)

echo [5/5] Creating desktop shortcut...
set SCRIPT="%TEMP%\automix_shortcut.vbs"
echo Set oWS = WScript.CreateObject("WScript.Shell") > %SCRIPT%
echo sLinkFile = oWS.SpecialFolders("Desktop") ^& "\AutoMix.lnk" >> %SCRIPT%
echo Set oLink = oWS.CreateShortcut(sLinkFile) >> %SCRIPT%
echo oLink.TargetPath = "%~dp0dist\AutoMix.exe" >> %SCRIPT%
echo oLink.WorkingDirectory = "%~dp0dist" >> %SCRIPT%
echo oLink.IconLocation = "%~dp0assets\automix.ico" >> %SCRIPT%
echo oLink.Save >> %SCRIPT%
cscript /nologo %SCRIPT%
del %SCRIPT%

echo.
echo ============================================
echo   Install complete.
echo   AutoMix.exe is on your Desktop.
echo   Full log saved to install_log.txt
echo ============================================
echo.
echo If AutoMix.exe ever fails to open, check for automix_error.log
echo next to it - that will explain why.
pause
