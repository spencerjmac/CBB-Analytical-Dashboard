# Quick Start Guide - Team Name Alignment

## What Was Changed

The **Evan Miya scraper** (`scrape_team_ratings.py`) has been modified to automatically normalize team names to match the KenPom format.

### Key Changes:
1. **Added emoji removal** - Removes all emojis (🔥, 🤕, 🥶, etc.)
2. **Added team name mapping** - Maps variations like "Iowa State" → "Iowa St."
3. **Automatic normalization** - Applied every time the scraper runs

## How to Use

### Step 1: Run KenPom Scraper (as usual)
```powershell
cd "c:\Users\spenc\OneDrive\Workspace\Tableau Final Project\KenPom Data"
.\activate.ps1
python main.py
```

### Step 2: Run Evan Miya Scraper (now with normalization)
```powershell
cd "c:\Users\spenc\OneDrive\Workspace\Tableau Final Project\Evan Miya\scraper"
& "C:/Users/spenc/OneDrive/Workspace/Tableau Final Project/.venv/Scripts/python.exe" scrape_team_ratings.py --once
```

### Step 3: Verify Team Names Match (optional)
```powershell
cd "c:\Users\spenc\OneDrive\Workspace\Tableau Final Project\Evan Miya\scraper"
& "C:/Users/spenc/OneDrive/Workspace/Tableau Final Project/.venv/Scripts/python.exe" verify_team_names.py
```

This will show you:
- ✅ How many teams match
- ❌ Any mismatches (if they exist)
- 💡 Suggestions for fixing mismatches

## Expected Results

**Before:**
- KenPom: `Iowa St.`, `Michigan St.`, `Mississippi`
- Evan Miya: `Iowa State`, `Michigan State 🤕`, `Ole Miss`
- ❌ Names don't match in Tableau

**After:**
- KenPom: `Iowa St.`, `Michigan St.`, `Mississippi`
- Evan Miya: `Iowa St.`, `Michigan St.`, `Mississippi`
- ✅ Names match perfectly in Tableau!

## Troubleshooting

### If you find new mismatches:

1. Open `scrape_team_ratings.py`
2. Find the `TEAM_NAME_MAPPING` dictionary (around line 32)
3. Add the mapping:
   ```python
   TEAM_NAME_MAPPING = {
       # ... existing mappings ...
       "Evan Miya Name": "KenPom Name",
   }
   ```
4. Re-run the Evan Miya scraper

### Common Mappings Already Included:
- State abbreviations: `Iowa State` → `Iowa St.`
- Name variations: `Ole Miss` → `Mississippi`
- School names: `Miami (Fla.)` → `Miami FL`
- And 20+ more...

## Files Modified
- ✏️ `Evan Miya/scraper/scrape_team_ratings.py` - Added normalization
- 📄 `Evan Miya/scraper/TEAM_NAME_MAPPING.md` - Documentation
- 🔍 `Evan Miya/scraper/verify_team_names.py` - Verification tool
- 🧪 `Evan Miya/scraper/test_normalize.py` - Test script

## Need Help?

Run the verification script to see exactly which teams don't match:
```powershell
python verify_team_names.py
```

It will show you specific mismatches and suggest fixes.
