# Xray API Reference for Migration

## System Versions

- **JIRA**: 9.12.15
- **Xray**: 7.9.1-j9 (Server/Data Center)

## API Endpoints Used

This document outlines all the Xray and Jira REST API endpoints used in the migration process.

---

## Base URLs

### Jira REST API v2

```
{jira-url}/rest/api/2/
```

### Xray REST API v1.0 (Server/Data Center)

```
{jira-url}/rest/raven/1.0/
```

---

## 1. JIRA Core API Endpoints

### 1.1 Project Operations

- **Get Project**
  - `GET /rest/api/2/project/{projectKey}`
  - Returns project details including available issue types

### 1.2 Issue Operations

- **Create Issue**

  - `POST /rest/api/2/issue`
  - Body: `{fields: {project, summary, description, issuetype}}`
  - Used to create: Tests, Test Sets, Test Executions, Preconditions

- **Update Issue**

  - `PUT /rest/api/2/issue/{issueKey}`
  - Body: `{fields: {...}}`

- **Get Issue**
  - `GET /rest/api/2/issue/{issueKey}`
  - Returns complete issue details

### 1.3 Search

- **Search Issues (JQL)**
  - `GET /rest/api/2/search?jql={query}&maxResults={n}&fields={fields}`
  - Used to find existing issues and verify migration

### 1.4 Comments

- **Add Comment**
  - `POST /rest/api/2/issue/{issueKey}/comment`
  - Body: `{body: "comment text"}`

### 1.5 Issue Links

- **Create Issue Link**
  - `POST /rest/api/2/issueLink`
  - Body: `{type: {name: "Relates"}, inwardIssue: {key}, outwardIssue: {key}}`

### 1.6 Versions/Releases

- **Create Version**
  - `POST /rest/api/2/project/{projectKey}/version`
  - Body: `{name, description, startDate, releaseDate, released}`
  - Used for migrating TestRail milestones

---

## 2. Xray Specific API Endpoints

### 2.1 Test Management

#### Create Test

Tests are created using standard Jira issue creation with `issuetype: "Test"`

```
POST /rest/api/2/issue
Body: {
  fields: {
    project: {key: "PROJECT"},
    summary: "Test name",
    description: "Test description",
    issuetype: {name: "Test"}
  }
}
```

#### Update Test Steps

- **Endpoint**: `PUT /rest/raven/1.0/api/testrun/{testKey}/step`
- **Body**:

```json
[
  {
    "index": 1,
    "step": "Action to perform",
    "data": "Test data",
    "result": "Expected result"
  },
  {
    "index": 2,
    "step": "Next action",
    "data": "More data",
    "result": "Expected outcome"
  }
]
```

### 2.2 Test Set Management

#### Create Test Set

Test Sets are created using standard Jira issue creation with `issuetype: "Test Set"`

```
POST /rest/api/2/issue
Body: {
  fields: {
    project: {key: "PROJECT"},
    summary: "Test Set name",
    description: "Description",
    issuetype: {name: "Test Set"}
  }
}
```

#### Add Tests to Test Set

- **Endpoint**: `POST /rest/raven/1.0/api/testset/{testSetKey}/test`
- **Body**:

```json
{
  "add": ["TEST-123", "TEST-124", "TEST-125"]
}
```

#### Remove Tests from Test Set

- **Body**:

```json
{
  "remove": ["TEST-123"]
}
```

### 2.3 Test Execution Management

#### Create Test Execution

Test Executions are created using standard Jira issue creation with `issuetype: "Test Execution"`

```
POST /rest/api/2/issue
Body: {
  fields: {
    project: {key: "PROJECT"},
    summary: "Test Execution name",
    description: "Description",
    issuetype: {name: "Test Execution"}
  }
}
```

#### Add Tests to Test Execution

- **Endpoint**: `POST /rest/raven/1.0/api/testexec/{testExecKey}/test`
- **Body**:

```json
{
  "add": ["TEST-123", "TEST-124"]
}
```

#### Update Test Status in Test Execution

- **Endpoint**: `POST /rest/raven/1.0/api/testexec/{testExecKey}/test/{testKey}/status`
- **Body**:

```json
{
  "status": "PASS",
  "comment": "Test passed successfully",
  "defects": ["BUG-123", "BUG-456"]
}
```

**Available Statuses**:

- `TODO` - Not executed
- `EXECUTING` - In progress
- `PASS` - Passed
- `FAIL` - Failed
- `ABORTED` - Aborted
- `BLOCKED` - Blocked

#### Get Test Execution Results

- **Endpoint**: `GET /rest/raven/1.0/api/testexec/{testExecKey}/test`
- Returns list of tests and their statuses in the execution

### 2.4 Precondition Management

#### Create Precondition

Preconditions are created using standard Jira issue creation with `issuetype: "Precondition"`

```
POST /rest/api/2/issue
Body: {
  fields: {
    project: {key: "PROJECT"},
    summary: "Precondition name",
    description: "Precondition details",
    issuetype: {name: "Precondition"}
  }
}
```

#### Link Precondition to Test

Use standard Jira issue linking:

```
POST /rest/api/2/issueLink
Body: {
  type: {name: "Test"},
  inwardIssue: {key: "TEST-123"},
  outwardIssue: {key: "PRECON-1"}
}
```

### 2.5 Test Plan Management (Optional)

#### Create Test Plan

```
POST /rest/api/2/issue
Body: {
  fields: {
    project: {key: "PROJECT"},
    summary: "Test Plan name",
    description: "Description",
    issuetype: {name: "Test Plan"}
  }
}
```

#### Add Test Executions to Test Plan

- **Endpoint**: `POST /rest/raven/1.0/api/testplan/{testPlanKey}/testexecution`
- **Body**:

```json
{
  "add": ["TEXEC-123", "TEXEC-124"]
}
```

### 2.6 Import/Export (Bulk Operations)

#### Import Test Execution Results (Xray JSON)

- **Endpoint**: `POST /rest/raven/1.0/import/execution`
- **Body**: Xray JSON format

```json
{
  "testExecutionKey": "TEXEC-123",
  "tests": [
    {
      "testKey": "TEST-123",
      "status": "PASS",
      "comment": "Test passed",
      "defects": ["BUG-456"]
    }
  ]
}
```

#### Import Test Execution Results (Cucumber JSON)

- **Endpoint**: `POST /rest/raven/1.0/import/execution/cucumber`

#### Import Test Execution Results (JUnit XML)

- **Endpoint**: `POST /rest/raven/1.0/import/execution/junit`

#### Export Test Execution Results

- **Endpoint**: `GET /rest/raven/1.0/export/test?keys={testKeys}`
- Returns test details in Xray format

---

## 3. TestRail to Xray Mapping

### Entity Mapping

| TestRail Entity | Xray Entity     | API Endpoint                                                  |
| --------------- | --------------- | ------------------------------------------------------------- |
| Test Case       | Test            | `POST /rest/api/2/issue` (issuetype: "Test")                  |
| Test Suite      | Test Set        | `POST /rest/api/2/issue` (issuetype: "Test Set")              |
| Test Run        | Test Execution  | `POST /rest/api/2/issue` (issuetype: "Test Execution")        |
| Test Result     | Test Status     | `POST /rest/raven/1.0/api/testexec/{exec}/test/{test}/status` |
| Milestone       | Version/Release | `POST /rest/api/2/project/{project}/version`                  |
| Test Plan       | Test Plan       | `POST /rest/api/2/issue` (issuetype: "Test Plan")             |
| Section         | Folder/Label    | Use Jira labels or custom field                               |

### Status Mapping

| TestRail Status | Xray Status | Description                |
| --------------- | ----------- | -------------------------- |
| Passed (1)      | PASS        | Test passed                |
| Blocked (2)     | BLOCKED     | Test blocked               |
| Untested (3)    | TODO        | Not yet executed           |
| Retest (4)      | FAIL        | Needs retest               |
| Failed (5)      | FAIL        | Test failed                |
| Custom Status   | TODO/FAIL   | Map based on is_final flag |

---

## 4. Authentication

### Basic Authentication

All API calls use HTTP Basic Authentication:

```python
requests.get(url, auth=HTTPBasicAuth(username, password))
```

### Headers

```json
{
  "Content-Type": "application/json",
  "Accept": "application/json"
}
```

---

## 5. Rate Limiting

- Recommended delay: 0.5 seconds between API calls
- Batch operations where possible
- Use bulk import endpoints for large datasets

---

## 6. Error Handling

### Common HTTP Status Codes

- `200 OK` - Success
- `201 Created` - Resource created successfully
- `400 Bad Request` - Invalid request data
- `401 Unauthorized` - Authentication failed
- `403 Forbidden` - Insufficient permissions
- `404 Not Found` - Resource not found
- `500 Internal Server Error` - Server error

### Best Practices

1. Always check response status codes
2. Log API errors with full response body
3. Implement retry logic for transient failures
4. Validate data before sending to API
5. Use transactions where possible

---

## 7. Data Validation

### Before Migration

1. Verify Jira project exists
2. Confirm issue types are available (Test, Test Set, Test Execution)
3. Check user permissions
4. Validate custom fields match

### During Migration

1. Track mapping between TestRail IDs and Xray keys
2. Save mapping to JSON file for reference
3. Log all errors and warnings
4. Validate created issues

### After Migration

1. Verify test counts match
2. Check test execution results
3. Validate links between issues
4. Review custom field mappings

---

## 8. Performance Optimization

### Tips

1. Use bulk import APIs when available
2. Batch related operations
3. Implement parallel processing for independent operations
4. Cache frequently accessed data (users, priorities, statuses)
5. Use pagination for large result sets

---

## 9. Additional Resources

### Official Documentation

- **Xray Server API Documentation**: https://docs.getxray.app/display/XRAYSERVER/REST+API
- **Jira REST API Documentation**: https://docs.atlassian.com/software/jira/docs/api/REST/9.12.15/
- **Xray Import/Export**: https://docs.getxray.app/display/XRAYSERVER/Import+Execution+Results

### Issue Types Required

Ensure these issue types exist in your Jira project:

- Test
- Test Set
- Test Execution
- Precondition (optional)
- Test Plan (optional)

---

## 10. Migration Workflow

1. **Extract** - Read data from TestRail SQLite database
2. **Transform** - Convert TestRail format to Xray format
3. **Load** - Create issues in Jira/Xray using REST API
4. **Link** - Create relationships between issues
5. **Validate** - Verify migration success
6. **Report** - Generate migration summary

---

## Notes

- Always test migration on a non-production environment first
- Keep backups of all data before migration
- Document any custom field mappings
- Review and adjust issue type names based on your Jira configuration
- Consider migrating in phases (tests first, then executions, then results)
