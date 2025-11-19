# Ninja Dash - Build Guide

This guide explains how to build Ninja Dash executables for different environments using PyInstaller.

## Overview

The build system supports **three separate environments**, each with its own configuration and executable:

| Environment | Executable Name | Console | Debug Features | Use Case |
|-------------|----------------|---------|----------------|----------|
| **TEST** | `NinjaDash_TEST.exe` | ✅ Visible | ✅ Enabled | Development & debugging |
| **STAGING** | `NinjaDash_STAGING.exe` | ✅ Visible | ⚠️ Limited | QA testing |
| **PRODUCTION** | `NinjaDash.exe` | ❌ Hidden | ❌ Disabled | End-user distribution |

## Prerequisites

1. **Python 3.8+** installed
2. **Dependencies** - The build scripts will automatically check for and offer to install missing dependencies, including:
   - pygame (game engine)
   - pyinstaller (executable builder)
   - pytest (testing framework)

### Easy Setup

The easiest way to get started is to run the setup script:

**Windows:**
```batch
setup_dependencies.bat
```

**Linux/Mac:**
```bash
./setup_dependencies.sh
```

This will check for Python and pip, then install all required dependencies automatically.

### Manual Installation

If you prefer to install dependencies manually:
```bash
pip install -r requirements.txt
```

## Quick Start

**Note:** All build scripts automatically check for dependencies and will prompt you to install them if missing. You don't need to install anything manually unless you want to!

### Windows

**Build individual environment:**
```batch
build_scripts\build_test.bat      # Build TEST version
build_scripts\build_staging.bat   # Build STAGING version
build_scripts\build_prod.bat      # Build PRODUCTION version
```

**Build all environments at once:**
```batch
build_scripts\build_all.bat
```

### Linux/Mac

**Build individual environment:**
```bash
./build_scripts/build_test.sh      # Build TEST version
./build_scripts/build_staging.sh   # Build STAGING version
./build_scripts/build_prod.sh      # Build PRODUCTION version
```

**Build all environments at once:**
```bash
./build_scripts/build_all.sh
```

## Output Locations

After building, executables will be in the `dist/` directory:

```
dist/
├── NinjaDash_TEST/
│   ├── NinjaDash_TEST.exe       (Windows) or NinjaDash_TEST (Linux/Mac)
│   ├── .env_test                (Environment marker file)
│   └── ... (supporting files)
├── NinjaDash_STAGING/
│   ├── NinjaDash_STAGING.exe
│   ├── .env_staging
│   └── ...
└── NinjaDash_PROD/
    ├── NinjaDash.exe
    ├── .env_prod
    └── ...
```

## Environment Details

### TEST Environment

**Purpose:** Development and debugging

**Features:**
- Console window visible for logs
- Debug overlays enabled (grid, bounding boxes, FPS, coordinates)
- Fixed seed (12345) for reproducible testing
- Debug hotkeys enabled:
  - `F5` - Quick restart
  - `F6` - Skip level
  - `F7` - God mode toggle
  - `F8` - No-clip toggle
- Window title: "Ninja Dash [TEST]"

**Configuration:** `configs/config_test.py`

**Use when:**
- Testing new features
- Debugging issues
- Verifying game behavior with consistent RNG

---

### STAGING Environment

**Purpose:** QA testing and pre-release validation

**Features:**
- Console window visible for QA logs
- Production-like settings
- FPS counter visible (for performance testing)
- Limited debug hotkeys:
  - `F5` - Quick restart
  - `F6` - Skip level
- Random seed (like production)
- Window title: "Ninja Dash [STAGING]"

**Configuration:** `configs/config_staging.py`

**Use when:**
- Running QA test suites
- Performance testing
- Pre-release validation
- Testing in production-like conditions with logging

---

### PRODUCTION Environment

**Purpose:** End-user distribution

**Features:**
- Console window **hidden** (clean experience)
- All debug features **disabled**
- No debug overlays
- No debug hotkeys
- Random seed
- Optimized for performance
- Clean window title: "Ninja Dash"

**Configuration:** `configs/config_prod.py`

**Use when:**
- Creating builds for distribution
- Sharing with players
- Publishing releases

## Environment Detection

The game automatically detects which environment it's running in through this priority order:

1. **Command line argument:** `--env=test|staging|prod`
   ```bash
   # Run TEST environment directly (without building)
   python main.py --env=test
   ```

2. **Environment variable:** `NINJA_DASH_ENV`
   ```bash
   # Windows
   set NINJA_DASH_ENV=staging
   python main.py

   # Linux/Mac
   export NINJA_DASH_ENV=staging
   python main.py
   ```

3. **Marker file:** `.env_test`, `.env_staging`, or `.env_prod` (automatically created during build)

4. **Default:** Falls back to TEST environment in development

## Advanced Usage

### Customizing Environment Settings

Edit the configuration files in `configs/`:

- `configs/config_test.py` - TEST environment settings
- `configs/config_staging.py` - STAGING environment settings
- `configs/config_prod.py` - PRODUCTION environment settings

Each configuration file includes:
- Debug flags
- Logging levels
- Performance settings
- Feature flags
- Testing helpers
- Window settings

### Customizing Build Scripts

The PyInstaller spec files are in `build_scripts/`:

- `build_scripts/ninja_dash_test.spec`
- `build_scripts/ninja_dash_staging.spec`
- `build_scripts/ninja_dash_prod.spec`

You can customize:
- Data files to include
- Hidden imports
- Console visibility
- UPX compression
- Icon files (add your own)
- Version info

### Manual Build

If you prefer to run PyInstaller manually:

```bash
# Build TEST
pyinstaller build_scripts/ninja_dash_test.spec --clean --noconfirm

# Build STAGING
pyinstaller build_scripts/ninja_dash_staging.spec --clean --noconfirm

# Build PRODUCTION
pyinstaller build_scripts/ninja_dash_prod.spec --clean --noconfirm
```

## Troubleshooting

### "Module not found" errors

Add missing modules to the `hiddenimports` list in the `.spec` file:

```python
hiddenimports = [
    'pygame',
    'your_missing_module',
]
```

### Data files not included

Add data files to the `datas` list in the `.spec` file:

```python
datas = [
    (os.path.join(root_dir, 'path/to/files', '*.ext'), 'destination_folder'),
]
```

### Build fails with PyInstaller errors

1. Ensure PyInstaller is up to date:
   ```bash
   pip install --upgrade pyinstaller
   ```

2. Clean previous builds:
   ```bash
   # Windows
   rmdir /s /q build dist

   # Linux/Mac
   rm -rf build dist
   ```

3. Try building with verbose output:
   ```bash
   pyinstaller build_scripts/ninja_dash_test.spec --clean --noconfirm --log-level DEBUG
   ```

### Executable won't run

1. Check if antivirus is blocking the executable
2. Ensure all dependencies are included in the spec file
3. Test in the same environment type (use TEST build for debugging)
4. Check console output (TEST/STAGING builds show console)

## Distribution

### For End Users (PRODUCTION)

Distribute the entire `dist/NinjaDash_PROD/` folder:
- Contains the main executable
- Includes all required libraries
- No Python installation needed

**Recommended:**
1. Rename folder to just `NinjaDash`
2. Create a zip file for easy distribution
3. Include a README with controls and system requirements

### For QA Teams (STAGING)

Provide the `dist/NinjaDash_STAGING/` folder:
- Console visible for logging issues
- Similar to production but with QA tools
- Can skip levels for targeted testing

### For Developers (TEST)

Use the `dist/NinjaDash_TEST/` folder or run directly from source:
```bash
python main.py --env=test
```

## Best Practices

1. **Always test STAGING build before creating PRODUCTION build**
2. **Use TEST build for debugging** - it has all the debug tools
3. **Clean builds** when switching between environments
4. **Version your builds** - consider adding version numbers to folder names
5. **Test on target platforms** - build on each platform you plan to support

## File Structure

```
ninja_dash_prototype/
├── configs/                    # Environment configurations
│   ├── __init__.py
│   ├── config_test.py         # TEST settings
│   ├── config_staging.py      # STAGING settings
│   └── config_prod.py         # PRODUCTION settings
├── build_scripts/             # Build scripts and specs
│   ├── ninja_dash_test.spec   # PyInstaller spec for TEST
│   ├── ninja_dash_staging.spec
│   ├── ninja_dash_prod.spec
│   ├── build_test.bat/.sh     # Individual build scripts
│   ├── build_staging.bat/.sh
│   ├── build_prod.bat/.sh
│   └── build_all.bat/.sh      # Build all at once
├── env_config.py              # Environment detection & loader
├── main.py                    # Game entry point
├── settings.py                # Game settings (uses env_config)
└── BUILD_GUIDE.md            # This file
```

## Need Help?

- Check the console output for errors (TEST/STAGING builds)
- Review the environment configuration files in `configs/`
- Verify PyInstaller spec files in `build_scripts/`
- Test with `python main.py --env=test` before building

---

**Happy building! 🥷**
