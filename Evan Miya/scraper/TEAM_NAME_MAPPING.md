# Team Name Mapping Implementation Summary

## Changes Made to Evan Miya Scraper

### 1. Added Team Name Mapping Dictionary (scrape_team_ratings.py)

A comprehensive mapping dictionary has been added to convert Evan Miya team names to match KenPom format:

```python
TEAM_NAME_MAPPING = {
    "Iowa State": "Iowa St.",
    "Michigan State": "Michigan St.",
    "NC State": "N.C. State",
    "Ohio State": "Ohio St.",
    "Saint Mary's": "Saint Mary's",
    "Miami (Fla.)": "Miami FL",
    "Utah State": "Utah St.",
    "Ole Miss": "Mississippi",
    "San Diego State": "San Diego St.",
    "Florida State": "Florida St.",
    "Kansas State": "Kansas St.",
    "Oklahoma State": "Oklahoma St.",
    "Boise State": "Boise St.",
    "Arizona State": "Arizona St.",
    "Penn State": "Penn St.",
    "McNeese State": "McNeese",
    "Colorado State": "Colorado St.",
    "Mississippi State": "Mississippi St.",
    "Wichita State": "Wichita St.",
    # And more...
}
```

### 2. Created normalize_team_names() Function

This function:
- Removes all emojis (🔥, 🤕, 🥶, 💥, 👠, 🔒, 🚰)
- Applies the mapping dictionary to standardize names
- Returns clean team names matching KenPom format

### 3. Integrated into normalize_columns() Function

The normalization is automatically applied when processing scraped data:
```python
if "Team" in df.columns:
    df["Team"] = df["Team"].apply(normalize_team_names)
```

## Examples of Transformations

| Evan Miya Original | After Normalization | KenPom Format |
|--------------------|---------------------|---------------|
| Duke 🔥            | Duke                | Duke          |
| Iowa State         | Iowa St.            | Iowa St.      |
| Michigan State     | Michigan St.        | Michigan St.  |
| Connecticut 🤕     | Connecticut         | Connecticut   |
| NC State           | N.C. State          | N.C. State    |
| Ohio State 🤕      | Ohio St.            | Ohio St.      |
| Saint Mary's🚰     | Saint Mary's        | Saint Mary's  |
| Miami (Fla.) 🔥🤕  | Miami FL            | Miami FL      |
| Ole Miss           | Mississippi         | Mississippi   |
| Kentucky 🤕        | Kentucky            | Kentucky      |
| UCLA 🤕            | UCLA                | UCLA          |

## How to Use

1. **Run KenPom Scraper First** (as you currently do):
   ```powershell
   cd "c:\Users\spenc\OneDrive\Workspace\Tableau Final Project\KenPom Data"
   .\activate.ps1
   python main.py
   ```

2. **Run Evan Miya Scraper** (which now normalizes team names):
   ```powershell
   cd "c:\Users\spenc\OneDrive\Workspace\Tableau Final Project\Evan Miya\scraper"
   python scrape_team_ratings.py --once
   ```

3. **Result**: The team names in both CSV files will now match!

## Testing the Changes

To test the normalization without running the full scraper:
```bash
cd "c:\Users\spenc\OneDrive\Workspace\Tableau Final Project\Evan Miya\scraper"
python test_normalize.py
```

This will show how various team names are transformed.

## Next Steps

1. Run the Evan Miya scraper to regenerate `team_ratings.csv` with normalized names
2. Verify that team names now match between:
   - `KenPom Data\kenpom_tableau.csv` (team_name column)
   - `Evan Miya\scraper\team_ratings.csv` (Team column)
3. Your Tableau integration should now work seamlessly with matching team names!

## Additional Notes

- The mapping is applied automatically every time the scraper runs
- If you find additional mismatches, simply add them to the `TEAM_NAME_MAPPING` dictionary
- Emojis are removed using a comprehensive Unicode regex pattern
- The original data structure remains the same - only team names are normalized
