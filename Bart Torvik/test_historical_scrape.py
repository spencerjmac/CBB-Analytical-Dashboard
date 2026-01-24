"""
Quick test to verify historical data scraping works correctly.
"""
from scrape_historical_seasons import HistoricalSeasonScraper
import pandas as pd

scraper = HistoricalSeasonScraper()

# Test with 2008 season
print("Testing 2008 season scrape...")
teams_2008 = scraper.scrape_season(2008)

if teams_2008:
    df = pd.DataFrame(teams_2008)
    print(f"\nScraped {len(df)} teams")
    print("\nFirst 10 teams:")
    print(df[['rank', 'team_name', 'year', 'efg_pct', 'tor', 'orb', 'ftr']].head(10))
    
    # Calculate margins
    df['efg_margin'] = df['efg_pct'] - df['efg_pct_d']
    df['ftr_margin'] = df['ftr'] - df['ftrd']
    df['turnover_edge'] = df['tord'] - df['tor']
    df['rebounding_edge'] = df['orb'] - df['drb']
    
    print("\nMeans:")
    print(f"EFG Margin: {df['efg_margin'].mean():.4f}")
    print(f"FTR Margin: {df['ftr_margin'].mean():.4f}")
    print(f"Turnover Edge: {df['turnover_edge'].mean():.4f}")
    print(f"Rebounding Edge: {df['rebounding_edge'].mean():.4f}")
else:
    print("Failed to scrape data")
