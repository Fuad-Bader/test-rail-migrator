#!/usr/bin/env python3
"""
Test script to check available issue types in Jira project
"""

import json
from migrator import JiraXrayClient

def test_issue_types():
    """Check what issue types are available in the project"""
    
    # Load config
    with open('config.json', 'r') as f:
        config = json.load(f)
    
    print("="*80)
    print("CHECKING JIRA ISSUE TYPES")
    print("="*80)
    
    # Connect
    client = JiraXrayClient(
        base_url=config['jira_url'],
        username=config['jira_username'],
        password=config['jira_password']
    )
    
    project_key = config['jira_project_key']
    
    # Get project info
    project = client.get_project(project_key)
    print(f"\n✓ Connected to project: {project['name']}")
    
    # Test 1: Get project metadata
    print("\n[Test 1] Getting project metadata...")
    try:
        response = client._make_request(
            'GET',
            f'project/{project_key}'
        )
        print(f"✓ Project Key: {response['key']}")
        print(f"✓ Project Name: {response['name']}")
        print(f"✓ Project ID: {response['id']}")
        
        if 'issueTypes' in response:
            print(f"\n✓ Found {len(response['issueTypes'])} issue types in project:")
            for itype in response['issueTypes']:
                print(f"   - {itype['name']} (id: {itype['id']}, subtask: {itype.get('subtask', False)})")
        
    except Exception as e:
        print(f"❌ Error: {e}")
    
    # Test 2: Get create metadata for project
    print("\n[Test 2] Getting create metadata for project...")
    try:
        response = client._make_request(
            'GET',
            'issue/createmeta',
            params={
                'projectKeys': project_key,
                'expand': 'projects.issuetypes.fields'
            }
        )
        
        if 'projects' in response and len(response['projects']) > 0:
            project = response['projects'][0]
            issue_types = project.get('issuetypes', [])
            
            print(f"\n✓ Found {len(issue_types)} creatable issue types:")
            for itype in issue_types:
                print(f"\n   Issue Type: {itype['name']}")
                print(f"   - ID: {itype['id']}")
                print(f"   - Subtask: {itype.get('subtask', False)}")
                
                # Check for Xray-specific fields
                fields = itype.get('fields', {})
                
                # Look for test-related fields
                test_fields = []
                for field_key, field_info in fields.items():
                    field_name = field_info.get('name', '')
                    if any(keyword in field_name.lower() for keyword in ['test', 'step', 'scenario']):
                        test_fields.append(f"{field_name} ({field_key})")
                
                if test_fields:
                    print(f"   - Test-related fields: {', '.join(test_fields)}")
        else:
            print("❌ No projects found in create metadata")
    
    except Exception as e:
        print(f"❌ Error: {e}")
    
    # Test 3: Check for Xray issue types specifically
    print("\n[Test 3] Checking for Xray-specific issue types...")
    try:
        response = client._make_request(
            'GET',
            'issue/createmeta',
            params={
                'projectKeys': project_key
            }
        )
        
        if 'projects' in response and len(response['projects']) > 0:
            project = response['projects'][0]
            issue_types = project.get('issuetypes', [])
            
            xray_types = ['Test', 'Test Set', 'Test Execution', 'Test Plan', 'Precondition']
            found_xray_types = {}
            
            for itype in issue_types:
                if itype['name'] in xray_types:
                    found_xray_types[itype['name']] = itype['id']
            
            if found_xray_types:
                print(f"\n✓ Found Xray issue types:")
                for name, type_id in found_xray_types.items():
                    print(f"   - {name}: {type_id}")
            else:
                print("\n⚠ No Xray issue types found!")
                print("   Available types:")
                for itype in issue_types:
                    print(f"   - {itype['name']} (id: {itype['id']})")
    
    except Exception as e:
        print(f"❌ Error: {e}")
    
    # Test 4: Try to get Xray API info
    print("\n[Test 4] Checking Xray REST API...")
    try:
        # Try to get test issue types from Xray API
        response = client._make_xray_request(
            'GET',
            'api/settings/teststatuses'
        )
        print(f"✓ Xray API is accessible")
        print(f"✓ Test statuses: {response}")
    except Exception as e:
        print(f"⚠ Xray API error: {e}")
    
    print("\n" + "="*80)
    print("DIAGNOSIS COMPLETE")
    print("="*80)

if __name__ == '__main__':
    test_issue_types()
