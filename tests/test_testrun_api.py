#!/usr/bin/env python3
"""Test script to explore TestRun API endpoints for updating test results"""
import json
import requests
from requests.auth import HTTPBasicAuth

# Load config
with open('config.json', 'r') as f:
    config = json.load(f)

base_url = config['jira_url']
username = config['jira_username']
password = config['jira_password']

# Detect if using PAT
import re
is_base64_like = bool(re.match(r'^[A-Za-z0-9+/=]+$', password))
is_token = (len(password) > 30 and is_base64_like) or len(password) > 40

if is_token:
    headers = {
        'Authorization': f'Bearer {password}',
        'Content-Type': 'application/json',
        'Accept': 'application/json'
    }
    auth = None
    print("Using Bearer Token authentication")
else:
    headers = {
        'Content-Type': 'application/json',
        'Accept': 'application/json'
    }
    auth = HTTPBasicAuth(username, password)
    print("Using Basic Auth")

# Test parameters - we'll use existing issues from the migration
test_exec_key = "MT-44"  # A Test Execution from the migration
test_key = "MT-26"  # A Test from the migration

print(f"\n{'='*80}")
print(f"TESTING TESTRUN API ENDPOINTS")
print(f"{'='*80}")
print(f"Test Execution: {test_exec_key}")
print(f"Test: {test_key}")
print(f"{'='*80}\n")

# Test 1: Get test runs (iterations) for a test execution
print("1. GET /testruns - Getting all test runs")
print("-" * 80)
try:
    url = f"{base_url}/rest/raven/2.0/api/testruns"
    print(f"URL: {url}")
    response = requests.get(url, auth=auth, headers=headers)
    print(f"Status: {response.status_code}")
    if response.ok:
        data = response.json()
        print(f"Response: {json.dumps(data, indent=2)[:500]}")
    else:
        print(f"Error: {response.text[:500]}")
except Exception as e:
    print(f"Exception: {e}")

print("\n" + "="*80 + "\n")

# Test 2: Get test runs for specific test execution
print(f"2. GET Test Runs for Test Execution {test_exec_key}")
print("-" * 80)
try:
    # Try to get the test execution issue first to see its structure
    url = f"{base_url}/rest/api/2/issue/{test_exec_key}"
    print(f"URL: {url}")
    response = requests.get(url, auth=auth, headers=headers)
    print(f"Status: {response.status_code}")
    if response.ok:
        issue_data = response.json()
        print(f"Issue Type: {issue_data['fields']['issuetype']['name']}")
        print(f"Summary: {issue_data['fields']['summary']}")
        
        # Check if there's a custom field for test runs
        print("\nCustom fields containing 'test' or 'run':")
        for key, value in issue_data['fields'].items():
            if 'test' in key.lower() or 'run' in key.lower():
                print(f"  {key}: {str(value)[:100]}")
    else:
        print(f"Error: {response.text[:500]}")
except Exception as e:
    print(f"Exception: {e}")

print("\n" + "="*80 + "\n")

# Test 3: Try the Xray v1 API to get test runs
print(f"3. GET /rest/raven/1.0/api/testexec/{test_exec_key}/test - Get tests in execution (v1)")
print("-" * 80)
try:
    url = f"{base_url}/rest/raven/1.0/api/testexec/{test_exec_key}/test"
    print(f"URL: {url}")
    response = requests.get(url, auth=auth, headers=headers)
    print(f"Status: {response.status_code}")
    if response.ok:
        data = response.json()
        print(f"Tests in execution: {json.dumps(data, indent=2)[:1000]}")
        
        # If we get test runs, try to update one
        if data and len(data) > 0:
            print(f"\nFound {len(data)} test(s) in execution")
            first_test = data[0]
            print(f"First test: {json.dumps(first_test, indent=2)[:500]}")
    else:
        print(f"Error: {response.text[:500]}")
except Exception as e:
    print(f"Exception: {e}")

print("\n" + "="*80 + "\n")

# Test 4: Try to update test status using testrun iteration endpoint
print(f"4. POST /rest/raven/2.0/api/testrun - Create a test run/iteration")
print("-" * 80)
try:
    # First, let's try to get existing test run ID
    url = f"{base_url}/rest/raven/1.0/api/testexec/{test_exec_key}/test"
    response = requests.get(url, auth=auth, headers=headers)
    
    if response.ok:
        tests = response.json()
        if tests and len(tests) > 0:
            # Get the first test
            test_info = tests[0]
            print(f"Test info: {json.dumps(test_info, indent=2)[:500]}")
            
            # Try to find the test run ID
            if 'id' in test_info:
                testrun_id = test_info['id']
                print(f"\nTest Run ID: {testrun_id}")
                
                # Try to update using v2 testrun endpoint
                print(f"\n5. PUT /rest/raven/2.0/api/testrun/{testrun_id}")
                print("-" * 80)
                url = f"{base_url}/rest/raven/2.0/api/testrun/{testrun_id}"
                print(f"URL: {url}")
                
                # Try to update with minimal data
                update_data = {
                    "status": "PASS",
                    "comment": "Test run updated via v2 API"
                }
                
                response = requests.put(url, auth=auth, headers=headers, json=update_data)
                print(f"Status: {response.status_code}")
                if response.ok:
                    print(f"Success! Response: {response.text[:500]}")
                else:
                    print(f"Error: {response.text[:500]}")
except Exception as e:
    print(f"Exception: {e}")

print("\n" + "="*80 + "\n")

# Test 5: Try the iteration/step endpoint structure from screenshot
print("6. Testing iteration/step/status endpoint structure")
print("-" * 80)
print("Based on screenshot, the structure seems to be:")
print("  /testrun/{id}/iteration/{iterationId}/step/{stepResultId}/status")
print("\nThis appears to be for updating individual step results within test runs.")
print("To use this, we would need:")
print("  1. testrun ID - the test run/result ID")
print("  2. iteration ID - which iteration/execution")
print("  3. stepResultId - the specific step result to update")
print("\nLet's try to find these IDs...")

try:
    # Get test execution details
    url = f"{base_url}/rest/raven/1.0/api/testexec/{test_exec_key}/test"
    response = requests.get(url, auth=auth, headers=headers)
    
    if response.ok:
        tests = response.json()
        print(f"\nTests structure from v1 API:")
        print(json.dumps(tests, indent=2)[:1500])
except Exception as e:
    print(f"Exception: {e}")

print("\n" + "="*80)
print("TEST COMPLETE")
print("="*80)
