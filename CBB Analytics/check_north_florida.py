import pandas as pd

df = pd.read_csv('cbb_analytics_tableau_cleaned.csv')
nf = df[df['team_kenpom'].str.contains('North Florida', na=False)]

print('Team:', nf['team_kenpom'].values[0])
print('\nAll columns with values around 30.4:')

for col in df.columns:
    val = nf[col].values[0]
    if isinstance(val, (int, float)) and 29 < val < 32:
        print(f'{col}: {val}')

print('\nAll columns with "DR" in name:')
for col in [c for c in df.columns if 'DR' in c or 'Dr' in c]:
    val = nf[col].values[0]
    print(f'{col}: {val}')
