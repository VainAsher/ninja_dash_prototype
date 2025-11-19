# -*- mode: python ; coding: utf-8 -*-
"""
PyInstaller spec file for TESTING build
- Console window visible
- Debug features enabled
- Fixed seed for reproducible testing
"""

import os
import sys
from PyInstaller.utils.hooks import collect_data_files, collect_submodules

block_cipher = None

# Get the project root directory
root_dir = os.path.abspath(os.path.join(SPECPATH, '..'))

# Data files to include
datas = [
    (os.path.join(root_dir, 'data', '*.json'), 'data'),
    (os.path.join(root_dir, 'configs', '*.py'), 'configs'),
]

# Hidden imports (packages not auto-detected)
hiddenimports = [
    'pygame',
    'configs.config_test',
    'configs.config_staging',
    'configs.config_prod',
]

a = Analysis(
    [os.path.join(root_dir, 'main.py')],
    pathex=[root_dir],
    binaries=[],
    datas=datas,
    hiddenimports=hiddenimports,
    hookspath=[],
    hooksconfig={},
    runtime_hooks=[],
    excludes=[],
    win_no_prefer_redirects=False,
    win_private_assemblies=False,
    cipher=block_cipher,
    noarchive=False,
)

pyz = PYZ(a.pure, a.zipped_data, cipher=block_cipher)

exe = EXE(
    pyz,
    a.scripts,
    [],
    exclude_binaries=True,
    name='NinjaDash_TEST',
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=True,
    console=True,  # Console visible for testing
    disable_windowed_traceback=False,
    argv_emulation=False,
    target_arch=None,
    codesign_identity=None,
    entitlements_file=None,
)

coll = COLLECT(
    exe,
    a.binaries,
    a.zipfiles,
    a.datas,
    strip=False,
    upx=True,
    upx_exclude=[],
    name='NinjaDash_TEST',
)

# Create environment marker file in the dist folder after collection
import shutil
marker_file = os.path.join(DISTPATH, 'NinjaDash_TEST', '.env_test')
os.makedirs(os.path.dirname(marker_file), exist_ok=True)
with open(marker_file, 'w') as f:
    f.write('test')
