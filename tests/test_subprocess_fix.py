#!/usr/bin/env python3
"""
Quick test to verify subprocess output buffering is fixed
Run this to test if the fix works before trying the full GUI
"""

import subprocess
import sys
import os

print("Testing subprocess output buffering fix...")
print("=" * 60)

# Test 1: Basic subprocess with unbuffered output
print("\nTest 1: Running subprocess with unbuffered output")
print("-" * 60)

test_script = """
import time
import sys

def print_flush(msg):
    print(msg)
    sys.stdout.flush()

print_flush("Line 1 - Immediate output")
time.sleep(0.5)
print_flush("Line 2 - After 0.5 seconds")
time.sleep(0.5)
print_flush("Line 3 - After another 0.5 seconds")
"""

env = os.environ.copy()
env['PYTHONUNBUFFERED'] = '1'

process = subprocess.Popen(
    [sys.executable, '-u', '-c', test_script],
    stdout=subprocess.PIPE,
    stderr=subprocess.STDOUT,
    text=True,
    bufsize=0,
    env=env
)

print("Reading output line by line:")
while True:
    line = process.stdout.readline()
    if not line and process.poll() is not None:
        break
    if line:
        print(f"  Received: {line.strip()}")

process.wait()

if process.returncode == 0:
    print("✓ Test 1 PASSED - Output appeared line by line")
else:
    print("✗ Test 1 FAILED")

# Test 2: Check if importer.py exists
print("\n" + "=" * 60)
print("\nTest 2: Checking if importer.py exists")
print("-" * 60)

if os.path.exists('importer.py'):
    print("✓ importer.py found")
else:
    print("✗ importer.py NOT FOUND")
    print("  Make sure you're running this from the project directory")

# Test 3: Check if config.json exists
print("\n" + "=" * 60)
print("\nTest 3: Checking if config.json exists")
print("-" * 60)

if os.path.exists('config.json'):
    print("✓ config.json found")
    try:
        import json
        with open('config.json') as f:
            config = json.load(f)
        
        required_keys = ['testrail_url', 'testrail_user', 'testrail_password']
        missing = [k for k in required_keys if not config.get(k)]
        
        if missing:
            print(f"⚠ Warning: Missing config values: {missing}")
        else:
            print("✓ All required TestRail config values present")
    except Exception as e:
        print(f"✗ Error reading config.json: {e}")
else:
    print("✗ config.json NOT FOUND")

# Test 4: Check tkinter
print("\n" + "=" * 60)
print("\nTest 4: Checking tkinter availability")
print("-" * 60)

try:
    import tkinter
    print(f"✓ tkinter is available (version {tkinter.TkVersion})")
except ImportError:
    print("✗ tkinter is NOT available")
    print("  Install with: sudo apt-get install python3-tk")

# Test 5: Check other dependencies
print("\n" + "=" * 60)
print("\nTest 5: Checking other dependencies")
print("-" * 60)

dependencies = {
    'requests': 'pip install requests',
    'sqlite3': 'built-in',
}

for module, install_cmd in dependencies.items():
    try:
        __import__(module)
        print(f"✓ {module} is available")
    except ImportError:
        print(f"✗ {module} is NOT available")
        if install_cmd != 'built-in':
            print(f"  Install with: {install_cmd}")

# Summary
print("\n" + "=" * 60)
print("SUMMARY")
print("=" * 60)
print("\nIf all tests passed, the subprocess output fix should work!")
print("You can now run: python3 ui.py")
print("\nIf any tests failed, fix those issues first.")
print("\nTo debug further, use VS Code debugger:")
print("  1. Open Run & Debug (Ctrl+Shift+D)")
print("  2. Select 'Debug UI Application'")
print("  3. Press F5")
print("=" * 60)
