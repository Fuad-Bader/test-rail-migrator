@echo off
REM Quick start script for TestRail to Xray Migrator (Windows)

echo ==========================================
echo TestRail to Xray Migrator - GUI Launcher
echo ==========================================
echo.

REM Check if Python is installed
python --version >nul 2>&1
if errorlevel 1 (
    echo Error: Python is not installed!
    echo Please install Python 3.7 or higher
    pause
    exit /b 1
)

REM Check if required files exist
if not exist "ui.py" (
    echo Error: ui.py not found!
    echo Please run this script from the project directory
    pause
    exit /b 1
)

if not exist "config.json" (
    echo Warning: config.json not found!
    echo Creating default config.json...
    (
        echo {
        echo   "testrail_url": "",
        echo   "testrail_user": "",
        echo   "testrail_password": "",
        echo   "jira_url": "",
        echo   "jira_username": "",
        echo   "jira_password": "",
        echo   "jira_project_key": ""
        echo }
    ) > config.json
    echo Default config.json created
)

REM Launch the GUI
echo.
echo Launching GUI application...
python ui.py

pause
