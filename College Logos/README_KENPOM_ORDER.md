# NCAA Basketball Logos - KenPom Alphabetical Order

## Overview
This folder contains NCAA D1 basketball team logos renamed to match the exact alphabetical order of KenPom team names. This ensures that when you use these as custom shapes in Tableau, they will be assigned to the correct teams in your visualizations.

## Files
- **NCAA_Logos_KenPom_Order.zip** - All 365 team logos renamed in KenPom alphabetical order (16.3 MB)
- **logos_kenpom_order/** - Unzipped folder with all 365 PNG logos

## How to Use in Tableau

### Step 1: Extract the Logos
1. Extract the contents of `NCAA_Logos_KenPom_Order.zip`
2. You should see 365 PNG files, one for each team

### Step 2: Add to Tableau Shapes
1. Locate your Tableau Repository folder:
   - Windows: `C:\Users\[YourUsername]\Documents\My Tableau Repository\Shapes\`
   - Mac: `~/Documents/My Tableau Repository/Shapes/`

2. Create a new folder inside `Shapes` called **NCAA_Basketball**

3. Copy all 365 PNG files into this `NCAA_Basketball` folder

4. **Restart Tableau Desktop** - This is required for Tableau to recognize the new shapes

### Step 3: Use in Your Visualization
1. Drag `Team Name` (from Sheet 16_Summary.csv) to the Marks shelf
2. Change the mark type to **Shape**
3. Click on the Shape button in the Marks shelf
4. Select **NCAA_Basketball** from the "Select Shape Palette" dropdown
5. Click **Assign Palette** - Tableau will automatically match logos to teams alphabetically
6. The logos should now be correctly assigned to each team!

## Team Name Format
All logo filenames match the exact KenPom team name format:
- Punctuation removed or replaced (`.` removed, `&` becomes `and`)
- Examples:
  - "St." teams: `St Bonaventure.png`, `St John's.png`
  - "A&M" teams: `Alabama AandM.png`, `Texas AandM.png`
  - Special chars: `William and Mary.png`, `NC State.png`

## Alphabetical Order
The logos are named to sort alphabetically from:
1. **Abilene Christian** (first)
2. ...through all 365 teams...
3. **Youngstown St.** (last)

This matches the exact ordering in your Sheet 16_Summary.csv file.

## Technical Details
- **Total Teams:** 365 NCAA D1 Basketball programs
- **Image Format:** PNG with transparent backgrounds
- **Source:** ESPN team logos
- **Processing:** Automated scraping, color palette extraction, and renaming

## Files in This Folder
- `rename_logos_kenpom_order.py` - Script that renames logos to match KenPom order
- `team_name_mapping.py` - Manual mapping of KenPom names to ESPN logo filenames
- `download_ncaa_d1_logos.py` - Original logo scraper script
- `README.md` - This file

## Troubleshooting

### Shapes not appearing?
- Make sure you **restarted Tableau** after copying the files
- Verify all 365 PNG files are in the `NCAA_Basketball` folder
- Check that the folder is in the correct location

### Logos assigned to wrong teams?
- Make sure your data uses the exact KenPom team names
- Verify the team names are sorted alphabetically in your data source
- The "Assign Palette" button in Tableau assigns shapes in alphabetical order

### Need to update logos?
- Re-run `download_ncaa_d1_logos.py` to get fresh logos from ESPN
- Then run `rename_logos_kenpom_order.py` to reorder them

## Credits
- Logo images © ESPN
- KenPom team names © Ken Pomeroy
- Scraper and ordering scripts by Spencer
