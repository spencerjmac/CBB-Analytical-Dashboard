"""
CBB Analytics Scraper
Scrapes Division I college basketball statistics from cbbanalytics.com
Requires login credentials in .env file
Automatically cleans percentile prefixes from scraped data
"""

import os
import time
import traceback
import re
from datetime import datetime
from pathlib import Path
import pandas as pd
from playwright.sync_api import sync_playwright

# Team name mapping to match KenPom format
TEAM_NAME_MAPPING = {
    "Albany (NY)": "Albany",
    "Arkansas-Little Rock": "Little Rock",
    "Arkansas-Pine Bluff": "Arkansas Pine Bluff",
    "Bethune-Cookman": "Bethune Cookman",
    "Central Connecticut": "Central Connecticut St.",
    "Charleston Southern": "Charleston So.",
    "College of Charleston": "Col. of Charleston",
    "Connecticut": "UConn",
    "Detroit Mercy": "Detroit",
    "Florida Atlantic": "FAU",
    "Florida Gulf Coast": "Florida Gulf Coast",
    "Fordham": "Fordham",
    "Green Bay": "WI Green Bay",
    "Hawai'i": "Hawaii",
    "Illinois-Chicago": "UIC",
    "IUPUI": "IUPUI",
    "LIU Brooklyn": "LIU",
    "Long Island University": "LIU",
    "Loyola Chicago": "Loyola Chicago",
    "Loyola Maryland": "Loyola MD",
    "Louisiana-Lafayette": "Louisiana",
    "Louisiana-Monroe": "ULM",
    "LSU": "LSU",
    "Maryland-Baltimore County": "UMBC",
    "Maryland-Eastern Shore": "MD Eastern Shore",
    "Massachusetts": "Massachusetts",
    "Miami (FL)": "Miami FL",
    "Miami (OH)": "Miami OH",
    "Mississippi": "Ole Miss",
    "Missouri-Kansas City": "UMKC",
    "Mount Saint Mary's": "Mt. St. Mary's",
    "Nevada-Las Vegas": "UNLV",
    "Nevada-Reno": "Nevada",
    "North Carolina State": "NC State",
    "Nicholls State": "Nicholls",
    "Northwestern State": "Northwestern St.",
    "Omaha": "Nebraska Omaha",
    "Oregon State": "Oregon St.",
    "Prairie View": "Prairie View A&M",
    "SIU Edwardsville": "SIUE",
    "Saint Bonaventure": "St. Bonaventure",
    "Saint Francis (PA)": "Saint Francis",
    "Sam Houston State": "Sam Houston St.",
    "South Carolina Upstate": "USC Upstate",
    "Southeast Missouri State": "Southeast Missouri",
    "Southern Mississippi": "Southern Miss",
    "St. Thomas (MN)": "St. Thomas",
    "Tarleton State": "Tarleton St.",
    "Tennessee State": "Tennessee St.",
    "Tennessee-Martin": "Tennessee Martin",
    "Texas A&M-Corpus Christi": "Texas A&M Corpus Chris",
    "Texas State": "Texas St.",
    "Texas-Rio Grande Valley": "UT Rio Grande Valley",
    "Washington State": "Washington St.",
    "Wright State": "Wright St.",
    "Youngstown State": "Youngstown St.",
}


def clean_percentile_value(val):
    """
    Remove percentile prefix from values
    CBB Analytics displays percentile rankings alongside actual values,
    which get scraped as concatenated strings (e.g., "2347.9%" = percentile 23 + actual 47.9%)
    """
    if pd.isna(val) or val == '' or val == '-':
        return val
    
    val_str = str(val).strip()
    
    if len(val_str) < 4:
        return val
    
    # Check if value is already clean (no percentile prefix needed)
    # Values already in typical ranges don't need cleaning
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
            # If value is in these ranges AND has reasonable length AND no leading zeros, it might be clean
            has_leading_zero = val_str[0] == '0' and len(val_str) > 3  # "093.6" or "0130.4"
            if (not has_leading_zero and
                (85 <= val_float <= 130 or 50 <= val_float <= 100 or 0 <= val_float <= 20) 
                and len(val_str) <= 6):  # e.g., "88.1" or "93.9" (not "1199.7" or "093.6")
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
            # If value is already in expected ranges and short enough, it's probably clean
            # BUT: Check for leading zeros (e.g., "0130.4") or values that are too long
            # Clean values should be like "130.4" (5 chars), not "0130.4" (6 chars with leading 0)
            has_leading_zero = val_str[0] == '0' and len(val_str) > 4  # "0130.4" has leading 0
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
            
            # First priority: ORtg/DRtg range (85-135) - extended to 135 to catch outliers
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


# KenPom team name mapping for Tableau joins
KENPOM_TEAM_MAPPING = {
    'A&M-Corpus Christi': 'Texas A&M Corpus Chris',
    'Alcorn': 'Alcorn St.',
    'App State': 'Appalachian St.',
    'Ark.-Pine Bluff': 'Arkansas Pine Bluff',
    'Army West Point': 'Army',
    'Boston U.': 'Boston University',
    'CSU Bakersfield': 'Cal St. Bakersfield',
    'California Baptist': 'Cal Baptist',
    'Central Ark.': 'Central Arkansas',
    'Central Conn. St.': 'Central Connecticut',
    'Central Mich.': 'Central Michigan',
    'Charleston So.': 'Charleston Southern',
    'Col. of Charleston': 'Charleston',
    'Detroit': 'Detroit Mercy',
    'ETSU': 'East Tennessee St.',
    'Eastern Ill.': 'Eastern Illinois',
    'Eastern Ky.': 'Eastern Kentucky',
    'Eastern Mich.': 'Eastern Michigan',
    'Eastern Wash.': 'Eastern Washington',
    'FDU': 'Fairleigh Dickinson',
    'FGCU': 'Florida Gulf Coast',
    'Fla. Atlantic': 'Florida Atlantic',
    'Ga. Southern': 'Georgia Southern',
    'Gardner-Webb': 'Gardner Webb',
    'Grambling': 'Grambling St.',
    'LMU (CA)': 'Loyola Marymount',
    'Lamar University': 'Lamar',
    'Middle Tenn.': 'Middle Tennessee',
    'Mississippi Val.': 'Mississippi Valley St.',
    'N.C. A&T': 'North Carolina A&T',
    'N.C. Central': 'North Carolina Central',
    'NC State': 'N.C. State',
    'NIU': 'Northern Illinois',
    'North Ala.': 'North Alabama',
    'Northern Ariz.': 'Northern Arizona',
    'Northern Colo.': 'Northern Colorado',
    'Northern Ky.': 'Northern Kentucky',
    'Ole Miss': 'Mississippi',
    'Queens (NC)': 'Queens',
    'SFA': 'Stephen F. Austin',
    "Saint Mary's (CA)": "Saint Mary's",
    'Sam Houston': 'Sam Houston St.',
    'Seattle U': 'Seattle',
    'South Fla.': 'South Florida',
    'Southeast Mo. St.': 'Southeast Missouri',
    'Southeastern La.': 'Southeastern Louisiana',
    'Southern California': 'USC',
    'Southern Ill.': 'Southern Illinois',
    'Southern Ind.': 'Southern Indiana',
    'Southern Miss.': 'Southern Miss',
    'Southern U.': 'Southern',
    "St. John's (NY)": "St. John's",
    'UAlbany': 'Albany',
    'UConn': 'Connecticut',
    'UIC': 'Illinois Chicago',
    'UIW': 'Incarnate Word',
    'ULM': 'Louisiana Monroe',
    'UMES': 'Maryland Eastern Shore',
    'UNCW': 'UNC Wilmington',
    'UNI': 'Northern Iowa',
    'UT Martin': 'Tennessee Martin',
    'UTRGV': 'UT Rio Grande Valley',
    'WI Green Bay': 'Green Bay',
    'West Ga.': 'West Georgia',
    'Western Caro.': 'Western Carolina',
    'Western Ill.': 'Western Illinois',
    'Western Ky.': 'Western Kentucky',
    'Western Mich.': 'Western Michigan',
}


# Category configurations with required columns
CATEGORIES = {
    # "team_four_factors": {
    #     "name": "Team Four Factors",
    #     "selector_text": "Team Four Factors",
    #     "columns": ["Team", "Net Rtg", "ORtg", "eFG%", "ORB%", "TOV%", "FTA Rate", "DRtg"]
    # },
    "team_four_factors_adj": {
        "name": "Team Four Factors Adj",
        "selector_text": "Team Four Factors Adj",
        "columns": [
            "Team", 
            "Net Rtg", 
            "Team 4-Factors_ORtg", 
            "Team 4-Factors_eFG%", 
            "Team 4-Factors_ORB%", 
            "Team 4-Factors_TOV%", 
            "Team 4-Factors_FTA Rate",
            "Opponent 4-Factors_DRtg",
            "Opponent 4-Factors_eFG%",
            "Opponent 4-Factors_TOV%",
            "Opponent 4-Factors_FTA Rate"
        ]
    },
    # "traditional_shooting": {
    #     "name": "Traditional Shooting",
    #     "selector_text": "Traditional Shooting",
    #     "columns": ["Team", "FTA/G", "FT%", "eFG%", "TS%", "3PAr", "FGA/G", "FG%", "2PA/G", "2P%", "3PA/G", "3P%"]
    # },
    "traditional_boxscore": {
        "name": "Traditional Boxscore",
        "selector_text": "Traditional Boxscore",
        "columns": ["Team", "PTS/G", "AST/G", "TOV/G", "ORB/G", "DRB/G", "TRB/G", "STL/G", "BLK/G", "PF/G"]
    },
    "boxscore_differentials": {
        "name": "Boxscore Differentials",
        "selector_text": "Boxscore Differentials",
        "columns": ["Team", "Pt Diff/G", "AST Diff/G", "TOV Diff/G", "ORB Diff/G", "DRB Diff/G", "STL Diff/G", "BLK Diff/G", "PF Diff/G"]
    },
    "advanced_offense": {
        "name": "Advanced Offense",
        "selector_text": "Advanced Offense",
        "columns": ["Team", "ORtg", "eFG%", "FTA/100 Poss", "ORB%", "TOV%", "3PA%", "2P%", "3P%", "2P eFG%"]
    },
    "advanced_defense": {
        "name": "Advanced Defense",
        "selector_text": "Advanced Defense",
        "columns": ["Team", "DRtg", "eFG% allowed", "FTA/100 Poss allowed", "DRB%", "TOV% forced", "3PA% allowed", "2P% allowed", "3P% allowed"]
    },
    "foul_related": {
        "name": "Foul Related",
        "selector_text": "Foul Related",
        "columns": ["Team", "PF/G", "PF/G allowed", "FTA/FGA", "FTA/FGA allowed", "And-1 Rate", "And-1 Rate allowed"]
    },
    "scoring_context": {
        "name": "Scoring Context",
        "selector_text": "Scoring Context",
        "columns": ["Team", "Pts from 2P/G", "Pts from 3P/G", "Pts from FT/G", "Pts from Paint/G", "Pts from Midrange/G", "2nd Chance Pts/G", "Fast Break Pts/G"]
    },
    "win_loss_by_splits": {
        "name": "Win/Loss by Splits",
        "selector_text": "Win/Loss by Splits",
        "columns": ["Team", "Conf Record", "Non-Conf Record", "Home Record", "Away Record", "Neutral Record"]
    },
    "win_loss_by_lead_deficit": {
        "name": "Win/Loss by Lead/Deficit",
        "selector_text": "Win/Loss by Lead/Deficit",
        "columns": ["Team", "Games Played", "Record When Trailing", "Record When Leading", "Avg Lead When Ahead", "Avg Deficit When Behind"]
    }
}


class CBBAnalyticsScraper:
    def __init__(self):
        self.base_url = "https://cbbanalytics.com"
        self.season_id = "41097"  # 2025-26 season
        self.stats_url = f"{self.base_url}/stats/{self.season_id}/division/d1/team-box"
        
        # Load credentials
        env_path = Path(__file__).parent / '.env'
        self.email = None
        self.password = None
        
        if env_path.exists():
            with open(env_path, 'r') as f:
                for line in f:
                    line = line.strip()
                    if line and not line.startswith('#'):
                        if '=' in line:
                            key, value = line.split('=', 1)
                            key = key.strip()
                            value = value.strip().strip('"').strip("'")
                            if key == 'CBB_ANALYTICS_EMAIL':
                                self.email = value
                            elif key == 'CBB_ANALYTICS_PASSWORD':
                                self.password = value
        
        if not self.email or not self.password:
            raise ValueError("Missing credentials in .env file")
    
    def login(self, page):
        """Login to CBB Analytics"""
        print("\nLogging in to CBB Analytics...")
        
        try:
            # Go to homepage with more flexible wait
            print(f"  Loading {self.base_url}...")
            page.goto(self.base_url, wait_until="domcontentloaded", timeout=90000)
            time.sleep(3)
            
            # Click login button in navbar
            login_buttons = [
                'a:has-text("Login")',
                'button:has-text("Login")',
                '.login-link',
                'a[href*="login"]'
            ]
            
            clicked_login = False
            for selector in login_buttons:
                try:
                    page.click(selector, timeout=5000)
                    print(f"  ✓ Clicked login button")
                    clicked_login = True
                    time.sleep(2)
                    break
                except:
                    continue
            
            if not clicked_login:
                print("  ❌ Could not find login button")
                return False
            
            # Fill email
            email_selectors = [
                'input[type="email"]',
                'input[name="email"]',
                'input[id="email"]',
                'input[placeholder*="email" i]'
            ]
            
            email_filled = False
            for selector in email_selectors:
                try:
                    page.wait_for_selector(selector, timeout=5000)
                    page.fill(selector, self.email)
                    print(f"  ✓ Filled email")
                    email_filled = True
                    time.sleep(1)
                    break
                except:
                    continue
            
            if not email_filled:
                print("  ❌ Could not find email field")
                return False
            
            # Click Next button
            next_button_selectors = [
                'button:has-text("Next")',
                'button[type="submit"]',
                'button:has-text("Continue")'
            ]
            
            next_clicked = False
            for selector in next_button_selectors:
                try:
                    page.click(selector, timeout=5000)
                    print(f"  ✓ Clicked Next button")
                    next_clicked = True
                    time.sleep(2)
                    break
                except:
                    continue
            
            if not next_clicked:
                print("  ⚠️  No Next button found, continuing...")
            
            # Fill password
            password_selectors = [
                'input[type="password"]',
                'input[name="password"]',
                'input[id="password"]',
                'input[placeholder*="password" i]'
            ]
            
            password_filled = False
            for selector in password_selectors:
                try:
                    page.wait_for_selector(selector, timeout=5000)
                    page.fill(selector, self.password)
                    print(f"  ✓ Filled password")
                    password_filled = True
                    time.sleep(1)
                    break
                except:
                    continue
            
            if not password_filled:
                print("  ❌ Could not find password field")
                return False
            
            # Click login submit button
            login_clicked = False
            submit_selectors = [
                'button[type="submit"]',
                'button:has-text("Log in")',
                'button:has-text("Login")',
                'button:has-text("Sign in")'
            ]
            
            for selector in submit_selectors:
                try:
                    page.click(selector, timeout=5000)
                    print(f"  ✓ Clicked login submit")
                    login_clicked = True
                    break
                except:
                    continue
            
            if not login_clicked:
                print("  ❌ Could not find login submit button")
                return False
            
            # Wait for navigation
            time.sleep(5)
            
            # Check if login successful
            current_url = page.url.lower()
            if "login" in current_url:
                print(f"  ⚠️  Still on login page")
                return False
            
            print(f"  ✓ Login successful!")
            return True
            
        except Exception as e:
            print(f"  ❌ Login failed: {str(e)}")
            traceback.print_exc()
            return False
    
    def clean_numeric_columns(self, df):
        """Clean numeric columns by removing percentile values that are concatenated"""
        import re
        
        for col in df.columns:
            # Skip team-related columns
            if 'team' in col.lower() or col == 'team_kenpom':
                continue
            
            # Check if column has values that look like they have percentiles concatenated
            if df[col].dtype == 'object':
                def extract_first_number(val):
                    if pd.isna(val):
                        return val
                    val_str = str(val)
                    # Match pattern like "126.2" or "-5.3" at the start, ignore what comes after
                    # This handles cases like "95126.2" -> "126.2" or "126.2" -> "126.2"
                    match = re.search(r'^(\d+)?(-?\d+\.?\d*)', val_str)
                    if match:
                        # If we have a digit followed by another number, take the second (e.g., "95126.2" -> "126.2")
                        if match.group(1) and match.group(2):
                            # Check if this looks like percentile + value (e.g., 95126.2)
                            full_match = match.group(1) + match.group(2)
                            # If the first group is 2 digits and looks like percentile (0-100)
                            if len(match.group(1)) <= 2 and int(match.group(1)) <= 100:
                                return match.group(2)
                            return full_match
                        # Otherwise just return the number
                        return match.group(2) if match.group(2) else match.group(1)
                    return val
                
                df[col] = df[col].apply(extract_first_number)
        
        return df
    
    def normalize_team_names_in_df(self, df):
        """Normalize team names in DataFrame"""
        # Check for various possible team column names
        team_col = None
        possible_names = ['Team', 'TEAM', 'team', 'Team Name', 'School', 'school']
        
        for col_name in possible_names:
            if col_name in df.columns:
                team_col = col_name
                break
        
        # If no exact match, look for column containing 'team' or 'school'
        if team_col is None:
            for col in df.columns:
                if 'team' in str(col).lower() or 'school' in str(col).lower():
                    team_col = col
                    break
        
        if team_col is None:
            # Use first column as team column
            team_col = df.columns[0]
            print(f"    Using first column as team: '{team_col}'")
        
        def normalize_name(name):
            if pd.isna(name):
                return name
            name_str = str(name).strip()
            return TEAM_NAME_MAPPING.get(name_str, name_str)
        
        df['team_kenpom'] = df[team_col].apply(normalize_name)
        return df
    
    def scrape_category(self, page, category_key, first_load=True):
        """
        Scrape a specific category from CBB Analytics.
        All categories are on the same page - we switch using buttons/selector.
        
        Args:
            page: Playwright page object
            category_key: Key for CATEGORIES dict
            first_load: Whether this is the first category (page already loaded)
        
        Returns:
            DataFrame with scraped data or None if failed
        """
        category = CATEGORIES[category_key]
        
        print(f"\nScraping {category['name']}...")
        
        try:
            # ALWAYS switch to the correct category, even on first load
            # (The page may not start on the category we want)
            print(f"  Switching to category: {category['selector_text']}")
            
            try:
                # Click the React-Select dropdown to open it (force click to bypass overlay)
                page.click('.cbb-select.cbb-table-types-select', force=True, timeout=5000)
                time.sleep(1)
                
                # DEBUG: Print all available dropdown options
                if first_load:  # Only print on first load to avoid spam
                    print("  📋 Available dropdown options:")
                    try:
                        options = page.locator('div[role="option"]').all_text_contents()
                        for i, opt in enumerate(options):
                            print(f"      {i+1}. '{opt}'")
                    except Exception as debug_e:
                        print(f"      Could not read options: {debug_e}")
                
                # Try clicking the option with the category name
                # Try multiple variations of the selector
                selectors_to_try = [
                    f'text="{category["selector_text"]}"',
                    f'div[role="option"]:has-text("{category["selector_text"]}")',
                    f'[class*="option"]:has-text("{category["selector_text"]}")',
                ]
                
                clicked_option = False
                for selector in selectors_to_try:
                    try:
                        page.click(selector, timeout=5000)
                        print(f"  ✓ Selected '{category['selector_text']}'")
                        clicked_option = True
                        break
                    except:
                        continue
                
                if not clicked_option:
                    print(f"  ⚠️  Could not find option: {category['selector_text']}")
                    return None
                time.sleep(4)  # Wait for data to load
                
            except Exception as e:
                print(f"  ⚠️  Could not switch to category: {str(e)}")
                return None
            
            # Change page size to 500 to get all teams at once
            try:
                print(f"  Setting page size to 500...")
                # Look for the "Show 25" dropdown (various possible selectors)
                page_size_selectors = [
                    'select:has-text("25")',
                    'select[name*="page"]',
                    'select[name*="size"]',
                    '[class*="page-size"] select',
                    'div:has-text("Show") select',
                    'text="Show 25" >> .. >> select'
                ]
                
                page_size_changed = False
                for selector in page_size_selectors:
                    try:
                        if page.locator(selector).count() > 0:
                            page.select_option(selector, value='500')
                            print(f"  ✓ Changed page size to 500")
                            page_size_changed = True
                            time.sleep(4)  # Wait for table to reload with all teams
                            break
                    except:
                        continue
                
                if not page_size_changed:
                    # Try clicking approach for React Select
                    try:
                        # Look for text "Show 25" or "25" near bottom of page
                        page.click('text="Show 25"', timeout=3000)
                        time.sleep(1)
                        page.click('text="500"', timeout=3000)
                        print(f"  ✓ Changed page size to 500")
                        time.sleep(4)
                    except:
                        print(f"  ⚠️  Could not change page size, using default (25)")
            except Exception as e:
                print(f"  ⚠️  Page size change failed: {str(e)}")
            
            # Scroll to trigger lazy loading
            page.evaluate("window.scrollTo(0, document.body.scrollHeight)")
            time.sleep(2)
            page.evaluate("window.scrollTo(0, 0)")
            time.sleep(2)
            
            # Get HTML and parse tables (should have all 365 teams if page size was set to 500)
            print(f"  Extracting table data...")
            html = page.content()
            tables = pd.read_html(html)
            
            if not tables:
                print(f"  ⚠️  No tables found")
                return None
            
            # Get the largest table (usually the data table)
            df = max(tables, key=len) if len(tables) > 1 else tables[0]
            
            # Flatten MultiIndex columns if present
            if isinstance(df.columns, pd.MultiIndex):
                df.columns = ['_'.join(map(str, col)).strip('_') for col in df.columns.values]
            
            print(f"  ✓ Found table with {len(df)} rows and {len(df.columns)} columns")
            
            # Normalize team names
            df = self.normalize_team_names_in_df(df)
            
            return df
            
        except Exception as e:
            print(f"  ❌ Error scraping {category['name']}: {str(e)}")
            traceback.print_exc()
            return None
    
    def scrape_all_categories(self):
        """
        Scrape all stat categories from CBB Analytics.
        All categories are on the same page - we switch between them.
        
        Returns:
            Dictionary mapping category keys to DataFrames
        """
        print("=" * 70)
        print("CBB Analytics Scraper - Division I Statistics")
        print("=" * 70)
        
        all_data = {}
        
        with sync_playwright() as p:
            # Launch browser
            browser = p.chromium.launch(headless=False)  # Visible for debugging
            context = browser.new_context(
                viewport={'width': 1920, 'height': 1080},
                user_agent='Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
            )
            page = context.new_page()
            
            try:
                # Login first
                if not self.login(page):
                    print("\n❌ Login failed - cannot proceed")
                    return all_data
                
                # Navigate to stats page
                print(f"\nNavigating to stats page...")
                page.goto(self.stats_url, wait_until="domcontentloaded", timeout=90000)
                time.sleep(5)
                
                print(f"  ✓ Loaded page: {page.title()}")
                
                # Scrape all categories from the same page
                first_load = True
                for category_key in CATEGORIES.keys():
                    df = self.scrape_category(page, category_key, first_load=first_load)
                    if df is not None:
                        all_data[category_key] = df
                    first_load = False
                    time.sleep(2)  # Pause between categories
                
            except Exception as e:
                print(f"\n❌ Fatal error: {str(e)}")
                traceback.print_exc()
            finally:
                browser.close()
        
        print("\n" + "=" * 70)
        print(f"Scraping complete! Collected {len(all_data)}/{len(CATEGORIES)} categories")
        print("=" * 70)
        
        return all_data
    
    def merge_and_export(self, all_data, output_file="cbb_analytics_tableau_cleaned.csv"):
        """Merge all category DataFrames, clean data (remove percentile prefixes), and export to CSV"""
        if not all_data:
            print("\n⚠️  No data to export")
            return
        
        print(f"\nMerging {len(all_data)} categories...")
        
        # Start with the first DataFrame
        merged_df = None
        
        for category_key, df in all_data.items():
            category = CATEGORIES[category_key]
            print(f"  Processing {category['name']}: {len(df)} teams, {len(df.columns)} columns")
            
            if 'team_kenpom' not in df.columns:
                print(f"    ⚠️  Missing team_kenpom column, skipping")
                continue
            
            # Keep ALL columns from the DataFrame
            df_filtered = df.copy()
            
            # Rename columns to include category prefix (except team_kenpom)
            rename_dict = {col: f"{category_key}_{col}" for col in df_filtered.columns if col != 'team_kenpom'}
            df_filtered = df_filtered.rename(columns=rename_dict)
            
            print(f"    ✓ Keeping {len(df_filtered.columns)-1} stat columns")
            
            # Merge
            if merged_df is None:
                merged_df = df_filtered
            else:
                merged_df = merged_df.merge(df_filtered, on='team_kenpom', how='outer')
        
        if merged_df is None:
            print("  ❌ No data to merge")
            return
        
        print("\n" + "="*70)
        print("Cleaning data (removing percentile prefixes)...")
        print("="*70)
        
        # Apply cleaning to all numeric columns
        numeric_cols = []
        for col in merged_df.columns:
            if col not in ['team_kenpom', 'Record', 'Conf_Record', 'GP']:
                # Check if column has numeric-like values
                sample = merged_df[col].dropna().head(5)
                if len(sample) > 0:
                    try:
                        # Try to convert to string and check if it looks numeric
                        str_val = str(sample.iloc[0])
                        if any(c.isdigit() for c in str_val):
                            numeric_cols.append(col)
                    except:
                        pass
        
        print(f"  Cleaning {len(numeric_cols)} columns...")
        
        # Apply cleaning function to numeric columns
        for col in numeric_cols:
            merged_df[col] = merged_df[col].apply(clean_percentile_value)
        
        print(f"  ✓ Cleaned all numeric values")
        
        print("\n" + "="*70)
        print("Cleaning column names...")
        print("="*70)
        
        # Remove category prefixes from column names
        # e.g., "traditional_boxscore_PTS/G" -> "PTS/G"
        rename_dict = {}
        for col in merged_df.columns:
            if col not in ['team_kenpom', 'kenpom_team_name', 'scrape_date', 'scrape_timestamp', 'season_id']:
                # Split by underscore and take the last part as the clean name
                # Handle cases like "traditional_boxscore_Traditional Box Score_PTS/G" -> "PTS/G"
                parts = col.split('_')
                clean_name = parts[-1]  # Get the last part (the actual stat name)
                
                # If we already have this column name, append a number to avoid duplicates
                if clean_name in rename_dict.values():
                    counter = 2
                    while f"{clean_name}_{counter}" in rename_dict.values():
                        counter += 1
                    clean_name = f"{clean_name}_{counter}"
                
                rename_dict[col] = clean_name
        
        merged_df = merged_df.rename(columns=rename_dict)
        print(f"  ✓ Cleaned {len(rename_dict)} column names")
        
        print("\nRemoving null columns...")
        # Remove columns that are completely null
        null_cols = merged_df.columns[merged_df.isnull().all()].tolist()
        if null_cols:
            merged_df = merged_df.drop(columns=null_cols)
            print(f"  ✓ Removed {len(null_cols)} completely null columns")
        else:
            print(f"  ✓ No null columns to remove")
        
        # Add KenPom team name mapping for Tableau joins
        print("\nAdding KenPom team name mapping...")
        merged_df['kenpom_team_name'] = merged_df['team_kenpom'].apply(
            lambda x: KENPOM_TEAM_MAPPING.get(x, x)
        )
        mapped_count = (merged_df['kenpom_team_name'] != merged_df['team_kenpom']).sum()
        print(f"  ✓ Mapped {mapped_count} team names for KenPom compatibility")
        
        # Add metadata
        merged_df['scrape_date'] = datetime.now().strftime('%Y-%m-%d')
        merged_df['scrape_timestamp'] = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        merged_df['season_id'] = self.season_id
        
        # Sort by team name
        merged_df = merged_df.sort_values('team_kenpom')
        
        # Export - default to cleaned file
        merged_df.to_csv(output_file, index=False)
        
        print("\n" + "="*70)
        print(f"✓ Exported cleaned data: {output_file}")
        print("="*70)
        print(f"  Teams: {len(merged_df)}")
        print(f"  Columns: {len(merged_df.columns)}")
        print(f"  All percentile prefixes removed")
        print(f"  KenPom team names added")
        print(f"  Ready for Tableau!")
        print("="*70)


def main():
    """Main execution function"""
    scraper = CBBAnalyticsScraper()
    
    # Scrape all categories
    all_data = scraper.scrape_all_categories()
    
    # Merge and export
    if all_data:
        scraper.merge_and_export(all_data)
    else:
        print("\n❌ No data scraped")


if __name__ == "__main__":
    main()
