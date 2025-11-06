#!/usr/bin/env python3
"""
Test script to verify milestone and test steps migration
"""
import json
import sqlite3
from migrator import JiraXrayClient

def test_milestone_migration():
    """Test milestone migration with duplicate handling"""
    print("=" * 80)
    print("TESTING MILESTONE MIGRATION")
    print("=" * 80)
    
    with open('config.json') as f:
        config = json.load(f)
    
    client = JiraXrayClient(
        config['jira_url'],
        config['jira_username'],
        config['jira_password']
    )
    
    project_key = config['jira_project_key']
    
    # Get existing versions
    print("\n1. Checking existing versions in Jira...")
    try:
        versions = client._make_request('GET', f'project/{project_key}/versions')
        print(f"   Found {len(versions)} existing version(s):")
        for v in versions[:5]:
            print(f"     - {v['name']} (ID: {v['id']})")
    except Exception as e:
        print(f"   Error: {e}")
        return False
    
    # Get milestones from database
    print("\n2. Checking milestones in database...")
    db = sqlite3.connect('testrail.db')
    cursor = db.cursor()
    cursor.execute('SELECT id, name, is_completed FROM milestones LIMIT 3')
    milestones = cursor.fetchall()
    db.close()
    
    print(f"   Found {len(milestones)} milestone(s) to test:")
    for m in milestones:
        print(f"     - ID {m[0]}: {m[1]} (Completed: {m[2]})")
    
    print("\n✓ Milestone check complete")
    print("  Run python migrator.py to test full migration with duplicate handling")
    return True

def test_steps_extraction():
    """Test extracting test steps from a case"""
    print("\n" + "=" * 80)
    print("TESTING TEST STEPS EXTRACTION")
    print("=" * 80)
    
    db = sqlite3.connect('testrail.db')
    cursor = db.cursor()
    
    # Get case 2 which has steps
    cursor.execute('SELECT id, title, custom_fields FROM cases WHERE id=2')
    case = cursor.fetchone()
    db.close()
    
    if not case:
        print("  ❌ Case 2 not found")
        return False
    
    print(f"\n1. Case: {case[1]} (ID: {case[0]})")
    
    # Parse custom fields
    custom_fields = {}
    if case[2]:
        try:
            custom_fields = eval(case[2])
        except:
            print("  ❌ Could not parse custom fields")
            return False
    
    print("\n2. Custom Fields Found:")
    print(f"   - custom_preconds: {'Yes' if custom_fields.get('custom_preconds') else 'No'}")
    print(f"   - custom_steps: {'Yes' if custom_fields.get('custom_steps') else 'No'}")
    print(f"   - custom_steps_separated: {'Yes' if custom_fields.get('custom_steps_separated') else 'No'}")
    print(f"   - custom_expected: {'Yes' if custom_fields.get('custom_expected') else 'No'}")
    
    # Show preconditions
    if custom_fields.get('custom_preconds'):
        print(f"\n3. Preconditions:")
        print(f"   {custom_fields['custom_preconds'][:100]}...")
    
    # Show steps
    if custom_fields.get('custom_steps'):
        print(f"\n4. Test Steps (plain text):")
        steps_text = custom_fields['custom_steps']
        step_lines = [line.strip() for line in steps_text.split('\n') if line.strip()]
        for i, line in enumerate(step_lines[:3], 1):
            print(f"   Step {i}: {line[:80]}...")
        print(f"   Total: {len(step_lines)} steps")
    
    # Show expected
    if custom_fields.get('custom_expected'):
        print(f"\n5. Expected Results:")
        print(f"   {custom_fields['custom_expected'][:100]}...")
    
    # Simulate step creation
    print(f"\n6. Creating Xray-compatible steps:")
    test_steps = []
    if custom_fields.get('custom_steps'):
        steps_text = custom_fields['custom_steps']
        step_lines = [line.strip() for line in steps_text.split('\n') if line.strip()]
        for i, line in enumerate(step_lines, 1):
            test_steps.append({
                'action': line,
                'data': '',
                'expected': custom_fields.get('custom_expected', '') if i == len(step_lines) else ''
            })
        
        print(f"   ✓ Created {len(test_steps)} Xray steps")
        print(f"   Sample step structure:")
        print(f"     {test_steps[0]}")
    
    print("\n✓ Test steps extraction complete")
    return True

if __name__ == '__main__':
    test_milestone_migration()
    test_steps_extraction()
    
    print("\n" + "=" * 80)
    print("NEXT STEPS")
    print("=" * 80)
    print("\n1. Run a fresh migration:")
    print("   rm testrail.db migration_mapping.json")
    print("   python importer.py")
    print("   python migrator.py")
    print("\n2. Check results:")
    print("   - Milestones should skip duplicates and map to existing versions")
    print("   - Test cases should have steps in Xray")
    print("=" * 80)
