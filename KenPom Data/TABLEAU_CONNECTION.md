# Connecting KenPom Data to Tableau

This guide provides multiple methods to connect your KenPom SQLite database to Tableau.

## Method 1: Export to CSV/Excel (Easiest - Recommended)

### Step 1: Export the Data

Run the export script to create Tableau-ready files:

```powershell
# Activate your virtual environment first
.\activate.ps1

# Export to CSV (default)
python export_to_tableau.py csv

# Or export to Excel with multiple sheets
python export_to_tableau.py excel

# Or export only latest rankings
python export_to_tableau.py latest
```

This will create:
- `kenpom_tableau.csv` - All historical rankings data
- `kenpom_tableau.xlsx` - Excel file with multiple sheets
- `kenpom_latest.csv` - Only the most recent rankings

### Step 2: Import into Tableau

1. Open Tableau Desktop
2. Click "Connect" → "Text file" (for CSV) or "Microsoft Excel" (for Excel)
3. Navigate to and select your exported file
4. Drag the data source to the canvas
5. Start building your visualizations!

**Advantages:**
- ✅ Simple and straightforward
- ✅ Works with all Tableau versions
- ✅ No additional drivers needed
- ✅ Easy to refresh (just re-export)

**Disadvantages:**
- ❌ Manual refresh required
- ❌ Not real-time

---

## Method 2: Direct SQLite Connection (Advanced)

Tableau can connect directly to SQLite databases, but requires an ODBC driver.

### Step 1: Install SQLite ODBC Driver

**Option A: SQLite ODBC Driver (Recommended)**
1. Download from: http://www.ch-werner.de/sqliteodbc/
2. Install the appropriate version (32-bit or 64-bit) matching your Tableau installation
3. Restart Tableau

**Option B: Use Tableau's Built-in Connector (Tableau 2020.2+)**
- Tableau Desktop 2020.2+ includes native SQLite support
- No additional driver needed!

### Step 2: Connect in Tableau

1. Open Tableau Desktop
2. Click "Connect" → "More..." → "SQLite"
   - If SQLite isn't listed, use "Other Databases (ODBC)" and select your SQLite DSN
3. Navigate to your database file: `kenpom_data.db`
4. Select the tables you want to use:
   - `rankings` - Historical ranking data
   - `teams` - Team information
   - `games` - Game data (if available)

### Step 3: Create Relationships

In Tableau, create relationships between tables:
- `rankings.team_id` → `teams.id`
- `games.team_id` → `teams.id` (if using games table)

**Advantages:**
- ✅ Direct database connection
- ✅ Can write custom SQL queries
- ✅ More flexible for complex analysis

**Disadvantages:**
- ❌ Requires ODBC driver (unless using Tableau 2020.2+)
- ❌ May need to set up DSN on some systems

---

## Method 3: Tableau Python Integration (For Live Updates)

If you want to automate data refresh, you can use Tableau's Python integration.

### Step 1: Set Up Python in Tableau

1. In Tableau, go to Help → Settings and Performance → Manage External Service Connection
2. Configure Python connection (if available in your Tableau version)

### Step 2: Use Tableau Prep or Tableau Desktop with Python

You can create a script that runs your scraper and exports data automatically.

**Advantages:**
- ✅ Can automate data refresh
- ✅ Integrates with your existing Python workflow

**Disadvantages:**
- ❌ More complex setup
- ❌ Requires Tableau Prep or specific Tableau versions

---

## Recommended Data Model for Tableau

### Primary Table: Rankings (Time Series)
- **Date** - Date dimension
- **Team Name** - Dimension
- **Conference** - Dimension
- **Rank** - Measure
- **AdjEM** - Measure (Adjusted Efficiency Margin)
- **AdjO** - Measure (Adjusted Offense)
- **AdjD** - Measure (Adjusted Defense)
- **AdjTempo** - Measure
- **Luck** - Measure
- **SOS AdjEM** - Measure (Strength of Schedule)

### Suggested Visualizations

1. **Rankings Over Time**
   - X-axis: Date
   - Y-axis: Rank
   - Color: Team or Conference
   - Filter: Top N teams

2. **Efficiency Scatter Plot**
   - X-axis: AdjO (Offense)
   - Y-axis: AdjD (Defense)
   - Size: AdjEM
   - Color: Conference

3. **Conference Comparison**
   - Bar chart: Average AdjEM by Conference
   - Box plot: AdjEM distribution by Conference

4. **Team Performance Dashboard**
   - Time series of key metrics
   - Current rank
   - Trend indicators

---

## Refreshing Data

### Option 1: Automated Scrape + Export (Recommended)

Use the combined script that scrapes AND exports in one step:

```powershell
# Scrape and export to CSV automatically
python scrape_and_export.py csv

# Or for Excel
python scrape_and_export.py excel
```

Then in Tableau: **Data → Refresh**

### Option 2: Manual Two-Step Process

1. Run the scraper: `python main.py`
2. Export again: `python export_to_tableau.py csv`
3. In Tableau: **Data → Refresh**

### Option 3: Automated Daily Updates

Set up the scheduler to automatically scrape and export daily:

```powershell
# This will scrape and export automatically every day at 2:00 AM
python scheduler.py
```

The scheduler now includes automatic export, so your CSV will be updated daily!

### Option 4: Direct SQLite Connection (Auto-updates on Refresh)

If you connect Tableau directly to the SQLite database:
1. Run the scraper: `python main.py` (updates the database)
2. In Tableau: **Data → Refresh** (reads fresh data from database)

This method doesn't require re-exporting - the database is the source of truth.

---

## Troubleshooting

### "SQLite driver not found"
- Install SQLite ODBC driver (see Method 2)
- Or use CSV/Excel export method instead

### "Cannot connect to database"
- Check that `kenpom_data.db` exists in the project directory
- Verify file permissions
- Try using absolute path in Tableau connection

### "Data not updating"
- Make sure you're running the scraper to update the database
- For CSV/Excel: re-export after scraping
- For direct connection: refresh the data source in Tableau

---

## Next Steps

1. **Export your data** using `export_to_tableau.py`
2. **Open Tableau** and connect to the exported file
3. **Explore the data** and create visualizations
4. **Set up daily refresh** by running the scraper on a schedule

For questions or issues, check the main README.md file.

