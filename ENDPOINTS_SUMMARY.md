# Xray API Endpoints Summary

## Quick Reference for JIRA 9.12.15 + Xray 7.9.1-j9

---

## Base URLs

```
Jira API:  {jira-url}/rest/api/2/
Xray API:  {jira-url}/rest/raven/1.0/
```

---

## Core Migration Endpoints

### 1. Create Test

```http
POST /rest/api/2/issue
Content-Type: application/json

{
  "fields": {
    "project": {"key": "PROJECT"},
    "summary": "Test Name",
    "description": "Test Description",
    "issuetype": {"name": "Test"}
  }
}
```

### 2. Update Test Steps

```http
PUT /rest/raven/1.0/api/testrun/{testKey}/step
Content-Type: application/json

[
  {
    "index": 1,
    "step": "Action",
    "data": "Test Data",
    "result": "Expected Result"
  }
]
```

### 3. Create Test Set

```http
POST /rest/api/2/issue
Content-Type: application/json

{
  "fields": {
    "project": {"key": "PROJECT"},
    "summary": "Test Set Name",
    "issuetype": {"name": "Test Set"}
  }
}
```

### 4. Add Tests to Test Set

```http
POST /rest/raven/1.0/api/testset/{testSetKey}/test
Content-Type: application/json

{
  "add": ["TEST-1", "TEST-2", "TEST-3"]
}
```

### 5. Create Test Execution

```http
POST /rest/api/2/issue
Content-Type: application/json

{
  "fields": {
    "project": {"key": "PROJECT"},
    "summary": "Test Execution Name",
    "issuetype": {"name": "Test Execution"}
  }
}
```

### 6. Add Tests to Test Execution

```http
POST /rest/raven/1.0/api/testexec/{execKey}/test
Content-Type: application/json

{
  "add": ["TEST-1", "TEST-2"]
}
```

### 7. Update Test Status in Execution

```http
POST /rest/raven/1.0/api/testexec/{execKey}/test/{testKey}/status
Content-Type: application/json

{
  "status": "PASS",
  "comment": "Test passed successfully",
  "defects": ["BUG-123"]
}
```

**Valid Statuses:** `TODO`, `EXECUTING`, `PASS`, `FAIL`, `ABORTED`, `BLOCKED`

### 8. Create Version (for Milestones)

```http
POST /rest/api/2/project/{projectKey}/version
Content-Type: application/json

{
  "name": "Release 1.0",
  "description": "First release",
  "startDate": "2025-01-01",
  "releaseDate": "2025-12-31",
  "released": false
}
```

### 9. Create Issue Link

```http
POST /rest/api/2/issueLink
Content-Type: application/json

{
  "type": {"name": "Relates"},
  "inwardIssue": {"key": "TEST-1"},
  "outwardIssue": {"key": "PRECON-1"}
}
```

### 10. Add Comment

```http
POST /rest/api/2/issue/{issueKey}/comment
Content-Type: application/json

{
  "body": "Comment text here"
}
```

---

## Bulk Import Endpoints

### Import Test Execution Results (Xray JSON)

```http
POST /rest/raven/1.0/import/execution
Content-Type: application/json

{
  "testExecutionKey": "EXEC-123",
  "tests": [
    {
      "testKey": "TEST-1",
      "status": "PASS",
      "comment": "Works perfectly"
    }
  ]
}
```

### Import JUnit Results

```http
POST /rest/raven/1.0/import/execution/junit
Content-Type: application/xml

<testsuites>...</testsuites>
```

### Import Cucumber Results

```http
POST /rest/raven/1.0/import/execution/cucumber
Content-Type: application/json

[
  {
    "id": "feature-1",
    "name": "Feature Name",
    ...
  }
]
```

---

## Query Endpoints

### Get Project

```http
GET /rest/api/2/project/{projectKey}
```

### Search Issues (JQL)

```http
GET /rest/api/2/search?jql=project=TEST+AND+issuetype=Test&maxResults=50
```

### Get Issue Details

```http
GET /rest/api/2/issue/{issueKey}
```

### Get Test Execution Results

```http
GET /rest/raven/1.0/api/testexec/{execKey}/test
```

### Export Tests

```http
GET /rest/raven/1.0/export/test?keys=TEST-1,TEST-2,TEST-3
```

---

## Authentication

All requests require HTTP Basic Authentication:

```python
import requests
from requests.auth import HTTPBasicAuth

response = requests.post(
    url,
    auth=HTTPBasicAuth('username', 'api_token'),
    headers={'Content-Type': 'application/json'},
    json=data
)
```

---

## Migration Flow

```
1. Extract from TestRail (main.py)
   ↓
2. Store in SQLite (testrail.db)
   ↓
3. Transform data (migrator.py)
   ↓
4. Create Tests via Jira API
   ↓
5. Create Test Sets via Jira API
   ↓
6. Link Tests to Sets via Xray API
   ↓
7. Create Test Executions via Jira API
   ↓
8. Add Tests to Executions via Xray API
   ↓
9. Update Test Statuses via Xray API
   ↓
10. Save mapping (migration_mapping.json)
```

---

## Status Codes

- `200` - OK (GET/PUT success)
- `201` - Created (POST success)
- `204` - No Content (DELETE success)
- `400` - Bad Request (invalid data)
- `401` - Unauthorized (auth failed)
- `403` - Forbidden (no permission)
- `404` - Not Found (resource missing)
- `500` - Internal Server Error

---

## Rate Limiting

- Recommended: 0.5-1 second delay between requests
- Use bulk APIs when possible
- Implement retry logic for 429 (Too Many Requests)

---

## Required Permissions

Your Jira user needs:

- Browse Projects
- Create Issues
- Edit Issues
- Add Comments
- Link Issues
- Manage Versions

---

## Issue Types Required

Ensure these exist in your project:

- `Test` (Xray issue type)
- `Test Set` (Xray issue type)
- `Test Execution` (Xray issue type)
- `Precondition` (optional)

---

## Common Errors & Solutions

### "Issue type 'Test' not found"

→ Install Xray plugin and enable issue types in project settings

### "No permission to create issues"

→ Grant user appropriate permissions in project role

### "Invalid status 'PASS'"

→ Check Xray is properly configured with default statuses

### "Too many requests"

→ Increase delay between API calls

---

## Testing Your Setup

Test API connectivity:

```bash
curl -u username:token \
  -H "Content-Type: application/json" \
  https://your-jira.com/rest/api/2/myself
```

Test Xray API:

```bash
curl -u username:token \
  https://your-jira.com/rest/raven/1.0/api/settings
```

---

## Resources

- **Xray Docs**: https://docs.getxray.app/display/XRAYSERVER/REST+API
- **Jira API**: https://docs.atlassian.com/software/jira/docs/api/REST/9.12.15/
- **Migration Tool**: `migrator.py` in this repository

---

## Support

For issues with:

- **TestRail extraction**: Check `main.py` and `testrail.py`
- **Xray migration**: Check `migrator.py`
- **API endpoints**: See `XRAY_API_REFERENCE.md`
- **Setup**: See `README.md`
