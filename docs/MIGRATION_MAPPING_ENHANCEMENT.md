# Migration Process Enhancement - Database Mapping Storage

## What Was Added

The migration process now automatically stores Jira issue mappings in the database for future reference and attachment validation.

## Changes Made

### 1. New Function: `store_mapping_in_database()`

**Location**: `migrator.py` (after `save_mapping()`)

**Purpose**: Stores the TestRail to Jira mappings in the database

**Features**:

- Creates `jira_mappings` table if it doesn't exist
- Stores all case, suite, and run mappings
- Uses INSERT OR REPLACE to safely handle re-runs
- Returns count of stored mappings

**Table Schema**:

```sql
CREATE TABLE jira_mappings (
    testrail_entity_type TEXT,      -- 'case', 'suite', or 'run'
    testrail_entity_id INTEGER,     -- TestRail ID
    jira_key TEXT,                  -- Jira issue key (e.g., 'MT-102')
    PRIMARY KEY (testrail_entity_type, testrail_entity_id)
)
```

### 2. Updated Migration Flow

**Modified**: `main()` function in `migrator.py`

**Before**:

```python
mapping = migrate_attachments(client, JIRA_PROJECT_KEY, mapping)

# Save mapping
save_mapping(mapping)

print("\n" + "=" * 80)
```

**After**:

```python
mapping = migrate_attachments(client, JIRA_PROJECT_KEY, mapping)

# Save mapping to file and database
save_mapping(mapping)
store_mapping_in_database(mapping)

print("\n" + "=" * 80)
```

## Benefits

1. **Persistent Storage**: Mappings are now stored in the database, not just in JSON file
2. **Easy Queries**: Can query which Jira issue corresponds to any TestRail entity
3. **Attachment Validation**: Attachments can be linked to correct Jira issues using database joins
4. **Audit Trail**: Database provides a reliable record of what was migrated where

## Usage Examples

### Query TestRail to Jira Mapping

```bash
# Get all case mappings
sqlite3 testrail.db "SELECT * FROM jira_mappings WHERE testrail_entity_type='case';"

# Find Jira issue for specific TestRail case
sqlite3 testrail.db "SELECT jira_key FROM jira_mappings WHERE testrail_entity_type='case' AND testrail_entity_id=2;"

# Count mappings by type
sqlite3 testrail.db "SELECT testrail_entity_type, COUNT(*) FROM jira_mappings GROUP BY testrail_entity_type;"
```

### Join with Attachments

```sql
-- Find all attachments with their Jira issue keys
SELECT
    a.filename,
    a.entity_type,
    a.entity_id,
    m.jira_key
FROM attachments a
LEFT JOIN jira_mappings m
    ON a.entity_type = m.testrail_entity_type
    AND a.entity_id = m.testrail_entity_id;
```

## Migration Process Flow

The complete migration now follows these steps:

1. **Connect to Jira/Xray**
2. **[1/6] Migrate Test Cases** → Creates mapping['cases']
3. **[2/6] Migrate Test Suites** → Creates mapping['suites']
4. **[3/6] Migrate Test Runs** → Creates mapping['runs']
5. **[4/6] Migrate Test Results**
6. **[5/6] Migrate Milestones** → Creates mapping['milestones']
7. **[6/6] Migrate Attachments** → Uses mappings to upload to correct issues
8. **Save Mapping to JSON file** → `migration_mapping.json`
9. **Store Mapping in Database** ← **NEW STEP**
10. **Display Summary**

## Backward Compatibility

- ✅ Existing code continues to work
- ✅ JSON file is still created (for backward compatibility)
- ✅ Database table is created automatically if missing
- ✅ Re-running migration safely updates mappings (INSERT OR REPLACE)

## Verification

After migration, verify mappings are stored:

```bash
# Check mapping counts
sqlite3 testrail.db "SELECT testrail_entity_type, COUNT(*) as count FROM jira_mappings GROUP BY testrail_entity_type;"

# Expected output:
# case|17
# run|7
# suite|1
```

## Next Migration Run

When you run `python migrator.py`, it will automatically:

1. Perform the full migration
2. Save mappings to JSON file
3. Store mappings in database
4. Upload attachments to correct issues using the mappings

No additional steps needed! 🎉
