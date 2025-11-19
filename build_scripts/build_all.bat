@echo off
REM Master build script - builds all three environments
REM TEST, STAGING, and PRODUCTION

echo ============================================
echo Building ALL Ninja Dash Environments
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

REM Build TEST
echo.
echo ============================================
echo Building TEST environment...
echo ============================================
pyinstaller build_scripts\ninja_dash_test.spec --clean --noconfirm
if %ERRORLEVEL% NEQ 0 (
    echo ERROR: TEST build failed!
    pause
    exit /b 1
)

REM Build STAGING
echo.
echo ============================================
echo Building STAGING environment...
echo ============================================
pyinstaller build_scripts\ninja_dash_staging.spec --clean --noconfirm
if %ERRORLEVEL% NEQ 0 (
    echo ERROR: STAGING build failed!
    pause
    exit /b 1
)

REM Build PRODUCTION
echo.
echo ============================================
echo Building PRODUCTION environment...
echo ============================================
pyinstaller build_scripts\ninja_dash_prod.spec --clean --noconfirm
if %ERRORLEVEL% NEQ 0 (
    echo ERROR: PRODUCTION build failed!
    pause
    exit /b 1
)

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
