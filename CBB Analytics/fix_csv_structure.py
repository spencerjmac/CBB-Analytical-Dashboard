"""
Fix the CBB Analytics CSV file structure
- Remove duplicate Team Name columns
- Remove Unnamed columns
- Keep only one Team Name that matches KenPom format
- Fix Record format
"""
import pandas as pd
import re

def clean_percentile_value(val):
    """Remove percentile prefix from values"""
    if pd.isna(val) or val == '' or val == '-':
        return val
    
    val_str = str(val).strip()
    
    if len(val_str) < 4:
        return val
    
    # Pattern 1: "87+17.6" -> "17.6" (for Net Rtg with +)
    match = re.match(r'^(\d{1,3})\+(.+)$', val_str)
    if match and 0 <= int(match.group(1)) <= 100:
        return match.group(2)
    
    # Pattern 2: "87-17.6" -> "-17.6" (for negative Net Rtg)
    match = re.match(r'^(\d{1,3})(-\d+\.?\d*)$', val_str)
    if match and 0 <= int(match.group(1)) <= 100:
        return match.group(2)
    
    # Pattern 3: Percentage values like "2347.9%" or "645.3%" (percentile + percentage)
    # These are the most common pattern from CBB Analytics
    if val_str.endswith('%') and val_str[0].isdigit() and '.' in val_str:
        candidates = []
        
        # Try 1-digit and 2-digit percentiles for percentage values
        for percentile_len in [1, 2]:
            if len(val_str) <= percentile_len + 1:  # +1 for the %
                continue
            
            percentile_str = val_str[:percentile_len]
            remaining = val_str[percentile_len:]  # includes the %
            
            try:
                percentile = int(percentile_str)
                if not (0 <= percentile <= 100):
                    continue
                
                # Parse the remaining percentage value
                actual_val = float(remaining.replace('%', ''))
                
                # Store valid candidates
                if 0 <= actual_val <= 150:  # Allow up to 150% for eFG%
                    candidates.append((percentile_len, remaining, actual_val))
            except:
                continue
        
        # Choose the best candidate: prefer values in typical percentage ranges
        # For percentages, prefer shorter percentile (1-digit) over longer when both give valid results
        # This is because percentiles are typically 0-100, so "766.0%" is more likely "7" + "66.0%" than "76" + "6.0%"
        if candidates:
            # Sort by percentile length (SHORTEST first) and then by value
            # This ensures we try 1-digit percentile before 2-digit
            candidates_sorted = sorted(candidates, key=lambda x: (x[0], -x[2]))
            
            # First, try to find a candidate with value in typical percentage range (30-100%)
            for percentile_len, remaining, actual_val in candidates_sorted:
                if 30 <= actual_val <= 100:
                    # Strip leading zeros from the value before %
                    val_part = remaining.replace('%', '')
                    if '.' in val_part:
                        parts = val_part.split('.')
                        parts[0] = parts[0].lstrip('0') or '0'
                        val_part = '.'.join(parts)
                    return val_part + '%'
            
            # If no candidate in typical range, try any value <= 100%
            for percentile_len, remaining, actual_val in candidates_sorted:
                if actual_val <= 100:
                    val_part = remaining.replace('%', '')
                    if '.' in val_part:
                        parts = val_part.split('.')
                        parts[0] = parts[0].lstrip('0') or '0'
                        val_part = '.'.join(parts)
                    return val_part + '%'
            
            # If no candidate <= 100%, take the first one (shortest percentile for eFG% which can exceed 100%)
            percentile_len, remaining, actual_val = candidates_sorted[0]
            val_part = remaining.replace('%', '')
            if '.' in val_part:
                parts = val_part.split('.')
                parts[0] = parts[0].lstrip('0') or '0'
                val_part = '.'.join(parts)
            return val_part + '%'
    
    # Universal pattern for percentile + value (non-percentage numbers)
    # Try different splits and pick the most reasonable one
    if val_str[0].isdigit() and '.' in val_str and not val_str.endswith('%'):
        candidates = []
        
        # Try all possible percentile lengths (1-3 digits)
        for percentile_len in [1, 2, 3]:
            if len(val_str) <= percentile_len:
                continue
            
            percentile_str = val_str[:percentile_len]
            remaining = val_str[percentile_len:]
            
            # Check if percentile is valid
            try:
                percentile = int(percentile_str)
                if not (0 <= percentile <= 100):
                    continue
            except:
                continue
            
            # Check if remaining part is a valid number
            try:
                actual_val = float(remaining)
                # Save this candidate with its value for sorting
                candidates.append((percentile_len, remaining, actual_val))
            except:
                continue
        
        # Choose the best candidate based on expected value ranges
        if candidates:
            # For 3-digit values (like "677.4"), strongly prefer 2-digit percentiles
            digits_before_decimal = len(val_str.split('.')[0]) if '.' in val_str else len(val_str)
            if digits_before_decimal == 3:
                for percentile_len, actual_val_str, actual_val in candidates:
                    if percentile_len == 2:
                        # This gives us single-digit values (0-9.9)
                        if '.' in actual_val_str:
                            parts = actual_val_str.split('.')
                            parts[0] = parts[0].lstrip('0') or '0'
                            return '.'.join(parts)
                        return actual_val_str.lstrip('0') or '0'
            
            # For 4+ digit values, check medium/large ranges with longer percentiles
            for percentile_len, actual_val_str, actual_val in sorted(candidates, key=lambda x: x[0], reverse=True):
                if 20 < actual_val <= 150:
                    # Strip leading zeros but keep decimal point intact
                    if '.' in actual_val_str:
                        parts = actual_val_str.split('.')
                        parts[0] = parts[0].lstrip('0') or '0'
                        return '.'.join(parts)
                    return actual_val_str.lstrip('0') or '0'
            
            # Check for small per-game stats (0-20)
            for percentile_len, actual_val_str, actual_val in sorted(candidates, key=lambda x: x[0], reverse=True):
                if 0 <= actual_val <= 20:
                    # Strip leading zeros but keep decimal point intact
                    if '.' in actual_val_str:
                        parts = actual_val_str.split('.')
                        parts[0] = parts[0].lstrip('0') or '0'
                        return '.'.join(parts)
                    return actual_val_str.lstrip('0') or '0'
            
            # Return smallest value as fallback
            result = min(candidates, key=lambda x: x[2])[1]
            if '.' in result:
                parts = result.split('.')
                parts[0] = parts[0].lstrip('0') or '0'
                result = '.'.join(parts)
            return result
    
    return val

# Team name mapping to match KenPom format
TEAM_NAME_MAPPING = {
    'A&M-Corpus Christi': 'A&M Corpus Chris',
    'Abilene Christian': 'Abilene Christian',
    'Air Force': 'Air Force',
    'Akron': 'Akron',
    'Alabama': 'Alabama',
    'Alabama A&M': 'Alabama A&M',
    'Alabama St.': 'Alabama St.',
    'Alcorn': 'Alcorn',
    'American': 'American',
    'App State': 'Appalachian St.',
    'Arizona': 'Arizona',
    'Arizona St.': 'Arizona St.',
    'Ark.-Pine Bluff': 'Ark. Pine Bluff',
    'Arkansas': 'Arkansas',
    'Arkansas St.': 'Arkansas St.',
    'Army West Point': 'Army',
    'Auburn': 'Auburn',
    'Austin Peay': 'Austin Peay',
    'BYU': 'BYU',
    'Ball St.': 'Ball St.',
    'Baylor': 'Baylor',
    'Bellarmine': 'Bellarmine',
    'Belmont': 'Belmont',
    'Bethune-Cookman': 'Bethune Cookman',
    'Binghamton': 'Binghamton',
    'Boise St.': 'Boise St.',
    'Boston College': 'Boston College',
    'Boston U.': 'Boston U.',
    'Bowling Green': 'Bowling Green',
    'Bradley': 'Bradley',
    'Brown': 'Brown',
    'Bryant': 'Bryant',
    'Bucknell': 'Bucknell',
    'Buffalo': 'Buffalo',
    'Butler': 'Butler',
    'CSU Bakersfield': 'CSU Bakersfield',
    'CSUN': 'CS Northridge',
    'California Baptist': 'Cal Baptist',
    'Cal Poly': 'Cal Poly',
    'Cal St. Fullerton': 'CS Fullerton',
    'California': 'California',
    'Campbell': 'Campbell',
    'Canisius': 'Canisius',
    'Central Ark.': 'Central Ark.',
    'Central Conn. St.': 'Central Conn.',
    'Central Mich.': 'Central Mich.',
    'Charleston So.': 'Charleston So.',
    'Charlotte': 'Charlotte',
    'Chattanooga': 'Chattanooga',
}

import os
os.chdir(r'C:\Users\spenc\OneDrive\Workspace\CBB Analytical Dashboard\CBB Analytics')

print("Loading CSV file...")
df = pd.read_csv('cbb_analytics_tableau.csv')

print(f"Original shape: {df.shape}")
print(f"Original columns: {len(df.columns)}")

# Identify columns to keep
columns_to_keep = []
columns_to_drop = []

# Get the base Team Name column (first one without suffix)
team_name_col = 'Unnamed: 5_level_0_Team Name'

for col in df.columns:
    # Keep timestamp columns at the end
    if col in ['scrape_date', 'scrape_timestamp']:
        columns_to_keep.append(col)
    # Keep team_kenpom if it exists
    elif 'team_kenpom' in col.lower() and not any(x in col for x in ['_team_four_factors_adj', '_traditional_shooting', '_traditional_boxscore', '_boxscore_differentials', '_advanced_offense', '_advanced_defense', '_foul_related', '_scoring_context', '_win_loss_splits', '_win_loss_lead']):
        columns_to_keep.append(col)
    # Keep team_original if it exists (the first one)
    elif col == 'team_original':
        columns_to_keep.append(col)
    # Drop Unnamed columns that are just row indices or empty
    elif col.startswith('Unnamed: 0_level_0_Unnamed: 0_level_1'):
        columns_to_drop.append(col)
    elif col.startswith('Unnamed: 1_level_0_Unnamed: 1_level_1'):
        columns_to_drop.append(col)
    elif col.startswith('Unnamed: 2_level_0_Unnamed: 2_level_1'):
        columns_to_drop.append(col)
    # Drop duplicate Team Name columns with suffixes
    elif 'Team Name' in col and col != team_name_col:
        columns_to_drop.append(col)
    # Drop duplicate All, Conf, GP, Net Rtg columns with suffixes
    elif any(x in col for x in ['_team_four_factors_adj', '_traditional_shooting', '_traditional_boxscore', '_boxscore_differentials', '_advanced_offense', '_advanced_defense', '_foul_related', '_scoring_context', '_win_loss_splits', '_win_loss_lead']) and any(base in col for base in ['Unnamed: 3_level_0_All', 'Unnamed: 4_level_0_Conf', 'Unnamed: 6_level_0_GP', 'Unnamed: 7_level_0_Net Rtg']):
        columns_to_drop.append(col)
    # Drop duplicate team_original columns with suffixes
    elif 'team_original_' in col:
        columns_to_drop.append(col)
    # Drop duplicate ORtg, eFG%, etc. with suffixes (keep the base ones)
    elif any(x in col for x in ['_team_four_factors_adj', '_traditional_shooting', '_traditional_boxscore', '_boxscore_differentials', '_advanced_offense', '_advanced_defense', '_foul_related', '_scoring_context', '_win_loss_splits', '_win_loss_lead']) and any(base in col for base in ['Team 4-Factors_ORtg', 'Team 4-Factors_eFG%', 'Team 4-Factors_ORB%', 'Team 4-Factors_TOV%', 'Team 4-Factors_FTA Rate', 'Opponent 4-Factors_DRtg', 'Opponent 4-Factors_eFG%', 'Opponent 4-Factors_ORB%', 'Opponent 4-Factors_TOV%', 'Opponent 4-Factors_FTA Rate']):
        columns_to_drop.append(col)
    else:
        columns_to_keep.append(col)

# Drop the duplicate columns
print(f"\nDropping {len(columns_to_drop)} duplicate columns...")
df = df[columns_to_keep]

print(f"New shape: {df.shape}")
print(f"New columns: {len(df.columns)}")

# Rename the Team Name column to just "Team Name"
if team_name_col in df.columns:
    df = df.rename(columns={team_name_col: 'Team Name'})
    print("\nRenamed Team Name column")

# Map team names to KenPom format
print("\nMapping team names to KenPom format...")
if 'Team Name' in df.columns:
    df['Team Name'] = df['Team Name'].map(lambda x: TEAM_NAME_MAPPING.get(x, x))

# Clean the Record column (rename from "Unnamed: 3_level_0_All")
record_col = 'Unnamed: 3_level_0_All'
if record_col in df.columns:
    df = df.rename(columns={record_col: 'Record'})
    print("Renamed Record column")

# Clean Conference column (rename from "Unnamed: 4_level_0_Conf")
conf_col = 'Unnamed: 4_level_0_Conf'
if conf_col in df.columns:
    df = df.rename(columns={conf_col: 'Conference'})
    print("Renamed Conference column")

# Clean GP column (rename from "Unnamed: 6_level_0_GP")
gp_col = 'Unnamed: 6_level_0_GP'
if gp_col in df.columns:
    df = df.rename(columns={gp_col: 'GP'})
    print("Renamed GP column")

# Clean Net Rtg column (rename from "Unnamed: 7_level_0_Net Rtg")
net_rtg_col = 'Unnamed: 7_level_0_Net Rtg'
if net_rtg_col in df.columns:
    df = df.rename(columns={net_rtg_col: 'Net Rtg'})
    print("Renamed Net Rtg column")

# Remove empty unnamed columns (the ones with no values)
print("\nRemoving empty unnamed columns...")
empty_unnamed_patterns = [
    '_Unnamed: 1_level_0_Unnamed: 1_level_1',
    '_Unnamed: 2_level_0_Unnamed: 2_level_1'
]
columns_to_drop = [col for col in df.columns if any(pattern in col for pattern in empty_unnamed_patterns)]
if columns_to_drop:
    df = df.drop(columns=columns_to_drop)
    print(f"  Dropped {len(columns_to_drop)} empty unnamed columns")

# Remove arrow separator columns
print("\nRemoving arrow separator columns...")
arrow_columns = [col for col in df.columns if '--->' in col]
if arrow_columns:
    df = df.drop(columns=arrow_columns)
    print(f"  Dropped {len(arrow_columns)} arrow columns")

# Remove the first unnamed column from each category (Unnamed: 0)
print("\nRemoving first unnamed column from each category...")
first_unnamed_columns = [col for col in df.columns if 'Unnamed: 0_level_0_Unnamed: 0_level_1' in col]
if first_unnamed_columns:
    df = df.drop(columns=first_unnamed_columns)
    print(f"  Dropped {len(first_unnamed_columns)} first unnamed columns")

# Remove any other unnamed columns that might be empty in win_loss_by_splits
print("\nRemoving other unnamed columns...")
other_unnamed = [col for col in df.columns if 'Unnamed:' in col and '_level_1' in col and col not in ['Team Name', 'Record', 'Conference', 'GP']]
if other_unnamed:
    df = df.drop(columns=other_unnamed)
    print(f"  Dropped {len(other_unnamed)} other unnamed columns")

# Rename the remaining Unnamed columns that have values
print("\nRenaming columns with data...")
rename_map = {}
for col in df.columns:
    if 'Unnamed: 3_level_0_All' in col:
        category = col.split('_Unnamed:')[0]
        rename_map[col] = f'{category}_Record'
    elif 'Unnamed: 4_level_0_Conf' in col:
        category = col.split('_Unnamed:')[0]
        rename_map[col] = f'{category}_Conf_Record'
    elif 'Unnamed: 6_level_0_GP' in col:
        category = col.split('_Unnamed:')[0]
        rename_map[col] = f'{category}_GP'
    elif 'Unnamed: 7_level_0_ORtg' in col:
        category = col.split('_Unnamed:')[0]
        rename_map[col] = f'{category}_ORtg'
    elif 'Unnamed: 7_level_0_DRtg' in col:
        category = col.split('_Unnamed:')[0]
        rename_map[col] = f'{category}_DRtg'
    elif 'Unnamed: 13_level_0_DRtg' in col:
        category = col.split('_Unnamed:')[0]
        rename_map[col] = f'{category}_DRtg_Opp'

if rename_map:
    df = df.rename(columns=rename_map)
    print(f"  Renamed {len(rename_map)} columns")

# Keep only one set of Record and Conf_Record columns
print("\nRemoving duplicate Record columns...")
# Find the first Record and Conf_Record columns (from team_four_factors_adj)
first_record_col = None
first_conf_record_col = None
for col in df.columns:
    if '_Record' in col and 'Conf_Record' not in col and first_record_col is None:
        first_record_col = col
    if 'Conf_Record' in col and first_conf_record_col is None:
        first_conf_record_col = col

# Rename the first ones to simple names
if first_record_col:
    df = df.rename(columns={first_record_col: 'Record'})
    print(f"  Kept {first_record_col} as 'Record'")
if first_conf_record_col:
    df = df.rename(columns={first_conf_record_col: 'Conf_Record'})
    print(f"  Kept {first_conf_record_col} as 'Conf_Record'")

# Drop all other Record columns
record_cols_to_drop = [col for col in df.columns if ('_Record' in col or 'Conf_Record' in col) and col not in ['Record', 'Conf_Record']]
if record_cols_to_drop:
    df = df.drop(columns=record_cols_to_drop)
    print(f"  Dropped {len(record_cols_to_drop)} duplicate Record columns")

# Keep only one GP (Games Played) column
print("\nRemoving duplicate GP columns...")
# Find the first GP column
first_gp_col = None
for col in df.columns:
    if col.endswith('_GP') and first_gp_col is None:
        first_gp_col = col
        break

# Rename the first one to simple name
if first_gp_col:
    df = df.rename(columns={first_gp_col: 'GP'})
    print(f"  Kept {first_gp_col} as 'GP'")

# Drop all other GP columns
gp_cols_to_drop = [col for col in df.columns if col.endswith('_GP') or (col == 'GP' and col != 'GP')]
if gp_cols_to_drop:
    df = df.drop(columns=gp_cols_to_drop)
    print(f"  Dropped {len(gp_cols_to_drop)} duplicate GP columns")

# Clean all numeric/percentage columns (remove percentile prefixes)
print("\nCleaning all numeric values (removing percentile prefixes)...")

# Skip non-numeric columns
skip_columns = ['team_kenpom', 'scrape_date', 'scrape_timestamp', 'season_id']
skip_columns.extend([col for col in df.columns if 'Record' in col])  # Skip record columns like "8-7"

# Clean all columns that contain numeric data or percentages
columns_to_clean = [col for col in df.columns if col not in skip_columns]

cleaned_count = 0
for col in columns_to_clean:
    # Check if column has any values that look like they need cleaning
    sample_val = str(df[col].iloc[0]) if not df[col].isna().all() else ""
    if sample_val and (sample_val.replace('.', '').replace('%', '').replace('-', '').isdigit() or 
                       any(char.isdigit() for char in sample_val)):
        df[col] = df[col].apply(clean_percentile_value)
        cleaned_count += 1

print(f"  Cleaned {cleaned_count} columns")

# Save the cleaned file
output_file = 'cbb_analytics_tableau_cleaned.csv'
df.to_csv(output_file, index=False)
print(f"\nSaved cleaned file to: {output_file}")

print(f"\nFinal shape: {df.shape}")
print(f"Final column count: {len(df.columns)}")

# Print sample of team_kenpom column if it exists
if 'team_kenpom' in df.columns:
    print("\nFirst 5 teams:")
    print(df[['team_kenpom']].head(5))

print("\nColumn list:")
for i, col in enumerate(df.columns, 1):
    print(f"  {i:3d}. {col}")
