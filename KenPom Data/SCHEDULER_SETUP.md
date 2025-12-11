# Setting Up Daily Automated Scraping

This guide explains how to set up daily automated scraping so your KenPom data updates automatically in Tableau.

## Option 1: Windows Task Scheduler (Recommended)

This method runs the scraper daily even when you're not logged in.

### Step 1: Set Up the Task

**Method A: Using PowerShell Script (Easiest)**

1. Open PowerShell as Administrator:
   - Press `Win + X`
   - Select "Windows PowerShell (Admin)" or "Terminal (Admin)"

2. Navigate to your project directory:
   ```powershell
   cd "C:\Users\spenc\OneDrive\Workspace\Tableau Final Project"
   ```

3. Run the setup script:
   ```powershell
   .\setup_windows_task.ps1
   ```

**Method B: Manual Setup**

1. Open Task Scheduler:
   - Press `Win + R`, type `taskschd.msc`, press Enter

2. Create Basic Task:
   - Click "Create Basic Task" in the right panel
   - Name: `KenPom Daily Scrape`
   - Description: `Daily KenPom data scrape and Tableau export`

3. Set Trigger:
   - Trigger: Daily
   - Start: Choose a time (e.g., 2:00 AM)
   - Recur every: 1 days

4. Set Action:
   - Action: Start a program
   - Program/script: `C:\Users\spenc\OneDrive\Workspace\Tableau Final Project\run_daily_scrape.bat`
   - Start in: `C:\Users\spenc\OneDrive\Workspace\Tableau Final Project`

5. Finish:
   - Check "Open the Properties dialog..." and click Finish
   - In Properties:
     - Check "Run whether user is logged on or not"
     - Check "Run with highest privileges"
     - Under "Conditions": Check "Start the task only if the following network connection is available"

### Step 2: Verify the Task

1. In Task Scheduler, find "KenPom Daily Scrape"
2. Right-click → Run (to test immediately)
3. Check `scrape_log.txt` to see if it ran successfully

### Step 3: Check Logs

View the log file to see when scrapes ran:
```powershell
Get-Content scrape_log.txt -Tail 20
```

Or open `scrape_log.txt` in a text editor.

## Option 2: Python Scheduler (Alternative)

If you prefer to keep a Python script running:

```powershell
python scheduler.py
```

This will:
- Run immediately on start
- Then run daily at 2:00 AM
- Keep running until you stop it (Ctrl+C)

**Note:** This requires the script to be running continuously.

## Verifying It's Working

### Check Recent Scrapes

1. **Check the log file:**
   ```powershell
   Get-Content scrape_log.txt -Tail 50
   ```

2. **Check the database:**
   ```powershell
   python verify_scraper.py
   ```

3. **Check CSV file date:**
   - Look at `kenpom_tableau.csv` file properties
   - "Date modified" should be recent

4. **In Tableau:**
   - Open your workbook
   - Data → Refresh Data Source
   - Check if you see new dates in your data

## Troubleshooting

### Task Not Running

1. **Check Task Scheduler:**
   - Open Task Scheduler
   - Find "KenPom Daily Scrape"
   - Check "Last Run Result" - should be "0x0" (success)
   - Check "Last Run Time" - should be recent

2. **Check Log File:**
   - Open `scrape_log.txt`
   - Look for error messages

3. **Test Manually:**
   ```powershell
   .\run_daily_scrape.bat
   ```

### Incorrect Values in Tableau

1. **Verify scraper is working:**
   ```powershell
   python verify_scraper.py
   ```

2. **Check if scraper code is up to date:**
   - The scraper should use correct column indices
   - AdjT should be at index 9, not 7
   - AdjD is calculated from AdjO - AdjEM

3. **Re-export manually:**
   ```powershell
   python scrape_and_export.py csv
   ```

### CSV Not Updating

1. **Check if export is running:**
   - Look in `scrape_log.txt` for export messages

2. **Check file permissions:**
   - Make sure the CSV file isn't open in another program
   - Make sure you have write permissions

3. **Manually trigger export:**
   ```powershell
   python export_to_tableau.py csv
   ```

## Manual Run

To manually run the scrape and export:

```powershell
# Activate environment
.\activate.ps1

# Run scrape and export
python scrape_and_export.py csv
```

## Schedule Times

The default is 2:00 AM. To change it:

1. Open Task Scheduler
2. Find "KenPom Daily Scrape"
3. Right-click → Properties
4. Triggers tab → Edit
5. Change the time
6. OK → OK

## Next Steps

1. Set up the Windows Task (Option 1 above)
2. Verify it runs successfully (check logs)
3. In Tableau, refresh your data source daily
4. Your visualizations will update with new data!

