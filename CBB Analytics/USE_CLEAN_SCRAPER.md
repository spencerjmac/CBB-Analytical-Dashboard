# CBB Analytics Scraper - IMPORTANT NOTE

## Use `scrape_cbb_analytics_clean.py` for all future scraping!

This file (`scrape_cbb_analytics_clean.py`) has the proper cleaning logic that:
- Removes percentile prefixes from all numeric values
- Cleans column names  
- Maps team names to KenPom format
- Exports clean, ready-to-use data for Tableau

### Command to run:
```bash
python scrape_cbb_analytics_clean.py
```

### Output:
- File: `cbb_analytics_tableau_cleaned.csv`
- 365 teams, ~165 clean columns
- All values properly cleaned (ORtg: 85-135, percentages: 0-100%)

### The scraper will:
1. Login to CBBAnalytics.com  
2. Scrape 9 statistical categories
3. Clean all percentile prefixes automatically
4. Export ready-for-Tableau CSV

---

Last updated: 2026-02-02
