# Bart Torvik College Basketball Data Scraper

This directory contains a Playwright-based web scraper for BartTorvik.com (T-Rank) college basketball ratings and statistics.

## Files

- **scraper_torvik.py**: Main scraper using Playwright browser automation to extract T-Rank data
- **export_to_tableau.py**: Export script that normalizes team names to match KenPom format and creates Tableau-ready CSV
- **torvik_tableau.csv**: Latest scraped data in Tableau format

## Features

- **Browser Automation**: Uses Playwright to bypass anti-scraping protections
- **Comprehensive Stats**: Scrapes 365 D-I teams with 25+ metrics including:
  - Adjusted Offensive/Defensive Efficiency (AdjOE, AdjDE)
  - Barthag (win probability rating)
  - Four Factors: eFG%, TO%, ORB%, FTR (and defensive versions)
  - Shooting percentages: 2P%, 3P%, 3P Rate
  - Tempo and WAB (Wins Above Bubble)
- **Team Name Normalization**: 100% compatibility with KenPom team naming conventions
- **Tableau-Ready**: CSV includes date components (year, month, day) and normalized team names

## Usage

### Scrape and Export to CSV

```powershell
python export_to_tableau.py
```

This will:
1. Launch headless browser and scrape BartTorvik.com
2. Extract all 365 teams with full statistics
3. Normalize team names to match KenPom format
4. Export to `torvik_tableau.csv`

### Test Scraper Only

```powershell
python scraper_torvik.py
```

## Data Dictionary

| Column | Description |
|--------|-------------|
| `date` | Scrape date (YYYY-MM-DD) |
| `rank` | T-Rank ranking (1-365) |
| `team_name` | Original Bart Torvik team name |
| `team_name_normalized` | Team name normalized to match KenPom |
| `conference` | Conference abbreviation |
| `games` | Games played |
| `record` | Win-loss record |
| `adj_oe` | Adjusted Offensive Efficiency |
| `adj_de` | Adjusted Defensive Efficiency |
| `barthag` | Barthag rating (win probability vs average team) |
| `adj_tempo` | Adjusted Tempo (possessions per 40 min) |
| `wab` | Wins Above Bubble |
| `efg_pct` | Effective Field Goal % |
| `efg_pct_d` | Effective Field Goal % Defense |
| `tor` | Turnover Rate |
| `tord` | Turnover Rate Defense |
| `orb` | Offensive Rebound % |
| `drb` | Defensive Rebound % |
| `ftr` | Free Throw Rate |
| `ftrd` | Free Throw Rate Defense |
| `two_p_pct` | Two-Point % |
| `two_p_pct_d` | Two-Point % Defense |
| `three_p_pct` | Three-Point % |
| `three_p_pct_d` | Three-Point % Defense |
| `three_pr` | Three-Point Rate (% of FGA that are 3s) |
| `three_prd` | Three-Point Rate Defense |

## Team Name Normalization

The scraper includes mappings to convert Bart Torvik team names to match KenPom exactly:
- `UMKC` → `Kansas City`
- `SIU Edwardsville` → `SIUE`
- `Nicholls St.` → `Nicholls`
- `McNeese St.` → `McNeese`
- And many more...

**Result**: 365/365 teams (100%) match KenPom naming

## Requirements

- Python 3.10+
- playwright
- beautifulsoup4
- pandas

Install with:
```powershell
pip install playwright beautifulsoup4 pandas
playwright install chromium
```

## Notes

- Scraper uses headless Chromium browser
- Waits 5 seconds for JavaScript table to fully load
- Handles dynamic table with 379+ rows split across multiple tbody sections
- Removes game information from team names (e.g., "Duke(H) 16 Florida" → "Duke")
- Latest scrape: **2025-12-02** with **365 teams**

## Tableau Integration

Import `torvik_tableau.csv` directly into Tableau. The file includes:
- Date components for time-series analysis
- Normalized team names for joining with KenPom/Evan Miya data
- All tempo-free statistics and Four Factors metrics
