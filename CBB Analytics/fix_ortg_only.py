"""
Quick fix for ORtg and PTS/G values that were incorrectly cleaned
by removing too many digits from single-digit percentile values
"""
import pandas as pd
import re


def fix_single_digit_percentile(val, expected_range_min, expected_range_max):
    """
    Fix values where single-digit percentile was incorrectly removed
    Expected ranges:
    - ORtg: 85-130
    - PTS/G: 50-100
    """
    try:
        val_float = float(val)
        
        # If value is already in expected range, return it
        if expected_range_min <= val_float <= expected_range_max:
            return val
        
        # If value is too low (like 3.8 instead of 93.8 or 103.8), try prepending digits
        if val_float < expected_range_min:
            # Try prepending each digit 0-9
            for prepend_digit in range(10):
                new_val = float(f"{prepend_digit}{val}")
                if expected_range_min <= new_val <= expected_range_max:
                    return new_val
        
        return val
    except:
        return val


# Load the incorrectly cleaned file
df = pd.read_csv('cbb_analytics_tableau_cleaned_backup_old.csv')

print(f"Loaded file: {df.shape}")
print(f"\nColumns to fix:")

# Find ORtg columns
ortg_cols = [col for col in df.columns if 'ORtg' in col or 'DRtg' in col]
print(f"  ORtg/DRtg columns: {len(ortg_cols)}")
for col in ortg_cols:
    print(f"    - {col}")

# Find PTS/G columns
pts_cols = [col for col in df.columns if 'PTS/G' in col]
print(f"  PTS/G columns: {len(pts_cols)}")
for col in pts_cols:
    print(f"    - {col}")

# Check Air Force before fix
print(f"\nAir Force BEFORE fix:")
for col in ortg_cols + pts_cols:
    val = df[df['team_kenpom'] == 'Air Force'][col].values[0]
    print(f"  {col}: {val}")

# Fix ORtg/DRtg columns (expected range 85-130)
for col in ortg_cols:
    print(f"\nFixing {col}...")
    df[col] = df[col].apply(lambda x: fix_single_digit_percentile(x, 85, 130))
    
    # Check how many were fixed
    try:
        low_values = (df[col].astype(float) < 85).sum()
        high_values = (df[col].astype(float) > 130).sum()
        print(f"  Values < 85: {low_values}")
        print(f"  Values > 130: {high_values}")
    except:
        pass

# Fix PTS/G columns (expected range 50-100)
for col in pts_cols:
    print(f"\nFixing {col}...")
    df[col] = df[col].apply(lambda x: fix_single_digit_percentile(x, 50, 100))
    
    # Check how many were fixed
    try:
        low_values = (df[col].astype(float) < 50).sum()
        high_values = (df[col].astype(float) > 100).sum()
        print(f"  Values < 50: {low_values}")
        print(f"  Values > 100: {high_values}")
    except:
        pass

# Check Air Force after fix
print(f"\nAir Force AFTER fix:")
for col in ortg_cols + pts_cols:
    val = df[df['team_kenpom'] == 'Air Force'][col].values[0]
    print(f"  {col}: {val}")

# Save the fixed file
df.to_csv('cbb_analytics_tableau_cleaned.csv', index=False)
print(f"\n✓ Saved fixed file: cbb_analytics_tableau_cleaned.csv")
print(f"  Shape: {df.shape}")
