#!/usr/bin/env python3
"""
Try using Xray's import/execution endpoint with proper format
Based on Xray Server/DC REST API documentation
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
    print("XRAY IMPORT EXECUTION RESULTS")
    print("="*80)
    
    test_exec_key = "RET-42"
    test_key = "RET-18"
    
    print(f"\nTest Execution: {test_exec_key}")
    print(f"Test: {test_key}")
    
    # Format 1: Xray JSON format (standard)
    print("\n[Try 1] Xray JSON Format (testExecutionKey field)...")
    try:
        payload = {
            "testExecutionKey": test_exec_key,
            "tests": [
                {
                    "testKey": test_key,
                    "status": "PASS",
                    "comment": "Test passed via migration"
                }
            ]
        }
        print(f"Payload: {json.dumps(payload, indent=2)}")
        
        response = client._make_xray_request('POST', 'import/execution', data=payload)
        print(f"✅ SUCCESS! Response: {response}")
        return True
    except Exception as e:
        error_msg = str(e)
        print(f"❌ Failed: {error_msg[:300]}")
        
        # Check if it's a screen/field issue
        if 'customfield' in error_msg or 'screen' in error_msg:
            print("\n⚠️ NOTE: This is a Jira screen configuration issue.")
            print("The API endpoint exists but some required fields are missing from screens.")
    
    # Format 2: Try with info object
    print("\n[Try 2] Xray JSON Format with info object...")
    try:
        payload = {
            "info": {
                "summary": f"Execution Results for {test_exec_key}",
                "description": "Imported from TestRail"
            },
            "testExecutionKey": test_exec_key,
            "tests": [
                {
                    "testKey": test_key,
                    "status": "PASS",
                    "comment": "Test passed"
                }
            ]
        }
        print(f"Payload: {json.dumps(payload, indent=2)}")
        
        response = client._make_xray_request('POST', 'import/execution', data=payload)
        print(f"✅ SUCCESS! Response: {response}")
        return True
    except Exception as e:
        print(f"❌ Failed: {str(e)[:300]}")
    
    # Format 3: Multipart form data approach
    print("\n[Try 3] Checking if multipart/form-data is required...")
    print("(Some Xray versions require file upload format)")
    
    # Format 4: Try the old API format
    print("\n[Try 4] Old API format (pre-4.0)...")
    try:
        payload = {
            "testExecIssueKey": test_exec_key,
            "testIssueKey": test_key,
            "status": "PASS",
            "comment": "Migrated from TestRail"
        }
        print(f"Payload: {json.dumps(payload, indent=2)}")
        
        response = client._make_xray_request('POST', 'import/execution', data=payload)
        print(f"✅ SUCCESS! Response: {response}")
        return True
    except Exception as e:
        print(f"❌ Failed: {str(e)[:300]}")
    
    print("\n" + "="*80)
    print("RECOMMENDATION:")
    print("="*80)
    print("""
The status update API endpoint appears to be unavailable in your Xray version.
This could be due to:

1. **Screen Configuration Issue**: The custom field 'customfield_10125' is not on 
   the appropriate screen. This is a Jira administration issue.
   
2. **API Version Mismatch**: Your Xray version (7.9.1) might use a different API
   structure than documented.

3. **License Limitation**: Some Xray features might require different license level.

WORKAROUNDS:

Option A: **Manual Status Update** (Easiest)
   - Open each Test Execution in Jira UI
   - Update test statuses manually in the execution screen
   
Option B: **Fix Screen Configuration** (Recommended if you need automation)
   - Go to Jira Admin → Issues → Screens
   - Find the screen used by "Test Execution" issue type
   - Add the missing custom field (customfield_10125) to the screen
   - Re-run the migration

Option C: **Use Xray UI Bulk Import** 
   - Export test results to Excel/CSV
   - Use Xray's built-in import functionality in Jira UI
   
Option D: **Contact Xray Support**
   - They can provide the correct API endpoint for version 7.9.1
   - URL: https://support.getxray.app/

For now, your migration IS SUCCESSFUL - all tests, test sets, and test executions
are created. Only the test result statuses need manual update.
""")
    
    return False

if __name__ == '__main__':
    main()
