#!/usr/bin/env python3
"""
Quick test of the fixed Jira client
"""

import sys
sys.path.insert(0, '.')

from migrator import JiraXrayClient
import json

print("=" * 80)
print("Testing Fixed Jira Client")
print("=" * 80)

# Load config
with open('config.json') as f:
    config = json.load(f)

JIRA_URL = config.get('jira_url')
JIRA_USERNAME = config.get('jira_username')
JIRA_PASSWORD = config.get('jira_password')
JIRA_PROJECT_KEY = config.get('jira_project_key')

print(f"\nConnecting to: {JIRA_URL}")
print(f"Username: {JIRA_USERNAME}")
print(f"Project: {JIRA_PROJECT_KEY}")

try:
    # Create client
    print("\nInitializing client...")
    client = JiraXrayClient(JIRA_URL, JIRA_USERNAME, JIRA_PASSWORD)
    
    # Test 1: Get user info
    print("\n[Test 1] Getting current user info...")
    myself = client._make_request('GET', 'myself')
    print(f"✓ SUCCESS!")
    print(f"  User: {myself.get('displayName')}")
    print(f"  Email: {myself.get('emailAddress')}")
    print(f"  Active: {myself.get('active')}")
    
    # Test 2: Get project
    print(f"\n[Test 2] Getting project '{JIRA_PROJECT_KEY}'...")
    project = client.get_project(JIRA_PROJECT_KEY)
    print(f"✓ SUCCESS!")
    print(f"  Name: {project.get('name')}")
    print(f"  Key: {project.get('key')}")
    print(f"  Lead: {project.get('lead', {}).get('displayName')}")
    
    # Test 3: List projects
    print(f"\n[Test 3] Listing accessible projects...")
    projects = client._make_request('GET', 'project')
    print(f"✓ SUCCESS! Found {len(projects)} projects:")
    for proj in projects[:5]:
        print(f"    - {proj.get('key')}: {proj.get('name')}")
    
    print("\n" + "=" * 80)
    print("✓ ALL TESTS PASSED!")
    print("=" * 80)
    print("\nYour Jira connection is working correctly now!")
    print("You can use the GUI to import and export data.")
    
except Exception as e:
    print("\n" + "=" * 80)
    print("✗ TEST FAILED")
    print("=" * 80)
    print(f"\nError: {e}")
    import traceback
    traceback.print_exc()
