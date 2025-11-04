#!/usr/bin/env python3
"""
Check Xray API capabilities and try to find working status update endpoint
"""

import json
import requests
from migrator import JiraXrayClient

def main():
    # Load config
    with open('config.json', 'r') as f:
        config = json.load(f)
    
    client = JiraXrayClient(
        base_url=config['jira_url'],
        username=config['jira_username'],
        password=config['jira_password']
    )
    
    print("="*80)
    print("XRAY API ENDPOINT INVESTIGATION")
    print("="*80)
    
    # Test execution and test to work with
    test_exec_key = "RET-42"
    test_key = "RET-18"
    
    print(f"\nTarget Test Execution: {test_exec_key}")
    print(f"Target Test: {test_key}")
    
    # Try to get more info about the test execution
    print("\n[1] Getting Test Execution Details...")
    try:
        exec_issue = client.get_issue(test_exec_key)
        print(f"  ✓ Issue Type: {exec_issue['fields']['issuetype']['name']}")
        print(f"  ✓ Summary: {exec_issue['fields']['summary']}")
        print(f"  ✓ Status: {exec_issue['fields']['status']['name']}")
    except Exception as e:
        print(f"  ❌ Error: {e}")
    
    # Get tests in execution
    print("\n[2] Getting Tests in Execution...")
    try:
        tests = client._make_xray_request('GET', f'api/testexec/{test_exec_key}/test')
        print(f"  ✓ Found {len(tests)} tests")
        for i, test in enumerate(tests[:3], 1):
            print(f"    {i}. {test['key']} - Status: {test.get('status', 'N/A')}")
            if 'id' in test:
                print(f"       ID: {test['id']}")
    except Exception as e:
        print(f"  ❌ Error: {e}")
    
    # Try different status update approaches
    print("\n[3] Trying Different Status Update Methods...")
    
    test_methods = [
        {
            'name': 'Method 1: Using test ID instead of key',
            'func': lambda: try_update_by_id(client, test_exec_key, test_key)
        },
        {
            'name': 'Method 2: Using Xray graphql endpoint',
            'func': lambda: try_graphql_update(client, test_exec_key, test_key)
        },
        {
            'name': 'Method 3: Direct Jira issue update',
            'func': lambda: try_direct_issue_update(client, test_exec_key, test_key)
        },
        {
            'name': 'Method 4: Check Xray internal API',
            'func': lambda: try_internal_api(client, test_exec_key, test_key)
        }
    ]
    
    for method in test_methods:
        print(f"\n  {method['name']}:")
        try:
            result = method['func']()
            if result:
                print(f"    ✅ SUCCESS!")
                print(f"    Response: {result}")
                break
        except Exception as e:
            print(f"    ❌ Failed: {str(e)[:200]}")
    
    print("\n" + "="*80)

def try_update_by_id(client, test_exec_key, test_key):
    """Try using test ID instead of key"""
    # First get the test run ID
    tests = client._make_xray_request('GET', f'api/testexec/{test_exec_key}/test')
    for test in tests:
        if test['key'] == test_key:
            test_id = test.get('id')
            if test_id:
                return client._make_xray_request(
                    'POST',
                    f'api/testexec/{test_exec_key}/test/{test_id}/status',
                    data={'status': 'PASS'}
                )
    return None

def try_graphql_update(client, test_exec_key, test_key):
    """Try using GraphQL if available"""
    # Xray might have a GraphQL endpoint
    return None  # Not implemented yet

def try_direct_issue_update(client, test_exec_key, test_key):
    """Try updating via Jira issue fields"""
    # Some Xray installations store status in custom fields
    return None  # Not implemented yet

def try_internal_api(client, test_exec_key, test_key):
    """Check if there's an internal API"""
    # Try different API paths
    paths = [
        f'api/internal/testrun/{test_exec_key}/{test_key}/status',
        f'api/testrun/status',
        f'api/test/{test_key}/execution/{test_exec_key}/status'
    ]
    
    for path in paths:
        try:
            result = client._make_xray_request(
                'POST',
                path,
                data={'status': 'PASS'}
            )
            return result
        except:
            pass
    return None

if __name__ == '__main__':
    main()
