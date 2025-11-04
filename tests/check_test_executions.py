#!/usr/bin/env python3
"""
Check what tests are in a Test Execution
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
    
    project_key = config['jira_project_key']
    
    print("="*80)
    print("CHECKING TEST EXECUTIONS")
    print("="*80)
    
    # Search for Test Execution issues
    try:
        result = client.search_issues(
            jql=f"project={project_key} AND issuetype='Test Execution'",
            fields=['summary', 'status', 'created'],
            max_results=5
        )
        
        print(f"\nFound {result['total']} Test Execution issues")
        
        for issue in result.get('issues', [])[:3]:  # Check first 3
            print(f"\n{'='*80}")
            print(f"Test Execution: {issue['key']}")
            print(f"Summary: {issue['fields']['summary']}")
            
            # Try to get tests in this execution using Xray API
            try:
                tests_response = client._make_xray_request(
                    'GET',
                    f'api/testexec/{issue["key"]}/test'
                )
                
                if tests_response:
                    print(f"✓ Tests in execution: {len(tests_response)}")
                    for i, test in enumerate(tests_response[:5], 1):
                        print(f"  {i}. {test.get('key', 'N/A')} - {test.get('status', 'N/A')}")
                else:
                    print(f"⚠ No tests found in this execution")
                    
            except Exception as e:
                print(f"❌ Could not get tests: {e}")
    
    except Exception as e:
        print(f"❌ Error: {e}")
    
    print("\n" + "="*80)

if __name__ == '__main__':
    main()
