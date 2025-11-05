#!/usr/bin/env python3
"""
Test script to verify attachment download and upload functionality
"""
import os
import sqlite3
import json
from testrail import APIClient

def test_attachment_download():
    """Test downloading attachments from TestRail"""
    print("=" * 80)
    print("TESTING ATTACHMENT DOWNLOAD")
    print("=" * 80)
    
    # Load config
    with open('config.json') as f:
        config = json.load(f)
    
    # Connect to TestRail
    client = APIClient(config['testrail_url'])
    client.user = config['testrail_user']
    client.password = config['testrail_password']
    
    # Test get_attachment endpoint
    print("\n1. Testing get_attachment endpoint...")
    
    # Connect to database to get an attachment ID
    db = sqlite3.connect('testrail.db')
    cursor = db.cursor()
    
    cursor.execute('SELECT id, entity_type, entity_id, filename FROM attachments LIMIT 1')
    row = cursor.fetchone()
    
    if not row:
        print("❌ No attachments found in database. Run importer first.")
        return False
    
    att_id, entity_type, entity_id, filename = row
    print(f"   Testing with attachment ID {att_id}: {filename}")
    
    try:
        # Try to download using get_attachment endpoint
        # The API takes a filepath and saves directly to it
        test_file = f"test_{filename}"
        result = client.send_get(f"get_attachment/{att_id}", test_file)
        
        if result == test_file and os.path.exists(test_file) and os.path.getsize(test_file) > 0:
            print(f"   ✓ Successfully downloaded file: {test_file}")
            print(f"   File size: {os.path.getsize(test_file)} bytes")
            print(f"   Try opening: {test_file}")
            return True
        else:
            print(f"   ❌ Failed to download file - Result: {result}")
            return False
            
    except Exception as e:
        print(f"   ❌ Error downloading attachment: {e}")
        import traceback
        traceback.print_exc()
        return False
    finally:
        db.close()

def test_file_integrity():
    """Test if downloaded files are readable"""
    print("\n" + "=" * 80)
    print("TESTING FILE INTEGRITY")
    print("=" * 80)
    
    attachments_dir = 'attachments'
    if not os.path.exists(attachments_dir):
        print("❌ Attachments directory doesn't exist")
        return False
    
    files = os.listdir(attachments_dir)
    if not files:
        print("❌ No files in attachments directory")
        return False
    
    print(f"\nFound {len(files)} files in {attachments_dir}/")
    
    for filename in files[:5]:  # Test first 5 files
        filepath = os.path.join(attachments_dir, filename)
        size = os.path.getsize(filepath)
        
        print(f"\n  File: {filename}")
        print(f"  Size: {size} bytes")
        
        # Try to read first few bytes
        try:
            with open(filepath, 'rb') as f:
                header = f.read(16)
                print(f"  Header (hex): {header.hex()}")
                
                # Check for common file signatures
                if filename.lower().endswith(('.jpg', '.jpeg')):
                    if header.startswith(b'\xff\xd8\xff'):
                        print(f"  ✓ Valid JPEG signature")
                    else:
                        print(f"  ❌ Invalid JPEG signature")
                elif filename.lower().endswith('.png'):
                    if header.startswith(b'\x89PNG'):
                        print(f"  ✓ Valid PNG signature")
                    else:
                        print(f"  ❌ Invalid PNG signature")
                elif filename.lower().endswith('.pdf'):
                    if header.startswith(b'%PDF'):
                        print(f"  ✓ Valid PDF signature")
                    else:
                        print(f"  ❌ Invalid PDF signature")
                else:
                    print(f"  ? Unknown file type")
        except Exception as e:
            print(f"  ❌ Error reading file: {e}")
    
    return True

def test_jira_upload():
    """Test uploading to Jira"""
    print("\n" + "=" * 80)
    print("TESTING JIRA UPLOAD")
    print("=" * 80)
    
    # Load config
    with open('config.json') as f:
        config = json.load(f)
    
    from migrator import JiraClient
    
    client = JiraClient(
        config['jira_url'],
        config['jira_username'],
        config['jira_token'],
        is_pat=True
    )
    
    # Get a test issue
    print("\n1. Finding a test issue to upload to...")
    db = sqlite3.connect('testrail.db')
    cursor = db.cursor()
    
    cursor.execute('''
        SELECT jira_key FROM test_mapping 
        WHERE jira_key IS NOT NULL 
        LIMIT 1
    ''')
    
    row = cursor.fetchone()
    if not row:
        print("❌ No test mappings found. Run migrator first.")
        return False
    
    test_key = row[0]
    print(f"   Using test issue: {test_key}")
    
    # Create a small test file
    print("\n2. Creating test file...")
    test_file = "test_upload.txt"
    with open(test_file, 'w') as f:
        f.write("This is a test attachment from the attachment verification script.")
    
    print(f"   Created: {test_file}")
    
    # Try to upload
    print(f"\n3. Uploading to {test_key}...")
    result = client.add_attachment(test_key, test_file)
    
    if result:
        print(f"   ✓ Upload successful!")
        print(f"   Response: {result}")
    else:
        print(f"   ❌ Upload failed")
        return False
    
    # Cleanup
    os.remove(test_file)
    db.close()
    
    return True

if __name__ == '__main__':
    print("\n" + "=" * 80)
    print("ATTACHMENT VERIFICATION TESTS")
    print("=" * 80)
    
    # Run tests
    download_ok = test_attachment_download()
    integrity_ok = test_file_integrity()
    upload_ok = test_jira_upload()
    
    print("\n" + "=" * 80)
    print("TEST RESULTS")
    print("=" * 80)
    print(f"Download test: {'✓ PASS' if download_ok else '❌ FAIL'}")
    print(f"File integrity test: {'✓ PASS' if integrity_ok else '❌ FAIL'}")
    print(f"Jira upload test: {'✓ PASS' if upload_ok else '❌ FAIL'}")
    print("=" * 80)
