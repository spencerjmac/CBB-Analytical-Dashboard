"""
CBB Analytics Scraper V2 - Streamlined Column Selection
Scrapes only specific columns from CBBAnalytics.com for Tableau dashboard
"""

import os
import re
import time
import pandas as pd
from playwright.sync_api import sync_playwright
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Column mapping: original pattern -> desired output name
COLUMN_MAPPING = {
    # Team Four Factors
    'team_four_factors': {
        'Net Rtg': 'Net Rtg',
        'ORtg': 'ORtg',
        'eFG%': 'eFG%',
        'ORB%': 'ORB%',
        'TOV%': 'TOV%',
        'FTA Rate': 'FTA Rate',
        'DRtg': 'DRtg',
        'Opponent_eFG%': 'Opponent eFG%',
        'Opponent_ORB%': 'Opponent ORB%',
        'Opponent_TOV%': 'Opponent TOV%',
        'Opponent_FTA Rate': 'Opponent FTA Rate'
    },
    # Team Four Factors (Adj)
    'team_four_factors_adj': {
        'Net Rtg': 'Net Rtg Adj',
        'ORtg': 'ORtg Adj',
        'eFG%': 'eFG% Adj',
        'ORB%': 'ORB% Adj',
        'TOV%': 'TOV% Adj',
        'FTA Rate': 'FTA Rate Adj',
        'DRtg': 'DRtg Adj',
        'Opponent_eFG%': 'Opponent eFG% Adj',
        'Opponent_ORB%': 'Opponent ORB% Adj',
        'Opponent_TOV%': 'Opponent TOV% Adj',
        'Opponent_FTA Rate': 'Opponent FTA Rate Adj'
    },
    # Traditional Shooting
    'traditional_shooting': {
        'FGA/G': 'FGA/G',
        'FG%': 'FG%',
        '2PA/G': '2PA/G',
        '2P%': '2P%',
        '3PA/G': '3PA/G',
        '3P%': '3P%',
        'FTA/G': 'FTA/G',
        'FT%': 'FT%',
        'TS%': 'TS%',
        '3PAr': '3PAr'
    },
    # Traditional Boxscore
    'traditional_boxscore': {
        'PTS/G': 'PTS/G',
        'AST/G': 'AST/G',
        'ORB/G': 'ORB/G',
        'DRB/G': 'DRB/G',
        'REB/G': 'REB/G',
        'STL/G': 'STL/G',
        'BLK/G': 'BLK/G',
        'TOV/G': 'TOV/G',
        'PF/G': 'PF/G',
        'OPF/G': 'OPF/G',
        'PFD/G': 'PFD/G'
    },
    # Advanced Offense
    'advanced_offense': {
        'AST%': 'AST%',
        'AST/TOV': 'AST/TOV',
        'Pace': 'Pace'
    },
    # Advanced Defense
    'advanced_defense': {
        'DRB%': 'DRB%',
        'STL%': 'STL%',
        'STL/TOV': 'STL/TOV',
        'BLK%': 'BLK%',
        'HKM%': 'HKM%',
        'PF/G': 'PF/G Def',
        'PF Eff': 'PF Eff',
        'STL/PF': 'STL/PF',
        'BLK/PF': 'BLK/PF'
    },
    # Scoring Context
    'scoring_context': {
        'PITP': 'PITP',
        'FBPTS': 'FBPTS',
        'SCP': 'SCP',
        'POTOV': 'POTOV',
        'BENCH': 'BENCH',
        'Opponent_PITP': 'Opponent PITP',
        'Opponent_FBPTS': 'Opponent FBPTS',
        'Opponent_SCP': 'Opponent SCP',
        'Opponent_POTOV': 'Opponent POTOV',
        'Opponent_BENCH': 'Opponent BENCH'
    },
    # Win/Loss Splits
    'win_loss_splits': {
        'Season Record': 'Season Record',
        'Conference Record': 'Conference Record',
        'NonC Record': 'NonC Record',
        'Last 5': 'Last 5',
        'Last 10': 'Last 10',
        'Home': 'Home',
        'Away': 'Away',
        'Neutral': 'Neutral',
        'Quad 1': 'Quad 1',
        'Quad 2': 'Quad 2',
        'Quad 3': 'Quad 3',
        'Quad 4': 'Quad 4',
        'Up 10': 'Up 10',
        'Down 10': 'Down 10',
        'Run 10-0': 'Run 10-0',
        'Run 0-10': 'Run 0-10'
    }
}

# Team name mapping to match KenPom format
TEAM_NAME_MAPPING = {
    'A&M-Corpus Chris': 'Texas A&M Corpus Chris',
    'Albany (NY)': 'Albany',
    'American': 'American Univ.',
    'Appalachian St.': 'Appalachian St',
    'Ark.-Pine Bluff': 'Arkansas Pine Bluff',
    'Arkansas St.': 'Arkansas St',
    'Bethune-Cookman': 'Bethune Cookman',
    'Bowling Green St.': 'Bowling Green',
    'Cal Baptist': 'California Baptist',
    'Cal St. Bakersfield': 'CS Bakersfield',
    'Cal St. Fullerton': 'CS Fullerton',
    'Cal St. Northridge': 'CS Northridge',
    'Central Conn. St.': 'Central Connecticut',
    'Charleston So.': 'Charleston Southern',
    'Col. of Charleston': 'Charleston',
    'Connecticut': 'UConn',
    'Detroit Mercy': 'Detroit',
    'E. Washington': 'Eastern Washington',
    'Fairleigh Dickinson': 'F Dickinson',
    'Florida Atlantic': 'Fla Atlantic',
    'Florida Gulf Coast': 'Fla Gulf Coast',
    'Florida Int\'l': 'Florida Intl',
    'Grambling': 'Grambling St',
    'Green Bay': 'WI Green Bay',
    'IL-Chicago': 'Ill Chicago',
    'Jackson St.': 'Jackson St',
    'Kansas City': 'UMKC',
    'La.-Monroe': 'Louisiana Monroe',
    'LIU': 'LIU Brooklyn',
    'Little Rock': 'Arkansas Little Rock',
    'Loyola Chicago': 'Loyola-Chicago',
    'Loyola Maryland': 'Loyola MD',
    'Loyola Marymount': 'Loy Marymount',
    'LSU': 'Louisiana St',
    'McNeese': 'McNeese St',
    'Miami (FL)': 'Miami FL',
    'Miami (OH)': 'Miami OH',
    'Miss Valley St.': 'Mississippi Valley St',
    'Missouri St.': 'Missouri St',
    'Monmouth': 'Monmouth NJ',
    'Montana St.': 'Montana St',
    'Morehead St.': 'Morehead St',
    'Morgan St.': 'Morgan St',
    'Mt. St. Mary\'s': 'Mt St Marys',
    'N.C. A&T': 'NC A&T',
    'N.C. Central': 'North Carolina Central',
    'N.C. State': 'North Carolina St',
    'Nebraska-Omaha': 'Omaha',
    'Nevada-Las Vegas': 'UNLV',
    'North Florida': 'N Florida',
    'Northern Colo.': 'Northern Colorado',
    'Northern Ky.': 'Northern Kentucky',
    'Ole Miss': 'Mississippi',
    'Penn St.': 'Penn St',
    'Pepperdine': 'Pepperdine',
    'Prairie View': 'Prairie View A&M',
    'Presbyterian': 'Presbyterian',
    'Purdue Fort Wayne': 'Fort Wayne',
    'Queens (NC)': 'Queens',
    'Saint Francis (PA)': 'St Francis PA',
    'Saint Joseph\'s': 'St Josephs',
    'Saint Louis': 'St Louis',
    'Saint Mary\'s (CA)': 'St Marys',
    'Saint Peter\'s': 'St Peters',
    'San Francisco': 'San Francisco',
    'San José State': 'San Jose St',
    'SC State': 'South Carolina St',
    'SE Louisiana': 'Southeastern Louisiana',
    'SE Missouri St.': 'Southeast Missouri St',
    'SFA': 'Stephen F Austin',
    'SIU-Edwardsville': 'SIU Edwardsville',
    'SMU': 'Southern Methodist',
    'Southern California': 'USC',
    'Southern Miss.': 'Southern Miss',
    'Southern Utah': 'Southern Utah',
    'St. Bonaventure': 'St Bonaventure',
    'St. Francis Brooklyn': 'St Francis NY',
    'St. John\'s (NY)': 'St Johns',
    'St. Thomas': 'St Thomas MN',
    'TCU': 'Texas Christian',
    'Tennessee St.': 'Tennessee St',
    'Tennessee-Martin': 'UT Martin',
    'Texas A&M': 'Texas A&M',
    'Texas Southern': 'Texas Southern',
    'Texas St.': 'Texas St',
    'Tex.-Arlington': 'UT Arlington',
    'Tex.-Rio Grande Valley': 'UT Rio Grande Valley',
    'UMASS-Lowell': 'Mass Lowell',
    'UMass': 'Massachusetts',
    'UNCG': 'UNC Greensboro',
    'UNCW': 'UNC Wilmington',
    'UT-San Antonio': 'UT San Antonio',
    'VCU': 'Virginia Commonwealth',
    'Western Caro.': 'Western Carolina',
    'Western Ky.': 'Western Kentucky',
    'William & Mary': 'William and Mary',
    'Winthrop': 'Winthrop'
}


def clean_percentile_value(value):
    """
    Remove percentile ranking prefix from values
    Examples: '98128.6' -> '128.6', '9960.5%' -> '60.5%'
    """
    if pd.isna(value) or value == '':
        return value
    
    value_str = str(value).strip()
    
    # Pattern 1: Starts with 1-2 digit percentile (e.g., "98128.6" or "9128.6")
    # Match: digits(percentile) followed by digits.digits(value)
    match = re.match(r'^(\d{1,2})(\d+\.\d+)$', value_str)
    if match:
        return match.group(2)
    
    # Pattern 2: Percentile with percentage in value (e.g., "9960.5%" or "860.5%")
    match = re.match(r'^(\d{1,2})(\d+\.\d+%)$', value_str)
    if match:
        return match.group(2)
    
    # Pattern 3: Percentile with no decimal (e.g., "98128" or "9128")
    match = re.match(r'^(\d{1,2})(\d+)$', value_str)
    if match and len(match.group(2)) >= 2:
        return match.group(2)
    
    # Pattern 4: Three digit percentile with value (e.g., "100128.6")
    match = re.match(r'^(\d{3})(\d+\.\d+)$', value_str)
    if match:
        return match.group(2)
    
    # Pattern 5: Percentage prefix before decimal (e.g., "98.604" where 98 is percentile)
    # Only apply if value looks like it has percentile (starts with high number)
    if '.' in value_str:
        parts = value_str.split('.')
        if len(parts[0]) >= 2 and parts[0][:2].isdigit():
            # Check if first 2 digits could be percentile (1-99)
            percentile = int(parts[0][:2])
            if 1 <= percentile <= 99:
                remaining = parts[0][2:] + '.' + parts[1]
                # Only apply if remaining looks like a reasonable value
                try:
                    float_val = float(remaining)
                    if 0 < float_val < 1000:  # Reasonable stat range
                        return remaining
                except:
                    pass
    
    # Pattern 6: Record format with percentile (e.g., "8615-2")
    match = re.match(r'^(\d{1,2})(\d+-\d+)$', value_str)
    if match:
        return match.group(2)
    
    # Pattern 7: Negative values with percentile (e.g., "98-5.2")
    match = re.match(r'^(\d{1,2})(-\d+\.?\d*)$', value_str)
    if match:
        return match.group(2)
    
    return value_str


def normalize_team_name(team_name):
    """Normalize team name to match KenPom format"""
    if team_name in TEAM_NAME_MAPPING:
        return TEAM_NAME_MAPPING[team_name]
    return team_name


class CBBAnalyticsScraper:
    def __init__(self):
        self.email = os.getenv('CBB_ANALYTICS_EMAIL')
        self.password = os.getenv('CBB_ANALYTICS_PASSWORD')
        self.base_url = "https://cbbanalytics.com/teamstats"
        
        if not self.email or not self.password:
            raise ValueError("CBB_ANALYTICS_EMAIL and CBB_ANALYTICS_PASSWORD must be set in .env file")
    
    def login(self, page):
        """Handle modal login"""
        try:
            print("Logging in...")
            page.goto(self.base_url)
            page.wait_for_load_state('networkidle')
            
            # Click the link that opens login modal
            login_link = page.locator('a:has-text("LOGIN")')
            login_link.click()
            time.sleep(2)
            
            # Fill in email
            email_input = page.locator('input[type="email"]')
            email_input.fill(self.email)
            
            # Click Next button
            next_button = page.locator('button:has-text("Next")')
            next_button.click()
            time.sleep(1)
            
            # Fill in password
            password_input = page.locator('input[type="password"]')
            password_input.fill(self.password)
            
            # Click Login/Submit button
            submit_button = page.locator('button[type="submit"]')
            submit_button.click()
            
            # Wait for login to complete
            time.sleep(3)
            page.wait_for_load_state('networkidle')
            
            print("  [OK] Login successful")
            return True
            
        except Exception as e:
            print(f"  [ERROR] Login error: {str(e)}")
            return False
    
    def set_pagination(self, page):
        """Set pagination to 500 rows"""
        try:
            print("Setting pagination to 500...")
            
            # Find and click pagination dropdown
            pagination_select = page.locator('select').first
            pagination_select.select_option('500')
            time.sleep(2)
            page.wait_for_load_state('networkidle')
            
            print("  [OK] Pagination set")
            return True
            
        except Exception as e:
            print(f"  [ERROR] Pagination error: {str(e)}")
            return False
    
    def switch_category(self, page, category_text):
        """Switch to different stat category"""
        try:
            print(f"Switching to category: {category_text}")
            
            # Try to find and click the category selector
            # The website uses text-based navigation
            elements = page.locator(f"text={category_text}").all()
            
            for elem in elements:
                try:
                    if elem.is_visible():
                        elem.click()
                        time.sleep(2)
                        page.wait_for_load_state('networkidle')
                        print(f"  [OK] Switched to {category_text}")
                        return True
                except:
                    continue
            
            print(f"  [WARN] Could not switch to {category_text}")
            return False
            
        except Exception as e:
            print(f"  [ERROR] Category switch error: {str(e)}")
            return False
    
    def scrape_category(self, page, category_key, column_mapping, category_name):
        """Scrape specific columns from a category"""
        try:
            print(f"\nScraping {category_name}...")
            
            # Save debug HTML
            html_content = page.content()
            debug_file = f'debug_{category_key}.html'
            with open(debug_file, 'w', encoding='utf-8') as f:
                f.write(html_content)
            print(f"  Saved debug HTML to {debug_file}")
            
            # Parse tables from page
            dfs = pd.read_html(html_content)
            
            if not dfs:
                print(f"  [WARN] No tables found for {category_name}")
                return pd.DataFrame()
            
            # Use first table
            df = dfs[0]
            
            print(f"  Found table with shape: {df.shape}")
            print(f"  Columns: {df.columns.tolist()}")
            
            # Initialize output dataframe with Team column
            output_df = pd.DataFrame()
            
            # Handle MultiIndex columns
            if isinstance(df.columns, pd.MultiIndex):
                print("  [OK] Detected MultiIndex columns")
                
                # Get team names from first column
                if len(df.columns[0]) >= 2:
                    team_col = df[df.columns[0]]
                    output_df['Team'] = team_col.apply(normalize_team_name)
                
                # Extract each requested column
                for orig_pattern, output_name in column_mapping.items():
                    found = False
                    
                    # Check if this is an opponent column
                    is_opponent = orig_pattern.startswith('Opponent_')
                    stat_name = orig_pattern.replace('Opponent_', '') if is_opponent else orig_pattern
                    
                    # Search through MultiIndex columns
                    for col in df.columns:
                        if len(col) >= 2:
                            group_name = str(col[0]).lower()
                            col_name = str(col[1])
                            
                            # Match logic
                            if is_opponent:
                                # For opponent stats, look in "Opponent X" groups
                                if 'opponent' in group_name and stat_name.lower() in col_name.lower():
                                    output_df[output_name] = df[col].apply(clean_percentile_value)
                                    print(f"  [OK] Found {output_name}")
                                    found = True
                                    break
                            else:
                                # For team stats, look in "Team X" groups (avoid Opponent groups)
                                if 'opponent' not in group_name and stat_name.lower() in col_name.lower():
                                    output_df[output_name] = df[col].apply(clean_percentile_value)
                                    print(f"  [OK] Found {output_name}")
                                    found = True
                                    break
                    
                    if not found:
                        print(f"  [WARN] Column not found: {output_name}")
            
            else:
                # Simple columns (not MultiIndex)
                print("  Simple column structure")
                output_df['Team'] = df.iloc[:, 0].apply(normalize_team_name)
                
                for orig_pattern, output_name in column_mapping.items():
                    # Find matching column
                    for col in df.columns:
                        if orig_pattern.lower() in str(col).lower():
                            output_df[output_name] = df[col].apply(clean_percentile_value)
                            print(f"  [OK] Found {output_name}")
                            break
            
            print(f"  Extracted {len(output_df.columns)} columns, {len(output_df)} rows")
            return output_df
            
        except Exception as e:
            print(f"  [ERROR] Scrape error: {str(e)}")
            import traceback
            traceback.print_exc()
            return pd.DataFrame()
    
    def scrape_all(self):
        """Main scraping function"""
        print("\n" + "="*60)
        print("CBB Analytics Scraper V2 - Streamlined Column Selection")
        print("="*60 + "\n")
        
        all_data = None
        
        with sync_playwright() as p:
            browser = p.chromium.launch(headless=False)
            page = browser.new_page()
            
            try:
                # Login
                if not self.login(page):
                    print("[ERROR] Login failed")
                    return
                
                # Set pagination
                if not self.set_pagination(page):
                    print("[ERROR] Pagination failed")
                    return
                
                # Scrape each category
                categories = [
                    ('team_four_factors', 'Team 4-Factors', 'Team Four Factors'),
                    ('team_four_factors_adj', 'Team 4-Factors (Adj)', 'Team Four Factors (Adj)'),
                    ('traditional_shooting', 'Traditional Shooting', 'Traditional Shooting'),
                    ('traditional_boxscore', 'Traditional Boxscore', 'Traditional Boxscore'),
                    ('advanced_offense', 'Advanced Offense', 'Advanced Offense'),
                    ('advanced_defense', 'Advanced Defense', 'Advanced Defense'),
                    ('scoring_context', 'Scoring Context', 'Scoring Context'),
                    ('win_loss_splits', 'Win/Loss Splits', 'Win/Loss Splits')
                ]
                
                for category_key, selector_text, display_name in categories:
                    # Switch category (skip first one as it's default)
                    if category_key != 'team_four_factors':
                        if not self.switch_category(page, selector_text):
                            print(f"[WARN] Skipping {display_name} - could not switch")
                            continue
                    
                    # Scrape category
                    category_data = self.scrape_category(
                        page, 
                        category_key, 
                        COLUMN_MAPPING[category_key],
                        display_name
                    )
                    
                    if category_data.empty:
                        print(f"[WARN] No data for {display_name}")
                        continue
                    
                    # Merge with all_data
                    if all_data is None:
                        all_data = category_data
                    else:
                        all_data = all_data.merge(category_data, on='Team', how='outer')
                
                # Save to CSV
                if all_data is not None and not all_data.empty:
                    output_file = 'cbb_analytics_tableau.csv'
                    all_data.to_csv(output_file, index=False)
                    print(f"\n[OK] SUCCESS")
                    print(f"Scraped {len(all_data)} teams")
                    print(f"Total columns: {len(all_data.columns)}")
                    print(f"Saved to: {output_file}")
                else:
                    print("\n[ERROR] No data collected")
                
            except Exception as e:
                print(f"\n[ERROR] Fatal error: {str(e)}")
                import traceback
                traceback.print_exc()
            
            finally:
                browser.close()


if __name__ == "__main__":
    scraper = CBBAnalyticsScraper()
    scraper.scrape_all()
