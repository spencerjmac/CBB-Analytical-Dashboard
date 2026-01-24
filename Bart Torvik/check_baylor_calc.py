import pandas as pd

df = pd.read_csv('torvik_champions_with_season_stats.csv')
baylor = df[df['year']==2021].iloc[0]

print('BAYLOR 2021 CALCULATION CHECK')
print('='*60)
print(f'EFG Margin Z: {baylor["efg_margin_z"]:.6f}')
print(f'Turnover Edge Z: {baylor["turnover_edge_z"]:.6f}')
print(f'Rebounding Edge Z: {baylor["rebounding_edge_z"]:.6f}')
print(f'FTR Margin Z: {baylor["ftr_margin_z"]:.6f}')
print()

print('WEIGHTED CALCULATION:')
weighted = (0.4069 * baylor['efg_margin_z']) + \
           (0.4069 * baylor['turnover_edge_z']) + \
           (0.1432 * baylor['rebounding_edge_z']) + \
           (0.0428 * baylor['ftr_margin_z'])

print(f'(0.4069 * {baylor["efg_margin_z"]:.4f}) + (0.4069 * {baylor["turnover_edge_z"]:.4f}) + (0.1432 * {baylor["rebounding_edge_z"]:.4f}) + (0.0428 * {baylor["ftr_margin_z"]:.4f})')
print(f'= {weighted:.6f}')
print()

print(f'My INCORRECT calculation (÷4): {baylor["four_factor_index_z"]:.6f}')
print(f'CORRECT calculation (NO ÷4): {weighted:.6f}')
print()

score_correct = min(100, max(0, 50 + 15 * weighted))
print(f'Correct Four Factor Score: {score_correct:.2f}')
print(f'My incorrect score: {baylor["four_factor_score"]:.2f}')
print()
print('='*60)
print('THE BUG: I divided by 4, but the weights already sum to 1!')
print('Weights: 0.4069 + 0.4069 + 0.1432 + 0.0428 = 0.9998 ≈ 1.0')
