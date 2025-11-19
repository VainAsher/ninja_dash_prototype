@echo off
REM Dependency installation script for Ninja Dash
REM Installs all required dependencies for building and running the game

echo ============================================
echo Ninja Dash - Dependency Setup
echo ============================================
echo.
echo This script will install all required dependencies:
echo   - pygame (game engine)
echo   - pyinstaller (executable builder)
echo   - pytest (testing framework)
echo.

REM Check for Python
python --version >nul 2>&1
if %ERRORLEVEL% NEQ 0 (
    echo ERROR: Python is not installed or not in PATH!
    echo.
    echo Please install Python 3.8+ from https://www.python.org/
    echo Make sure to check "Add Python to PATH" during installation.
    echo.
    pause
    exit /b 1
)

echo [OK] Python found:
python --version
echo.

REM Check for pip
pip --version >nul 2>&1
if %ERRORLEVEL% NEQ 0 (
    echo ERROR: pip is not installed or not in PATH!
    echo Please reinstall Python with pip enabled.
    echo.
    pause
    exit /b 1
)

echo [OK] pip found
echo.

REM Install dependencies
echo Installing dependencies from requirements.txt...
echo.
pip install -r requirements.txt

if %ERRORLEVEL% NEQ 0 (
    echo.
    echo ERROR: Failed to install dependencies!
    echo Please check the error messages above.
    echo.
    pause
    exit /b 1
)

echo.
echo ============================================
echo Dependencies installed successfully!
echo ============================================
echo.
echo You can now:
echo   1. Run the game: python main.py
echo   2. Build executables: build_scripts\build_all.bat
echo.
echo ============================================
echo.

pause
