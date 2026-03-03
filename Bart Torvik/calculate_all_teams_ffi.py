"""
Calculate Raw FFI and Adjusted FFI for EVERY team in torvik_historical_all_teams.csv.

Uses the same SOS-regression approach from calculate_champion_adj_ffi.py:
1. Per-season OLS:  adj_oe ~ raw offensive four factors,  adj_de ~ raw defensive four factors
2. SOS multiplier = actual adj efficiency / predicted adj efficiency
3. Scale raw four factors by SOS → adjusted four factors → adjusted margins
4. Z-score each margin within season (population std, ddof=0)
5. Weighted Z → 0-100 scale  (same formula as backend)

Output: torvik_historical_all_teams_with_ffi.csv
"""
import pandas as pd
import numpy as np

# ── Constants ─────────────────────────────────────────────────────────────
W_EFG = 0.4069
W_TOV = 0.4069
W_REB = 0.1432
W_FTR = 0.0428
SCALE = 20

# ── Helper: OLS ──────────────────────────────────────────────────────────
def ols_predict(X, y):
    """Return predictions from OLS fit (X should NOT include intercept)."""
    X = np.asarray(X, dtype=float)
    y = np.asarray(y, dtype=float)
    X_aug = np.hstack([np.ones((X.shape[0], 1)), X])
    beta = np.linalg.lstsq(X_aug, y, rcond=None)[0]
    return X_aug @ beta


# ── Load ──────────────────────────────────────────────────────────────────
df = pd.read_csv('torvik_historical_all_teams.csv')
print(f"Loaded {len(df)} team-season records across {df['year'].nunique()} seasons")

# ── Raw four factor margins ──────────────────────────────────────────────
df['efg_margin'] = df['efg_pct'] - df['efg_pct_d']
df['tov_edge']   = df['tord'] - df['tor']
df['reb_edge']   = df['orb'] - df['drb']
df['ftr_margin'] = df['ftr'] - df['ftrd']

# ── Per-season: regression → SOS → adjusted factors → z-scores → FFI ────
raw_ffi_all  = np.full(len(df), np.nan)
adj_ffi_all  = np.full(len(df), np.nan)
raw_wz_all   = np.full(len(df), np.nan)
adj_wz_all   = np.full(len(df), np.nan)
sos_off_all  = np.full(len(df), np.nan)
sos_def_all  = np.full(len(df), np.nan)
# Adjusted margins
adj_efg_margin_all = np.full(len(df), np.nan)
adj_tov_edge_all   = np.full(len(df), np.nan)
adj_reb_edge_all   = np.full(len(df), np.nan)
adj_ftr_margin_all = np.full(len(df), np.nan)

for year in sorted(df['year'].unique()):
    mask = df['year'] == year
    idx = df.index[mask]
    season = df.loc[mask].copy()
    n = len(season)

    # ── Offensive regression: adj_oe ~ efg_pct, tor, orb, ftr ────────
    cols_off = ['efg_pct', 'tor', 'orb', 'ftr', 'adj_oe']
    valid_off = season.dropna(subset=cols_off)
    pred_oe = ols_predict(valid_off[['efg_pct', 'tor', 'orb', 'ftr']].values,
                          valid_off['adj_oe'].values)
    pred_oe_safe = np.clip(pred_oe, 1.0, None)
    sos_off = valid_off['adj_oe'].values / pred_oe_safe

    # ── Defensive regression: adj_de ~ efg_pct_d, tord, drb, ftrd ────
    cols_def = ['efg_pct_d', 'tord', 'drb', 'ftrd', 'adj_de']
    valid_def = season.dropna(subset=cols_def)
    pred_de = ols_predict(valid_def[['efg_pct_d', 'tord', 'drb', 'ftrd']].values,
                          valid_def['adj_de'].values)
    pred_de_safe = np.clip(pred_de, 1.0, None)
    sos_def = valid_def['adj_de'].values / pred_de_safe

    # Store SOS (aligned by valid_off/valid_def indices)
    sos_off_all[valid_off.index] = sos_off
    sos_def_all[valid_def.index] = sos_def

    # ── Adjusted four factors (for rows that have both SOS values) ────
    s = season.copy()
    s['sos_off'] = np.nan
    s['sos_def'] = np.nan
    s.loc[valid_off.index, 'sos_off'] = sos_off
    s.loc[valid_def.index, 'sos_def'] = sos_def

    # Offense scaling
    s['adj_efg']  = s['efg_pct'] * s['sos_off']
    s['adj_tor']  = s['tor']     / s['sos_off']
    s['adj_orb']  = s['orb']     * s['sos_off']
    s['adj_ftr']  = s['ftr']     * s['sos_off']

    # Defense scaling
    s['adj_efg_d'] = s['efg_pct_d'] * s['sos_def']
    s['adj_tord']  = s['tord']      / s['sos_def']
    s['adj_drb']   = s['drb']       * s['sos_def']
    s['adj_ftrd']  = s['ftrd']      * s['sos_def']

    # Adjusted margins
    s['adj_efg_margin'] = s['adj_efg'] - s['adj_efg_d']
    s['adj_tov_edge']   = s['adj_tord'] - s['adj_tor']
    s['adj_reb_edge']   = s['adj_orb'] - s['adj_drb']
    s['adj_ftr_margin'] = s['adj_ftr'] - s['adj_ftrd']

    adj_efg_margin_all[idx] = s['adj_efg_margin'].values
    adj_tov_edge_all[idx]   = s['adj_tov_edge'].values
    adj_reb_edge_all[idx]   = s['adj_reb_edge'].values
    adj_ftr_margin_all[idx] = s['adj_ftr_margin'].values

    # ── Raw FFI z-scores (population std) ─────────────────────────────
    raw_metrics = ['efg_margin', 'tov_edge', 'reb_edge', 'ftr_margin']
    raw_means = {m: season[m].mean() for m in raw_metrics}
    raw_stds  = {m: season[m].std(ddof=0) for m in raw_metrics}

    z_efg_raw = (season['efg_margin'] - raw_means['efg_margin']) / raw_stds['efg_margin'] if raw_stds['efg_margin'] > 0 else 0
    z_tov_raw = (season['tov_edge']   - raw_means['tov_edge'])   / raw_stds['tov_edge']   if raw_stds['tov_edge']   > 0 else 0
    z_reb_raw = (season['reb_edge']   - raw_means['reb_edge'])   / raw_stds['reb_edge']   if raw_stds['reb_edge']   > 0 else 0
    z_ftr_raw = (season['ftr_margin'] - raw_means['ftr_margin']) / raw_stds['ftr_margin'] if raw_stds['ftr_margin'] > 0 else 0

    wz_raw = W_EFG * z_efg_raw + W_TOV * z_tov_raw + W_REB * z_reb_raw + W_FTR * z_ftr_raw
    ffi_raw = np.clip(50 + SCALE * wz_raw, 0, 100)

    raw_wz_all[idx]  = wz_raw.values
    raw_ffi_all[idx] = ffi_raw.values

    # ── Adj FFI z-scores (population std) ─────────────────────────────
    adj_m = ['adj_efg_margin', 'adj_tov_edge', 'adj_reb_edge', 'adj_ftr_margin']
    adj_means = {m: s[m].mean() for m in adj_m}
    adj_stds  = {m: s[m].std(ddof=0) for m in adj_m}

    z_efg_adj = (s['adj_efg_margin'] - adj_means['adj_efg_margin']) / adj_stds['adj_efg_margin'] if adj_stds['adj_efg_margin'] > 0 else 0
    z_tov_adj = (s['adj_tov_edge']   - adj_means['adj_tov_edge'])   / adj_stds['adj_tov_edge']   if adj_stds['adj_tov_edge']   > 0 else 0
    z_reb_adj = (s['adj_reb_edge']   - adj_means['adj_reb_edge'])   / adj_stds['adj_reb_edge']   if adj_stds['adj_reb_edge']   > 0 else 0
    z_ftr_adj = (s['adj_ftr_margin'] - adj_means['adj_ftr_margin']) / adj_stds['adj_ftr_margin'] if adj_stds['adj_ftr_margin'] > 0 else 0

    wz_adj = W_EFG * z_efg_adj + W_TOV * z_tov_adj + W_REB * z_reb_adj + W_FTR * z_ftr_adj
    ffi_adj = np.clip(50 + SCALE * wz_adj, 0, 100)

    adj_wz_all[idx]  = wz_adj.values
    adj_ffi_all[idx] = ffi_adj.values

    print(f"  {year}: {n} teams  |  Raw FFI range {ffi_raw.min():.1f}–{ffi_raw.max():.1f}  |  "
          f"Adj FFI range {ffi_adj.min():.1f}–{ffi_adj.max():.1f}")

# ── Attach to main df ────────────────────────────────────────────────────
df['raw_wz']  = np.round(raw_wz_all, 3)
df['raw_ffi'] = np.round(raw_ffi_all, 1)
df['adj_efg_margin'] = np.round(adj_efg_margin_all, 2)
df['adj_tov_edge']   = np.round(adj_tov_edge_all, 2)
df['adj_reb_edge']   = np.round(adj_reb_edge_all, 2)
df['adj_ftr_margin'] = np.round(adj_ftr_margin_all, 2)
df['adj_wz']  = np.round(adj_wz_all, 3)
df['adj_ffi'] = np.round(adj_ffi_all, 1)
df['sos_off'] = np.round(sos_off_all, 4)
df['sos_def'] = np.round(sos_def_all, 4)

# ── Save ──────────────────────────────────────────────────────────────────
output = 'torvik_historical_all_teams_with_ffi.csv'
df.to_csv(output, index=False)
print(f"\nSaved {len(df)} rows to {output}")

# ── Quick summary ─────────────────────────────────────────────────────────
print(f"\nNew columns: efg_margin, tov_edge, reb_edge, ftr_margin, raw_wz, raw_ffi, "
      f"adj_efg_margin, adj_tov_edge, adj_reb_edge, adj_ftr_margin, adj_wz, adj_ffi, sos_off, sos_def")
print(f"\nOverall Raw FFI:  mean={df['raw_ffi'].mean():.1f}  std={df['raw_ffi'].std():.1f}")
print(f"Overall Adj FFI:  mean={df['adj_ffi'].mean():.1f}  std={df['adj_ffi'].std():.1f}")

# Show champions
champs = df[df['team_name'].str.contains('CHAMPS', case=False, na=False)].copy()
champs['clean_name'] = champs['team_name'].str.replace(r'\d+\s*seed\s*,?\s*CHAMPS', '', regex=True).str.strip()
print(f"\n{'Year':>4}  {'Champion':<25}  {'Raw FFI':>8}  {'Adj FFI':>8}")
print("-" * 55)
for _, r in champs.sort_values('year').iterrows():
    print(f"{r['year']:>4}  {r['clean_name']:<25}  {r['raw_ffi']:>8.1f}  {r['adj_ffi']:>8.1f}")
