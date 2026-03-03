import pandas as pd
import re
import numpy as np

df = pd.read_csv('torvik_historical_all_teams_with_ffi.csv')
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

round_rank = {'First Four': -1, 'Round of 64': 0, 'Round of 32': 1,
              'Sweet Sixteen': 2, 'Elite Eight': 3, 'Final Four': 4,
              'Finals': 5, 'Champion': 6}

tourney['round'] = tourney['team_name'].apply(parse_round)
tourney['round_rank'] = tourney['round'].map(round_rank)
tourney['seed'] = tourney['team_name'].str.extract(r'(\d+)\s*seed', flags=re.IGNORECASE).astype(int)
tourney['team_base'] = tourney['team_name'].apply(lambda x: re.sub(r'\d+\s*seed.*', '', x).strip())

champs = tourney[tourney['round'] == 'Champion'].sort_values('year')
all_t = tourney.copy()

metrics = ['adj_ffi', 'adj_efg_margin', 'adj_tov_edge', 'adj_reb_edge', 'adj_ftr_margin']
current_thresholds = {
    'adj_ffi': 68.7,
    'adj_efg_margin': 2.798,
    'adj_tov_edge': 0.6,
    'adj_reb_edge': 0.0,
    'adj_ftr_margin': -7.31,
}

print("=" * 90)
print("NATIONAL CHAMPION CHECKLIST THRESHOLD ANALYSIS")
print("=" * 90)

# ── Per-champion values for each metric ──────────────────────────────────────────
print("\n\n━━━ CHAMPION VALUES FOR EACH METRIC (sorted by metric) ━━━\n")

for metric in metrics:
    print(f"\n{'─'*70}")
    print(f"  {metric.upper()}  |  Current threshold: {current_thresholds[metric]}")
    print(f"{'─'*70}")
    sorted_c = champs[['year', 'team_base', metric]].sort_values(metric)
    for _, r in sorted_c.iterrows():
        flag = " ← MIN" if r[metric] == sorted_c[metric].min() else ""
        below = " ✗ BELOW THRESHOLD" if r[metric] < current_thresholds[metric] else ""
        print(f"  {r['year']:.0f}  {r['team_base']:<25}  {r[metric]:>8.3f}{flag}{below}")
    print(f"\n  Min:    {sorted_c[metric].min():.3f}")
    print(f"  25th %: {sorted_c[metric].quantile(0.25):.3f}")
    print(f"  Median: {sorted_c[metric].median():.3f}")
    print(f"  75th %: {sorted_c[metric].quantile(0.75):.3f}")
    print(f"  Max:    {sorted_c[metric].max():.3f}")
    print(f"  Mean:   {sorted_c[metric].mean():.3f}")

# ── For each candidate threshold, what % of tournament teams pass vs what % of champs fail ──
print("\n\n━━━ THRESHOLD SENSITIVITY ANALYSIS FOR ADJ FFI ━━━")
print("   For each threshold: how many champs would FAIL, and how many non-champs are FILTERED OUT\n")
print(f"{'Threshold':>10}  {'Champs Passing':>15}  {'Champs Failing':>15}  {'Non-Champs Filtered':>22}  {'False Positive Rate':>20}")
print("─" * 90)
non_champs = tourney[tourney['round'] != 'Champion']
for threshold in [68, 70, 72, 74, 76, 78, 80, 82, 84, 85]:
    c_pass = len(champs[champs['adj_ffi'] >= threshold])
    c_fail = len(champs) - c_pass
    nc_filtered = len(non_champs[non_champs['adj_ffi'] < threshold])
    nc_total = len(non_champs)
    fp_rate = len(non_champs[non_champs['adj_ffi'] >= threshold]) / nc_total * 100
    print(f"{threshold:>10}  {c_pass:>6}/{len(champs):<8}  {c_fail:>6}/{len(champs):<8}  {nc_filtered:>8}/{nc_total:<12}  {fp_rate:>19.1f}%")

# ── For each four factor margin, same analysis ──────────────────────────────────
print("\n\n━━━ THRESHOLD SENSITIVITY: ADJ EFG MARGIN ━━━")
print(f"{'Threshold':>10}  {'Champs Passing':>15}  {'Non-Champs ≥ threshold':>24}")
print("─" * 55)
for threshold in [0, 2, 3, 4, 5, 6, 7, 8, 9, 10]:
    c_pass = len(champs[champs['adj_efg_margin'] >= threshold])
    nc_pass = len(non_champs[non_champs['adj_efg_margin'] >= threshold])
    print(f"{threshold:>10.1f}  {c_pass:>6}/{len(champs):<8}  {nc_pass:>8}/{len(non_champs)}")

print("\n\n━━━ THRESHOLD SENSITIVITY: ADJ TURNOVER EDGE ━━━")
print(f"{'Threshold':>10}  {'Champs Passing':>15}  {'Non-Champs ≥ threshold':>24}")
print("─" * 55)
for threshold in [-1, 0, 0.5, 1, 1.5, 2, 2.5, 3, 3.5, 4]:
    c_pass = len(champs[champs['adj_tov_edge'] >= threshold])
    nc_pass = len(non_champs[non_champs['adj_tov_edge'] >= threshold])
    print(f"{threshold:>10.1f}  {c_pass:>6}/{len(champs):<8}  {nc_pass:>8}/{len(non_champs)}")

print("\n\n━━━ THRESHOLD SENSITIVITY: ADJ REBOUNDING EDGE ━━━")
print(f"{'Threshold':>10}  {'Champs Passing':>15}  {'Non-Champs ≥ threshold':>24}")
print("─" * 55)
for threshold in [-5, -2, 0, 2, 4, 6, 8, 10]:
    c_pass = len(champs[champs['adj_reb_edge'] >= threshold])
    nc_pass = len(non_champs[non_champs['adj_reb_edge'] >= threshold])
    print(f"{threshold:>10.1f}  {c_pass:>6}/{len(champs):<8}  {nc_pass:>8}/{len(non_champs)}")

print("\n\n━━━ THRESHOLD SENSITIVITY: ADJ FTR MARGIN ━━━")
print(f"{'Threshold':>10}  {'Champs Passing':>15}  {'Non-Champs ≥ threshold':>24}")
print("─" * 55)
for threshold in [-10, -7, -5, -3, 0, 2, 4, 6]:
    c_pass = len(champs[champs['adj_ftr_margin'] >= threshold])
    nc_pass = len(non_champs[non_champs['adj_ftr_margin'] >= threshold])
    print(f"{threshold:>10.1f}  {c_pass:>6}/{len(champs):<8}  {nc_pass:>8}/{len(non_champs)}")

# ── Recommendation summary ──────────────────────────────────────────────────────
print("\n\n━━━ COMBINED FILTER IMPACT ━━━")
print("   How many teams pass ALL thresholds under different scenarios\n")

scenarios = {
    "Current thresholds": {'adj_ffi': 68.7, 'adj_efg_margin': 2.798, 'adj_tov_edge': 0.6, 'adj_reb_edge': 0.0, 'adj_ftr_margin': -7.31},
    "Moderate tighten (FFI 80)": {'adj_ffi': 80.0, 'adj_efg_margin': 2.798, 'adj_tov_edge': 0.6, 'adj_reb_edge': 0.0, 'adj_ftr_margin': -7.31},
    "All tightened (proposal)": {'adj_ffi': 80.0, 'adj_efg_margin': 5.0, 'adj_tov_edge': 1.0, 'adj_reb_edge': 2.0, 'adj_ftr_margin': -5.0},
    "Strict (median of champs)": {'adj_ffi': 85.7, 'adj_efg_margin': 9.1, 'adj_tov_edge': 3.5, 'adj_reb_edge': 7.4, 'adj_ftr_margin': 5.5},
}

for name, thresholds in scenarios.items():
    mask = pd.Series([True] * len(tourney), index=tourney.index)
    for col, val in thresholds.items():
        mask = mask & (tourney[col] >= val)
    passing = tourney[mask]
    champ_pass = passing[passing['round'] == 'Champion']
    ff_pass = passing[passing['round_rank'] >= 4]
    s16_pass = passing[passing['round_rank'] >= 2]
    print(f"  {name}")
    print(f"    Teams passing all filters: {len(passing)}")
    print(f"    Champions captured: {len(champ_pass)}/{len(champs)} ({len(champ_pass)/len(champs)*100:.0f}%)")
    print(f"    Final Four+ captured: {len(ff_pass)}")
    print(f"    Sweet 16+ captured: {len(s16_pass)}")
    print()
