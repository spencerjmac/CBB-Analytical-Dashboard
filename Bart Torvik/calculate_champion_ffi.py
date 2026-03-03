"""
Calculate Raw Four Factor Index (FFI) for every national champion (2008-2025)
using season-specific distributions from torvik_historical_all_teams.csv.

Formula (from backend compute_four_factor_index.py):
  1. Compute four margins for every team:
       eFG margin    = efg_pct - efg_pct_d
       TOV edge      = tord - tor
       REB edge      = orb - drb
       FTR margin    = ftr - ftrd
  2. For each season, compute mean & population std dev of each margin
  3. Z-score each margin: z = (value - mean) / std
  4. Weighted Z = 0.4069*z_eFG + 0.4069*z_TOV + 0.1432*z_REB + 0.0428*z_FTR
  5. FFI_100 = clamp(50 + 20 * weighted_z, 0, 100)

NOTE: "Adjusted FFI" requires opponent-adjusted four-factor margins which are
      NOT in the Torvik historical CSV (it only has raw four factors + AdjOE/AdjDE).
      The Raw FFI below uses season-specific z-scores which already normalise
      across eras — making it the best available metric from this data.
"""
import pandas as pd
import numpy as np

# ── Weights (Dean Oliver / backend constants) ────────────────────────────
W_EFG = 0.4069
W_TOV = 0.4069
W_REB = 0.1432
W_FTR = 0.0428
SCALE = 20  # from backend FOUR_FACTOR_SCALE

# ── Load data ─────────────────────────────────────────────────────────────
df = pd.read_csv('torvik_historical_all_teams.csv')
print(f"Loaded {len(df)} team-season records across {df['year'].nunique()} seasons\n")

# ── Compute four factor margins for ALL teams ─────────────────────────────
df['efg_margin'] = df['efg_pct'] - df['efg_pct_d']
df['tov_edge']   = df['tord'] - df['tor']
df['reb_edge']   = df['orb'] - df['drb']
df['ftr_margin'] = df['ftr'] - df['ftrd']

# ── Identify champions (team_name contains 'CHAMPS') ─────────────────────
champs = df[df['team_name'].str.contains('CHAMPS', case=False, na=False)].copy()
print(f"Found {len(champs)} champions\n")

if champs.empty:
    print("ERROR: No champions found in dataset.")
    exit(1)

# Clean champion team name for display
champs['clean_name'] = champs['team_name'].str.replace(
    r'\d+\s*seed\s*,?\s*CHAMPS', '', regex=True
).str.strip()

# ── Compute season-specific z-scores and Raw FFI ─────────────────────────
metrics = ['efg_margin', 'tov_edge', 'reb_edge', 'ftr_margin']
z_cols  = ['z_efg', 'z_tov', 'z_reb', 'z_ftr']

results = []

print("=" * 90)
print(f"{'Year':>4}  {'Champion':<25} {'eFG_m':>7} {'TOV_e':>7} {'REB_e':>7} {'FTR_m':>7}  {'Wt_Z':>6}  {'Raw FFI':>8}")
print("=" * 90)

for year in sorted(champs['year'].unique()):
    # All teams in this season
    season = df[df['year'] == year].copy()
    n_teams = len(season)

    # Population mean & std (ddof=0 to match backend)
    stats = {}
    for m in metrics:
        stats[m] = {
            'mean': season[m].mean(),
            'std':  season[m].std(ddof=0),
        }

    # Champion row(s) for this year
    champ_rows = champs[champs['year'] == year]

    for _, row in champ_rows.iterrows():
        zs = {}
        for m, zc in zip(metrics, z_cols):
            std = stats[m]['std']
            zs[zc] = (row[m] - stats[m]['mean']) / std if std > 0 else 0.0

        # Weighted z-score
        wz = W_EFG * zs['z_efg'] + W_TOV * zs['z_tov'] + W_REB * zs['z_reb'] + W_FTR * zs['z_ftr']

        # Scale to 0-100
        ffi_raw = max(0.0, min(100.0, 50 + SCALE * wz))

        results.append({
            'year': year,
            'champion': row['clean_name'],
            'n_teams': n_teams,
            'efg_margin': round(row['efg_margin'], 2),
            'tov_edge':   round(row['tov_edge'], 2),
            'reb_edge':   round(row['reb_edge'], 2),
            'ftr_margin': round(row['ftr_margin'], 2),
            'z_efg': round(zs['z_efg'], 3),
            'z_tov': round(zs['z_tov'], 3),
            'z_reb': round(zs['z_reb'], 3),
            'z_ftr': round(zs['z_ftr'], 3),
            'weighted_z': round(wz, 3),
            'raw_ffi': round(ffi_raw, 1),
            'adj_oe': row.get('adj_oe'),
            'adj_de': row.get('adj_de'),
        })

        print(f"{year:>4}  {row['clean_name']:<25} "
              f"{row['efg_margin']:>7.2f} {row['tov_edge']:>7.2f} "
              f"{row['reb_edge']:>7.2f} {row['ftr_margin']:>7.2f}  "
              f"{wz:>6.3f}  {ffi_raw:>8.1f}")

print("=" * 90)

# ── Build results DataFrame ───────────────────────────────────────────────
res = pd.DataFrame(results)

# ── Summary Stats ─────────────────────────────────────────────────────────
print()
print("=" * 60)
print("RAW FOUR FACTOR INDEX — CHAMPION SUMMARY")
print("=" * 60)
print(f"  Champions analysed : {len(res)}")
print(f"  Mean Raw FFI       : {res['raw_ffi'].mean():.1f}")
print(f"  Median Raw FFI     : {res['raw_ffi'].median():.1f}")
print(f"  Std Dev            : {res['raw_ffi'].std():.1f}")
best = res.loc[res['raw_ffi'].idxmax()]
worst = res.loc[res['raw_ffi'].idxmin()]
print(f"  Highest            : {best['raw_ffi']:.1f}  ({int(best['year'])} {best['champion']})")
print(f"  Lowest             : {worst['raw_ffi']:.1f}  ({int(worst['year'])} {worst['champion']})")
print()

# ── Ranked list ───────────────────────────────────────────────────────────
print("=" * 60)
print("CHAMPIONS RANKED BY RAW FFI (BEST → WORST)")
print("=" * 60)
ranked = res.sort_values('raw_ffi', ascending=False).reset_index(drop=True)
for i, r in ranked.iterrows():
    print(f"  {i+1:>2}. {int(r['year'])} {r['champion']:<25} Raw FFI = {r['raw_ffi']:5.1f}  (Wt_Z = {r['weighted_z']:+.3f})")

# ── Z-score breakdown ────────────────────────────────────────────────────
print()
print("=" * 90)
print("Z-SCORE BREAKDOWN BY CHAMPION")
print("=" * 90)
print(f"{'Year':>4}  {'Champion':<25} {'z_eFG':>7} {'z_TOV':>7} {'z_REB':>7} {'z_FTR':>7}  {'Wt_Z':>7}  {'Raw FFI':>8}")
print("-" * 90)
for _, r in ranked.iterrows():
    print(f"{int(r['year']):>4}  {r['champion']:<25} "
          f"{r['z_efg']:>+7.3f} {r['z_tov']:>+7.3f} "
          f"{r['z_reb']:>+7.3f} {r['z_ftr']:>+7.3f}  "
          f"{r['weighted_z']:>+7.3f}  {r['raw_ffi']:>8.1f}")

# ── Save to CSV ───────────────────────────────────────────────────────────
output_file = 'champion_raw_ffi_results.csv'
res.to_csv(output_file, index=False)
print(f"\nResults saved to {output_file}")
