"""
CBB Analytics Scraper - Division I Team Statistics
Scrapes comprehensive team data from cbbanalytics.com including:
- Team Four Factors (Adj)
- Traditional Shooting
- Traditional Boxscore
- Boxscore Differentials
- Advanced Offense
- Advanced Defense
- Foul Related
- Scoring Context
- Win/Loss by Splits
- Win/Loss by Lead/Deficit

Team names are normalized to match KenPom format for Tableau integration.
"""

from playwright.sync_api import sync_playwright, TimeoutError as PlaywrightTimeout
import pandas as pd
from datetime import datetime
import re
import time
import os
import traceback
from typing import List, Dict, Optional
from dotenv import load_dotenv
from pathlib import Path

# Load environment variables from .env file in the same directory as this script
script_dir = Path(__file__).parent
env_path = script_dir / '.env'
load_dotenv(dotenv_path=env_path)


# Team name mapping to match KenPom format
TEAM_NAME_MAPPING = {
    "Iowa State": "Iowa St.",
    "Michigan State": "Michigan St.",
    "Connecticut": "Connecticut",
    "NC State": "N.C. State",
    "Ohio State": "Ohio St.",
    "Saint Mary's": "Saint Mary's",
    "Miami (Fla.)": "Miami FL",
    "Miami (OH)": "Miami OH",
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
    "Illinois State": "Illinois St.",
    "New Mexico State": "New Mexico St.",
    "Fresno State": "Fresno St.",
    "Morgan State": "Morgan St.",
    "Ball State": "Ball St.",
    "Sacramento State": "Sacramento St.",
    "Portland State": "Portland St.",
    "Montana State": "Montana St.",
    "Weber State": "Weber St.",
    "San Jose State": "San Jose St.",
    "Appalachian State": "Appalachian St.",
    "Arkansas State": "Arkansas St.",
    "Georgia State": "Georgia St.",
    "Louisiana State": "LSU",
    "Murray State": "Murray St.",
    "Norfolk State": "Norfolk St.",
    "North Carolina State": "N.C. State",
    "North Dakota State": "North Dakota St.",
    "South Carolina State": "South Carolina St.",
    "South Dakota State": "South Dakota St.",
    "St. John's": "St. John's",
    "St. Mary's": "Saint Mary's",
    "Alabama State": "Alabama St.",
    "Alcorn State": "Alcorn St.",
    "Arkansas-Little Rock": "Little Rock",
    "Arkansas-Pine Bluff": "Arkansas Pine Bluff",
    "Cal State Bakersfield": "Cal St. Bakersfield",
    "Cal State Fullerton": "Cal St. Fullerton",
    "Cal State Northridge": "CSUN",
    "California Baptist": "Cal Baptist",
    "Chicago State": "Chicago St.",
    "Cleveland State": "Cleveland St.",
    "College of Charleston": "Charleston",
    "Coppin State": "Coppin St.",
    "Delaware State": "Delaware St.",
    "Detroit": "Detroit Mercy",
    "East Tennessee State": "East Tennessee St.",
    "Florida International": "FIU",
    "Fort Wayne": "Purdue Fort Wayne",
    "Gardner-Webb": "Gardner Webb",
    "Grambling": "Grambling St.",
    "Idaho State": "Idaho St.",
    "Illinois-Chicago": "Illinois Chicago",
    "Indiana State": "Indiana St.",
    "Jackson State": "Jackson St.",
    "Jacksonville State": "Jacksonville St.",
    "Kennesaw State": "Kennesaw St.",
    "Kent State": "Kent St.",
    "Long Beach State": "Long Beach St.",
    "Long Island": "LIU",
    "Louisiana-Lafayette": "Louisiana",
    "Louisiana-Monroe": "Louisiana Monroe",
    "Loyola Maryland": "Loyola MD",
    "Maryland-Eastern Shore": "Maryland Eastern Shore",
    "Mississippi Valley State": "Mississippi Valley St.",
    "Missouri State": "Missouri St.",
    "Missouri-Kansas City": "Kansas City",
    "Morehead State": "Morehead St.",
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
    "Bethune-Cookman": "Bethune Cookman",
}


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


# Category configurations with required columns
# All categories are on the same page - we switch using dropdown/selector
CATEGORIES = {
    "team_four_factors": {
        "name": "Team Four Factors",
        "selector_text": "Team Four Factors",
        "columns": ["Team", "Net Rtg", "ORtg", "eFG%", "ORB%", "TOV%", "FTA Rate", "DRtg"]
    },
    "team_four_factors_adj": {
        "name": "Team Four Factors (Adj)",
        "selector_text": "Team Four Factors (Adj)",
        "columns": ["Team", "ORtg adj", "eFG% adj", "ORB% adj", "TOV% adj", "FTA Rate adj", "DRtg adj"]
    },
    "traditional_shooting": {
        "name": "Traditional Shooting",
        "selector_text": "Traditional Shooting",
        "columns": ["Team", "FTA/G", "FT%", "eFG%", "TS%", "3PAr", "FGA/G", "FG%", "2PA/G", "2P%", "3PA/G", "3P%"]
    },
    "traditional_boxscore": {
        "name": "Traditional Boxscore",
        "selector_text": "Traditional Boxscore",
        "columns": ["Team", "PTS/G", "FG%", "2P%", "3P%", "AST/G", "ORB/G", "DRB/G", "REB/G", "STL/G", "BLK/G", "TOV/G", "PF/G", "OPF/G", "PFD/G"]
    },
    "boxscore_differentials": {
        "name": "Boxscore Differentials",
        "selector_text": "Boxscore Differentials",
        "columns": ["Team", "FTM DIFF", "FTA DIFF", "REB DIFF", "TOV DIFF", "RBTV DIFF"]
    },
    "advanced_offense": {
        "name": "Advanced Offense",
        "selector_text": "Advanced Offense",
        "columns": ["Team", "ORtg", "TS%", "2P%", "3P%", "FT%", "AST%", "AST Ratio", "TOV%", "AST/TOV", "ORB%", "FTA Rate", "3PAr", "Pace"]
    },
    "advanced_defense": {
        "name": "Advanced Defense",
        "selector_text": "Advanced Defense",
        "columns": ["Team", "DRtg", "DRB", "DRB%", "STL", "STL%", "STL/TOV", "BLK", "BLK%", "HKM%", "PF", "PF/G", "PF EFF", "STL/PF", "BLK/PF"]
    },
    "foul_related": {
        "name": "Foul Related",
        "selector_text": "Foul Related",
        "columns": ["Team", "PF", "PF/G", "OPF", "OPF/G", "DPF", "DPF/G", "PFD", "PFD/G", "STL", "STL/PF", "BLK", "BLK/PF", "PF Eff"]
    },
    "scoring_context": {
        "name": "Scoring Context",
        "selector_text": "Scoring Context",
        "columns": ["Team", "ORtg", "PITP", "FBPTS", "SCP", "POTOV", "BENCH", "DRtg"]
    },
    "win_loss_splits": {
        "name": "Win/Loss by Splits",
        "selector_text": "Win/Loss by Splits",
        "columns": ["Team", "Season", "Conf", "NonC", "Last 5", "Last 10", "Home", "Away", "Neut", "Quad 1", "Quad 2", "Quad 3", "Quad 4", "Up 10", "Down 10", "Run 10-0", "Run 0-10"]
    },
    "win_loss_lead": {
        "name": "Win/Loss by Lead/Deficit",
        "selector_text": "Win/Loss by Lead/Deficit",
        "columns": ["Team", "5+", "10+", "15+", "20+", "Wins", "Loss"]
    },
}


def normalize_team_name(team_name: str) -> str:
    """
    Normalize team names to match KenPom format.
    Removes special characters and applies custom mapping.
    """
    # Convert to string if not already (handles float values)
    team_name = str(team_name) if not isinstance(team_name, str) else team_name
    
    # Remove common prefixes/numbers that might appear
    clean_name = re.sub(r'^\d+\.\s*', '', team_name).strip()
    
    # Apply custom mapping if exists
    if clean_name in TEAM_NAME_MAPPING:
        return TEAM_NAME_MAPPING[clean_name]
    
    return clean_name


class CBBAnalyticsScraper:
    """Scraper for CBBAnalytics.com team statistics."""
    
    def __init__(self, email: str, password: str):
        """
        Initialize scraper with authentication.
        
        Args:
            email: CBB Analytics account email
            password: CBB Analytics account password
        """
        self.base_url = "https://cbbanalytics.com"
        self.season_id = "41097"  # Current season ID
        self.email = email
        self.password = password
    
    def login(self, page):
        """Login to CBBAnalytics.com."""
        print("\nLogging in to CBBAnalytics.com...")
        
        try:
            # Go to home page first
            page.goto(self.base_url, wait_until='networkidle', timeout=30000)
            time.sleep(2)
            
            # Click the "Login" button to open the modal
            print("  Looking for login button...")
            try:
                # Wait for login button to be visible
                page.wait_for_selector('a.login-button', timeout=10000, state='visible')
                page.click('a.login-button')
                print("  ✓ Clicked login button")
                time.sleep(3)  # Wait for modal to fully appear
            except Exception as e:
                print(f"  ⚠️  Could not click login button: {e}")
                # Save debug HTML to see what's on the page
                with open('debug_login_page.html', 'w', encoding='utf-8') as f:
                    f.write(page.content())
                print("  Saved page to debug_login_page.html")
                return False
            
            # Try to find and fill email field with various selectors
            email_filled = False
            email_selectors = [
                'input[type="email"]',
                'input[name="email"]',
                'input[id="email"]',
                '#email',
                'input[placeholder*="email" i]',
                'input[placeholder*="Email" i]'
            ]
            
            for selector in email_selectors:
                try:
                    page.wait_for_selector(selector, timeout=5000)
                    page.fill(selector, self.email)
                    print(f"  ✓ Filled email with selector: {selector}")
                    email_filled = True
                    
                    # Check if there's a "Next" or "Continue" button for multi-step login
                    try:
                        next_button = page.query_selector('button:has-text("Next"), button:has-text("Continue")')
                        if next_button:
                            next_button.click()
                            print("  ✓ Clicked 'Next' button")
                            time.sleep(2)
                    except:
                        pass
                    
                    time.sleep(2)  # Give form time to react or show password field
                    break
                except:
                    continue
            
            if not email_filled:
                print("  ❌ Could not find email field")
                return False
            
            # Try to find and fill password field
            password_filled = False
            password_selectors = [
                'input[type="password"]',
                'input[name="password"]',
                'input[id="password"]',
                '#password',
                'input[placeholder*="password" i]'
            ]
            
            for selector in password_selectors:
                try:
                    page.wait_for_selector(selector, timeout=5000)
                    page.fill(selector, self.password)
                    print(f"  ✓ Filled password with selector: {selector}")
                    password_filled = True
                    time.sleep(1)  # Give form time to react
                    break
                except:
                    continue
            
            if not password_filled:
                print("  ❌ Could not find password field")
                return False
            
            # Click login button
            login_clicked = False
            login_button_selectors = [
                'button[type="submit"]',
                'button:has-text("Log in")',
                'button:has-text("Login")',
                'button:has-text("Sign in")',
                '.login-button',
                'input[type="submit"]',
                'button.btn'
            ]
            
            for selector in login_button_selectors:
                try:
                    page.click(selector, timeout=5000)
                    print(f"  ✓ Clicked login with selector: {selector}")
                    login_clicked = True
                    break
                except:
                    continue
            
            if not login_clicked:
                print("  ❌ Could not find login button")
                return False
            
            # Wait for navigation after login
            time.sleep(5)
            
            # Check if login was successful
            current_url = page.url.lower()
            if "login" in current_url:
                print(f"  ⚠️  Still on login page: {page.url}")
                # Save post-login page for debugging
                with open('debug_after_login.html', 'w', encoding='utf-8') as f:
                    f.write(page.content())
                return False
            else:
                print(f"  ✓ Login successful! Now at: {page.url}")
                return True
                
        except Exception as e:
            print(f"  ❌ Login error: {e}")
            return False
    
    def scrape_category(self, page, category_key: str, first_load: bool = False) -> Optional[pd.DataFrame]:
        """
        Scrape data for a specific category by selecting it from the dropdown.
        
        Args:
            page: Playwright page object (already on the stats page)
            category_key: Key from CATEGORIES dict
            first_load: Whether this is the first category (page already loaded)
            
        Returns:
            DataFrame with scraped data or None if failed
        """
        category = CATEGORIES[category_key]
        
        print(f"\nScraping {category['name']}...")
        
        try:
            # If not first load, we need to select the category
            if not first_load:
                print(f"  Switching to category: {category['selector_text']}")
                
                # Look for button/span with category name (based on HTML structure)
                selectors_to_try = [
                    f'span.button:has-text("{category["selector_text"]}")',
                    f'button:has-text("{category["selector_text"]}")',
                    f'span:has-text("{category["selector_text"]}")',
                ]
                
                category_found = False
                for selector in selectors_to_try:
                    try:
                        page.click(selector, timeout=5000)
                        print(f"  ✓ Clicked '{category['selector_text']}'")
                        category_found = True
                        time.sleep(4)  # Wait for new data to load
                        break
                    except Exception as e:
                        continue
                
                if not category_found:
                    print(f"  ⚠️  Could not switch to category")
            
            # Scroll to trigger lazy-loading
            page.evaluate("window.scrollTo(0, document.body.scrollHeight)")
            time.sleep(2)
            page.evaluate("window.scrollTo(0, 0)")
            time.sleep(2)
            # Check if we hit a login wall
            current_url = page.url.lower()
            if "login" in current_url or "sign" in current_url:
                print(f"  ⚠️  Login required - redirected to {page.url}")
                return None
            
            # Check page title
            title = page.title()
            print(f"  Page title: {title}")
            
            # Try multiple selectors for tables
            table_found = False
            selectors_to_try = [
                'table',
                '.table', 
                '[role="table"]',
                '.data-table',
                '.stats-table',
                'div.rt-table',
                'div[class*="table"]'
            ]
            
            for selector in selectors_to_try:
                try:
                    elements = page.query_selector_all(selector)
                    if elements:
                        table_found = True
                        print(f"  ✓ Found {len(elements)} table(s) with selector: {selector}")
                        break
                except:
                    continue
            
            if not table_found:
                print(f"  ⚠️  No table found - may require higher subscription tier")
                # Save debug HTML
                debug_file = f"debug_{category_key}.html"
                with open(debug_file, 'w', encoding='utf-8') as f:
                    f.write(page.content())
                return None
            
            # Get page HTML
            html_content = page.content()
            
            # Parse with pandas
            tables = pd.read_html(html_content)
            
            if not tables:
                print(f"  ⚠️  No tables found in HTML")
                return None
            
            # Get the largest table (usually the data table)
            df = max(tables, key=len) if len(tables) > 1 else tables[0]
            
            print(f"  ✓ Found table with {len(df)} rows and {len(df.columns)} columns")
            
            # Flatten MultiIndex columns if present
            if isinstance(df.columns, pd.MultiIndex):
                df.columns = ['_'.join(map(str, col)).strip('_') for col in df.columns.values]
            
            # Clean the data - separate percentile from actual values
            df = self.clean_percentile_values(df)
            
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
        All categories are on the same page - we switch between them using the category selector.
        
        Returns:
            Dictionary mapping category keys to DataFrames
        """
        print("=" * 70)
        print("CBB Analytics Scraper - Division I Statistics")
        print("=" * 70)
        
        all_data = {}
        
        with sync_playwright() as p:
            browser = p.chromium.launch(headless=True)
            
            context = browser.new_context(
                viewport={'width': 1920, 'height': 1080},
                user_agent='Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
            )
            
            page = context.new_page()
            
            # Login first
            if not self.login(page):
                print("\n❌ Login failed - cannot proceed with scraping")
                browser.close()
                return {}
            
            # Navigate to the main stats page (only once)
            url = f"{self.base_url}/stats/{self.season_id}/division/d1/team-box"
            print(f"\nNavigating to stats page: {url}")
            page.goto(url, wait_until='networkidle', timeout=60000)
            print("  ✓ Stats page loaded")
            time.sleep(5)
            
            # Change pagination to show 500 rows (all teams)
            print("\n  Changing pagination to 500 rows...")
            try:
                # Try to find and click the rows per page dropdown
                pagination_selectors = [
                    'select[aria-label*="rows"]',
                    'select.pagination-select',
                    'select[class*="pageSize"]',
                    'select[class*="per-page"]',
                    'select',  # Last resort - find any select
                ]
                
                pagination_changed = False
                for selector in pagination_selectors:
                    try:
                        # Find all select elements
                        selects = page.query_selector_all(selector)
                        for select in selects:
                            # Check if this select has option for 500
                            options = select.query_selector_all('option')
                            option_values = [opt.get_attribute('value') for opt in options]
                            
                            if '500' in option_values or '500' in [opt.inner_text() for opt in options]:
                                # Found the right select, click it and select 500
                                select.select_option('500')
                                print(f"  ✓ Changed to 500 rows per page")
                                pagination_changed = True
                                time.sleep(3)  # Wait for table to reload with all data
                                break
                    except Exception as e:
                        continue
                    
                    if pagination_changed:
                        break
                
                if not pagination_changed:
                    print(f"  ⚠️  Could not change pagination - may need manual adjustment")
            except Exception as e:
                print(f"  ⚠️  Pagination error: {e}")
            
            # Scrape each category by switching the selector
            first = True
            for category_key in CATEGORIES.keys():
                df = self.scrape_category(page, category_key, first_load=first)
                first = False
                if df is not None:
                    all_data[category_key] = df
                time.sleep(2)  # Be nice to the server
            
            browser.close()
        
        return all_data
    
    def clean_percentile_values(self, df: pd.DataFrame) -> pd.DataFrame:
        """
        Clean columns that have percentile + value concatenated.
        Uses the comprehensive clean_percentile_value function.
        """
        # Find and skip certain columns
        skip_columns = set()
        for col in df.columns:
            col_str = str(col).lower()
            # Skip team names, GP, and record columns
            if any(x in col_str for x in ['team', ' gp', 'record', 'conf']):
                skip_columns.add(col)
        
        # Process remaining columns
        for col in df.columns:
            if col in skip_columns:
                continue
            try:
                # Apply the comprehensive cleaning function to the entire column
                df[col] = df[col].apply(clean_percentile_value)
            except Exception as e:
                # If any error, leave column as-is
                pass
        
        return df
    
    def normalize_team_names_in_df(self, df: pd.DataFrame) -> pd.DataFrame:
        """Normalize team names in a DataFrame."""
        # Flatten MultiIndex columns if present
        if isinstance(df.columns, pd.MultiIndex):
            df.columns = ['_'.join(map(str, col)).strip('_') for col in df.columns.values]
        
        # Find team name column (could be 'Team', 'TEAM', etc.)
        team_col = None
        for col in df.columns:
            if isinstance(col, str) and 'team' in col.lower():
                team_col = col
                break
        
        if team_col:
            df['team_original'] = df[team_col]
            df['team_kenpom'] = df[team_col].apply(normalize_team_name)
            # Drop rows where team_kenpom is NaN or empty
            df = df[df['team_kenpom'].notna() & (df['team_kenpom'] != '')]
            # Drop duplicate teams within this category
            df = df.drop_duplicates(subset=['team_kenpom'], keep='first')
        
        return df
    
    def merge_and_export(self, all_data: Dict[str, pd.DataFrame], output_file: str = 'cbb_analytics_tableau_cleaned.csv'):
        """
        Merge all category data and export to CSV for Tableau.
        
        Args:
            all_data: Dictionary of DataFrames by category
            output_file: Output CSV filename
        """
        if not all_data:
            print("\nNo data to export")
            return
        
        print("\n" + "=" * 70)
        print("Processing and exporting data...")
        print("=" * 70)
        
        # Normalize team names in all DataFrames
        for key in all_data:
            all_data[key] = self.normalize_team_names_in_df(all_data[key])
        
        # Find a common team list (from first available category)
        first_key = list(all_data.keys())[0]
        team_col = 'team_kenpom' if 'team_kenpom' in all_data[first_key].columns else None
        
        if not team_col:
            print("Could not find team column for merging")
            # Just concatenate all data
            combined_df = pd.concat(all_data.values(), ignore_index=True)
        else:
            # Merge all categories on team name
            combined_df = None
            for key, df in all_data.items():
                # Validate data before merge
                print(f"  {key}: {len(df)} teams")
                if combined_df is None:
                    combined_df = df.copy()
                else:
                    # Add suffix to avoid column conflicts
                    suffix = f"_{key}"
                    combined_df = combined_df.merge(
                        df,
                        on=team_col,
                        how='outer',
                        suffixes=('', suffix)
                    )
                    print(f"    After merge: {len(combined_df)} rows")
        
        # Clean percentile prefixes from all numeric columns
        print("\n" + "=" * 70)
        print("Cleaning data (removing percentile prefixes)...")
        print("=" * 70)
        
        # Identify columns to clean (skip team names, records, GP)
        skip_columns = {team_col, 'team_original', 'scrape_date', 'scrape_timestamp'}
        
        # Add any column with 'team', 'record', 'gp' in name to skip list
        for col in combined_df.columns:
            col_lower = col.lower()
            if 'team' in col_lower or 'record' in col_lower or col_lower == 'gp':
                skip_columns.add(col)
        
        numeric_cols = [col for col in combined_df.columns if col not in skip_columns]
        
        print(f"  Cleaning {len(numeric_cols)} columns...")
        
        # Apply cleaning function to numeric columns
        for col in numeric_cols:
            combined_df[col] = combined_df[col].apply(clean_percentile_value)
        
        print(f"  ✓ Cleaned all numeric values")
        
        # Add scrape metadata
        combined_df['scrape_date'] = datetime.now().strftime('%Y-%m-%d')
        combined_df['scrape_timestamp'] = datetime.now().isoformat()
        
        # Export to CSV
        combined_df.to_csv(output_file, index=False)
        
        print(f"\n✓ Exported {len(combined_df)} records to {output_file}")
        print(f"  Columns: {len(combined_df.columns)}")
        print(f"  Categories scraped: {len(all_data)}")
        
        # Show sample
        if team_col and team_col in combined_df.columns:
            print(f"\nFirst 5 teams:")
            print("-" * 70)
            for idx, team in enumerate(combined_df[team_col].head(5), 1):
                print(f"  {idx}. {team}")
        
        return combined_df


def main():
    """Main scraper function."""
    # Read .env file directly
    script_dir = Path(__file__).parent
    env_path = script_dir / '.env'
    
    email = None
    password = None
    
    if env_path.exists():
        print(f"Reading .env from: {env_path}")
        with open(env_path, 'r') as f:
            for line in f:
                line = line.strip()
                if line.startswith('CBB_ANALYTICS_EMAIL='):
                    email = line.split('=', 1)[1].strip()
                elif line.startswith('CBB_ANALYTICS_PASSWORD='):
                    password = line.split('=', 1)[1].strip()
    
    if not email or not password:
        print("=" * 70)
        print("ERROR: Credentials not found!")
        print("=" * 70)
        print("\nPlease create a .env file with your credentials:")
        print("  1. Copy .env.example to .env")
        print("  2. Edit .env and add your actual email and password")
        print("\nExample .env file content:")
        print("  CBB_ANALYTICS_EMAIL=your-email@example.com")
        print("  CBB_ANALYTICS_PASSWORD=your-password")
        print("=" * 70)
        return
    
    print("=" * 70)
    print("Credentials loaded from .env file")
    print(f"Email: {email}")
    print("=" * 70)
    
    # Create scraper with authentication
    scraper = CBBAnalyticsScraper(email=email, password=password)
    
    # Scrape all categories
    all_data = scraper.scrape_all_categories()
    
    # Export to CSV
    if all_data:
        scraper.merge_and_export(all_data)
        print("\n" + "=" * 70)
        print("Scraping completed successfully!")
        print("=" * 70)
    else:
        print("\nNo data was scraped - site may require login or has access restrictions")
        print("Try accessing the site directly in a browser to check availability")


if __name__ == '__main__':
    main()
