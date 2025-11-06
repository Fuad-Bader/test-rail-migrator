#!/usr/bin/env python3
"""
Migration Report Generator

Generates detailed reports for TestRail import and Xray export operations.
"""

import sqlite3
import json
import os
from datetime import datetime


class MigrationReporter:
    """Generate detailed migration reports"""
    
    def __init__(self, db_path='testrail.db', mapping_path='migration_mapping.json', project_id=None):
        self.db_path = db_path
        self.mapping_path = mapping_path
        self.project_id = project_id
    
    def generate_import_report(self):
        """Generate detailed import report from database"""
        if not os.path.exists(self.db_path):
            return {
                'status': 'error',
                'message': 'Database not found. Please run import first.'
            }
        
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        report = {
            'status': 'success',
            'timestamp': datetime.now().isoformat(),
            'database': self.db_path,
            'summary': {},
            'details': {}
        }
        
        # Get list of all tables
        cursor.execute("SELECT name FROM sqlite_master WHERE type='table' ORDER BY name")
        tables = [row[0] for row in cursor.fetchall() if row[0] != 'sqlite_sequence']
        
        total_records = 0
        
        # Count records in each table
        for table in tables:
            try:
                cursor.execute(f'SELECT COUNT(*) FROM {table}')
                count = cursor.fetchone()[0]
                total_records += count
                report['details'][table] = {
                    'count': count,
                    'type': self._get_table_description(table)
                }
            except:
                pass
        
        report['summary'] = {
            'total_tables': len(tables),
            'total_records': total_records,
            'tables_with_data': sum(1 for t in report['details'].values() if t['count'] > 0)
        }
        
        # Get specific entity counts for summary
        entity_counts = {}
        
        # Add project filter info if specified
        if self.project_id:
            report['filtered_by_project'] = self.project_id
            cursor.execute('SELECT name FROM projects WHERE id = ?', (self.project_id,))
            project_row = cursor.fetchone()
            if project_row:
                report['project_name'] = project_row[0]
        
        # Projects
        if 'projects' in report['details']:
            if self.project_id:
                cursor.execute('SELECT id, name FROM projects WHERE id = ?', (self.project_id,))
            else:
                cursor.execute('SELECT id, name FROM projects')
            projects = cursor.fetchall()
            entity_counts['projects'] = {
                'count': len(projects),
                'items': [{'id': p[0], 'name': p[1]} for p in projects]
            }
        
        # Users
        if 'users' in report['details']:
            cursor.execute('SELECT COUNT(*) FROM users WHERE is_active = 1')
            active_users = cursor.fetchone()[0]
            entity_counts['users'] = {
                'count': report['details']['users']['count'],
                'active': active_users
            }
        
        # Test Suites
        if 'suites' in report['details']:
            if self.project_id:
                cursor.execute('SELECT id, name, project_id FROM suites WHERE project_id = ?', (self.project_id,))
            else:
                cursor.execute('SELECT id, name, project_id FROM suites')
            suites = cursor.fetchall()
            entity_counts['suites'] = {
                'count': len(suites),
                'items': [{'id': s[0], 'name': s[1], 'project_id': s[2]} for s in suites]
            }
        
        # Sections
        if 'sections' in report['details']:
            cursor.execute('SELECT COUNT(*) FROM sections')
            section_count = cursor.fetchone()[0]
            entity_counts['sections'] = {
                'count': section_count
            }
        
        # Test Cases
        if 'cases' in report['details']:
            if self.project_id:
                # Filter cases by project through suites
                cursor.execute('''
                    SELECT c.priority_id, COUNT(*) 
                    FROM cases c 
                    JOIN suites s ON c.suite_id = s.id 
                    WHERE s.project_id = ? 
                    GROUP BY c.priority_id
                ''', (self.project_id,))
                priority_breakdown = {row[0]: row[1] for row in cursor.fetchall()}
                
                cursor.execute('''
                    SELECT c.type_id, COUNT(*) 
                    FROM cases c 
                    JOIN suites s ON c.suite_id = s.id 
                    WHERE s.project_id = ? 
                    GROUP BY c.type_id
                ''', (self.project_id,))
                type_breakdown = {row[0]: row[1] for row in cursor.fetchall()}
                
                cursor.execute('''
                    SELECT COUNT(*) 
                    FROM cases c 
                    JOIN suites s ON c.suite_id = s.id 
                    WHERE s.project_id = ?
                ''', (self.project_id,))
                case_count = cursor.fetchone()[0]
            else:
                cursor.execute('SELECT priority_id, COUNT(*) FROM cases GROUP BY priority_id')
                priority_breakdown = {row[0]: row[1] for row in cursor.fetchall()}
                
                cursor.execute('SELECT type_id, COUNT(*) FROM cases GROUP BY type_id')
                type_breakdown = {row[0]: row[1] for row in cursor.fetchall()}
                
                case_count = report['details']['cases']['count']
            
            entity_counts['cases'] = {
                'count': case_count,
                'by_priority': priority_breakdown,
                'by_type': type_breakdown
            }
        
        # Test Runs
        if 'runs' in report['details']:
            if self.project_id:
                cursor.execute('SELECT is_completed, COUNT(*) FROM runs WHERE project_id = ? GROUP BY is_completed', (self.project_id,))
                status_breakdown = {}
                for row in cursor.fetchall():
                    status = 'completed' if row[0] == 1 else 'active'
                    status_breakdown[status] = row[1]
                
                cursor.execute('SELECT COUNT(*) FROM runs WHERE project_id = ?', (self.project_id,))
                run_count = cursor.fetchone()[0]
            else:
                cursor.execute('SELECT is_completed, COUNT(*) FROM runs GROUP BY is_completed')
                status_breakdown = {}
                for row in cursor.fetchall():
                    status = 'completed' if row[0] == 1 else 'active'
                    status_breakdown[status] = row[1]
                run_count = report['details']['runs']['count']
            
            entity_counts['runs'] = {
                'count': run_count,
                'by_status': status_breakdown
            }
        
        # Test Results
        if 'results' in report['details']:
            cursor.execute('SELECT status_id, COUNT(*) FROM results GROUP BY status_id')
            status_breakdown = {row[0]: row[1] for row in cursor.fetchall()}
            
            entity_counts['results'] = {
                'count': report['details']['results']['count'],
                'by_status': status_breakdown
            }
        
        # Milestones
        if 'milestones' in report['details']:
            if self.project_id:
                cursor.execute('SELECT is_completed, COUNT(*) FROM milestones WHERE project_id = ? GROUP BY is_completed', (self.project_id,))
                status_breakdown = {}
                for row in cursor.fetchall():
                    status = 'completed' if row[0] == 1 else 'active'
                    status_breakdown[status] = row[1]
                
                cursor.execute('SELECT COUNT(*) FROM milestones WHERE project_id = ?', (self.project_id,))
                milestone_count = cursor.fetchone()[0]
            else:
                cursor.execute('SELECT is_completed, COUNT(*) FROM milestones GROUP BY is_completed')
                status_breakdown = {}
                for row in cursor.fetchall():
                    status = 'completed' if row[0] == 1 else 'active'
                    status_breakdown[status] = row[1]
                milestone_count = report['details']['milestones']['count']
            
            entity_counts['milestones'] = {
                'count': milestone_count,
                'by_status': status_breakdown
            }
        
        # Attachments
        if 'attachments' in report['details']:
            cursor.execute('SELECT entity_type, COUNT(*) FROM attachments GROUP BY entity_type')
            type_breakdown = {row[0]: row[1] for row in cursor.fetchall()}
            
            cursor.execute('SELECT SUM(size) FROM attachments')
            total_size = cursor.fetchone()[0] or 0
            
            entity_counts['attachments'] = {
                'count': report['details']['attachments']['count'],
                'by_entity_type': type_breakdown,
                'total_size_mb': round(total_size / (1024 * 1024), 2)
            }
        
        report['entities'] = entity_counts
        
        conn.close()
        return report
    
    def generate_export_report(self):
        """Generate detailed export report from mapping file"""
        if not os.path.exists(self.mapping_path):
            return {
                'status': 'error',
                'message': 'Mapping file not found. Please run export first.'
            }
        
        with open(self.mapping_path) as f:
            mapping = json.load(f)
        
        report = {
            'status': 'success',
            'timestamp': datetime.now().isoformat(),
            'mapping_file': self.mapping_path,
            'summary': {},
            'details': {}
        }
        
        total_migrated = 0
        
        # Test Cases
        if 'cases' in mapping:
            test_cases = mapping['cases']
            report['details']['test_cases'] = {
                'count': len(test_cases),
                'testrail_ids': list(test_cases.keys()),
                'xray_keys': list(test_cases.values()),
                'type': 'Test issues in Xray'
            }
            total_migrated += len(test_cases)
        
        # Test Suites
        if 'suites' in mapping:
            test_suites = mapping['suites']
            report['details']['test_suites'] = {
                'count': len(test_suites),
                'testrail_ids': list(test_suites.keys()),
                'xray_keys': list(test_suites.values()),
                'type': 'Test Set issues in Xray'
            }
            total_migrated += len(test_suites)
        
        # Test Runs/Executions
        if 'runs' in mapping:
            test_runs = mapping['runs']
            report['details']['test_executions'] = {
                'count': len(test_runs),
                'testrail_ids': list(test_runs.keys()),
                'xray_keys': list(test_runs.values()),
                'type': 'Test Execution issues in Xray'
            }
            total_migrated += len(test_runs)
        
        # Milestones
        if 'milestones' in mapping:
            milestones = mapping['milestones']
            report['details']['milestones'] = {
                'count': len(milestones),
                'testrail_ids': list(milestones.keys()),
                'jira_version_ids': list(milestones.values()),
                'type': 'Versions in Jira'
            }
            total_migrated += len(milestones)
        
        # Plans
        if 'plans' in mapping:
            plans = mapping['plans']
            report['details']['test_plans'] = {
                'count': len(plans),
                'testrail_ids': list(plans.keys()),
                'xray_keys': list(plans.values()),
                'type': 'Test Plan issues in Xray'
            }
            total_migrated += len(plans)
        
        report['summary'] = {
            'total_entities_migrated': total_migrated,
            'entity_types': len([k for k in report['details'].keys() if report['details'][k]['count'] > 0])
        }
        
        # If database exists, add attachment info
        if os.path.exists(self.db_path):
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            try:
                cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='attachments'")
                if cursor.fetchone():
                    cursor.execute('SELECT COUNT(*) FROM attachments')
                    attachment_count = cursor.fetchone()[0]
                    
                    report['details']['attachments'] = {
                        'count': attachment_count,
                        'type': 'Attachments uploaded to Jira issues'
                    }
                    total_migrated += attachment_count
                    report['summary']['total_entities_migrated'] = total_migrated
            except:
                pass
            
            conn.close()
        
        return report
    
    def generate_combined_report(self):
        """Generate combined import and export report"""
        import_report = self.generate_import_report()
        export_report = self.generate_export_report()
        
        combined = {
            'timestamp': datetime.now().isoformat(),
            'import': import_report,
            'export': export_report,
            'comparison': {}
        }
        
        # Compare import vs export
        if import_report['status'] == 'success' and export_report['status'] == 'success':
            comparison = {}
            
            # Test Cases
            imported_cases = import_report['entities'].get('cases', {}).get('count', 0)
            exported_cases = export_report['details'].get('test_cases', {}).get('count', 0)
            comparison['test_cases'] = {
                'imported': imported_cases,
                'exported': exported_cases,
                'pending': imported_cases - exported_cases
            }
            
            # Test Suites
            imported_suites = import_report['entities'].get('suites', {}).get('count', 0)
            exported_suites = export_report['details'].get('test_suites', {}).get('count', 0)
            comparison['test_suites'] = {
                'imported': imported_suites,
                'exported': exported_suites,
                'pending': imported_suites - exported_suites
            }
            
            # Test Runs
            imported_runs = import_report['entities'].get('runs', {}).get('count', 0)
            exported_runs = export_report['details'].get('test_executions', {}).get('count', 0)
            comparison['test_runs'] = {
                'imported': imported_runs,
                'exported': exported_runs,
                'pending': imported_runs - exported_runs
            }
            
            # Milestones
            imported_milestones = import_report['entities'].get('milestones', {}).get('count', 0)
            exported_milestones = export_report['details'].get('milestones', {}).get('count', 0)
            comparison['milestones'] = {
                'imported': imported_milestones,
                'exported': exported_milestones,
                'pending': imported_milestones - exported_milestones
            }
            
            # Attachments
            imported_attachments = import_report['entities'].get('attachments', {}).get('count', 0)
            exported_attachments = export_report['details'].get('attachments', {}).get('count', 0)
            comparison['attachments'] = {
                'imported': imported_attachments,
                'exported': exported_attachments,
                'pending': imported_attachments - exported_attachments
            }
            
            combined['comparison'] = comparison
        
        return combined
    
    def _get_table_description(self, table_name):
        """Get human-readable description for table"""
        descriptions = {
            'projects': 'TestRail Projects',
            'users': 'TestRail Users',
            'case_types': 'Test Case Types',
            'case_fields': 'Custom Case Fields',
            'result_fields': 'Custom Result Fields',
            'priorities': 'Priority Levels',
            'statuses': 'Test Statuses',
            'templates': 'Test Case Templates',
            'suites': 'Test Suites',
            'sections': 'Test Suite Sections',
            'cases': 'Test Cases',
            'milestones': 'Milestones',
            'plans': 'Test Plans',
            'runs': 'Test Runs',
            'tests': 'Tests in Runs',
            'results': 'Test Results',
            'attachments': 'File Attachments'
        }
        return descriptions.get(table_name, table_name)
    
    def save_report_to_file(self, report, filename=None):
        """Save report to JSON file"""
        if filename is None:
            timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
            filename = f'migration_report_{timestamp}.json'
        
        with open(filename, 'w') as f:
            json.dump(report, f, indent=2)
        
        return filename
    
    def print_report(self, report, report_type='combined'):
        """Print formatted report to console"""
        print("\n" + "=" * 80)
        print(f"MIGRATION REPORT - {report_type.upper()}")
        print("=" * 80)
        print(f"Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        print("=" * 80)
        
        if report_type == 'import':
            self._print_import_report(report)
        elif report_type == 'export':
            self._print_export_report(report)
        elif report_type == 'combined':
            self._print_combined_report(report)
    
    def _print_import_report(self, report):
        """Print import report"""
        if report['status'] == 'error':
            print(f"\n❌ {report['message']}")
            return
        
        print("\n📥 IMPORT SUMMARY")
        print("-" * 80)
        print(f"Database: {report['database']}")
        print(f"Total Tables: {report['summary']['total_tables']}")
        print(f"Tables with Data: {report['summary']['tables_with_data']}")
        print(f"Total Records: {report['summary']['total_records']}")
        
        if 'entities' in report:
            print("\n📊 DETAILED BREAKDOWN")
            print("-" * 80)
            
            entities = report['entities']
            
            # Projects
            if 'projects' in entities:
                print(f"\n✓ Projects: {entities['projects']['count']}")
                for proj in entities['projects']['items']:
                    print(f"  - ID {proj['id']}: {proj['name']}")
            
            # Users
            if 'users' in entities:
                print(f"\n✓ Users: {entities['users']['count']}")
                print(f"  - Active: {entities['users'].get('active', 'N/A')}")
            
            # Suites
            if 'suites' in entities:
                print(f"\n✓ Test Suites: {entities['suites']['count']}")
                for suite in entities['suites']['items']:
                    print(f"  - ID {suite['id']}: {suite['name']} (Project {suite['project_id']})")
            
            # Sections
            if 'sections' in entities:
                print(f"\n✓ Sections: {entities['sections']['count']}")
            
            # Cases
            if 'cases' in entities:
                print(f"\n✓ Test Cases: {entities['cases']['count']}")
                if 'by_priority' in entities['cases']:
                    print("  By Priority:")
                    for priority, count in entities['cases']['by_priority'].items():
                        print(f"    - Priority {priority}: {count}")
                if 'by_type' in entities['cases']:
                    print("  By Type:")
                    for type_id, count in entities['cases']['by_type'].items():
                        print(f"    - Type {type_id}: {count}")
            
            # Runs
            if 'runs' in entities:
                print(f"\n✓ Test Runs: {entities['runs']['count']}")
                if 'by_status' in entities['runs']:
                    for status, count in entities['runs']['by_status'].items():
                        print(f"  - {status.title()}: {count}")
            
            # Results
            if 'results' in entities:
                print(f"\n✓ Test Results: {entities['results']['count']}")
                if 'by_status' in entities['results']:
                    print("  By Status:")
                    for status_id, count in entities['results']['by_status'].items():
                        print(f"    - Status {status_id}: {count}")
            
            # Milestones
            if 'milestones' in entities:
                print(f"\n✓ Milestones: {entities['milestones']['count']}")
                if 'by_status' in entities['milestones']:
                    for status, count in entities['milestones']['by_status'].items():
                        print(f"  - {status.title()}: {count}")
            
            # Attachments
            if 'attachments' in entities:
                print(f"\n✓ Attachments: {entities['attachments']['count']}")
                print(f"  - Total Size: {entities['attachments']['total_size_mb']} MB")
                if 'by_entity_type' in entities['attachments']:
                    print("  By Type:")
                    for entity_type, count in entities['attachments']['by_entity_type'].items():
                        print(f"    - {entity_type}: {count}")
    
    def _print_export_report(self, report):
        """Print export report"""
        if report['status'] == 'error':
            print(f"\n❌ {report['message']}")
            return
        
        print("\n📤 EXPORT SUMMARY")
        print("-" * 80)
        print(f"Mapping File: {report['mapping_file']}")
        print(f"Total Entities Migrated: {report['summary']['total_entities_migrated']}")
        print(f"Entity Types: {report['summary']['entity_types']}")
        
        print("\n📊 DETAILED BREAKDOWN")
        print("-" * 80)
        
        details = report['details']
        
        # Test Cases
        if 'test_cases' in details:
            print(f"\n✓ Test Cases (Xray Test issues): {details['test_cases']['count']}")
            print(f"  - Xray Keys: {', '.join(details['test_cases']['xray_keys'][:5])}")
            if len(details['test_cases']['xray_keys']) > 5:
                print(f"    ... and {len(details['test_cases']['xray_keys']) - 5} more")
        
        # Test Suites
        if 'test_suites' in details:
            print(f"\n✓ Test Suites (Xray Test Set issues): {details['test_suites']['count']}")
            print(f"  - Xray Keys: {', '.join(details['test_suites']['xray_keys'])}")
        
        # Test Executions
        if 'test_executions' in details:
            print(f"\n✓ Test Executions (Xray Test Execution issues): {details['test_executions']['count']}")
            print(f"  - Xray Keys: {', '.join(details['test_executions']['xray_keys'])}")
        
        # Milestones
        if 'milestones' in details:
            print(f"\n✓ Milestones (Jira Versions): {details['milestones']['count']}")
        
        # Test Plans
        if 'test_plans' in details:
            print(f"\n✓ Test Plans (Xray Test Plan issues): {details['test_plans']['count']}")
        
        # Attachments
        if 'attachments' in details:
            print(f"\n✓ Attachments: {details['attachments']['count']}")
    
    def _print_combined_report(self, report):
        """Print combined report"""
        print("\n" + "=" * 80)
        print("IMPORT REPORT")
        print("=" * 80)
        self._print_import_report(report['import'])
        
        print("\n\n" + "=" * 80)
        print("EXPORT REPORT")
        print("=" * 80)
        self._print_export_report(report['export'])
        
        if report.get('comparison'):
            print("\n\n" + "=" * 80)
            print("📊 IMPORT vs EXPORT COMPARISON")
            print("=" * 80)
            
            comparison = report['comparison']
            
            print("\n{:<20} {:>12} {:>12} {:>12}".format(
                "Entity Type", "Imported", "Exported", "Pending"
            ))
            print("-" * 60)
            
            for entity_type, data in comparison.items():
                entity_name = entity_type.replace('_', ' ').title()
                print("{:<20} {:>12} {:>12} {:>12}".format(
                    entity_name,
                    data['imported'],
                    data['exported'],
                    data['pending']
                ))
            
            # Calculate completion percentage
            total_imported = sum(d['imported'] for d in comparison.values())
            total_exported = sum(d['exported'] for d in comparison.values())
            
            if total_imported > 0:
                completion = (total_exported / total_imported) * 100
                print("\n" + "-" * 60)
                print(f"Overall Migration Completion: {completion:.1f}%")


def main():
    """Main function for command-line usage"""
    import sys
    
    reporter = MigrationReporter()
    
    if len(sys.argv) > 1:
        report_type = sys.argv[1]
    else:
        report_type = 'combined'
    
    if report_type == 'import':
        report = reporter.generate_import_report()
        reporter.print_report(report, 'import')
    elif report_type == 'export':
        report = reporter.generate_export_report()
        reporter.print_report(report, 'export')
    else:
        report = reporter.generate_combined_report()
        reporter.print_report(report, 'combined')
    
    # Save to file
    filename = reporter.save_report_to_file(report)
    print(f"\n💾 Report saved to: {filename}")
    print("=" * 80)


if __name__ == '__main__':
    main()
