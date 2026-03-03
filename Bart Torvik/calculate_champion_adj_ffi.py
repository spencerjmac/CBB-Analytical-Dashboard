"""
Calculate Adjusted Four Factor Index (Adj FFI) for historical champions
using an SOS-approximation approach.

APPROACH:
=========
The backend computes adj four factors game-by-game using opponent ratings + site
factors.  We don't have game-level data in the historical CSV — only season-level
raw four factors + Torvik's adj_oe / adj_de.

Approximation:
1. For each season, fit regressions:
       adj_oe ~ eFG% + TO% + ORB% + FTR        (offense)
       adj_de ~ eFG%_d + TORD + DRB + FTRD      (defense)
   R² is typically 0.85-0.95 — raw four factors explain most of adjusted
   efficiency, with the residual capturing SOS + interaction effects.

2. Compute an SOS multiplier for each team:
       sos_off = adj_oe / predicted_adj_oe   (>1 → tough defensive schedule)
       sos_def = adj_de / predicted_adj_de   (<1 → tough offensive schedule)

3. Scale each raw four factor by the SOS multiplier:
   Offense (higher=better except TO which is lower=better):
       adj_efg   = efg_pct   × sos_off
       adj_tor   = tor       / sos_off     (lower TO = better)
       adj_orb   = orb       × sos_off
       adj_ftr   = ftr       × sos_off
   Defense (team wants low opponent stats except TORD which is high=better):
       adj_efg_d = efg_pct_d × sos_def
       adj_tord  = tord      / sos_def     (higher TORD = better for D)
       adj_drb   = drb       × sos_def
       adj_ftrd  = ftrd      × sos_def

4. Compute adjusted margins → season z-scores → Adj FFI (same formula as Raw FFI).

SIMPLIFICATION ACKNOWLEDGED:
    This applies a uniform SOS multiplier to all four factors for each side
    (offense / defense).  In reality, a team may face opponents with great
    rebounding D but poor eFG% D — that factor-specific nuance is lost.
    For most teams (especially champions with balanced schedules), this is
    a reasonable approximation.
"""
import pandas as pd
import numpy as np
import math

# ── Constants ─────────────────────────────────────────────────────────────
W_EFG = 0.4069
W_TOV = 0.4069
W_REB = 0.1432
W_FTR = 0.0428
SCALE = 20

# ── Helper: OLS via numpy (no sklearn needed) ────────────────────────────
def ols_regression(X, y):
    """
    Ordinary least-squares regression.
    Returns (coefficients, intercept, r_squared, predictions).
    X: (n, p) array of features
    y: (n,) array of target
    """
    X = np.asarray(X, dtype=float)
    y = np.asarray(y, dtype=float)
    # Add intercept column
    ones = np.ones((X.shape[0], 1))
    X_aug = np.hstack([ones, X])
    # Solve normal equations
    beta, residuals, rank, sv = np.linalg.lstsq(X_aug, y, rcond=None)
    predictions = X_aug @ beta
    ss_res = np.sum((y - predictions) ** 2)
    ss_tot = np.sum((y - np.mean(y)) ** 2)
    r2 = 1 - ss_res / ss_tot if ss_tot > 0 else 0.0
    return beta[1:], beta[0], r2, predictions


def compute_z(values, mean, std):
    """Z-score with zero-std protection."""
    if std == 0:
        return np.zeros_like(values)
    return (values - mean) / std


# ── Load data ─────────────────────────────────────────────────────────────
df = pd.read_csv('torvik_historical_all_teams.csv')
print(f"Loaded {len(df)} team-season records across {df['year'].nunique()} seasons\n")

# ── Compute raw four factor margins ──────────────────────────────────────
df['efg_margin'] = df['efg_pct'] - df['efg_pct_d']
df['tov_edge']   = df['tord'] - df['tor']
df['reb_edge']   = df['orb'] - df['drb']
df['ftr_margin'] = df['ftr'] - df['ftrd']

# ── For each season: regression → SOS multipliers → adjusted factors ─────
all_seasons = sorted(df['year'].unique())

print("=" * 80)
print("STEP 1: Regression Diagnostics  (adj efficiency ~ raw four factors)")
print("=" * 80)
print(f"{'Year':>4}  {'N':>4}  {'R²_off':>7}  {'R²_def':>7}  "
      f"{'SOS_off range':>18}  {'SOS_def range':>18}")
print("-" * 80)

for year in all_seasons:
    mask = df['year'] == year
    season = df.loc[mask].copy()
    n = len(season)

    # Drop any rows with NaN in the columns we need
    cols_off = ['efg_pct', 'tor', 'orb', 'ftr', 'adj_oe']
    cols_def = ['efg_pct_d', 'tord', 'drb', 'ftrd', 'adj_de']
    valid_off = season.dropna(subset=cols_off)
    valid_def = season.dropna(subset=cols_def)

    # ── Offensive regression ──────────────────────────────────────────
    X_off = valid_off[['efg_pct', 'tor', 'orb', 'ftr']].values
    y_off = valid_off['adj_oe'].values
    _, _, r2_off, pred_oe = ols_regression(X_off, y_off)

    # SOS offensive multiplier (clip predictions to avoid div-by-zero)
    pred_oe_safe = np.clip(pred_oe, 1.0, None)
    sos_off = y_off / pred_oe_safe

    # ── Defensive regression ──────────────────────────────────────────
    X_def = valid_def[['efg_pct_d', 'tord', 'drb', 'ftrd']].values
    y_def = valid_def['adj_de'].values
    _, _, r2_def, pred_de = ols_regression(X_def, y_def)

    pred_de_safe = np.clip(pred_de, 1.0, None)
    sos_def = y_def / pred_de_safe

    print(f"{year:>4}  {n:>4}  {r2_off:>7.4f}  {r2_def:>7.4f}  "
          f"{sos_off.min():>7.4f}–{sos_off.max():.4f}  "
          f"{sos_def.min():>7.4f}–{sos_def.max():.4f}")

    # ── Store SOS multipliers back in main df ─────────────────────────
    # Create SOS series aligned with the valid rows
    df.loc[valid_off.index, 'sos_off'] = sos_off
    df.loc[valid_def.index, 'sos_def'] = sos_def

# ── Apply SOS scaling to produce adjusted four factors ────────────────────
print("\n" + "=" * 80)
print("STEP 2: Compute Adjusted Four Factors via SOS Scaling")
print("=" * 80)

# Offense (higher = better, except tor where lower = better)
df['adj_efg']  = df['efg_pct'] * df['sos_off']
df['adj_tor']  = df['tor']     / df['sos_off']
df['adj_orb']  = df['orb']     * df['sos_off']
df['adj_ftr']  = df['ftr']     * df['sos_off']

# Defense (team wants low opponent stats, except tord which is high = better)
df['adj_efg_d'] = df['efg_pct_d'] * df['sos_def']
df['adj_tord']  = df['tord']      / df['sos_def']
df['adj_drb']   = df['drb']       * df['sos_def']
df['adj_ftrd']  = df['ftrd']      * df['sos_def']

# Adjusted margins
df['adj_efg_margin'] = df['adj_efg'] - df['adj_efg_d']
df['adj_tov_edge']   = df['adj_tord'] - df['adj_tor']
df['adj_reb_edge']   = df['adj_orb'] - df['adj_drb']
df['adj_ftr_margin'] = df['adj_ftr'] - df['adj_ftrd']

print("  Adjusted four factors computed for all teams.\n")

# ── Identify champions ───────────────────────────────────────────────────
champs = df[df['team_name'].str.contains('CHAMPS', case=False, na=False)].copy()
champs['clean_name'] = champs['team_name'].str.replace(
    r'\d+\s*seed\s*,?\s*CHAMPS', '', regex=True
).str.strip()
print(f"  Found {len(champs)} champions.\n")

# ── Compute Raw FFI and Adj FFI using season-specific z-scores ───────────
raw_metrics = ['efg_margin', 'tov_edge', 'reb_edge', 'ftr_margin']
adj_metrics = ['adj_efg_margin', 'adj_tov_edge', 'adj_reb_edge', 'adj_ftr_margin']
z_names     = ['z_efg', 'z_tov', 'z_reb', 'z_ftr']

results = []

print("=" * 110)
print("STEP 3: Champion FFI Results")
print("=" * 110)
header = (f"{'Year':>4}  {'Champion':<22}  "
          f"{'Raw FFI':>8}  {'Adj FFI':>8}  {'Δ':>6}  "
          f"{'SOS_off':>8}  {'SOS_def':>8}")
print(header)
print("-" * 110)

for year in sorted(champs['year'].unique()):
    season = df[df['year'] == year]
    n_teams = len(season)

    # Season stats for RAW margins (population std, ddof=0)
    raw_stats = {}
    for m in raw_metrics:
        raw_stats[m] = {'mean': season[m].mean(), 'std': season[m].std(ddof=0)}

    # Season stats for ADJUSTED margins
    adj_stats = {}
    for m in adj_metrics:
        adj_stats[m] = {'mean': season[m].mean(), 'std': season[m].std(ddof=0)}

    champ_rows = champs[champs['year'] == year]
    for _, row in champ_rows.iterrows():
        # ── Raw FFI ───────────────────────────────────────────────
        raw_zs = {}
        for rm, zn in zip(raw_metrics, z_names):
            s = raw_stats[rm]
            raw_zs[zn] = (row[rm] - s['mean']) / s['std'] if s['std'] > 0 else 0.0
        raw_wz = W_EFG * raw_zs['z_efg'] + W_TOV * raw_zs['z_tov'] + W_REB * raw_zs['z_reb'] + W_FTR * raw_zs['z_ftr']
        raw_ffi = max(0.0, min(100.0, 50 + SCALE * raw_wz))

        # ── Adj FFI ───────────────────────────────────────────────
        adj_zs = {}
        for am, zn in zip(adj_metrics, z_names):
            s = adj_stats[am]
            adj_zs[zn] = (row[am] - s['mean']) / s['std'] if s['std'] > 0 else 0.0
        adj_wz = W_EFG * adj_zs['z_efg'] + W_TOV * adj_zs['z_tov'] + W_REB * adj_zs['z_reb'] + W_FTR * adj_zs['z_ftr']
        adj_ffi = max(0.0, min(100.0, 50 + SCALE * adj_wz))

        delta = adj_ffi - raw_ffi

        results.append({
            'year': year,
            'champion': row['clean_name'],
            'n_teams': n_teams,
            # Raw margins
            'efg_margin': round(row['efg_margin'], 2),
            'tov_edge':   round(row['tov_edge'], 2),
            'reb_edge':   round(row['reb_edge'], 2),
            'ftr_margin': round(row['ftr_margin'], 2),
            # Raw FFI
            'raw_wz':  round(raw_wz, 3),
            'raw_ffi': round(raw_ffi, 1),
            # Adjusted margins
            'adj_efg_margin': round(row['adj_efg_margin'], 2),
            'adj_tov_edge':   round(row['adj_tov_edge'], 2),
            'adj_reb_edge':   round(row['adj_reb_edge'], 2),
            'adj_ftr_margin': round(row['adj_ftr_margin'], 2),
            # Adj FFI
            'adj_wz':  round(adj_wz, 3),
            'adj_ffi': round(adj_ffi, 1),
            'delta': round(delta, 1),
            # SOS
            'sos_off': round(row['sos_off'], 4),
            'sos_def': round(row['sos_def'], 4),
        })

        print(f"{year:>4}  {row['clean_name']:<22}  "
              f"{raw_ffi:>8.1f}  {adj_ffi:>8.1f}  {delta:>+6.1f}  "
              f"{row['sos_off']:>8.4f}  {row['sos_def']:>8.4f}")

print("=" * 110)

# ── Build results DataFrame ──────────────────────────────────────────────
res = pd.DataFrame(results)

# ── Summary ──────────────────────────────────────────────────────────────
print()
print("=" * 70)
print("SUMMARY: RAW FFI vs ADJUSTED FFI")
print("=" * 70)
print(f"              {'Raw FFI':>10}  {'Adj FFI':>10}")
print(f"  Mean      : {res['raw_ffi'].mean():>10.1f}  {res['adj_ffi'].mean():>10.1f}")
print(f"  Median    : {res['raw_ffi'].median():>10.1f}  {res['adj_ffi'].median():>10.1f}")
print(f"  Std Dev   : {res['raw_ffi'].std():>10.1f}  {res['adj_ffi'].std():>10.1f}")
print(f"  Correlation: {res['raw_ffi'].corr(res['adj_ffi']):.4f}")
print()

# ── Ranked comparison ────────────────────────────────────────────────────
print("=" * 100)
print("CHAMPIONS RANKED BY ADJUSTED FFI (with Raw FFI comparison)")
print("=" * 100)
ranked = res.sort_values('adj_ffi', ascending=False).reset_index(drop=True)
print(f"{'#':>3}  {'Year':>4}  {'Champion':<22}  {'Adj FFI':>8}  {'Raw FFI':>8}  {'Δ':>6}  {'SOS_off':>8}  {'SOS_def':>8}")
print("-" * 100)
for i, r in ranked.iterrows():
    print(f"{i+1:>3}  {int(r['year']):>4}  {r['champion']:<22}  "
          f"{r['adj_ffi']:>8.1f}  {r['raw_ffi']:>8.1f}  {r['delta']:>+6.1f}  "
          f"{r['sos_off']:>8.4f}  {r['sos_def']:>8.4f}")

# ── Four factor margin comparison ────────────────────────────────────────
print()
print("=" * 120)
print("RAW vs ADJUSTED FOUR FACTOR MARGINS")
print("=" * 120)
print(f"{'Year':>4}  {'Champion':<22}  "
      f"{'eFG_m':>6} {'→adj':>6}  "
      f"{'TOV_e':>6} {'→adj':>6}  "
      f"{'REB_e':>6} {'→adj':>6}  "
      f"{'FTR_m':>6} {'→adj':>6}")
print("-" * 120)
for _, r in ranked.iterrows():
    print(f"{int(r['year']):>4}  {r['champion']:<22}  "
          f"{r['efg_margin']:>6.2f} {r['adj_efg_margin']:>6.2f}  "
          f"{r['tov_edge']:>6.2f} {r['adj_tov_edge']:>6.2f}  "
          f"{r['reb_edge']:>6.2f} {r['adj_reb_edge']:>6.2f}  "
          f"{r['ftr_margin']:>6.2f} {r['adj_ftr_margin']:>6.2f}")

# ── Biggest movers ──────────────────────────────────────────────────────
print()
print("=" * 70)
print("BIGGEST MOVERS (Raw → Adjusted)")
print("=" * 70)
sorted_delta = res.sort_values('delta', ascending=False)
print("\nBiggest GAINS (tough schedule → adjustment helps):")
for _, r in sorted_delta.head(5).iterrows():
    print(f"  {int(r['year'])} {r['champion']:<22}  Raw={r['raw_ffi']:.1f} → Adj={r['adj_ffi']:.1f}  ({r['delta']:+.1f})")
print("\nBiggest DROPS (easy schedule → adjustment hurts):")
for _, r in sorted_delta.tail(5).iterrows():
    print(f"  {int(r['year'])} {r['champion']:<22}  Raw={r['raw_ffi']:.1f} → Adj={r['adj_ffi']:.1f}  ({r['delta']:+.1f})")

# ── Save ─────────────────────────────────────────────────────────────────
output_file = 'champion_adj_ffi_results.csv'
res.to_csv(output_file, index=False)
print(f"\nResults saved to {output_file}")
