# Migration Reports Guide

## Overview

The Migration Reports feature provides detailed statistics and analysis of both TestRail import and Xray export operations. You can generate three types of reports to track your migration progress.

## Report Types

### 1. Import Report

Shows detailed statistics about data imported from TestRail into the local SQLite database.

**Includes:**

- Total tables and records
- Breakdown by entity type (projects, users, test cases, runs, results, etc.)
- Test cases by priority and type
- Test runs by status (active/completed)
- Test results by status
- Milestones by status
- Attachments with file sizes and types

### 2. Export Report

Shows detailed statistics about data migrated from SQLite to Jira/Xray.

**Includes:**

- Total entities migrated
- Test Cases → Xray Test issues (with issue keys)
- Test Suites → Xray Test Set issues (with issue keys)
- Test Runs → Xray Test Execution issues (with issue keys)
- Milestones → Jira Versions
- Test Plans → Xray Test Plan issues
- Attachments uploaded

### 3. Combined Report

Comprehensive report showing both import and export data with comparison.

**Includes:**

- Complete import report
- Complete export report
- Side-by-side comparison of imported vs exported entities
- Pending items (not yet exported)
- Overall migration completion percentage

## Using Reports in the GUI

### Accessing Reports

1. Launch the application: `python3 ui.py`
2. Click on the **"Reports"** tab
3. Choose one of the report generation buttons:
   - **📥 Import Report**: Generate import statistics
   - **📤 Export Report**: Generate export statistics
   - **📊 Combined Report**: Generate complete comparison
   - **💾 Save Report to File**: Save current report as JSON

### Report Display

Reports are displayed in a scrollable text area with:

- Formatted sections with headers
- Emoji indicators (✓, 📥, 📤, 📊)
- Hierarchical breakdown of data
- Tabular comparison data
- Status information

### Saving Reports

1. Generate any report type
2. Click **"💾 Save Report to File"**
3. Report is saved as JSON with timestamp: `migration_report_YYYYMMDD_HHMMSS.json`
4. Location is shown in the status bar

## Using Reports from Command Line

### Generate Reports

```bash
# Combined report (default)
python3 report_generator.py

# Import report only
python3 report_generator.py import

# Export report only
python3 report_generator.py export

# Combined report (explicit)
python3 report_generator.py combined
```

### Output

Reports are:

1. Printed to console with formatting
2. Automatically saved to timestamped JSON file
3. Location of saved file is displayed

## Report Structure (JSON)

### Import Report

```json
{
  "status": "success",
  "timestamp": "2025-11-05T11:50:29",
  "database": "testrail.db",
  "summary": {
    "total_tables": 17,
    "total_records": 202,
    "tables_with_data": 17
  },
  "details": {
    "cases": {
      "count": 17,
      "type": "Test Cases"
    }
  },
  "entities": {
    "projects": {
      "count": 1,
      "items": [...]
    },
    "cases": {
      "count": 17,
      "by_priority": {...},
      "by_type": {...}
    },
    "attachments": {
      "count": 1,
      "total_size_mb": 0.77,
      "by_entity_type": {...}
    }
  }
}
```

### Export Report

```json
{
  "status": "success",
  "timestamp": "2025-11-05T11:50:29",
  "mapping_file": "migration_mapping.json",
  "summary": {
    "total_entities_migrated": 31,
    "entity_types": 4
  },
  "details": {
    "test_cases": {
      "count": 17,
      "testrail_ids": ["1", "2", "3", ...],
      "xray_keys": ["TM-1", "TM-2", "TM-3", ...],
      "type": "Test issues in Xray"
    }
  }
}
```

### Combined Report

```json
{
  "timestamp": "2025-11-05T11:50:29",
  "import": {...},
  "export": {...},
  "comparison": {
    "test_cases": {
      "imported": 17,
      "exported": 17,
      "pending": 0
    },
    "test_suites": {
      "imported": 1,
      "exported": 1,
      "pending": 0
    }
  }
}
```

## Example Output

### Import Report Sample

```
================================================================================
IMPORT REPORT
================================================================================
Generated: 2025-11-05 11:50:29
================================================================================

📥 IMPORT SUMMARY
--------------------------------------------------------------------------------
Database: testrail.db
Total Tables: 17
Tables with Data: 17
Total Records: 202

📊 DETAILED BREAKDOWN
--------------------------------------------------------------------------------

✓ Projects: 1
  - ID 1: Sample Project

✓ Test Cases: 17
  By Priority:
    - Priority 1: 3
    - Priority 2: 6
    - Priority 3: 8

✓ Attachments: 1
  - Total Size: 0.77 MB
  By Type:
    - case: 1
```

### Export Report Sample

```
================================================================================
EXPORT REPORT
================================================================================
Generated: 2025-11-05 11:50:29
================================================================================

📤 EXPORT SUMMARY
--------------------------------------------------------------------------------
Mapping File: migration_mapping.json
Total Entities Migrated: 31
Entity Types: 4

📊 DETAILED BREAKDOWN
--------------------------------------------------------------------------------

✓ Test Cases (Xray Test issues): 17
  - Xray Keys: TM-1, TM-2, TM-3, TM-4, TM-5
    ... and 12 more

✓ Test Executions (Xray Test Execution issues): 7
  - Xray Keys: TM-19, TM-20, TM-21, TM-22, TM-23, TM-24, TM-25
```

### Comparison Sample

```
================================================================================
📊 IMPORT vs EXPORT COMPARISON
================================================================================

Entity Type          Imported     Exported      Pending
------------------------------------------------------------
Test Cases                 17           17            0
Test Suites                 1            1            0
Test Runs                   7            7            0
Milestones                  5            5            0
Attachments                 1            1            0

------------------------------------------------------------
Overall Migration Completion: 100.0%
```

## Use Cases

### 1. Pre-Migration Assessment

Generate an **Import Report** after importing from TestRail to:

- Verify all data was imported correctly
- Understand the scope of migration
- Identify data distribution (priorities, types, statuses)
- Check attachment counts and sizes

### 2. Post-Migration Verification

Generate an **Export Report** after migrating to Xray to:

- Confirm all entities were created in Jira
- Get list of created issue keys
- Verify attachment uploads
- Document migration results

### 3. Migration Progress Tracking

Generate a **Combined Report** to:

- Track migration completion percentage
- Identify pending items not yet migrated
- Compare imported vs exported counts
- Generate audit trail

### 4. Troubleshooting

Use reports to:

- Identify missing entities
- Find data discrepancies
- Verify counts match between systems
- Debug migration issues

### 5. Documentation

Save reports to:

- Document migration history
- Create audit logs
- Share migration results with team
- Track multiple migration runs

## Tips

1. **Generate Import Report First**: Always run import before checking the import report
2. **Save Reports**: Use the save feature to keep historical records
3. **Compare Before/After**: Generate combined report to ensure complete migration
4. **Check Pending Items**: Review comparison section to find unmigrated entities
5. **Use for Auditing**: Save reports as proof of migration completion

## Automation

Reports can be integrated into scripts:

```python
from report_generator import MigrationReporter

reporter = MigrationReporter()

# Generate reports
import_report = reporter.generate_import_report()
export_report = reporter.generate_export_report()
combined_report = reporter.generate_combined_report()

# Print to console
reporter.print_report(combined_report, 'combined')

# Save to file
filename = reporter.save_report_to_file(combined_report)
print(f"Report saved to: {filename}")
```

## Report Files

All saved reports are timestamped:

- Format: `migration_report_YYYYMMDD_HHMMSS.json`
- Example: `migration_report_20251105_115029.json`
- Location: Current working directory

## Summary

The Migration Reports feature provides comprehensive visibility into your TestRail to Xray migration:

✅ Detailed import statistics from TestRail
✅ Complete export tracking to Jira/Xray
✅ Side-by-side comparison with completion percentage
✅ Save reports as JSON for audit trail
✅ Easy-to-use GUI and command-line interfaces
✅ Automatic timestamp and file naming
✅ Support for all entity types including attachments

Use reports to ensure complete, accurate migrations and maintain documentation of all migration activities.
