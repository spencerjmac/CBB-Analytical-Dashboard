# College Basketball Analytics - Tableau Final Project

A comprehensive data collection system for college basketball analytics, aggregating data from multiple sources (KenPom, Evan Miya, Bart Torvik, ESPN AP Poll) for Tableau visualization and analysis.

## 📊 Project Overview

This project scrapes and normalizes NCAA Division I men's basketball data from four major sources:

- **KenPom** - Adjusted efficiency metrics, tempo, luck ratings
- **Evan Miya** - Advanced team ratings and performance metrics
- **Bart Torvik (T-Rank)** - Four Factors analysis and comprehensive statistics
- **ESPN AP Poll** - Weekly Associated Press rankings

All data sources provide metrics for **365 NCAA Division I teams** with normalized team names for seamless cross-dataset analysis in Tableau.

## 🚀 Quick Start

### Prerequisites

- **Python 3.14.0** (or compatible version)
- **Virtual environment** (shared across all scrapers)
- **Playwright** for browser automation

### Initial Setup

1. **Activate the virtual environment:**
   ```powershell
   .\.venv\Scripts\Activate.ps1
   ```

2. **Install dependencies (if needed):**
   ```powershell
   pip install playwright beautifulsoup4 pandas
   playwright install chromium
   ```

### Running the Scrapers

**Update all data sources for Tableau:**

```powershell
# KenPom Data
cd "KenPom Data"
python main.py
python export_to_tableau.py

# Evan Miya
cd "..\Evan Miya\scraper"
python scrape_team_ratings.py

# Bart Torvik (may timeout occasionally)
cd "..\..\Bart Torvik"
python export_to_tableau.py
```

## 📁 Project Structure

```
Tableau Final Project/
├── README.md                          # This file
├── .venv/                            # Shared Python virtual environment
│
├── KenPom Data/                      # KenPom.com scraper
│   ├── main.py                       # Main scraper (Playwright)
│   ├── scraper_playwright.py        # Browser automation scraper
│   ├── export_to_tableau.py         # Export to kenpom_tableau.csv
│   ├── database.py                   # SQLite database operations
│   ├── kenpom_data.db               # SQLite database
│   ├── kenpom_tableau.csv           # Tableau-ready CSV export
│   └── README.md                     # Detailed KenPom documentation
│
├── Evan Miya/                        # evanmiya.com scraper
│   └── scraper/
│       ├── scrape_team_ratings.py   # Main scraper (Playwright)
│       ├── team_ratings.csv         # Tableau-ready CSV export
│       ├── team_ratings.db          # SQLite database
│       └── README.md                 # Detailed Evan Miya documentation
│
├── Bart Torvik/                      # barttorvik.com scraper
│   ├── scraper_torvik.py            # Browser automation scraper
│   ├── export_to_tableau.py         # Scrape & export to torvik_tableau.csv
│   └── torvik_tableau.csv           # Tableau-ready CSV export
│
└── ESPN AP Poll/                     # ESPN AP Poll scraper
    ├── scrape_ap_poll.py            # AP Poll Week 6 scraper
    └── ap_poll_week6.csv            # Tableau-ready CSV export
```

## 📊 Data Sources

### KenPom (kenpom.com)
**Status:** ✅ Working consistently  
**Teams:** 365  
**Update Frequency:** Daily  
**Key Metrics:**
- Adjusted Efficiency Margin (AdjEM)
- Adjusted Offense (AdjO) / Defense (AdjD)
- Adjusted Tempo (AdjT)
- Luck rating
- Strength of Schedule (SOS)

**Export:** `KenPom Data/kenpom_tableau.csv`

### Evan Miya (evanmiya.com)
**Status:** ✅ Working consistently  
**Teams:** 365  
**Update Frequency:** Daily  
**Key Metrics:**
- Overall team ratings
- Advanced efficiency metrics
- Offensive/defensive ratings

**Export:** `Evan Miya/scraper/team_ratings.csv`

### Bart Torvik (barttorvik.com)
**Status:** ✅ Working reliably  
**Teams:** 365  
**Update Frequency:** Daily  
**Key Metrics:**
- Four Factors (eFG%, TOV%, ORB%, FTRate)
- Barthag rating
- Adjusted efficiency metrics
- 25+ statistical categories

**Export:** `Bart Torvik/torvik_tableau.csv`

### ESPN AP Poll
**Status:** ✅ One-time scrape  
**Teams:** 25 (ranked teams only)  
**Update Frequency:** Manual (by week)  
**Key Metrics:**
- AP Poll rank
- Poll points
- Previous rank
- Team record

**Export:** `ESPN AP Poll/ap_poll_week6.csv`

## 🔗 Team Name Normalization

All scrapers normalize team names for **100% compatibility** across datasets:

| Source Name | Normalized Name |
|-------------|-----------------|
| Iowa State | Iowa St. |
| UConn | Connecticut |
| Michigan State | Michigan St. |
| UMKC | Kansas City |
| SIUE | SIU Edwardsville |
| NC State | North Carolina St. |
| VCU | Virginia Commonwealth |
| USC | Southern California |

This ensures seamless joins and relationships in Tableau across all 365 teams.

## 📈 Tableau Integration

### Connecting Data Sources

1. **Open Tableau Desktop**
2. **Connect → Text file**
3. **Load each CSV:**
   - `KenPom Data/kenpom_tableau.csv`
   - `Evan Miya/scraper/team_ratings.csv`
   - `Bart Torvik/torvik_tableau.csv`
   - `ESPN AP Poll/ap_poll_week6.csv`

4. **Create relationships:**
   - Join on `team_name` field (or equivalent)
   - All team names are normalized for compatibility

5. **Refresh data:**
   - Data → Refresh All Extracts
   - Or right-click data source → Refresh

### Recommended Visualizations

- **Efficiency Analysis:** AdjEM vs SOS scatter plots
- **Four Factors:** eFG%, TOV%, ORB%, FTRate comparisons
- **Tempo Analysis:** Adjusted tempo vs offensive/defensive efficiency
- **Poll Tracking:** AP Poll rankings over time
- **Conference Comparisons:** Aggregate metrics by conference
- **Team Dashboards:** Multi-metric team cards with normalized names

## 🔧 Technical Details

### Browser Automation (Playwright)

All scrapers use Playwright for browser automation to handle:
- JavaScript-rendered content
- Dynamic page loading
- Anti-scraping protections (403 Forbidden errors)
- Multi-section tables (10 tbody elements)

### Database Storage

- **SQLite databases** for historical data persistence
- **CSV exports** optimized for Tableau consumption
- **Timestamp tracking** for data versioning

### Error Handling

- **Timeouts:** 90-second page loads, 60-second element waits
- **Retry logic:** Automatic retries on intermittent failures
- **Fallback data:** Last successful scrape retained on timeout

## 🐛 Known Issues

1. **Bart Torvik Timeouts:**
   - Site occasionally unresponsive (timeout issues on ~30% of attempts)
   - Last successful data is retained in CSV when scraping fails
   - Typically resolves within 24-48 hours

2. **Excel Export (KenPom):**
   - Excel export has undefined variable error
   - CSV export works perfectly (recommended for Tableau)

3. **Rate Limiting:**
   - Avoid running scrapers more than once per day
   - Excessive requests may trigger temporary blocks

## 📅 Update Schedule

**Recommended:** Run scrapers once daily

```powershell
# Daily update script (run all scrapers)
cd "c:\Users\spenc\OneDrive\Workspace\Tableau Final Project"
.\.venv\Scripts\Activate.ps1

# KenPom
cd "KenPom Data"; python main.py; python export_to_tableau.py

# Evan Miya
cd "..\Evan Miya\scraper"; python scrape_team_ratings.py

# Bart Torvik (may timeout)
cd "..\..\Bart Torvik"; python export_to_tableau.py
```

## 🎓 Use Cases

- **Team Performance Analysis:** Compare efficiency metrics across sources
- **Recruiting Analytics:** Identify undervalued programs
- **Conference Strength:** Aggregate team metrics by conference
- **Tournament Predictions:** Multi-factor models using KenPom + Torvik
- **Tempo Analysis:** Pace-adjusted offensive/defensive ratings
- **Poll Movement:** Track AP Poll changes vs efficiency metrics

## 📝 Notes

- **Data Freshness:** KenPom and Evan Miya update daily; check timestamps
- **Historical Data:** Databases store historical data; CSVs contain latest snapshot
- **Team Count:** 365 teams represent all NCAA Division I programs
- **Logo Files:** Sequential numbering (001-365) for Tableau shape palettes

## 🤝 Contributing

This is a final project for Tableau analytics. Data sources are publicly available college basketball statistics.

## 📧 Support

For issues or questions about:
- **KenPom scraper:** See `KenPom Data/README.md`
- **Evan Miya scraper:** See `Evan Miya/scraper/README.md`
- **Data compatibility:** All team names normalized to KenPom standard
- **Tableau connection:** See `KenPom Data/TABLEAU_CONNECTION.md`

---

**Last Updated:** December 2025  
**Python Version:** 3.14.0  
**Key Dependencies:** Playwright, BeautifulSoup4, Pandas, SQLite3
