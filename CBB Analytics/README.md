# CBB Analytics Scraper

Comprehensive scraper for Division I college basketball statistics from cbbanalytics.com

## Features

Scrapes multiple categories of team data:
- **Team Four Factors (Adj)** - Adjusted four factors metrics
- **Traditional Shooting** - Shooting percentages and attempts
- **Traditional Boxscore** - Points, rebounds, assists, etc.
- **Boxscore Differentials** - Statistical margins
- **Advanced Offense** - Advanced offensive metrics
- **Advanced Defense** - Advanced defensive metrics
- **Foul Related** - Foul statistics
- **Scoring Context** - Scoring breakdown analysis
- **Win/Loss by Splits** - Record by various splits
- **Win/Loss by Lead/Deficit** - Performance in different game situations

## Team Name Normalization

All team names are normalized to match KenPom format for seamless integration with other data sources in Tableau.

## Authentication

CBBAnalytics.com may require a login. If so, set environment variables:

```powershell
$env:CBB_ANALYTICS_EMAIL = "your-email@example.com"
$env:CBB_ANALYTICS_PASSWORD = "your-password"
```

Or add them to a `.env` file (not recommended for security):
```
CBB_ANALYTICS_EMAIL=your-email@example.com
CBB_ANALYTICS_PASSWORD=your-password
```

## Installation

Install required packages:
```powershell
pip install playwright pandas python-dotenv
playwright install chromium
```

## Usage

Run the scraper:
```powershell
python scrape_cbb_analytics.py
```

Output: `cbb_analytics_tableau.csv` - Ready for Tableau import

## Output Format

The CSV file contains:
- All team statistics from each category
- `team_kenpom` - Normalized team name matching KenPom format
- `team_original` - Original team name from source
- `scrape_date` - Date of scrape (YYYY-MM-DD)
- `scrape_timestamp` - Full ISO timestamp
- `category` - Data category identifier

## Integration with Tableau

1. Run the scraper to generate `cbb_analytics_tableau.csv`
2. In Tableau, add this as a data source
3. Join with KenPom data using `team_kenpom` field
4. Create visualizations combining metrics from all sources

## Notes

- Respects rate limits with 2-second delays between requests
- Uses headless browser automation via Playwright
- Handles login walls gracefully
- Season ID is currently hardcoded to 41097 (2025-26 season)

## Troubleshooting

**Issue**: "Login required" message
- **Solution**: Set environment variables with valid credentials

**Issue**: No data scraped
- **Solution**: Check if site structure has changed or if account access is needed

**Issue**: Team names don't match KenPom
- **Solution**: Update `TEAM_NAME_MAPPING` dictionary in script
