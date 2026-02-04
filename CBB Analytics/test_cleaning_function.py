"""Test the cleaning function"""
import pandas as pd
import re


def clean_percentile_value(val):
    """
    Remove percentile prefix from values.
    """
    if pd.isna(val) or val == '' or val == '-':
        return val
    
    val_str = str(val).strip()
    
    if len(val_str) < 4:
        return val
    
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
    
    return val


# Test cases
test_vals = ['11101.1', '1046.9%', '99127.0', '193.3', '94123.3', '105.5', '112.0']
print('Testing clean_percentile_value function:')
print('=' * 60)
for v in test_vals:
    result = clean_percentile_value(v)
    print(f'{v:15} -> {result}')
