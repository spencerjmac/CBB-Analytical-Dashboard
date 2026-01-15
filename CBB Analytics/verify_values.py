import pandas as pd

df = pd.read_csv('cbb_analytics_tableau.csv')

# Check Alabama
alabama = df[df['Team Name'] == 'Alabama']
print('Alabama:')
print(f"  Net Rtg: {alabama['Net Rtg'].values[0]}")
print(f"  ORtg: {alabama['Team 4-Factors_ORtg'].values[0]}")

# Check Air Force
air_force = df[df['Team Name'] == 'Air Force']
print('\nAir Force:')
print(f"  Net Rtg: {air_force['Net Rtg'].values[0]}")
print(f"  ORtg: {air_force['Team 4-Factors_ORtg'].values[0]}")

# Check a few more teams
print('\n--- Sample of Net Rtg and ORtg values ---')
for i, row in df.head(15).iterrows():
    print(f"{row['Team Name']:25s} Net Rtg: {str(row['Net Rtg']):8s} ORtg: {str(row['Team 4-Factors_ORtg'])}")
