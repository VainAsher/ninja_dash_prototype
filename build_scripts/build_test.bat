@echo off
REM Build script for TESTING environment
REM Creates NinjaDash_TEST.exe with debug features enabled

echo ============================================
echo Building Ninja Dash - TESTING Build
echo ============================================
echo.

REM Clean previous build
echo Cleaning previous TEST build...
if exist build rmdir /s /q build
if exist dist\NinjaDash_TEST rmdir /s /q dist\NinjaDash_TEST

REM Run PyInstaller with test spec
echo.
echo Running PyInstaller...
pyinstaller build_scripts\ninja_dash_test.spec --clean --noconfirm

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
echo Output: dist\NinjaDash_TEST\
echo Executable: dist\NinjaDash_TEST\NinjaDash_TEST.exe
echo ============================================
echo.

pause
