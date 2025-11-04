#!/usr/bin/env python3
"""
Jira Connection Tester - Diagnose 403 Errors
Tests various authentication methods and provides detailed error information
"""

import requests
from requests.auth import HTTPBasicAuth
import json
import base64

print("=" * 80)
print("JIRA CONNECTION DIAGNOSTIC TOOL")
print("=" * 80)

# Load config
try:
    with open('config.json') as f:
        config = json.load(f)
    
    JIRA_URL = config.get('jira_url', '').rstrip('/')
    JIRA_USERNAME = config.get('jira_username', '')
    JIRA_PASSWORD = config.get('jira_password', '')
    JIRA_PROJECT_KEY = config.get('jira_project_key', '')
    
    print(f"\n✓ Config loaded")
    print(f"  URL: {JIRA_URL}")
    print(f"  Username: {JIRA_USERNAME}")
    print(f"  Project: {JIRA_PROJECT_KEY}")
    print(f"  Password/Token: {'*' * min(len(JIRA_PASSWORD), 20)}...")
except Exception as e:
    print(f"✗ Failed to load config.json: {e}")
    exit(1)

print("\n" + "=" * 80)
print("TEST 1: Basic Server Reachability")
print("=" * 80)

try:
    response = requests.get(f"{JIRA_URL}/status", timeout=10, verify=False)
    print(f"✓ Server is reachable (Status: {response.status_code})")
except Exception as e:
    print(f"✗ Server not reachable: {e}")
    exit(1)

print("\n" + "=" * 80)
print("TEST 2: Authentication Method Detection")
print("=" * 80)

# Check if it's a PAT or password
is_token = len(JIRA_PASSWORD) > 50 or JIRA_PASSWORD.startswith('N')  # Typical token pattern

if is_token:
    print("ℹ Detected: Personal Access Token (PAT)")
    print("  Note: Jira Server/Data Center PATs are different from Cloud API tokens")
else:
    print("ℹ Detected: Regular password")

print("\n" + "=" * 80)
print("TEST 3: Method 1 - HTTP Basic Auth with Username/Password")
print("=" * 80)

try:
    auth = HTTPBasicAuth(JIRA_USERNAME, JIRA_PASSWORD)
    headers = {
        'Content-Type': 'application/json',
        'Accept': 'application/json'
    }
    
    response = requests.get(
        f"{JIRA_URL}/rest/api/2/myself",
        auth=auth,
        headers=headers,
        timeout=10,
        verify=False
    )
    
    if response.status_code == 200:
        user_info = response.json()
        print(f"✓ SUCCESS with Basic Auth")
        print(f"  User: {user_info.get('displayName')}")
        print(f"  Email: {user_info.get('emailAddress')}")
        print(f"  Active: {user_info.get('active')}")
    else:
        print(f"✗ Failed: {response.status_code}")
        print(f"  Response: {response.text[:200]}")
        
except Exception as e:
    print(f"✗ Exception: {e}")

print("\n" + "=" * 80)
print("TEST 4: Method 2 - Bearer Token (for PAT)")
print("=" * 80)

try:
    headers = {
        'Authorization': f'Bearer {JIRA_PASSWORD}',
        'Content-Type': 'application/json',
        'Accept': 'application/json'
    }
    
    response = requests.get(
        f"{JIRA_URL}/rest/api/2/myself",
        headers=headers,
        timeout=10,
        verify=False
    )
    
    if response.status_code == 200:
        user_info = response.json()
        print(f"✓ SUCCESS with Bearer Token")
        print(f"  User: {user_info.get('displayName')}")
        print(f"  Email: {user_info.get('emailAddress')}")
        print(f"  Active: {user_info.get('active')}")
    else:
        print(f"✗ Failed: {response.status_code}")
        print(f"  Response: {response.text[:200]}")
        
except Exception as e:
    print(f"✗ Exception: {e}")

print("\n" + "=" * 80)
print("TEST 5: Check User Permissions")
print("=" * 80)

try:
    auth = HTTPBasicAuth(JIRA_USERNAME, JIRA_PASSWORD)
    headers = {
        'Content-Type': 'application/json',
        'Accept': 'application/json'
    }
    
    # Try to get user permissions
    response = requests.get(
        f"{JIRA_URL}/rest/api/2/mypermissions",
        auth=auth,
        headers=headers,
        timeout=10,
        verify=False
    )
    
    if response.status_code == 200:
        perms = response.json()
        print(f"✓ Retrieved permissions")
        print(f"  Total permissions: {len(perms.get('permissions', {}))}")
        
        # Check specific permissions
        key_perms = ['CREATE_ISSUES', 'EDIT_ISSUES', 'BROWSE']
        print("\n  Key permissions:")
        for perm in key_perms:
            perm_info = perms.get('permissions', {}).get(perm, {})
            has_perm = perm_info.get('havePermission', False)
            print(f"    {perm}: {'✓' if has_perm else '✗'}")
    else:
        print(f"✗ Failed: {response.status_code}")
        print(f"  Response: {response.text[:200]}")
        
except Exception as e:
    print(f"✗ Exception: {e}")

print("\n" + "=" * 80)
print("TEST 6: Check Project Access")
print("=" * 80)

try:
    auth = HTTPBasicAuth(JIRA_USERNAME, JIRA_PASSWORD)
    headers = {
        'Content-Type': 'application/json',
        'Accept': 'application/json'
    }
    
    response = requests.get(
        f"{JIRA_URL}/rest/api/2/project/{JIRA_PROJECT_KEY}",
        auth=auth,
        headers=headers,
        timeout=10,
        verify=False
    )
    
    if response.status_code == 200:
        project = response.json()
        print(f"✓ SUCCESS - Project accessible")
        print(f"  Name: {project.get('name')}")
        print(f"  Key: {project.get('key')}")
        print(f"  ID: {project.get('id')}")
        print(f"  Lead: {project.get('lead', {}).get('displayName')}")
    elif response.status_code == 403:
        print(f"✗ 403 FORBIDDEN - You don't have access to this project")
        print(f"  Response: {response.text[:500]}")
        print(f"\n  Possible causes:")
        print(f"    1. User '{JIRA_USERNAME}' doesn't have permission to browse project '{JIRA_PROJECT_KEY}'")
        print(f"    2. Project doesn't exist")
        print(f"    3. CAPTCHA is enabled (too many failed login attempts)")
        print(f"    4. Account is locked or disabled")
    elif response.status_code == 404:
        print(f"✗ 404 NOT FOUND - Project '{JIRA_PROJECT_KEY}' doesn't exist")
    else:
        print(f"✗ Failed: {response.status_code}")
        print(f"  Response: {response.text[:500]}")
        
except Exception as e:
    print(f"✗ Exception: {e}")

print("\n" + "=" * 80)
print("TEST 7: List All Accessible Projects")
print("=" * 80)

try:
    auth = HTTPBasicAuth(JIRA_USERNAME, JIRA_PASSWORD)
    headers = {
        'Content-Type': 'application/json',
        'Accept': 'application/json'
    }
    
    response = requests.get(
        f"{JIRA_URL}/rest/api/2/project",
        auth=auth,
        headers=headers,
        timeout=10,
        verify=False
    )
    
    if response.status_code == 200:
        projects = response.json()
        print(f"✓ Retrieved {len(projects)} accessible projects:")
        for proj in projects[:10]:  # Show first 10
            print(f"    - {proj.get('key')}: {proj.get('name')}")
        if len(projects) > 10:
            print(f"    ... and {len(projects) - 10} more")
        
        if JIRA_PROJECT_KEY not in [p.get('key') for p in projects]:
            print(f"\n  ⚠ WARNING: Project '{JIRA_PROJECT_KEY}' is NOT in your accessible projects list!")
            print(f"     You need to use one of the projects listed above.")
    else:
        print(f"✗ Failed: {response.status_code}")
        print(f"  Response: {response.text[:200]}")
        
except Exception as e:
    print(f"✗ Exception: {e}")

print("\n" + "=" * 80)
print("TEST 8: Check CAPTCHA Status")
print("=" * 80)

try:
    # CAPTCHA check endpoint
    response = requests.get(
        f"{JIRA_URL}/rest/auth/1/session",
        timeout=10,
        verify=False
    )
    
    if 'CAPTCHA' in response.text or 'captcha' in response.text.lower():
        print(f"⚠ WARNING: CAPTCHA might be enabled")
        print(f"  You may need to log in via browser first to clear CAPTCHA")
    else:
        print(f"✓ No CAPTCHA detected")
        
except Exception as e:
    print(f"ℹ Could not check CAPTCHA status: {e}")

print("\n" + "=" * 80)
print("SUMMARY & RECOMMENDATIONS")
print("=" * 80)

print("""
Common 403 Error Solutions for Jira Server/Data Center:

1. **Using PAT (Personal Access Token)**:
   - Ensure PAT has correct permissions (Browse Projects, Create Issues, etc.)
   - PAT should be generated for the same user in config
   - Try regenerating the PAT
   - In Jira: Profile > Personal Access Tokens > Create Token

2. **Using Password**:
   - Verify password is correct (no special characters causing issues)
   - Check if account is locked or disabled
   - Try logging in via browser first

3. **Project Access**:
   - Verify project key is correct (case-sensitive)
   - User must have "Browse Projects" permission
   - Check project permissions in Jira: Project Settings > Permissions

4. **CAPTCHA**:
   - Too many failed login attempts trigger CAPTCHA
   - Log in via browser to clear CAPTCHA
   - Wait 30+ minutes before retrying

5. **Account Status**:
   - Verify account is active in Jira
   - Check if account has required permissions
   - Admin may need to grant project access

6. **Try This**:
   - Log in to Jira web interface first
   - Navigate to the project in browser
   - Generate a NEW PAT
   - Update config.json with new PAT
   - Try connection test again

For Jira Server/Data Center, you typically need:
- Username (not email for Server)
- Password OR Personal Access Token
- Project browse permission
- Account not locked/disabled
""")

print("=" * 80)
print("END OF DIAGNOSTIC")
print("=" * 80)
