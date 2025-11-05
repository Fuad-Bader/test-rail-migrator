# Jira Screen Configuration Guide - Fix Test Execution Status Updates

## Problem Overview

When migrating test executions from TestRail to Xray, the test statuses remain as "TODO" instead of showing the actual results (PASS, FAIL, etc.). This happens because the custom field `customfield_10125` (used by Xray for test execution status) is not added to the appropriate Jira screen.

**Error Message You Might See:**

```
Field 'customfield_10125' cannot be set. It is not on the appropriate screen, or unknown.
```

## Solution

Add the Xray test execution fields to the Test Execution issue type screen configuration.

---

## Step-by-Step Configuration Guide

### Step 1: Access Jira Administration

1. Log into your Jira instance as an administrator
2. Click on the **Settings** gear icon (⚙️) in the top right corner
3. Select **"Issues"** from the dropdown menu

![Jira Settings Menu]

### Step 2: Navigate to Screens

1. In the left sidebar under **"FIELDS"**, click on **"Screens"**
2. You'll see a list of all screens in your Jira instance

![Screens List]

### Step 3: Find the Test Execution Screen

You need to identify which screen is used for the Test Execution issue type. There are several ways to find this:

#### Option A: Through Screen Schemes

1. Click on **"Screen Schemes"** in the left sidebar
2. Look for schemes that mention "Xray" or your project name
3. Click on the scheme to see which screens it uses
4. Note the screen used for **"Edit Issue"** or **"Default Screen"**

#### Option B: Through Issue Type Screen Schemes

1. Click on **"Issue Type Screen Schemes"** in the left sidebar
2. Find the scheme associated with your project (e.g., "RET" project)
3. Click **"Configure"** next to the scheme
4. Find the **"Test Execution"** issue type in the list
5. Note which screen scheme it uses
6. Go back to Screen Schemes and find that scheme
7. Note the screen used for editing

#### Option C: Direct Search

Common screen names for Xray:

- "Default Screen"
- "Xray Test Execution Screen"
- "Test Management Screen"
- Your project name + "Screen"

### Step 4: Edit the Screen

1. Once you've identified the correct screen, click on **"Configure"** next to it
2. You'll see a list of all fields currently on the screen
3. Look for Xray-related fields (they usually have "Xray" or "Test" in the name)

### Step 5: Add the Missing Field

1. Click the **"Add Field"** button (usually in the top right or bottom of the field list)
2. In the search box, type: **"Test Execution"** or **"customfield_10125"**
3. Look for these Xray fields:
   - **"Test Execution Status"** or similar
   - **"Test Execution Results"** or similar
   - Any field related to test execution status

**Important Fields to Add:**

- Custom field for test execution status (customfield_10125 or similar)
- Test Run custom field (if exists)
- Test Execution Status field

4. Select the field(s) and click **"Add"**

### Step 6: Position the Field (Optional)

1. The newly added field will appear in the list
2. You can drag and drop it to position it where you want
3. Common positions:
   - Near other Xray fields
   - In a dedicated "Test Execution Details" section
   - At the bottom of the screen

### Step 7: Add to View Screen (if needed)

Repeat Steps 4-6 for the **"View Issue"** screen if you want the field to be visible when viewing test executions.

### Step 8: Verify the Configuration

1. Go to your project (e.g., RET project)
2. Open any Test Execution issue
3. Click **"Edit"** or use the pencil icon
4. Check if you can now see the test execution status field
5. You should be able to manually change test statuses

### Step 9: Test the API

After configuring the screen, test if the migration can now update statuses:

1. Go to your migration tool
2. Run the export again (or just the test results migration part)
3. Check if test execution statuses are now being updated correctly

---

## Alternative: Using the Field Configuration

If adding to screens doesn't work, you might need to check the field configuration:

### Step 1: Access Field Configurations

1. Go to **Settings** (⚙️) > **Issues**
2. Click on **"Field Configurations"** in the left sidebar
3. Find the configuration used by your project

### Step 2: Edit Field Configuration

1. Click **"Configure"** next to the field configuration
2. Find the Xray custom fields in the list
3. Make sure they are **not** set to "Hidden"
4. Click on the field to edit it
5. Ensure **"Renderer"** is set appropriately

---

## Finding the Exact Field Name

If you're not sure which field is `customfield_10125`:

### Method 1: Through Jira API

1. Open your browser's developer tools (F12)
2. Go to a Test Execution issue
3. Click "Edit"
4. In the Network tab, look for API calls to `/rest/api/2/issue/`
5. Check the response to see field mappings

### Method 2: Through Issue Edit Screen

1. Open a Test Execution issue
2. Click "Edit"
3. Right-click on any field and select "Inspect Element"
4. Look for `data-field-id` or `id` attributes that show `customfield_10125`

### Method 3: Using Custom Field Admin

1. Go to **Settings** (⚙️) > **Issues**
2. Click **"Custom Fields"** in the left sidebar
3. Use browser search (Ctrl+F) to find "10125"
4. This will show you the exact field name

---

## Xray-Specific Configuration

### For Xray Server/Data Center

1. Go to **Project Settings** > **Xray Settings**
2. Check **"Test Execution Settings"**
3. Ensure that test execution fields are enabled
4. Verify that custom fields are properly configured

### Verify Xray Issue Types

1. Go to **Settings** (⚙️) > **Issues** > **Issue Types**
2. Confirm these Xray issue types exist:
   - Test
   - Test Execution
   - Test Set
   - Test Plan
   - Pre-Condition (optional)

---

## Common Screen Names to Check

Depending on your Jira configuration, check these screens:

1. **"Default Screen"** - Most common
2. **"Xray Test Execution Screen"**
3. **"Workflow Screen"**
4. **"[Your Project] Screen"** (e.g., "RET Screen")
5. **"Test Management Screen"**
6. **"Agile Screen"** (if using Scrum/Kanban)

---

## Troubleshooting

### Issue: Can't Find the Screen

**Solution:**

1. Create a test Test Execution issue manually
2. Try to edit it and note which fields you can see
3. Go to the screen configuration and add the missing Xray fields

### Issue: Field Appears But Can't Be Edited

**Solution:**

1. Check field configuration - ensure it's not "Hidden"
2. Check user permissions - you might need Xray permissions
3. Check if the field is locked by a workflow

### Issue: Field Added But API Still Fails

**Solution:**

1. Clear Jira cache (if you have admin access)
2. Restart Jira instance (if possible)
3. Wait a few minutes for changes to propagate
4. Try using a different field if multiple test execution fields exist

### Issue: Multiple Custom Fields

If you see multiple custom fields for test execution:

1. Note the ID of each (customfield_10125, customfield_10126, etc.)
2. Add all of them to the screen
3. Test which one works with the API
4. Update your migration script to use the correct field ID

---

## After Configuration

### Verify It Works

1. **Manual Test:**

   - Open a Test Execution issue
   - Edit it manually
   - Try to change test statuses
   - If you can change them manually, the API should work too

2. **API Test:**
   ```bash
   # From your migration directory
   python3 migrator.py
   ```
3. **Check Results:**
   - Open the Test Execution issues in Jira
   - Verify that test statuses show PASS, FAIL, etc. instead of TODO
   - Check the test execution report in Xray

### Re-run Migration

If you want to update the existing Test Executions with correct statuses:

1. Delete the test results in Xray (optional)
2. Re-run the export from your migration tool
3. Or manually update statuses in Jira UI

---

## Quick Reference Checklist

- [ ] Login as Jira Administrator
- [ ] Go to Settings > Issues > Screens
- [ ] Find the screen used by Test Execution issue type
- [ ] Click "Configure" on that screen
- [ ] Click "Add Field"
- [ ] Search for "Test Execution Status" or "customfield_10125"
- [ ] Add the field to the screen
- [ ] Save changes
- [ ] Test by editing a Test Execution issue manually
- [ ] Re-run your migration to verify API works

---

## Important Notes

1. **Admin Access Required**: You need Jira Administrator privileges to modify screens
2. **Backup First**: Consider backing up your screen configuration before making changes
3. **Test Environment**: If possible, test changes in a non-production environment first
4. **Xray License**: Ensure your Xray license is valid and active
5. **Field Permissions**: Make sure users have permission to edit Xray custom fields

---

## Visual Guide Summary

```
Settings (⚙️)
    └── Issues
        └── Screens (or Screen Schemes > Issue Type Screen Schemes)
            └── Find: Test Execution Screen
                └── Configure
                    └── Add Field
                        └── Search: "Test Execution Status" or "customfield_10125"
                            └── Add
                                └── Save
```

---

## Need More Help?

If you're still having issues:

1. **Check Xray Documentation**: [https://docs.getxray.app/](https://docs.getxray.app/)
2. **Xray Support**: Contact Xray support with your screen configuration
3. **Jira Logs**: Check Jira logs for more detailed error messages
4. **Community**: Ask on Atlassian Community forums

---

## Additional Resources

- **Xray Screen Configuration**: [Xray Server Documentation](https://docs.getxray.app/display/XRAY/Test+Execution+Screen)
- **Jira Screen Administration**: [Atlassian Documentation](https://confluence.atlassian.com/adminjiraserver/managing-screens-938847165.html)
- **Custom Fields**: [Jira Custom Fields Guide](https://confluence.atlassian.com/adminjiraserver/managing-custom-fields-938847222.html)

---

## Summary

The key to fixing test execution status updates is ensuring that the Xray test execution custom field (`customfield_10125`) is added to the screen configuration for the Test Execution issue type. This allows both the Jira UI and API to update test statuses.

**Steps in Brief:**

1. Settings > Issues > Screens
2. Find Test Execution screen
3. Add "Test Execution Status" field
4. Save and test

After this configuration, your migration tool should be able to update test statuses automatically! ✅
