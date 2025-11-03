#!/bin/bash
# Quick start script for TestRail to Xray Migrator

echo "=========================================="
echo "TestRail to Xray Migrator - GUI Launcher"
echo "=========================================="
echo ""

# Check if Python is installed
if ! command -v python3 &> /dev/null; then
    echo "Error: Python 3 is not installed!"
    echo "Please install Python 3.7 or higher"
    exit 1
fi

# Check if required files exist
if [ ! -f "ui.py" ]; then
    echo "Error: ui.py not found!"
    echo "Please run this script from the project directory"
    exit 1
fi

if [ ! -f "config.json" ]; then
    echo "Warning: config.json not found!"
    echo "Creating default config.json..."
    cat > config.json << 'EOF'
{
  "testrail_url": "",
  "testrail_user": "",
  "testrail_password": "",
  "jira_url": "",
  "jira_username": "",
  "jira_password": "",
  "jira_project_key": ""
}
EOF
    echo "✓ Default config.json created"
fi

# Launch the GUI
echo ""
echo "Launching GUI application..."
python3 ui.py

exit 0
