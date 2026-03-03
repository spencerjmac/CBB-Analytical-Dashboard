import pandas as pd

df = pd.read_csv('torvik_historical_all_teams_with_ffi.csv')
s = df[df['year'] == 2014].copy()

# Tournament teams have seed info in team_name
tourney = s[s['team_name'].str.contains(r'\d+\s*seed', case=False, na=False)].copy()
tourney = tourney.sort_values('adj_ffi', ascending=False)

print(f"2008 NCAA Tournament Teams ({len(tourney)} teams), sorted by Adj FFI:\n")
print(f"{'#':>3}  {'Adj FFI':>8}  {'Raw FFI':>8}  Team Name")
print("-" * 90)
for i, (_, r) in enumerate(tourney.iterrows(), 1):
    print(f"{i:>3}  {r['adj_ffi']:>8.1f}  {r['raw_ffi']:>8.1f}  {r['team_name']}")
