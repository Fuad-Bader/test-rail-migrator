# Attachment Issues - Fixes Applied

## Issues Reported

1. **Duplicate Attachments**: Running import twice creates duplicate entries in database
2. **File Corruption**: Downloaded attachments are unreadable/corrupted
3. **Missing Uploads**: Attachments don't appear in Jira after migration

## Root Causes Identified

### Issue 1: Duplicate Attachments

- **Cause**: The attachments table lacked a UNIQUE constraint, and `INSERT OR REPLACE` was used without checking for existing records
- **Impact**: Each import run would add duplicate rows for the same attachment

### Issue 2: File Corruption

- **Cause**: Misunderstood TestRail's `get_attachment` API - tried to decode as base64 when it returns binary data
- **Details**: TestRail's `get_attachment(id, filepath)` saves binary content directly to the provided filepath
- **Impact**: Code was trying to base64 decode the JSON response instead of using the API correctly

### Issue 3: Missing Uploads

- **Cause**: Silent failures during upload - no verification that files actually uploaded
- **Details**: Upload might fail due to file not existing, empty files, or API errors
- **Impact**: Migration appeared successful but attachments were never uploaded to Jira

## Fixes Applied

### Fix 1: Prevent Duplicates

**File**: `importer.py`

1. **Added UNIQUE constraint to attachments table**:

```python
CREATE TABLE IF NOT EXISTS attachments (
    id INTEGER NOT NULL,
    entity_type TEXT,
    entity_id INTEGER,
    filename TEXT,
    size INTEGER,
    created_on INTEGER,
    user_id INTEGER,
    url TEXT,
    local_path TEXT,
    UNIQUE(id, entity_type, entity_id)  # <-- Added this
)
```

2. **Added duplicate check before download**:

```python
# Check if already exists to avoid duplicates
cursor.execute('SELECT id FROM attachments WHERE id = ? AND entity_type = ? AND entity_id = ?',
               (attachment['id'], 'case', case['id']))
if cursor.fetchone():
    print(f"    Skipping duplicate: {attachment['filename']}")
    continue
```

### Fix 2: Fix File Corruption

**File**: `importer.py`

**Changed from**: Direct URL download with requests

```python
response = requests.get(
    attachment_url,
    auth=(config['testrail_user'], config['testrail_password']),
    stream=True
)
with open(local_filename, 'wb') as f:
    for chunk in response.iter_content(chunk_size=8192):
        f.write(chunk)
```

**Changed to**: TestRail API correct usage

```python
# Download file using TestRail API
# The get_attachment endpoint takes a filepath and saves directly to it
# It returns the filepath on success or error message on failure
result = client.send_get(f"get_attachment/{attachment['id']}", local_filename)

# Verify file was written successfully
if result == local_filename and os.path.exists(local_filename) and os.path.getsize(local_filename) > 0:
    # Store in database
    ...
else:
    print(f"    Warning: Failed to download file: {attachment['filename']} - {result}")
```

**Key insight**: TestRail's `send_get('get_attachment/ID', filepath)` automatically saves the binary content to the file. No need to decode base64 or manually write content.

### Fix 3: Add Upload Verification

**File**: `migrator.py`

Enhanced the `add_attachment()` method with:

1. **File existence check**:

```python
if not os.path.exists(file_path):
    print(f"❌ File not found: {file_path}")
    return None
```

2. **File size validation**:

```python
file_size = os.path.getsize(file_path)
if file_size == 0:
    print(f"❌ File is empty: {file_path}")
    return None
```

3. **Upload progress logging**:

```python
print(f"  📎 Uploading {os.path.basename(file_path)} ({file_size} bytes) to {issue_key}...")
```

4. **Success confirmation**:

```python
result = response.json()
print(f"  ✓ Uploaded successfully (ID: {result[0]['id']})")
return result
```

5. **Detailed error messages**:

```python
except requests.exceptions.HTTPError as e:
    print(f"❌ HTTP Error uploading {file_path}: {e.response.status_code} - {e.response.text}")
    return None
```

## Testing the Fixes

### Step 1: Clean Existing Data

```bash
# Backup your existing database
cp testrail.db testrail.db.backup

# Remove corrupted attachments
rm -rf attachments/

# Optional: Delete attachments table to start fresh
sqlite3 testrail.db "DROP TABLE IF EXISTS attachments;"
```

### Step 2: Run Test Script

```bash
# First, run a fresh import
python importer.py

# Then run the verification script
python test_attachments.py
```

The test script will:

- Test downloading attachments using the correct API endpoint
- Verify file integrity by checking file signatures
- Test uploading attachments to Jira
- Provide detailed diagnostics

### Step 3: Run Full Migration

```bash
# Delete old database and attachments
rm testrail.db
rm -rf attachments/

# Run fresh import with fixes
python importer.py

# Run migration with verbose logging
python migrator.py
```

### Step 4: Verify in Jira

1. Open any Test issue in Jira (e.g., RET-1, RET-2, etc.)
2. Scroll down to the "Attachments" section
3. You should see the migrated attachments listed
4. Click on an attachment to verify it's viewable/downloadable

## Expected Output

### During Import (importer.py)

```
[15/15] Fetching Attachments...
  Fetching case attachments...
    Downloaded 10 attachments...
  Fetching result attachments...
✓ Stored and downloaded 15 attachments
```

### During Migration (migrator.py)

```
Migrating attachments...
  📎 Uploading screenshot.jpg (12458 bytes) to RET-1...
  ✓ Uploaded successfully (ID: 10001)
  📎 Uploading testdata.pdf (45632 bytes) to RET-2...
  ✓ Uploaded successfully (ID: 10002)
✓ Migrated 2 attachments
```

### On Subsequent Import (should skip duplicates)

```
[15/15] Fetching Attachments...
  Fetching case attachments...
    Skipping duplicate: screenshot.jpg
    Skipping duplicate: testdata.pdf
✓ Stored and downloaded 0 attachments (15 existing)
```

## Troubleshooting

### If files are still corrupted:

1. Check TestRail API permissions - ensure your API key has attachment access
2. Run test_attachments.py to see the actual API response
3. Check if TestRail returns base64 or binary data

### If uploads still fail:

1. Check Jira permissions - ensure user can add attachments
2. Verify file exists before migration: `ls -lh attachments/`
3. Check Jira attachment size limits in System settings
4. Look for HTTP error codes in output (401 = auth, 403 = permission, 413 = too large)

### If duplicates still occur:

1. Ensure you're using the latest importer.py with UNIQUE constraint
2. Delete the old attachments table: `sqlite3 testrail.db "DROP TABLE attachments;"`
3. Re-run import to create table with new schema

## Summary of Changes

| File                  | Lines Changed | Description                                           |
| --------------------- | ------------- | ----------------------------------------------------- |
| `importer.py`         | Lines 1-8     | Added imports: base64, os, traceback, requests        |
| `importer.py`         | Line 506      | Added UNIQUE constraint to attachments table          |
| `importer.py`         | Lines 535-588 | Rewrote case attachment download with API + base64    |
| `importer.py`         | Lines 620-670 | Rewrote result attachment download with API + base64  |
| `migrator.py`         | Lines 175-220 | Enhanced add_attachment() with validation and logging |
| `test_attachments.py` | New file      | Created comprehensive test script                     |

## Next Steps

1. ✅ Run `python test_attachments.py` to verify the fixes work
2. ✅ Delete old database and attachments folder
3. ✅ Run fresh import: `python importer.py`
4. ✅ Run migration: `python migrator.py`
5. ✅ Check Jira UI to confirm attachments are visible
6. ✅ Try opening downloaded files to verify they're not corrupted

All three issues should now be resolved! 🎉
