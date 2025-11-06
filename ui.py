"""
TestRail to Xray Migrator - GUI Application
A graphical interface for importing from TestRail and migrating to Xray/Jira
"""

import tkinter as tk
from tkinter import ttk, messagebox, scrolledtext
import sqlite3
import json
import threading
import sys
import io
import subprocess
import os
from datetime import datetime

# Import migrator for client class
import migrator


class RedirectText(io.StringIO):
    """Redirect stdout to text widget"""
    def __init__(self, text_widget):
        super().__init__()
        self.text_widget = text_widget
    
    def write(self, string):
        self.text_widget.insert(tk.END, string)
        self.text_widget.see(tk.END)
        self.text_widget.update_idletasks()
    
    def flush(self):
        pass


class TestRailMigratorUI:
    def __init__(self, root):
        self.root = root
        self.root.title("TestRail to Xray Migrator")
        self.root.geometry("1200x800")
        
        # Set up proper window close handler
        self.root.protocol("WM_DELETE_WINDOW", self.on_closing)
        
        # Load configuration
        self.load_config()
        
        # Create main notebook (tabs)
        self.notebook = ttk.Notebook(root)
        self.notebook.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)
        
        # Bind tab change event to update project labels
        self.notebook.bind("<<NotebookTabChanged>>", self.on_tab_changed)
        
        # Create tabs
        self.create_project_selection_tab()
        self.create_import_tab()
        self.create_export_tab()
        self.create_reports_tab()
        self.create_viewer_tab()
        self.create_config_tab()
        
    def load_config(self):
        """Load configuration from config.json"""
        try:
            with open('config.json') as f:
                self.config = json.load(f)
        except Exception as e:
            messagebox.showerror("Config Error", f"Failed to load config.json: {e}")
            self.config = {}
    
    def save_config(self):
        """Save configuration to config.json"""
        try:
            with open('config.json', 'w') as f:
                json.dump(self.config, f, indent=2)
            messagebox.showinfo("Success", "Configuration saved successfully!")
        except Exception as e:
            messagebox.showerror("Error", f"Failed to save configuration: {e}")
    
    # ========================================================================
    # PROJECT SELECTION TAB
    # ========================================================================
    
    def create_project_selection_tab(self):
        """Create the project selection tab for choosing TestRail and Jira projects"""
        project_frame = ttk.Frame(self.notebook)
        self.notebook.add(project_frame, text="1. Select Projects")
        
        # Title
        title = ttk.Label(project_frame, text="Project Selection", 
                         font=("Arial", 16, "bold"))
        title.pack(pady=10)
        
        # Check for existing configuration
        migration_config = self.load_migration_config()
        
        # Current selection display
        current_frame = ttk.LabelFrame(project_frame, text="Current Selection", padding=10)
        current_frame.pack(fill=tk.X, padx=10, pady=5)
        
        if migration_config:
            ttk.Label(current_frame, text=f"✓ TestRail Project: {migration_config.get('testrail_project_name')} (ID: {migration_config.get('testrail_project_id')})", 
                     foreground="green", font=("Arial", 10, "bold")).pack(anchor=tk.W, pady=2)
            ttk.Label(current_frame, text=f"✓ Jira Project: {migration_config.get('jira_project_name')} ({migration_config.get('jira_project_key')})", 
                     foreground="green", font=("Arial", 10, "bold")).pack(anchor=tk.W, pady=2)
        else:
            ttk.Label(current_frame, text="⚠ No project selection found. Please select projects below.", 
                     foreground="orange", font=("Arial", 10, "bold")).pack(anchor=tk.W)
        
        # Instructions
        instructions = ttk.LabelFrame(project_frame, text="Instructions", padding=10)
        instructions.pack(fill=tk.X, padx=10, pady=5)
        ttk.Label(instructions, text="1. Ensure your credentials are configured in the Config tab\n"
                                    "2. Click 'Refresh Projects' to load available projects\n"
                                    "3. Select a TestRail project to import\n"
                                    "4. Select a Jira project (or add one by key) as migration target\n"
                                    "5. Click 'Save Selection' to proceed",
                 justify=tk.LEFT).pack(anchor=tk.W)
        
        # Main selection area
        selection_paned = ttk.PanedWindow(project_frame, orient=tk.HORIZONTAL)
        selection_paned.pack(fill=tk.BOTH, expand=True, padx=10, pady=5)
        
        # TestRail projects panel
        testrail_frame = ttk.LabelFrame(selection_paned, text="TestRail Projects", padding=10)
        selection_paned.add(testrail_frame, weight=1)
        
        ttk.Button(testrail_frame, text="Refresh TestRail Projects", 
                  command=self.refresh_testrail_projects).pack(pady=5)
        
        self.testrail_projects_tree = ttk.Treeview(testrail_frame, columns=("ID", "Status"), 
                                                    show="tree headings", selectmode="browse")
        self.testrail_projects_tree.heading("#0", text="Project Name")
        self.testrail_projects_tree.heading("ID", text="ID")
        self.testrail_projects_tree.heading("Status", text="Status")
        self.testrail_projects_tree.column("ID", width=60)
        self.testrail_projects_tree.column("Status", width=100)
        
        testrail_scroll = ttk.Scrollbar(testrail_frame, orient=tk.VERTICAL, 
                                       command=self.testrail_projects_tree.yview)
        self.testrail_projects_tree.configure(yscrollcommand=testrail_scroll.set)
        
        self.testrail_projects_tree.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        testrail_scroll.pack(side=tk.RIGHT, fill=tk.Y)
        
        # Jira projects panel
        jira_frame = ttk.LabelFrame(selection_paned, text="Jira Projects", padding=10)
        selection_paned.add(jira_frame, weight=1)
        
        button_frame = ttk.Frame(jira_frame)
        button_frame.pack(pady=5)
        
        ttk.Button(button_frame, text="Refresh Jira Projects", 
                  command=self.refresh_jira_projects).pack(side=tk.LEFT, padx=5)
        
        ttk.Button(button_frame, text="Add Project by Key", 
                  command=self.add_jira_project_by_key, 
                  style="Accent.TButton").pack(side=tk.LEFT, padx=5)
        
        self.jira_projects_tree = ttk.Treeview(jira_frame, columns=("Key",), 
                                               show="tree headings", selectmode="browse")
        self.jira_projects_tree.heading("#0", text="Project Name")
        self.jira_projects_tree.heading("Key", text="Key")
        self.jira_projects_tree.column("Key", width=100)
        
        jira_scroll = ttk.Scrollbar(jira_frame, orient=tk.VERTICAL, 
                                    command=self.jira_projects_tree.yview)
        self.jira_projects_tree.configure(yscrollcommand=jira_scroll.set)
        
        self.jira_projects_tree.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        jira_scroll.pack(side=tk.RIGHT, fill=tk.Y)
        
        # Save button
        save_frame = ttk.Frame(project_frame)
        save_frame.pack(pady=10)
        
        ttk.Button(save_frame, text="Save Selection", 
                  command=self.save_project_selection,
                  style="Accent.TButton").pack(side=tk.LEFT, padx=5)
        
        ttk.Button(save_frame, text="Clear Selection", 
                  command=self.clear_project_selection).pack(side=tk.LEFT, padx=5)
    
    def load_migration_config(self):
        """Load existing migration configuration"""
        try:
            with open('migration_config.json') as f:
                return json.load(f)
        except:
            return None
    
    def refresh_testrail_projects(self):
        """Fetch and display TestRail projects"""
        # Clear existing items
        for item in self.testrail_projects_tree.get_children():
            self.testrail_projects_tree.delete(item)
        
        if not self.config.get('testrail_url') or not self.config.get('testrail_user'):
            messagebox.showerror("Configuration Error", 
                               "Please configure TestRail credentials in the Config tab first!")
            return
        
        try:
            from testrail import APIClient
            
            client = APIClient(self.config['testrail_url'])
            client.user = self.config['testrail_user']
            client.password = self.config['testrail_password']
            
            response = client.send_get('get_projects')
            projects = response.get('projects', [])
            
            for project in projects:
                status = "✓ Active" if not project.get('is_completed') else "✗ Completed"
                self.testrail_projects_tree.insert("", tk.END, text=project['name'],
                                                   values=(project['id'], status),
                                                   tags=(project['id'], project['name']))
            
            messagebox.showinfo("Success", f"Loaded {len(projects)} TestRail projects")
            
        except Exception as e:
            messagebox.showerror("Error", f"Failed to fetch TestRail projects: {e}")
    
    def refresh_jira_projects(self):
        """Fetch and display Jira projects"""
        # Clear existing items
        for item in self.jira_projects_tree.get_children():
            self.jira_projects_tree.delete(item)
        
        if not self.config.get('jira_url') or not self.config.get('jira_username'):
            messagebox.showerror("Configuration Error", 
                               "Please configure Jira credentials in the Config tab first!")
            return
        
        try:
            import requests
            from requests.auth import HTTPBasicAuth
            import re
            
            base_url = self.config['jira_url']
            username = self.config['jira_username']
            password = self.config['jira_password']
            
            # Detect if using PAT
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
            
            url = f"{base_url}/rest/api/2/project"
            response = requests.get(url, auth=auth, headers=headers)
            response.raise_for_status()
            projects = response.json()
            
            for project in projects:
                self.jira_projects_tree.insert("", tk.END, text=project['name'],
                                              values=(project['key'],),
                                              tags=(project['key'], project['name'], 
                                                   project.get('id', '')))
            
            messagebox.showinfo("Success", f"Loaded {len(projects)} Jira projects")
            
        except Exception as e:
            messagebox.showerror("Error", f"Failed to fetch Jira projects: {e}")
    
    def add_jira_project_by_key(self):
        """Show dialog to add a Jira project by entering its key"""
        dialog = tk.Toplevel(self.root)
        dialog.title("Add Jira Project by Key")
        dialog.geometry("450x200")
        dialog.transient(self.root)
        dialog.grab_set()
        
        ttk.Label(dialog, text="Add Jira Project by Key", 
                 font=("Arial", 14, "bold")).pack(pady=10)
        
        ttk.Label(dialog, text="Enter the existing Jira project key to add it to the list:",
                 wraplength=400).pack(pady=10, padx=20)
        
        # Form fields
        form_frame = ttk.Frame(dialog, padding=20)
        form_frame.pack(fill=tk.BOTH, expand=True)
        
        ttk.Label(form_frame, text="Project Key:").grid(row=0, column=0, sticky=tk.W, pady=5, padx=5)
        key_entry = ttk.Entry(form_frame, width=20)
        key_entry.grid(row=0, column=1, pady=5, padx=5)
        key_entry.focus()
        
        # Buttons
        button_frame = ttk.Frame(dialog)
        button_frame.pack(pady=10)
        
        def add_project():
            project_key = key_entry.get().strip().upper()
            
            if not project_key:
                messagebox.showerror("Error", "Project key cannot be empty")
                return
            
            if not project_key.isalnum() or len(project_key) < 2 or len(project_key) > 10:
                messagebox.showerror("Error", "Project key must be 2-10 alphanumeric characters")
                return
            
            try:
                import requests
                from requests.auth import HTTPBasicAuth
                import re
                
                base_url = self.config['jira_url']
                username = self.config['jira_username']
                password = self.config['jira_password']
                
                # Detect if using PAT
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
                
                # Fetch project details to verify it exists
                url = f"{base_url}/rest/api/2/project/{project_key}"
                response = requests.get(url, auth=auth, headers=headers)
                
                if response.status_code == 404:
                    messagebox.showerror("Error", f"Project '{project_key}' not found in Jira.")
                    return
                elif response.status_code not in [200, 201]:
                    messagebox.showerror("Error", 
                        f"Failed to fetch project (HTTP {response.status_code}):\n{response.text[:500]}")
                    return
                
                project = response.json()
                project_name = project.get('name', project_key)
                project_id = project.get('id', '')
                
                # Check if already in the list
                for item in self.jira_projects_tree.get_children():
                    item_data = self.jira_projects_tree.item(item)
                    if item_data['tags'] and item_data['tags'][0] == project_key:
                        messagebox.showinfo("Info", f"Project '{project_key}' is already in the list.")
                        dialog.destroy()
                        return
                
                messagebox.showinfo("Success", f"Added project '{project_name}' ({project_key})")
                
                # Add to tree
                self.jira_projects_tree.insert("", tk.END, text=project_name,
                                              values=(project_key,),
                                              tags=(project_key, project_name, project_id))
                
                dialog.destroy()
                
            except requests.exceptions.RequestException as e:
                error_msg = f"Request failed: {e}"
                if hasattr(e, 'response') and e.response is not None:
                    error_msg += f"\n\nStatus: {e.response.status_code}\nResponse: {e.response.text[:500]}"
                messagebox.showerror("Error", error_msg)
            except Exception as e:
                messagebox.showerror("Error", f"Failed to add project: {e}")
        
        ttk.Button(button_frame, text="Add Project", command=add_project,
                  style="Accent.TButton").pack(side=tk.LEFT, padx=5)
        ttk.Button(button_frame, text="Cancel", command=dialog.destroy).pack(side=tk.LEFT, padx=5)
    
    def save_project_selection(self):
        """Save the selected projects to migration_config.json"""
        # Get selected TestRail project
        testrail_selection = self.testrail_projects_tree.selection()
        if not testrail_selection:
            messagebox.showerror("Error", "Please select a TestRail project")
            return
        
        testrail_item = self.testrail_projects_tree.item(testrail_selection[0])
        testrail_tags = testrail_item['tags']
        testrail_project_id = testrail_tags[0]
        testrail_project_name = testrail_tags[1]
        
        # Get selected Jira project
        jira_selection = self.jira_projects_tree.selection()
        if not jira_selection:
            messagebox.showerror("Error", "Please select a Jira project")
            return
        
        jira_item = self.jira_projects_tree.item(jira_selection[0])
        jira_tags = jira_item['tags']
        jira_project_key = jira_tags[0]
        jira_project_name = jira_tags[1]
        
        # Save configuration
        migration_config = {
            'testrail_project_id': testrail_project_id,
            'testrail_project_name': testrail_project_name,
            'jira_project_key': jira_project_key,
            'jira_project_name': jira_project_name
        }
        
        try:
            with open('migration_config.json', 'w') as f:
                json.dump(migration_config, f, indent=2)
            
            messagebox.showinfo("Success", 
                              f"Project selection saved!\n\n"
                              f"TestRail: {testrail_project_name} (ID: {testrail_project_id})\n"
                              f"Jira: {jira_project_name} ({jira_project_key})\n\n"
                              f"You can now proceed to the Import tab.")
            
            # Update the project labels in Import, Export, and Reports tabs
            self.update_import_project_labels()
            self.update_export_project_labels()
            self.update_reports_project_label()
            
        except Exception as e:
            messagebox.showerror("Error", f"Failed to save configuration: {e}")
    
    def clear_project_selection(self):
        """Clear the project selection"""
        try:
            if os.path.exists('migration_config.json'):
                os.remove('migration_config.json')
            messagebox.showinfo("Success", "Project selection cleared")
            # Update the project labels in Import, Export, and Reports tabs
            self.update_import_project_labels()
            self.update_export_project_labels()
            self.update_reports_project_label()
        except Exception as e:
            messagebox.showerror("Error", f"Failed to clear selection: {e}")
    
    # ========================================================================
    # IMPORT TAB
    # ========================================================================
    
    def create_import_tab(self):
        """Create the import tab for fetching data from TestRail"""
        import_frame = ttk.Frame(self.notebook)
        self.notebook.add(import_frame, text="2. Import from TestRail")
        
        # Title
        title = ttk.Label(import_frame, text="Import Data from TestRail", 
                         font=("Arial", 16, "bold"))
        title.pack(pady=10)
        
        # Project selection status
        selection_frame = ttk.LabelFrame(import_frame, text="Selected Projects", padding=10)
        selection_frame.pack(fill=tk.X, padx=10, pady=5)
        
        # Create labels that will be updated dynamically
        self.import_testrail_label = ttk.Label(selection_frame, text="", font=("Arial", 10, "bold"))
        self.import_testrail_label.pack(anchor=tk.W, pady=2)
        
        self.import_jira_label = ttk.Label(selection_frame, text="", font=("Arial", 10, "bold"))
        self.import_jira_label.pack(anchor=tk.W, pady=2)
        
        self.import_warning_label = ttk.Label(selection_frame, text="", font=("Arial", 10, "bold"))
        self.import_warning_label.pack(anchor=tk.W)
        
        # Initial update
        self.update_import_project_labels()
        
        # Configuration display
        config_frame = ttk.LabelFrame(import_frame, text="TestRail Configuration", padding=10)
        config_frame.pack(fill=tk.X, padx=10, pady=5)
        
        ttk.Label(config_frame, text=f"TestRail URL: {self.config.get('testrail_url', 'Not set')}").pack(anchor=tk.W)
        ttk.Label(config_frame, text=f"TestRail User: {self.config.get('testrail_user', 'Not set')}").pack(anchor=tk.W)
        
        # Instructions
        instructions = ttk.LabelFrame(import_frame, text="Instructions", padding=10)
        instructions.pack(fill=tk.X, padx=10, pady=5)
        ttk.Label(instructions, text="1. Ensure projects are selected in the 'Select Projects' tab\n"
                                    "2. Ensure your TestRail credentials are configured in the Config tab\n"
                                    "3. Click 'Start Import' to fetch the selected TestRail project data\n"
                                    "4. Data will be stored in 'testrail.db' SQLite database\n"
                                    "5. Monitor the progress in the console below",
                 justify=tk.LEFT).pack(anchor=tk.W)
        
        # Control buttons
        button_frame = ttk.Frame(import_frame)
        button_frame.pack(pady=10)
        
        self.import_btn = ttk.Button(button_frame, text="Start Import", 
                                     command=self.start_import, style="Accent.TButton")
        self.import_btn.pack(side=tk.LEFT, padx=5)
        
        ttk.Button(button_frame, text="Clear Console", 
                  command=lambda: self.import_console.delete(1.0, tk.END)).pack(side=tk.LEFT, padx=5)
        
        # Console output
        console_frame = ttk.LabelFrame(import_frame, text="Console Output", padding=5)
        console_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=5)
        
        self.import_console = scrolledtext.ScrolledText(console_frame, wrap=tk.WORD, 
                                                        height=20, bg="#1e1e1e", fg="#dcdcdc",
                                                        font=("Courier", 9))
        self.import_console.pack(fill=tk.BOTH, expand=True)
    
    def start_import(self):
        """Start the import process in a separate thread"""
        if not self.config.get('testrail_url') or not self.config.get('testrail_user'):
            messagebox.showerror("Configuration Error", 
                               "Please configure TestRail credentials in the Config tab first!")
            return
        
        # Disable button during import
        self.import_btn.config(state=tk.DISABLED)
        self.import_console.delete(1.0, tk.END)
        
        # Run import in separate thread to avoid freezing UI
        thread = threading.Thread(target=self.run_import)
        thread.daemon = True
        thread.start()
    
    def run_import(self):
        """Run the import process"""
        self.import_console.insert(tk.END, "Starting import process...\n")
        self.import_console.insert(tk.END, f"Working directory: {os.getcwd()}\n")
        self.import_console.insert(tk.END, f"Python executable: {sys.executable}\n")
        self.import_console.insert(tk.END, "=" * 80 + "\n")
        self.import_console.update_idletasks()
        
        try:
            # Run importer.py as a subprocess with unbuffered output
            env = os.environ.copy()
            env['PYTHONUNBUFFERED'] = '1'  # Force unbuffered output
            
            process = subprocess.Popen(
                [sys.executable, '-u', 'importer.py'],  # -u flag for unbuffered
                stdout=subprocess.PIPE,
                stderr=subprocess.STDOUT,
                text=True,
                bufsize=0,  # Unbuffered
                universal_newlines=True,
                env=env,
                cwd=os.getcwd()
            )
            
            # Read output line by line
            while True:
                line = process.stdout.readline()
                if not line and process.poll() is not None:
                    break
                if line:
                    self.import_console.insert(tk.END, line)
                    self.import_console.see(tk.END)
                    self.import_console.update_idletasks()
            
            # Get any remaining output
            remaining = process.stdout.read()
            if remaining:
                self.import_console.insert(tk.END, remaining)
                self.import_console.see(tk.END)
                self.import_console.update_idletasks()
            
            process.wait()
            
            if process.returncode == 0:
                self.import_console.insert(tk.END, f"\n{'='*80}\n")
                self.import_console.insert(tk.END, "IMPORT COMPLETED SUCCESSFULLY!\n")
                self.import_console.insert(tk.END, f"{'='*80}\n")
            else:
                self.import_console.insert(tk.END, f"\n{'='*80}\n")
                self.import_console.insert(tk.END, f"ERROR: Process exited with code {process.returncode}\n")
                self.import_console.insert(tk.END, f"{'='*80}\n")
            
        except Exception as e:
            self.import_console.insert(tk.END, f"\n{'='*80}\n")
            self.import_console.insert(tk.END, f"ERROR: {e}\n")
            self.import_console.insert(tk.END, f"{'='*80}\n")
            import traceback
            self.import_console.insert(tk.END, traceback.format_exc())
        finally:
            self.import_btn.config(state=tk.NORMAL)
    
    # ========================================================================
    # EXPORT TAB
    # ========================================================================
    
    def create_export_tab(self):
        """Create the export tab for migrating to Xray"""
        export_frame = ttk.Frame(self.notebook)
        self.notebook.add(export_frame, text="3. Export to Xray")
        
        # Title
        title = ttk.Label(export_frame, text="Export Data to Xray (Jira)", 
                         font=("Arial", 16, "bold"))
        title.pack(pady=10)
        
        # Project selection status
        selection_frame = ttk.LabelFrame(export_frame, text="Selected Projects", padding=10)
        selection_frame.pack(fill=tk.X, padx=10, pady=5)
        
        # Create labels that will be updated dynamically
        self.export_testrail_label = ttk.Label(selection_frame, text="", font=("Arial", 10, "bold"))
        self.export_testrail_label.pack(anchor=tk.W, pady=2)
        
        self.export_jira_label = ttk.Label(selection_frame, text="", font=("Arial", 10, "bold"))
        self.export_jira_label.pack(anchor=tk.W, pady=2)
        
        self.export_warning_label = ttk.Label(selection_frame, text="", font=("Arial", 10, "bold"))
        self.export_warning_label.pack(anchor=tk.W)
        
        # Initial update
        self.update_export_project_labels()
        
        # Configuration display
        config_frame = ttk.LabelFrame(export_frame, text="Jira Configuration", padding=10)
        config_frame.pack(fill=tk.X, padx=10, pady=5)
        
        ttk.Label(config_frame, text=f"Jira URL: {self.config.get('jira_url', 'Not set')}").pack(anchor=tk.W)
        ttk.Label(config_frame, text=f"Jira Username: {self.config.get('jira_username', 'Not set')}").pack(anchor=tk.W)
        
        # Instructions
        instructions = ttk.LabelFrame(export_frame, text="Instructions", padding=10)
        instructions.pack(fill=tk.X, padx=10, pady=5)
        ttk.Label(instructions, text="1. Ensure projects are selected in the 'Select Projects' tab\n"
                                    "2. Ensure you have imported TestRail data first (Import tab)\n"
                                    "3. Configure Jira/Xray credentials in the Config tab\n"
                                    "4. Click 'Start Export' to migrate data to Xray\n"
                                    "5. The process creates Tests, Test Sets, and Test Executions\n"
                                    "6. Monitor progress in the console below",
                 justify=tk.LEFT).pack(anchor=tk.W)
        
        # Control buttons
        button_frame = ttk.Frame(export_frame)
        button_frame.pack(pady=10)
        
        self.export_btn = ttk.Button(button_frame, text="Start Export", 
                                     command=self.start_export, style="Accent.TButton")
        self.export_btn.pack(side=tk.LEFT, padx=5)
        
        ttk.Button(button_frame, text="Clear Console", 
                  command=lambda: self.export_console.delete(1.0, tk.END)).pack(side=tk.LEFT, padx=5)
        
        # Console output
        console_frame = ttk.LabelFrame(export_frame, text="Console Output", padding=5)
        console_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=5)
        
        self.export_console = scrolledtext.ScrolledText(console_frame, wrap=tk.WORD, 
                                                        height=20, bg="#1e1e1e", fg="#dcdcdc",
                                                        font=("Courier", 9))
        self.export_console.pack(fill=tk.BOTH, expand=True)
    
    def start_export(self):
        """Start the export process in a separate thread"""
        if not self.config.get('jira_url') or not self.config.get('jira_username'):
            messagebox.showerror("Configuration Error", 
                               "Please configure Jira/Xray credentials in the Config tab first!")
            return
        
        # Check if database exists
        try:
            conn = sqlite3.connect('testrail.db')
            conn.close()
        except:
            messagebox.showerror("Database Error", 
                               "Database not found! Please import TestRail data first.")
            return
        
        # Disable button during export
        self.export_btn.config(state=tk.DISABLED)
        self.export_console.delete(1.0, tk.END)
        
        # Run export in separate thread
        thread = threading.Thread(target=self.run_export)
        thread.daemon = True
        thread.start()
    
    def run_export(self):
        """Run the export process"""
        self.export_console.insert(tk.END, "Starting export process...\n")
        self.export_console.insert(tk.END, f"Working directory: {os.getcwd()}\n")
        self.export_console.insert(tk.END, f"Python executable: {sys.executable}\n")
        self.export_console.insert(tk.END, "=" * 80 + "\n")
        self.export_console.update_idletasks()
        
        try:
            # Run migrator.py as a subprocess with unbuffered output
            env = os.environ.copy()
            env['PYTHONUNBUFFERED'] = '1'  # Force unbuffered output
            
            process = subprocess.Popen(
                [sys.executable, '-u', 'migrator.py'],  # -u flag for unbuffered
                stdout=subprocess.PIPE,
                stderr=subprocess.STDOUT,
                text=True,
                bufsize=0,  # Unbuffered
                universal_newlines=True,
                env=env,
                cwd=os.getcwd()
            )
            
            # Read output line by line
            while True:
                line = process.stdout.readline()
                if not line and process.poll() is not None:
                    break
                if line:
                    self.export_console.insert(tk.END, line)
                    self.export_console.see(tk.END)
                    self.export_console.update_idletasks()
            
            # Get any remaining output
            remaining = process.stdout.read()
            if remaining:
                self.export_console.insert(tk.END, remaining)
                self.export_console.see(tk.END)
                self.export_console.update_idletasks()
            
            process.wait()
            
            if process.returncode == 0:
                self.export_console.insert(tk.END, f"\n{'='*80}\n")
                self.export_console.insert(tk.END, "EXPORT COMPLETED SUCCESSFULLY!\n")
                self.export_console.insert(tk.END, f"{'='*80}\n")
            else:
                self.export_console.insert(tk.END, f"\n{'='*80}\n")
                self.export_console.insert(tk.END, f"ERROR: Process exited with code {process.returncode}\n")
                self.export_console.insert(tk.END, f"{'='*80}\n")
            
        except Exception as e:
            self.export_console.insert(tk.END, f"\n{'='*80}\n")
            self.export_console.insert(tk.END, f"ERROR: {e}\n")
            self.export_console.insert(tk.END, f"{'='*80}\n")
            import traceback
            self.export_console.insert(tk.END, traceback.format_exc())
        finally:
            self.export_btn.config(state=tk.NORMAL)
    
    # ========================================================================
    # REPORTS TAB
    # ========================================================================
    
    def create_reports_tab(self):
        """Create the reports tab"""
        reports_frame = ttk.Frame(self.notebook)
        self.notebook.add(reports_frame, text="Reports")
        
        # Title
        title = ttk.Label(reports_frame, text="Migration Reports", 
                         font=("Arial", 16, "bold"))
        title.pack(pady=10)
        
        # Project selection status
        selection_frame = ttk.Frame(reports_frame)
        selection_frame.pack(fill=tk.X, padx=10, pady=5)
        
        self.reports_project_label = ttk.Label(selection_frame, text="", 
                                               font=("Arial", 10, "bold"))
        self.reports_project_label.pack()
        
        # Initial update
        self.update_reports_project_label()
        
        # Info
        info = ttk.Label(reports_frame, text="Generate detailed reports of import and export operations",
                        font=("Arial", 10))
        info.pack(pady=5)
        
        # Buttons frame
        button_frame = ttk.Frame(reports_frame)
        button_frame.pack(pady=10)
        
        ttk.Button(button_frame, text="📥 Import Report", 
                  command=self.generate_import_report,
                  width=20).pack(side=tk.LEFT, padx=5)
        
        ttk.Button(button_frame, text="📤 Export Report", 
                  command=self.generate_export_report,
                  width=20).pack(side=tk.LEFT, padx=5)
        
        ttk.Button(button_frame, text="📊 Combined Report", 
                  command=self.generate_combined_report,
                  width=20).pack(side=tk.LEFT, padx=5)
        
        ttk.Button(button_frame, text="💾 Save Report to File", 
                  command=self.save_report_to_file,
                  width=20).pack(side=tk.LEFT, padx=5)
        
        # Report output frame
        output_frame = ttk.LabelFrame(reports_frame, text="Report Output", padding=10)
        output_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        # Report text widget with scrollbar
        self.report_text = scrolledtext.ScrolledText(output_frame, 
                                                      width=120, 
                                                      height=30,
                                                      font=("Courier", 9))
        self.report_text.pack(fill=tk.BOTH, expand=True)
        
        # Status bar
        self.report_status = ttk.Label(reports_frame, text="Ready to generate reports", 
                                      relief=tk.SUNKEN, anchor=tk.W)
        self.report_status.pack(side=tk.BOTTOM, fill=tk.X, padx=5, pady=2)
        
        # Store current report
        self.current_report = None
    
    def generate_import_report(self):
        """Generate and display import report"""
        self.report_text.delete(1.0, tk.END)
        self.report_status.config(text="Generating import report...")
        self.root.update()
        
        try:
            # Get selected project ID from migration config
            migration_config = self.load_migration_config()
            project_id = migration_config.get('testrail_project_id') if migration_config else None
            
            from report_generator import MigrationReporter
            reporter = MigrationReporter(project_id=project_id)
            report = reporter.generate_import_report()
            self.current_report = report
            
            # Format and display report
            self.display_import_report(report)
            self.report_status.config(text="Import report generated successfully")
        except Exception as e:
            self.report_text.insert(tk.END, f"Error generating report: {e}\n")
            self.report_status.config(text="Error generating report")
    
    def generate_export_report(self):
        """Generate and display export report"""
        self.report_text.delete(1.0, tk.END)
        self.report_status.config(text="Generating export report...")
        self.root.update()
        
        try:
            # Get selected project ID from migration config
            migration_config = self.load_migration_config()
            project_id = migration_config.get('testrail_project_id') if migration_config else None
            
            from report_generator import MigrationReporter
            reporter = MigrationReporter(project_id=project_id)
            report = reporter.generate_export_report()
            self.current_report = report
            
            # Format and display report
            self.display_export_report(report)
            self.report_status.config(text="Export report generated successfully")
        except Exception as e:
            self.report_text.insert(tk.END, f"Error generating report: {e}\n")
            self.report_status.config(text="Error generating report")
    
    def generate_combined_report(self):
        """Generate and display combined report"""
        self.report_text.delete(1.0, tk.END)
        self.report_status.config(text="Generating combined report...")
        self.root.update()
        
        try:
            # Get selected project ID from migration config
            migration_config = self.load_migration_config()
            project_id = migration_config.get('testrail_project_id') if migration_config else None
            
            from report_generator import MigrationReporter
            reporter = MigrationReporter(project_id=project_id)
            report = reporter.generate_combined_report()
            self.current_report = report
            
            # Format and display report
            self.display_combined_report(report)
            self.report_status.config(text="Combined report generated successfully")
        except Exception as e:
            self.report_text.insert(tk.END, f"Error generating report: {e}\n")
            self.report_status.config(text="Error generating report")
    
    def display_import_report(self, report):
        """Display formatted import report"""
        t = self.report_text
        
        t.insert(tk.END, "=" * 80 + "\n")
        t.insert(tk.END, "IMPORT REPORT\n")
        t.insert(tk.END, "=" * 80 + "\n")
        t.insert(tk.END, f"Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
        
        # Show project filter if active
        if report.get('filtered_by_project'):
            t.insert(tk.END, f"Filtered by Project: {report.get('project_name', 'Unknown')} (ID: {report['filtered_by_project']})\n")
        else:
            t.insert(tk.END, "Showing: All Projects\n")
        
        t.insert(tk.END, "=" * 80 + "\n\n")
        
        if report['status'] == 'error':
            t.insert(tk.END, f"❌ {report['message']}\n")
            return
        
        t.insert(tk.END, "📥 IMPORT SUMMARY\n")
        t.insert(tk.END, "-" * 80 + "\n")
        t.insert(tk.END, f"Database: {report['database']}\n")
        t.insert(tk.END, f"Total Tables: {report['summary']['total_tables']}\n")
        t.insert(tk.END, f"Tables with Data: {report['summary']['tables_with_data']}\n")
        t.insert(tk.END, f"Total Records: {report['summary']['total_records']}\n")
        
        if 'entities' in report:
            t.insert(tk.END, "\n📊 DETAILED BREAKDOWN\n")
            t.insert(tk.END, "-" * 80 + "\n")
            
            entities = report['entities']
            
            # Projects
            if 'projects' in entities:
                t.insert(tk.END, f"\n✓ Projects: {entities['projects']['count']}\n")
                for proj in entities['projects']['items']:
                    t.insert(tk.END, f"  - ID {proj['id']}: {proj['name']}\n")
            
            # Users
            if 'users' in entities:
                t.insert(tk.END, f"\n✓ Users: {entities['users']['count']}\n")
                t.insert(tk.END, f"  - Active: {entities['users'].get('active', 'N/A')}\n")
            
            # Suites
            if 'suites' in entities:
                t.insert(tk.END, f"\n✓ Test Suites: {entities['suites']['count']}\n")
                for suite in entities['suites']['items']:
                    t.insert(tk.END, f"  - ID {suite['id']}: {suite['name']} (Project {suite['project_id']})\n")
            
            # Sections
            if 'sections' in entities:
                t.insert(tk.END, f"\n✓ Sections: {entities['sections']['count']}\n")
            
            # Cases
            if 'cases' in entities:
                t.insert(tk.END, f"\n✓ Test Cases: {entities['cases']['count']}\n")
                if 'by_priority' in entities['cases']:
                    t.insert(tk.END, "  By Priority:\n")
                    for priority, count in entities['cases']['by_priority'].items():
                        t.insert(tk.END, f"    - Priority {priority}: {count}\n")
                if 'by_type' in entities['cases']:
                    t.insert(tk.END, "  By Type:\n")
                    for type_id, count in entities['cases']['by_type'].items():
                        t.insert(tk.END, f"    - Type {type_id}: {count}\n")
            
            # Runs
            if 'runs' in entities:
                t.insert(tk.END, f"\n✓ Test Runs: {entities['runs']['count']}\n")
                if 'by_status' in entities['runs']:
                    for status, count in entities['runs']['by_status'].items():
                        t.insert(tk.END, f"  - {status.title()}: {count}\n")
            
            # Results
            if 'results' in entities:
                t.insert(tk.END, f"\n✓ Test Results: {entities['results']['count']}\n")
                if 'by_status' in entities['results']:
                    t.insert(tk.END, "  By Status:\n")
                    for status_id, count in entities['results']['by_status'].items():
                        t.insert(tk.END, f"    - Status {status_id}: {count}\n")
            
            # Milestones
            if 'milestones' in entities:
                t.insert(tk.END, f"\n✓ Milestones: {entities['milestones']['count']}\n")
                if 'by_status' in entities['milestones']:
                    for status, count in entities['milestones']['by_status'].items():
                        t.insert(tk.END, f"  - {status.title()}: {count}\n")
            
            # Attachments
            if 'attachments' in entities:
                t.insert(tk.END, f"\n✓ Attachments: {entities['attachments']['count']}\n")
                t.insert(tk.END, f"  - Total Size: {entities['attachments']['total_size_mb']} MB\n")
                if 'by_entity_type' in entities['attachments']:
                    t.insert(tk.END, "  By Type:\n")
                    for entity_type, count in entities['attachments']['by_entity_type'].items():
                        t.insert(tk.END, f"    - {entity_type}: {count}\n")
        
        t.insert(tk.END, "\n" + "=" * 80 + "\n")
    
    def display_export_report(self, report):
        """Display formatted export report"""
        t = self.report_text
        
        t.insert(tk.END, "=" * 80 + "\n")
        t.insert(tk.END, "EXPORT REPORT\n")
        t.insert(tk.END, "=" * 80 + "\n")
        t.insert(tk.END, f"Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
        
        # Show project info from migration config
        migration_config = self.load_migration_config()
        if migration_config:
            t.insert(tk.END, f"TestRail Project: {migration_config.get('testrail_project_name', 'Unknown')} (ID: {migration_config.get('testrail_project_id', 'N/A')})\n")
            t.insert(tk.END, f"Jira Project: {migration_config.get('jira_project_name', 'Unknown')} ({migration_config.get('jira_project_key', 'N/A')})\n")
        
        t.insert(tk.END, "=" * 80 + "\n\n")
        
        if report['status'] == 'error':
            t.insert(tk.END, f"❌ {report['message']}\n")
            return
        
        t.insert(tk.END, "📤 EXPORT SUMMARY\n")
        t.insert(tk.END, "-" * 80 + "\n")
        t.insert(tk.END, f"Mapping File: {report['mapping_file']}\n")
        t.insert(tk.END, f"Total Entities Migrated: {report['summary']['total_entities_migrated']}\n")
        t.insert(tk.END, f"Entity Types: {report['summary']['entity_types']}\n")
        
        t.insert(tk.END, "\n📊 DETAILED BREAKDOWN\n")
        t.insert(tk.END, "-" * 80 + "\n")
        
        details = report['details']
        
        # Test Cases
        if 'test_cases' in details:
            t.insert(tk.END, f"\n✓ Test Cases (Xray Test issues): {details['test_cases']['count']}\n")
            xray_keys = details['test_cases']['xray_keys']
            t.insert(tk.END, f"  - Xray Keys: {', '.join(xray_keys[:5])}")
            if len(xray_keys) > 5:
                t.insert(tk.END, f" ... and {len(xray_keys) - 5} more")
            t.insert(tk.END, "\n")
        
        # Test Suites
        if 'test_suites' in details:
            t.insert(tk.END, f"\n✓ Test Suites (Xray Test Set issues): {details['test_suites']['count']}\n")
            t.insert(tk.END, f"  - Xray Keys: {', '.join(details['test_suites']['xray_keys'])}\n")
        
        # Test Executions
        if 'test_executions' in details:
            t.insert(tk.END, f"\n✓ Test Executions (Xray Test Execution issues): {details['test_executions']['count']}\n")
            t.insert(tk.END, f"  - Xray Keys: {', '.join(details['test_executions']['xray_keys'])}\n")
        
        # Milestones
        if 'milestones' in details:
            t.insert(tk.END, f"\n✓ Milestones (Jira Versions): {details['milestones']['count']}\n")
        
        # Test Plans
        if 'test_plans' in details:
            t.insert(tk.END, f"\n✓ Test Plans (Xray Test Plan issues): {details['test_plans']['count']}\n")
        
        # Attachments
        if 'attachments' in details:
            t.insert(tk.END, f"\n✓ Attachments: {details['attachments']['count']}\n")
        
        t.insert(tk.END, "\n" + "=" * 80 + "\n")
    
    def display_combined_report(self, report):
        """Display formatted combined report"""
        t = self.report_text
        
        # Display import report
        if 'import' in report:
            self.display_import_report(report['import'])
        
        # Display export report
        t.insert(tk.END, "\n\n")
        if 'export' in report:
            self.display_export_report(report['export'])
        
        # Display comparison
        if report.get('comparison'):
            t.insert(tk.END, "\n\n" + "=" * 80 + "\n")
            t.insert(tk.END, "📊 IMPORT vs EXPORT COMPARISON\n")
            t.insert(tk.END, "=" * 80 + "\n\n")
            
            comparison = report['comparison']
            
            # Header
            t.insert(tk.END, f"{'Entity Type':<20} {'Imported':>12} {'Exported':>12} {'Pending':>12}\n")
            t.insert(tk.END, "-" * 60 + "\n")
            
            # Data rows
            for entity_type, data in comparison.items():
                entity_name = entity_type.replace('_', ' ').title()
                t.insert(tk.END, f"{entity_name:<20} {data['imported']:>12} {data['exported']:>12} {data['pending']:>12}\n")
            
            # Calculate completion percentage
            total_imported = sum(d['imported'] for d in comparison.values())
            total_exported = sum(d['exported'] for d in comparison.values())
            
            if total_imported > 0:
                completion = (total_exported / total_imported) * 100
                t.insert(tk.END, "\n" + "-" * 60 + "\n")
                t.insert(tk.END, f"Overall Migration Completion: {completion:.1f}%\n")
            
            t.insert(tk.END, "=" * 80 + "\n")
    
    def save_report_to_file(self):
        """Save current report to JSON file"""
        if self.current_report is None:
            messagebox.showwarning("No Report", "Please generate a report first")
            return
        
        try:
            from report_generator import MigrationReporter
            reporter = MigrationReporter()
            filename = reporter.save_report_to_file(self.current_report)
            messagebox.showinfo("Success", f"Report saved to: {filename}")
            self.report_status.config(text=f"Report saved to: {filename}")
        except Exception as e:
            messagebox.showerror("Error", f"Failed to save report: {e}")
    
    # ========================================================================
    # DATABASE VIEWER TAB
    # ========================================================================
    
    def create_viewer_tab(self):
        """Create the database viewer tab"""
        viewer_frame = ttk.Frame(self.notebook)
        self.notebook.add(viewer_frame, text="Database Viewer")
        
        # Title
        title = ttk.Label(viewer_frame, text="SQLite Database Viewer", 
                         font=("Arial", 16, "bold"))
        title.pack(pady=10)
        
        # Control frame
        control_frame = ttk.Frame(viewer_frame)
        control_frame.pack(fill=tk.X, padx=10, pady=5)
        
        ttk.Label(control_frame, text="Select Table:").pack(side=tk.LEFT, padx=5)
        
        self.table_var = tk.StringVar()
        self.table_combo = ttk.Combobox(control_frame, textvariable=self.table_var, 
                                        width=30, state="readonly")
        self.table_combo.pack(side=tk.LEFT, padx=5)
        self.table_combo.bind("<<ComboboxSelected>>", self.load_table_data)
        
        ttk.Button(control_frame, text="Refresh Tables", 
                  command=self.load_tables).pack(side=tk.LEFT, padx=5)
        
        ttk.Button(control_frame, text="Export to CSV", 
                  command=self.export_to_csv).pack(side=tk.LEFT, padx=5)
        
        # Info label
        self.info_label = ttk.Label(viewer_frame, text="No table selected", 
                                    font=("Arial", 10))
        self.info_label.pack(pady=5)
        
        # Treeview frame with scrollbars
        tree_frame = ttk.Frame(viewer_frame)
        tree_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=5)
        
        # Scrollbars
        v_scrollbar = ttk.Scrollbar(tree_frame, orient=tk.VERTICAL)
        v_scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        
        h_scrollbar = ttk.Scrollbar(tree_frame, orient=tk.HORIZONTAL)
        h_scrollbar.pack(side=tk.BOTTOM, fill=tk.X)
        
        # Treeview
        self.tree = ttk.Treeview(tree_frame, 
                                yscrollcommand=v_scrollbar.set,
                                xscrollcommand=h_scrollbar.set)
        self.tree.pack(fill=tk.BOTH, expand=True)
        
        v_scrollbar.config(command=self.tree.yview)
        h_scrollbar.config(command=self.tree.xview)
        
        # Load initial tables
        self.load_tables()
    
    def load_tables(self):
        """Load available tables from database"""
        try:
            conn = sqlite3.connect('testrail.db')
            cursor = conn.cursor()
            cursor.execute("SELECT name FROM sqlite_master WHERE type='table' ORDER BY name")
            tables = [row[0] for row in cursor.fetchall()]
            conn.close()
            
            self.table_combo['values'] = tables
            if tables:
                self.table_combo.current(0)
                self.load_table_data()
        except Exception as e:
            messagebox.showerror("Database Error", f"Failed to load tables: {e}")
    
    def load_table_data(self, event=None):
        """Load data from selected table"""
        table_name = self.table_var.get()
        if not table_name:
            return
        
        try:
            conn = sqlite3.connect('testrail.db')
            cursor = conn.cursor()
            
            # Get column names
            cursor.execute(f"PRAGMA table_info({table_name})")
            columns = [row[1] for row in cursor.fetchall()]
            
            # Get data
            cursor.execute(f"SELECT * FROM {table_name} LIMIT 1000")
            rows = cursor.fetchall()
            
            conn.close()
            
            # Clear existing data
            self.tree.delete(*self.tree.get_children())
            
            # Configure columns
            self.tree['columns'] = columns
            self.tree['show'] = 'headings'
            
            for col in columns:
                self.tree.heading(col, text=col)
                self.tree.column(col, width=150)
            
            # Insert data
            for row in rows:
                # Convert None to empty string for display
                display_row = ['' if val is None else str(val) for val in row]
                self.tree.insert('', tk.END, values=display_row)
            
            # Update info
            self.info_label.config(text=f"Table: {table_name} | Rows: {len(rows)} | Columns: {len(columns)}")
            
        except Exception as e:
            messagebox.showerror("Error", f"Failed to load table data: {e}")
    
    def export_to_csv(self):
        """Export current table to CSV"""
        table_name = self.table_var.get()
        if not table_name:
            messagebox.showwarning("Warning", "Please select a table first!")
            return
        
        try:
            import csv
            conn = sqlite3.connect('testrail.db')
            cursor = conn.cursor()
            
            # Get data
            cursor.execute(f"SELECT * FROM {table_name}")
            rows = cursor.fetchall()
            
            # Get column names
            columns = [desc[0] for desc in cursor.description]
            
            conn.close()
            
            # Write to CSV
            filename = f"{table_name}_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv"
            with open(filename, 'w', newline='', encoding='utf-8') as f:
                writer = csv.writer(f)
                writer.writerow(columns)
                writer.writerows(rows)
            
            messagebox.showinfo("Success", f"Data exported to {filename}")
            
        except Exception as e:
            messagebox.showerror("Error", f"Failed to export data: {e}")
    
    # ========================================================================
    # CONFIG TAB
    # ========================================================================
    
    def create_config_tab(self):
        """Create configuration tab"""
        config_frame = ttk.Frame(self.notebook)
        self.notebook.add(config_frame, text="Configuration")
        
        # Title
        title = ttk.Label(config_frame, text="Configuration Settings", 
                         font=("Arial", 16, "bold"))
        title.pack(pady=10)
        
        # Create scrollable frame
        canvas = tk.Canvas(config_frame)
        scrollbar = ttk.Scrollbar(config_frame, orient="vertical", command=canvas.yview)
        scrollable_frame = ttk.Frame(canvas)
        
        scrollable_frame.bind(
            "<Configure>",
            lambda e: canvas.configure(scrollregion=canvas.bbox("all"))
        )
        
        canvas.create_window((0, 0), window=scrollable_frame, anchor="nw")
        canvas.configure(yscrollcommand=scrollbar.set)
        
        # TestRail Configuration
        tr_frame = ttk.LabelFrame(scrollable_frame, text="TestRail Configuration", padding=15)
        tr_frame.pack(fill=tk.X, padx=20, pady=10)
        
        ttk.Label(tr_frame, text="TestRail URL:").grid(row=0, column=0, sticky=tk.W, pady=5)
        self.tr_url = ttk.Entry(tr_frame, width=50)
        self.tr_url.grid(row=0, column=1, pady=5, padx=5)
        self.tr_url.insert(0, self.config.get('testrail_url', ''))
        
        ttk.Label(tr_frame, text="TestRail User:").grid(row=1, column=0, sticky=tk.W, pady=5)
        self.tr_user = ttk.Entry(tr_frame, width=50)
        self.tr_user.grid(row=1, column=1, pady=5, padx=5)
        self.tr_user.insert(0, self.config.get('testrail_user', ''))
        
        ttk.Label(tr_frame, text="TestRail Password:").grid(row=2, column=0, sticky=tk.W, pady=5)
        self.tr_password = ttk.Entry(tr_frame, width=50, show="*")
        self.tr_password.grid(row=2, column=1, pady=5, padx=5)
        self.tr_password.insert(0, self.config.get('testrail_password', ''))
        
        # Jira/Xray Configuration
        jira_frame = ttk.LabelFrame(scrollable_frame, text="Jira/Xray Configuration", padding=15)
        jira_frame.pack(fill=tk.X, padx=20, pady=10)
        
        ttk.Label(jira_frame, text="Jira URL:").grid(row=0, column=0, sticky=tk.W, pady=5)
        self.jira_url = ttk.Entry(jira_frame, width=50)
        self.jira_url.grid(row=0, column=1, pady=5, padx=5)
        self.jira_url.insert(0, self.config.get('jira_url', ''))
        
        ttk.Label(jira_frame, text="Jira Username:").grid(row=1, column=0, sticky=tk.W, pady=5)
        self.jira_username = ttk.Entry(jira_frame, width=50)
        self.jira_username.grid(row=1, column=1, pady=5, padx=5)
        self.jira_username.insert(0, self.config.get('jira_username', ''))
        
        ttk.Label(jira_frame, text="Jira Password/Token:").grid(row=2, column=0, sticky=tk.W, pady=5)
        self.jira_password = ttk.Entry(jira_frame, width=50, show="*")
        self.jira_password.grid(row=2, column=1, pady=5, padx=5)
        self.jira_password.insert(0, self.config.get('jira_password', ''))
        
        ttk.Label(jira_frame, text="Jira Project Key:").grid(row=3, column=0, sticky=tk.W, pady=5)
        self.jira_project = ttk.Entry(jira_frame, width=50)
        self.jira_project.grid(row=3, column=1, pady=5, padx=5)
        self.jira_project.insert(0, self.config.get('jira_project_key', ''))
        
        # Buttons
        button_frame = ttk.Frame(scrollable_frame)
        button_frame.pack(pady=20)
        
        ttk.Button(button_frame, text="Save Configuration", 
                  command=self.save_configuration, style="Accent.TButton").pack(side=tk.LEFT, padx=5)
        ttk.Button(button_frame, text="Test TestRail Connection", 
                  command=self.test_testrail_connection).pack(side=tk.LEFT, padx=5)
        ttk.Button(button_frame, text="Test Jira Connection", 
                  command=self.test_jira_connection).pack(side=tk.LEFT, padx=5)
        
        canvas.pack(side="left", fill="both", expand=True)
        scrollbar.pack(side="right", fill="y")
    
    def save_configuration(self):
        """Save configuration from UI to config.json"""
        self.config['testrail_url'] = self.tr_url.get()
        self.config['testrail_user'] = self.tr_user.get()
        self.config['testrail_password'] = self.tr_password.get()
        self.config['jira_url'] = self.jira_url.get()
        self.config['jira_username'] = self.jira_username.get()
        self.config['jira_password'] = self.jira_password.get()
        self.config['jira_project_key'] = self.jira_project.get()
        
        self.save_config()
    
    def test_testrail_connection(self):
        """Test TestRail connection"""
        try:
            from testrail import APIClient
            client = APIClient(self.tr_url.get())
            client.user = self.tr_user.get()
            client.password = self.tr_password.get()
            
            # Try to get projects
            projects = client.send_get('get_projects')
            messagebox.showinfo("Success", 
                              f"Connected successfully!\nFound {len(projects.get('projects', []))} project(s)")
        except Exception as e:
            messagebox.showerror("Connection Failed", f"Failed to connect to TestRail:\n{e}")
    
    def test_jira_connection(self):
        """Test Jira connection"""
        try:
            client = migrator.JiraXrayClient(
                self.jira_url.get(),
                self.jira_username.get(),
                self.jira_password.get()
            )
            project = client.get_project(self.jira_project.get())
            messagebox.showinfo("Success", 
                              f"Connected successfully!\nProject: {project['name']}")
        except Exception as e:
            messagebox.showerror("Connection Failed", f"Failed to connect to Jira:\n{e}")
    
    def on_closing(self):
        """Handle window close event"""
        if messagebox.askokcancel("Quit", "Do you want to quit?"):
            self.root.destroy()
            sys.exit(0)
    
    def on_tab_changed(self, event):
        """Handle tab change event to update project labels"""
        current_tab = self.notebook.index(self.notebook.select())
        
        # Update labels when switching to Import tab (tab 1), Export tab (tab 2), or Reports tab (tab 3)
        if current_tab == 1:  # Import tab
            self.update_import_project_labels()
        elif current_tab == 2:  # Export tab
            self.update_export_project_labels()
        elif current_tab == 3:  # Reports tab
            self.update_reports_project_label()
    
    def update_import_project_labels(self):
        """Update the project selection labels in the Import tab"""
        migration_config = self.load_migration_config()
        
        if migration_config:
            self.import_testrail_label.config(
                text=f"✓ TestRail Project: {migration_config.get('testrail_project_name')} (ID: {migration_config.get('testrail_project_id')})",
                foreground="green"
            )
            self.import_jira_label.config(
                text=f"✓ Jira Project: {migration_config.get('jira_project_name')} ({migration_config.get('jira_project_key')})",
                foreground="green"
            )
            self.import_warning_label.config(text="")
        else:
            self.import_testrail_label.config(text="")
            self.import_jira_label.config(text="")
            self.import_warning_label.config(
                text="⚠ No project selection found! Please go to 'Select Projects' tab first.",
                foreground="orange"
            )
    
    def update_export_project_labels(self):
        """Update the project selection labels in the Export tab"""
        migration_config = self.load_migration_config()
        
        if migration_config:
            self.export_testrail_label.config(
                text=f"✓ TestRail Project: {migration_config.get('testrail_project_name')} (ID: {migration_config.get('testrail_project_id')})",
                foreground="green"
            )
            self.export_jira_label.config(
                text=f"✓ Jira Project: {migration_config.get('jira_project_name')} ({migration_config.get('jira_project_key')})",
                foreground="green"
            )
            self.export_warning_label.config(text="")
        else:
            self.export_testrail_label.config(text="")
            self.export_jira_label.config(text="")
            self.export_warning_label.config(
                text="⚠ No project selection found! Please go to 'Select Projects' tab first.",
                foreground="orange"
            )
    
    def update_reports_project_label(self):
        """Update the project selection label in the Reports tab"""
        migration_config = self.load_migration_config()
        
        if migration_config:
            self.reports_project_label.config(
                text=f"📊 Reports filtered for: TestRail Project '{migration_config.get('testrail_project_name')}' (ID: {migration_config.get('testrail_project_id')}) → Jira Project '{migration_config.get('jira_project_name')}' ({migration_config.get('jira_project_key')})",
                foreground="green"
            )
        else:
            self.reports_project_label.config(
                text="⚠ No project selected - Reports will show data from all projects",
                foreground="orange"
            )


def main():
    root = tk.Tk()
    app = TestRailMigratorUI(root)
    root.mainloop()


if __name__ == "__main__":
    main()
