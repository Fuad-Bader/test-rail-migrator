# Multi-Project Migration Feature - Summary

## What Changed

The TestRail to Xray migrator has been enhanced with multi-project support. Here's what's new:

### New Files

1. **project_selector.py** - Interactive tool for project selection

   - Lists all TestRail projects
   - Lists all Jira projects
   - Allows creating new Jira projects
   - Saves configuration to `migration_config.json`

2. **migration_config.json** (generated) - Project mapping configuration

   ```json
   {
     "testrail_project_id": 2,
     "testrail_project_name": "Web Portal Tests",
     "jira_project_key": "WEBTEST",
     "jira_project_name": "Web Portal Testing"
   }
   ```

3. **MULTI_PROJECT_GUIDE.md** - Complete guide for using the new feature

### Modified Files

1. **importer.py**

   - Now requires `migration_config.json` to exist
   - Only imports the selected TestRail project (instead of all projects)
   - Shows selected project information at startup
   - Filters all data by selected project ID

2. **migrator.py**

   - Now reads `jira_project_key` from `migration_config.json`
   - Shows selected projects at startup
   - Maintains all existing functionality

3. **README.md**
   - Updated with new Step 2 (project selection)
   - Removed `jira_project_key` from `config.json` requirements
   - Added multi-project workflow section
   - Updated command examples

### Unchanged Files

- **config.json** - Still contains credentials (now without `jira_project_key`)
- **migrator.py** - Core migration logic unchanged
- **testrail.py** - API client unchanged

## New Workflow

### Before (Old Workflow)

```bash
# Edit config.json with project key
python main.py      # Import ALL projects
python migrator.py  # Migrate to hardcoded project
```

### After (New Workflow)

```bash
# Edit config.json (no project key needed)
python3 project_selector.py  # Select projects interactively
python3 importer.py           # Import ONLY selected project
python3 migrator.py           # Migrate to selected project
```

## Key Benefits

1. **Project Selection** - Choose which TestRail project to import
2. **Jira Project Options** - Select existing or create new Jira project
3. **Reduced Import Time** - Only imports one project's data
4. **Multi-Project Support** - Migrate different projects to different Jira projects
5. **Better Organization** - Keep test projects isolated in Jira
6. **Interactive UI** - User-friendly project selection interface

## Features

### TestRail Project Selection

- Lists all available projects
- Shows project status (Active/Completed)
- Allows selecting by number
- Displays project ID and name

### Jira Project Selection

- Lists all existing Jira projects
- Shows project keys
- Option to create new project
- Interactive project creation wizard

### Jira Project Creation

When creating a new project, you specify:

- **Project Key** (2-10 uppercase letters)
- **Project Name**
- **Project Description** (optional)
- **Project Template** (Scrum/Kanban/Basic)

### Data Filtering

The importer now filters:

- Templates by project_id
- Suites by project_id
- Sections by project_id
- Cases by suite_id (which belongs to project)
- Milestones by project_id
- Plans by project_id
- Runs by project_id
- Tests by run_id (which belongs to project)
- Results by test_id
- Attachments by case/result (which belong to project)

## Migration Scenarios

### Scenario 1: Single Project Migration

```bash
python3 project_selector.py  # Select Project A → Jira Project X
python3 importer.py
python3 migrator.py
```

### Scenario 2: Multiple Projects to Different Jira Projects

```bash
# Project 1
python3 project_selector.py  # Select Project A → Jira Project X
python3 importer.py
python3 migrator.py

# Project 2
python3 project_selector.py  # Select Project B → Jira Project Y
python3 importer.py           # Overwrites testrail.db
python3 migrator.py
```

### Scenario 3: Multiple Projects to Same Jira Project

```bash
# Project 1
python3 project_selector.py  # Select Project A → Jira Project X
python3 importer.py
python3 migrator.py

# Project 2 (to same Jira project)
python3 project_selector.py  # Select Project B → Jira Project X
python3 importer.py
python3 migrator.py
```

## Technical Implementation

### Project Selection Flow

```
project_selector.py
    ↓
1. Fetch TestRail projects via API
    ↓
2. Display projects and prompt user
    ↓
3. Fetch Jira projects via API
    ↓
4. Display projects or create new
    ↓
5. Save to migration_config.json
```

### Import Flow

```
importer.py
    ↓
1. Read migration_config.json
    ↓
2. Load SELECTED_PROJECT_ID
    ↓
3. Fetch only that project's data
    ↓
4. Filter all subsequent data by project_id
    ↓
5. Save to testrail.db
```

### Migration Flow

```
migrator.py
    ↓
1. Read migration_config.json
    ↓
2. Load jira_project_key
    ↓
3. Read testrail.db
    ↓
4. Migrate to selected Jira project
    ↓
5. Save mapping to migration_mapping.json
```

## Authentication

### TestRail

- Uses email + password from config.json
- No changes to authentication

### Jira

- Auto-detects API token vs password
- Supports both Cloud (Bearer token) and Server (Basic Auth)
- Uses credentials from config.json

## Error Handling

### Missing Configuration

- **Before running importer.py**: Checks for migration_config.json
- **Before running migrator.py**: Checks for migration_config.json
- **Clear error messages** with instructions

### API Errors

- **TestRail project fetch fails**: Shows error, exits
- **Jira project fetch fails**: Shows warning, offers to create new
- **Project creation fails**: Shows error details, allows retry

### User Cancellation

- **Ctrl+C during selection**: Graceful exit
- **Empty selection**: Re-prompts user
- **Invalid selection**: Shows error, re-prompts

## Backward Compatibility

### Not Fully Backward Compatible

The new version requires:

1. Running `project_selector.py` first
2. `migration_config.json` must exist
3. `jira_project_key` removed from `config.json`

### Migration Path for Existing Users

Old setup:

```json
// config.json
{
  "jira_project_key": "TEST"
}
```

New setup:

```bash
# Remove jira_project_key from config.json
# Run project selector
python3 project_selector.py
# Select projects
```

## Testing Recommendations

1. **Test with small project first**
2. **Verify project selection UI**
3. **Test Jira project creation**
4. **Verify filtering works correctly**
5. **Test multiple project migrations**
6. **Check error handling**

## Documentation Updates

1. **README.md** - Updated main guide
2. **MULTI_PROJECT_GUIDE.md** - New comprehensive guide
3. **This file** - Technical summary

## Usage Examples

### Example 1: Create New Jira Project

```bash
$ python3 project_selector.py

Available TestRail Projects:
  1. Web Portal Tests (ID: 2) - ✓ Active
Select project: 1

Available Jira Projects:
  1. Create new project
Select project: 1

Enter project key: WEBTEST
Enter project name: Web Portal Testing
Select template: 1

✓ Project created successfully!
✓ Configuration saved
```

### Example 2: Select Existing Jira Project

```bash
$ python3 project_selector.py

Available TestRail Projects:
  1. API Tests (ID: 3) - ✓ Active
Select project: 1

Available Jira Projects:
  1. Existing Project (EXIST)
  2. Create new project
Select project: 1

✓ Configuration saved
```

## Limitations

1. **Sequential processing** - One project at a time
2. **Database overwrite** - Each import overwrites testrail.db
3. **No project merging** - Each TestRail project must map to exactly one Jira project
4. **Config overwrite** - Each run of project_selector overwrites migration_config.json

## Future Enhancements (Potential)

1. **Batch mode** - Select and import multiple projects at once
2. **Project merge** - Merge multiple TestRail projects into one Jira project
3. **Incremental import** - Add to existing database instead of overwriting
4. **GUI version** - Graphical interface for project selection
5. **Scheduled migrations** - Automated periodic migrations

## Summary of Changes

| Component              | Status   | Changes                            |
| ---------------------- | -------- | ---------------------------------- |
| project_selector.py    | NEW      | Interactive project selection tool |
| migration_config.json  | NEW      | Generated configuration file       |
| importer.py            | MODIFIED | Now imports only selected project  |
| migrator.py            | MODIFIED | Now reads project from config      |
| config.json            | MODIFIED | Removed jira_project_key           |
| README.md              | MODIFIED | Updated with new workflow          |
| MULTI_PROJECT_GUIDE.md | NEW      | Complete feature guide             |

## Quick Start Reminder

```bash
# 1. Configure credentials
nano config.json

# 2. Select projects
python3 project_selector.py

# 3. Import selected project
python3 importer.py

# 4. Migrate to selected Jira project
python3 migrator.py
```

That's it! The multi-project support is now fully integrated and ready to use.
