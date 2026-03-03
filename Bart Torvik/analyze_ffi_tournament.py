import pandas as pd
import re

df = pd.read_csv('torvik_historical_all_teams_with_ffi.csv')

# Filter to tournament teams only
tourney = df[df['team_name'].str.contains(r'\d+\s*seed', case=False, na=False)].copy()

# Parse the round reached from team_name
def parse_round(name):
    n = name.upper()
    if 'CHAMPS' in n:
        return 'Champion'
    elif 'FINALS' in n or 'FINAL,' in n:
        return 'Finals'
    elif 'FINAL FOUR' in n:
        return 'Final Four'
    elif 'ELITE' in n:
        return 'Elite Eight'
    elif 'SWEET' in n:
        return 'Sweet Sixteen'
    elif 'R32' in n:
        return 'Round of 32'
    elif 'R64' in n:
        return 'Round of 64'
    elif 'R68' in n:
        return 'First Four'
    else:
        return 'Unknown'

# Games won mapping
games_won_map = {
    'First Four': 0,    # lost in play-in (or won play-in but lost R64... treat as 0 net tourney wins)
    'Round of 64': 0,   # lost first real game
    'Round of 32': 1,
    'Sweet Sixteen': 2,
    'Elite Eight': 3,
    'Final Four': 4,
    'Finals': 5,
    'Champion': 6,
}

tourney['round'] = tourney['team_name'].apply(parse_round)
tourney['games_won'] = tourney['round'].map(games_won_map)

# Parse seed
tourney['seed'] = tourney['team_name'].str.extract(r'(\d+)\s*seed', flags=re.IGNORECASE).astype(int)

# Adj FFI buckets
def ffi_bucket(val):
    if val >= 90:
        return '90+'
    elif val >= 80:
        return '80-90'
    elif val >= 70:
        return '70-80'
    else:
        return '<70'

tourney['ffi_bucket'] = tourney['adj_ffi'].apply(ffi_bucket)

# Round order for display
round_order = ['Round of 64', 'Round of 32', 'Sweet Sixteen', 'Elite Eight', 
               'Final Four', 'Finals', 'Champion']

# For "reaching" a round, we need cumulative counts
# A champion "reached" every round. A Sweet 16 team "reached" R64, R32, and S16.
round_rank = {
    'First Four': -1,
    'Round of 64': 0,
    'Round of 32': 1,
    'Sweet Sixteen': 2,
    'Elite Eight': 3,
    'Final Four': 4,
    'Finals': 5,
    'Champion': 6,
}

tourney['round_rank'] = tourney['round'].map(round_rank)

buckets = ['90+', '80-90', '70-80', '<70']

print("=" * 90)
print("ADJ FFI TOURNAMENT ADVANCEMENT ANALYSIS (2008-2025, excl. 2020)")
print("=" * 90)

# --- SECTION 1: Bucket overview ---
print("\n--- BUCKET OVERVIEW ---\n")
print(f"{'Bucket':<10} {'Count':>6} {'Avg Adj FFI':>12} {'Avg Seed':>10} {'Avg Games Won':>15}")
print("-" * 60)
for b in buckets:
    sub = tourney[tourney['ffi_bucket'] == b]
    print(f"{b:<10} {len(sub):>6} {sub['adj_ffi'].mean():>12.1f} {sub['seed'].mean():>10.1f} {sub['games_won'].mean():>15.2f}")

total = len(tourney)
print(f"\nTotal tournament teams: {total}")

# --- SECTION 2: % that REACH each round (at least) ---
print("\n\n--- PERCENTAGE OF TEAMS THAT REACH AT LEAST EACH ROUND ---\n")

header = f"{'Round':<18}"
for b in buckets:
    header += f" {b:>10}"
header += f" {'Overall':>10}"
print(header)
print("-" * 72)

for rnd in round_order:
    rr = round_rank[rnd]
    row = f"{rnd:<18}"
    for b in buckets:
        sub = tourney[tourney['ffi_bucket'] == b]
        reached = sub[sub['round_rank'] >= rr]
        pct = len(reached) / len(sub) * 100 if len(sub) > 0 else 0
        row += f" {pct:>9.1f}%"
    # Overall
    reached_all = tourney[tourney['round_rank'] >= rr]
    pct_all = len(reached_all) / total * 100
    row += f" {pct_all:>9.1f}%"
    print(row)

# --- SECTION 3: % that are ELIMINATED at each round ---
print("\n\n--- PERCENTAGE OF TEAMS ELIMINATED AT EACH ROUND ---\n")

elim_rounds = ['First Four', 'Round of 64', 'Round of 32', 'Sweet Sixteen', 
               'Elite Eight', 'Final Four', 'Finals', 'Champion']

header = f"{'Eliminated At':<18}"
for b in buckets:
    header += f" {b:>10}"
header += f" {'Overall':>10}"
print(header)
print("-" * 72)

for rnd in elim_rounds:
    row = f"{rnd:<18}"
    for b in buckets:
        sub = tourney[tourney['ffi_bucket'] == b]
        elim = sub[sub['round'] == rnd]
        pct = len(elim) / len(sub) * 100 if len(sub) > 0 else 0
        row += f" {pct:>9.1f}%"
    elim_all = tourney[tourney['round'] == rnd]
    pct_all = len(elim_all) / total * 100
    row += f" {pct_all:>9.1f}%"
    print(row)

# --- SECTION 4: Average games won ---
print("\n\n--- AVERAGE TOURNAMENT GAMES WON BY ADJ FFI BUCKET ---\n")
print(f"{'Bucket':<10} {'N':>6} {'Avg Games':>10} {'Median':>8} {'Min':>5} {'Max':>5}")
print("-" * 50)
for b in buckets:
    sub = tourney[tourney['ffi_bucket'] == b]
    print(f"{b:<10} {len(sub):>6} {sub['games_won'].mean():>10.2f} {sub['games_won'].median():>8.1f} {sub['games_won'].min():>5} {sub['games_won'].max():>5}")

# Overall
print(f"{'ALL':<10} {total:>6} {tourney['games_won'].mean():>10.2f} {tourney['games_won'].median():>8.1f} {tourney['games_won'].min():>5} {tourney['games_won'].max():>5}")

# --- SECTION 5: Champions breakdown ---
print("\n\n--- ALL CHAMPIONS BY ADJ FFI BUCKET ---\n")
champs = tourney[tourney['round'] == 'Champion'].sort_values('adj_ffi', ascending=False)
print(f"{'Year':<6} {'Team':<30} {'Adj FFI':>8} {'Bucket':<8} {'Seed':>5}")
print("-" * 62)
for _, r in champs.iterrows():
    # Extract team base name
    name = re.sub(r'\d+\s*seed.*', '', r['team_name']).strip()
    print(f"{r['year']:<6} {name:<30} {r['adj_ffi']:>8.1f} {r['ffi_bucket']:<8} {r['seed']:>5}")

# --- SECTION 6: Final Four teams breakdown ---
print("\n\n--- FINAL FOUR TEAMS (reached at least FF) BY ADJ FFI BUCKET ---\n")
ff = tourney[tourney['round_rank'] >= 4].copy()
for b in buckets:
    sub = ff[ff['ffi_bucket'] == b]
    pct_of_ff = len(sub) / len(ff) * 100
    print(f"  {b}: {len(sub)} teams ({pct_of_ff:.1f}% of all Final Four teams)")
print(f"  Total Final Four+ teams: {len(ff)}")

# --- SECTION 7: Upset rate (seed >= 5 making S16+) by bucket ---
print("\n\n--- CINDERELLA ANALYSIS: Seeds 5+ making Sweet Sixteen or deeper ---\n")
cinderellas = tourney[(tourney['seed'] >= 5) & (tourney['round_rank'] >= 2)]
print(f"Total Cinderella runs (5+ seed, Sweet 16+): {len(cinderellas)}")
print(f"\nBy FFI bucket:")
for b in buckets:
    sub_all = tourney[(tourney['seed'] >= 5) & (tourney['ffi_bucket'] == b)]
    sub_cin = cinderellas[cinderellas['ffi_bucket'] == b]
    pct = len(sub_cin) / len(sub_all) * 100 if len(sub_all) > 0 else 0
    print(f"  {b}: {len(sub_cin)}/{len(sub_all)} ({pct:.1f}%)")
