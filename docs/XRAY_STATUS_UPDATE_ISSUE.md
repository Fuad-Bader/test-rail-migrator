# Xray Test Status Update Issue - Investigation Results

## Problem Summary

The TestRail to Xray migration successfully creates:

- ✅ Test Cases (17 migrated)
- ✅ Test Sets (1 migrated)
- ✅ Test Executions (7 migrated)
- ✅ Tests are properly added to executions

**However**, updating test execution statuses fails with API errors.

## Root Cause

The Xray API endpoint for updating test statuses returns errors due to a **Jira screen configuration issue**:

```
Error: customfield_10125: Field 'customfield_10125' cannot be set.
It is not on the appropriate screen, or unknown.
```

## Investigation Details

### API Endpoints Tested

1. **Individual Status Update** (404 Not Found)

   - `POST /rest/raven/1.0/api/testexec/{execKey}/test/{testKey}/status`
   - Status: ❌ 404 - Endpoint not found
   - Note: Documented in Xray REST API v1.0 reference but not working

2. **Import Execution Results** (400 Bad Request)

   - `POST /rest/raven/1.0/import/execution`
   - Status: ❌ 400 - Screen configuration issue
   - Error: Custom field `customfield_10125` missing from screen

3. **Alternative Endpoints Tried**:
   - Using test ID instead of key: ❌ 404
   - Internal API paths: ❌ 404/405
   - Old API format: ❌ 400

### Why This Happens

1. **Xray Version**: Your Xray 7.9.1-j9 (Server/Data Center) may have different API structure
2. **Screen Configuration**: Custom field used by Xray import is not configured
3. **API Documentation Mismatch**: Official docs may be for newer/different version

## Solutions

### Option A: Fix Jira Screen Configuration (Recommended for Automation)

This will enable the import/execution API endpoint to work.

**Steps:**

1. **Find the Custom Field**

   ```bash
   # Go to Jira Administration → Issues → Custom Fields
   # Search for field ID: customfield_10125
   # Note its name (likely related to Xray test execution)
   ```

2. **Add Field to Screen**

   ```bash
   # Go to: Jira Admin → Issues → Screens
   # Find screen(s) used by "Test Execution" issue type
   # Click "Configure" on each screen
   # Click "Add Field" and select customfield_10125
   # Save changes
   ```

3. **Test the API**

   ```bash
   python3 try_import_execution.py
   # Should now return success
   ```

4. **Re-run Migration**

   ```bash
   # Option 1: Re-run full migration (will skip existing issues)
   python3 migrator.py

   # Option 2: Only update statuses (if we create a separate script)
   ```

### Option B: Manual Status Update (Easiest, No Config Changes)

**Steps:**

1. Open Jira in browser: http://localhost:8080
2. Navigate to Test Execution issue (e.g., RET-42)
3. In the Test Execution view, you'll see list of tests
4. Click on each test and update its status (PASS/FAIL/BLOCKED/etc.)
5. Repeat for all 7 Test Executions

**Pros:**

- No configuration changes needed
- Works immediately
- You can review each test

**Cons:**

- Manual work (7 executions × ~6 tests each = ~42 manual updates)
- Time consuming

### Option C: Use Xray's Built-in Import (Alternative)

Xray has UI-based import functionality that might work better.

**Steps:**

1. Export test results from migrator to Excel/CSV format
2. Go to Jira → Xray menu → "Import"
3. Follow Xray's import wizard
4. Map columns to Xray fields
5. Import test results

### Option D: Create Custom Update Script

I can create a script that updates test statuses using a different approach (e.g., direct custom field updates via Jira API).

**Requirements:**

- Need to identify which custom field stores test status
- May need to update Jira issue fields directly
- Less clean but might work around screen issue

### Option E: Contact Xray Support

For the definitive answer on your specific Xray version.

**Info to provide:**

- Xray Version: 7.9.1-j9 (Server/Data Center)
- Jira Version: 9.12.15
- Issue: Cannot update test execution status via REST API
- Error: 404 on status endpoint, 400 on import endpoint
- Support: https://support.getxray.app/

## Recommended Action Plan

### Short Term (Use Now)

1. ✅ Migration completed successfully - use as-is
2. ✅ All test structure is in Jira/Xray
3. ⚠️ Update test statuses manually in Jira UI (Option B)

### Medium Term (Fix for Future)

1. Fix Jira screen configuration (Option A)
2. Test import/execution API
3. Re-run migration or create update script

### Long Term (Improve Process)

1. Document custom field configuration
2. Create migration validation script
3. Set up automated status synchronization

## Technical Details

### Custom Field customfield_10125

This field is created automatically by Xray but may not be added to screens by default.

**To find it:**

```bash
# Via Jira UI:
Administration → Issues → Custom Fields → Search "10125"

# Via API:
curl -u admin:password \
  "http://localhost:8080/rest/api/2/field" | grep customfield_10125
```

### Test Execution Current State

Your Test Executions are correctly created with tests added:

```
Test Execution: RET-42 - "Smoke Test Sprint 55"
├── RET-18 (Status: TODO)
├── RET-19 (Status: TODO)
├── RET-20 (Status: TODO)
├── RET-21 (Status: TODO)
└── RET-22 (Status: TODO)
```

All tests default to "TODO" status. You need to update them to their actual status (PASS/FAIL/etc).

### Status Mapping Reference

From TestRail to Xray:

| TestRail Status | Xray Status | ID  |
| --------------- | ----------- | --- |
| Passed          | PASS        | 0   |
| Blocked         | BLOCKED     | 4   |
| Untested        | TODO        | 1   |
| Retest          | FAIL        | 3   |
| Failed          | FAIL        | 3   |
| In Progress     | EXECUTING   | 2   |

## Scripts for Reference

### Check Test Execution Status

```bash
python3 check_test_executions.py
```

### Try Different API Formats

```bash
python3 try_import_execution.py
```

### Investigate API Endpoints

```bash
python3 investigate_xray_api.py
```

## Conclusion

Your migration is **functionally complete**. The core data (tests, suites, executions) is successfully migrated. Only the test result statuses need to be updated, which can be done:

1. **Manually** (quickest for now)
2. **Via API** after fixing screen configuration
3. **Via Xray UI import** as alternative

The screen configuration issue is a one-time fix that will enable full API automation for future migrations or synchronization.

---

**Created:** 2025-11-04  
**Xray Version:** 7.9.1-j9 (Server/Data Center)  
**Jira Version:** 9.12.15  
**Issue:** Status update API endpoints not working  
**Workaround:** Manual status update or screen configuration fix
