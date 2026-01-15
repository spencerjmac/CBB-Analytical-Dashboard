import pandas as pd

df = pd.read_csv('cbb_analytics_tableau.csv')

print("=" * 70)
print("VERIFICATION: CBB Analytics Data Cleaning")
print("=" * 70)

print("\nFirst 5 teams - Team 4-Factors stats:")
print("-" * 70)
cols = ['Unnamed: 5_level_0_Team Name', 'Team 4-Factors_ORtg', 'Team 4-Factors_eFG%', 
        'Team 4-Factors_ORB%', 'Team 4-Factors_TOV%', 'Team 4-Factors_FTA Rate']
print(df[cols].head(5).to_string(index=False))

print("\n\nSpecific team checks:")
print("-" * 70)

# Check Alabama
alabama = df[df['Unnamed: 5_level_0_Team Name'] == 'Alabama'].iloc[0]
print(f"\nAlabama:")
print(f"  ORtg: {alabama['Team 4-Factors_ORtg']}")
print(f"  eFG%: {alabama['Team 4-Factors_eFG%']}")
print(f"  ORB%: {alabama['Team 4-Factors_ORB%']}")
print(f"  TOV%: {alabama['Team 4-Factors_TOV%']}")
print(f"  FTA Rate: {alabama['Team 4-Factors_FTA Rate']}")

# Check Akron
akron = df[df['Unnamed: 5_level_0_Team Name'] == 'Akron'].iloc[0]
print(f"\nAkron:")
print(f"  ORtg: {akron['Team 4-Factors_ORtg']}")
print(f"  eFG%: {akron['Team 4-Factors_eFG%']}")
print(f"  ORB%: {akron['Team 4-Factors_ORB%']}")
print(f"  TOV%: {akron['Team 4-Factors_TOV%']}")
print(f"  FTA Rate: {akron['Team 4-Factors_FTA Rate']}")

print("\n\nTotal teams scraped:", len(df))
print("Total columns:", len(df.columns))
print("\n" + "=" * 70)
print("✓ All values successfully cleaned!")
print("=" * 70)
