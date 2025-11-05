# TestRail to Xray Migrator - GUI

A graphical user interface for migrating test data from TestRail to Xray (Jira).

## Features

- **Import from TestRail**: Fetch and store all test data from TestRail into a local SQLite database
- **Export to Xray**: Migrate stored data to Xray/Jira, creating Tests, Test Sets, and Test Executions
- **Migration Reports**: Generate detailed statistics and progress tracking for import/export operations
- **Database Viewer**: Browse and explore the imported TestRail data with a table viewer
- **Configuration Manager**: Easy setup and testing of TestRail and Jira connections

## Installation

1. Install the required Python packages:

```bash
pip install -r requirements.txt
```

2. Ensure you have the following packages (should be in requirements.txt):
   - tkinter (usually comes with Python)
   - requests
   - sqlite3 (comes with Python)

## Running the GUI

Launch the application:

```bash
python ui.py
```

## Usage Guide

### 1. Configuration Tab

Before starting any migration, configure your credentials:

**TestRail Configuration:**

- TestRail URL (e.g., `https://your-company.testrail.io/`)
- TestRail User (email address)
- TestRail Password or API Key

**Jira/Xray Configuration:**

- Jira URL (e.g., `http://localhost:8080` or `https://your-company.atlassian.net`)
- Jira Username
- Jira Password or API Token
- Jira Project Key (e.g., `RET`)

Click **"Save Configuration"** after entering your credentials.

Use **"Test TestRail Connection"** and **"Test Jira Connection"** buttons to verify your settings.

### 2. Import from TestRail Tab

Import all data from TestRail:

1. Ensure your TestRail credentials are configured
2. Click **"Start Import"**
3. Monitor progress in the console
4. Data is saved to `testrail.db` SQLite database

The import fetches:

- Projects
- Users
- Test Cases
- Test Suites
- Test Runs
- Test Results
- Milestones
- Attachments (downloaded to `attachments/` directory)
- And more...

### 3. Export to Xray Tab

Migrate data to Xray/Jira:

1. Ensure you have imported TestRail data first
2. Configure your Jira/Xray credentials
3. Click **"Start Export"**
4. Monitor progress in the console

The export creates:

- **Tests**: TestRail test cases → Xray Test issues
- **Test Sets**: TestRail suites → Xray Test Set issues
- **Test Executions**: TestRail runs → Xray Test Execution issues
- **Versions**: TestRail milestones → Jira Versions
- **Attachments**: Uploads files to corresponding Jira issues

A mapping file (`migration_mapping.json`) is created to track the migration.

For detailed information about attachment migration, see [ATTACHMENT_MIGRATION.md](../ATTACHMENT_MIGRATION.md).

### 4. Reports Tab

Generate detailed migration reports:

1. Choose a report type:
   - **Import Report**: Statistics about data imported from TestRail
   - **Export Report**: Statistics about data migrated to Xray
   - **Combined Report**: Complete comparison with migration completion percentage
2. View the formatted report in the output area
3. Click **"Save Report to File"** to save as timestamped JSON file

Reports include:

- Entity counts by type (test cases, runs, results, attachments, etc.)
- Breakdown by status, priority, type
- Xray issue keys created
- Import vs Export comparison
- Migration completion percentage

For detailed information about reports, see [REPORTS_GUIDE.md](../REPORTS_GUIDE.md).

### 5. Database Viewer Tab

Browse the imported TestRail data:

1. Select a table from the dropdown menu
2. View up to 1000 rows of data in the table
3. Use **"Refresh Tables"** to reload available tables
4. Click **"Export to CSV"** to save the current table to a CSV file

Available tables include:

- `projects`, `users`, `cases`, `suites`, `runs`, `tests`, `results`
- And many more...

## Tips

- **Long Running Operations**: Import and export can take time depending on the size of your TestRail data. Be patient and monitor the console output.
- **Database Location**: The SQLite database (`testrail.db`) is stored in the same directory as the scripts.
- **Error Handling**: If an import or export fails, check the console output for error details.
- **Incremental Migration**: You can run the import multiple times - it will update existing records.

## Troubleshooting

### Import Fails

- Verify TestRail credentials in the Config tab
- Check network connectivity to TestRail
- Ensure you have API access enabled in TestRail

### Export Fails

- Verify Jira/Xray credentials
- Ensure the Jira project exists
- Check that Xray is installed and configured in Jira
- Verify you have correct issue types (Test, Test Execution, Test Set)

### Database Viewer Empty

- Run an import first to populate the database
- Check if `testrail.db` file exists in the project directory

## Files Generated

- `testrail.db`: SQLite database containing imported TestRail data
- `migration_mapping.json`: Mapping of TestRail IDs to Jira issue keys
- `[tablename]_[timestamp].csv`: CSV exports from the database viewer

## Command Line Alternative

You can still run the scripts directly without the GUI:

```bash
# Import from TestRail
python importer.py

# Export to Xray
python migrator.py
```

## Requirements

- Python 3.7+
- TestRail account with API access
- Jira instance with Xray installed
- Network access to both TestRail and Jira

## Notes

- The UI runs import/export operations in separate threads to keep the interface responsive
- Console output is displayed in real-time
- Configuration is stored in `config.json`
