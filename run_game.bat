@echo off
REM Ninja Dash - Direct Run Script for Windows
REM This script installs pygame and runs the game

echo ========================================
echo         NINJA DASH - Setup and Run
echo ========================================
echo.

REM Check if Python is installed
python --version >nul 2>&1
if errorlevel 1 (
    echo ERROR: Python is not installed or not in PATH
    echo Please install Python from python.org
    pause
    exit /b 1
)

echo Installing/Updating pygame...
python -m pip install --upgrade pip
python -m pip install pygame

echo.
echo Starting Ninja Dash...
echo ========================================
python main.py

if errorlevel 1 (
    echo.
    echo ERROR: Game failed to start
    echo Check that all files are present
)

pause
