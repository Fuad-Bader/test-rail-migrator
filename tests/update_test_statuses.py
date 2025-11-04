#!/usr/bin/env python3
"""
Update Test Execution Results (Statuses Only)
Use this script after fixing the Jira screen configuration issue
to update test statuses without re-running the full migration
"""

import json
import sqlite3
from migrator import JiraXrayClient, map_testrail_status_to_xray, get_db_connection

def load_mapping():
    """Load the migration mapping"""
    try:
        with open('migration_mapping.json', 'r') as f:
            return json.load(f)
    except FileNotFoundError:
        print("❌ Error: migration_mapping.json not found")
        print("   Please run the full migration first (migrator.py)")
        return None

def update_test_statuses_batch(client, mapping):
    """Update test statuses using import/execution API (batch mode)"""
    print("\n[Method 1] Using Xray Import Execution API (Batch Mode)...")
    
    db = get_db_connection()
    cursor = db.cursor()
    
    # Get statuses for mapping
    cursor.execute('SELECT * FROM statuses')
    statuses = [dict(zip([desc[0] for desc in cursor.description], row)) 
                for row in cursor.fetchall()]
    
    # Get all test results grouped by execution
    cursor.execute('''
        SELECT t.run_id, t.case_id, r.status_id, r.comment, r.defects
        FROM tests t
        LEFT JOIN results r ON t.id = r.test_id
        WHERE r.id IS NOT NULL
        ORDER BY t.run_id
    ''')
    
    results = cursor.fetchall()
    columns = [desc[0] for desc in cursor.description]
    
    # Group by test execution
    executions = {}
    for row in results:
        result = dict(zip(columns, row))
        run_id = result['run_id']
        
        if run_id not in executions:
            executions[run_id] = []
        
        case_id = result['case_id']
        test_key = mapping['cases'].get(str(case_id))
        
        if test_key:
            executions[run_id].append({
                'testKey': test_key,
                'status': map_testrail_status_to_xray(result['status_id'], statuses),
                'comment': result.get('comment') or 'Imported from TestRail'
            })
    
    # Update each execution
    success_count = 0
    fail_count = 0
    
    for run_id, tests in executions.items():
        exec_key = mapping['runs'].get(str(run_id))
        
        if not exec_key:
            continue
        
        print(f"\n  Updating {exec_key}: {len(tests)} tests...")
        
        try:
            payload = {
                "testExecutionKey": exec_key,
                "tests": tests
            }
            
            response = client._make_xray_request('POST', 'import/execution', data=payload)
            print(f"  ✅ Success: {exec_key}")
            success_count += 1
            
        except Exception as e:
            print(f"  ❌ Failed: {exec_key} - {str(e)[:100]}")
            fail_count += 1
    
    db.close()
    
    print(f"\n✅ Updated {success_count} test executions")
    if fail_count > 0:
        print(f"❌ Failed: {fail_count} test executions")
    
    return success_count > 0

def update_test_statuses_individual(client, mapping):
    """Update test statuses one by one (slower but more reliable)"""
    print("\n[Method 2] Using Individual Status Update API...")
    
    db = get_db_connection()
    cursor = db.cursor()
    
    # Get statuses for mapping
    cursor.execute('SELECT * FROM statuses')
    statuses = [dict(zip([desc[0] for desc in cursor.description], row)) 
                for row in cursor.fetchall()]
    
    # Get all test results
    cursor.execute('''
        SELECT t.*, r.status_id, r.comment, r.defects
        FROM tests t
        LEFT JOIN results r ON t.id = r.test_id
        WHERE r.id IS NOT NULL
        ORDER BY t.run_id
    ''')
    
    test_results = cursor.fetchall()
    columns = [desc[0] for desc in cursor.description]
    
    success_count = 0
    fail_count = 0
    
    for row in test_results:
        test = dict(zip(columns, row))
        
        run_key = mapping['runs'].get(str(test['run_id']))
        test_key = mapping['cases'].get(str(test['case_id']))
        
        if not run_key or not test_key:
            continue
        
        try:
            xray_status = map_testrail_status_to_xray(test['status_id'], statuses)
            
            client.update_test_execution_status(
                test_execution_key=run_key,
                test_key=test_key,
                status=xray_status,
                comment=test.get('comment')
            )
            
            success_count += 1
            
            if success_count % 10 == 0:
                print(f"  ✓ Updated {success_count} test results...")
                
        except Exception as e:
            fail_count += 1
    
    db.close()
    
    print(f"\n✅ Updated {success_count} test results")
    if fail_count > 0:
        print(f"⚠️  Skipped {fail_count} test results")
    
    return success_count > 0

def main():
    print("="*80)
    print("UPDATE TEST EXECUTION STATUSES")
    print("="*80)
    
    # Load config
    with open('config.json', 'r') as f:
        config = json.load(f)
    
    # Load mapping
    mapping = load_mapping()
    if not mapping:
        return
    
    print(f"\nLoaded mapping:")
    print(f"  - Test Cases: {len(mapping['cases'])}")
    print(f"  - Test Executions: {len(mapping['runs'])}")
    
    # Connect to Jira
    print("\nConnecting to Jira/Xray...")
    client = JiraXrayClient(
        base_url=config['jira_url'],
        username=config['jira_username'],
        password=config['jira_password']
    )
    
    project_key = config['jira_project_key']
    project = client.get_project(project_key)
    print(f"✓ Connected to project: {project['name']}")
    
    # Try batch update first (faster)
    print("\n" + "="*80)
    print("ATTEMPTING STATUS UPDATES")
    print("="*80)
    
    success = update_test_statuses_batch(client, mapping)
    
    if not success:
        print("\n⚠️  Batch update failed. Trying individual updates...")
        success = update_test_statuses_individual(client, mapping)
    
    if success:
        print("\n" + "="*80)
        print("✅ STATUS UPDATE COMPLETE!")
        print("="*80)
        print("\nTest execution statuses have been updated from TestRail data.")
        print("Check your Jira Test Executions to verify.")
    else:
        print("\n" + "="*80)
        print("❌ STATUS UPDATE FAILED")
        print("="*80)
        print("\nThe API is still not working. Possible solutions:")
        print("1. Fix the Jira screen configuration (see XRAY_STATUS_UPDATE_ISSUE.md)")
        print("2. Update statuses manually in Jira UI")
        print("3. Contact Xray support for API guidance")

if __name__ == '__main__':
    main()
