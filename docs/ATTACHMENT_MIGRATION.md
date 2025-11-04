# Attachment Migration Guide

This guide explains how attachments are imported from TestRail and migrated to Jira/Xray.

## Overview

The attachment migration process consists of two main phases:

1. **Import Phase**: Download attachments from TestRail and store them locally
2. **Export Phase**: Upload attachments to corresponding Jira issues

## Import Phase

### What Gets Imported

The importer fetches attachments from two sources:

1. **Test Case Attachments**: Files attached to test cases in TestRail
2. **Test Result Attachments**: Files attached to test results/executions

### Storage Structure

Attachments are stored in two places:

1. **Database**: `attachments` table in `testrail.db`
   - `id`: TestRail attachment ID
   - `entity_type`: Either 'case' or 'result'
   - `entity_id`: ID of the test case or result
   - `filename`: Original filename
   - `size`: File size in bytes
   - `created_on`: Timestamp when attachment was created
   - `user_id`: User who created the attachment
   - `url`: Original TestRail URL
   - `local_path`: Path to downloaded file

2. **File System**: `attachments/` directory
   - Files are named: `{entity_type}_{entity_id}_{filename}`
   - Example: `case_123_screenshot.png`
   - Example: `result_456_test_data.csv`

### Import Process

When you click "Start Import" in the GUI:

1. Creates `attachments` table if it doesn't exist
2. Creates `attachments/` directory
3. For each test case:
   - Fetches attachments using TestRail API
   - Downloads each file
   - Stores metadata in database
4. For each test result:
   - Fetches attachments using TestRail API
   - Downloads each file
   - Stores metadata in database
5. Shows progress every 10 attachments
6. Final summary shows total attachments imported

### TestRail API Endpoints Used

- `get_attachments_for_case/{case_id}`: Get attachments for a test case
- `get_attachments_for_test/{result_id}`: Get attachments for a test result
- `index.php?/attachments/get/{attachment_id}`: Download attachment file

## Export Phase

### Attachment Mapping

Attachments are uploaded to Jira issues based on their entity type:

1. **Case Attachments** → Uploaded to migrated Test issues
   - Uses mapping: `cases[testrail_case_id] → jira_test_key`
   - Example: TestRail case 123 → Jira issue RET-18

2. **Result Attachments** → Uploaded to Test Execution issues
   - Finds the test run for the result
   - Uses mapping: `runs[testrail_run_id] → jira_execution_key`
   - Example: TestRail result 456 → Jira execution RET-25

### Upload Process

When you click "Start Export" in the GUI:

1. Reads attachments from database
2. For each attachment:
   - Determines target Jira issue using mapping
   - Checks if file exists locally
   - Uploads file to Jira issue
   - Shows progress every 10 attachments
3. Skips attachments if:
   - File doesn't exist locally
   - No mapping found for entity
   - Upload fails (with warning)

### Jira API Details

- **Endpoint**: `POST /rest/api/2/issue/{issueKey}/attachments`
- **Headers**: `X-Atlassian-Token: no-check` (required by Jira)
- **Method**: multipart/form-data upload
- **Authentication**: Bearer token (PAT) or Basic Auth

## Checking Attachment Status

Use the test script to verify attachment migration:

```bash
python3 test_attachments.py
```

This shows:
- Total attachments imported
- Breakdown by entity type (case/result)
- File existence status
- Sample attachments
- How many attachments can be migrated
- Migration mapping status

## GUI Integration

### Import Tab
- Shows attachment progress during import
- Final summary includes attachment count

### Export Tab
- Shows attachment upload progress during export
- Final summary includes attachment count

### Database Viewer Tab
- Select "attachments" table to view all attachments
- Shows all metadata including local file paths
- Export to CSV for analysis

## Troubleshooting

### No Attachments Found

If the import shows 0 attachments:
1. Check if your TestRail test cases have attachments
2. Check if your TestRail results have attachments
3. Verify TestRail API credentials in `config.json`

### File Download Fails

If attachment downloads fail:
1. Check TestRail URL and credentials
2. Verify network connectivity
3. Check TestRail API permissions
4. Look for warnings in import output

### Upload Fails

If attachment uploads fail:
1. Verify Jira API credentials
2. Check if target issue exists
3. Verify file size (Jira may have limits)
4. Check Jira attachment permissions
5. Look for warnings in export output

### Missing Files

If files are missing during export:
1. Check if `attachments/` directory exists
2. Verify files were downloaded during import
3. Re-run import if files are missing
4. Check disk space

## File Size Considerations

- **Jira Limits**: Check your Jira instance's attachment size limit
- **Disk Space**: Ensure sufficient space for all attachments
- **Network**: Large attachments may take time to upload
- **Memory**: Large files are streamed to minimize memory usage

## Best Practices

1. **Run Import First**: Always import before attempting export
2. **Verify Downloads**: Use `test_attachments.py` to check files
3. **Check Mapping**: Ensure test cases and runs are migrated before attachments
4. **Monitor Progress**: Watch for warnings during upload
5. **Backup Files**: Keep the `attachments/` directory as backup

## Example Workflow

1. Click "Start Import" in GUI
2. Wait for import to complete (includes attachments)
3. Run `python3 test_attachments.py` to verify
4. Click "Start Export" in GUI
5. Attachments are uploaded to Jira issues
6. Verify in Jira by checking test issues for attachments

## Database Schema

```sql
CREATE TABLE attachments (
    id INTEGER NOT NULL PRIMARY KEY,
    entity_type TEXT,           -- 'case' or 'result'
    entity_id INTEGER,          -- TestRail case/result ID
    filename TEXT,              -- Original filename
    size INTEGER,               -- Size in bytes
    created_on INTEGER,         -- Unix timestamp
    user_id INTEGER,            -- TestRail user ID
    url TEXT,                   -- Original TestRail URL
    local_path TEXT             -- Path to downloaded file
)
```

## Summary

The attachment migration feature:
- ✅ Downloads all test case and result attachments
- ✅ Stores metadata in database
- ✅ Uploads to correct Jira issues
- ✅ Handles errors gracefully
- ✅ Shows progress and warnings
- ✅ Integrates with existing migration workflow
