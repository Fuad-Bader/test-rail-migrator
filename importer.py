from testrail import *
from sqlite3 import *
import json

with open('config.json') as config_file:
    config = json.load(config_file)
db = connect('testrail.db')
cursor = db.cursor()

client = APIClient(config['testrail_url'])
client.user = config['testrail_user']
client.password = config['testrail_password']

print("=" * 80)
print("FETCHING AND STORING TESTRAIL DATA")
print("=" * 80)

# 1. PROJECTS
print("\n[1/15] Fetching Projects...")
projects = client.send_get('get_projects')['projects']
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
for project in projects:
    project_id = project['id']
    project = client.send_get(f'get_project/{project_id}')
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
print(f"✓ Stored {len(projects)} projects")

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
for project in projects:
    try:
        templates = client.send_get(f'get_templates/{project["id"]}')
        for template in templates:
            cursor.execute('INSERT OR REPLACE INTO templates (id, project_id, name, is_default) VALUES (?, ?, ?, ?)',
                           (template['id'], project['id'], template['name'], template['is_default']))
        db.commit()
    except Exception as e:
        print(f"  Warning: Could not fetch templates for project {project['id']}: {e}")
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
for project in projects:
    try:
        suites = client.send_get(f'get_suites/{project["id"]}')['suites']
        for suite in suites:
            cursor.execute('INSERT OR REPLACE INTO suites (id, project_id, name, description, url, is_master, is_baseline, is_completed, completed_on) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)',
                           (suite['id'], suite['project_id'], suite['name'], suite.get('description'), suite['url'], 
                            suite['is_master'], suite['is_baseline'], suite['is_completed'], suite.get('completed_on')))
            suite_count += 1
        db.commit()
    except Exception as e:
        print(f"  Warning: Could not fetch suites for project {project['id']}: {e}")
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
for project in projects:
    try:
        suites = client.send_get(f'get_suites/{project["id"]}')['suites']
        for suite in suites:
            try:
                sections = client.send_get(f'get_sections/{project["id"]}&suite_id={suite["id"]}')['sections']
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
for project in projects:
    try:
        milestones = client.send_get(f'get_milestones/{project["id"]}')['milestones']
        for milestone in milestones:
            cursor.execute('INSERT OR REPLACE INTO milestones (id, project_id, name, description, start_on, started_on, is_started, due_on, is_completed, completed_on, parent_id, url) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)',
                           (milestone['id'], milestone['project_id'], milestone['name'], milestone.get('description'), 
                            milestone.get('start_on'), milestone.get('started_on'), milestone['is_started'], 
                            milestone.get('due_on'), milestone['is_completed'], milestone.get('completed_on'), 
                            milestone.get('parent_id'), milestone['url']))
            milestone_count += 1
        db.commit()
    except Exception as e:
        print(f"  Warning: Could not fetch milestones for project {project['id']}: {e}")
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
for project in projects:
    try:
        suites = client.send_get(f'get_suites/{project["id"]}')['suites']
        for suite in suites:
            try:
                cases = client.send_get(f'get_cases/{project["id"]}&suite_id={suite["id"]}')['cases']
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
for project in projects:
    try:
        plans = client.send_get(f'get_plans/{project["id"]}')['plans']
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
        print(f"  Warning: Could not fetch plans for project {project['id']}: {e}")
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
for project in projects:
    try:
        runs = client.send_get(f'get_runs/{project["id"]}')['runs']
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
        print(f"  Warning: Could not fetch runs for project {project['id']}: {e}")
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
for project in projects:
    try:
        runs = client.send_get(f'get_runs/{project["id"]}')['runs']
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
for project in projects:
    try:
        runs = client.send_get(f'get_runs/{project["id"]}')['runs']
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

print("\n" + "=" * 80)
print("MIGRATION COMPLETE!")
print("=" * 80)
print(f"\nDatabase saved to: testrail.db")
print("\nSummary:")
print(f"  - Projects: {len(projects)}")
print(f"  - Users: {len(users)}")
print(f"  - Suites: {suite_count}")
print(f"  - Sections: {section_count}")
print(f"  - Cases: {case_count}")
print(f"  - Milestones: {milestone_count}")
print(f"  - Plans: {plan_count}")
print(f"  - Runs: {run_count}")
print(f"  - Tests: {test_count}")
print(f"  - Results: {result_count}")

db.close()
