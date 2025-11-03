# Troubleshooting Guide: No Output in GUI Console

## Problem

When clicking "Start Import" or "Start Export", no output appears in the console widget.

## Root Causes

### 1. **Python Output Buffering** (MOST LIKELY)

**Issue**: Python buffers stdout by default when running as a subprocess. Output is held in a buffer until it's full or the program ends.

**Solution Applied**:

- Added `-u` flag to Python subprocess call (unbuffered mode)
- Set `PYTHONUNBUFFERED=1` environment variable
- Set `bufsize=0` in Popen (unbuffered)
- Added `print_flush()` helper in importer.py

### 2. **Line Reading Loop Issue**

**Issue**: The original `iter(process.stdout.readline, '')` pattern doesn't work reliably with buffered streams.

**Solution Applied**:

- Changed to a `while True` loop
- Check `process.poll()` to detect when process ends
- Read remaining output after loop

### 3. **No Initial Feedback**

**Issue**: User doesn't know if button click registered.

**Solution Applied**:

- Added immediate console output when process starts
- Shows working directory and Python executable
- Displays "Starting import/export process..." message

### 4. **Exception Swallowing**

**Issue**: Errors might occur but not be displayed.

**Solution Applied**:

- Added `traceback.format_exc()` to show full error details
- Wrapped subprocess calls in try-catch with detailed error reporting

## How to Debug

### Method 1: Use VS Code Debugger

1. Open VS Code
2. Go to Run & Debug (Ctrl+Shift+D)
3. Select "Debug UI Application" from dropdown
4. Set breakpoints in `ui.py`:
   - Line in `start_import()` function
   - Line in `run_import()` function
   - Line where subprocess is created
5. Press F5 to start debugging
6. Click "Start Import" button
7. Step through code with F10 (step over) or F11 (step into)

### Method 2: Check Console Output Directly

Run the importer manually to verify it works:

```bash
cd /home/fuad/Documents/Github/test-rail-migrator
python3 importer.py
```

### Method 3: Add More Debug Output

Add this at the beginning of `run_import()`:

```python
print(f"DEBUG: Thread started, ID: {threading.current_thread().ident}")
print(f"DEBUG: Button state: {self.import_btn['state']}")
```

### Method 4: Check for Config Issues

```python
# In start_import(), add:
print(f"Config loaded: {self.config}")
```

## Testing the Fix

1. **Run the GUI**:

   ```bash
   python3 ui.py
   ```

2. **Click "Start Import"**:

   - You should IMMEDIATELY see:
     ```
     Starting import process...
     Working directory: /home/fuad/Documents/Github/test-rail-migrator
     Python executable: /usr/bin/python3
     ================================================================================
     ```

3. **Watch for output**:

   - Output should appear line-by-line as the import progresses
   - Each section should display immediately after completion

4. **If still no output**:
   - Check the terminal where you ran `ui.py` for error messages
   - Use the VS Code debugger (see Method 1 above)
   - Verify `importer.py` runs successfully standalone

## Common Issues

### Issue: "FileNotFoundError: importer.py"

**Cause**: Working directory is wrong
**Fix**: The subprocess now uses `cwd=os.getcwd()` to ensure correct directory

### Issue: Output appears all at once at the end

**Cause**: Buffering still happening
**Fix**:

- Ensure using Python 3.7+
- Check that `-u` flag is being used
- Verify `PYTHONUNBUFFERED` is set

### Issue: Button stays disabled

**Cause**: Exception occurred but wasn't shown
**Fix**: Check terminal output for traceback

### Issue: Process hangs

**Cause**: Subprocess is waiting for input or deadlocked
**Fix**:

- Add timeout to subprocess.wait()
- Check importer.py for input() calls
- Verify config.json has all required fields

## Verification Steps

After applying fixes, verify:

1. ✓ Immediate "Starting process..." message appears
2. ✓ Output appears line-by-line, not all at once
3. ✓ Progress shows in real-time
4. ✓ Final completion message appears
5. ✓ Button re-enables after completion
6. ✓ No errors in terminal

## Debug Configuration Details

The `.vscode/launch.json` provides:

- **Debug UI Application**: Debug the GUI with breakpoints
- **Debug Importer**: Debug importer.py standalone
- **Debug Migrator**: Debug migrator.py standalone

All configurations:

- Use integrated terminal (see output immediately)
- Have `PYTHONUNBUFFERED=1` set
- Allow debugging into library code (`justMyCode: false`)

## Additional Debug Commands

```bash
# Test if tkinter works
python3 -c "import tkinter; tkinter.Tk()"

# Test if subprocess output works
python3 -c "import subprocess, sys; p = subprocess.Popen([sys.executable, '-u', '-c', 'print(\"test\")'], stdout=subprocess.PIPE, text=True, bufsize=0); print(p.stdout.read())"

# Check config.json
cat config.json

# Verify Python version
python3 --version
```

## Expected Behavior After Fix

**Before clicking button**:

- Button enabled
- Console empty

**After clicking button**:

- Button disabled
- Console shows: "Starting import process..."
- Console shows working directory info
- Console shows separator line

**During import**:

- Each section appears as it completes
- Progress messages appear in real-time
- Console auto-scrolls to bottom

**After completion**:

- Success or error message appears
- Button re-enables
- Can click again if needed

## If Problem Persists

1. Run with debug output:

   ```bash
   python3 -u ui.py 2>&1 | tee ui_debug.log
   ```

2. Check the log file for clues

3. Test each component separately:

   - Test tkinter: `python3 -c "import tkinter; print('OK')"`
   - Test subprocess: Run importer.py directly
   - Test threading: Add print statements in thread function

4. Share the error messages or behavior for further diagnosis
