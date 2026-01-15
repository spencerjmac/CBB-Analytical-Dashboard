"""
Manual scraper specifically for Team Four Factors Adj
This script will only scrape the adjusted team four factors data
"""

import os
import time
from datetime import datetime
from pathlib import Path
import pandas as pd
from playwright.sync_api import sync_playwright

class AdjFactorsScraper:
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
            print(f"  Loading {self.base_url}...")
            page.goto(self.base_url, wait_until="domcontentloaded", timeout=90000)
            time.sleep(3)
            
            # Save page for debugging
            print(f"  Current URL: {page.url}")
            
            # Click login button
            login_buttons = ['a:has-text("Login")', 'button:has-text("Login")']
            clicked = False
            for selector in login_buttons:
                try:
                    page.click(selector, timeout=5000)
                    print(f"  ✓ Clicked login button")
                    time.sleep(2)
                    clicked = True
                    break
                except Exception as e:
                    print(f"    Failed with {selector}: {str(e)[:50]}")
                    continue
            
            if not clicked:
                print(f"  ❌ Could not find login button")
                return False
            
            # Fill email
            try:
                page.fill('input[type="email"]', self.email, timeout=10000)
                print(f"  ✓ Filled email")
            except Exception as e:
                print(f"  ❌ Could not fill email: {str(e)[:100]}")
                return False
            
            # Click Next button
            try:
                page.click('button:has-text("Next")', timeout=10000)
                print(f"  ✓ Clicked Next button")
                time.sleep(3)
            except Exception as e:
                print(f"  ❌ Could not click Next: {str(e)[:100]}")
                return False
            
            # Fill password
            try:
                page.fill('input[type="password"]', self.password, timeout=10000)
                print(f"  ✓ Filled password")
            except Exception as e:
                print(f"  ❌ Could not fill password: {str(e)[:100]}")
                return False
            
            # Click login submit
            try:
                page.click('button[type="submit"]', timeout=10000)
                print(f"  ✓ Clicked login submit")
                time.sleep(8)
            except Exception as e:
                print(f"  ❌ Could not click submit: {str(e)[:100]}")
                return False
            
            # Verify login success
            if "login" not in page.url.lower():
                print(f"  ✓ Login successful! Current URL: {page.url}")
                return True
            else:
                print(f"  ⚠️  Still on login page: {page.url}")
                return False
            
        except Exception as e:
            print(f"  ❌ Login failed: {str(e)}")
            import traceback
            traceback.print_exc()
            return False
    
    def scrape_adj_factors(self):
        """Scrape Team Four Factors Adj data"""
        print("="* 70)
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
                    print("\n❌ Login failed - cannot proceed")
                    return None
                
                # Navigate to stats page
                print(f"\nNavigating to stats page...")
                page.goto(self.stats_url, wait_until="domcontentloaded", timeout=90000)
                time.sleep(5)
                
                # Click dropdown to open it
                print(f"Opening category dropdown...")
                page.click('.cbb-select.cbb-table-types-select', force=True)
                time.sleep(2)
                
                # Try different variations of the text
                selectors_to_try = [
                    'text="Team Four Factors Adj"',
                    'text="Team Four Factors (Adj)"',
                    'text="Team 4-Factors Adj"',
                    'text="Team 4-Factors (Adj)"',
                    'div[role="option"]:has-text("Adj")',
                ]
                
                selected = False
                for selector in selectors_to_try:
                    try:
                        print(f"  Trying selector: {selector}")
                        page.click(selector, timeout=3000)
                        print(f"  ✓ Selected category!")
                        selected = True
                        time.sleep(4)
                        break
                    except Exception as e:
                        print(f"    Failed: {str(e)[:50]}")
                        continue
                
                if not selected:
                    print("  ⚠️ Could not select category, saving HTML for inspection...")
                    html_content = page.content()
                    with open('dropdown_debug.html', 'w', encoding='utf-8') as f:
                        f.write(html_content)
                    print("  Saved to dropdown_debug.html")
                    return None
                
                # Set page size to 500
                print(f"Setting page size to 500...")
                try:
                    page.select_option('select', value='500', timeout=5000)
                    print(f"  ✓ Changed page size to 500")
                    time.sleep(4)
                except:
                    print(f"  ⚠️  Using default page size")
                
                # Extract table
                print(f"Extracting table data...")
                html = page.content()
                tables = pd.read_html(html)
                
                if not tables:
                    print(f"  ⚠️  No tables found")
                    return None
                
                df = max(tables, key=len) if len(tables) > 1 else tables[0]
                
                # Flatten MultiIndex columns if present
                if isinstance(df.columns, pd.MultiIndex):
                    df.columns = ['_'.join(map(str, col)).strip('_') for col in df.columns.values]
                
                print(f"  ✓ Found table with {len(df)} rows and {len(df.columns)} columns")
                print(f"\nColumns found:")
                for i, col in enumerate(df.columns, 1):
                    print(f"  {i:2d}. {col}")
                
                # Save to CSV
                output_file = 'team_four_factors_adj.csv'
                df.to_csv(output_file, index=False)
                print(f"\n✓ Saved to {output_file}")
                
                return df
                
            except Exception as e:
                print(f"\n❌ Error: {str(e)}")
                import traceback
                traceback.print_exc()
                return None
            finally:
                input("\nPress Enter to close browser...")
                browser.close()

def main():
    scraper = AdjFactorsScraper()
    df = scraper.scrape_adj_factors()
    
    if df is not None:
        print(f"\n✓ Successfully scraped {len(df)} teams")
    else:
        print(f"\n❌ Scraping failed")

if __name__ == "__main__":
    main()
