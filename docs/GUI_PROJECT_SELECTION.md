# GUI Project Selection Feature

## What's New

The GUI now includes an integrated **Project Selection** tab that replaces the need to run `project_selector.py` separately.

## New Workflow

### Step 1: Select Projects (New Tab!)

1. Launch the GUI:
   ```bash
   ./start_gui.sh
   # or
   python3 ui.py
   ```

2. Go to the **"1. Select Projects"** tab (first tab)

3. Click **"Refresh TestRail Projects"** to load all available TestRail projects

4. Click **"Refresh Jira Projects"** to load all existing Jira projects

5. Select a TestRail project from the left panel

6. Either:
   - Select an existing Jira project from the right panel, OR
   - Click **"Create New Jira Project"** to create a new one

7. Click **"Save Selection"** to save your configuration

### Step 2: Import Data

1. Go to the **"2. Import from TestRail"** tab

2. Verify your selected projects are shown at the top

3. Click **"Start Import"** to import the selected TestRail project

### Step 3: Export to Xray

1. Go to the **"3. Export to Xray"** tab

2. Verify your selected projects are shown at the top

3. Click **"Start Export"** to migrate to Jira/Xray

## Features

### Project Selection Tab

- **TestRail Projects Panel**
  - Lists all available TestRail projects
  - Shows project ID and status (Active/Completed)
  - Select by clicking on a project

- **Jira Projects Panel**
  - Lists all existing Jira projects
  - Shows project keys
  - Create new projects with a wizard dialog

- **Current Selection Display**
  - Shows currently selected projects
  - Green checkmarks when configured
  - Warning when not configured

### Create New Jira Project Dialog

When creating a new Jira project, you can specify:

- **Project Key** (2-10 uppercase letters)
- **Project Name**
- **Description** (optional)
- **Project Template**:
  - Scrum software development
  - Kanban software development
  - Basic software development

### Status Indicators

Throughout the GUI, you'll see:

- ✓ **Green text** = Configuration is complete
- ⚠ **Orange text** = Configuration is missing

## Migration Config

The tool creates `migration_config.json` with your selections:

```json
{
  "testrail_project_id": 2,
  "testrail_project_name": "Web Portal Tests",
  "jira_project_key": "WEBTEST",
  "jira_project_name": "Web Portal Testing"
}
```

This file is used by both the import and export processes.

## Updated Tab Names

- **Tab 1**: "1. Select Projects" (NEW!)
- **Tab 2**: "2. Import from TestRail" (formerly "Import from TestRail")
- **Tab 3**: "3. Export to Xray" (formerly "Export to Xray")
- **Tab 4**: "Reports"
- **Tab 5**: "Database Viewer"
- **Tab 6**: "Config"

## Benefits

1. **All-in-one GUI** - No need to switch between command-line and GUI
2. **Visual project selection** - See all projects at once
3. **Create Jira projects** - Create new projects without leaving the app
4. **Status tracking** - Always see which projects are selected
5. **Integrated workflow** - Seamless progression through all steps

## Backward Compatibility

- The command-line tools still work: `python3 project_selector.py`
- The GUI now offers the same functionality
- Both approaches use the same `migration_config.json` file

## Screenshots

### Project Selection Tab
- Left panel: TestRail projects list
- Right panel: Jira projects list with "Create New Project" button
- Top: Current selection status
- Bottom: Save and Clear buttons

### Import Tab
- Top: Selected projects display (green checkmarks or warning)
- Middle: Instructions
- Bottom: Console output

### Export Tab
- Top: Selected projects display (green checkmarks or warning)
- Middle: Instructions
- Bottom: Console output

## Tips

1. **Configure credentials first** - Go to the Config tab and set up your TestRail and Jira credentials before selecting projects

2. **Refresh to see latest** - Click refresh buttons to reload projects if you've made changes outside the GUI

3. **Verify selection** - Always check that green checkmarks appear before importing/exporting

4. **One project at a time** - Complete the full workflow (select → import → export) for one project before starting another

5. **Clear selection** - Use "Clear Selection" button to start fresh with different projects

## Troubleshooting

### "No project selection found" warning

**Solution**: Go to the "1. Select Projects" tab and save your selection

### "Failed to fetch TestRail projects"

**Solution**: Check your TestRail credentials in the Config tab

### "Failed to fetch Jira projects"

**Solution**: Check your Jira credentials in the Config tab

### Projects not loading

**Solution**: Ensure you have network connectivity and correct API URLs in config.json

## Example Workflow

1. **Launch GUI**
   ```bash
   ./start_gui.sh
   ```

2. **Configure Credentials** (Config tab)
   - Set TestRail URL, user, password
   - Set Jira URL, username, API token

3. **Select Projects** (Select Projects tab)
   - Refresh TestRail projects
   - Select "Web Portal Tests"
   - Refresh Jira projects
   - Click "Create New Project"
   - Enter: WEBTEST, "Web Portal Testing"
   - Save selection

4. **Import Data** (Import tab)
   - Verify green checkmarks showing selection
   - Click "Start Import"
   - Monitor console for progress

5. **Export to Xray** (Export tab)
   - Verify green checkmarks showing selection
   - Click "Start Export"
   - Monitor console for progress

6. **View Reports** (Reports tab)
   - Generate migration summary
   - Review statistics

## Summary

The GUI now provides a complete, integrated workflow for migrating TestRail projects to Jira/Xray without needing to use command-line tools. The project selection tab makes it easy to choose which projects to migrate and where to migrate them to.

**Enjoy the streamlined migration experience! 🚀**
