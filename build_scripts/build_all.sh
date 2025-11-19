#!/bin/bash
# Master build script - builds all three environments
# TEST, STAGING, and PRODUCTION
# Includes dependency checking and installation

echo "============================================"
echo "Building ALL Ninja Dash Environments"
echo "============================================"
echo ""

# Check for Python
if ! command -v python3 &> /dev/null; then
    if ! command -v python &> /dev/null; then
        echo "ERROR: Python is not installed or not in PATH!"
        echo "Please install Python 3.8+ from https://www.python.org/"
        exit 1
    fi
    PYTHON_CMD=python
else
    PYTHON_CMD=python3
fi

echo "[OK] Python found:"
$PYTHON_CMD --version

# Check for pip
if ! command -v pip3 &> /dev/null; then
    if ! command -v pip &> /dev/null; then
        echo "ERROR: pip is not installed or not in PATH!"
        echo "Please reinstall Python with pip enabled"
        exit 1
    fi
    PIP_CMD=pip
else
    PIP_CMD=pip3
fi

echo "[OK] pip found"

# Check for PyInstaller
if ! command -v pyinstaller &> /dev/null; then
    echo ""
    echo "WARNING: PyInstaller is not installed!"
    echo ""
    echo "Would you like to install all required dependencies now?"
    echo "This will run: $PIP_CMD install -r requirements.txt"
    echo ""
    read -p "Install dependencies? (y/n): " INSTALL

    if [[ "$INSTALL" =~ ^[Yy]$ ]]; then
        echo ""
        echo "Installing dependencies..."
        $PIP_CMD install -r requirements.txt

        if [ $? -ne 0 ]; then
            echo "ERROR: Failed to install dependencies!"
            exit 1
        fi

        echo ""
        echo "[OK] Dependencies installed successfully"
    else
        echo ""
        echo "ERROR: PyInstaller is required to build executables"
        echo "Please install it with: $PIP_CMD install -r requirements.txt"
        exit 1
    fi
else
    echo "[OK] PyInstaller found"

    # Check if requirements are up to date
    echo ""
    echo "Checking if all dependencies are installed..."
    $PIP_CMD install -r requirements.txt --dry-run &> /dev/null
    if [ $? -ne 0 ]; then
        echo ""
        echo "Some dependencies may be missing or outdated."
        read -p "Update dependencies? (y/n): " UPDATE

        if [[ "$UPDATE" =~ ^[Yy]$ ]]; then
            $PIP_CMD install -r requirements.txt
        fi
    fi
fi

echo ""
echo "============================================"
echo "Starting build process..."
echo "============================================"
echo ""
echo "This will build:"
echo "  1. TEST build (with debug features)"
echo "  2. STAGING build (for QA)"
echo "  3. PRODUCTION build (for distribution)"
echo ""
echo "This may take several minutes..."
echo ""
read -p "Press Enter to continue..."

# Clean all previous builds
echo "Cleaning all previous builds..."
rm -rf build
rm -rf dist/NinjaDash_TEST
rm -rf dist/NinjaDash_STAGING
rm -rf dist/NinjaDash_PROD

# Build TEST
echo ""
echo "============================================"
echo "[1/3] Building TEST environment..."
echo "============================================"
pyinstaller build_scripts/ninja_dash_test.spec --clean --noconfirm
if [ $? -ne 0 ]; then
    echo "ERROR: TEST build failed!"
    exit 1
fi
echo "[OK] TEST build completed"

# Build STAGING
echo ""
echo "============================================"
echo "[2/3] Building STAGING environment..."
echo "============================================"
pyinstaller build_scripts/ninja_dash_staging.spec --clean --noconfirm
if [ $? -ne 0 ]; then
    echo "ERROR: STAGING build failed!"
    exit 1
fi
echo "[OK] STAGING build completed"

# Build PRODUCTION
echo ""
echo "============================================"
echo "[3/3] Building PRODUCTION environment..."
echo "============================================"
pyinstaller build_scripts/ninja_dash_prod.spec --clean --noconfirm
if [ $? -ne 0 ]; then
    echo "ERROR: PRODUCTION build failed!"
    exit 1
fi
echo "[OK] PRODUCTION build completed"

echo ""
echo "============================================"
echo "ALL BUILDS COMPLETED SUCCESSFULLY!"
echo "============================================"
echo ""
echo "Built executables:"
echo "  TEST:       dist/NinjaDash_TEST/NinjaDash_TEST"
echo "  STAGING:    dist/NinjaDash_STAGING/NinjaDash_STAGING"
echo "  PRODUCTION: dist/NinjaDash_PROD/NinjaDash"
echo ""
echo "============================================"
echo ""
