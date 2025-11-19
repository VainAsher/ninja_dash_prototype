@echo off
REM Build script for PRODUCTION environment
REM Creates NinjaDash.exe for distribution

echo ============================================
echo Building Ninja Dash - PRODUCTION Build
echo ============================================
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
