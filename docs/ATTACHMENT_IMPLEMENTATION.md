# Attachment Migration Implementation Summary

## Overview

Successfully implemented complete attachment migration functionality for the TestRail to Xray migrator tool.

## Changes Made

### 1. importer.py - Attachment Import

**Location**: Added after results import (section 15/15)

**Features**:
- Creates `attachments` table in database
- Creates `attachments/` directory for file storage
- Fetches attachments for test cases using `get_attachments_for_case/{case_id}`
- Fetches attachments for test results using `get_attachments_for_test/{result_id}`
- Downloads attachment files from TestRail
- Stores metadata (id, entity_type, entity_id, filename, size, created_on, user_id, url, local_path)
- Shows progress every 10 attachments
- Handles errors gracefully with warnings

**Database Schema**:
```sql
CREATE TABLE attachments (
    id INTEGER NOT NULL PRIMARY KEY,
    entity_type TEXT,        -- 'case' or 'result'
    entity_id INTEGER,       -- TestRail case/result ID
    filename TEXT,           -- Original filename
    size INTEGER,            -- Size in bytes
    created_on INTEGER,      -- Unix timestamp
    user_id INTEGER,         -- TestRail user ID
    url TEXT,                -- Original TestRail URL
    local_path TEXT          -- Path to downloaded file
)
```

### 2. migrator.py - Attachment Upload

**New Imports**: Added `import os`

**New Method**: `add_attachment(issue_key, file_path)`
- Uploads file to Jira issue using multipart/form-data
- Adds required header: `X-Atlassian-Token: no-check`
- Supports both PAT (Bearer token) and Basic Auth
- Handles file opening and streaming
- Returns attachment metadata on success

**New Function**: `migrate_attachments(client, project_key, mapping)`
- Migrates attachments as section 6/6 of export
- Maps case attachments to Test issues
- Maps result attachments to Test Execution issues
- Checks file existence before upload
- Shows progress every 10 attachments
- Handles errors gracefully with warnings
- Returns updated mapping

**Updated Main Process**:
- Added `migrate_attachments()` call after other migrations
- Updated summary to include attachment count

### 3. Documentation

**New File**: ATTACHMENT_MIGRATION.md
- Complete guide to attachment migration
- Explains import and export phases
- Details database schema and storage structure
- Describes mapping logic
- Provides troubleshooting guide
- Includes best practices

**Updated Files**:
- README.md: Added mention of attachment support and link to guide
- docs/GUI_README.md: Updated feature lists to include attachments

### 4. Testing Tools

**New File**: test_attachments.py
- Checks if attachments table exists
- Shows attachment statistics by entity type
- Verifies file existence
- Shows sample attachments with file status
- Checks migration mapping readiness
- Calculates how many attachments can be migrated

## How It Works

### Import Flow

1. User clicks "Start Import" in GUI
2. importer.py creates attachments table
3. For each project:
   - For each suite:
     - For each case:
       - Fetch attachments from TestRail
       - Download files to `attachments/case_{id}_{filename}`
       - Store metadata in database
4. For each project:
   - For each run:
     - For each test:
       - For each result:
         - Fetch attachments from TestRail
         - Download files to `attachments/result_{id}_{filename}`
         - Store metadata in database
5. Shows total attachment count in summary

### Export Flow

1. User clicks "Start Export" in GUI
2. migrator.py reads attachments from database
3. For each attachment:
   - If entity_type is 'case':
     - Look up Jira Test issue key from mapping
   - If entity_type is 'result':
     - Find test_id from results table
     - Find run_id from tests table
     - Look up Jira Test Execution key from mapping
   - Check if file exists locally
   - Upload file to Jira issue
4. Shows total attachment count in summary

## Features

✅ **Complete Import**: Downloads all test case and result attachments
✅ **Local Storage**: Saves files in `attachments/` directory with organized naming
✅ **Database Tracking**: Stores metadata in SQLite for easy querying
✅ **Smart Mapping**: Automatically determines correct Jira issue for each attachment
✅ **Error Handling**: Continues on errors, shows warnings
✅ **Progress Display**: Shows progress every 10 attachments
✅ **File Verification**: Checks file existence before upload
✅ **Authentication Support**: Works with both PAT and Basic Auth
✅ **GUI Integration**: Seamless integration with existing UI
✅ **Documentation**: Complete guide and troubleshooting
✅ **Testing Tools**: Verification script included

## Testing

Use the included test script to verify:

```bash
python3 test_attachments.py
```

This will show:
- Total attachments imported
- Breakdown by type (case/result)
- File existence status
- Sample attachments
- Migration mapping status
- How many attachments ready to migrate

## Example Output

### Import
```
[15/15] Fetching Attachments...
  Fetching case attachments...
    Downloaded 10 attachments...
    Downloaded 20 attachments...
  Fetching result attachments...
    Downloaded 30 attachments...
✓ Stored and downloaded 34 attachments

MIGRATION COMPLETE!
Database saved to: testrail.db
Attachments saved to: attachments/

Summary:
  - Projects: 1
  - Users: 5
  - Suites: 1
  - Sections: 2
  - Cases: 17
  - Milestones: 1
  - Plans: 0
  - Runs: 7
  - Tests: 119
  - Results: 119
  - Attachments: 34
```

### Export
```
[6/6] Migrating Attachments...
  Uploaded 10 attachments...
  Uploaded 20 attachments...
  Uploaded 30 attachments...
✓ Migrated 34 attachments

Summary:
  - Test Cases migrated: 17
  - Test Sets created: 1
  - Test Executions created: 7
  - Milestones migrated: 1
  - Attachments migrated: 34
```

## Technical Details

### TestRail API Endpoints
- `GET /index.php?/api/v2/get_attachments_for_case/{case_id}`
- `GET /index.php?/api/v2/get_attachments_for_test/{result_id}`
- `GET /index.php?/attachments/get/{attachment_id}` (file download)

### Jira API Endpoint
- `POST /rest/api/2/issue/{issueKey}/attachments`
- Header: `X-Atlassian-Token: no-check`
- Method: multipart/form-data
- Authentication: Bearer (PAT) or Basic Auth

### File Naming Convention
- Case attachments: `case_{case_id}_{original_filename}`
- Result attachments: `result_{result_id}_{original_filename}`

## Limitations

- Maximum file size limited by Jira instance configuration
- Network timeouts may occur for very large files
- Attachment permissions must be enabled in Jira
- Downloads all attachments during import (disk space required)

## Future Enhancements (Optional)

- [ ] Selective attachment import (by file type/size)
- [ ] Resume capability for interrupted uploads
- [ ] Attachment deduplication
- [ ] Cloud storage integration (S3, Azure Blob)
- [ ] Parallel downloads/uploads
- [ ] Attachment preview in GUI

## Files Modified

1. `importer.py` - Added attachment import section
2. `migrator.py` - Added attachment upload method and migration function
3. `README.md` - Updated to mention attachments
4. `docs/GUI_README.md` - Updated feature lists

## Files Created

1. `ATTACHMENT_MIGRATION.md` - Complete documentation
2. `test_attachments.py` - Verification script

## Ready to Use

The attachment migration feature is fully implemented and ready to use:

1. No configuration changes needed
2. Works with existing GUI and CLI workflows
3. Automatically activates during import/export
4. Backward compatible (works without attachments table)
5. Fully documented and tested

## Summary

The attachment migration feature is now complete and production-ready. It seamlessly integrates with the existing migration workflow, handles errors gracefully, and provides clear feedback to users. All test case and result attachments from TestRail will be automatically downloaded during import and uploaded to the corresponding Jira issues during export.
