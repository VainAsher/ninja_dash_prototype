#!/bin/bash
# Build script for STAGING environment
# Creates NinjaDash_STAGING executable for QA testing

echo "============================================"
echo "Building Ninja Dash - STAGING Build"
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

echo "[OK] Python found"

# Check for pip
if ! command -v pip3 &> /dev/null; then
    if ! command -v pip &> /dev/null; then
        echo "ERROR: pip is not installed or not in PATH!"
        exit 1
    fi
    PIP_CMD=pip
else
    PIP_CMD=pip3
fi

# Check for PyInstaller
if ! command -v pyinstaller &> /dev/null; then
    echo ""
    echo "WARNING: PyInstaller is not installed!"
    echo ""
    read -p "Install dependencies now? (y/n): " INSTALL

    if [[ "$INSTALL" =~ ^[Yy]$ ]]; then
        echo "Installing dependencies..."
        $PIP_CMD install -r requirements.txt
        if [ $? -ne 0 ]; then
            echo "ERROR: Failed to install dependencies!"
            exit 1
        fi
    else
        echo "ERROR: PyInstaller is required to build"
        exit 1
    fi
fi

echo "[OK] PyInstaller found"
echo ""

# Clean previous build
echo "Cleaning previous STAGING build..."
rm -rf build
rm -rf dist/NinjaDash_STAGING

# Run PyInstaller with staging spec
echo ""
echo "Running PyInstaller..."
pyinstaller build_scripts/ninja_dash_staging.spec --clean --noconfirm

if [ $? -ne 0 ]; then
    echo ""
    echo "ERROR: Build failed!"
    exit 1
fi

echo ""
echo "============================================"
echo "Build completed successfully!"
echo "============================================"
echo "Output: dist/NinjaDash_STAGING/"
echo "Executable: dist/NinjaDash_STAGING/NinjaDash_STAGING"
echo "============================================"
echo ""
