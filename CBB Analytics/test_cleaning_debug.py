import pandas as pd
import re

def clean_percentile_value(val):
    """Remove percentile prefix from values - ISOLATED VERSION FOR TESTING"""
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
    
    # Universal pattern for percentile + value
    if val_str[0].isdigit() and '.' in val_str:
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
                # Handle percentages
                if '%' in remaining:
                    actual_val_str = remaining
                    actual_val = float(remaining.replace('%', ''))
                else:
                    actual_val_str = remaining
                    actual_val = float(remaining)
                
                # Save this candidate
                candidates.append((percentile_len, actual_val_str, actual_val))
                print(f"  Candidate: percentile={percentile} ({percentile_len} digits), value={actual_val_str}")
            except:
                continue
        
        # Choose the best candidate
        if candidates:
            # Check candidates in order of preference
            for percentile_len, actual_val_str, actual_val in candidates:
                if '%' in actual_val_str:
                    if 0 <= actual_val <= 100:
                        print(f"  -> Matched percentage pattern: {actual_val_str}")
                        return actual_val_str
                elif 0 <= actual_val <= 20:
                    print(f"  -> Matched small stat pattern (0-20): {actual_val_str}")
                    return actual_val_str
                    
            # Check for medium values
            for percentile_len, actual_val_str, actual_val in candidates:
                if 20 < actual_val <= 100:
                    if percentile_len <= 2:
                        print(f"  -> Matched medium stat pattern (20-100): {actual_val_str}")
                        return actual_val_str
                        
            # Check for ratings
            for percentile_len, actual_val_str, actual_val in candidates:
                if 70 <= actual_val <= 150:
                    print(f"  -> Matched rating pattern (70-150): {actual_val_str}")
                    return actual_val_str
            
            # Return smallest value as fallback
            result = min(candidates, key=lambda x: x[2])[1]
            print(f"  -> Fallback (smallest): {result}")
            return result
    
    # Pattern 3: "10061.8%" -> "61.8%" (3-digit percentile + percentage)
    match = re.match(r'^(\d{3})(\d+\.?\d*)%$', val_str)
    if match and 0 <= int(match.group(1)) <= 100:
        return match.group(2) + '%'
    
    return val

# Test values
test_vals = {
    '462.9': 'Air Force PTS/G',
    '100132.7': 'Alabama ORtgAdj',
    '1065.4': 'Alcorn PTS/G',
}

print("Testing clean_percentile_value function:")
for val, desc in test_vals.items():
    print(f"\n{desc}: {val}")
    result = clean_percentile_value(val)
    print(f"RESULT: {result}\n")
