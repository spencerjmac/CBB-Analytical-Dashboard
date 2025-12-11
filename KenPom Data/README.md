# KenPom Data Scraper

A Python project to scrape college basketball data from KenPom.com and store it in a SQLite database for analysis and visualization.

## Features

- Web scraping of KenPom.com rankings and team statistics
- SQLite database storage with structured schema
- Daily automated scraping capability
- Data viewing and querying tools

## Setup

### 1. Install UV (if not already installed)

UV is a fast Python package installer. On Windows, install it with:

```powershell
powershell -Command "irm https://astral.sh/uv/install.ps1 | iex"
```

After installation, add UV to your PATH (or restart your terminal):
```powershell
$env:Path = "C:\Users\spenc\.local\bin;$env:Path"
```

### 2. Create Virtual Environment and Install Dependencies

Using UV to create a virtual environment and install dependencies:

```powershell
# Create virtual environment
uv venv

# Install dependencies
uv pip install -r requirements.txt
```

### 3. Activate Virtual Environment

**PowerShell:**
```powershell
.\.venv\Scripts\Activate.ps1
# Or use the helper script:
.\activate.ps1
```

**Command Prompt:**
```cmd
.venv\Scripts\activate.bat
# Or use the helper script:
activate.bat
```

### 4. Run the Scraper

**Manual run (scrape only):**
```bash
python main.py
```

**Scrape AND export to Tableau (recommended):**
```bash
python scrape_and_export.py csv
```

**View stored data:**
```bash
python main.py view
```

**Set up daily scheduler (automated scrape + export):**

**Option 1: Windows Task Scheduler (Recommended - runs even when logged out):**
```powershell
# Run as Administrator
.\setup_windows_task.ps1
```

**Option 2: Python Scheduler (requires script to be running):**
```bash
python scheduler.py
```

**Check scheduler status:**
```powershell
.\check_schedule_status.ps1
```

See `SCHEDULER_SETUP.md` for detailed setup instructions.

## Project Structure

- `main.py` - Main script to run scraping and database operations
- `scraper.py` - Web scraper for KenPom.com
- `database.py` - SQLite database operations
- `scheduler.py` - Daily scheduling for automated runs
- `query_data.py` - Data query and exploration tools
- `activate.ps1` / `activate.bat` - Helper scripts to activate virtual environment
- `.venv/` - Virtual environment (created by UV)
- `kenpom_data.db` - SQLite database (created automatically)
- `requirements.txt` - Python dependencies

## Database Schema

### Teams Table
- Stores team information (name, conference)

### Rankings Table
- Daily rankings and metrics:
  - Rank
  - Adjusted Efficiency Margin (AdjEM)
  - Adjusted Offense (AdjO)
  - Adjusted Defense (AdjD)
  - Adjusted Tempo (AdjT)
  - Luck
  - Strength of Schedule metrics
  - Opponent metrics

### Games Table
- Game predictions and results (for future use)

## Usage

### Manual Scraping
Run the scraper manually to collect current data:
```bash
python main.py
```

### View Data
View the latest stored rankings:
```bash
python main.py view
```

### Daily Automation
For Windows Task Scheduler:
1. Create a task that runs daily
2. Action: Start a program
3. Program: `python`
4. Arguments: `C:\path\to\main.py`
5. Start in: `C:\path\to\project`

Or use the Python scheduler (runs continuously):
```bash
python scheduler.py
```

## Notes

- KenPom.com may have rate limiting or require authentication for some features
- The scraper includes error handling and fallback mechanisms
- Database uses SQLite for simplicity (can be migrated to other databases later)
- Data is stored with timestamps for historical analysis

## Tableau Integration

Export your data to CSV/Excel for Tableau:

```powershell
# Export to CSV (recommended for Tableau)
python export_to_tableau.py csv

# Export to Excel with multiple sheets
python export_to_tableau.py excel

# Export only latest rankings
python export_to_tableau.py latest
```

This creates Tableau-ready files:
- `kenpom_tableau.csv` - All historical data
- `kenpom_tableau.xlsx` - Excel with multiple sheets
- `kenpom_latest.csv` - Latest rankings only

**See `TABLEAU_CONNECTION.md` for detailed instructions on connecting to Tableau.**

### Quick Tableau Setup:
1. Run: `python export_to_tableau.py csv`
2. Open Tableau Desktop
3. Connect → Text file → Select `kenpom_tableau.csv`
4. Start visualizing!

## Future Enhancements

- Additional data sources
- Game-by-game data collection
- Advanced analytics and predictions

