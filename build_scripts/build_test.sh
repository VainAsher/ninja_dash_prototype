#!/bin/bash
# Build script for TESTING environment
# Creates NinjaDash_TEST executable with debug features enabled

echo "============================================"
echo "Building Ninja Dash - TESTING Build"
echo "============================================"
echo ""

# Clean previous build
echo "Cleaning previous TEST build..."
rm -rf build
rm -rf dist/NinjaDash_TEST

# Run PyInstaller with test spec
echo ""
echo "Running PyInstaller..."
pyinstaller build_scripts/ninja_dash_test.spec --clean --noconfirm

if [ $? -ne 0 ]; then
    echo ""
    echo "ERROR: Build failed!"
    exit 1
fi

echo ""
echo "============================================"
echo "Build completed successfully!"
echo "============================================"
echo "Output: dist/NinjaDash_TEST/"
echo "Executable: dist/NinjaDash_TEST/NinjaDash_TEST"
echo "============================================"
echo ""
