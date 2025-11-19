@echo off
REM Build script for PRODUCTION environment
REM Creates NinjaDash.exe for distribution

echo ============================================
echo Building Ninja Dash - PRODUCTION Build
echo ============================================
echo.

REM Check for Python
python --version >nul 2>&1
if %ERRORLEVEL% NEQ 0 (
    echo ERROR: Python is not installed or not in PATH!
    echo Please install Python 3.8+ from https://www.python.org/
    pause
    exit /b 1
)

echo [OK] Python found

REM Check for pip
pip --version >nul 2>&1
if %ERRORLEVEL% NEQ 0 (
    echo ERROR: pip is not installed or not in PATH!
    pause
    exit /b 1
)

REM Check for PyInstaller
pyinstaller --version >nul 2>&1
if %ERRORLEVEL% NEQ 0 (
    echo.
    echo WARNING: PyInstaller is not installed!
    echo.
    set /p INSTALL="Install dependencies now? (Y/N): "

    if /i "%INSTALL%"=="Y" (
        echo Installing dependencies...
        pip install -r requirements.txt
        if %ERRORLEVEL% NEQ 0 (
            echo ERROR: Failed to install dependencies!
            pause
            exit /b 1
        )
    ) else (
        echo ERROR: PyInstaller is required to build
        pause
        exit /b 1
    )
)

echo [OK] PyInstaller found
echo.

REM Clean previous build
echo Cleaning previous PRODUCTION build...
if exist build rmdir /s /q build
if exist dist\NinjaDash_PROD rmdir /s /q dist\NinjaDash_PROD

REM Run PyInstaller with production spec
echo.
echo Running PyInstaller...
pyinstaller build_scripts\ninja_dash_prod.spec --clean --noconfirm

if %ERRORLEVEL% NEQ 0 (
    echo.
    echo ERROR: Build failed!
    pause
    exit /b 1
)

echo.
echo ============================================
echo Build completed successfully!
echo ============================================
echo Output: dist\NinjaDash_PROD\
echo Executable: dist\NinjaDash_PROD\NinjaDash.exe
echo ============================================
echo.
echo NOTE: This is the PRODUCTION build for distribution.
echo Console is hidden and all debug features are disabled.
echo.

pause
