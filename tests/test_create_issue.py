#!/usr/bin/env python3
"""
Test creating a Test issue in Jira/Xray
"""

import json
from migrator import JiraXrayClient

def main():
    # Load config
    with open('config.json', 'r') as f:
        config = json.load(f)
    
    print("="*80)
    print("TEST ISSUE CREATION")
    print("="*80)
    
    client = JiraXrayClient(
        base_url=config['jira_url'],
        username=config['jira_username'],
        password=config['jira_password']
    )
    
    project_key = config['jira_project_key']
    
    print(f"\nProject: {project_key}")
    print("\nAttempting to create a Test issue...")
    
    try:
        # Try to create a simple Test issue
        issue_data = {
            'fields': {
                'project': {'key': project_key},
                'summary': 'TEST - Sample Test Case from Migration Tool',
                'description': 'This is a test issue created to verify the migration tool works correctly.',
                'issuetype': {'name': 'Test'}
            }
        }
        
        print(f"\nPayload:")
        print(json.dumps(issue_data, indent=2))
        
        result = client.create_issue(issue_data)
        
        print(f"\n✅ SUCCESS! Test issue created:")
        print(f"   - Key: {result['key']}")
        print(f"   - ID: {result['id']}")
        print(f"   - URL: {config['jira_url']}/browse/{result['key']}")
        
        # Try to delete it (cleanup)
        print(f"\nCleaning up test issue...")
        client._make_request('DELETE', f"issue/{result['key']}")
        print(f"✅ Test issue deleted successfully")
        
    except Exception as e:
        print(f"\n❌ FAILED to create Test issue:")
        print(f"   Error: {e}")
        if hasattr(e, 'response') and hasattr(e.response, 'text'):
            print(f"   Response: {e.response.text}")
        return False
    
    print("\n" + "="*80)
    print("✅ ALL CHECKS PASSED - Migration should work now!")
    print("="*80)
    return True

if __name__ == '__main__':
    success = main()
    exit(0 if success else 1)
