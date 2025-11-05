#!/usr/bin/env python3
"""
Add Jira mappings to database and validate/upload all attachments
"""
import os
import json
import sqlite3
from migrator import JiraXrayClient

def add_mapping_to_database():
    """Add Jira issue mapping to the database"""
    print("=" * 80)
    print("ADDING JIRA MAPPINGS TO DATABASE")
    print("=" * 80)
    
    # Load mapping file
    with open('migration_mapping.json') as f:
        mapping = json.load(f)
    
    # Connect to database
    db = sqlite3.connect('testrail.db')
    cursor = db.cursor()
    
    # Create mapping table if it doesn't exist
    print("\n1. Creating mappings table...")
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS jira_mappings (
            testrail_entity_type TEXT,
            testrail_entity_id INTEGER,
            jira_key TEXT,
            PRIMARY KEY (testrail_entity_type, testrail_entity_id)
        )
    ''')
    
    # Insert case mappings
    print("2. Inserting case mappings...")
    case_count = 0
    for testrail_id, jira_key in mapping['cases'].items():
        cursor.execute(
            'INSERT OR REPLACE INTO jira_mappings (testrail_entity_type, testrail_entity_id, jira_key) VALUES (?, ?, ?)',
            ('case', int(testrail_id), jira_key)
        )
        case_count += 1
    print(f"   ✓ Added {case_count} case mappings")
    
    # Insert suite mappings
    print("3. Inserting suite mappings...")
    suite_count = 0
    for testrail_id, jira_key in mapping['suites'].items():
        cursor.execute(
            'INSERT OR REPLACE INTO jira_mappings (testrail_entity_type, testrail_entity_id, jira_key) VALUES (?, ?, ?)',
            ('suite', int(testrail_id), jira_key)
        )
        suite_count += 1
    print(f"   ✓ Added {suite_count} suite mappings")
    
    # Insert run mappings
    print("4. Inserting run mappings...")
    run_count = 0
    for testrail_id, jira_key in mapping['runs'].items():
        cursor.execute(
            'INSERT OR REPLACE INTO jira_mappings (testrail_entity_type, testrail_entity_id, jira_key) VALUES (?, ?, ?)',
            ('run', int(testrail_id), jira_key)
        )
        run_count += 1
    print(f"   ✓ Added {run_count} run mappings")
    
    db.commit()
    db.close()
    
    print(f"\n✓ Total mappings added: {case_count + suite_count + run_count}")
    return True

def validate_and_upload_attachments():
    """Validate and upload all attachments to their correct Jira issues"""
    print("\n" + "=" * 80)
    print("VALIDATING AND UPLOADING ATTACHMENTS")
    print("=" * 80)
    
    # Load config
    with open('config.json') as f:
        config = json.load(f)
    
    # Create Jira client
    client = JiraXrayClient(
        config['jira_url'],
        config['jira_username'],
        config['jira_password']
    )
    
    # Connect to database
    db = sqlite3.connect('testrail.db')
    cursor = db.cursor()
    
    # Get all attachments with their Jira mappings
    print("\n1. Querying attachments and mappings...")
    cursor.execute('''
        SELECT 
            a.id,
            a.entity_type,
            a.entity_id,
            a.filename,
            a.local_path,
            m.jira_key
        FROM attachments a
        LEFT JOIN jira_mappings m 
            ON a.entity_type = m.testrail_entity_type 
            AND a.entity_id = m.testrail_entity_id
        ORDER BY a.entity_type, a.entity_id, a.filename
    ''')
    
    attachments = cursor.fetchall()
    
    if not attachments:
        print("   ⚠ No attachments found in database")
        db.close()
        return
    
    print(f"   ✓ Found {len(attachments)} attachment(s)")
    
    # Group attachments by Jira issue
    issues_with_attachments = {}
    unmapped_attachments = []
    
    for att_id, entity_type, entity_id, filename, local_path, jira_key in attachments:
        if not jira_key:
            unmapped_attachments.append((entity_type, entity_id, filename))
            continue
        
        if jira_key not in issues_with_attachments:
            issues_with_attachments[jira_key] = []
        
        issues_with_attachments[jira_key].append({
            'id': att_id,
            'entity_type': entity_type,
            'entity_id': entity_id,
            'filename': filename,
            'local_path': local_path
        })
    
    if unmapped_attachments:
        print(f"\n   ⚠ Warning: {len(unmapped_attachments)} attachment(s) have no Jira mapping:")
        for entity_type, entity_id, filename in unmapped_attachments:
            print(f"      - {entity_type} {entity_id}: {filename}")
    
    # Upload attachments to each issue
    print(f"\n2. Uploading attachments to {len(issues_with_attachments)} issue(s)...\n")
    
    total_uploaded = 0
    total_failed = 0
    total_missing = 0
    
    for jira_key, attachments_list in sorted(issues_with_attachments.items()):
        print(f"   Issue {jira_key} ({len(attachments_list)} attachment(s)):")
        
        for att in attachments_list:
            if not os.path.exists(att['local_path']):
                print(f"      ❌ File not found: {att['filename']}")
                total_missing += 1
                continue
            
            result = client.add_attachment(jira_key, att['local_path'])
            if result:
                total_uploaded += 1
            else:
                total_failed += 1
        
        print()  # Empty line between issues
    
    db.close()
    
    # Summary
    print("=" * 80)
    print("UPLOAD SUMMARY")
    print("=" * 80)
    print(f"✓ Successfully uploaded: {total_uploaded}")
    print(f"❌ Failed: {total_failed}")
    print(f"⚠ Missing files: {total_missing}")
    print(f"📁 Total attachments processed: {len(attachments)}")
    print("=" * 80)
    
    # Verification instructions
    if total_uploaded > 0:
        print("\nVERIFICATION:")
        print("Check these issues in Jira to verify attachments:")
        for jira_key in sorted(issues_with_attachments.keys()):
            print(f"   {config['jira_url']}/browse/{jira_key}")

if __name__ == '__main__':
    # Step 1: Add mappings to database
    if add_mapping_to_database():
        # Step 2: Validate and upload attachments
        validate_and_upload_attachments()
