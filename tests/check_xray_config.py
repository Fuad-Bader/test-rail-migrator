#!/usr/bin/env python3
"""
Check Xray configuration and issue types
"""

import json
from migrator import JiraXrayClient

def main():
    # Load config
    with open('config.json', 'r') as f:
        config = json.load(f)
    
    print("="*80)
    print("XRAY CONFIGURATION CHECK")
    print("="*80)
    
    client = JiraXrayClient(
        base_url=config['jira_url'],
        username=config['jira_username'],
        password=config['jira_password']
    )
    
    project_key = config['jira_project_key']
    project = client.get_project(project_key)
    print(f"\n✓ Project: {project['name']} ({project_key})")
    
    # Check 1: Get all issue types from the server
    print("\n[Check 1] All available issue types on server:")
    try:
        all_types = client._make_request('GET', 'issuetype')
        for itype in all_types:
            xray_marker = " ⭐" if any(x in itype['name'] for x in ['Test', 'Precondition']) else ""
            print(f"   - {itype['name']} (id: {itype['id']}){xray_marker}")
    except Exception as e:
        print(f"   ❌ Error: {e}")
    
    # Check 2: Try simplified createmeta
    print("\n[Check 2] Issue types available for creation in project:")
    try:
        meta = client._make_request('GET', 'issue/createmeta', params={'projectKeys': project_key})
        
        if 'projects' in meta and len(meta['projects']) > 0:
            for proj in meta['projects']:
                for itype in proj.get('issuetypes', []):
                    xray_marker = " ⭐" if any(x in itype['name'] for x in ['Test', 'Precondition', 'Execution', 'Set', 'Plan']) else ""
                    print(f"   - {itype['name']} (id: {itype['id']}){xray_marker}")
        else:
            print("   ⚠ No issue types found in createmeta")
    except Exception as e:
        print(f"   ❌ Error: {e}")
    
    # Check 3: Get project configuration
    print("\n[Check 3] Project issue type scheme:")
    try:
        # Get the project's issue type scheme
        project_detail = client._make_request('GET', f'project/{project_key}')
        
        if 'issueTypes' in project_detail:
            print(f"   Found {len(project_detail['issueTypes'])} issue types:")
            xray_count = 0
            for itype in project_detail['issueTypes']:
                is_xray = any(x in itype['name'] for x in ['Test', 'Precondition', 'Execution', 'Set', 'Plan'])
                marker = " ⭐ XRAY" if is_xray else ""
                print(f"   - {itype['name']} (id: {itype['id']}){marker}")
                if is_xray:
                    xray_count += 1
            
            print(f"\n   Summary: {xray_count} Xray issue types configured")
            
            if xray_count == 0:
                print("\n   ⚠ WARNING: No Xray issue types found!")
                print("   You need to add Xray issue types to your project.")
                print("   Steps:")
                print("   1. Go to Project Settings → Issue Types")
                print("   2. Add these Xray issue types:")
                print("      - Test")
                print("      - Test Set")
                print("      - Test Execution")
                print("      - Test Plan (optional)")
                print("      - Precondition (optional)")
        
    except Exception as e:
        print(f"   ❌ Error: {e}")
    
    # Check 4: Try to create a test issue (dry run info)
    print("\n[Check 4] Testing issue creation capability:")
    try:
        # Get fields for Test issue type
        meta = client._make_request('GET', 'issue/createmeta', params={
            'projectKeys': project_key,
            'issuetypeNames': 'Test',
            'expand': 'projects.issuetypes.fields'
        })
        
        if 'projects' in meta and len(meta['projects']) > 0:
            project_meta = meta['projects'][0]
            if 'issuetypes' in project_meta and len(project_meta['issuetypes']) > 0:
                print("   ✓ 'Test' issue type is available for creation")
                test_type = project_meta['issuetypes'][0]
                print(f"   - Test Type ID: {test_type['id']}")
                print(f"   - Test Type Name: {test_type['name']}")
                
                # Check required fields
                fields = test_type.get('fields', {})
                required = [name for name, info in fields.items() if info.get('required', False)]
                print(f"   - Required fields: {', '.join(required)}")
            else:
                print("   ❌ 'Test' issue type NOT found")
                print("   You need to add 'Test' issue type to your project")
        else:
            print("   ❌ Could not retrieve metadata for 'Test' issue type")
            print("   This usually means the issue type is not configured for your project")
    
    except Exception as e:
        print(f"   ⚠ Could not check Test issue type: {e}")
    
    print("\n" + "="*80)

if __name__ == '__main__':
    main()
