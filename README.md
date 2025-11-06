# TestRail to Xray Migration - Quick Start Guide

## Overview

This project migrates test data from TestRail to Xray (Jira Test Management).

**Supported Versions:**

- JIRA: 9.12.15
- Xray: 7.9.1-j9 (Server/Data Center)

---

## 🎨 NEW: Graphical User Interface

We now offer a **GUI application** for easier migration!

### Quick Start with GUI

1. **Install dependencies:**

   ```bash
   pip install -r requirements.txt
   ```

2. **Launch the GUI:**

   ```bash
   python ui.py
   ```

   Or use the launcher scripts:

   - **Linux/Mac:** `./start_gui.sh`
   - **Windows:** `start_gui.bat`

3. **Use the interface:**
   - **Config Tab**: Set up TestRail and Jira credentials
   - **Import Tab**: Fetch data from TestRail with one click (including attachments)
   - **Export Tab**: Migrate data to Xray/Jira (including attachments)
   - **Reports Tab**: Generate detailed migration statistics and progress reports
   - **Database Viewer**: Browse imported data in table format

For detailed GUI instructions, see [GUI_README.md](GUI_README.md)
For attachment migration details, see [ATTACHMENT_MIGRATION.md](ATTACHMENT_MIGRATION.md)
For report generation guide, see [REPORTS_GUIDE.md](REPORTS_GUIDE.md)

---

## Command Line Usage

If you prefer command-line tools, follow the steps below:

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
  "jira_password": "your-jira-api-token"
}
```

**Note:** The `jira_project_key` is no longer needed in config.json - you'll select the target project in the next step.

### Getting Jira API Token

For Jira Cloud, generate an API token at:
https://id.atlassian.com/manage-profile/security/api-tokens

For Jira Server/Data Center, you can use your password.

---

## Step 2: Select Projects

**NEW:** Run the interactive project selector to choose which TestRail project to import and which Jira project to migrate to:

```bash
python3 project_selector.py
```

This interactive tool will:

1. **List all TestRail projects** - Select which one to import
2. **List all Jira projects** - Select the target project
3. **Create new Jira project** (optional) - If you need a new project
4. **Save configuration** to `migration_config.json`

**Example output:**

```text
================================================================================
TESTRAIL TO JIRA/XRAY MIGRATION - PROJECT SELECTION
================================================================================

📋 Step 1: Select TestRail project to import

--------------------------------------------------------------------------------
SELECT TESTRAIL PROJECT TO IMPORT
--------------------------------------------------------------------------------

Available TestRail Projects:

  1. Mobile App Testing (ID: 1) - ✓ Active
  2. Web Portal Tests (ID: 2) - ✓ Active
  3. API Test Suite (ID: 3) - ✓ Active

Select project (1-3): 2

✓ Selected: Web Portal Tests

📋 Step 2: Select target Jira project

--------------------------------------------------------------------------------
SELECT TARGET JIRA PROJECT
--------------------------------------------------------------------------------

Available Jira Projects:

  1. Mobile Testing (MT)
  2. Web Testing (WT)
  3. API Testing (API)
  4. Create new project

Select project (1-4): 4

--------------------------------------------------------------------------------
CREATE NEW JIRA PROJECT
--------------------------------------------------------------------------------

Enter project key (2-10 uppercase letters, e.g., 'MYPROJ'): WEBTEST
Enter project name: Web Portal Testing
Enter project description (optional): Migration from TestRail

Project Templates:
  1. Scrum software development
  2. Kanban software development
  3. Basic software development

Select template (1-3) [default: 1]: 1

Creating project 'Web Portal Testing' (WEBTEST)...
✓ Project created successfully!
  Key: WEBTEST
  Name: Web Portal Testing

================================================================================
MIGRATION CONFIGURATION
================================================================================

TestRail Project: Web Portal Tests (ID: 2)
Jira Project:     Web Portal Testing (WEBTEST)

Proceed with this configuration? (y/n): y

✓ Migration configuration saved to 'migration_config.json'

================================================================================
NEXT STEPS
================================================================================

1. Run the importer with the selected TestRail project:
   python3 importer.py

2. Run the migrator to migrate to the selected Jira project:
   python3 migrator.py

================================================================================
```

**Created file:** `migration_config.json`

```json
{
  "testrail_project_id": 2,
  "testrail_project_name": "Web Portal Tests",
  "jira_project_key": "WEBTEST",
  "jira_project_name": "Web Portal Testing"
}
```

---

## Step 3: Import Data from TestRail

Run the importer script to pull the selected TestRail project data into a local SQLite database:

```bash
python3 importer.py
```

This will:

- Connect to TestRail
- Fetch ONLY the selected project's data (users, test cases, suites, runs, results, etc.)
- Store everything in `testrail.db`

**Output:**

```text
================================================================================
IMPORTING SELECTED PROJECT: Web Portal Tests
Project ID: 2
================================================================================

================================================================================
FETCHING AND STORING TESTRAIL DATA
================================================================================

[1/15] Fetching Selected Project...
✓ Stored project: Web Portal Tests

[2/15] Fetching Users...
✓ Stored 12 users

[3/15] Fetching Case Types...
✓ Stored 3 case types

...

================================================================================
IMPORT COMPLETE!
================================================================================

Database saved to: testrail.db
Attachments saved to: attachments/

Summary:
  - Project: Web Portal Tests (ID: 2)
  - Target Jira Project: Web Portal Testing (WEBTEST)
  - Users: 12
  - Suites: 5
  - Sections: 23
  - Cases: 87
  - Milestones: 3
  - Plans: 8
  - Runs: 15
  - Tests: 145
  - Results: 298
  - Attachments: 12
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

Execute the migrator script to migrate to the selected Jira project:

```bash
python3 migrator.py
```

This will automatically use the Jira project from `migration_config.json` and:

1. **Migrate Test Cases** → Create Xray Tests
2. **Migrate Test Suites** → Create Xray Test Sets
3. **Migrate Test Runs** → Create Xray Test Executions
4. **Migrate Test Results** → Update Test Execution statuses
5. **Migrate Milestones** → Create Jira Versions

**Output:**

```text
================================================================================
MIGRATING TO JIRA PROJECT: Web Portal Testing
Project Key: WEBTEST
From TestRail Project: Web Portal Tests
================================================================================

================================================================================
TESTRAIL TO XRAY MIGRATION
================================================================================

Target: https://jira.company.com
Project: WEBTEST

================================================================================

Connecting to Jira/Xray...
✓ Connected to project: Web Portal Testing

[1/5] Migrating Test Cases...
  ✓ Migrated 10 test cases...
  ✓ Migrated 20 test cases...
✓ Migrated 87 test cases

[2/5] Migrating Test Suites as Test Sets...
✓ Migrated 5 test suites as test sets

[3/5] Migrating Test Runs as Test Executions...
  ✓ Migrated 5 test runs...
✓ Migrated 15 test runs as test executions

[4/5] Migrating Test Results...
  ✓ Migrated 50 test results...
✓ Migrated 145 test results

[5/5] Migrating Milestones as Versions...
✓ Migrated 3 milestones as versions

✓ Mapping saved to migration_mapping.json

================================================================================
MIGRATION COMPLETE!
================================================================================

Summary:
  - Test Cases migrated: 87
  - Test Sets created: 5
  - Test Executions created: 15
  - Milestones migrated: 3
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

### Issue: Test Execution Statuses Not Updating

**Problem:** Test executions are created but statuses remain as "TODO" instead of PASS/FAIL.

**Solution:** The Xray custom field needs to be added to your Jira screen configuration. See the detailed guides:

- **Quick Fix (5 steps):** [SCREEN_CONFIG_QUICKFIX.md](SCREEN_CONFIG_QUICKFIX.md)
- **Complete Guide:** [JIRA_SCREEN_CONFIG_GUIDE.md](JIRA_SCREEN_CONFIG_GUIDE.md)

**Summary:**

1. Go to Jira Settings → Issues → Screens
2. Find the screen used by Test Execution issue type
3. Add the "Test Execution Status" field to the screen
4. Re-run your migration

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

```text
test-rail-migrator/
├── config.json              # Credentials configuration (edit this!)
├── project_selector.py      # NEW: Interactive project selection tool
├── migration_config.json    # Generated project mapping (auto-generated)
├── importer.py              # Import selected TestRail project
├── migrator.py              # Migration to Xray
├── testrail.py              # TestRail API client
├── testrail.db              # Local SQLite database (auto-generated)
├── migration_mapping.json   # ID to Key mapping (auto-generated)
├── attachments/             # Downloaded attachments (auto-generated)
├── XRAY_API_REFERENCE.md    # Complete API documentation
└── README.md                # This file
```

## Multi-Project Workflow

If you have multiple TestRail projects to migrate:

1. Run `python3 project_selector.py` for the first project
2. Run `python3 importer.py` to import data
3. Run `python3 migrator.py` to migrate
4. Repeat steps 1-3 for each additional project

**Note:** Each run of `project_selector.py` will overwrite `migration_config.json`, so complete one full migration before starting the next.

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
