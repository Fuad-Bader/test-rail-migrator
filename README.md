# TestRail to Xray Migration - Quick Start Guide

## Overview

This project migrates test data from TestRail to Xray (Jira Test Management).

**Supported Versions:**

- JIRA: 9.12.15
- Xray: 7.9.1-j9 (Server/Data Center)

---

## Prerequisites

1. **Python 3.x** installed
2. **Access to TestRail** with API credentials
3. **Access to Jira/Xray** with appropriate permissions
4. **Required Python packages:**
   ```bash
   pip install requests
   ```

---

## Step 1: Configure Credentials

Edit `config.json` with your credentials:

```json
{
  "testrail_url": "https://your-instance.testrail.io/",
  "testrail_user": "your-email@company.com",
  "testrail_password": "your-testrail-password",

  "jira_url": "https://your-jira-instance.com",
  "jira_username": "your-jira-email@company.com",
  "jira_password": "your-jira-api-token",
  "jira_project_key": "TEST"
}
```

### Getting Jira API Token

For Jira Cloud, generate an API token at:
https://id.atlassian.com/manage-profile/security/api-tokens

For Jira Server/Data Center, you can use your password.

---

## Step 2: Extract Data from TestRail

Run the main extraction script to pull all TestRail data into a local SQLite database:

```bash
python main.py
```

This will:

- Connect to TestRail
- Fetch all projects, users, test cases, suites, runs, results, etc.
- Store everything in `testrail.db`

**Output:**

```
================================================================================
FETCHING AND STORING TESTRAIL DATA
================================================================================

[1/15] Fetching Projects...
✓ Stored 5 projects

[2/15] Fetching Users...
✓ Stored 12 users

...

================================================================================
MIGRATION COMPLETE!
================================================================================

Summary:
  - Projects: 5
  - Users: 12
  - Suites: 15
  - Cases: 234
  - Runs: 45
  - Tests: 567
  - Results: 890
```

---

## Step 3: Prepare Jira/Xray

### 3.1 Verify Issue Types

Ensure your Jira project has these issue types:

- **Test** (required)
- **Test Set** (required)
- **Test Execution** (required)
- **Precondition** (optional)
- **Test Plan** (optional)

To check: Go to Project Settings → Issue Types

### 3.2 Set Up Permissions

Your Jira user needs permissions to:

- Create issues
- Edit issues
- Add comments
- Create issue links
- Manage versions

---

## Step 4: Run Migration to Xray

Execute the migrator script:

```bash
python migrator.py
```

This will:

1. **Migrate Test Cases** → Create Xray Tests
2. **Migrate Test Suites** → Create Xray Test Sets
3. **Migrate Test Runs** → Create Xray Test Executions
4. **Migrate Test Results** → Update Test Execution statuses
5. **Migrate Milestones** → Create Jira Versions

**Output:**

```
================================================================================
TESTRAIL TO XRAY MIGRATION
================================================================================

Target: https://jira.company.com
Project: TEST

================================================================================

Connecting to Jira/Xray...
✓ Connected to project: Test Project

[1/5] Migrating Test Cases...
  ✓ Migrated 10 test cases...
  ✓ Migrated 20 test cases...
✓ Migrated 234 test cases

[2/5] Migrating Test Suites as Test Sets...
✓ Migrated 15 test suites as test sets

[3/5] Migrating Test Runs as Test Executions...
  ✓ Migrated 5 test runs...
✓ Migrated 45 test runs as test executions

[4/5] Migrating Test Results...
  ✓ Migrated 20 test results...
✓ Migrated 567 test results

[5/5] Migrating Milestones as Versions...
✓ Migrated 8 milestones as versions

✓ Mapping saved to migration_mapping.json

================================================================================
MIGRATION COMPLETE!
================================================================================

Summary:
  - Test Cases migrated: 234
  - Test Sets created: 15
  - Test Executions created: 45
  - Milestones migrated: 8
```

---

## Step 5: Verify Migration

### 5.1 Check Migration Mapping

The file `migration_mapping.json` contains the mapping between TestRail IDs and Xray keys:

```json
{
  "cases": {
    "123": "TEST-101",
    "124": "TEST-102",
    ...
  },
  "suites": {
    "5": "TEST-201",
    ...
  },
  "runs": {
    "10": "TEST-301",
    ...
  }
}
```

### 5.2 Verify in Jira

1. Navigate to your Jira project
2. Check that Tests are created
3. Open a Test Set to verify it contains the correct tests
4. Open a Test Execution to verify test results

---

## Data Mapping Reference

| TestRail    | Xray           | Description                |
| ----------- | -------------- | -------------------------- |
| Test Case   | Test           | Individual test with steps |
| Test Suite  | Test Set       | Collection of tests        |
| Test Run    | Test Execution | Execution of tests         |
| Test Result | Test Status    | Pass/Fail status           |
| Milestone   | Version        | Release/Version            |
| Section     | Label          | Test organization          |
| Priority    | Priority       | Test priority              |

---

## Status Mapping

| TestRail Status | Xray Status |
| --------------- | ----------- |
| Passed          | PASS        |
| Blocked         | BLOCKED     |
| Untested        | TODO        |
| Retest          | FAIL        |
| Failed          | FAIL        |

---

## Troubleshooting

### Issue: "Could not access project"

**Solution:** Verify `jira_project_key` in config.json matches an existing project key.

### Issue: "Authentication failed"

**Solution:** Check your Jira username and API token/password.

### Issue: "Issue type 'Test' not found"

**Solution:** Ensure Xray is installed and Test issue types are enabled in your project.

### Issue: "Rate limit exceeded"

**Solution:** Increase `RATE_LIMIT_DELAY` in migrator.py (e.g., to 1.0 second).

### Issue: "Permission denied"

**Solution:** Verify your Jira user has permissions to create issues and manage the project.

---

## Advanced Configuration

### Customize Issue Type Names

Edit these constants in `migrator.py` if your Jira uses different names:

```python
XRAY_TEST_TYPE = 'Test'
XRAY_TEST_EXECUTION_TYPE = 'Test Execution'
XRAY_TEST_SET_TYPE = 'Test Set'
XRAY_PRECONDITION_TYPE = 'Precondition'
```

### Adjust Rate Limiting

Modify the delay between API calls:

```python
RATE_LIMIT_DELAY = 0.5  # seconds
```

### Custom Field Mapping

To map TestRail custom fields to Jira custom fields, modify the `migrate_test_cases` function in `migrator.py`.

---

## Files Reference

```
test-rail-migrator/
├── config.json              # Configuration file (edit this!)
├── main.py                  # TestRail data extraction
├── migrator.py              # Migration to Xray
├── testrail.py              # TestRail API client
├── testrail.db              # Local SQLite database (auto-generated)
├── migration_mapping.json   # ID to Key mapping (auto-generated)
├── XRAY_API_REFERENCE.md    # Complete API documentation
└── README.md                # This file
```

---

## Support

For API documentation and detailed endpoint information, see:

- **XRAY_API_REFERENCE.md** - Complete Xray API reference
- **Xray Documentation**: https://docs.getxray.app/
- **Jira REST API**: https://docs.atlassian.com/software/jira/docs/api/REST/

---

## Notes

- Always test migration on a non-production environment first
- Keep backups of TestRail data before migration
- Migration is idempotent - you can run it multiple times
- The SQLite database can be used for custom queries and analysis
- Large datasets may take significant time to migrate

---

## Next Steps

After successful migration:

1. **Review migrated data** in Jira
2. **Train team members** on Xray
3. **Configure test automation** integration
4. **Set up CI/CD pipelines** with Xray
5. **Archive TestRail** instance (after verification)

Good luck with your migration! 🚀
