@echo off
REM Master build script - builds all three environments
REM TEST, STAGING, and PRODUCTION
REM Includes dependency checking and installation

echo ============================================
echo Building ALL Ninja Dash Environments
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

echo [OK] Python found:
python --version

REM Check for pip
pip --version >nul 2>&1
if %ERRORLEVEL% NEQ 0 (
    echo ERROR: pip is not installed or not in PATH!
    echo Please reinstall Python with pip enabled
    pause
    exit /b 1
)

echo [OK] pip found

REM Check for PyInstaller using Python module check (more reliable)
python -m PyInstaller --version >nul 2>&1
if %ERRORLEVEL% NEQ 0 (
    echo.
    echo WARNING: PyInstaller is not installed!
    echo.
    echo Would you like to install all required dependencies now?
    echo This will run: pip install -r requirements.txt
    echo.
    set /p INSTALL="Install dependencies? (Y/N): "

    if /i "%INSTALL%"=="Y" (
        echo.
        echo Installing dependencies...
        pip install -r requirements.txt

        if %ERRORLEVEL% NEQ 0 (
            echo ERROR: Failed to install dependencies!
            pause
            exit /b 1
        )

        echo.
        echo [OK] Dependencies installed successfully
        echo.

        REM Verify installation worked
        python -m PyInstaller --version >nul 2>&1
        if %ERRORLEVEL% NEQ 0 (
            echo ERROR: PyInstaller installation verification failed!
            echo Please try closing this window and running the script again.
            pause
            exit /b 1
        )

        echo [OK] PyInstaller verified and ready
    ) else (
        echo.
        echo ERROR: PyInstaller is required to build executables
        echo Please install it with: pip install -r requirements.txt
        pause
        exit /b 1
    )
) else (
    echo [OK] PyInstaller found
)

echo.
echo ============================================
echo Starting build process...
echo ============================================
echo.
echo This will build:
echo   1. TEST build (with debug features)
echo   2. STAGING build (for QA)
echo   3. PRODUCTION build (for distribution)
echo.
echo This may take several minutes...
echo.
pause

REM Clean all previous builds
echo Cleaning all previous builds...
if exist build rmdir /s /q build
if exist dist\NinjaDash_TEST rmdir /s /q dist\NinjaDash_TEST
if exist dist\NinjaDash_STAGING rmdir /s /q dist\NinjaDash_STAGING
if exist dist\NinjaDash_PROD rmdir /s /q dist\NinjaDash_PROD

REM Build TEST - using python -m PyInstaller for reliability
echo.
echo ============================================
echo [1/3] Building TEST environment...
echo ============================================
python -m PyInstaller build_scripts\ninja_dash_test.spec --clean --noconfirm
if %ERRORLEVEL% NEQ 0 (
    echo ERROR: TEST build failed!
    pause
    exit /b 1
)
echo [OK] TEST build completed

REM Build STAGING
echo.
echo ============================================
echo [2/3] Building STAGING environment...
echo ============================================
python -m PyInstaller build_scripts\ninja_dash_staging.spec --clean --noconfirm
if %ERRORLEVEL% NEQ 0 (
    echo ERROR: STAGING build failed!
    pause
    exit /b 1
)
echo [OK] STAGING build completed

REM Build PRODUCTION
echo.
echo ============================================
echo [3/3] Building PRODUCTION environment...
echo ============================================
python -m PyInstaller build_scripts\ninja_dash_prod.spec --clean --noconfirm
if %ERRORLEVEL% NEQ 0 (
    echo ERROR: PRODUCTION build failed!
    pause
    exit /b 1
)
echo [OK] PRODUCTION build completed

echo.
echo ============================================
echo ALL BUILDS COMPLETED SUCCESSFULLY!
echo ============================================
echo.
echo Built executables:
echo   TEST:       dist\NinjaDash_TEST\NinjaDash_TEST.exe
echo   STAGING:    dist\NinjaDash_STAGING\NinjaDash_STAGING.exe
echo   PRODUCTION: dist\NinjaDash_PROD\NinjaDash.exe
echo.
echo ============================================
echo.

pause
