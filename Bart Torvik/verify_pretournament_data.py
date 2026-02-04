import pandas as pd

# Load the historical data
df = pd.read_csv('torvik_historical_all_teams.csv')

# Load champions data  
champs = pd.read_csv('torvik_champions.csv')

print("VERIFYING PRE-TOURNAMENT DATA")
print("="*70)
print()

# Check 2008 Kansas - should have ~30-33 games pre-tournament
print("2008 KANSAS COMPARISON:")
print("-"*70)

# From champions file (definitely pre-tournament)
kansas_champ = champs[champs['year'] == 2008].iloc[0]
print(f"Champions file (pre-tournament): {kansas_champ['games']} games")

# From historical all teams file
kansas_hist = df[(df['year'] == 2008) & (df['team_name'].str.contains('Kansas', case=False, na=False))].iloc[0]
print(f"Historical file: {kansas_hist['games']} games")
print(f"Team name: {kansas_hist['team_name']}")
print()

# Check a few more years
for year in [2012, 2019, 2021]:
    print(f"{year} CHAMPION:")
    print("-"*70)
    champ_row = champs[champs['year'] == year].iloc[0]
    champ_name = champ_row['team_name'].split('1 seed')[0].strip()
    
    print(f"Champions file: {champ_row['games']} games - {champ_row['team_name']}")
    
    # Try to find in historical data
    hist_match = df[(df['year'] == year) & (df['team_name'].str.contains(champ_name, case=False, na=False))]
    if len(hist_match) > 0:
        hist_row = hist_match.iloc[0]
        print(f"Historical file: {hist_row['games']} games - {hist_row['team_name']}")
        
        if hist_row['games'] != champ_row['games']:
            print(f"⚠️  MISMATCH! Games don't match!")
    else:
        print(f"⚠️  Could not find {champ_name} in historical data")
    print()

# Check if team names in historical data include tournament info
print("\nSAMPLE TEAM NAMES FROM HISTORICAL DATA:")
print("-"*70)
sample_2008 = df[df['year'] == 2008].head(10)
for _, row in sample_2008.iterrows():
    print(f"{row['rank']:3.0f}. {row['team_name']}")
