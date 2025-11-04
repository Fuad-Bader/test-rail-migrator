#!/usr/bin/env python3
"""
Check TestRail database for attachment tables and data
"""

import sqlite3

db = sqlite3.connect('testrail.db')
cursor = db.cursor()

print("="*80)
print("TESTRAIL DATABASE - ATTACHMENT TABLES")
print("="*80)

# Get all tables
cursor.execute("SELECT name FROM sqlite_master WHERE type='table' ORDER BY name")
tables = [row[0] for row in cursor.fetchall()]

print("\n[All Tables in Database]")
for table in tables:
    print(f"  - {table}")

# Look for attachment-related tables
attachment_tables = [t for t in tables if 'attach' in t.lower()]

print(f"\n[Attachment-Related Tables]")
if attachment_tables:
    for table in attachment_tables:
        print(f"\n  Table: {table}")
        
        # Get schema
        cursor.execute(f"PRAGMA table_info({table})")
        columns = cursor.fetchall()
        print(f"  Columns:")
        for col in columns:
            print(f"    - {col[1]} ({col[2]})")
        
        # Get row count
        cursor.execute(f"SELECT COUNT(*) FROM {table}")
        count = cursor.fetchone()[0]
        print(f"  Row count: {count}")
        
        # Show sample data if exists
        if count > 0:
            cursor.execute(f"SELECT * FROM {table} LIMIT 3")
            rows = cursor.fetchall()
            col_names = [desc[0] for desc in cursor.description]
            
            print(f"  Sample data:")
            for row in rows:
                print(f"    {dict(zip(col_names, row))}")
else:
    print("  No attachment tables found")

# Check if results table has attachment info
print("\n[Checking 'results' table for attachment references]")
cursor.execute("PRAGMA table_info(results)")
columns = [col[1] for col in cursor.fetchall()]
print(f"  Columns: {', '.join(columns)}")

if 'attachment_ids' in columns or 'attachments' in columns:
    cursor.execute("SELECT id, attachment_ids FROM results WHERE attachment_ids IS NOT NULL LIMIT 5")
    rows = cursor.fetchall()
    if rows:
        print(f"  Found {len(rows)} results with attachments:")
        for row in rows:
            print(f"    Result ID {row[0]}: {row[1]}")

# Check cases table
print("\n[Checking 'cases' table for attachment references]")
cursor.execute("PRAGMA table_info(cases)")
columns = [col[1] for col in cursor.fetchall()]
if 'attachment_ids' in columns or 'attachments' in columns:
    print("  Has attachment column")

db.close()
print("\n" + "="*80)
