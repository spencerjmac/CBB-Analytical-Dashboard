# Quick Start Guide - Daily Automated Scraping

## ✅ Current Status

Your scraper is working correctly and getting the right values:
- ✅ Column mappings are correct (AdjT at index 9, AdjD calculated correctly)
- ✅ Data is being stored in database (3 dates: 2025-11-16, 2025-11-17, 2025-11-18)
- ✅ CSV export is working (1098 records with 3 unique dates)
- ✅ Logging is enabled (`scrape_log.txt`)

## 🚀 Set Up Daily Automation (Windows Task Scheduler)

### Quick Setup (5 minutes)

1. **Open PowerShell as Administrator:**
   - Press `Win + X`
   - Select "Windows PowerShell (Admin)" or "Terminal (Admin)"

2. **Navigate to project:**
   ```powershell
   cd "C:\Users\spenc\OneDrive\Workspace\Tableau Final Project"
   ```

3. **Run setup script:**
   ```powershell
   .\setup_windows_task.ps1
   ```

4. **Verify it's set up:**
   ```powershell
   .\check_schedule_status.ps1
   ```

That's it! The task will run daily at 2:00 AM automatically.

## 📊 Verify It's Working

### Check Logs
```powershell
Get-Content scrape_log.txt -Tail 20
```

### Check Database
```powershell
python verify_scraper.py
```

### Check CSV File
- Open `kenpom_tableau.csv` in Excel/Tableau
- Check the latest date in the data
- Should update daily

### In Tableau
1. Open your workbook
2. **Data → Refresh Data Source**
3. Check if new dates appear

## 🔧 Manual Run (If Needed)

```powershell
# Activate environment
.\activate.ps1

# Run scrape and export
python scrape_and_export.py csv
```

## ⚠️ Troubleshooting

### Task Not Running?
1. Check Task Scheduler:
   - Press `Win + R`, type `taskschd.msc`
   - Find "KenPom Daily Scrape"
   - Check "Last Run Result" (should be 0x0)
   - Right-click → Run (to test)

2. Check logs:
   ```powershell
   Get-Content scrape_log.txt -Tail 50
   ```

3. Test manually:
   ```powershell
   .\run_daily_scrape.bat
   ```

### Values Look Wrong?
1. Verify scraper:
   ```powershell
   python verify_scraper.py
   ```

2. Re-scrape manually:
   ```powershell
   python scrape_and_export.py csv
   ```

## 📝 Important Notes

- **The scraper uses correct column mappings** - AdjT is at index 9, AdjD is calculated
- **Data is stored daily** - Each scrape adds a new date to the database
- **CSV is updated automatically** - When you refresh in Tableau, you'll see new data
- **Logs are saved** - Check `scrape_log.txt` to see when scrapes ran

## 🎯 Next Steps

1. ✅ Set up Windows Task Scheduler (see above)
2. ✅ Verify it runs (check logs after first scheduled run)
3. ✅ In Tableau, refresh your data source daily
4. ✅ Your visualizations will update automatically!

For detailed instructions, see `SCHEDULER_SETUP.md`.

