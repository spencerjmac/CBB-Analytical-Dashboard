"""
Clean column names and remove null columns from the cleaned CSV file.
"""
import pandas as pd
import re

# Read the current cleaned file
print("Loading cbb_analytics_tableau_cleaned.csv...")
df = pd.read_csv('cbb_analytics_tableau_cleaned.csv')
print(f"  Loaded {len(df)} rows, {len(df.columns)} columns")

# Clean column names
print("\nCleaning column names...")
rename_dict = {}
for col in df.columns:
    if col not in ['team_kenpom', 'kenpom_team_name', 'scrape_date', 'scrape_timestamp', 'season_id']:
        # Remove category prefix and keep just the stat name
        # e.g., "traditional_boxscore_Traditional Box Score_PTS/G" -> "PTS/G"
        # Split by underscore and take the last part
        parts = col.split('_')
        
        # The actual stat name is usually the last part
        clean_name = parts[-1]
        
        # If clean_name is still complex (like from multi-level headers), try to extract better
        # Handle cases like "Traditional Box Score_PTS/G" by taking after the last _
        if '/' in clean_name or '%' in clean_name or any(c.isdigit() for c in clean_name):
            # This looks like an actual stat, use it
            pass
        else:
            # Try to find a better stat name by looking at the full column
            # Match patterns like "PTS/G", "FG%", "3P%", etc.
            match = re.search(r'([A-Z0-9]+[/%][A-Z]?|[A-Z][a-z]+\s[A-Z][a-z]+|[A-Z]{2,}|ORtg|DRtg|Net\sRtg)', col)
            if match:
                clean_name = match.group(1)
        
        # Handle duplicates by appending numbers
        original_clean_name = clean_name
        counter = 1
        while clean_name in rename_dict.values():
            counter += 1
            clean_name = f"{original_clean_name}_{counter}"
        
        rename_dict[col] = clean_name

df = df.rename(columns=rename_dict)
print(f"  ✓ Cleaned {len(rename_dict)} column names")

# Show some examples of renamed columns
print("\nExample column name changes:")
for old, new in list(rename_dict.items())[:10]:
    print(f"  {old[:60]:60s} -> {new}")

# Remove completely null columns
print("\nRemoving null columns...")
null_cols = df.columns[df.isnull().all()].tolist()
if null_cols:
    df = df.drop(columns=null_cols)
    print(f"  ✓ Removed {len(null_cols)} completely null columns")
else:
    print(f"  ✓ No null columns to remove")

# Save the cleaned file
output_file = 'cbb_analytics_tableau_cleaned.csv'
print(f"\nSaving to {output_file}...")
df.to_csv(output_file, index=False)

print("\n" + "="*70)
print("✓ Column names cleaned and saved!")
print("="*70)
print(f"  Final: {len(df)} rows, {len(df.columns)} columns")
print("="*70)
