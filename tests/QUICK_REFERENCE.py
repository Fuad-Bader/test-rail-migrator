"""
TestRail to Xray Migrator - Quick Reference
============================================

GUI TABS:
---------
1. Configuration
   - Set TestRail credentials
   - Set Jira/Xray credentials
   - Test connections
   - Save config

2. Import from TestRail
   - Click "Start Import" to fetch all TestRail data
   - Monitor progress in console
   - Data saved to testrail.db

3. Export to Xray
   - Click "Start Export" to migrate to Jira
   - Creates Tests, Test Sets, Test Executions
   - Monitor progress in console
   - Mapping saved to migration_mapping.json

4. Database Viewer
   - Select table from dropdown
   - Browse up to 1000 rows
   - Export to CSV

KEYBOARD SHORTCUTS:
------------------
Ctrl+W : Close window
Ctrl+Q : Quit application

TABLES IN DATABASE:
------------------
- projects       : TestRail projects
- users          : TestRail users
- cases          : Test cases
- suites         : Test suites
- sections       : Test sections
- runs           : Test runs
- tests          : Tests in runs
- results        : Test results
- milestones     : Milestones/releases
- plans          : Test plans
- priorities     : Priority levels
- statuses       : Status definitions
- case_types     : Test case types
- case_fields    : Custom fields for cases
- result_fields  : Custom fields for results
- templates      : Test case templates

FILES CREATED:
-------------
- testrail.db              : SQLite database with TestRail data
- migration_mapping.json   : Maps TestRail IDs → Jira keys
- [table]_[time].csv      : CSV exports from viewer

TIPS:
-----
✓ Always configure credentials first
✓ Test connections before importing/exporting
✓ Import takes time for large datasets
✓ Export can be run multiple times (idempotent)
✓ Use Database Viewer to verify imported data
✓ Save mapping file for reference

TROUBLESHOOTING:
---------------
Problem: Import fails
→ Check TestRail credentials in Config tab
→ Verify network connectivity
→ Check console for error details

Problem: Export fails
→ Check Jira credentials in Config tab
→ Verify Xray is installed in Jira
→ Ensure project key is correct
→ Check issue types exist (Test, Test Execution, Test Set)

Problem: Database Viewer empty
→ Run import first
→ Check if testrail.db exists

Problem: GUI freezes
→ Operations run in background
→ Wait for completion (check console)
→ Don't close window during operations
"""

if __name__ == "__main__":
    print(__doc__)
