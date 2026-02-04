"""
Calculate season-specific mean and standard deviation for Four Factor metrics
This allows proper Z-score calculation for historical national champions
"""

import pandas as pd
import numpy as np
from datetime import datetime

# Read the data
print("Loading data...")
tableau_df = pd.read_csv('torvik_tableau.csv')
champions_df = pd.read_csv('torvik_champions.csv')

# Extract year from date in tableau data
tableau_df['season_year'] = pd.to_datetime(tableau_df['date']).dt.year

print(f"Loaded {len(tableau_df)} teams from Torvik tableau")
print(f"Loaded {len(champions_df)} champion records")

# Calculate the four margin/edge metrics for ALL teams
print("\nCalculating Four Factor margins/edges for all teams...")
tableau_df['efg_margin'] = tableau_df['efg_pct'] - tableau_df['efg_pct_d']
tableau_df['ftr_margin'] = tableau_df['ftr'] - tableau_df['ftrd']
tableau_df['turnover_edge'] = tableau_df['tord'] - tableau_df['tor']
tableau_df['rebounding_edge'] = tableau_df['orb'] - tableau_df['drb']

# Calculate season-specific statistics
print("\nCalculating season-specific means and standard deviations...")
season_stats = tableau_df.groupby('season_year').agg({
    'efg_margin': ['mean', 'std'],
    'ftr_margin': ['mean', 'std'],
    'turnover_edge': ['mean', 'std'],
    'rebounding_edge': ['mean', 'std']
}).reset_index()

# Flatten column names
season_stats.columns = ['season_year', 
                        'efg_margin_mean', 'efg_margin_std',
                        'ftr_margin_mean', 'ftr_margin_std',
                        'turnover_edge_mean', 'turnover_edge_std',
                        'rebounding_edge_mean', 'rebounding_edge_std']

print("\nSeason statistics calculated:")
print(season_stats)

# Calculate the four margins for champions
print("\nCalculating Four Factor margins/edges for champions...")
champions_df['efg_margin'] = champions_df['efg_pct'] - champions_df['efg_pct_d']
champions_df['ftr_margin'] = champions_df['ftr'] - champions_df['ftrd']
champions_df['turnover_edge'] = champions_df['tord'] - champions_df['tor']
champions_df['rebounding_edge'] = champions_df['orb'] - champions_df['drb']

# Merge season stats with champions data
print("\nMerging season statistics with champions data...")
champions_with_stats = champions_df.merge(
    season_stats,
    left_on='year',
    right_on='season_year',
    how='left'
)

# Calculate Z-scores for each champion using their season's mean and std
print("\nCalculating Z-scores for each champion...")
champions_with_stats['efg_margin_z'] = (
    (champions_with_stats['efg_margin'] - champions_with_stats['efg_margin_mean']) / 
    champions_with_stats['efg_margin_std']
)
champions_with_stats['ftr_margin_z'] = (
    (champions_with_stats['ftr_margin'] - champions_with_stats['ftr_margin_mean']) / 
    champions_with_stats['ftr_margin_std']
)
champions_with_stats['turnover_edge_z'] = (
    (champions_with_stats['turnover_edge'] - champions_with_stats['turnover_edge_mean']) / 
    champions_with_stats['turnover_edge_std']
)
champions_with_stats['rebounding_edge_z'] = (
    (champions_with_stats['rebounding_edge'] - champions_with_stats['rebounding_edge_mean']) / 
    champions_with_stats['rebounding_edge_std']
)

# Calculate Four Factor Index using the weights provided
print("\nCalculating Four Factor Index with weights...")
champions_with_stats['four_factor_index_z'] = (
    (0.4069 * champions_with_stats['efg_margin_z']) +
    (0.4069 * champions_with_stats['turnover_edge_z']) +
    (0.1432 * champions_with_stats['rebounding_edge_z']) +
    (0.0428 * champions_with_stats['ftr_margin_z'])
) / 4

# Calculate the 0-100 score
champions_with_stats['four_factor_score'] = np.minimum(
    100,
    np.maximum(
        0,
        50 + 15 * champions_with_stats['four_factor_index_z']
    )
)

# Save the enhanced champions data
output_file = 'torvik_champions_with_season_stats.csv'
champions_with_stats.to_csv(output_file, index=False)
print(f"\n✓ Saved enhanced champions data to: {output_file}")

# Display summary
print("\n" + "="*80)
print("SUMMARY OF CHAMPIONS WITH PROPER Z-SCORES")
print("="*80)
summary_cols = ['year', 'team_name', 'efg_margin', 'efg_margin_z', 
                'turnover_edge', 'turnover_edge_z', 'four_factor_score']
print(champions_with_stats[summary_cols].to_string(index=False))

print("\n" + "="*80)
print("CHAMPION STATISTICS BY SEASON")
print("="*80)
champ_stats = champions_with_stats[['year', 'team_name', 
                                     'efg_margin', 'ftr_margin', 
                                     'turnover_edge', 'rebounding_edge',
                                     'four_factor_index_z', 'four_factor_score']]
print(champ_stats.to_string(index=False))

# Also create a separate file with just the season statistics for reference
season_stats.to_csv('torvik_season_statistics.csv', index=False)
print(f"\n✓ Saved season statistics to: torvik_season_statistics.csv")

print("\n" + "="*80)
print("COMPLETE!")
print("="*80)
print("\nYou now have:")
print("1. torvik_champions_with_season_stats.csv - Champions with all calculated metrics")
print("2. torvik_season_statistics.csv - Mean and std dev for each season")
print("\nThese files contain the correct season-specific statistics for accurate Z-score calculations!")
