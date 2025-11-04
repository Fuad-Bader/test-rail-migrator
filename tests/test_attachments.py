#!/usr/bin/env python3
"""
Test script to check if attachments are properly imported and can be migrated
"""

import sqlite3
import os
import json

def check_attachments():
    """Check attachments in database and files"""
    
    print("=" * 80)
    print("ATTACHMENT MIGRATION CHECK")
    print("=" * 80)
    
    # Check if database exists
    if not os.path.exists('testrail.db'):
        print("\n❌ Database not found. Please run import first.")
        return
    
    # Connect to database
    conn = sqlite3.connect('testrail.db')
    cursor = conn.cursor()
    
    # Check if attachments table exists
    cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='attachments'")
    if not cursor.fetchone():
        print("\n❌ Attachments table not found. Please run import with attachment support.")
        conn.close()
        return
    
    print("\n✓ Attachments table found")
    
    # Get attachment statistics
    cursor.execute('SELECT COUNT(*) FROM attachments')
    total_count = cursor.fetchone()[0]
    print(f"\nTotal attachments in database: {total_count}")
    
    if total_count == 0:
        print("\nℹ️  No attachments found in TestRail data")
        conn.close()
        return
    
    # Count by entity type
    cursor.execute('SELECT entity_type, COUNT(*) FROM attachments GROUP BY entity_type')
    for entity_type, count in cursor.fetchall():
        print(f"  - {entity_type}: {count}")
    
    # Check file existence
    cursor.execute('SELECT local_path FROM attachments')
    paths = cursor.fetchall()
    
    existing_files = 0
    missing_files = 0
    
    for (path,) in paths:
        if os.path.exists(path):
            existing_files += 1
        else:
            missing_files += 1
    
    print(f"\nFile status:")
    print(f"  - Existing files: {existing_files}")
    print(f"  - Missing files: {missing_files}")
    
    # Show sample attachments
    print("\nSample attachments (first 5):")
    cursor.execute('SELECT entity_type, entity_id, filename, size, local_path FROM attachments LIMIT 5')
    for entity_type, entity_id, filename, size, path in cursor.fetchall():
        size_kb = size / 1024 if size else 0
        exists = "✓" if os.path.exists(path) else "✗"
        print(f"  {exists} {entity_type}:{entity_id} - {filename} ({size_kb:.1f} KB)")
    
    # Check migration mapping
    print("\nChecking migration mapping...")
    if not os.path.exists('migration_mapping.json'):
        print("  ⚠️  No migration mapping found. Run export first.")
    else:
        with open('migration_mapping.json') as f:
            mapping = json.load(f)
        
        # Count mappings
        case_count = len(mapping.get('cases', {}))
        run_count = len(mapping.get('runs', {}))
        
        print(f"  - Test cases mapped: {case_count}")
        print(f"  - Test runs mapped: {run_count}")
        
        # Check which attachments can be migrated
        cursor.execute('SELECT entity_type, entity_id FROM attachments')
        attachments = cursor.fetchall()
        
        migratable = 0
        for entity_type, entity_id in attachments:
            if entity_type == 'case' and entity_id in mapping.get('cases', {}):
                migratable += 1
            elif entity_type == 'result':
                # Check if result's run is mapped
                cursor.execute('SELECT test_id FROM results WHERE id = ?', (entity_id,))
                result = cursor.fetchone()
                if result:
                    test_id = result[0]
                    cursor.execute('SELECT run_id FROM tests WHERE id = ?', (test_id,))
                    test = cursor.fetchone()
                    if test and test[0] in mapping.get('runs', {}):
                        migratable += 1
        
        print(f"  - Attachments ready to migrate: {migratable}")
    
    conn.close()
    
    print("\n" + "=" * 80)
    print("Check complete!")
    print("=" * 80)

if __name__ == '__main__':
    check_attachments()
