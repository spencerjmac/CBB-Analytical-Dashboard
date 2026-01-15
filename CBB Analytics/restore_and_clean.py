"""
Restore original data from scraper and clean properly
"""
import pandas as pd
import re

def clean_percentile_value(val):
    """Remove percentile prefix from values - CORRECT VERSION"""
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
    
    # Pattern 5: "98129.3" or "98128.6" -> "128.6" (2-digit percentile + 3-digit value)
    match = re.match(r'^(\d{2})(\d{3}\.\d+)$', val_str)
    if match and 0 <= int(match.group(1)) <= 100:
        return match.group(2)
    
    # Pattern 7 BEFORE Pattern 6: "20101.8" -> "101.8" (handles values >100)
    match = re.match(r'^(\d{2})(\d{2,3}\.\d+)$', val_str)
    if match:
        percentile = int(match.group(1))
        actual_value = match.group(2)
        if 0 <= percentile <= 100:
            try:
                float_val = float(actual_value)
                # Only apply if value is in range for ratings (50-200)
                if 50 < float_val < 200:
                    return actual_value
            except:
                pass
    
    # Pattern 6: "1399.4" -> "99.4" (1-2 digit percentile + 2-digit value)
    # This should only match values < 100
    match = re.match(r'^(\d{1,2})(\d{2}\.\d+)$', val_str)
    if match:
        percentile = int(match.group(1))
        actual_value = match.group(2)
        if 0 <= percentile <= 100:
            try:
                float_val = float(actual_value)
                # Only apply if value is < 50 (not a rating)
                if float_val < 50:
                    return actual_value
            except:
                pass
    
    return val

# Since the scraper isn't working, let me check if there's a backup
# or we need to restore from the partially-cleaned file
print("Checking current CSV state...")
df = pd.read_csv('cbb_analytics_tableau.csv')

# Check first few ORtg values
print("\nFirst 10 ORtg values in current CSV:")
for i in range(10):
    val = df.loc[i, 'Team 4-Factors_ORtg']
    team = df.loc[i, 'Unnamed: 5_level_0_Team Name']
    print(f"  {i}: {team:25s} = {val}")

print("\n")
print("The data appears to have been corrupted by previous cleaning attempts.")
print("You'll need to re-run the scraper to get fresh uncleaned data.")
print("\nTry running: python scrape_cbb_analytics.py")
