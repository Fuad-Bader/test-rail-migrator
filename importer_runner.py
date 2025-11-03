"""
Wrapper to run the importer as a function
"""
import subprocess
import sys

def run_import():
    """Run the importer script"""
    result = subprocess.run([sys.executable, 'importer.py'], 
                          capture_output=False, 
                          text=True)
    return result.returncode == 0

if __name__ == '__main__':
    run_import()
