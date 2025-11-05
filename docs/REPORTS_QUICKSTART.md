# Report Generation - Quick Start Guide

## What's New?

A new **Reports** tab has been added to the GUI that provides detailed statistics and analysis of your migration.

## Quick Access

1. Launch the application:

   ```bash
   python3 ui.py
   ```

2. Click on the **"Reports"** tab (3rd tab)

3. You'll see 4 buttons:
   - **📥 Import Report** - Shows what was imported from TestRail
   - **📤 Export Report** - Shows what was migrated to Xray
   - **📊 Combined Report** - Shows both with comparison and completion %
   - **💾 Save Report to File** - Saves current report as JSON

## Example Workflow

### After Import

1. Click **"Import Report"**
2. See statistics like:
   - Total test cases: 17
   - Test runs: 7
   - Attachments: 1 (0.77 MB)
   - Results: 60
   - And more...

### After Export

1. Click **"Export Report"**
2. See migration results:
   - Test Cases created: 17 (with Xray keys)
   - Test Executions created: 7
   - Attachments uploaded: 1
   - And more...

### Check Progress

1. Click **"Combined Report"**
2. See comparison table:

   ```
   Entity Type       Imported    Exported    Pending
   ------------------------------------------------
   Test Cases             17          17          0
   Test Suites             1           1          0
   Test Runs               7           7          0
   Attachments             1           1          0

   Overall Migration Completion: 100.0%
   ```

### Save for Records

1. After viewing any report
2. Click **"Save Report to File"**
3. Report saved as: `migration_report_20251105_115029.json`

## Command Line Alternative

You can also generate reports from terminal:

```bash
# Combined report
python3 report_generator.py

# Just import stats
python3 report_generator.py import

# Just export stats
python3 report_generator.py export
```

## What You Get

### Import Report Details

- ✓ Total tables and records
- ✓ Projects with names
- ✓ Test cases by priority and type
- ✓ Test runs by status
- ✓ Test results by status
- ✓ Attachments with sizes

### Export Report Details

- ✓ Total entities migrated
- ✓ Xray issue keys created
- ✓ Test Cases → Test issues
- ✓ Test Suites → Test Set issues
- ✓ Test Runs → Test Execution issues
- ✓ Attachments uploaded

### Combined Report Extras

- ✓ Side-by-side comparison
- ✓ Pending items count
- ✓ Completion percentage
- ✓ Full audit trail

## Use Cases

**Before Migration**

- Check what you're about to migrate
- Understand data scope
- Plan resources

**During Migration**

- Track progress
- Verify steps completed
- Identify issues early

**After Migration**

- Confirm completion
- Generate documentation
- Share results with team

**Auditing**

- Save reports for compliance
- Track multiple migrations
- Compare migration runs

## Benefits

✅ **No Extra Setup** - Works immediately
✅ **Fast** - Generates in seconds
✅ **Comprehensive** - All details included
✅ **Easy to Use** - Just click a button
✅ **Exportable** - Save as JSON for sharing
✅ **Audit Trail** - Timestamped records

## Tips

1. **Generate After Each Step**: Run import report after import, export report after export
2. **Use Combined for Final Check**: Best way to verify complete migration
3. **Save Important Reports**: Use save button to keep records
4. **Share with Team**: Export JSON and share migration status
5. **Compare Multiple Runs**: Save reports from different migration attempts

## Troubleshooting

**Report shows error?**

- Make sure you've run import/export first
- Check that database file exists
- Verify mapping file exists for export report

**No data in report?**

- Run import first for import report
- Run export first for export report
- Check console for any error messages

**Want more details?**

- See full documentation: REPORTS_GUIDE.md
- Check feature summary: REPORT_FEATURE_SUMMARY.md

## Summary

The Reports feature gives you complete visibility into your migration:

- 📥 **Import**: See what came from TestRail
- 📤 **Export**: See what went to Xray
- 📊 **Compare**: Check completion status
- 💾 **Save**: Keep permanent records

It's the perfect tool to verify, track, and document your migrations!
