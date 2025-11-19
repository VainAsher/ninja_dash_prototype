@echo off
REM Quick development runner - runs game from source without building
REM Uses environment configuration system

REM Change to project root
cd /d "%~dp0"

echo ============================================
echo Ninja Dash - Development Mode
echo ============================================
echo.
echo Running from source (no build required)
echo Press Ctrl+C to stop
echo.

REM Check for Python
python --version >nul 2>&1
if %ERRORLEVEL% NEQ 0 (
    echo ERROR: Python is not installed!
    pause
    exit /b 1
)

REM Check for pygame
python -c "import pygame" >nul 2>&1
if %ERRORLEVEL% NEQ 0 (
    echo WARNING: pygame is not installed!
    echo.
    set /p INSTALL="Install dependencies? (Y/N): "
    if /i "%INSTALL%"=="Y" (
        pip install -r requirements.txt
    ) else (
        echo ERROR: Dependencies required to run game
        pause
        exit /b 1
    )
)

REM Run the game (defaults to TEST environment)
python main.py --env=test

pause
