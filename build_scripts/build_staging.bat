@echo off
REM Build script for STAGING environment
REM Creates NinjaDash_STAGING.exe for QA testing

REM Change to project root directory (parent of build_scripts)
cd /d "%~dp0\.."

echo ============================================
echo Building Ninja Dash - STAGING Build
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

REM Check for PyInstaller using Python module check (more reliable)
python -m PyInstaller --version >nul 2>&1
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

        REM Verify installation
        python -m PyInstaller --version >nul 2>&1
        if %ERRORLEVEL% NEQ 0 (
            echo ERROR: PyInstaller installation verification failed!
            pause
            exit /b 1
        )
        echo [OK] Dependencies installed
    ) else (
        echo ERROR: PyInstaller is required to build
        pause
        exit /b 1
    )
)

echo [OK] PyInstaller found
echo.

REM Clean previous build
echo Cleaning previous STAGING build...
if exist build rmdir /s /q build
if exist dist\NinjaDash_STAGING.exe del /f /q dist\NinjaDash_STAGING.exe
if exist dist\.env_staging del /f /q dist\.env_staging

REM Run PyInstaller with staging spec - using python -m for reliability
echo.
echo Running PyInstaller...
python -m PyInstaller build_scripts\ninja_dash_staging.spec --clean --noconfirm

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
echo Single-file executable: dist\NinjaDash_STAGING.exe
echo.
echo This is a standalone executable that includes all dependencies.
echo Just distribute the .exe file - no folder needed!
echo ============================================
echo.

pause
