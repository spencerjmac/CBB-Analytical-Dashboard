import pandas as pd

df = pd.read_csv('torvik_historical_all_teams.csv')
df['efg_margin'] = df['efg_pct'] - df['efg_pct_d']

print('Checking if scraped data varies by year:')
print('='*60)

for year in [2008, 2012, 2019, 2025]:
    year_data = df[df['year']==year]
    print(f'\n{year}: {len(year_data)} teams')
    print(f'  Top team: {year_data.iloc[0]["team_name"]}')
    print(f'  Top team EFG%: {year_data.iloc[0]["efg_pct"]:.2f}')
    print(f'  EFG Margin mean: {year_data["efg_margin"].mean():.4f}')
    print(f'  EFG Margin std: {year_data["efg_margin"].std():.4f}')
