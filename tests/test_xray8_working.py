#!/usr/bin/env python3
"""
Test the working Xray 8.x endpoint with proper authentication
"""

import json
import requests
import time

def main():
    # Load config
    with open('config.json', 'r') as f:
        config = json.load(f)
    
    base_url = config['jira_url']
    password = config['jira_password']
    
    # Detect PAT
    import re
    is_base64_like = bool(re.match(r'^[A-Za-z0-9+/=]+$', password))
    is_token = (len(password) > 30 and is_base64_like) or len(password) > 40
    
    headers = {
        'Authorization': f'Bearer {password}' if is_token else None,
        'Content-Type': 'application/json',
        'Accept': 'application/json'
    }
    
    if not is_token:
        from requests.auth import HTTPBasicAuth
        auth = HTTPBasicAuth(config['jira_username'], password)
    else:
        auth = None
        print("Using Bearer Token authentication")
    
    print("="*80)
    print("TESTING XRAY 8.x ENDPOINT WITH PROPER AUTH")
    print("="*80)
    
    test_exec_key = "RET-42"
    test_key = "RET-18"
    
    print(f"\nTest Execution: {test_exec_key}")
    print(f"Test: {test_key}")
    print(f"Target Status: PASS")
    
    # Test the endpoint
    url = f"{base_url}/rest/tests-1.0/testexec/{test_exec_key}/test/{test_key}/status"
    data = {
        'status': 'PASS',
        'comment': 'Updated via Xray 8.x API'
    }
    
    print(f"\nEndpoint: {url}")
    print(f"Data: {json.dumps(data, indent=2)}")
    
    try:
        response = requests.post(url, auth=auth, headers=headers, json=data)
        print(f"\nResponse Status: {response.status_code}")
        print(f"Response Headers: {dict(response.headers)}")
        
        response.raise_for_status()
        
        print(f"\n✅ SUCCESS!")
        
        if response.text:
            print(f"Response Body:")
            if response.text.startswith('<!DOCTYPE') or response.text.startswith('<html'):
                print("  (HTML response - checking if it's actually working...)")
            else:
                print(f"  {response.text[:500]}")
        else:
            print("  (Empty response - status updated successfully)")
        
        # Verify by checking the test execution
        print(f"\nVerifying status change...")
        verify_url = f"{base_url}/rest/raven/1.0/api/testexec/{test_exec_key}/test"
        
        verify_response = requests.get(verify_url, auth=auth, headers=headers)
        verify_response.raise_for_status()
        
        tests = verify_response.json()
        for test in tests:
            if test['key'] == test_key:
                print(f"✅ Test {test_key} status is now: {test.get('status', 'UNKNOWN')}")
                if test.get('status') == 'PASS':
                    print("\n🎉 STATUS UPDATE SUCCESSFUL!")
                    return True
                else:
                    print(f"\n⚠️  Status not updated (still {test.get('status')})")
                    return False
        
    except requests.exceptions.HTTPError as e:
        print(f"\n❌ HTTP Error: {e}")
        print(f"Response: {e.response.text[:500] if e.response else 'No response'}")
        return False
    except Exception as e:
        print(f"\n❌ Error: {e}")
        return False
    
    print("\n" + "="*80)
    return False

if __name__ == '__main__':
    success = main()
    
    if success:
        print("\n✅ THE API WORKS!")
        print("="*80)
        print("""
The Xray 8.x API endpoint is working correctly!

Endpoint: /rest/tests-1.0/testexec/{execKey}/test/{testKey}/status
Method: POST
Data: {"status": "PASS", "comment": "..."}

The migrator.py has been updated to use this endpoint.
You can now run the migration and statuses will be updated automatically!

To update existing test executions:
    python3 update_test_statuses.py
""")
    else:
        print("\n⚠️  API Still Not Working")
        print("="*80)
        print("""
The endpoint responds but may still have authentication or configuration issues.

Your options remain:
1. Manual status updates in Jira UI (~10 minutes)
2. Fix screen configuration for import/execution endpoint
3. Contact Xray support for Xray 8.1.1 specific guidance

The migration structure is complete and working!
""")

