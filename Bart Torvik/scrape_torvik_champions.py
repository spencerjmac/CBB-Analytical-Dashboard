"""
Scraper for Past National Champions from BartTorvik.com
Scrapes historical data for NCAA tournament champions with full stats.
"""
from playwright.sync_api import sync_playwright, TimeoutError as PlaywrightTimeout
import pandas as pd
import re
import time
from typing import List, Dict, Optional
from datetime import datetime, timedelta


class TorvikChampionsScraper:
    """Scraper for Bart Torvik historical champions data."""
    
    # NCAA Tournament Champions by year
    NCAA_CHAMPIONS = {
        2008: "Kansas",
        2009: "North Carolina",
        2010: "Duke",
        2011: "Connecticut",
        2012: "Kentucky",
        2013: "Louisville",  # Vacated but was the champion
        2014: "Connecticut",
        2015: "Duke",
        2016: "Villanova",
        2017: "North Carolina",
        2018: "Villanova",
        2019: "Virginia",
        2020: None,  # No tournament (COVID-19)
        2021: "Baylor",
        2022: "Kansas",
        2023: "Connecticut",
        2024: "Connecticut",
        2025: "Florida",
    }
    
    # Selection Sunday dates for each year (pre-tournament)
    SELECTION_SUNDAY_DATES = {
        2008: "20080316",  # March 16, 2008
        2009: "20090315",  # March 15, 2009
        2010: "20100314",  # March 14, 2010
        2011: "20110313",  # March 13, 2011
        2012: "20120311",  # March 11, 2012
        2013: "20130317",  # March 17, 2013
        2014: "20140316",  # March 16, 2014
        2015: "20150315",  # March 15, 2015
        2016: "20160313",  # March 13, 2016
        2017: "20170312",  # March 12, 2017
        2018: "20180311",  # March 11, 2018
        2019: "20190317",  # March 17, 2019
        2020: None,  # No tournament
        2021: "20210314",  # March 14, 2021
        2022: "20220313",  # March 13, 2022
        2023: "20230312",  # March 12, 2023
        2024: "20240317",  # March 17, 2024
        2025: "20250316",  # March 16, 2025
    }
    
    def __init__(self):
        """Initialize scraper."""
        self.base_url = "https://barttorvik.com"
        self.rankings_url = f"{self.base_url}/trank.php"
    
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
    
    def scrape_year(self, year: int, browser=None) -> Optional[Dict]:
        """
        Scrape Bart Torvik data for a specific year's NCAA champion.
        Returns champion data for that year using pre-tournament data.
        
        Args:
            year: The year to scrape (e.g., 2024 for 2023-24 season)
            browser: Optional browser instance to reuse
        """
        # Check if there was a champion this year
        champion_name = self.NCAA_CHAMPIONS.get(year)
        if champion_name is None:
            print(f"  Skipping {year}: No tournament held")
            return None
        
        # Get Selection Sunday date (pre-tournament data)
        selection_sunday = self.SELECTION_SUNDAY_DATES.get(year)
        if selection_sunday is None:
            print(f"  Skipping {year}: No Selection Sunday date available")
            return None
        
        # Bart Torvik URL with year and end date filter only
        # Don't set begin parameter - let it default to start of season
        url = f"{self.rankings_url}?year={year}&end={selection_sunday}"
        
        should_close = False
        if browser is None:
            should_close = True
        
        try:
            if browser is None:
                playwright = sync_playwright().start()
                browser = playwright.chromium.launch(headless=True)
            
            page = browser.new_page()
            
            print(f"  Fetching {year} pre-tournament data (Selection Sunday {selection_sunday}) for {champion_name}...")
            page.goto(url, wait_until='domcontentloaded', timeout=90000)
            
            # Wait for the main table to load
            page.wait_for_selector('table', timeout=60000)
            page.wait_for_selector('tbody tr', timeout=30000)
            
            # Wait for data to fully load
            time.sleep(3)
            
            # Get the page content
            html_content = page.content()
            
            # Parse the HTML
            from bs4 import BeautifulSoup
            soup = BeautifulSoup(html_content, 'html.parser')
            
            # Find the main rankings table
            table = soup.find('table')
            if not table:
                print(f"    Warning: Could not find rankings table for {year}")
                page.close()
                return None
            
            # Get all rows
            rows = table.find_all('tr')
            
            # Find the NCAA champion in the rankings
            champion_data = None
            
            for i, row in enumerate(rows[1:], 1):  # Skip header
                try:
                    cells = row.find_all(['td', 'th'])
                    if len(cells) < 8:
                        continue
                    
                    # Get rank
                    rank_text = cells[0].get_text(strip=True)
                    if not rank_text.isdigit():
                        continue
                    
                    # Get team name
                    team_cell = cells[1]
                    team_full = team_cell.get_text(strip=True)
                    
                    # Clean team name - remove CHAMPS marker if present
                    team_name = re.sub(r'\s*CHAMPS?\s*', '', team_full, flags=re.IGNORECASE).strip()
                    # Remove game info patterns
                    team_name = re.split(r'(?:\([HANhant]\)|vs\.)\s*\d', team_name)[0].strip()
                    
                    # Check if this is the NCAA champion
                    # Use case-insensitive comparison and handle variations
                    if self._is_champion_match(team_name, champion_name):
                        # Parse all stats
                        is_marked = 'CHAMPS' in team_full.upper()
                        champion_data = self._parse_team_row(cells, year, team_name, is_marked, selection_sunday)
                        break
                    
                except Exception as e:
                    print(f"    Error parsing row {i}: {e}")
                    continue
            
            page.close()
            
            if should_close:
                browser.close()
                playwright.stop()
            
            if champion_data is None:
                print(f"    Warning: Could not find {champion_name} in {year} rankings")
            else:
                # Verify we got pre-tournament data
                games = champion_data.get('games', 0)
                print(f"    Found {champion_name} with {games} games played")
            
            return champion_data
            
        except PlaywrightTimeout:
            print(f"    ERROR: Timeout loading data for {year}")
            if should_close and browser:
                browser.close()
            return None
        except Exception as e:
            print(f"    ERROR scraping {year}: {e}")
            if should_close and browser:
                browser.close()
            return None
    
    def _is_champion_match(self, team_name: str, champion_name: str) -> bool:
        """
        Check if a team name matches the expected champion.
        Handles common variations in team names.
        """
        team_lower = team_name.lower().strip()
        champion_lower = champion_name.lower().strip()
        
        # Direct match
        if team_lower == champion_lower:
            return True
        
        # Handle common variations
        # UConn vs Connecticut
        if champion_lower == "connecticut" and "uconn" in team_lower:
            return True
        if champion_lower == "uconn" and "connecticut" in team_lower:
            return True
        
        # Check if champion name is in team name (handles "North Carolina" vs "UNC")
        if champion_lower in team_lower or team_lower in champion_lower:
            return True
        
        return False
    
    def _parse_team_row(self, cells: List, year: int, team_name: str, is_marked_champion: bool, date_used: str) -> Dict:
        """Parse a row to extract team data."""
        data = {}
        
        # Year information
        data['year'] = year
        data['season'] = f"{year-1}-{str(year)[2:]}"  # e.g., "2023-24"
        data['date'] = date_used  # Store the date used for this data
        
        # Mark if explicitly labeled as champion
        data['is_marked_champion'] = is_marked_champion
        
        # Team info - append season to avoid duplicates
        data['rank'] = int(cells[0].get_text(strip=True))
        data['team_name'] = f"{team_name} {data['season']}"  # e.g., "Kansas 2007-08"
        data['team_name_normalized'] = f"{team_name} {data['season']}"  # Same format
        data['conference'] = cells[2].get_text(strip=True) if len(cells) > 2 else None
        data['games'] = self._parse_number(cells[3].get_text(strip=True)) if len(cells) > 3 else None
        data['record'] = cells[4].get_text(strip=True) if len(cells) > 4 else None
        
        # Column structure matches current torvik scraper
        # Columns: 0:Rank, 1:Team, 2:Conf, 3:G, 4:Rec, 5:AdjOE, 6:AdjDE, 7:Barthag,
        #          8:EFG%, 9:EFGD%, 10:TOR, 11:TORD, 12:ORB, 13:DRB, 14:FTR, 15:FTRD,
        #          16:2P%, 17:2P%D, 18:3P%, 19:3P%D, 20:3PR, 21:3PRD, 22:AdjT, 23:WAB
        
        data['adj_oe'] = self._parse_number(cells[5].get_text(strip=True)) if len(cells) > 5 else None
        data['adj_de'] = self._parse_number(cells[6].get_text(strip=True)) if len(cells) > 6 else None
        data['barthag'] = self._parse_number(cells[7].get_text(strip=True)) if len(cells) > 7 else None
        data['efg_pct'] = self._parse_number(cells[8].get_text(strip=True)) if len(cells) > 8 else None
        data['efg_pct_d'] = self._parse_number(cells[9].get_text(strip=True)) if len(cells) > 9 else None
        data['tor'] = self._parse_number(cells[10].get_text(strip=True)) if len(cells) > 10 else None
        data['tord'] = self._parse_number(cells[11].get_text(strip=True)) if len(cells) > 11 else None
        data['orb'] = self._parse_number(cells[12].get_text(strip=True)) if len(cells) > 12 else None
        data['drb'] = self._parse_number(cells[13].get_text(strip=True)) if len(cells) > 13 else None
        data['ftr'] = self._parse_number(cells[14].get_text(strip=True)) if len(cells) > 14 else None
        data['ftrd'] = self._parse_number(cells[15].get_text(strip=True)) if len(cells) > 15 else None
        data['two_p_pct'] = self._parse_number(cells[16].get_text(strip=True)) if len(cells) > 16 else None
        data['two_p_pct_d'] = self._parse_number(cells[17].get_text(strip=True)) if len(cells) > 17 else None
        data['three_p_pct'] = self._parse_number(cells[18].get_text(strip=True)) if len(cells) > 18 else None
        data['three_p_pct_d'] = self._parse_number(cells[19].get_text(strip=True)) if len(cells) > 19 else None
        data['three_pr'] = self._parse_number(cells[20].get_text(strip=True)) if len(cells) > 20 else None
        data['three_prd'] = self._parse_number(cells[21].get_text(strip=True)) if len(cells) > 21 else None
        data['adj_tempo'] = self._parse_number(cells[22].get_text(strip=True)) if len(cells) > 22 else None
        data['wab'] = self._parse_number(cells[23].get_text(strip=True)) if len(cells) > 23 else None
        
        return data
    
    def scrape_champions(self, start_year: int = 2008, end_year: int = 2024) -> List[Dict]:
        """
        Scrape NCAA champion data for a range of years.
        Bart Torvik data starts from 2008 season.
        
        Args:
            start_year: First year to scrape (default 2008)
            end_year: Last year to scrape (default 2024, last completed tournament)
        
        Returns:
            List of champion data dictionaries
        """
        champions_data = []
        
        print(f"Scraping NCAA Tournament Champions from Bart Torvik ({start_year} to {end_year})...")
        print()
        
        # Create a persistent browser for all requests
        with sync_playwright() as p:
            browser = p.chromium.launch(headless=True)
            
            for year in range(start_year, end_year + 1):
                champion_data = self.scrape_year(year, browser=browser)
                
                if champion_data:
                    champions_data.append(champion_data)
                    marked = " [MARKED]" if champion_data.get('is_marked_champion') else ""
                    print(f"  Success {year}: {champion_data['team_name']} (Rank #{champion_data['rank']}){marked}")
                elif self.NCAA_CHAMPIONS.get(year) is not None:
                    # Only show as error if there should have been a champion
                    print(f"  ERROR {year}: Could not find {self.NCAA_CHAMPIONS[year]} in data")
                
                # Be polite to the server
                time.sleep(2)
            
            browser.close()
        
        return champions_data


def main():
    """Main function to scrape champions and save to CSV."""
    print("="*60)
    print("Bart Torvik NCAA Tournament Champions Scraper")
    print("="*60)
    print()
    
    scraper = TorvikChampionsScraper()
    
    # Scrape all available years (Bart Torvik has data from 2008 onwards)
    # Only scrape through 2025 (last completed tournament as of Jan 2026)
    champions = scraper.scrape_champions(start_year=2008, end_year=2025)
    
    if not champions:
        print("\nNo champion data scraped. Exiting.")
        return
    
    # Convert to DataFrame
    df = pd.DataFrame(champions)
    
    # Add timestamp
    df['scraped_at'] = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    
    # Reorder columns to match torvik_tableau.csv structure
    column_order = [
        'year', 'season', 'date', 'rank', 'team_name', 'team_name_normalized', 
        'conference', 'games', 'record',
        'adj_oe', 'adj_de', 'barthag',
        'efg_pct', 'efg_pct_d', 'tor', 'tord', 'orb', 'drb', 
        'ftr', 'ftrd', 'two_p_pct', 'two_p_pct_d', 'three_p_pct', 
        'three_p_pct_d', 'three_pr', 'three_prd',
        'adj_tempo', 'wab',
        'is_marked_champion', 'scraped_at'
    ]
    
    # Only include columns that exist
    column_order = [col for col in column_order if col in df.columns]
    df = df[column_order]
    
    # Save to CSV
    output_file = 'torvik_champions.csv'
    df.to_csv(output_file, index=False)
    
    print()
    print("="*60)
    print(f"SUCCESS: Scraped {len(champions)} NCAA Tournament Champions")
    print(f"Saved to: {output_file}")
    print("="*60)
    print()
    print("Champions Summary:")
    print(df[['year', 'date', 'team_name', 'rank', 'adj_oe', 'adj_de', 'barthag']].to_string())
    print()
    
    # Show statistics
    marked_champs = df[df['is_marked_champion'] == True]
    if len(marked_champs) > 0:
        print(f"\n{len(marked_champs)} teams were explicitly marked as 'CHAMPS' on the website")
    
    print(f"\nAverage championship team rank: {df['rank'].mean():.1f}")
    print(f"Average championship AdjOE: {df['adj_oe'].mean():.2f}")
    print(f"Average championship AdjDE: {df['adj_de'].mean():.2f}")
    print(f"Average championship Barthag: {df['barthag'].mean():.4f}")


if __name__ == "__main__":
    main()
