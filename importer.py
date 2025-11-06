from testrail import *
from sqlite3 import *
import json
import sys
import base64
import os
import traceback
import requests

# Helper function to print with immediate flush
def print_flush(*args, **kwargs):
    print(*args, **kwargs)
    sys.stdout.flush()

with open('config.json') as config_file:
    config = json.load(config_file)

# Load migration configuration
migration_config = None
SELECTED_PROJECT_ID = None

try:
    with open('migration_config.json') as mig_file:
        migration_config = json.load(mig_file)
        SELECTED_PROJECT_ID = migration_config.get('testrail_project_id')
        print_flush("=" * 80)
        print_flush(f"IMPORTING SELECTED PROJECT: {migration_config.get('testrail_project_name')}")
        print_flush(f"Project ID: {SELECTED_PROJECT_ID}")
        print_flush("=" * 80)
except FileNotFoundError:
    print_flush("=" * 80)
    print_flush("⚠ WARNING: migration_config.json not found!")
    print_flush("Please run 'python3 project_selector.py' first to select projects.")
    print_flush("=" * 80)
    sys.exit(1)

db = connect('testrail.db')
cursor = db.cursor()

client = APIClient(config['testrail_url'])
client.user = config['testrail_user']
client.password = config['testrail_password']

print_flush("\n" + "=" * 80)
print_flush("FETCHING AND STORING TESTRAIL DATA")
print_flush("=" * 80)

# 1. PROJECTS - Only import the selected project
print_flush("\n[1/15] Fetching Selected Project...")
cursor.execute('''CREATE TABLE IF NOT EXISTS projects (
    id INTEGER NOT NULL PRIMARY KEY,
    name TEXT,
    announcement TEXT,
    show_announcement TEXT,
    is_completed TEXT,
    suite_mode TEXT,
    default_role_id TEXT,
    case_statuses_enabled TEXT,
    url TEXT,
    users TEXT, 
    groups TEXT
)''')

project = client.send_get(f'get_project/{SELECTED_PROJECT_ID}')
cursor.execute('INSERT OR REPLACE INTO projects (id, name, announcement, show_announcement, is_completed, suite_mode, default_role_id, case_statuses_enabled, url, users, groups) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)',
               (
                   project['id'], 
                   project['name'], 
                   project['announcement'], 
                   project['show_announcement'], 
                   project['is_completed'], 
                   project['suite_mode'], 
                   project['default_role_id'], 
                   project['case_statuses_enabled'], 
                   project['url'],
                   str(project['users']),
                   str(project['groups'])
                ))
db.commit()
print(f"✓ Stored project: {project['name']}")

# 2. USERS
print("\n[2/15] Fetching Users...")
cursor.execute('''CREATE TABLE IF NOT EXISTS users (
    id INTEGER NOT NULL PRIMARY KEY,
    name TEXT,
    email TEXT,
    is_active INTEGER,
    role_id INTEGER,
    role TEXT
)''')
users = client.send_get('get_users')['users']
for user in users:
    cursor.execute('INSERT OR REPLACE INTO users (id, name, email, is_active, role_id, role) VALUES (?, ?, ?, ?, ?, ?)',
                   (user['id'], user['name'], user['email'], user['is_active'], user.get('role_id'), user.get('role')))
db.commit()
print(f"✓ Stored {len(users)} users")

# 3. CASE TYPES
print("\n[3/15] Fetching Case Types...")
cursor.execute('''CREATE TABLE IF NOT EXISTS case_types (
    id INTEGER NOT NULL PRIMARY KEY,
    name TEXT,
    is_default INTEGER
)''')
case_types = client.send_get('get_case_types')
for case_type in case_types:
    cursor.execute('INSERT OR REPLACE INTO case_types (id, name, is_default) VALUES (?, ?, ?)',
                   (case_type['id'], case_type['name'], case_type['is_default']))
db.commit()
print(f"✓ Stored {len(case_types)} case types")

# 4. CASE FIELDS
print("\n[4/15] Fetching Case Fields...")
cursor.execute('''CREATE TABLE IF NOT EXISTS case_fields (
    id INTEGER NOT NULL PRIMARY KEY,
    type_id INTEGER,
    name TEXT,
    system_name TEXT,
    label TEXT,
    description TEXT,
    is_active INTEGER,
    configs TEXT
)''')
case_fields = client.send_get('get_case_fields')
for field in case_fields:
    cursor.execute('INSERT OR REPLACE INTO case_fields (id, type_id, name, system_name, label, description, is_active, configs) VALUES (?, ?, ?, ?, ?, ?, ?, ?)',
                   (field['id'], field['type_id'], field['name'], field['system_name'], field['label'], 
                    field.get('description'), field['is_active'], str(field.get('configs'))))
db.commit()
print(f"✓ Stored {len(case_fields)} case fields")

# 5. PRIORITIES
print("\n[5/15] Fetching Priorities...")
cursor.execute('''CREATE TABLE IF NOT EXISTS priorities (
    id INTEGER NOT NULL PRIMARY KEY,
    name TEXT,
    short_name TEXT,
    is_default INTEGER,
    priority INTEGER
)''')
priorities = client.send_get('get_priorities')
for priority in priorities:
    cursor.execute('INSERT OR REPLACE INTO priorities (id, name, short_name, is_default, priority) VALUES (?, ?, ?, ?, ?)',
                   (priority['id'], priority['name'], priority['short_name'], priority['is_default'], priority['priority']))
db.commit()
print(f"✓ Stored {len(priorities)} priorities")

# 6. RESULT FIELDS
print("\n[6/15] Fetching Result Fields...")
cursor.execute('''CREATE TABLE IF NOT EXISTS result_fields (
    id INTEGER NOT NULL PRIMARY KEY,
    type_id INTEGER,
    name TEXT,
    system_name TEXT,
    label TEXT,
    description TEXT,
    is_active INTEGER,
    configs TEXT
)''')
result_fields = client.send_get('get_result_fields')
for field in result_fields:
    cursor.execute('INSERT OR REPLACE INTO result_fields (id, type_id, name, system_name, label, description, is_active, configs) VALUES (?, ?, ?, ?, ?, ?, ?, ?)',
                   (field['id'], field['type_id'], field['name'], field['system_name'], field['label'], 
                    field.get('description'), field['is_active'], str(field.get('configs'))))
db.commit()
print(f"✓ Stored {len(result_fields)} result fields")

# 7. STATUSES
print("\n[7/15] Fetching Statuses...")
cursor.execute('''CREATE TABLE IF NOT EXISTS statuses (
    id INTEGER NOT NULL PRIMARY KEY,
    name TEXT,
    label TEXT,
    color_dark INTEGER,
    color_medium INTEGER,
    color_bright INTEGER,
    is_system INTEGER,
    is_untested INTEGER,
    is_final INTEGER
)''')
statuses = client.send_get('get_statuses')
for status in statuses:
    cursor.execute('INSERT OR REPLACE INTO statuses (id, name, label, color_dark, color_medium, color_bright, is_system, is_untested, is_final) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)',
                   (status['id'], status['name'], status['label'], status['color_dark'], status['color_medium'], 
                    status['color_bright'], status['is_system'], status['is_untested'], status['is_final']))
db.commit()
print(f"✓ Stored {len(statuses)} statuses")

# 8. TEMPLATES
print("\n[8/15] Fetching Templates...")
cursor.execute('''CREATE TABLE IF NOT EXISTS templates (
    id INTEGER NOT NULL PRIMARY KEY,
    project_id INTEGER,
    name TEXT,
    is_default INTEGER
)''')
try:
    templates = client.send_get(f'get_templates/{SELECTED_PROJECT_ID}')
    for template in templates:
        cursor.execute('INSERT OR REPLACE INTO templates (id, project_id, name, is_default) VALUES (?, ?, ?, ?)',
                       (template['id'], SELECTED_PROJECT_ID, template['name'], template['is_default']))
    db.commit()
    print(f"✓ Stored {len(templates)} templates")
except Exception as e:
    print(f"  Warning: Could not fetch templates for project {SELECTED_PROJECT_ID}: {e}")
    print(f"✓ Stored templates")

# 9. SUITES
print("\n[9/15] Fetching Suites...")
cursor.execute('''CREATE TABLE IF NOT EXISTS suites (
    id INTEGER NOT NULL PRIMARY KEY,
    project_id INTEGER,
    name TEXT,
    description TEXT,
    url TEXT,
    is_master INTEGER,
    is_baseline INTEGER,
    is_completed INTEGER,
    completed_on INTEGER
)''')
suite_count = 0
try:
    suites = client.send_get(f'get_suites/{SELECTED_PROJECT_ID}')['suites']
    for suite in suites:
        cursor.execute('INSERT OR REPLACE INTO suites (id, project_id, name, description, url, is_master, is_baseline, is_completed, completed_on) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)',
                       (suite['id'], suite['project_id'], suite['name'], suite.get('description'), suite['url'], 
                        suite['is_master'], suite['is_baseline'], suite['is_completed'], suite.get('completed_on')))
        suite_count += 1
    db.commit()
except Exception as e:
    print(f"  Warning: Could not fetch suites for project {SELECTED_PROJECT_ID}: {e}")
print(f"✓ Stored {suite_count} suites")

# 10. SECTIONS
print("\n[10/15] Fetching Sections...")
cursor.execute('''CREATE TABLE IF NOT EXISTS sections (
    id INTEGER NOT NULL PRIMARY KEY,
    suite_id INTEGER,
    name TEXT,
    description TEXT,
    parent_id INTEGER,
    display_order INTEGER,
    depth INTEGER
)''')
section_count = 0
try:
    suites = client.send_get(f'get_suites/{SELECTED_PROJECT_ID}')['suites']
    for suite in suites:
        try:
            sections = client.send_get(f'get_sections/{SELECTED_PROJECT_ID}&suite_id={suite["id"]}')['sections']
            for section in sections:
                cursor.execute('INSERT OR REPLACE INTO sections (id, suite_id, name, description, parent_id, display_order, depth) VALUES (?, ?, ?, ?, ?, ?, ?)',
                               (section['id'], section['suite_id'], section['name'], section.get('description'), 
                                section.get('parent_id'), section['display_order'], section['depth']))
                section_count += 1
            db.commit()
        except Exception as e:
            print(f"  Warning: Could not fetch sections for suite {suite['id']}: {e}")
except:
    pass
print(f"✓ Stored {section_count} sections")

# 11. MILESTONES
print("\n[11/15] Fetching Milestones...")
cursor.execute('''CREATE TABLE IF NOT EXISTS milestones (
    id INTEGER NOT NULL PRIMARY KEY,
    project_id INTEGER,
    name TEXT,
    description TEXT,
    start_on INTEGER,
    started_on INTEGER,
    is_started INTEGER,
    due_on INTEGER,
    is_completed INTEGER,
    completed_on INTEGER,
    parent_id INTEGER,
    url TEXT
)''')
milestone_count = 0
try:
    milestones = client.send_get(f'get_milestones/{SELECTED_PROJECT_ID}')['milestones']
    for milestone in milestones:
        cursor.execute('INSERT OR REPLACE INTO milestones (id, project_id, name, description, start_on, started_on, is_started, due_on, is_completed, completed_on, parent_id, url) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)',
                       (milestone['id'], milestone['project_id'], milestone['name'], milestone.get('description'), 
                        milestone.get('start_on'), milestone.get('started_on'), milestone['is_started'], 
                        milestone.get('due_on'), milestone['is_completed'], milestone.get('completed_on'), 
                        milestone.get('parent_id'), milestone['url']))
        milestone_count += 1
    db.commit()
except Exception as e:
    print(f"  Warning: Could not fetch milestones for project {SELECTED_PROJECT_ID}: {e}")
print(f"✓ Stored {milestone_count} milestones")

# 12. CASES (Test Cases)
print("\n[12/15] Fetching Cases...")
cursor.execute('''CREATE TABLE IF NOT EXISTS cases (
    id INTEGER NOT NULL PRIMARY KEY,
    title TEXT,
    section_id INTEGER,
    template_id INTEGER,
    type_id INTEGER,
    priority_id INTEGER,
    milestone_id INTEGER,
    refs TEXT,
    created_by INTEGER,
    created_on INTEGER,
    updated_by INTEGER,
    updated_on INTEGER,
    estimate TEXT,
    estimate_forecast TEXT,
    suite_id INTEGER,
    custom_fields TEXT
)''')
case_count = 0
try:
    suites = client.send_get(f'get_suites/{SELECTED_PROJECT_ID}')['suites']
    for suite in suites:
        try:
            cases = client.send_get(f'get_cases/{SELECTED_PROJECT_ID}&suite_id={suite["id"]}')['cases']
            for case in cases:
                # Extract custom fields
                custom_fields = {k: v for k, v in case.items() if k.startswith('custom_')}
                cursor.execute('INSERT OR REPLACE INTO cases (id, title, section_id, template_id, type_id, priority_id, milestone_id, refs, created_by, created_on, updated_by, updated_on, estimate, estimate_forecast, suite_id, custom_fields) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)',
                               (case['id'], case['title'], case['section_id'], case['template_id'], 
                                case['type_id'], case['priority_id'], case.get('milestone_id'), case.get('refs'), 
                                case['created_by'], case['created_on'], case['updated_by'], case['updated_on'], 
                                case.get('estimate'), case.get('estimate_forecast'), case['suite_id'], 
                                str(custom_fields)))
                case_count += 1
            db.commit()
        except Exception as e:
            print(f"  Warning: Could not fetch cases for suite {suite['id']}: {e}")
except:
    pass
print(f"✓ Stored {case_count} cases")

# 13. PLANS
print("\n[13/15] Fetching Plans...")
cursor.execute('''CREATE TABLE IF NOT EXISTS plans (
    id INTEGER NOT NULL PRIMARY KEY,
    project_id INTEGER,
    name TEXT,
    description TEXT,
    milestone_id INTEGER,
    assignedto_id INTEGER,
    is_completed INTEGER,
    completed_on INTEGER,
    created_by INTEGER,
    created_on INTEGER,
    url TEXT,
    entries TEXT
)''')
plan_count = 0
try:
    plans = client.send_get(f'get_plans/{SELECTED_PROJECT_ID}')['plans']
    for plan in plans:
        plan_details = client.send_get(f'get_plan/{plan["id"]}')
        cursor.execute('INSERT OR REPLACE INTO plans (id, project_id, name, description, milestone_id, assignedto_id, is_completed, completed_on, created_by, created_on, url, entries) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)',
                       (plan_details['id'], plan_details['project_id'], plan_details['name'], 
                        plan_details.get('description'), plan_details.get('milestone_id'), 
                        plan_details.get('assignedto_id'), plan_details['is_completed'], 
                        plan_details.get('completed_on'), plan_details['created_by'], 
                        plan_details['created_on'], plan_details['url'], str(plan_details.get('entries'))))
        plan_count += 1
    db.commit()
except Exception as e:
    print(f"  Warning: Could not fetch plans for project {SELECTED_PROJECT_ID}: {e}")
print(f"✓ Stored {plan_count} plans")

# 14. RUNS
print("\n[14/15] Fetching Runs...")
cursor.execute('''CREATE TABLE IF NOT EXISTS runs (
    id INTEGER NOT NULL PRIMARY KEY,
    suite_id INTEGER,
    project_id INTEGER,
    plan_id INTEGER,
    name TEXT,
    description TEXT,
    milestone_id INTEGER,
    assignedto_id INTEGER,
    include_all INTEGER,
    is_completed INTEGER,
    completed_on INTEGER,
    config TEXT,
    config_ids TEXT,
    passed_count INTEGER,
    blocked_count INTEGER,
    untested_count INTEGER,
    retest_count INTEGER,
    failed_count INTEGER,
    custom_status1_count INTEGER,
    custom_status2_count INTEGER,
    custom_status3_count INTEGER,
    custom_status4_count INTEGER,
    custom_status5_count INTEGER,
    custom_status6_count INTEGER,
    custom_status7_count INTEGER,
    created_by INTEGER,
    created_on INTEGER,
    url TEXT
)''')
run_count = 0
try:
    runs = client.send_get(f'get_runs/{SELECTED_PROJECT_ID}')['runs']
    for run in runs:
        cursor.execute('INSERT OR REPLACE INTO runs (id, suite_id, project_id, plan_id, name, description, milestone_id, assignedto_id, include_all, is_completed, completed_on, config, config_ids, passed_count, blocked_count, untested_count, retest_count, failed_count, custom_status1_count, custom_status2_count, custom_status3_count, custom_status4_count, custom_status5_count, custom_status6_count, custom_status7_count, created_by, created_on, url) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)',
                       (run['id'], run.get('suite_id'), run['project_id'], run.get('plan_id'), run['name'], 
                        run.get('description'), run.get('milestone_id'), run.get('assignedto_id'), 
                        run['include_all'], run['is_completed'], run.get('completed_on'), run.get('config'), 
                        str(run.get('config_ids')), run['passed_count'], run['blocked_count'], 
                        run['untested_count'], run['retest_count'], run['failed_count'], 
                        run.get('custom_status1_count'), run.get('custom_status2_count'), 
                        run.get('custom_status3_count'), run.get('custom_status4_count'), 
                        run.get('custom_status5_count'), run.get('custom_status6_count'), 
                        run.get('custom_status7_count'), run['created_by'], run['created_on'], run['url']))
        run_count += 1
    db.commit()
except Exception as e:
    print(f"  Warning: Could not fetch runs for project {SELECTED_PROJECT_ID}: {e}")
print(f"✓ Stored {run_count} runs")

# 15. TESTS
print("\n[15/15] Fetching Tests...")
cursor.execute('''CREATE TABLE IF NOT EXISTS tests (
    id INTEGER NOT NULL PRIMARY KEY,
    case_id INTEGER,
    run_id INTEGER,
    status_id INTEGER,
    assignedto_id INTEGER,
    priority_id INTEGER,
    type_id INTEGER,
    milestone_id INTEGER,
    refs TEXT,
    title TEXT,
    template_id INTEGER,
    estimate TEXT,
    estimate_forecast TEXT,
    custom_fields TEXT
)''')
test_count = 0
try:
    runs = client.send_get(f'get_runs/{SELECTED_PROJECT_ID}')['runs']
    for run in runs:
        try:
            tests = client.send_get(f'get_tests/{run["id"]}')['tests']
            for test in tests:
                custom_fields = {k: v for k, v in test.items() if k.startswith('custom_')}
                cursor.execute('INSERT OR REPLACE INTO tests (id, case_id, run_id, status_id, assignedto_id, priority_id, type_id, milestone_id, refs, title, template_id, estimate, estimate_forecast, custom_fields) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)',
                               (test['id'], test['case_id'], test['run_id'], test['status_id'], 
                                test.get('assignedto_id'), test['priority_id'], test['type_id'], 
                                test.get('milestone_id'), test.get('refs'), test['title'], 
                                test['template_id'], test.get('estimate'), test.get('estimate_forecast'), 
                                str(custom_fields)))    
                test_count += 1
            db.commit()
        except Exception as e:
            print(f"  Warning: Could not fetch tests for run {run['id']}: {e}")
except:
    pass
print(f"✓ Stored {test_count} tests")


print("\nFetching Results (this may take a while)...")
cursor.execute('''CREATE TABLE IF NOT EXISTS results (
    id INTEGER NOT NULL PRIMARY KEY,
    test_id INTEGER,
    status_id INTEGER,
    created_by INTEGER,
    created_on INTEGER,
    assignedto_id INTEGER,
    comment TEXT,
    version TEXT,
    elapsed TEXT,
    defects TEXT,
    custom_fields TEXT
)''')
result_count = 0
try:
    runs = client.send_get(f'get_runs/{SELECTED_PROJECT_ID}')['runs']
    for run in runs:
        try:
            tests = client.send_get(f'get_tests/{run["id"]}')['tests']
            for test in tests:
                try:
                    results = client.send_get(f'get_results/{test["id"]}')['results']
                    for result in results:
                        custom_fields = {k: v for k, v in result.items() if k.startswith('custom_')}
                        cursor.execute('INSERT OR REPLACE INTO results (id, test_id, status_id, created_by, created_on, assignedto_id, comment, version, elapsed, defects, custom_fields) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)',
                                       (result['id'], result['test_id'], result['status_id'], 
                                        result['created_by'], result['created_on'], result.get('assignedto_id'), 
                                        result.get('comment'), result.get('version'), result.get('elapsed'), 
                                        result.get('defects'), str(custom_fields)))
                        result_count += 1
                    db.commit()
                except Exception as e:
                    pass  # Skip individual test results that fail
        except:
            pass
except:
    pass
print(f"✓ Stored {result_count} results")

# 15. ATTACHMENTS
print("\n[15/15] Fetching Attachments...")
cursor.execute('''CREATE TABLE IF NOT EXISTS attachments (
    id INTEGER NOT NULL PRIMARY KEY,
    entity_type TEXT,
    entity_id INTEGER,
    filename TEXT,
    size INTEGER,
    created_on INTEGER,
    user_id INTEGER,
    url TEXT,
    local_path TEXT,
    UNIQUE(id, entity_type, entity_id)
)''')

# Create attachments directory
attachments_dir = 'attachments'
os.makedirs(attachments_dir, exist_ok=True)

attachment_count = 0

# Get attachments for test cases
print("  Fetching case attachments...")
try:
    suites_response = client.send_get(f'get_suites/{SELECTED_PROJECT_ID}')
    if suites_response:
        suites = suites_response if isinstance(suites_response, list) else suites_response.get('suites', [])
        
        for suite in suites:
            try:
                cases_response = client.send_get(f'get_cases/{SELECTED_PROJECT_ID}&suite_id={suite["id"]}')
                if not cases_response:
                    continue
                cases = cases_response if isinstance(cases_response, list) else cases_response.get('cases', [])
                
                for case in cases:
                    try:
                        attachments = client.send_get(f'get_attachments_for_case/{case["id"]}')
                        if attachments and 'attachments' in attachments:
                            for attachment in attachments['attachments']:
                                # Download attachment
                                attachment_url = f"{config['testrail_url']}index.php?/attachments/get/{attachment['id']}"
                                local_filename = f"{attachments_dir}/case_{case['id']}_{attachment['filename']}"
                                
                                try:
                                    # Check if already exists to avoid duplicates
                                    cursor.execute('SELECT id FROM attachments WHERE id = ? AND entity_type = ? AND entity_id = ?',
                                                   (attachment['id'], 'case', case['id']))
                                    if cursor.fetchone():
                                        print(f"    Skipping duplicate: {attachment['filename']}")
                                        continue
                                    
                                    # Download file using TestRail API
                                    # The get_attachment endpoint takes a filepath and saves directly to it
                                    # It returns the filepath on success or error message on failure
                                    result = client.send_get(f"get_attachment/{attachment['id']}", local_filename)
                                    
                                    # Verify file was written successfully
                                    if result == local_filename and os.path.exists(local_filename) and os.path.getsize(local_filename) > 0:
                                        # Store in database
                                        cursor.execute(
                                            'INSERT OR REPLACE INTO attachments (id, entity_type, entity_id, filename, size, created_on, user_id, url, local_path) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)',
                                            (attachment['id'], 'case', case['id'], attachment['filename'], 
                                             attachment.get('size'), attachment.get('created_on'), 
                                             attachment.get('user_id'), attachment_url, local_filename)
                                        )
                                        attachment_count += 1
                                        
                                        if attachment_count % 10 == 0:
                                            print(f"    Downloaded {attachment_count} attachments...")
                                            db.commit()
                                    else:
                                        print(f"    Warning: Failed to download file: {attachment['filename']} - {result}")
                                        
                                except Exception as e:
                                    print(f"    Warning: Could not download attachment {attachment['id']}: {e}")
                                    traceback.print_exc()
                                    
                    except:
                        pass
            except:
                pass
except Exception as e:
    print(f"  Warning: Could not fetch case attachments: {e}")

# Get attachments for test results
print("  Fetching result attachments...")
result_attachment_count = 0
try:
    runs = client.send_get(f'get_runs/{SELECTED_PROJECT_ID}')['runs']
    print(f"  Checking {len(runs)} runs for result attachments...")
    for run_idx, run in enumerate(runs, 1):
        try:
            print(f"  Processing run {run_idx}/{len(runs)}: {run['name']} (ID: {run['id']})")
            tests_response = client.send_get(f'get_tests/{run["id"]}')
            if not tests_response:
                continue
            tests = tests_response if isinstance(tests_response, list) else tests_response.get('tests', [])
            
            for test in tests:
                try:
                    results_response = client.send_get(f'get_results/{test["id"]}')
                    if not results_response:
                        continue
                    results = results_response if isinstance(results_response, list) else results_response.get('results', [])
                    
                    for result in results:
                        try:
                            # Get attachments for this test (they're associated with results through the test)
                            attachments = client.send_get(f'get_attachments_for_test/{test["id"]}')
                            if attachments and 'attachments' in attachments:
                                for attachment in attachments['attachments']:
                                    try:
                                        # Check if attachment belongs to this specific result
                                        # Attachments for results show up under the test's attachments
                                        # We store them associated with the result
                                        
                                        # Check if already exists to avoid duplicates
                                        cursor.execute('SELECT id FROM attachments WHERE id = ? AND entity_type = ? AND entity_id = ?',
                                                       (attachment['id'], 'result', result['id']))
                                        if cursor.fetchone():
                                            continue
                                        
                                        # Download attachment
                                        attachment_url = f"{config['testrail_url']}index.php?/attachments/get/{attachment['id']}"
                                        local_filename = f"{attachments_dir}/result_{result['id']}_{attachment['filename']}"
                                        
                                        print(f"    Downloading result attachment: {attachment['filename']} (ID: {attachment['id']}) for result {result['id']}")
                                        
                                        # Download file using TestRail API
                                        # The get_attachment endpoint takes a filepath and saves directly to it
                                        # It returns the filepath on success or error message on failure
                                        result_path = client.send_get(f"get_attachment/{attachment['id']}", local_filename)
                                        
                                        # Verify file was written successfully
                                        if result_path == local_filename and os.path.exists(local_filename) and os.path.getsize(local_filename) > 0:
                                            print(f"    ✓ Successfully downloaded: {attachment['filename']} ({os.path.getsize(local_filename)} bytes)")
                                            # Store in database
                                            cursor.execute(
                                                'INSERT OR REPLACE INTO attachments (id, entity_type, entity_id, filename, size, created_on, user_id, url, local_path) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)',
                                                (attachment['id'], 'result', result['id'], attachment['filename'], 
                                                 attachment.get('size'), attachment.get('created_on'), 
                                                 attachment.get('user_id'), attachment_url, local_filename)
                                            )
                                            attachment_count += 1
                                            result_attachment_count += 1
                                            
                                            if attachment_count % 10 == 0:
                                                print(f"    Downloaded {attachment_count} attachments total ({result_attachment_count} from results)...")
                                                db.commit()
                                        else:
                                            print(f"    ❌ Failed to download: {attachment['filename']}")
                                            print(f"       Expected path: {local_filename}")
                                            print(f"       API returned: {result_path}")
                                            print(f"       File exists: {os.path.exists(local_filename)}")
                                            if os.path.exists(local_filename):
                                                print(f"       File size: {os.path.getsize(local_filename)} bytes")
                                            
                                    except Exception as e:
                                        print(f"    ❌ Error downloading attachment {attachment['id']} ({attachment['filename']}): {e}")
                                        traceback.print_exc()
                        except Exception as e:
                            print(f"    Warning: Error getting attachments for test {test.get('id', 'unknown')}: {e}")
                except:
                    pass
        except:
            pass
except Exception as e:
    print(f"  Warning: Could not fetch result attachments: {e}")
    traceback.print_exc()

db.commit()
print(f"✓ Stored and downloaded {attachment_count} attachments total")
print(f"  - From test cases: {attachment_count - result_attachment_count}")
print(f"  - From test results: {result_attachment_count}")

print("\n" + "=" * 80)
print("IMPORT COMPLETE!")
print("=" * 80)
print(f"\nDatabase saved to: testrail.db")
print(f"Attachments saved to: {attachments_dir}/")
print("\nSummary:")
print(f"  - Project: {migration_config.get('testrail_project_name')} (ID: {SELECTED_PROJECT_ID})")
print(f"  - Target Jira Project: {migration_config.get('jira_project_name')} ({migration_config.get('jira_project_key')})")
print(f"  - Users: {len(users)}")
print(f"  - Suites: {suite_count}")
print(f"  - Sections: {section_count}")
print(f"  - Cases: {case_count}")
print(f"  - Milestones: {milestone_count}")
print(f"  - Plans: {plan_count}")
print(f"  - Runs: {run_count}")
print(f"  - Tests: {test_count}")
print(f"  - Results: {result_count}")
print(f"  - Attachments: {attachment_count}")

db.close()
