"""
Quick script to clean the current cbb_analytics_tableau_cleaned.csv file
by removing percentile prefixes from all numeric columns.
"""

import pandas as pd
import re
from datetime import datetime


def clean_percentile_value(val):
    """
    Remove percentile prefix from values.
    CBB Analytics displays percentile rankings alongside actual values,
    which get scraped as concatenated strings (e.g., "2347.9%" = percentile 23 + actual 47.9%)
    """
    if pd.isna(val) or val == '' or val == '-':
        return val
    
    val_str = str(val).strip()
    
    if len(val_str) < 4:
        return val
    
    # Check if value is already clean (no percentile prefix needed)
    try:
        val_float = float(val_str.replace('%', ''))
        # If it's a percentage in 0-150% range, might already be clean
        if val_str.endswith('%') and 0 <= val_float <= 150:
            # But percentages like "2347.9%" clearly have prefixes
            if val_float <= 100 and len(val_str) <= 7:  # e.g., "45.3%" or "99.9%"
                return val  # Already clean
        # If it's a non-percentage value in typical basketball ranges, might be clean
        elif not val_str.endswith('%'):
            # ORtg/DRtg range: 85-130
            # PTS/G range: 50-100
            # Per-game stats: 0-20
            has_leading_zero = val_str[0] == '0' and len(val_str) > 3
            if (not has_leading_zero and
                (85 <= val_float <= 130 or 50 <= val_float <= 100 or 0 <= val_float <= 20) 
                and len(val_str) <= 6):
                return val  # Already clean
    except:
        pass  # Continue with percentile removal logic
    
    # Pattern 1: "87+17.6" -> "17.6" (for Net Rtg with +)
    match = re.match(r'^(\d{1,3})\+(.+)$', val_str)
    if match and 0 <= int(match.group(1)) <= 100:
        return match.group(2)
    
    # Pattern 2: "87-17.6" -> "-17.6" (for negative Net Rtg)
    match = re.match(r'^(\d{1,3})(-\d+\.?\d*)$', val_str)
    if match and 0 <= int(match.group(1)) <= 100:
        return match.group(2)
    
    # Pattern 3: Percentage values like "2347.9%" or "645.3%" (percentile + percentage)
    if val_str.endswith('%') and val_str[0].isdigit() and '.' in val_str:
        candidates = []
        
        # Try 1-digit and 2-digit percentiles for percentage values
        for percentile_len in [1, 2]:
            if len(val_str) <= percentile_len + 1:
                continue
            
            percentile_str = val_str[:percentile_len]
            remaining = val_str[percentile_len:]
            
            try:
                percentile = int(percentile_str)
                if not (0 <= percentile <= 100):
                    continue
                
                actual_val = float(remaining.replace('%', ''))
                if 0 <= actual_val <= 150:
                    candidates.append((percentile_len, remaining, actual_val))
            except:
                continue
        
        if candidates:
            candidates_sorted = sorted(candidates, key=lambda x: (x[0], -x[2]))
            
            # Prefer values in typical percentage range (30-100%)
            for percentile_len, remaining, actual_val in candidates_sorted:
                if 30 <= actual_val <= 100:
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
            
            # Take first candidate (shortest percentile)
            percentile_len, remaining, actual_val = candidates_sorted[0]
            val_part = remaining.replace('%', '')
            if '.' in val_part:
                parts = val_part.split('.')
                parts[0] = parts[0].lstrip('0') or '0'
                val_part = '.'.join(parts)
            return val_part + '%'
    
    # Universal pattern for non-percentage numbers
    if val_str[0].isdigit() and '.' in val_str and not val_str.endswith('%'):
        # CHECK IF ALREADY CLEAN FIRST
        try:
            current_val = float(val_str)
            has_leading_zero = val_str[0] == '0' and len(val_str) > 4
            if not has_leading_zero and current_val < 150 and len(val_str) <= 6:
                # ORtg/DRtg range (85-135)
                if 85 <= current_val <= 135:
                    return val
                # PTS/G, assists, rebounds, etc. range (0-85)
                if 0 <= current_val < 85:
                    return val
        except:
            pass
        
        candidates = []
        
        # Try all possible percentile lengths (1-3 digits)
        for percentile_len in [1, 2, 3]:
            if len(val_str) <= percentile_len:
                continue
            
            percentile_str = val_str[:percentile_len]
            remaining = val_str[percentile_len:]
            
            try:
                percentile = int(percentile_str)
                if not (0 <= percentile <= 100):
                    continue
                actual_val = float(remaining)
                candidates.append((percentile_len, remaining, actual_val))
            except:
                continue
        
        if candidates:
            candidates_sorted = sorted(candidates, key=lambda x: x[0])
            
            # First priority: ORtg/DRtg range (85-135)
            for percentile_len, actual_val_str, actual_val in candidates_sorted:
                if 85 <= actual_val <= 135:
                    if '.' in actual_val_str:
                        parts = actual_val_str.split('.')
                        parts[0] = parts[0].lstrip('0') or '0'
                        return '.'.join(parts)
                    return actual_val_str.lstrip('0') or '0'
            
            # Second priority: Medium/large ranges (20-85)
            for percentile_len, actual_val_str, actual_val in candidates_sorted:
                if 20 <= actual_val < 85:
                    if '.' in actual_val_str:
                        parts = actual_val_str.split('.')
                        parts[0] = parts[0].lstrip('0') or '0'
                        return '.'.join(parts)
                    return actual_val_str.lstrip('0') or '0'
            
            # Third priority: Small per-game stats (0-20)
            for percentile_len, actual_val_str, actual_val in candidates_sorted:
                if 0 <= actual_val < 20:
                    if '.' in actual_val_str:
                        parts = actual_val_str.split('.')
                        parts[0] = parts[0].lstrip('0') or '0'
                        return '.'.join(parts)
                    return actual_val_str.lstrip('0') or '0'
            
            # Fourth priority: Values over 130
            for percentile_len, actual_val_str, actual_val in candidates_sorted:
                if actual_val > 130:
                    if '.' in actual_val_str:
                        parts = actual_val_str.split('.')
                        parts[0] = parts[0].lstrip('0') or '0'
                        return '.'.join(parts)
                    return actual_val_str.lstrip('0') or '0'
            
            # Fallback: Return first candidate
            result = candidates_sorted[0][1]
            if '.' in result:
                parts = result.split('.')
                parts[0] = parts[0].lstrip('0') or '0'
                result = '.'.join(parts)
            return result
    
    return val


def main():
    """Clean the current CSV file"""
    input_file = 'cbb_analytics_tableau_cleaned.csv'
    
    print("=" * 70)
    print("CBB Analytics CSV Cleaner")
    print("=" * 70)
    
    # Read the current CSV
    print(f"\nReading {input_file}...")
    df = pd.read_csv(input_file)
    print(f"  Loaded {len(df)} rows, {len(df.columns)} columns")
    
    # Identify columns to clean (skip team names, records, GP, dates)
    skip_columns = set()
    for col in df.columns:
        col_lower = str(col).lower()
        if any(keyword in col_lower for keyword in ['team', 'record', 'date', 'timestamp', 'gp', 'unnamed: 0']):
            skip_columns.add(col)
    
    numeric_cols = [col for col in df.columns if col not in skip_columns]
    
    print(f"\nCleaning {len(numeric_cols)} columns...")
    print("  This may take a minute...")
    
    # Apply cleaning function to numeric columns
    for i, col in enumerate(numeric_cols, 1):
        if i % 50 == 0:
            print(f"  Progress: {i}/{len(numeric_cols)} columns...")
        df[col] = df[col].apply(clean_percentile_value)
    
    print(f"  ✓ Cleaned all numeric values")
    
    # Update timestamp
    df['scrape_date'] = datetime.now().strftime('%Y-%m-%d')
    df['scrape_timestamp'] = datetime.now().isoformat()
    
    # Save the cleaned CSV
    print(f"\nSaving cleaned data to {input_file}...")
    df.to_csv(input_file, index=False)
    
    print("\n" + "=" * 70)
    print("✓ CSV file cleaned successfully!")
    print("=" * 70)
    print(f"  Teams: {len(df)}")
    print(f"  Columns: {len(df.columns)}")
    print(f"  All percentile prefixes removed")
    print(f"  Ready for Tableau!")
    print("=" * 70)


if __name__ == "__main__":
    main()
