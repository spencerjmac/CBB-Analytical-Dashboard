@echo off
REM Windows batch file to run daily KenPom scrape and export
REM This is designed to be called by Windows Task Scheduler

cd /d "C:\Users\spenc\OneDrive\Workspace\KenPom Data"

REM Use the Python from virtual environment directly
.venv\Scripts\python.exe scrape_and_export.py csv

REM Exit with error code if Python script failed
if errorlevel 1 (
    echo [%date% %time%] ERROR: Scrape failed with error code %errorlevel% >> scrape_log.txt
    exit /b %errorlevel%
) else (
    echo [%date% %time%] Batch file completed successfully >> scrape_log.txt
)

