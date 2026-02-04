from scrape_historical_seasons import HistoricalSeasonScraper
import pandas as pd

scraper = HistoricalSeasonScraper()

print("Testing 2021 season scrape with corrected URL...")
teams_2021 = scraper.scrape_season(2021)

if teams_2021:
    df = pd.DataFrame(teams_2021)
    print(f"\nScraped {len(df)} teams")
    
    # Find Baylor
    baylor = df[df['team_name'].str.contains('Baylor', case=False, na=False)]
    if len(baylor) > 0:
        print(f"\nBaylor found:")
        print(f"  Games: {baylor.iloc[0]['games']}")
        print(f"  Team name: {baylor.iloc[0]['team_name']}")
        print(f"  Expected: 24 games (pre-tournament)")
        
        if baylor.iloc[0]['games'] == 24:
            print("  ✅ CORRECT - Pre-tournament data!")
        else:
            print("  ❌ WRONG - Includes tournament games")
    
    print(f"\nFirst 5 teams:")
    print(df[['rank', 'team_name', 'games']].head())
