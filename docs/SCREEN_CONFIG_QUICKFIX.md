# Quick Fix: Test Execution Status Update Issue

## The Problem

Test statuses stay as "TODO" instead of showing PASS/FAIL after migration.

**Root Cause:** The Xray custom field for test execution status is not added to the Jira screen configuration.

---

## The Quick Fix (5 Steps)

### 1️⃣ Go to Screens Settings

```
Jira Settings (⚙️) → Issues → Screens
```

### 2️⃣ Find the Right Screen

Look for one of these:

- "Default Screen"
- "Xray Test Execution Screen"
- "[Your Project] Screen" (e.g., "RET Screen")

**How to verify it's the right screen:**

- Go to Screen Schemes → Find your project's scheme
- Check which screen is used for "Edit Issue"

### 3️⃣ Add the Missing Field

1. Click **"Configure"** next to the screen
2. Click **"Add Field"** button
3. Search for: **"Test Execution"** or **"customfield_10125"**
4. Select the field (usually called "Test Execution Status" or similar)
5. Click **"Add"**

### 4️⃣ Verify It Works

1. Open any Test Execution issue in your project
2. Click **"Edit"**
3. You should now see the test execution status field
4. Try changing a test status manually - if you can, the API will work too

### 5️⃣ Re-run Your Migration

```bash
python3 migrator.py
```

The test statuses should now update correctly! ✅

---

## If You Can't Find the Field

### Option A: Browse All Custom Fields

```
Settings (⚙️) → Issues → Custom Fields
```

Search the page (Ctrl+F) for "10125" to find the exact field name.

### Option B: Check Multiple Screens

Some projects use different screens for different operations. Check:

- Default Screen
- Edit Screen
- View Screen
- Workflow Screen

Add the field to all of them if needed.

---

## Still Not Working?

### Check These:

1. **Field Configuration**

   - Settings → Issues → Field Configurations
   - Make sure the field is NOT set to "Hidden"

2. **Permissions**

   - Make sure you have Jira Administrator access
   - Check that your API user has permission to edit custom fields

3. **Screen Scheme**

   - Settings → Issues → Issue Type Screen Schemes
   - Verify Test Execution issue type is mapped correctly

4. **Clear Cache**
   - Restart Jira (if you can)
   - Or wait 5-10 minutes for changes to propagate

---

## Visual Path

```
🏠 Jira Home
  ↓
⚙️ Settings
  ↓
📋 Issues
  ↓
🖥️ Screens
  ↓
📝 [Your Screen] → Configure
  ↓
➕ Add Field
  ↓
🔍 Search: "Test Execution Status"
  ↓
✅ Add → Save
```

---

## Test It Manually First

Before running the migration again:

1. Go to a Test Execution issue
2. Click "Edit"
3. Try to manually change a test status from "TODO" to "PASS"
4. If you can do it manually, the API will work

---

## Common Screen Names

| Screen Name                         | Likelihood             |
| ----------------------------------- | ---------------------- |
| Default Screen                      | ⭐⭐⭐⭐⭐ Very Common |
| Xray Test Execution Screen          | ⭐⭐⭐⭐ Common        |
| [Project] Screen (e.g., RET Screen) | ⭐⭐⭐ Common          |
| Workflow Screen                     | ⭐⭐ Less Common       |
| Custom Screen                       | ⭐ Rare                |

---

## Need Admin Access?

If you don't have Jira Administrator access:

1. Contact your Jira Administrator
2. Share this guide with them
3. Ask them to add the "Test Execution Status" field to the screen
4. Tell them it's for the Test Execution issue type

---

## Summary

**What to do:**

1. Add the Xray test execution status field to your Jira screen configuration
2. The field is usually called "Test Execution Status" or is `customfield_10125`
3. Test manually that you can edit test statuses
4. Re-run your migration

**Where to do it:**

- Settings → Issues → Screens → [Your Screen] → Configure → Add Field

**How long:** About 2-5 minutes once you find the right screen

After this, your test execution statuses will update automatically during migration! 🎉
