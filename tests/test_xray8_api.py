#!/usr/bin/env python3
"""
Test Xray 8.x API endpoints for status updates
Xray 8.1.1 may have different/improved API endpoints
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
    print("XRAY 8.x API ENDPOINT TESTING")
    print("="*80)
    print(f"\nXray Version: 8.1.1-j9")
    
    test_exec_key = "RET-42"
    test_key = "RET-18"
    
    print(f"Test Execution: {test_exec_key}")
    print(f"Test: {test_key}")
    
    # List of endpoints to try for Xray 8.x
    endpoints_to_try = [
        # Xray 8.x may have updated paths
        {
            'name': 'Xray 8.x - testrun endpoint',
            'method': 'PUT',
            'path': 'api/testrun',
            'data': {
                'testExecutionKey': test_exec_key,
                'testKey': test_key,
                'status': 'PASS',
                'comment': 'Updated via API'
            }
        },
        {
            'name': 'Xray 8.x - testrun with testIssueKey',
            'method': 'PUT',
            'path': 'api/testrun',
            'data': {
                'testExecIssueKey': test_exec_key,
                'testIssueKey': test_key,
                'status': 'PASS',
                'comment': 'Updated via API'
            }
        },
        {
            'name': 'Xray 8.x - Direct status update v2',
            'method': 'PUT',
            'path': f'api/testexec/{test_exec_key}/test/{test_key}',
            'data': {
                'status': 'PASS',
                'comment': 'Updated via API'
            }
        },
        {
            'name': 'Xray 8.x - Results endpoint',
            'method': 'POST',
            'path': 'api/testexec/results',
            'data': {
                'testExecutionKey': test_exec_key,
                'tests': [
                    {
                        'testKey': test_key,
                        'status': 'PASS',
                        'comment': 'Updated via API'
                    }
                ]
            }
        },
        {
            'name': 'Xray 8.x - Import execution with minimal fields',
            'method': 'POST',
            'path': 'import/execution',
            'data': {
                'testExecutionKey': test_exec_key,
                'tests': [
                    {
                        'testKey': test_key,
                        'status': 'PASS'
                    }
                ]
            }
        },
        {
            'name': 'Xray 8.x - Import execution with info.project only',
            'method': 'POST',
            'path': 'import/execution',
            'data': {
                'info': {
                    'project': 'RET'
                },
                'testExecutionKey': test_exec_key,
                'tests': [
                    {
                        'testKey': test_key,
                        'status': 'PASS'
                    }
                ]
            }
        },
        {
            'name': 'Xray 8.x - Multipart endpoint check',
            'method': 'POST',
            'path': 'import/execution/multipart',
            'data': {
                'testExecutionKey': test_exec_key,
                'tests': [
                    {
                        'testKey': test_key,
                        'status': 'PASS'
                    }
                ]
            }
        },
        {
            'name': 'Xray 8.x - Batch update endpoint',
            'method': 'POST',
            'path': 'api/testexecution/update',
            'data': {
                'testExecutionKey': test_exec_key,
                'tests': [
                    {
                        'testKey': test_key,
                        'status': 'PASS'
                    }
                ]
            }
        },
        {
            'name': 'Xray 8.x - Legacy compatibility endpoint',
            'method': 'POST',
            'path': f'api/test/{test_key}/execution/{test_exec_key}',
            'data': {
                'status': 'PASS',
                'comment': 'Updated via API'
            }
        },
        # Try with different base path (some Xray versions use /rest/tests-1.0/)
        {
            'name': 'Xray 8.x - Alternative base path',
            'method': 'POST',
            'path': f'testexec/{test_exec_key}/test/{test_key}/status',
            'data': {
                'status': 'PASS'
            },
            'base': '/rest/tests-1.0/'
        },
    ]
    
    success = False
    
    for i, endpoint in enumerate(endpoints_to_try, 1):
        print(f"\n[{i}/{len(endpoints_to_try)}] {endpoint['name']}")
        print(f"  Method: {endpoint['method']}")
        
        # Use custom base if specified
        if 'base' in endpoint:
            url = f"{client.base_url}{endpoint['base']}{endpoint['path']}"
            print(f"  URL: {url}")
            
            try:
                import requests
                auth_param = None if client.is_token else client.auth
                
                if endpoint['method'] == 'POST':
                    response = requests.post(url, auth=auth_param, headers=client.headers, json=endpoint['data'])
                elif endpoint['method'] == 'PUT':
                    response = requests.put(url, auth=auth_param, headers=client.headers, json=endpoint['data'])
                
                response.raise_for_status()
                print(f"  ✅ SUCCESS!")
                print(f"  Response: {response.text[:200] if response.text else 'OK'}")
                success = True
                break
            except Exception as e:
                print(f"  ❌ Failed: {str(e)[:150]}")
        else:
            print(f"  Path: /rest/raven/1.0/{endpoint['path']}")
            print(f"  Data: {json.dumps(endpoint['data'], indent=4)[:200]}")
            
            try:
                if endpoint['method'] == 'POST':
                    response = client._make_xray_request('POST', endpoint['path'], data=endpoint['data'])
                elif endpoint['method'] == 'PUT':
                    response = client._make_xray_request('PUT', endpoint['path'], data=endpoint['data'])
                
                print(f"  ✅ SUCCESS!")
                print(f"  Response: {response}")
                success = True
                break
            except Exception as e:
                error_msg = str(e)
                # Show more details for interesting errors
                if '400' in error_msg:
                    print(f"  ❌ 400 Bad Request: {error_msg[:200]}")
                elif '404' in error_msg:
                    print(f"  ❌ 404 Not Found")
                elif '405' in error_msg:
                    print(f"  ❌ 405 Method Not Allowed")
                else:
                    print(f"  ❌ Failed: {error_msg[:150]}")
    
    print("\n" + "="*80)
    
    if success:
        print("✅ WORKING ENDPOINT FOUND!")
        print("="*80)
        print("\nThe migration tool can be updated to use this endpoint.")
        print("I'll update the migrator.py code to use the working endpoint.")
    else:
        print("⚠️  NO WORKING ENDPOINT FOUND")
        print("="*80)
        print("""
Xray 8.1.1 API endpoints tested but none worked for status updates.

This is likely still due to the screen configuration issue with customfield_10125.

RECOMMENDED ACTIONS:
1. Check Xray 8.1.1 release notes for API changes
2. Review Xray documentation: https://docs.getxray.app/display/XRAY811/
3. Fix the screen configuration (add customfield_10125)
4. Or update statuses manually in Jira UI

Your migration is still complete and functional - only status updates need
the manual workaround or screen configuration fix.
""")
    
    return success

if __name__ == '__main__':
    main()
