#!/usr/bin/env python3
"""
TestRail to Xray Migrator - Setup Check
Verifies that all dependencies are installed and ready
"""

import sys
import subprocess

def check_python_version():
    """Check if Python version is 3.7 or higher"""
    print("Checking Python version...")
    version = sys.version_info
    if version.major >= 3 and version.minor >= 7:
        print(f"✓ Python {version.major}.{version.minor}.{version.micro} (OK)")
        return True
    else:
        print(f"✗ Python {version.major}.{version.minor}.{version.micro} (Need 3.7+)")
        return False

def check_module(module_name, import_name=None):
    """Check if a Python module is installed"""
    if import_name is None:
        import_name = module_name
    
    try:
        __import__(import_name)
        print(f"✓ {module_name} is installed")
        return True
    except ImportError:
        print(f"✗ {module_name} is NOT installed")
        return False

def check_file(filename):
    """Check if a required file exists"""
    import os
    if os.path.exists(filename):
        print(f"✓ {filename} exists")
        return True
    else:
        print(f"✗ {filename} NOT FOUND")
        return False

def main():
    print("=" * 60)
    print("TestRail to Xray Migrator - Setup Check")
    print("=" * 60)
    print()
    
    all_good = True
    
    # Check Python version
    all_good = check_python_version() and all_good
    print()
    
    # Check required modules
    print("Checking required Python packages...")
    all_good = check_module("tkinter") and all_good
    all_good = check_module("requests") and all_good
    all_good = check_module("sqlite3") and all_good
    print()
    
    # Check required files
    print("Checking required files...")
    all_good = check_file("ui.py") and all_good
    all_good = check_file("importer.py") and all_good
    all_good = check_file("migrator.py") and all_good
    all_good = check_file("testrail.py") and all_good
    all_good = check_file("config.json") and all_good
    print()
    
    # Final result
    print("=" * 60)
    if all_good:
        print("✓ ALL CHECKS PASSED!")
        print()
        print("You're ready to run the application:")
        print("  python ui.py")
        print()
        print("Or use the launcher:")
        print("  Linux/Mac: ./start_gui.sh")
        print("  Windows:   start_gui.bat")
    else:
        print("✗ SOME CHECKS FAILED")
        print()
        print("Please fix the issues above before running.")
        print()
        print("To install missing packages:")
        print("  pip install -r requirements.txt")
    print("=" * 60)
    
    return 0 if all_good else 1

if __name__ == "__main__":
    sys.exit(main())
