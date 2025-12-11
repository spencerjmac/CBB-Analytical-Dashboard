# Security Review - Items to Address Before Publishing to GitHub

## ✅ SAFE - No Credentials Found
- No API keys, passwords, tokens, or secrets found in code
- No authentication credentials stored in files
- Sites are scraped as public data (no login required)

## ⚠️ PERSONAL INFORMATION TO REMOVE/REPLACE

### 1. Personal Username "spenc" in File Paths
**Files with hardcoded paths:**
- `College Logos/rename_logos_kenpom_order.py` - Lines 13, 26, 27
- `College Logos/analyze_logos.py` - Lines 9, 13
- `KenPom Data/setup_windows_task.ps1` - Lines 5, 6
- `KenPom Data/SCHEDULER_SETUP.md` - Lines 19, 44, 45
- `KenPom Data/run_daily_scrape.bat` - Line 5
- `KenPom Data/add_uv_to_path.ps1` - Line 4
- `KenPom Data/activate.ps1` - Lines 5, 22
- `KenPom Data/activate.bat` - Line 5
- `KenPom Data/README.md` - Line 24
- `README.md` - Line 230
- `Evan Miya/scraper/TEAM_NAME_MAPPING.md` - Lines 69, 76, 86
- `Evan Miya/scraper/QUICK_START.md` - Lines 16, 23, 24, 29, 30

**Action Required:** Replace all instances of `C:\Users\spenc` with generic placeholder like:
- `C:\Users\YOUR_USERNAME` or
- `%USERPROFILE%` (Windows batch) or
- `$env:USERPROFILE` (PowerShell) or
- Just use relative paths where possible

### 2. Name "Spencer" 
**Files:**
- `College Logos/README_KENPOM_ORDER.md` - Line 82: "Scraper and ordering scripts by Spencer"

**Action Required:** Consider replacing with just "Author" or leaving it (if you want credit)

### 3. Downloaded Personal Files Referenced
**Files:**
- `College Logos/rename_logos_kenpom_order.py` - References `c:\Users\spenc\Downloads\Sheet 16_Summary.csv`
- `College Logos/analyze_logos.py` - References `c:\Users\spenc\Downloads\Sheet 16_Summary.csv`

**Action Required:** Update to relative path or remove these scripts (they're one-time setup scripts)

### 4. Log Files with Personal Paths
**Files:**
- `Evan Miya/scraper/scrape_team_ratings.log` - Contains `C:\Users\spenc\AppData\Local`

**Action Required:** Delete log files (already in .gitignore)

### 5. Debug HTML Files
**Files:**
- `KenPom Data/kenpom_debug.html`
- `Evan Miya/scraper/debug_page.html`
- `Evan Miya/evanmiya_team_ratings.html`

**Action Required:** Delete these files (already in .gitignore)

## 🗑️ FILES TO DELETE BEFORE PUSH

Delete these files/folders (already covered by .gitignore):
```
# Databases
**/*.db
**/*.sqlite

# Debug files
**/debug_page.html
**/kenpom_debug.html
**/*_debug.html

# Log files
**/*.log

# Python cache
**/__pycache__/

# Virtual environment
.venv/

# Zip files
**/*.zip
```

## 📝 RECOMMENDED ACTIONS

### High Priority (Required)
1. **Create .gitignore** at root ✅ DONE
2. **Replace hardcoded paths** in all scripts with relative paths or environment variables
3. **Delete database files** (.db files with potentially personal data)
4. **Delete log files** (may contain local paths)
5. **Delete debug HTML files** (temporary files)

### Medium Priority (Recommended)
6. **Remove/sanitize QUICK_START.md** - Contains specific local paths
7. **Update setup scripts** - Use generic paths instead of hardcoded user paths
8. **Review CSV data** - Ensure no personal annotations or comments in data files

### Low Priority (Optional)
9. **Consider excluding CSV/data files** - Data files are large; users can generate their own
10. **Add LICENSE file** - Specify how others can use your code
11. **Add CONTRIBUTING.md** - If you want others to contribute

## ✅ ALREADY SECURE

These are fine to keep:
- All Python scraper code (no credentials)
- README files (informational only)
- requirements.txt files
- Database schema code (no actual data)
- Team name mapping dictionaries (public info)

## 🚀 QUICK CLEANUP SCRIPT

Run this PowerShell script before pushing:

```powershell
# Navigate to project root
cd "C:\Users\spenc\OneDrive\Workspace\Tableau Final Project"

# Remove database files
Remove-Item -Recurse -Force **/*.db
Remove-Item -Recurse -Force **/*.sqlite

# Remove log files
Remove-Item -Recurse -Force **/*.log

# Remove debug HTML
Remove-Item -Recurse -Force **/debug_page.html, **/kenpom_debug.html, **/*_debug.html

# Remove Python cache
Remove-Item -Recurse -Force **/__pycache__

# Remove zip files
Remove-Item -Recurse -Force **/*.zip

# Don't commit .venv folder
# Don't commit .db files
```

## 🔍 FINAL CHECKLIST

Before `git push`:
- [ ] .gitignore created at root level ✅
- [ ] All database files removed (.db, .sqlite)
- [ ] All log files removed (.log)
- [ ] All debug HTML files removed
- [ ] __pycache__ folders removed
- [ ] .venv folder not committed
- [ ] Personal paths replaced with generic paths or env variables
- [ ] Review `git status` - no sensitive files staged
- [ ] Test scripts work with generic paths
- [ ] README.md updated with generic setup instructions

## 📋 SUMMARY

**No sensitive credentials found!** ✅

**Main concerns:**
1. Personal username "spenc" in hardcoded file paths (not a security risk, just not portable)
2. Temporary files (logs, debug HTML, databases) should be excluded
3. Path references should be made generic for portability

**Risk Level:** LOW - Mainly portability/usability issues, not security risks
