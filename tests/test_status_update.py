#!/usr/bin/env python3
"""
Test updating test status in execution
"""

import json
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
    print("TEST STATUS UPDATE")
    print("="*80)
    
    # Use one of the executions we know has tests
    test_exec_key = "RET-42"
    test_key = "RET-18"
    
    print(f"\nTest Execution: {test_exec_key}")
    print(f"Test: {test_key}")
    print(f"\nAttempting to update status to PASS...")
    
    # Try different API endpoints
    endpoints_to_try = [
        # Try import execution results (batch mode)
        {
            'method': 'POST',
            'url': 'import/execution',
            'data': {
                'testExecutionKey': test_exec_key,
                'tests': [
                    {
                        'testKey': test_key,
                        'status': 'PASS',
                        'comment': 'Updated via migration tool'
                    }
                ]
            },
            'desc': 'Xray REST API v1 - Import Execution Results'
        },
        # v1 REST API
        {
            'method': 'POST',
            'url': f'api/testexec/{test_exec_key}/test/{test_key}/status',
            'data': {'status': 'PASS'},
            'desc': 'Xray REST API v1 - POST status'
        },
        {
            'method': 'PUT',
            'url': f'api/testexec/{test_exec_key}/test/{test_key}/status',
            'data': {'status': 'PASS'},
            'desc': 'Xray REST API v1 - PUT status'
        },
        {
            'method': 'PUT',
            'url': f'api/testrun',
            'data': {
                'testExecutionKey': test_exec_key,
                'testKey': test_key,
                'status': 'PASS'
            },
            'desc': 'Xray REST API v1 - PUT testrun'
        },
    ]
    
    for endpoint in endpoints_to_try:
        print(f"\n[Try] {endpoint['desc']}")
        print(f"  URL: /rest/raven/1.0/{endpoint['url']}")
        print(f"  Data: {endpoint['data']}")
        
        try:
            if endpoint['method'] == 'POST':
                response = client._make_xray_request('POST', endpoint['url'], data=endpoint['data'])
            elif endpoint['method'] == 'PUT':
                response = client._make_xray_request('PUT', endpoint['url'], data=endpoint['data'])
            
            print(f"  ✅ SUCCESS!")
            print(f"  Response: {response}")
            break  # Stop on first success
            
        except Exception as e:
            print(f"  ❌ Failed: {e}")
    
    print("\n" + "="*80)

if __name__ == '__main__':
    main()
