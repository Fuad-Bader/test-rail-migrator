#!/usr/bin/env python3
"""Test script to verify test steps update API call"""
import json
import sqlite3
from migrator import JiraXrayClient

# Load config
with open('config.json', 'r') as f:
    config = json.load(f)

# Connect to database
conn = sqlite3.connect('testrail.db')
cursor = conn.cursor()

# Get test case 2 which has steps
cursor.execute("SELECT id, title, custom_fields FROM cases WHERE id = 2")
row = cursor.fetchone()

if row:
    case_id, title, custom_fields_str = row
    # Custom fields are stored as Python dict literal, not JSON
    import ast
    custom_fields = ast.literal_eval(custom_fields_str) if custom_fields_str else {}
    
    print(f"Test Case: {title}")
    print(f"Custom Fields Keys: {list(custom_fields.keys())}")
    
    # Parse steps
    if custom_fields.get('custom_steps'):
        steps_text = custom_fields['custom_steps']
        print(f"\nSteps Text:\n{steps_text}\n")
        
        test_steps = []
        step_lines = [line.strip() for line in steps_text.split('\n') if line.strip()]
        
        for i, line in enumerate(step_lines, 1):
            step = {
                'action': line,
                'data': '',
                'expected': custom_fields.get('custom_expected', '') if i == len(step_lines) else ''
            }
            test_steps.append(step)
        
        print(f"Parsed {len(test_steps)} steps:")
        for idx, step in enumerate(test_steps, 1):
            print(f"  Step {idx}: {step['action'][:50]}...")
        
        # Get the Jira key for this test case
        cursor.execute("SELECT jira_key FROM jira_mappings WHERE testrail_entity_type = 'case' AND testrail_entity_id = ?", (case_id,))
        mapping_row = cursor.fetchone()
        
        if mapping_row:
            jira_key = mapping_row[0]
            print(f"\nJira Issue: {jira_key}")
            
            # Initialize client and test the update
            client = JiraXrayClient(
                config['jira_url'],
                config['jira_username'],
                config['jira_password']
            )
            
            # Prepare steps data for Xray
            steps_data = []
            for idx, step in enumerate(test_steps, 1):
                step_obj = {
                    'index': idx,
                    'step': step.get('action', ''),
                    'data': step.get('data', ''),
                    'result': step.get('expected', '')
                }
                steps_data.append(step_obj)
            
            print(f"\nAttempting to update test steps for {jira_key}...")
            print(f"Steps data: {json.dumps(steps_data, indent=2)}")
            
            try:
                result = client.update_test_steps(jira_key, test_steps)
                if result:
                    print(f"✓ Successfully updated test steps!")
                else:
                    print("✗ Failed to update test steps (no result returned)")
            except Exception as e:
                print(f"✗ Error: {e}")
        else:
            print(f"\n✗ No Jira mapping found for case {case_id}")
    else:
        print("No custom_steps found")

conn.close()
