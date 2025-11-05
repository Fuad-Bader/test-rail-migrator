#!/usr/bin/env python3
"""
Upload actual attachments from the attachments folder to a Jira issue
"""
import os
import json
from migrator import JiraXrayClient

def upload_real_attachments():
    """Upload actual downloaded attachments to a Jira issue"""
    print("=" * 80)
    print("UPLOADING REAL ATTACHMENTS TO JIRA")
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
    
    # Use the test issue we just created
    test_key = "MT-127"
    
    # Check attachments folder
    attachments_dir = 'attachments'
    if not os.path.exists(attachments_dir):
        print(f"❌ Attachments directory not found: {attachments_dir}")
        return
    
    files = [f for f in os.listdir(attachments_dir) if os.path.isfile(os.path.join(attachments_dir, f))]
    
    if not files:
        print(f"❌ No files found in {attachments_dir}/")
        return
    
    print(f"\nFound {len(files)} files in {attachments_dir}/")
    print(f"Uploading to issue: {test_key}")
    print()
    
    uploaded = 0
    failed = 0
    
    for filename in files:
        file_path = os.path.join(attachments_dir, filename)
        result = client.add_attachment(test_key, file_path)
        if result:
            uploaded += 1
        else:
            failed += 1
    
    print(f"\n" + "=" * 80)
    print(f"UPLOAD SUMMARY")
    print("=" * 80)
    print(f"✓ Successfully uploaded: {uploaded}")
    print(f"❌ Failed: {failed}")
    print(f"Total files: {len(files)}")
    
    print(f"\n" + "=" * 80)
    print(f"VERIFICATION")
    print("=" * 80)
    print(f"Open in browser: {config['jira_url']}/browse/{test_key}")
    print(f"Check the Attachments section to see all {uploaded} files")
    print("=" * 80)

if __name__ == '__main__':
    upload_real_attachments()
