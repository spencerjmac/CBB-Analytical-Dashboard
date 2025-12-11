"""
Web scraper for KenPom.com college basketball data using Playwright.
This version uses browser automation to avoid 403 blocking.
"""
from playwright.sync_api import sync_playwright, TimeoutError as PlaywrightTimeout
import time
import re
from typing import List, Dict, Optional
from datetime import datetime


class KenPomScraperPlaywright:
    """Scraper for KenPom.com data using Playwright browser automation."""
    
    def __init__(self):
        """Initialize scraper."""
        self.base_url = "https://kenpom.com"
        self.rankings_url = f"{self.base_url}/index.php"
    
    def _parse_number(self, text: str) -> Optional[float]:
        """Parse number from text, handling various formats including + signs."""
        if not text or text.strip() == '':
            return None
        
        text = text.strip()
        text = text.replace('+', '')
        cleaned = re.sub(r'[^\d\.\-]', '', text)
        if not cleaned:
            return None
        
        try:
            return float(cleaned)
        except ValueError:
            return None
    
    def _parse_value_and_rank(self, text: str) -> tuple:
        """
        Parse a cell that may contain both a value and a rank.
        KenPom format: "123.2 (6)" where 123.2 is value and 6 is rank.
        """
        if not text or text.strip() == '':
            return None, None
        
        text = text.strip()
        match = re.match(r'([+-]?\d+\.?\d*)\s*\((\d+)\)', text)
        
        if match:
            value = self._parse_number(match.group(1))
            rank = int(match.group(2))
            return value, rank
        else:
            value = self._parse_number(text)
            return value, None
    
    def scrape_rankings(self) -> List[Dict]:
        """
        Scrape current rankings from KenPom using Playwright.
        Returns list of team data dictionaries.
        """
        print(f"Fetching data from {self.rankings_url} using browser automation...")
        
        with sync_playwright() as p:
            # Launch browser in headless mode
            browser = p.chromium.launch(headless=True)
            
            # Create context with realistic settings
            context = browser.new_context(
                viewport={'width': 1920, 'height': 1080},
                user_agent='Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36'
            )
            
            page = context.new_page()
            
            try:
                # Navigate to KenPom
                print("Loading KenPom.com...")
                page.goto(self.rankings_url, wait_until='networkidle', timeout=30000)
                
                # Wait for the ratings table to load
                print("Waiting for rankings table...")
                page.wait_for_selector('table#ratings-table', timeout=10000)
                
                # Get the page content
                html_content = page.content()
                
                # Parse the HTML
                from bs4 import BeautifulSoup
                soup = BeautifulSoup(html_content, 'html.parser')
                
                # Find the ratings table
                table = soup.find('table', {'id': 'ratings-table'})
                if not table:
                    print("ERROR: Could not find ratings table")
                    return []
                
                # Get all team rows from ALL tbody sections (table has multiple tbody with headers between)
                teams_data = []
                all_tbody = table.find_all('tbody')
                rows = []
                for tbody in all_tbody:
                    rows.extend(tbody.find_all('tr'))
                
                print(f"Found {len(rows)} team rows across {len(all_tbody)} tbody sections")
                
                for row in rows:
                    try:
                        cells = row.find_all('td')
                        if len(cells) < 20:
                            continue
                        
                        # Parse team info
                        rank_cell = cells[0].get_text(strip=True)
                        team_cell = cells[1]
                        team_link = team_cell.find('a')
                        
                        if not team_link:
                            continue
                        
                        team_name = team_link.get_text(strip=True)
                        conf = cells[2].get_text(strip=True)
                        record = cells[3].get_text(strip=True)
                        
                        # Parse metrics
                        adj_em = self._parse_number(cells[4].get_text(strip=True))
                        adj_o, adj_o_rank = self._parse_value_and_rank(cells[5].get_text(strip=True))
                        adj_d, adj_d_rank = self._parse_value_and_rank(cells[7].get_text(strip=True))
                        adj_t, adj_t_rank = self._parse_value_and_rank(cells[9].get_text(strip=True))
                        luck, luck_rank = self._parse_value_and_rank(cells[11].get_text(strip=True))
                        sos_adj_em, sos_adj_em_rank = self._parse_value_and_rank(cells[13].get_text(strip=True))
                        
                        # NCSOS metrics
                        ncsos_adj_em = None
                        ncsos_adj_em_rank = None
                        if len(cells) > 19:
                            ncsos_adj_em, ncsos_adj_em_rank = self._parse_value_and_rank(cells[19].get_text(strip=True))
                        
                        team_data = {
                            'rank': int(rank_cell),
                            'team': team_name,
                            'team_name': team_name,  # For database compatibility
                            'conf': conf,
                            'conference': conf,  # For database compatibility
                            'record': record,
                            'adj_em': adj_em,
                            'adj_o': adj_o,
                            'adj_o_rank': adj_o_rank,
                            'adj_d': adj_d,
                            'adj_d_rank': adj_d_rank,
                            'adj_t': adj_t,
                            'adj_tempo': adj_t,  # For database compatibility
                            'adj_t_rank': adj_t_rank,
                            'luck': luck,
                            'luck_rank': luck_rank,
                            'sos_adj_em': sos_adj_em,
                            'sos_adj_em_rank': sos_adj_em_rank,
                            'opp_o': None,  # Not available in this format
                            'opp_d': None,  # Not available in this format
                            'ncsos_adj_em': ncsos_adj_em,
                            'ncsos_adj_em_rank': ncsos_adj_em_rank,
                            'date': datetime.now().strftime('%Y-%m-%d')
                        }
                        
                        teams_data.append(team_data)
                        
                    except Exception as e:
                        print(f"Error parsing row: {e}")
                        continue
                
                print(f"Successfully parsed {len(teams_data)} teams")
                return teams_data
                
            except PlaywrightTimeout:
                print("ERROR: Timeout loading KenPom page")
                return []
            except Exception as e:
                print(f"ERROR: {e}")
                return []
            finally:
                browser.close()


def main():
    """Test the scraper."""
    scraper = KenPomScraperPlaywright()
    teams = scraper.scrape_rankings()
    
    if teams:
        print(f"\nSuccessfully scraped {len(teams)} teams!")
        print("\nFirst 5 teams:")
        for team in teams[:5]:
            print(f"{team['rank']}. {team['team']} - AdjEM: {team['adj_em']}")
    else:
        print("\nNo data scraped!")


if __name__ == "__main__":
    main()
