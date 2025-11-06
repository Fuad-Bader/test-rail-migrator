#!/usr/bin/env python3
"""Debug script to test defects update"""
import json
import requests
from requests.auth import HTTPBasicAuth

# Load config
with open('config.json', 'r') as f:
    config = json.load(f)

base_url = config['jira_url']
username = config['jira_username']
password = config['jira_password']

# Setup auth
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
else:
    headers = {
        'Content-Type': 'application/json',
        'Accept': 'application/json'
    }
    auth = HTTPBasicAuth(username, password)

# Test updating with defects
test_exec_key = "MT-19"
test_key = "MT-1"

print("Getting test run ID...")
url = f"{base_url}/rest/raven/1.0/api/testexec/{test_exec_key}/test"
response = requests.get(url, auth=auth, headers=headers)
tests = response.json()
testrun_id = tests[0]['id']

print(f"Test Run ID: {testrun_id}")

# Try different defect formats
test_cases = [
    ("Without defects", {"status": "FAIL", "comment": "Test without defects"}),
    ("With defects as objects with key", {"status": "FAIL", "comment": "Test", "defects": [{"key": "MT-1"}]}),
    ("With defects as objects with id", {"status": "FAIL", "comment": "Test", "defects": [{"id": "10001"}]}),
    ("With defects as string", {"status": "FAIL", "comment": "Test", "defects": "MT-1,MT-2"}),
]

for name, data in test_cases:
    print(f"\n{'='*80}")
    print(f"Testing: {name}")
    print(f"Data: {json.dumps(data, indent=2)}")
    print("-" * 80)
    
    url = f"{base_url}/rest/raven/2.0/api/testrun/{testrun_id}"
    response = requests.put(url, auth=auth, headers=headers, json=data)
    
    print(f"Status: {response.status_code}")
    if response.ok:
        print(f"✓ Success!")
        result = response.json()
        print(f"Response: {json.dumps(result, indent=2)[:500]}")
    else:
        print(f"✗ Error: {response.text[:500]}")

print("\n" + "="*80)
