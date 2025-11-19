#!/bin/bash
# Build script for STAGING environment
# Creates NinjaDash_STAGING executable for QA testing

echo "============================================"
echo "Building Ninja Dash - STAGING Build"
echo "============================================"
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
