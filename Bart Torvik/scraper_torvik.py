"""
Web scraper for BartTorvik.com college basketball data using Playwright.
Uses browser automation to avoid blocking.
"""
from playwright.sync_api import sync_playwright, TimeoutError as PlaywrightTimeout
import time
import re
from typing import List, Dict, Optional
from datetime import datetime


class BartTorvikScraper:
    """Scraper for BartTorvik.com data using Playwright browser automation."""
    
    def __init__(self):
        """Initialize scraper."""
        self.base_url = "https://barttorvik.com"
        self.rankings_url = f"{self.base_url}/#"
    
    def _parse_number(self, text: str) -> Optional[float]:
        """Parse number from text, handling various formats."""
        if not text or text.strip() == '':
            return None
        
        text = text.strip()
        # Remove commas and other formatting
        text = text.replace(',', '')
        cleaned = re.sub(r'[^\d\.\-]', '', text)
        if not cleaned:
            return None
        
        try:
            return float(cleaned)
        except ValueError:
            return None
    
    def scrape_rankings(self) -> List[Dict]:
        """
        Scrape current rankings from Bart Torvik using Playwright.
        Returns list of team data dictionaries.
        """
        print(f"Fetching data from {self.rankings_url} using browser automation...")
        
        try:
            with sync_playwright() as p:
                # Launch browser
                browser = p.chromium.launch(headless=True)
                page = browser.new_page()
                
                # Navigate to Bart Torvik
                print("Loading BartTorvik.com...")
                page.goto(self.rankings_url, wait_until='domcontentloaded', timeout=90000)
                
                # Wait for the main table to load
                print("Waiting for rankings table...")
                page.wait_for_selector('table', timeout=60000)
                
                # Wait for data rows to populate (DataTables loads via JS)
                print("Waiting for table data to load...")
                page.wait_for_selector('tbody tr', timeout=30000)
                
                # Wait a bit more for all 365 teams to load
                time.sleep(5)
                
                # Check how many rows are loaded
                row_count = page.locator('tbody tr').count()
                print(f"Found {row_count} rows loaded")
                
                # Get the page content
                html_content = page.content()
                
                # Save for debugging
                with open('torvik_debug.html', 'w', encoding='utf-8') as f:
                    f.write(html_content)
                
                # Parse the HTML
                from bs4 import BeautifulSoup
                soup = BeautifulSoup(html_content, 'html.parser')
                
                # Find the main rankings table
                table = soup.find('table')
                if not table:
                    print("ERROR: Could not find rankings table")
                    browser.close()
                    return []
                
                # Get all rows
                teams_data = []
                rows = table.find_all('tr')
                
                print(f"Found {len(rows)} total rows in table")
                
                # Parse header to understand column structure
                header_row = rows[0] if rows else None
                headers = []
                if header_row:
                    headers = [th.get_text(strip=True) for th in header_row.find_all(['th', 'td'])]
                    print(f"Headers: {headers[:10]}...")  # Print first 10 headers
                
                # Parse data rows
                for i, row in enumerate(rows[1:], 1):  # Skip header
                    try:
                        cells = row.find_all(['td', 'th'])
                        if len(cells) < 8:  # Need at least 8 columns for basic stats
                            continue
                        
                        # Column structure:
                        # 0: Rank, 1: Team, 2: Conf, 3: G, 4: Record, 5: AdjOE, 6: AdjDE, 7: Barthag...
                        
                        rank_text = cells[0].get_text(strip=True)
                        if not rank_text.isdigit():
                            continue
                        
                        # Team name - may include game info like "Duke(H) 16 Florida" or "Teamvs. 123 Opponent"
                        # Extract just the first part before any game notation
                        team_full = cells[1].get_text(strip=True)
                        # Remove game info patterns like "(H) 123 Opponent" or "vs. 123 Opponent"
                        team_name = re.split(r'(?:\([HANhant]\)|vs\.)\s*\d', team_full)[0].strip()
                        
                        # Skip if no team name
                        if not team_name:
                            continue
                        
                        # Get conference
                        conf = cells[2].get_text(strip=True) if len(cells) > 2 else None
                        
                        # Parse metrics based on actual column structure
                        # Columns: 0:Rank, 1:Team, 2:Conf, 3:G, 4:Rec, 5:AdjOE, 6:AdjDE, 7:Barthag,
                        #          8:EFG%, 9:EFGD%, 10:TOR, 11:TORD, 12:ORB, 13:DRB, 14:FTR, 15:FTRD,
                        #          16:2P%, 17:2P%D, 18:3P%, 19:3P%D, 20:3PR, 21:3PRD, 22:AdjT, 23:WAB
                        
                        team_data = {
                            'rank': int(rank_text),
                            'team': team_name,
                            'team_name': team_name,  # For database compatibility
                            'conference': conf,
                            'conf': conf,
                            'games': self._parse_number(cells[3].get_text(strip=True)),
                            'record': cells[4].get_text(strip=True),
                            'adj_oe': self._parse_number(cells[5].get_text(strip=True)),
                            'adj_de': self._parse_number(cells[6].get_text(strip=True)),
                            'barthag': self._parse_number(cells[7].get_text(strip=True)),
                            'efg_pct': self._parse_number(cells[8].get_text(strip=True)) if len(cells) > 8 else None,
                            'efg_pct_d': self._parse_number(cells[9].get_text(strip=True)) if len(cells) > 9 else None,
                            'tor': self._parse_number(cells[10].get_text(strip=True)) if len(cells) > 10 else None,
                            'tord': self._parse_number(cells[11].get_text(strip=True)) if len(cells) > 11 else None,
                            'orb': self._parse_number(cells[12].get_text(strip=True)) if len(cells) > 12 else None,
                            'drb': self._parse_number(cells[13].get_text(strip=True)) if len(cells) > 13 else None,
                            'ftr': self._parse_number(cells[14].get_text(strip=True)) if len(cells) > 14 else None,
                            'ftrd': self._parse_number(cells[15].get_text(strip=True)) if len(cells) > 15 else None,
                            'two_p_pct': self._parse_number(cells[16].get_text(strip=True)) if len(cells) > 16 else None,
                            'two_p_pct_d': self._parse_number(cells[17].get_text(strip=True)) if len(cells) > 17 else None,
                            'three_p_pct': self._parse_number(cells[18].get_text(strip=True)) if len(cells) > 18 else None,
                            'three_p_pct_d': self._parse_number(cells[19].get_text(strip=True)) if len(cells) > 19 else None,
                            'three_pr': self._parse_number(cells[20].get_text(strip=True)) if len(cells) > 20 else None,
                            'three_prd': self._parse_number(cells[21].get_text(strip=True)) if len(cells) > 21 else None,
                            'adj_tempo': self._parse_number(cells[22].get_text(strip=True)) if len(cells) > 22 else None,
                            'wab': self._parse_number(cells[23].get_text(strip=True)) if len(cells) > 23 else None,
                            'date': datetime.now().strftime('%Y-%m-%d')
                        }
                        
                        teams_data.append(team_data)
                        
                    except Exception as e:
                        print(f"Error parsing row {i}: {e}")
                        continue
                
                print(f"Successfully parsed {len(teams_data)} teams")
                browser.close()
                return teams_data
                
        except PlaywrightTimeout:
            print("ERROR: Timeout loading Bart Torvik page")
            return []
        except Exception as e:
            print(f"ERROR: {e}")
            import traceback
            traceback.print_exc()
            return []


def main():
    """Test the scraper."""
    scraper = BartTorvikScraper()
    teams = scraper.scrape_rankings()
    
    if teams:
        print(f"\nSuccessfully scraped {len(teams)} teams!")
        print("\nFirst 5 teams:")
        for team in teams[:5]:
            barthag = team.get('barthag', 'N/A')
            adj_oe = team.get('adj_oe', 'N/A')
            adj_de = team.get('adj_de', 'N/A')
            print(f"{team['rank']}. {team['team']} - Barthag: {barthag}, AdjOE: {adj_oe}, AdjDE: {adj_de}")
    else:
        print("\nNo data scraped!")


if __name__ == '__main__':
    main()
