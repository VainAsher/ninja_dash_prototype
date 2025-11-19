#!/bin/bash
# Master build script - builds all three environments
# TEST, STAGING, and PRODUCTION

echo "============================================"
echo "Building ALL Ninja Dash Environments"
echo "============================================"
echo ""
echo "This will build:"
echo "  1. TEST build (with debug features)"
echo "  2. STAGING build (for QA)"
echo "  3. PRODUCTION build (for distribution)"
echo ""
echo "This may take several minutes..."
echo ""

# Clean all previous builds
echo "Cleaning all previous builds..."
rm -rf build
rm -rf dist/NinjaDash_TEST
rm -rf dist/NinjaDash_STAGING
rm -rf dist/NinjaDash_PROD

# Build TEST
echo ""
echo "============================================"
echo "Building TEST environment..."
echo "============================================"
pyinstaller build_scripts/ninja_dash_test.spec --clean --noconfirm
if [ $? -ne 0 ]; then
    echo "ERROR: TEST build failed!"
    exit 1
fi

# Build STAGING
echo ""
echo "============================================"
echo "Building STAGING environment..."
echo "============================================"
pyinstaller build_scripts/ninja_dash_staging.spec --clean --noconfirm
if [ $? -ne 0 ]; then
    echo "ERROR: STAGING build failed!"
    exit 1
fi

# Build PRODUCTION
echo ""
echo "============================================"
echo "Building PRODUCTION environment..."
echo "============================================"
pyinstaller build_scripts/ninja_dash_prod.spec --clean --noconfirm
if [ $? -ne 0 ]; then
    echo "ERROR: PRODUCTION build failed!"
    exit 1
fi

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
