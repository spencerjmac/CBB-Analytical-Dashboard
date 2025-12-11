"""
Web scraper for KenPom.com college basketball data.
"""
import requests
from bs4 import BeautifulSoup
import time
import re
from typing import List, Dict, Optional
from datetime import datetime


class KenPomScraper:
    """Scraper for KenPom.com data."""
    
    def __init__(self):
        """Initialize scraper with headers to mimic browser."""
        self.base_url = "https://kenpom.com"
        self.session = requests.Session()
        self.session.headers.update({
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
            'Accept-Language': 'en-US,en;q=0.5',
            'Accept-Encoding': 'gzip, deflate',
            'Connection': 'keep-alive',
            'Upgrade-Insecure-Requests': '1',
        })
    
    def _parse_number(self, text: str) -> Optional[float]:
        """Parse number from text, handling various formats including + signs."""
        if not text or text.strip() == '':
            return None
        
        text = text.strip()
        
        # Handle + signs (like "+29.70")
        text = text.replace('+', '')
        
        # Remove any non-numeric characters except decimal point and minus sign
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
        KenPom format is typically: "123.2 (6)" where 123.2 is the value and 6 is the rank.
        Returns (value, rank) tuple.
        """
        if not text or text.strip() == '':
            return (None, None)
        
        text = text.strip()
        
        # Try to extract rank from parentheses first (like "(6)" or " (6)")
        rank_match = re.search(r'\((\d+)\)', text)
        rank = None
        if rank_match:
            try:
                rank = int(rank_match.group(1))
            except ValueError:
                pass
        
        # Extract the main value - this should be before the parentheses
        # Remove the rank in parentheses if it exists
        text_without_rank = re.sub(r'\(\d+\)', '', text).strip()
        
        # Try to find the numeric value (can be negative, can have decimal)
        value_match = re.search(r'([-]?\d+\.?\d*)', text_without_rank)
        value = None
        if value_match:
            try:
                candidate = float(value_match.group(1))
                # Values are typically in ranges like:
                # AdjEM: -30 to +30
                # AdjO/AdjD: 80-130
                # AdjT: 60-80
                # Luck: -0.2 to +0.2
                # If it's a reasonable value, use it
                if -200 <= candidate <= 200:
                    value = candidate
            except ValueError:
                pass
        
        # If we still don't have a value but have text, try parsing the whole thing
        if value is None and text_without_rank:
            num = self._parse_number(text_without_rank)
            if num is not None:
                # If it's a reasonable range for a metric value, use it
                if -200 <= num <= 200:
                    value = num
                elif num < 400 and num == int(num) and rank is None:
                    # Small integer without parentheses might be a rank
                    rank = int(num)
        
        return (value, rank)
    
    def _parse_rank(self, text: str) -> Optional[int]:
        """Parse rank number from text."""
        if not text:
            return None
        
        # Extract first number found
        match = re.search(r'\d+', text.strip())
        if match:
            return int(match.group())
        return None
    
    def scrape_rankings(self) -> List[Dict]:
        """
        Scrape the main KenPom rankings page.
        Returns list of team ranking data.
        """
        url = f"{self.base_url}/index.php"
        
        try:
            print(f"Fetching data from {url}...")
            response = self.session.get(url, timeout=30)
            response.raise_for_status()
            
            soup = BeautifulSoup(response.content, 'html.parser')
            
            # Find the rankings table
            # KenPom uses a table with id="ratings-table" or similar
            table = soup.find('table', {'id': 'ratings-table'})
            
            if not table:
                # Try alternative table selectors
                table = soup.find('table', class_=re.compile(r'table|ratings'))
                if not table:
                    # Try finding any table with ranking data
                    tables = soup.find_all('table')
                    for t in tables:
                        if t.find('th') and ('Rank' in str(t.find('th')) or 'Team' in str(t.find('th'))):
                            table = t
                            break
            
            if not table:
                print("Warning: Could not find rankings table. KenPom may have changed their structure.")
                print("Attempting to extract data from page content...")
                # Fallback: try to extract any structured data
                return self._extract_fallback_data(soup)
            
            teams_data = []
            rows = table.find_all('tr')
            # Skip first row (empty header) and second row (column headers)
            # Data starts at row 2 (index 2)
            # IMPORTANT: This ensures we skip the header rows and start with actual data
            if len(rows) > 2:
                rows = rows[2:]
            else:
                rows = []
                print("Warning: Not enough rows found in table")
            
            for row in rows:
                cells = row.find_all(['td', 'th'])
                if len(cells) < 5:  # Need at least some data
                    continue
                
                try:
                    # Parse team data - structure may vary
                    team_data = self._parse_ranking_row(cells)
                    if team_data:
                        teams_data.append(team_data)
                except Exception as e:
                    print(f"Error parsing row: {e}")
                    continue
            
            print(f"Successfully scraped {len(teams_data)} teams")
            return teams_data
            
        except requests.RequestException as e:
            print(f"Error fetching data: {e}")
            return []
        except Exception as e:
            print(f"Error parsing data: {e}")
            return []
    
    def _parse_ranking_row(self, cells: List) -> Optional[Dict]:
        """
        Parse a single row of ranking data.
        KenPom table structure (values and ranks are in SEPARATE cells):
        [0]: Rank
        [1]: Team
        [2]: Conference
        [3]: W-L (skip)
        [4]: AdjEM value
        [5]: AdjO value
        [6]: AdjO rank (skip - this is why AdjD was wrong!)
        [7]: AdjD value (this is what we need!)
        [8]: AdjD rank (skip)
        [9]: AdjT value
        [10]: AdjT rank (skip)
        [11]: Luck value
        [12]: Luck rank (skip)
        [13]: SOS AdjEM value
        [14]: SOS AdjEM rank (skip)
        [15]: OppO value
        [16]: OppO rank (skip)
        [17]: OppD value
        [18]: OppD rank (skip)
        [19]: NCSOS AdjEM value
        [20]: NCSOS AdjEM rank (skip)
        """
        if len(cells) < 3:
            return None
        
        data = {}
        
        # Extract rank (first cell)
        rank_text = cells[0].get_text(strip=True)
        data['rank'] = self._parse_rank(rank_text)
        
        # Team name (second cell, may have link)
        team_cell = cells[1]
        team_link = team_cell.find('a')
        if team_link:
            team_name = team_link.get_text(strip=True)
        else:
            team_name = team_cell.get_text(strip=True)
        data['team_name'] = team_name
        
        # Conference (third cell)
        if len(cells) > 2:
            data['conference'] = cells[2].get_text(strip=True)
        
        # Parse values - KenPom structure has value/rank pairs
        # The pattern is: value, rank, value, rank, etc.
        # But AdjD seems to be missing from the main table structure
        # Based on inspection:
        # [4]: AdjEM value, [5]: AdjO value, [6]: AdjO rank, [7]: AdjT value, [8]: AdjT rank
        # [9]: Luck value, [10]: Luck rank, [11]: SOS AdjEM value, [12]: SOS AdjEM rank
        # [13]: NCSOS AdjEM value, [14]: NCSOS AdjEM rank, [15]: OppO value, [16]: OppO rank
        # [17]: OppD value, [18]: OppD rank, [19]: (duplicate NCSOS?)
        
        # AdjEM value (index 4)
        if len(cells) > 4:
            adj_em_text = cells[4].get_text(strip=True)
            data['adj_em'] = self._parse_number(adj_em_text)
        
        # AdjO value (index 5)
        if len(cells) > 5:
            adj_o_text = cells[5].get_text(strip=True)
            data['adj_o'] = self._parse_number(adj_o_text)
        
        # AdjD value - KenPom table shows DRtg header but only displays the rank, not the value
        # Calculate AdjD from AdjO and AdjEM: AdjEM = AdjO - AdjD, so AdjD = AdjO - AdjEM
        # We'll calculate this after we have both AdjO and AdjEM
        # (Set to None for now, will calculate after parsing other values)
        data['adj_d'] = None
        
        # AdjT value (index 9) - NOT index 7! 
        # Index 6: AdjO rank (skip)
        # Index 7: appears to be something else (maybe AdjD rank or another metric)
        # Index 8: rank (skip)
        # Index 9: AdjT value = 71.1 for Duke
        if len(cells) > 9:
            adj_t_text = cells[9].get_text(strip=True)
            data['adj_tempo'] = self._parse_number(adj_t_text)
        
        # Luck value (index 11) - note: index 10 is AdjT rank (skip)
        if len(cells) > 11:
            luck_text = cells[11].get_text(strip=True)
            data['luck'] = self._parse_number(luck_text)
        
        # SOS AdjEM value (index 13) - note: index 12 is Luck rank (skip)
        if len(cells) > 13:
            sos_text = cells[13].get_text(strip=True)
            data['sos_adj_em'] = self._parse_number(sos_text)
        
        # NCSOS AdjEM value (index 19) - note: index 14 is SOS AdjEM rank, 15-18 are OppO/OppD values and ranks
        if len(cells) > 19:
            ncsos_text = cells[19].get_text(strip=True)
            data['ncsos_adj_em'] = self._parse_number(ncsos_text)
        
        # OppO value (index 15) - note: index 14 is NCSOS AdjEM rank
        if len(cells) > 15:
            opp_o_text = cells[15].get_text(strip=True)
            data['opp_o'] = self._parse_number(opp_o_text)
        
        # OppD value (index 17) - note: index 16 is OppO rank
        if len(cells) > 17:
            opp_d_text = cells[17].get_text(strip=True)
            data['opp_d'] = self._parse_number(opp_d_text)
        
        # Calculate AdjD from AdjO and AdjEM if we have both
        # AdjEM = AdjO - AdjD, so AdjD = AdjO - AdjEM
        if data.get('adj_o') is not None and data.get('adj_em') is not None:
            data['adj_d'] = data['adj_o'] - data['adj_em']
        
        return data if data.get('team_name') else None
    
    def _extract_fallback_data(self, soup: BeautifulSoup) -> List[Dict]:
        """Fallback method to extract data if table structure is not found."""
        # This is a placeholder for more sophisticated extraction
        # In practice, you might need to inspect the actual HTML structure
        print("Fallback extraction not fully implemented. Please check KenPom.com structure.")
        return []
    
    def scrape_team_schedule(self, team_name: str) -> List[Dict]:
        """
        Scrape schedule for a specific team.
        Note: This may require authentication or subscription on KenPom.
        """
        # This would require finding the team's schedule page
        # KenPom may require login for detailed schedules
        print(f"Team schedule scraping for {team_name} not yet implemented")
        return []

