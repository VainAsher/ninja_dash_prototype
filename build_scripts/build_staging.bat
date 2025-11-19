@echo off
REM Build script for STAGING environment
REM Creates NinjaDash_STAGING.exe for QA testing

echo ============================================
echo Building Ninja Dash - STAGING Build
echo ============================================
echo.

REM Clean previous build
echo Cleaning previous STAGING build...
if exist build rmdir /s /q build
if exist dist\NinjaDash_STAGING rmdir /s /q dist\NinjaDash_STAGING

REM Run PyInstaller with staging spec
echo.
echo Running PyInstaller...
pyinstaller build_scripts\ninja_dash_staging.spec --clean --noconfirm

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
echo Output: dist\NinjaDash_STAGING\
echo Executable: dist\NinjaDash_STAGING\NinjaDash_STAGING.exe
echo ============================================
echo.

pause
