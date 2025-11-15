@echo off
setlocal
REM Ninja Dash - Virtual Environment Setup for Windows
REM This script creates a virtual environment, installs dependencies, and runs the game

echo ========================================
echo     NINJA DASH - Virtual Environment
echo ========================================
echo.

REM Jump to the folder this BAT lives in
cd /d "%~dp0"

REM Check for Python using py launcher first, then python
where py >nul 2>nul && (set PY=py) || (set PY=python)

REM Check if venv exists
if not exist ".venv" (
    echo Creating virtual environment...
    %PY% -m venv .venv
    if errorlevel 1 (
        echo ERROR: Failed to create virtual environment
        pause
        exit /b 1
    )
    echo Virtual environment created successfully
) else (
    echo Virtual environment already exists
)

echo.
echo Activating virtual environment...
call .venv\Scripts\activate.bat

echo.
echo Installing/Updating dependencies...
python -m pip install --upgrade pip
python -m pip install -r requirements.txt

echo.
echo ========================================
echo Starting Ninja Dash...
echo ========================================
python main.py

if errorlevel 1 (
    echo.
    echo ERROR: Game failed to start
    echo Check that all files are present
)

pause
