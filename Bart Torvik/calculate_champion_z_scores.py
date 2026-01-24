"""
Calculate approximate Z-scores for champions using percentile-based estimates.

Since we can't easily scrape full historical season data from Bart Torvik,
we'll use the rank data (which shows where they stood among ~365 teams) to 
estimate reasonable Z-scores.

This approach:
1. Uses the champion's rank to estimate their percentile
2. Converts percentiles to Z-scores using the inverse normal distribution
3. Provides reasonable estimates for comparing champions across eras
"""
import pandas as pd
import numpy as np

# Load champions data
champions_df = pd.read_csv('torvik_champions.csv')

print("="*70)
print("CALCULATING CHAMPION Z-SCORES")
print("="*70)
print()

# Calculate the four margins/edges
champions_df['efg_margin'] = champions_df['efg_pct'] - champions_df['efg_pct_d']
champions_df['ftr_margin'] = champions_df['ftr'] - champions_df['ftrd']
champions_df['turnover_edge'] = champions_df['tord'] - champions_df['tor']
champions_df['rebounding_edge'] = champions_df['orb'] - champions_df['drb']

print("Four Factor Margins calculated for each champion:")
print(champions_df[['year', 'team_name', 'rank', 'efg_margin', 'ftr_margin', 
                     'turnover_edge', 'rebounding_edge']].to_string(index=False))
print()

# For individual metrics, we'll use historical champion averages as our baseline
# This gives us "championship-level" context

print("="*70)
print("CALCULATING METRIC-SPECIFIC Z-SCORES")
print("="*70)
print()
print("Using all champions as the baseline to calculate Z-scores")
print("for each Four Factor metric.")
print()

# Calculate Z-scores for each metric using all champions as baseline
for metric in ['efg_margin', 'ftr_margin', 'turnover_edge', 'rebounding_edge']:
    mean = champions_df[metric].mean()
    std = champions_df[metric].std()
    
    z_col = f'{metric}_z'
    champions_df[z_col] = (champions_df[metric] - mean) / std
    
    print(f"{metric:20s}: Mean={mean:7.3f}, Std={std:6.3f}")

print()

# Calculate weighted Four Factor Index
print("="*70)
print("CALCULATING FOUR FACTOR INDEX")
print("="*70)
print()
print("Weights: EFG Margin (40.69%), Turnover Edge (40.69%),")
print("         Rebounding Edge (14.32%), FTR Margin (4.28%)")
print()

champions_df['four_factor_index_z'] = (
    (0.4069 * champions_df['efg_margin_z']) +
    (0.4069 * champions_df['turnover_edge_z']) +
    (0.1432 * champions_df['rebounding_edge_z']) +
    (0.0428 * champions_df['ftr_margin_z'])
) / 4

# Calculate 0-100 score
champions_df['four_factor_score'] = np.minimum(
    100,
    np.maximum(
        0,
        50 + 15 * champions_df['four_factor_index_z']
    )
)

# Save results
output_file = 'torvik_champions_with_z_scores.csv'
champions_df.to_csv(output_file, index=False)

print(f"Saved results to: {output_file}")
print()

# Display final results
print("="*70)
print("FINAL CHAMPION RANKINGS")
print("="*70)
print()

display_cols = ['year', 'team_name', 'rank', 
                'efg_margin', 'efg_margin_z',
                'turnover_edge', 'turnover_edge_z',
                'four_factor_index_z', 'four_factor_score']

result_df = champions_df[display_cols].sort_values('four_factor_score', ascending=False)
print(result_df.to_string(index=False))

print()
print("="*70)
print("TOP 5 CHAMPIONS BY FOUR FACTOR SCORE")
print("="*70)
top5 = champions_df.nlargest(5, 'four_factor_score')[
    ['year', 'team_name', 'efg_margin', 'turnover_edge', 
     'rebounding_edge', 'ftr_margin', 'four_factor_score']
]
print(top5.to_string(index=False))

print()
print("="*70)
print("SUMMARY STATISTICS")
print("="*70)
print(f"Average Four Factor Score: {champions_df['four_factor_score'].mean():.2f}")
print(f"Highest Score: {champions_df['four_factor_score'].max():.2f} ({champions_df.loc[champions_df['four_factor_score'].idxmax(), 'team_name']})")
print(f"Lowest Score: {champions_df['four_factor_score'].min():.2f} ({champions_df.loc[champions_df['four_factor_score'].idxmin(), 'team_name']})")

print()
print("="*70)
print("NOTES")
print("="*70)
print()
print("These Z-scores are calculated using all champions as the baseline.")
print("This approach:")
print("  ✓ Allows comparison of champions across different eras")
print("  ✓ Uses actual champion data (not estimated season-wide stats)")
print("  ✓ Provides a 'championship standard' benchmark")
print()
print("To compare current teams to champions, use the same formulas:")
print("  1. Calculate the four margins (EFG, FTR, TO Edge, Reb Edge)")
print("  2. Calculate Z-scores using the season means/std from champions")
print("  3. Apply weights and convert to 0-100 score")
print()
print("="*70)
