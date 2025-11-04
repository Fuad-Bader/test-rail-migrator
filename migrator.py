"""
TestRail to Xray (Jira) Migrator
Compatible with:
- JIRA: 9.12.15
- Xray: 7.9.1-j9 (Server/Data Center)

This script migrates test data from TestRail (stored in SQLite) to Xray in Jira.
"""

import requests
import json
import sqlite3
from requests.auth import HTTPBasicAuth
import time
from datetime import datetime

# ============================================================================
# CONFIGURATION
# ============================================================================

with open('config.json') as config_file:
    config = json.load(config_file)

# Jira/Xray Configuration
JIRA_URL = config.get('jira_url')
JIRA_USERNAME = config.get('jira_username')
JIRA_PASSWORD = config.get('jira_password')
JIRA_PROJECT_KEY = config.get('jira_project_key')

# Database
DB_PATH = 'testrail.db'

# API Rate limiting
RATE_LIMIT_DELAY = 0.5  # seconds between API calls

# Xray issue type names (customize based on your Jira configuration)
XRAY_TEST_TYPE = 'Test'
XRAY_TEST_EXECUTION_TYPE = 'Test Execution'
XRAY_TEST_SET_TYPE = 'Test Set'
XRAY_PRECONDITION_TYPE = 'Precondition'

# ============================================================================
# JIRA/XRAY API CLIENT
# ============================================================================

class JiraXrayClient:
    """Client for interacting with Jira and Xray APIs"""
    
    def __init__(self, base_url, username, password):
        self.base_url = base_url.rstrip('/')
        self.username = username
        self.password = password
        
        # Detect if using PAT (Personal Access Token) vs regular password
        # PATs are typically:
        # - Longer than normal passwords (>30 chars)
        # - Base64-encoded (alphanumeric + = padding)
        # - No special characters like !, @, #, etc.
        import re
        is_base64_like = bool(re.match(r'^[A-Za-z0-9+/=]+$', password))
        self.is_token = (len(password) > 30 and is_base64_like) or len(password) > 40
        
        if self.is_token:
            # Use Bearer token authentication for PAT
            self.auth = None
            self.headers = {
                'Authorization': f'Bearer {password}',
                'Content-Type': 'application/json',
                'Accept': 'application/json'
            }
            print("  ℹ Using Bearer Token authentication (PAT detected)")
        else:
            # Use Basic Auth for regular password
            self.auth = HTTPBasicAuth(username, password)
            self.headers = {
                'Content-Type': 'application/json',
                'Accept': 'application/json'
            }
            print("  ℹ Using HTTP Basic Auth (password detected)")
        
    def _make_request(self, method, endpoint, data=None, params=None):
        """Make HTTP request to Jira API"""
        url = f"{self.base_url}/rest/api/2/{endpoint}"
        
        try:
            # Use auth only if not using Bearer token (it's in headers)
            auth_param = None if self.is_token else self.auth
            
            if method == 'GET':
                response = requests.get(url, auth=auth_param, headers=self.headers, params=params)
            elif method == 'POST':
                response = requests.post(url, auth=auth_param, headers=self.headers, json=data)
            elif method == 'PUT':
                response = requests.put(url, auth=auth_param, headers=self.headers, json=data)
            elif method == 'DELETE':
                response = requests.delete(url, auth=auth_param, headers=self.headers)
            
            response.raise_for_status()
            time.sleep(RATE_LIMIT_DELAY)  # Rate limiting
            
            if response.text:
                return response.json()
            return {}
            
        except requests.exceptions.RequestException as e:
            print(f"  ❌ API Error: {e}")
            if hasattr(e, 'response') and hasattr(e.response, 'text'):
                print(f"  Response: {e.response.text[:500]}")
            raise
    
    def _make_xray_request(self, method, endpoint, data=None):
        """Make HTTP request to Xray API"""
        url = f"{self.base_url}/rest/raven/1.0/{endpoint}"
        
        try:
            # Use auth only if not using Bearer token (it's in headers)
            auth_param = None if self.is_token else self.auth
            
            if method == 'GET':
                response = requests.get(url, auth=auth_param, headers=self.headers)
            elif method == 'POST':
                response = requests.post(url, auth=auth_param, headers=self.headers, json=data)
            elif method == 'PUT':
                response = requests.put(url, auth=auth_param, headers=self.headers, json=data)
            
            response.raise_for_status()
            time.sleep(RATE_LIMIT_DELAY)
            
            if response.text:
                return response.json()
            return {}
            
        except requests.exceptions.RequestException as e:
            print(f"  ❌ Xray API Error: {e}")
            if hasattr(e, 'response') and hasattr(e.response, 'text'):
                print(f"  Response: {e.response.text[:500]}")
            raise
    
    # ========================================================================
    # JIRA CORE API METHODS
    # ========================================================================
    
    def get_project(self, project_key):
        """Get project details"""
        return self._make_request('GET', f'project/{project_key}')
    
    def create_issue(self, issue_data):
        """Create a new issue in Jira"""
        return self._make_request('POST', 'issue', data=issue_data)
    
    def update_issue(self, issue_key, update_data):
        """Update an existing issue"""
        return self._make_request('PUT', f'issue/{issue_key}', data=update_data)
    
    def get_issue(self, issue_key):
        """Get issue details"""
        return self._make_request('GET', f'issue/{issue_key}')
    
    def search_issues(self, jql, fields=None, max_results=100):
        """Search for issues using JQL"""
        params = {
            'jql': jql,
            'maxResults': max_results
        }
        if fields:
            params['fields'] = ','.join(fields)
        return self._make_request('GET', 'search', params=params)
    
    def add_comment(self, issue_key, comment):
        """Add comment to an issue"""
        data = {'body': comment}
        return self._make_request('POST', f'issue/{issue_key}/comment', data=data)
    
    def create_link(self, inward_issue, outward_issue, link_type='Relates'):
        """Create link between two issues"""
        data = {
            'type': {'name': link_type},
            'inwardIssue': {'key': inward_issue},
            'outwardIssue': {'key': outward_issue}
        }
        return self._make_request('POST', 'issueLink', data=data)
    
    # ========================================================================
    # XRAY SPECIFIC API METHODS (REST API v1.0)
    # ========================================================================
    
    def create_test(self, project_key, summary, description=None, steps=None, precondition=None):
        """Create a Test issue in Xray"""
        issue_data = {
            'fields': {
                'project': {'key': project_key},
                'summary': summary,
                'description': description or '',
                'issuetype': {'name': XRAY_TEST_TYPE}
            }
        }
        
        test = self.create_issue(issue_data)
        test_key = test['key']
        
        # Add test steps using Xray API
        if steps:
            self.update_test_steps(test_key, steps)
        
        # Link precondition if provided
        if precondition:
            self.create_link(test_key, precondition, 'Test')
        
        return test
    
    def update_test_steps(self, test_key, steps):
        """Update test steps for a Test issue"""
        # Xray REST API endpoint for test steps
        steps_data = []
        for idx, step in enumerate(steps, 1):
            step_obj = {
                'index': idx,
                'step': step.get('action', ''),
                'data': step.get('data', ''),
                'result': step.get('expected', '')
            }
            steps_data.append(step_obj)
        
        try:
            return self._make_xray_request('PUT', f'api/testrun/{test_key}/step', data=steps_data)
        except Exception as e:
            print(f"  Warning: Could not update test steps for {test_key}: {e}")
    
    def create_test_set(self, project_key, summary, description=None, tests=None):
        """Create a Test Set issue in Xray"""
        issue_data = {
            'fields': {
                'project': {'key': project_key},
                'summary': summary,
                'description': description or '',
                'issuetype': {'name': XRAY_TEST_SET_TYPE}
            }
        }
        
        test_set = self.create_issue(issue_data)
        test_set_key = test_set['key']
        
        # Add tests to test set
        if tests:
            self.add_tests_to_test_set(test_set_key, tests)
        
        return test_set
    
    def add_tests_to_test_set(self, test_set_key, test_keys):
        """Add tests to a test set"""
        try:
            data = {'add': test_keys}
            return self._make_xray_request('POST', f'api/testset/{test_set_key}/test', data=data)
        except Exception as e:
            print(f"  Warning: Could not add tests to test set {test_set_key}: {e}")
    
    def create_test_execution(self, project_key, summary, description=None, tests=None):
        """Create a Test Execution issue in Xray"""
        issue_data = {
            'fields': {
                'project': {'key': project_key},
                'summary': summary,
                'description': description or '',
                'issuetype': {'name': XRAY_TEST_EXECUTION_TYPE}
            }
        }
        
        test_exec = self.create_issue(issue_data)
        test_exec_key = test_exec['key']
        
        # Add tests to execution
        if tests:
            self.add_tests_to_execution(test_exec_key, tests)
        
        return test_exec
    
    def add_tests_to_execution(self, test_execution_key, test_keys):
        """Add tests to a test execution"""
        try:
            data = {'add': test_keys}
            return self._make_xray_request('POST', f'api/testexec/{test_execution_key}/test', data=data)
        except Exception as e:
            print(f"  Warning: Could not add tests to execution {test_execution_key}: {e}")
    
    def update_test_execution_status(self, test_execution_key, test_key, status, comment=None, 
                                     defects=None, evidence=None):
        """Update the status of a test within a test execution"""
        data = {
            'status': status  # e.g., 'PASS', 'FAIL', 'EXECUTING', 'TODO', 'ABORTED'
        }
        
        if comment:
            data['comment'] = comment
        
        if defects:
            data['defects'] = defects  # List of defect keys
        
        try:
            # Try Xray 8.x API first (different base path)
            url = f"{self.base_url}/rest/tests-1.0/testexec/{test_execution_key}/test/{test_key}/status"
            auth_param = None if self.is_token else self.auth
            
            response = requests.post(url, auth=auth_param, headers=self.headers, json=data)
            response.raise_for_status()
            time.sleep(RATE_LIMIT_DELAY)
            
            if response.text and not response.text.startswith('<!DOCTYPE'):
                return response.json() if response.text else {}
            return {}
        except Exception as e:
            # Fallback to old API
            try:
                return self._make_xray_request('POST', 
                    f'api/testexec/{test_execution_key}/test/{test_key}/status', 
                    data=data)
            except Exception as e2:
                print(f"  Warning: Could not update test status: {e2}")
    
    def create_precondition(self, project_key, summary, description=None):
        """Create a Precondition issue"""
        issue_data = {
            'fields': {
                'project': {'key': project_key},
                'summary': summary,
                'description': description or '',
                'issuetype': {'name': XRAY_PRECONDITION_TYPE}
            }
        }
        return self.create_issue(issue_data)

# ============================================================================
# DATA MIGRATION FUNCTIONS
# ============================================================================

def get_db_connection():
    """Get database connection"""
    return sqlite3.connect(DB_PATH)

def map_testrail_status_to_xray(status_id, statuses):
    """Map TestRail status to Xray status"""
    status_map = {
        1: 'PASS',      # Passed
        2: 'BLOCKED',   # Blocked
        3: 'TODO',      # Untested
        4: 'FAIL',      # Retest
        5: 'FAIL',      # Failed
    }
    
    # Try to find status in database
    for status in statuses:
        if status['id'] == status_id:
            if status['is_final'] and not status['is_untested']:
                return 'PASS'
            elif status['is_untested']:
                return 'TODO'
            else:
                return 'FAIL'
    
    return status_map.get(status_id, 'TODO')

def migrate_test_cases(client, project_key, mapping):
    """Migrate test cases to Xray Tests"""
    print("\n[1/5] Migrating Test Cases...")
    
    db = get_db_connection()
    cursor = db.cursor()
    
    # Get all test cases
    cursor.execute('''
        SELECT c.*, s.name as section_name, p.name as priority_name
        FROM cases c
        LEFT JOIN sections s ON c.section_id = s.id
        LEFT JOIN priorities p ON c.priority_id = p.id
    ''')
    
    cases = cursor.fetchall()
    columns = [desc[0] for desc in cursor.description]
    
    test_count = 0
    for row in cases:
        case = dict(zip(columns, row))
        
        try:
            # Parse custom fields
            custom_fields = {}
            if case.get('custom_fields'):
                try:
                    custom_fields = eval(case['custom_fields'])
                except:
                    pass
            
            # Build description
            description = f"*Imported from TestRail (ID: {case['id']})*\n\n"
            
            if case.get('section_name'):
                description += f"*Section:* {case['section_name']}\n"
            
            # Add preconditions if exists
            if custom_fields.get('custom_preconds'):
                description += f"\n*Preconditions:*\n{custom_fields['custom_preconds']}\n"
            
            # Add steps and expected results
            if custom_fields.get('custom_steps_separated'):
                description += f"\n*Steps:*\n"
                try:
                    steps = eval(custom_fields['custom_steps_separated'])
                    for step in steps:
                        description += f"- {step}\n"
                except:
                    pass
            
            # Add any additional custom fields
            description += f"\n*Additional Information:*\n"
            if case.get('refs'):
                description += f"- References: {case['refs']}\n"
            if case.get('estimate'):
                description += f"- Estimate: {case['estimate']}\n"
            
            # Create test in Xray
            test = client.create_test(
                project_key=project_key,
                summary=case['title'],
                description=description
            )
            
            # Store mapping
            mapping['cases'][case['id']] = test['key']
            test_count += 1
            
            if test_count % 10 == 0:
                print(f"  ✓ Migrated {test_count} test cases...")
            
        except Exception as e:
            print(f"  ❌ Error migrating case {case['id']}: {e}")
    
    db.close()
    print(f"✓ Migrated {test_count} test cases")
    return mapping

def migrate_test_suites(client, project_key, mapping):
    """Migrate test suites to Xray Test Sets"""
    print("\n[2/5] Migrating Test Suites as Test Sets...")
    
    db = get_db_connection()
    cursor = db.cursor()
    
    # Get all suites
    cursor.execute('SELECT * FROM suites')
    suites = cursor.fetchall()
    columns = [desc[0] for desc in cursor.description]
    
    suite_count = 0
    for row in suites:
        suite = dict(zip(columns, row))
        
        try:
            # Get tests in this suite
            cursor.execute('SELECT id FROM cases WHERE suite_id = ?', (suite['id'],))
            case_ids = [r[0] for r in cursor.fetchall()]
            
            # Get corresponding Xray test keys
            test_keys = [mapping['cases'][cid] for cid in case_ids if cid in mapping['cases']]
            
            description = f"*Imported from TestRail Suite (ID: {suite['id']})*\n\n"
            if suite.get('description'):
                description += suite['description']
            
            # Create Test Set
            test_set = client.create_test_set(
                project_key=project_key,
                summary=suite['name'],
                description=description,
                tests=test_keys
            )
            
            mapping['suites'][suite['id']] = test_set['key']
            suite_count += 1
            
        except Exception as e:
            print(f"  ❌ Error migrating suite {suite['id']}: {e}")
    
    db.close()
    print(f"✓ Migrated {suite_count} test suites as test sets")
    return mapping

def migrate_test_runs(client, project_key, mapping):
    """Migrate test runs to Xray Test Executions"""
    print("\n[3/5] Migrating Test Runs as Test Executions...")
    
    db = get_db_connection()
    cursor = db.cursor()
    
    # Get all runs
    cursor.execute('SELECT * FROM runs ORDER BY created_on')
    runs = cursor.fetchall()
    columns = [desc[0] for desc in cursor.description]
    
    run_count = 0
    for row in runs:
        run = dict(zip(columns, row))
        
        try:
            # Get tests in this run
            cursor.execute('SELECT case_id FROM tests WHERE run_id = ?', (run['id'],))
            case_ids = [r[0] for r in cursor.fetchall()]
            
            # Get corresponding Xray test keys
            test_keys = [mapping['cases'][cid] for cid in case_ids if cid in mapping['cases']]
            
            # Build description
            description = f"*Imported from TestRail Run (ID: {run['id']})*\n\n"
            if run.get('description'):
                description += f"{run['description']}\n\n"
            
            description += f"*Statistics:*\n"
            description += f"- Passed: {run.get('passed_count', 0)}\n"
            description += f"- Failed: {run.get('failed_count', 0)}\n"
            description += f"- Blocked: {run.get('blocked_count', 0)}\n"
            description += f"- Untested: {run.get('untested_count', 0)}\n"
            description += f"- Retest: {run.get('retest_count', 0)}\n"
            
            if run.get('created_on'):
                created_date = datetime.fromtimestamp(run['created_on']).strftime('%Y-%m-%d %H:%M:%S')
                description += f"\n*Created:* {created_date}\n"
            
            # Create Test Execution
            test_exec = client.create_test_execution(
                project_key=project_key,
                summary=run['name'],
                description=description,
                tests=test_keys
            )
            
            mapping['runs'][run['id']] = test_exec['key']
            run_count += 1
            
            if run_count % 5 == 0:
                print(f"  ✓ Migrated {run_count} test runs...")
            
        except Exception as e:
            print(f"  ❌ Error migrating run {run['id']}: {e}")
    
    db.close()
    print(f"✓ Migrated {run_count} test runs as test executions")
    return mapping

def migrate_test_results(client, project_key, mapping):
    """Migrate test results to Xray Test Execution results"""
    print("\n[4/5] Migrating Test Results...")
    
    db = get_db_connection()
    cursor = db.cursor()
    
    # Get statuses for mapping
    cursor.execute('SELECT * FROM statuses')
    statuses = [dict(zip([desc[0] for desc in cursor.description], row)) 
                for row in cursor.fetchall()]
    
    # Get all tests with their results
    cursor.execute('''
        SELECT t.*, r.status_id, r.comment, r.defects, r.created_on as result_date
        FROM tests t
        LEFT JOIN results r ON t.id = r.test_id
        WHERE r.id IS NOT NULL
        ORDER BY t.run_id, r.created_on
    ''')
    
    test_results = cursor.fetchall()
    columns = [desc[0] for desc in cursor.description]
    
    # Group results by test execution for batch processing
    results_by_execution = {}
    for row in test_results:
        test = dict(zip(columns, row))
        run_key = mapping['runs'].get(test['run_id'])
        test_key = mapping['cases'].get(test['case_id'])
        
        if not run_key or not test_key:
            continue
            
        if run_key not in results_by_execution:
            results_by_execution[run_key] = []
        
        results_by_execution[run_key].append({
            'test_key': test_key,
            'status': map_testrail_status_to_xray(test['status_id'], statuses),
            'comment': test.get('comment'),
            'defects': test.get('defects', '').split(',') if test.get('defects') else None
        })
    
    result_count = 0
    skipped_count = 0
    
    # Process each test execution
    for run_key, results in results_by_execution.items():
        for result in results:
            try:
                # Update test execution status
                client.update_test_execution_status(
                    test_execution_key=run_key,
                    test_key=result['test_key'],
                    status=result['status'],
                    comment=result['comment'],
                    defects=result['defects']
                )
                
                result_count += 1
                
                if result_count % 20 == 0:
                    print(f"  ✓ Migrated {result_count} test results...")
                    
            except Exception as e:
                # Test might not be in execution - skip silently
                skipped_count += 1
    
    db.close()
    
    if skipped_count > 0:
        print(f"✓ Migrated {result_count} test results ({skipped_count} skipped)")
    else:
        print(f"✓ Migrated {result_count} test results")
    
    return mapping

def migrate_milestones(client, project_key, mapping):
    """Migrate milestones as Jira versions/releases"""
    print("\n[5/5] Migrating Milestones as Versions...")
    
    db = get_db_connection()
    cursor = db.cursor()
    
    # Get all milestones
    cursor.execute('SELECT * FROM milestones ORDER BY due_on')
    milestones = cursor.fetchall()
    columns = [desc[0] for desc in cursor.description]
    
    milestone_count = 0
    for row in milestones:
        milestone = dict(zip(columns, row))
        
        try:
            # Create version in Jira
            version_data = {
                'name': milestone['name'],
                'description': milestone.get('description', ''),
                'project': project_key,
                'released': milestone.get('is_completed', 0) == 1
            }
            
            if milestone.get('start_on'):
                start_date = datetime.fromtimestamp(milestone['start_on']).strftime('%Y-%m-%d')
                version_data['startDate'] = start_date
            
            if milestone.get('due_on'):
                due_date = datetime.fromtimestamp(milestone['due_on']).strftime('%Y-%m-%d')
                version_data['releaseDate'] = due_date
            
            version = client._make_request('POST', 'version', data=version_data)
            
            mapping['milestones'][milestone['id']] = version['id']
            milestone_count += 1
            
        except Exception as e:
            print(f"  ❌ Error migrating milestone {milestone['id']}: {e}")
    
    db.close()
    print(f"✓ Migrated {milestone_count} milestones as versions")
    return mapping

def save_mapping(mapping, filename='migration_mapping.json'):
    """Save migration mapping to file"""
    with open(filename, 'w') as f:
        json.dump(mapping, f, indent=2)
    print(f"\n✓ Mapping saved to {filename}")

# ============================================================================
# MAIN MIGRATION PROCESS
# ============================================================================

def main():
    print("=" * 80)
    print("TESTRAIL TO XRAY MIGRATION")
    print("=" * 80)
    print(f"\nTarget: {JIRA_URL}")
    print(f"Project: {JIRA_PROJECT_KEY}")
    print(f"Database: {DB_PATH}")
    print("\n" + "=" * 80)
    
    # Initialize client
    print("\nConnecting to Jira/Xray...")
    client = JiraXrayClient(JIRA_URL, JIRA_USERNAME, JIRA_PASSWORD)
    
    # Verify project exists
    try:
        project = client.get_project(JIRA_PROJECT_KEY)
        print(f"✓ Connected to project: {project['name']}")
    except Exception as e:
        print(f"❌ Error: Could not access project {JIRA_PROJECT_KEY}")
        print(f"   {e}")
        return
    
    # Initialize mapping dictionary
    mapping = {
        'cases': {},      # TestRail case_id -> Xray test key
        'suites': {},     # TestRail suite_id -> Xray test set key
        'runs': {},       # TestRail run_id -> Xray test execution key
        'milestones': {}, # TestRail milestone_id -> Jira version id
        'plans': {}       # TestRail plan_id -> Xray test plan key (if needed)
    }
    
    # Perform migration
    try:
        mapping = migrate_test_cases(client, JIRA_PROJECT_KEY, mapping)
        mapping = migrate_test_suites(client, JIRA_PROJECT_KEY, mapping)
        mapping = migrate_test_runs(client, JIRA_PROJECT_KEY, mapping)
        mapping = migrate_test_results(client, JIRA_PROJECT_KEY, mapping)
        mapping = migrate_milestones(client, JIRA_PROJECT_KEY, mapping)
        
        # Save mapping
        save_mapping(mapping)
        
        print("\n" + "=" * 80)
        print("MIGRATION COMPLETE!")
        print("=" * 80)
        print(f"\nSummary:")
        print(f"  - Test Cases migrated: {len(mapping['cases'])}")
        print(f"  - Test Sets created: {len(mapping['suites'])}")
        print(f"  - Test Executions created: {len(mapping['runs'])}")
        print(f"  - Milestones migrated: {len(mapping['milestones'])}")
        
    except Exception as e:
        print(f"\n❌ Migration failed: {e}")
        import traceback
        traceback.print_exc()

if __name__ == '__main__':
    main()
