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
        
        # Load configuration
        self.load_config()
        
        # Create main notebook (tabs)
        self.notebook = ttk.Notebook(root)
        self.notebook.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)
        
        # Create tabs
        self.create_import_tab()
        self.create_export_tab()
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
    # IMPORT TAB
    # ========================================================================
    
    def create_import_tab(self):
        """Create the import tab for fetching data from TestRail"""
        import_frame = ttk.Frame(self.notebook)
        self.notebook.add(import_frame, text="Import from TestRail")
        
        # Title
        title = ttk.Label(import_frame, text="Import Data from TestRail", 
                         font=("Arial", 16, "bold"))
        title.pack(pady=10)
        
        # Configuration display
        config_frame = ttk.LabelFrame(import_frame, text="Configuration", padding=10)
        config_frame.pack(fill=tk.X, padx=10, pady=5)
        
        ttk.Label(config_frame, text=f"TestRail URL: {self.config.get('testrail_url', 'Not set')}").pack(anchor=tk.W)
        ttk.Label(config_frame, text=f"TestRail User: {self.config.get('testrail_user', 'Not set')}").pack(anchor=tk.W)
        ttk.Label(config_frame, text="TestRail Password: ********" if self.config.get('testrail_password') else "Not set").pack(anchor=tk.W)
        
        # Instructions
        instructions = ttk.LabelFrame(import_frame, text="Instructions", padding=10)
        instructions.pack(fill=tk.X, padx=10, pady=5)
        ttk.Label(instructions, text="1. Ensure your TestRail credentials are configured in the Config tab\n"
                                    "2. Click 'Start Import' to fetch all data from TestRail\n"
                                    "3. Data will be stored in 'testrail.db' SQLite database\n"
                                    "4. Monitor the progress in the console below",
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
        self.notebook.add(export_frame, text="Export to Xray")
        
        # Title
        title = ttk.Label(export_frame, text="Export Data to Xray (Jira)", 
                         font=("Arial", 16, "bold"))
        title.pack(pady=10)
        
        # Configuration display
        config_frame = ttk.LabelFrame(export_frame, text="Configuration", padding=10)
        config_frame.pack(fill=tk.X, padx=10, pady=5)
        
        ttk.Label(config_frame, text=f"Jira URL: {self.config.get('jira_url', 'Not set')}").pack(anchor=tk.W)
        ttk.Label(config_frame, text=f"Jira Username: {self.config.get('jira_username', 'Not set')}").pack(anchor=tk.W)
        ttk.Label(config_frame, text=f"Jira Project: {self.config.get('jira_project_key', 'Not set')}").pack(anchor=tk.W)
        
        # Instructions
        instructions = ttk.LabelFrame(export_frame, text="Instructions", padding=10)
        instructions.pack(fill=tk.X, padx=10, pady=5)
        ttk.Label(instructions, text="1. Ensure you have imported TestRail data first\n"
                                    "2. Configure Jira/Xray credentials in the Config tab\n"
                                    "3. Click 'Start Export' to migrate data to Xray\n"
                                    "4. The process creates Tests, Test Sets, and Test Executions\n"
                                    "5. Monitor progress in the console below",
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


def main():
    root = tk.Tk()
    app = TestRailMigratorUI(root)
    root.mainloop()


if __name__ == "__main__":
    main()
