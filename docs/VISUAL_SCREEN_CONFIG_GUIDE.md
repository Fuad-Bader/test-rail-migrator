# Visual Guide: Fixing Test Execution Status Updates

## Navigation Path

```
┌─────────────────────────────────────────────────────────────┐
│                                                             │
│  1. Click Settings Gear (⚙️) in Top Right                  │
│                                                             │
└─────────────────────────┬───────────────────────────────────┘
                          │
                          ▼
┌─────────────────────────────────────────────────────────────┐
│                                                             │
│  2. Select "Issues" from Dropdown                           │
│                                                             │
└─────────────────────────┬───────────────────────────────────┘
                          │
                          ▼
┌─────────────────────────────────────────────────────────────┐
│                                                             │
│  3. Click "Screens" in Left Sidebar                         │
│     (Under "FIELDS" section)                                │
│                                                             │
└─────────────────────────┬───────────────────────────────────┘
                          │
                          ▼
┌─────────────────────────────────────────────────────────────┐
│                                                             │
│  4. Find Your Screen:                                       │
│     • Default Screen (most common)                          │
│     • Xray Test Execution Screen                            │
│     • [Your Project] Screen (e.g., RET Screen)              │
│                                                             │
└─────────────────────────┬───────────────────────────────────┘
                          │
                          ▼
┌─────────────────────────────────────────────────────────────┐
│                                                             │
│  5. Click "Configure" next to the screen                    │
│                                                             │
└─────────────────────────┬───────────────────────────────────┘
                          │
                          ▼
┌─────────────────────────────────────────────────────────────┐
│                                                             │
│  6. Click "Add Field" button                                │
│                                                             │
└─────────────────────────┬───────────────────────────────────┘
                          │
                          ▼
┌─────────────────────────────────────────────────────────────┐
│                                                             │
│  7. Search for "Test Execution" or "customfield_10125"      │
│                                                             │
└─────────────────────────┬───────────────────────────────────┘
                          │
                          ▼
┌─────────────────────────────────────────────────────────────┐
│                                                             │
│  8. Select the field and click "Add"                        │
│                                                             │
└─────────────────────────┬───────────────────────────────────┘
                          │
                          ▼
┌─────────────────────────────────────────────────────────────┐
│                                                             │
│  9. DONE! ✅                                                │
│     Now re-run your migration                               │
│                                                             │
└─────────────────────────────────────────────────────────────┘
```

---

## Screen Configuration View

### Before (Missing Field)

```
┌──────────────────────────────────────────────────────┐
│  Screen: Default Screen                              │
├──────────────────────────────────────────────────────┤
│                                                      │
│  Fields on this screen:                              │
│                                                      │
│  ☑ Summary                                           │
│  ☑ Description                                       │
│  ☑ Issue Type                                        │
│  ☑ Priority                                          │
│  ☑ Assignee                                          │
│  ☑ Reporter                                          │
│  ☑ Labels                                            │
│  ☑ Components                                        │
│                                                      │
│  ❌ Test Execution Status (MISSING!)                 │
│                                                      │
│  [Add Field]                                         │
│                                                      │
└──────────────────────────────────────────────────────┘
```

### After (Field Added)

```
┌──────────────────────────────────────────────────────┐
│  Screen: Default Screen                              │
├──────────────────────────────────────────────────────┤
│                                                      │
│  Fields on this screen:                              │
│                                                      │
│  ☑ Summary                                           │
│  ☑ Description                                       │
│  ☑ Issue Type                                        │
│  ☑ Priority                                          │
│  ☑ Assignee                                          │
│  ☑ Reporter                                          │
│  ☑ Labels                                            │
│  ☑ Components                                        │
│  ☑ Test Execution Status ✅ (ADDED!)                 │
│                                                      │
│  [Add Field]                                         │
│                                                      │
└──────────────────────────────────────────────────────┘
```

---

## Finding the Right Screen

### Option 1: Through Screen Schemes

```
Settings → Issues → Screen Schemes
                      │
                      ▼
            Find your project's scheme
                      │
                      ▼
              Click "Configure"
                      │
                      ▼
        Note the screen for "Edit Issue"
                      │
                      ▼
        Go back to Screens and find it
```

### Option 2: Through Issue Type Screen Schemes

```
Settings → Issues → Issue Type Screen Schemes
                      │
                      ▼
            Find your project's scheme
                      │
                      ▼
              Click "Configure"
                      │
                      ▼
        Find "Test Execution" issue type
                      │
                      ▼
            Note which screen it uses
                      │
                      ▼
         Go back to Screens and find it
```

---

## Test Before & After

### Before Configuration (Won't Work ❌)

```
API Call:
POST /rest/raven/1.0/import/execution
{
  "testExecutionKey": "RET-25",
  "tests": [
    {
      "testKey": "RET-1",
      "status": "PASS"
    }
  ]
}

Response:
❌ Error 400: Field 'customfield_10125' cannot be set.
   It is not on the appropriate screen.

Result:
Test status remains: TODO
```

### After Configuration (Works ✅)

```
API Call:
POST /rest/raven/1.0/import/execution
{
  "testExecutionKey": "RET-25",
  "tests": [
    {
      "testKey": "RET-1",
      "status": "PASS"
    }
  ]
}

Response:
✅ 200 OK

Result:
Test status updated: PASS ✓
```

---

## Verification Steps

### Step 1: Manual Edit Test

```
1. Go to a Test Execution issue (e.g., RET-25)
2. Click "Edit" button
3. Look for "Test Execution Status" or similar field
4. Try changing a test status from TODO to PASS
```

**If you can do this manually → API will work too! ✅**

### Step 2: Re-run Migration

```bash
cd /home/fuad/Documents/Github/test-rail-migrator
python3 migrator.py
```

### Step 3: Check Results

```
1. Open Test Execution issue in Jira
2. Check test statuses
3. Should show: PASS, FAIL, SKIP (not TODO)
```

---

## Common Mistakes

### ❌ Wrong Screen

```
You edited: "View Issue Screen"
You need:   "Edit Issue Screen" or "Default Screen"
```

### ❌ Wrong Field

```
You added:  "Status" (built-in Jira field)
You need:   "Test Execution Status" (Xray custom field)
```

### ❌ Wrong Issue Type

```
You configured: "Test" issue type screen
You need:       "Test Execution" issue type screen
```

---

## Quick Checklist

```
□ I have Jira Administrator access
□ I found Settings → Issues → Screens
□ I identified the correct screen (Default/Xray/Project Screen)
□ I clicked "Configure" on that screen
□ I clicked "Add Field"
□ I searched for "Test Execution" or "customfield_10125"
□ I added the field to the screen
□ I can manually edit test statuses in a Test Execution issue
□ I re-ran the migration
□ Test statuses now show PASS/FAIL instead of TODO
```

---

## Still Need Help?

### Contact Your Jira Admin

Send them this message:

```
Hi [Admin Name],

I need help configuring a Jira screen for our Xray test migration.

What I need:
- Add the "Test Execution Status" field (customfield_10125)
  to the screen used by the "Test Execution" issue type

Where to do it:
Settings → Issues → Screens → [Screen Name] → Configure → Add Field

Why: This allows our migration tool to update test statuses via API.

Guides:
- Quick fix: SCREEN_CONFIG_QUICKFIX.md
- Complete guide: JIRA_SCREEN_CONFIG_GUIDE.md

Thanks!
```

---

## Success Indicators

### ✅ You Did It Right When:

1. You can manually edit test statuses in Test Execution issues
2. The migration script runs without "field cannot be set" errors
3. Test statuses show PASS/FAIL/SKIP (not TODO) after migration
4. The Xray test execution report shows actual results

### ❌ Something's Still Wrong When:

1. You still can't edit test statuses manually
2. Migration still gives field errors
3. Test statuses remain as TODO
4. Xray report shows no test results

→ Double-check you edited the correct screen for the Test Execution issue type

---

## Time Estimate

- **Finding the screen**: 2-5 minutes
- **Adding the field**: 1 minute
- **Testing**: 2 minutes
- **Total**: ~5-10 minutes

---

## Final Check

After configuration, run this test:

```bash
# Test manually in Jira UI:
1. Edit a Test Execution issue
2. Change a test status
3. If you can → You're done! ✅

# Test via migration:
python3 migrator.py

# Check results:
Open Test Execution in Jira and verify statuses
```

**If all tests pass → Configuration is correct! 🎉**
