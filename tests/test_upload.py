#!/usr/bin/env python3
"""
Test script to verify attachment upload to Jira
Creates a new Test issue and uploads test attachments
"""
import os
import json
from migrator import JiraXrayClient

def create_test_files():
    """Create some test files to upload"""
    print("\n1. Creating test files...")
    
    test_files = []
    
    # Create a text file
    txt_file = "test_text.txt"
    with open(txt_file, 'w') as f:
        f.write("This is a test text file for attachment verification.\n")
        f.write("Created to test the attachment upload functionality.\n")
        f.write("If you can read this, the upload worked! ✅\n")
    test_files.append(txt_file)
    print(f"   ✓ Created: {txt_file}")
    
    # Create a small JSON file
    json_file = "test_data.json"
    with open(json_file, 'w') as f:
        json.dump({
            "test": "data",
            "status": "success",
            "attachments": ["working"],
            "date": "2025-11-05"
        }, f, indent=2)
    test_files.append(json_file)
    print(f"   ✓ Created: {json_file}")
    
    # Create a small HTML file
    html_file = "test_report.html"
    with open(html_file, 'w') as f:
        f.write("""<!DOCTYPE html>
<html>
<head>
    <title>Test Report</title>
    <style>
        body { font-family: Arial, sans-serif; margin: 20px; }
        .success { color: green; }
    </style>
</head>
<body>
    <h1>Attachment Upload Test Report</h1>
    <p class="success">✅ If you can see this HTML rendered, attachments are working!</p>
</body>
</html>""")
    test_files.append(html_file)
    print(f"   ✓ Created: {html_file}")
    
    return test_files

def test_attachment_upload():
    """Test uploading attachments to a new Jira issue"""
    print("=" * 80)
    print("ATTACHMENT UPLOAD TEST")
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
    
    print("\n2. Creating a new Test issue in Jira...")
    
    # Create a test issue
    test_data = {
        'fields': {
            'project': {'key': config['jira_project_key']},
            'summary': 'Attachment Upload Test - ' + str(os.getpid()),
            'description': 'This test issue was created to verify attachment upload functionality.\n\nExpected attachments:\n- test_text.txt\n- test_data.json\n- test_report.html',
            'issuetype': {'name': 'Test'}
        }
    }
    
    try:
        response = client._make_request('POST', 'issue', data=test_data)
        test_key = response['key']
        print(f"   ✓ Created Test issue: {test_key}")
        print(f"   URL: {config['jira_url']}/browse/{test_key}")
    except Exception as e:
        print(f"   ❌ Failed to create issue: {e}")
        return None
    
    # Create test files
    test_files = create_test_files()
    
    # Upload attachments
    print("\n3. Uploading attachments...")
    uploaded = 0
    failed = 0
    
    for file_path in test_files:
        result = client.add_attachment(test_key, file_path)
        if result:
            uploaded += 1
        else:
            failed += 1
    
    print(f"\n4. Upload Summary:")
    print(f"   ✓ Uploaded: {uploaded}")
    print(f"   ❌ Failed: {failed}")
    
    # Cleanup test files
    print("\n5. Cleaning up test files...")
    for file_path in test_files:
        if os.path.exists(file_path):
            os.remove(file_path)
            print(f"   ✓ Removed: {file_path}")
    
    # Final instructions
    print("\n" + "=" * 80)
    print("VERIFICATION STEPS")
    print("=" * 80)
    print(f"\n1. Open the issue in your browser:")
    print(f"   {config['jira_url']}/browse/{test_key}")
    print(f"\n2. Scroll down to the 'Attachments' section")
    print(f"\n3. You should see {uploaded} attachment(s):")
    for f in test_files:
        print(f"   - {f}")
    print(f"\n4. Try clicking on each attachment to verify they open correctly")
    print(f"\n5. If all attachments are visible and openable, the upload is working! ✅")
    print("=" * 80)
    
    return test_key

if __name__ == '__main__':
    test_key = test_attachment_upload()
    
    if test_key:
        print(f"\n✅ Test completed successfully!")
        print(f"Test issue created: {test_key}")
    else:
        print(f"\n❌ Test failed - could not create test issue")
