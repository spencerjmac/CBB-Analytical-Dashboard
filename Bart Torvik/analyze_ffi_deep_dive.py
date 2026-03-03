import pandas as pd
import re
import numpy as np

df = pd.read_csv('torvik_historical_all_teams_with_ffi.csv')

# Filter to tournament teams only
tourney = df[df['team_name'].str.contains(r'\d+\s*seed', case=False, na=False)].copy()

def parse_round(name):
    n = name.upper()
    if 'CHAMPS' in n: return 'Champion'
    elif 'FINALS' in n or 'FINAL,' in n: return 'Finals'
    elif 'FINAL FOUR' in n: return 'Final Four'
    elif 'ELITE' in n: return 'Elite Eight'
    elif 'SWEET' in n: return 'Sweet Sixteen'
    elif 'R32' in n: return 'Round of 32'
    elif 'R64' in n: return 'Round of 64'
    elif 'R68' in n: return 'First Four'
    else: return 'Unknown'

games_won_map = {'First Four': 0, 'Round of 64': 0, 'Round of 32': 1,
                 'Sweet Sixteen': 2, 'Elite Eight': 3, 'Final Four': 4,
                 'Finals': 5, 'Champion': 6}
round_rank = {'First Four': -1, 'Round of 64': 0, 'Round of 32': 1,
              'Sweet Sixteen': 2, 'Elite Eight': 3, 'Final Four': 4,
              'Finals': 5, 'Champion': 6}

tourney['round'] = tourney['team_name'].apply(parse_round)
tourney['games_won'] = tourney['round'].map(games_won_map)
tourney['round_rank'] = tourney['round'].map(round_rank)
tourney['seed'] = tourney['team_name'].str.extract(r'(\d+)\s*seed', flags=re.IGNORECASE).astype(int)

# Clean team base name
tourney['team_base'] = tourney['team_name'].apply(lambda x: re.sub(r'\d+\s*seed.*', '', x).strip())

def ffi_bucket(val):
    if val >= 90: return '90+'
    elif val >= 80: return '80-90'
    elif val >= 70: return '70-80'
    else: return '<70'
tourney['ffi_bucket'] = tourney['adj_ffi'].apply(ffi_bucket)

# Per-season rank
tourney['ffi_rank'] = tourney.groupby('year')['adj_ffi'].rank(ascending=False, method='min').astype(int)

sep = "=" * 95

# ============================================================
# 1. ADJ FFI RANK AMONG TOURNAMENT TEAMS vs OUTCOME
# ============================================================
print(sep)
print("1. CHAMPION'S ADJ FFI RANK AMONG TOURNAMENT TEAMS")
print(sep)
champs = tourney[tourney['round'] == 'Champion'].sort_values('year')
print(f"\n{'Year':<6} {'Team':<25} {'Adj FFI':>8} {'Rank':>5} {'Seed':>5}")
print("-" * 55)
for _, r in champs.iterrows():
    print(f"{r['year']:<6} {r['team_base']:<25} {r['adj_ffi']:>8.1f} {r['ffi_rank']:>5} {r['seed']:>5}")

top5_champs = len(champs[champs['ffi_rank'] <= 5])
top10_champs = len(champs[champs['ffi_rank'] <= 10])
print(f"\nChampions ranked Top 5 in Adj FFI: {top5_champs}/{len(champs)} ({top5_champs/len(champs)*100:.0f}%)")
print(f"Champions ranked Top 10 in Adj FFI: {top10_champs}/{len(champs)} ({top10_champs/len(champs)*100:.0f}%)")

# ============================================================
# 2. DOES THE #1 ADJ FFI TEAM WIN? HOW FAR DO THEY GO?
# ============================================================
print(f"\n{sep}")
print("2. HOW DOES THE #1 ADJ FFI TEAM IN EACH TOURNAMENT PERFORM?")
print(sep)
top1 = tourney[tourney['ffi_rank'] == 1].sort_values('year')
print(f"\n{'Year':<6} {'Team':<25} {'Adj FFI':>8} {'Seed':>5} {'Result':<20}")
print("-" * 70)
for _, r in top1.iterrows():
    print(f"{r['year']:<6} {r['team_base']:<25} {r['adj_ffi']:>8.1f} {r['seed']:>5} {r['round']:<20}")

won = len(top1[top1['round'] == 'Champion'])
ff = len(top1[top1['round_rank'] >= 4])
s16 = len(top1[top1['round_rank'] >= 2])
print(f"\n#1 Adj FFI team won title: {won}/{len(top1)} ({won/len(top1)*100:.0f}%)")
print(f"#1 Adj FFI team made Final Four+: {ff}/{len(top1)} ({ff/len(top1)*100:.0f}%)")
print(f"#1 Adj FFI team made Sweet 16+: {s16}/{len(top1)} ({s16/len(top1)*100:.0f}%)")
print(f"#1 Adj FFI team avg games won: {top1['games_won'].mean():.2f}")

# ============================================================
# 3. TOP 5 ADJ FFI TEAMS - HOW MANY MAKE FINAL FOUR?
# ============================================================
print(f"\n{sep}")
print("3. TOP 5 ADJ FFI TEAMS EACH YEAR - FINAL FOUR REPRESENTATION")
print(sep)
top5 = tourney[tourney['ffi_rank'] <= 5]
print(f"\n{'Year':<6} {'Top5 in FF':>10} {'Top5 in S16':>12} {'Champion Rank':>14}")
print("-" * 50)
for yr in sorted(tourney['year'].unique()):
    t5 = top5[top5['year'] == yr]
    t5_ff = len(t5[t5['round_rank'] >= 4])
    t5_s16 = len(t5[t5['round_rank'] >= 2])
    champ = champs[champs['year'] == yr].iloc[0]
    print(f"{yr:<6} {t5_ff:>10} {t5_s16:>12} {champ['ffi_rank']:>14}")

t5_ff_total = len(top5[top5['round_rank'] >= 4])
print(f"\nOverall: Top 5 Adj FFI teams that make FF+: {t5_ff_total}/{len(top5)} ({t5_ff_total/len(top5)*100:.1f}%)")

# ============================================================
# 4. SEED vs ADJ FFI MISMATCH - UNDERSEEDED TEAMS
# ============================================================
print(f"\n{sep}")
print("4. BIGGEST SEED vs ADJ FFI MISMATCHES (Underseeded by FFI)")
print(sep)
print("   Teams ranked high in Adj FFI but given a low seed — and how they performed\n")

# Calculate expected seed from FFI rank (rough: rank 1-4 = 1 seed, 5-8 = 2 seed, etc.)
tourney['expected_seed'] = ((tourney['ffi_rank'] - 1) // 4) + 1
tourney['seed_diff'] = tourney['seed'] - tourney['expected_seed']  # positive = underseeded

underseeded = tourney[tourney['seed_diff'] >= 4].sort_values('seed_diff', ascending=False).head(25)
print(f"{'Year':<6} {'Team':<25} {'FFI Rank':>9} {'Seed':>5} {'Exp Seed':>9} {'Diff':>5} {'Result':<18} {'Adj FFI':>8}")
print("-" * 100)
for _, r in underseeded.iterrows():
    print(f"{r['year']:<6} {r['team_base']:<25} {r['ffi_rank']:>9} {r['seed']:>5} {r['expected_seed']:>9} {r['seed_diff']:>+5} {r['round']:<18} {r['adj_ffi']:>8.1f}")

# How do underseeded teams do?
under4 = tourney[tourney['seed_diff'] >= 4]
print(f"\nTeams underseeded by 4+ spots: {len(under4)}")
print(f"  Made Sweet 16+: {len(under4[under4['round_rank'] >= 2])} ({len(under4[under4['round_rank'] >= 2])/len(under4)*100:.1f}%)")
print(f"  Avg games won: {under4['games_won'].mean():.2f}")
print(f"  Compare to all tourney avg: {tourney['games_won'].mean():.2f}")

# ============================================================
# 5. OVERSEEDED TEAMS - HIGH SEED, LOW FFI (UPSET CANDIDATES)
# ============================================================
print(f"\n{sep}")
print("5. BIGGEST OVERSEEDED TEAMS (High seed, low FFI) — UPSET BAIT")
print(sep)
print("   Teams given a high seed but ranked low in Adj FFI\n")

overseeded = tourney[(tourney['seed'] <= 4) & (tourney['ffi_rank'] >= 20)].sort_values('ffi_rank', ascending=False).head(25)
print(f"{'Year':<6} {'Team':<25} {'FFI Rank':>9} {'Seed':>5} {'Adj FFI':>8} {'Result':<18}")
print("-" * 80)
for _, r in overseeded.iterrows():
    print(f"{r['year']:<6} {r['team_base']:<25} {r['ffi_rank']:>9} {r['seed']:>5} {r['adj_ffi']:>8.1f} {r['round']:<18}")

over = tourney[(tourney['seed'] <= 4) & (tourney['ffi_rank'] >= 20)]
print(f"\n1-4 seeds ranked 20+ in Adj FFI: {len(over)}")
print(f"  Lost in R64 or R32: {len(over[over['round_rank'] <= 1])} ({len(over[over['round_rank'] <= 1])/len(over)*100:.1f}%)")

# ============================================================
# 6. FFI GAP BETWEEN CHAMPION AND RUNNER-UP
# ============================================================
print(f"\n{sep}")
print("6. ADJ FFI GAP: CHAMPION vs RUNNER-UP")
print(sep)
finals_teams = tourney[tourney['round'].isin(['Champion', 'Finals'])].sort_values(['year', 'round_rank'], ascending=[True, False])
print(f"\n{'Year':<6} {'Champion':<22} {'Ch FFI':>7} {'Runner-Up':<22} {'RU FFI':>7} {'Gap':>6}")
print("-" * 78)
for yr in sorted(tourney['year'].unique()):
    ft = finals_teams[finals_teams['year'] == yr]
    ch = ft[ft['round'] == 'Champion']
    ru = ft[ft['round'] == 'Finals']
    if len(ch) > 0 and len(ru) > 0:
        ch = ch.iloc[0]
        ru = ru.iloc[0]
        gap = ch['adj_ffi'] - ru['adj_ffi']
        print(f"{yr:<6} {ch['team_base']:<22} {ch['adj_ffi']:>7.1f} {ru['team_base']:<22} {ru['adj_ffi']:>7.1f} {gap:>+6.1f}")

# ============================================================
# 7. CONFERENCE STRENGTH BY ADJ FFI
# ============================================================
print(f"\n{sep}")
print("7. WHICH CONFERENCES PRODUCE HIGH-FFI TOURNAMENT TEAMS?")
print(sep)

# We need conference info - check if it's in the data
if 'conf' in tourney.columns:
    conf_stats = tourney.groupby('conf').agg(
        teams=('adj_ffi', 'count'),
        avg_ffi=('adj_ffi', 'mean'),
        med_ffi=('adj_ffi', 'median'),
        avg_games=('games_won', 'mean'),
        s16_plus=('round_rank', lambda x: (x >= 2).sum()),
        champs=('round', lambda x: (x == 'Champion').sum())
    ).sort_values('avg_ffi', ascending=False)
    
    conf_stats['s16_pct'] = conf_stats['s16_plus'] / conf_stats['teams'] * 100
    
    print(f"\n{'Conf':<10} {'Teams':>6} {'Avg FFI':>8} {'Med FFI':>8} {'Avg Wins':>9} {'S16+ %':>8} {'Champs':>7}")
    print("-" * 65)
    for conf, r in conf_stats.head(20).iterrows():
        print(f"{conf:<10} {r['teams']:>6.0f} {r['avg_ffi']:>8.1f} {r['med_ffi']:>8.1f} {r['avg_games']:>9.2f} {r['s16_pct']:>7.1f}% {r['champs']:>7.0f}")
else:
    print("  (Conference column not available in dataset)")

# ============================================================
# 8. RAW FFI vs ADJ FFI - WHEN DOES THE ADJUSTMENT MATTER?
# ============================================================
print(f"\n{sep}")
print("8. RAW FFI vs ADJ FFI — WHEN DOES THE SOS ADJUSTMENT CHANGE THE PICTURE?")
print(sep)

tourney['raw_rank'] = tourney.groupby('year')['raw_ffi'].rank(ascending=False, method='min').astype(int)
tourney['rank_change'] = tourney['raw_rank'] - tourney['ffi_rank']  # positive = moved UP after adjustment

# Biggest risers (teams that benefit most from SOS adjustment)
print("\nBiggest RISERS after SOS adjustment (weak raw stats, strong schedule):\n")
risers = tourney.nlargest(15, 'rank_change')
print(f"{'Year':<6} {'Team':<25} {'Raw Rank':>9} {'Adj Rank':>9} {'Change':>7} {'Raw FFI':>8} {'Adj FFI':>8} {'Result':<15}")
print("-" * 100)
for _, r in risers.iterrows():
    print(f"{r['year']:<6} {r['team_base']:<25} {r['raw_rank']:>9} {r['ffi_rank']:>9} {r['rank_change']:>+7} {r['raw_ffi']:>8.1f} {r['adj_ffi']:>8.1f} {r['round']:<15}")

print("\nBiggest FALLERS after SOS adjustment (inflated raw stats, weak schedule):\n")
fallers = tourney.nsmallest(15, 'rank_change')
print(f"{'Year':<6} {'Team':<25} {'Raw Rank':>9} {'Adj Rank':>9} {'Change':>7} {'Raw FFI':>8} {'Adj FFI':>8} {'Result':<15}")
print("-" * 100)
for _, r in fallers.iterrows():
    print(f"{r['year']:<6} {r['team_base']:<25} {r['raw_rank']:>9} {r['ffi_rank']:>9} {r['rank_change']:>+7} {r['raw_ffi']:>8.1f} {r['adj_ffi']:>8.1f} {r['round']:<15}")

# Which is more predictive - Raw or Adj?
from scipy.stats import spearmanr
raw_corr, _ = spearmanr(tourney['raw_ffi'], tourney['games_won'])
adj_corr, _ = spearmanr(tourney['adj_ffi'], tourney['games_won'])
print(f"\nSpearman correlation with tournament games won:")
print(f"  Raw FFI: {raw_corr:.4f}")
print(f"  Adj FFI: {adj_corr:.4f}")
print(f"  Adj FFI is {'MORE' if adj_corr > raw_corr else 'LESS'} predictive than Raw FFI (delta: {abs(adj_corr - raw_corr):.4f})")

# ============================================================
# 9. INDIVIDUAL FOUR FACTORS — WHICH MATTERS MOST?
# ============================================================
print(f"\n{sep}")
print("9. WHICH INDIVIDUAL FOUR FACTOR IS MOST PREDICTIVE OF TOURNAMENT SUCCESS?")
print(sep)

factors = {
    'adj_efg_margin': 'eFG Margin (adj)',
    'adj_tov_edge': 'TOV Edge (adj)',
    'adj_reb_edge': 'REB Edge (adj)',
    'adj_ftr_margin': 'FTR Margin (adj)',
    'efg_margin': 'eFG Margin (raw)',
    'tov_edge': 'TOV Edge (raw)',
    'reb_edge': 'REB Edge (raw)',
    'ftr_margin': 'FTR Margin (raw)',
}

print(f"\n{'Factor':<22} {'Spearman r':>11} {'Avg (Champs)':>13} {'Avg (All)':>10}")
print("-" * 60)
for col, label in factors.items():
    if col in tourney.columns:
        corr, _ = spearmanr(tourney[col], tourney['games_won'])
        champ_avg = tourney[tourney['round'] == 'Champion'][col].mean()
        all_avg = tourney[col].mean()
        print(f"{label:<22} {corr:>11.4f} {champ_avg:>13.3f} {all_avg:>10.3f}")

# ============================================================
# 10. THE "DANGER ZONE" — HIGH FFI EARLY EXITS
# ============================================================
print(f"\n{sep}")
print("10. THE 'DANGER ZONE' — TOP 10 ADJ FFI TEAMS THAT LOST IN R64 OR R32")
print(sep)

early_exits = tourney[(tourney['ffi_rank'] <= 10) & (tourney['round_rank'] <= 1)].sort_values('adj_ffi', ascending=False)
print(f"\n{'Year':<6} {'Team':<25} {'Adj FFI':>8} {'Rank':>5} {'Seed':>5} {'Lost In':<15}")
print("-" * 70)
for _, r in early_exits.iterrows():
    print(f"{r['year']:<6} {r['team_base']:<25} {r['adj_ffi']:>8.1f} {r['ffi_rank']:>5} {r['seed']:>5} {r['round']:<15}")
print(f"\nTotal top-10 FFI teams bounced by R32: {len(early_exits)}")
total_top10 = len(tourney[tourney['ffi_rank'] <= 10])
print(f"Out of {total_top10} total top-10 FFI teams ({len(early_exits)/total_top10*100:.1f}%)")

# ============================================================
# 11. "MINIMUM VIABLE FFI" — LOWEST FFI TO REACH EACH ROUND
# ============================================================
print(f"\n{sep}")
print("11. MINIMUM ADJ FFI TO REACH EACH ROUND (Historical Floor)")
print(sep)

rounds_ordered = ['Round of 32', 'Sweet Sixteen', 'Elite Eight', 'Final Four', 'Finals', 'Champion']
print(f"\n{'Round':<18} {'Min FFI':>8} {'Team':<30} {'Year':>5} {'Seed':>5}")
print("-" * 72)
for rnd in rounds_ordered:
    rr = round_rank[rnd]
    reached = tourney[tourney['round_rank'] >= rr]
    if len(reached) > 0:
        worst = reached.loc[reached['adj_ffi'].idxmin()]
        print(f"{rnd:<18} {worst['adj_ffi']:>8.1f} {worst['team_base']:<30} {worst['year']:>5.0f} {worst['seed']:>5}")

# ============================================================
# 12. ADJ FFI DIFFERENTIAL IN FINAL FOUR — DOES THE BEST TEAM WIN?
# ============================================================
print(f"\n{sep}")
print("12. FINAL FOUR — DOES THE HIGHEST ADJ FFI TEAM IN THE FF WIN?")
print(sep)

ff_teams = tourney[tourney['round_rank'] >= 4].copy()
print(f"\n{'Year':<6} {'FF #1 FFI Team':<25} {'FFI':>7} {'Won?':<6} {'Champ FFI Rank in FF':>22}")
print("-" * 72)
for yr in sorted(tourney['year'].unique()):
    ff_yr = ff_teams[ff_teams['year'] == yr].sort_values('adj_ffi', ascending=False)
    if len(ff_yr) > 0:
        top = ff_yr.iloc[0]
        champ_yr = ff_yr[ff_yr['round'] == 'Champion']
        if len(champ_yr) > 0:
            champ = champ_yr.iloc[0]
            won = "YES" if top['team_base'] == champ['team_base'] else "no"
            # rank of champ within FF
            champ_ff_rank = (ff_yr['adj_ffi'] > champ['adj_ffi']).sum() + 1
            print(f"{yr:<6} {top['team_base']:<25} {top['adj_ffi']:>7.1f} {won:<6} {champ_ff_rank:>22}")

best_won = sum(1 for yr in sorted(tourney['year'].unique()) 
               if len(ff_teams[ff_teams['year'] == yr]) > 0
               and len(ff_teams[(ff_teams['year'] == yr) & (ff_teams['round'] == 'Champion')]) > 0
               and ff_teams[ff_teams['year'] == yr].sort_values('adj_ffi', ascending=False).iloc[0]['team_base'] == 
                   ff_teams[(ff_teams['year'] == yr) & (ff_teams['round'] == 'Champion')].iloc[0]['team_base'])
print(f"\nHighest Adj FFI team in Final Four won title: {best_won}/{len(tourney['year'].unique())} seasons")

# ============================================================
# 13. SEED-FFI COMBO — OPTIMAL BRACKET STRATEGY
# ============================================================
print(f"\n{sep}")
print("13. SEED LINE PERFORMANCE BY ADJ FFI TIER")
print(sep)
print("    For each seed, what % reach S16+ split by FFI above/below median for that seed?\n")

for seed_num in range(1, 17):
    seed_teams = tourney[tourney['seed'] == seed_num]
    if len(seed_teams) == 0:
        continue
    med = seed_teams['adj_ffi'].median()
    above = seed_teams[seed_teams['adj_ffi'] >= med]
    below = seed_teams[seed_teams['adj_ffi'] < med]
    
    above_s16 = len(above[above['round_rank'] >= 2]) / len(above) * 100 if len(above) > 0 else 0
    below_s16 = len(below[below['round_rank'] >= 2]) / len(below) * 100 if len(below) > 0 else 0
    above_wins = above['games_won'].mean() if len(above) > 0 else 0
    below_wins = below['games_won'].mean() if len(below) > 0 else 0
    
    print(f"  Seed {seed_num:>2}: Median FFI={med:.1f} | Above median: {above_s16:.0f}% S16+, {above_wins:.1f} avg wins | Below median: {below_s16:.0f}% S16+, {below_wins:.1f} avg wins")

# ============================================================
# 14. DYNASTY TEAMS — SAME PROGRAM MULTIPLE HIGH FFI SEASONS
# ============================================================
print(f"\n{sep}")
print("14. PROGRAMS WITH MOST 80+ ADJ FFI TOURNAMENT SEASONS")
print(sep)

elite_seasons = tourney[tourney['adj_ffi'] >= 80].groupby('team_base').agg(
    count=('year', 'count'),
    years=('year', lambda x: list(sorted(x))),
    avg_ffi=('adj_ffi', 'mean'),
    titles=('round', lambda x: (x == 'Champion').sum()),
    avg_games=('games_won', 'mean')
).sort_values('count', ascending=False)

print(f"\n{'Program':<25} {'80+ Seasons':>12} {'Avg FFI':>8} {'Titles':>7} {'Avg Wins':>9}")
print("-" * 65)
for team, r in elite_seasons[elite_seasons['count'] >= 2].iterrows():
    print(f"{team:<25} {r['count']:>12} {r['avg_ffi']:>8.1f} {r['titles']:>7} {r['avg_games']:>9.1f}  {r['years']}")

# ============================================================
# 15. YEAR-OVER-YEAR: IS FFI GETTING MORE/LESS PREDICTIVE?
# ============================================================
print(f"\n{sep}")
print("15. IS ADJ FFI GETTING MORE OR LESS PREDICTIVE OVER TIME?")
print(sep)

print(f"\n{'Year':<6} {'Champ Rank':>11} {'Top5 in FF':>11} {'Avg FFI of FF':>14} {'Spread (std)':>13}")
print("-" * 60)
for yr in sorted(tourney['year'].unique()):
    yr_data = tourney[tourney['year'] == yr]
    champ = yr_data[yr_data['round'] == 'Champion']
    ff = yr_data[yr_data['round_rank'] >= 4]
    if len(champ) > 0:
        cr = champ.iloc[0]['ffi_rank']
        t5_ff = len(yr_data[(yr_data['ffi_rank'] <= 5) & (yr_data['round_rank'] >= 4)])
        ff_avg_ffi = ff['adj_ffi'].mean()
        yr_std = yr_data['adj_ffi'].std()
        print(f"{yr:<6} {cr:>11.0f} {t5_ff:>11} {ff_avg_ffi:>14.1f} {yr_std:>13.1f}")

print(f"\n{'='*95}")
print("ANALYSIS COMPLETE")
print(f"{'='*95}")
