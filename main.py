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

projects = client.send_get('get_projects')['projects']
for project in projects:
    project_id=project['id']
    project = client.send_get(f'get_project/{project_id}')
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
    print(project)
