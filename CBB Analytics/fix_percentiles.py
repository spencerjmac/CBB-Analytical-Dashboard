import pandas as pd
import re

def clean_percentile_value(val):
    """Remove percentile prefix from values."""
    if pd.isna(val) or val == '' or val == '-':
        return val
    
    val_str = str(val).strip()
    
    if len(val_str) < 4:
        return val
    
    # Pattern 1: "100+40.4" -> "+40.4"
    match = re.match(r'^(\d{1,3})\+(.+)$', val_str)
    if match and 0 <= int(match.group(1)) <= 100:
        return '+' + match.group(2)
    
    # Pattern 2: "100-40.4" -> "-40.4"
    match = re.match(r'^(\d{1,3})(-\d+\.?\d*)$', val_str)
    if match and 0 <= int(match.group(1)) <= 100:
        return match.group(2)
    
    # Pattern 3: "10061.8%" -> "61.8%"
    match = re.match(r'^(\d{3})(\d+\.?\d*)%$', val_str)
    if match and 0 <= int(match.group(1)) <= 100:
        return match.group(2) + '%'
    
    # Pattern 4: "9960.5%" -> "60.5%"
    match = re.match(r'^(\d{2})(\d+\.?\d*)%$', val_str)
    if match and 0 <= int(match.group(1)) <= 100:
        return match.group(2) + '%'
    
    # Pattern 4b: "645.0%" -> "45.0%"
    match = re.match(r'^(\d{1})(\d{2}\.?\d*)%$', val_str)
    if match and 0 <= int(match.group(1)) <= 100:
        return match.group(2) + '%'
    
    # Pattern 5: "98129.3" or "98128.6" -> "128.6" (2-digit percentile + 3-digit value before decimal)
    match = re.match(r'^(\d{2})(\d{3}\.\d+)$', val_str)
    if match and 0 <= int(match.group(1)) <= 100:
        return match.group(2)
    
    # Pattern 7 BEFORE Pattern 6: "20101.8" -> "101.8" (handles rating values 100-120 range)
    match = re.match(r'^(\d{2})(\d{2,3}\.\d+)$', val_str)
    if match:
        percentile = int(match.group(1))
        actual_value = match.group(2)
        if 0 <= percentile <= 100:
            try:
                float_val = float(actual_value)
                # Only apply if value is in typical rating range (85-130)
                if 85 <= float_val <= 130:
                    return actual_value
            except:
                pass
    
    # Pattern 6: "1399.4" -> "99.4" (1-2 digit percentile + 2-digit value < 50)
    match = re.match(r'^(\d{1,2})(\d{2}\.\d+)$', val_str)
    if match:
        percentile = int(match.group(1))
        actual_value = match.group(2)
        if 0 <= percentile <= 100:
            try:
                float_val = float(actual_value)
                # Only apply to percentage values (typically < 50)
                if float_val < 50:
                    return actual_value
            except:
                pass
    
    return val

# Read the CSV
print("Reading CSV file...")
df = pd.read_csv('cbb_analytics_tableau.csv')

print(f"Found {len(df)} rows and {len(df.columns)} columns")

# Find columns to clean (exclude team names, GP, dates)
columns_to_clean = []
skip_keywords = ['team_original', 'team_kenpom', 'scrape_date', 'scrape_timestamp', 'team name']
for col in df.columns:
    col_lower = col.lower()
    
    # Skip specific columns
    if any(skip in col_lower for skip in skip_keywords):
        continue
    
    # Skip GP columns
    if col_lower.endswith('_gp') or 'unnamed: 6_level_0_gp' in col_lower:
        continue
    
    # Skip record columns (All, Conf, positional Unnamed 0-4)
    if col in ['Unnamed: 0_level_0_Unnamed: 0_level_1', 'Unnamed: 1_level_0_Unnamed: 1_level_1', 
               'Unnamed: 2_level_0_Unnamed: 2_level_1', 'Unnamed: 3_level_0_All', 'Unnamed: 4_level_0_Conf']:
        continue
    if '_unnamed: 0_level_1' in col_lower or '_unnamed: 1_level_1' in col_lower or '_unnamed: 2_level_1' in col_lower:
        continue
    if '_all' in col_lower or '_conf' in col_lower:
        if not any(x in col_lower for x in ['rtg', '%', 'rate']):
            continue
    
    # Include ALL other numeric/stat columns
    columns_to_clean.append(col)

print(f"\nCleaning {len(columns_to_clean)} columns...")
print("Sample columns:", columns_to_clean[:5])

# Clean each column
for col in columns_to_clean:
    print(f"  Cleaning: {col}")
    df[col] = df[col].apply(clean_percentile_value)

# Show before/after for Akron
print("\nAkron stats (row 4):")
print(f"  ORtg: {df.loc[3, 'Team 4-Factors_ORtg']}")
print(f"  eFG%: {df.loc[3, 'Team 4-Factors_eFG%']}")
print(f"  ORB%: {df.loc[3, 'Team 4-Factors_ORB%']}")
print(f"  TOV%: {df.loc[3, 'Team 4-Factors_TOV%']}")
print(f"  FTA Rate: {df.loc[3, 'Team 4-Factors_FTA Rate']}")

# Save the cleaned CSV
print("\nSaving cleaned CSV...")
df.to_csv('cbb_analytics_tableau.csv', index=False)
print("✓ Done!")
