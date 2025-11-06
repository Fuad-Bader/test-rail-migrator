#!/usr/bin/env python3
"""
Interactive project selector for TestRail to Jira/Xray migration
Allows selecting which TestRail project to import and which Jira project to migrate to
"""
import json
import sys
import sqlite3
import requests
from requests.auth import HTTPBasicAuth

def print_header(text):
    """Print a formatted header"""
    print("\n" + "=" * 80)
    print(text)
    print("=" * 80)

def print_section(text):
    """Print a formatted section"""
    print("\n" + "-" * 80)
    print(text)
    print("-" * 80)

def get_testrail_projects(config):
    """Fetch all TestRail projects"""
    from testrail import APIClient
    
    client = APIClient(config['testrail_url'])
    client.user = config['testrail_user']
    client.password = config['testrail_password']
    
    try:
        response = client.send_get('get_projects')
        return response.get('projects', [])
    except Exception as e:
        print(f"❌ Error fetching TestRail projects: {e}")
        return []

def get_jira_projects(config):
    """Fetch all Jira projects"""
    base_url = config['jira_url']
    username = config['jira_username']
    password = config['jira_password']
    
    # Detect if using PAT
    import re
    is_base64_like = bool(re.match(r'^[A-Za-z0-9+/=]+$', password))
    is_token = (len(password) > 30 and is_base64_like) or len(password) > 40
    
    if is_token:
        headers = {
            'Authorization': f'Bearer {password}',
            'Content-Type': 'application/json',
            'Accept': 'application/json'
        }
        auth = None
    else:
        headers = {
            'Content-Type': 'application/json',
            'Accept': 'application/json'
        }
        auth = HTTPBasicAuth(username, password)
    
    try:
        url = f"{base_url}/rest/api/2/project"
        response = requests.get(url, auth=auth, headers=headers)
        response.raise_for_status()
        return response.json()
    except Exception as e:
        print(f"❌ Error fetching Jira projects: {e}")
        return []

def create_jira_project(config):
    """Create a new Jira project"""
    print_section("CREATE NEW JIRA PROJECT")
    
    project_key = input("Enter project key (2-10 uppercase letters, e.g., 'MYPROJ'): ").strip().upper()
    if not project_key or len(project_key) < 2 or len(project_key) > 10:
        print("❌ Invalid project key. Must be 2-10 uppercase letters.")
        return None
    
    project_name = input("Enter project name: ").strip()
    if not project_name:
        print("❌ Project name cannot be empty.")
        return None
    
    description = input("Enter project description (optional): ").strip()
    
    # Ask for project template
    print("\nProject Templates:")
    print("  Standard Jira Templates:")
    print("    1. Scrum software development")
    print("    2. Kanban software development")
    print("    3. Basic software development")
    print("\n  Xray Test Management Templates:")
    print("    4. Xray Test Management (Scrum)")
    print("    5. Xray Test Management (Kanban)")
    print("    6. Xray Test Management (Classic)")
    
    template_choice = input("Select template (1-6) [default: 4]: ").strip() or "4"
    
    template_map = {
        # Standard Jira templates
        "1": "com.pyxis.greenhopper.jira:gh-simplified-scrum",
        "2": "com.pyxis.greenhopper.jira:gh-simplified-kanban",
        "3": "com.atlassian.jira-core-project-templates:jira-core-simplified-project-management",
        # Xray templates - these use the same base templates but with Xray issue types
        "4": "com.pyxis.greenhopper.jira:gh-simplified-scrum",  # Scrum with Xray
        "5": "com.pyxis.greenhopper.jira:gh-simplified-kanban", # Kanban with Xray
        "6": "com.atlassian.jira-core-project-templates:jira-core-simplified-project-management"  # Classic with Xray
    }
    
    template_key = template_map.get(template_choice, template_map["4"])
    use_xray = template_choice in ["4", "5", "6"]
    
    base_url = config['jira_url']
    username = config['jira_username']
    password = config['jira_password']
    
    # Detect if using PAT
    import re
    is_base64_like = bool(re.match(r'^[A-Za-z0-9+/=]+$', password))
    is_token = (len(password) > 30 and is_base64_like) or len(password) > 40
    
    if is_token:
        headers = {
            'Authorization': f'Bearer {password}',
            'Content-Type': 'application/json',
            'Accept': 'application/json'
        }
        auth = None
    else:
        headers = {
            'Content-Type': 'application/json',
            'Accept': 'application/json'
        }
        auth = HTTPBasicAuth(username, password)
    
    try:
        print(f"\nCreating project '{project_name}' ({project_key})...")
        
        # Get current user's account ID
        user_url = f"{base_url}/rest/api/3/myself"
        user_response = requests.get(user_url, auth=auth, headers=headers)
        user_response.raise_for_status()
        account_id = user_response.json().get('accountId')
        
        if not account_id:
            print(f"❌ Error: Could not retrieve user account ID")
            return None
        
        project_data = {
            'key': project_key,
            'name': project_name,
            'projectTypeKey': 'software',
            'projectTemplateKey': template_key,
            'leadAccountId': account_id
        }
        
        # Add description only if provided (avoid empty string)
        if description:
            project_data['description'] = description
        
        url = f"{base_url}/rest/api/2/project"
        response = requests.post(url, auth=auth, headers=headers, json=project_data)
        response.raise_for_status()
        
        project = response.json()
        print(f"✓ Project created successfully!")
        print(f"  Key: {project['key']}")
        print(f"  Name: {project.get('name', project_name)}")
        
        # If Xray template selected, add Xray issue types
        if use_xray:
            print(f"\n⚙ Configuring Xray Test Management...")
            try:
                # Add Xray issue types to the project
                xray_issue_types = ['Test', 'Test Set', 'Test Execution', 'Test Plan', 'Precondition']
                
                # Note: Xray issue types are typically added automatically when Xray is installed
                # This is just a note for the user
                print(f"  ℹ Xray issue types (Test, Test Set, Test Execution, etc.) should be")
                print(f"    available if Xray plugin is installed in your Jira instance.")
                print(f"  ℹ Please verify Xray issue types are available in Project Settings.")
                
            except Exception as e:
                print(f"  ⚠ Note: Could not verify Xray configuration: {e}")
                print(f"    Please manually verify Xray issue types are available.")
        
        return {
            'key': project['key'],
            'name': project.get('name', project_name),
            'id': project.get('id')
        }
    except requests.exceptions.HTTPError as e:
        print(f"❌ Error creating project: {e}")
        if hasattr(e, 'response') and e.response.text:
            print(f"   Response: {e.response.text[:500]}")
        return None
    except Exception as e:
        print(f"❌ Error: {e}")
        return None

def select_testrail_project(projects):
    """Interactive selection of TestRail project"""
    print_section("SELECT TESTRAIL PROJECT TO IMPORT")
    
    if not projects:
        print("❌ No projects found in TestRail!")
        return None
    
    print("\nAvailable TestRail Projects:\n")
    for idx, project in enumerate(projects, 1):
        status = "✓ Active" if not project.get('is_completed') else "✗ Completed"
        print(f"  {idx}. {project['name']} (ID: {project['id']}) - {status}")
    
    while True:
        try:
            choice = input(f"\nSelect project (1-{len(projects)}): ").strip()
            if not choice:
                return None
            
            idx = int(choice) - 1
            if 0 <= idx < len(projects):
                selected = projects[idx]
                print(f"\n✓ Selected: {selected['name']}")
                return selected
            else:
                print(f"❌ Please enter a number between 1 and {len(projects)}")
        except ValueError:
            print("❌ Please enter a valid number")
        except KeyboardInterrupt:
            print("\n\n❌ Selection cancelled")
            return None

def select_jira_project(projects):
    """Interactive selection of Jira project"""
    print_section("SELECT TARGET JIRA PROJECT")
    
    if not projects:
        print("⚠ No existing Jira projects found")
        create = input("\nWould you like to create a new project? (y/n): ").strip().lower()
        return 'CREATE' if create == 'y' else None
    
    print("\nAvailable Jira Projects:\n")
    for idx, project in enumerate(projects, 1):
        print(f"  {idx}. {project['name']} ({project['key']})")
    
    print(f"  {len(projects) + 1}. Create new project")
    
    while True:
        try:
            choice = input(f"\nSelect project (1-{len(projects) + 1}): ").strip()
            if not choice:
                return None
            
            idx = int(choice) - 1
            
            if idx == len(projects):
                return 'CREATE'
            elif 0 <= idx < len(projects):
                selected = projects[idx]
                print(f"\n✓ Selected: {selected['name']} ({selected['key']})")
                return selected
            else:
                print(f"❌ Please enter a number between 1 and {len(projects) + 1}")
        except ValueError:
            print("❌ Please enter a valid number")
        except KeyboardInterrupt:
            print("\n\n❌ Selection cancelled")
            return None

def save_migration_config(testrail_project, jira_project):
    """Save the selected projects to a migration config file"""
    config_data = {
        'testrail_project_id': testrail_project['id'],
        'testrail_project_name': testrail_project['name'],
        'jira_project_key': jira_project['key'],
        'jira_project_name': jira_project.get('name', jira_project['key'])
    }
    
    with open('migration_config.json', 'w') as f:
        json.dump(config_data, f, indent=2)
    
    print(f"\n✓ Migration configuration saved to 'migration_config.json'")
    return config_data

def main():
    """Main interactive project selection"""
    print_header("TESTRAIL TO JIRA/XRAY MIGRATION - PROJECT SELECTION")
    
    # Load config
    try:
        with open('config.json', 'r') as f:
            config = json.load(f)
    except FileNotFoundError:
        print("❌ Error: config.json not found!")
        print("   Please create a config.json file with your TestRail and Jira credentials.")
        sys.exit(1)
    
    # Step 1: Select TestRail project
    print("\n📋 Step 1: Select TestRail project to import")
    testrail_projects = get_testrail_projects(config)
    
    if not testrail_projects:
        print("❌ Could not fetch TestRail projects. Please check your configuration.")
        sys.exit(1)
    
    testrail_project = select_testrail_project(testrail_projects)
    if not testrail_project:
        print("\n❌ No TestRail project selected. Exiting.")
        sys.exit(0)
    
    # Step 2: Select or create Jira project
    print("\n📋 Step 2: Select target Jira project")
    jira_projects = get_jira_projects(config)
    
    jira_project_selection = select_jira_project(jira_projects)
    
    if not jira_project_selection:
        print("\n❌ No Jira project selected. Exiting.")
        sys.exit(0)
    
    if jira_project_selection == 'CREATE':
        jira_project = create_jira_project(config)
        if not jira_project:
            print("\n❌ Failed to create Jira project. Exiting.")
            sys.exit(1)
    else:
        jira_project = jira_project_selection
    
    # Step 3: Save configuration
    print_header("MIGRATION CONFIGURATION")
    print(f"\nTestRail Project: {testrail_project['name']} (ID: {testrail_project['id']})")
    print(f"Jira Project:     {jira_project['name']} ({jira_project['key']})")
    
    confirm = input("\nProceed with this configuration? (y/n): ").strip().lower()
    if confirm != 'y':
        print("\n❌ Migration cancelled.")
        sys.exit(0)
    
    # Save configuration
    save_migration_config(testrail_project, jira_project)
    
    print_header("NEXT STEPS")
    print("\n1. Run the importer with the selected TestRail project:")
    print("   python3 importer.py")
    print("\n2. Run the migrator to migrate to the selected Jira project:")
    print("   python3 migrator.py")
    print("\n" + "=" * 80 + "\n")

if __name__ == '__main__':
    try:
        main()
    except KeyboardInterrupt:
        print("\n\n❌ Process interrupted by user.")
        sys.exit(1)
