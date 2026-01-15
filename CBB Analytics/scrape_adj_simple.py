"""
Simplified scraper to get ONLY Team Four Factors Adj
"""

import os
import time
from datetime import datetime
from pathlib import Path
import pandas as pd
from playwright.sync_api import sync_playwright

# Category configuration
CATEGORY = {
    "name": "Team Four Factors Adj",
    "selector_options": [
        "Team Four Factors Adj",
        "Team 4-Factors Adj",
        "Team Four Factors (Adj)",
        "Team 4-Factors (Adj)",
    ]
}

class SimpleAdjScraper:
    def __init__(self):
        self.base_url = "https://cbbanalytics.com"
        self.season_id = "41097"
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
        """Login using the same method as the working scraper"""
        print("\nLogging in...")
        
        try:
            page.goto(self.base_url, wait_until="domcontentloaded", timeout=90000)
            time.sleep(3)
            
            # Click login
            page.click('a:has-text("Login")', timeout=5000)
            time.sleep(2)
            
            # Fill email
            page.fill('input[type="email"]', self.email)
            
            # Click Next
            page.click('button:has-text("Next")')
            time.sleep(2)
            
            # Fill password
            page.fill('input[type="password"]', self.password)
            
            # Submit
            page.click('button[type="submit"]')
            time.sleep(5)
            
            print("✓ Login successful")
            return True
            
        except Exception as e:
            print(f"❌ Login failed: {str(e)}")
            return False
    
    def scrape(self):
        """Scrape the adjusted factors"""
        print("=" * 70)
        print("Scraping Team Four Factors Adj")
        print("=" * 70)
        
        with sync_playwright() as p:
            browser = p.chromium.launch(headless=False)
            context = browser.new_context(
                viewport={'width': 1920, 'height': 1080},
                user_agent='Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
            )
            page = context.new_page()
            
            try:
                # Login
                if not self.login(page):
                    return None
                
                # Go to stats page
                print(f"\nNavigating to stats page...")
                page.goto(self.stats_url, wait_until="domcontentloaded", timeout=90000)
                time.sleep(5)
                
                # Change page size first (on default category)
                print(f"Setting page size to 500...")
                try:
                    page.select_option('select', value='500', timeout=5000)
                    time.sleep(4)
                    print("✓ Page size set to 500")
                except:
                    print("⚠️ Could not set page size")
                
                # Now try to switch to Adj category
                print(f"\nSwitching to Team Four Factors Adj...")
                
                # Click dropdown
                page.click('.cbb-select.cbb-table-types-select', force=True, timeout=5000)
                time.sleep(1)
                
                # Try each selector option
                selected = False
                for selector_text in CATEGORY["selector_options"]:
                    try:
                        print(f"  Trying: {selector_text}")
                        page.click(f'text="{selector_text}"', timeout=3000)
                        print(f"  ✓ Selected!")
                        selected = True
                        time.sleep(4)
                        break
                    except:
                        print(f"    Not found")
                        continue
                
                if not selected:
                    print("\n❌ Could not find the Adj category")
                    print("Available options in dropdown:")
                    options = page.query_selector_all('div[role="option"]')
                    for opt in options:
                        print(f"  - {opt.inner_text()}")
                    return None
                
                # Extract table
                print(f"\nExtracting table...")
                html = page.content()
                tables = pd.read_html(html)
                
                if not tables:
                    print("❌ No tables found")
                    return None
                
                df = max(tables, key=len) if len(tables) > 1 else tables[0]
                
                # Flatten MultiIndex
                if isinstance(df.columns, pd.MultiIndex):
                    df.columns = ['_'.join(map(str, col)).strip('_') for col in df.columns.values]
                
                print(f"✓ Got {len(df)} rows, {len(df.columns)} columns")
                
                # Save
                df.to_csv('team_four_factors_adj_raw.csv', index=False)
                print(f"✓ Saved to team_four_factors_adj_raw.csv")
                
                return df
                
            except Exception as e:
                print(f"\n❌ Error: {str(e)}")
                import traceback
                traceback.print_exc()
                return None
            finally:
                browser.close()

def main():
    scraper = SimpleAdjScraper()
    df = scraper.scrape()
    
    if df is not None:
        print(f"\n✓ Success!")
    else:
        print(f"\n❌ Failed")

if __name__ == "__main__":
    main()
