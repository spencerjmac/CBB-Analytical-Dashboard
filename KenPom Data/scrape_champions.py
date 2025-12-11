"""
Scraper for Past National Champions from KenPom.com
Scrapes historical data for NCAA tournament champions and exports to CSV.
"""
import requests
from bs4 import BeautifulSoup
import pandas as pd
import re
from datetime import datetime
from typing import List, Dict, Optional
import time


class ChampionsScraper:
    """Scraper for KenPom historical champions data."""
    
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
            'Referer': 'https://kenpom.com/',
        })
    
    def _parse_number(self, text: str) -> Optional[float]:
        """Parse number from text, handling various formats."""
        if not text or text.strip() == '':
            return None
        
        text = text.strip().replace('+', '')
        cleaned = re.sub(r'[^\d\.\-]', '', text)
        
        if not cleaned:
            return None
        
        try:
            return float(cleaned)
        except ValueError:
            return None
    
    def scrape_year(self, year: int) -> Dict:
        """
        Scrape KenPom data for a specific year.
        Returns champion data for that year.
        """
        url = f"{self.base_url}/index.php?y={year}"
        
        try:
            print(f"Fetching data for {year} season from {url}...")
            response = self.session.get(url, timeout=30)
            response.raise_for_status()
            
            soup = BeautifulSoup(response.content, 'html.parser')
            
            # Find the ratings table
            table = soup.find('table', {'id': 'ratings-table'})
            
            if not table:
                print(f"Warning: Could not find ratings table for {year}")
                return None
            
            # Get the champion (typically rank #1 or marked specially)
            # We'll look for the first valid team in the table
            rows = table.find_all('tr')
            
            for row in rows[2:]:  # Skip header rows
                cells = row.find_all(['td', 'th'])
                if len(cells) < 5:
                    continue
                
                team_data = self._parse_champion_row(cells, year)
                if team_data:
                    # Get the first team (which should be the champion or final #1)
                    return team_data
            
            return None
            
        except requests.RequestException as e:
            print(f"Error fetching data for {year}: {e}")
            return None
        except Exception as e:
            print(f"Error parsing data for {year}: {e}")
            return None
    
    def _parse_champion_row(self, cells: List, year: int) -> Optional[Dict]:
        """Parse a row to extract champion data."""
        if len(cells) < 5:
            return None
        
        data = {}
        data['year'] = year
        data['season'] = f"{year-1}-{str(year)[2:]}"  # e.g., "2023-24"
        
        # Rank
        rank_text = cells[0].get_text(strip=True)
        data['final_rank'] = self._parse_number(rank_text)
        
        # Team name
        team_cell = cells[1]
        team_link = team_cell.find('a')
        if team_link:
            data['team_name'] = team_link.get_text(strip=True)
        else:
            data['team_name'] = team_cell.get_text(strip=True)
        
        # Conference
        if len(cells) > 2:
            data['conference'] = cells[2].get_text(strip=True)
        
        # Parse metrics (similar to main scraper)
        # AdjEM (index 4)
        if len(cells) > 4:
            data['adj_em'] = self._parse_number(cells[4].get_text(strip=True))
        
        # AdjO (index 5)
        if len(cells) > 5:
            data['adj_o'] = self._parse_number(cells[5].get_text(strip=True))
        
        # AdjD - calculated from AdjO - AdjEM
        if data.get('adj_o') and data.get('adj_em'):
            data['adj_d'] = data['adj_o'] - data['adj_em']
        
        # AdjT (index 9)
        if len(cells) > 9:
            data['adj_tempo'] = self._parse_number(cells[9].get_text(strip=True))
        
        # Luck (index 11)
        if len(cells) > 11:
            data['luck'] = self._parse_number(cells[11].get_text(strip=True))
        
        # SOS AdjEM (index 13)
        if len(cells) > 13:
            data['sos_adj_em'] = self._parse_number(cells[13].get_text(strip=True))
        
        return data if data.get('team_name') else None
    
    def scrape_champions(self, start_year: int = 2002, end_year: int = 2025) -> List[Dict]:
        """
        Scrape champion data for a range of years.
        KenPom data starts from 2002 season.
        
        Args:
            start_year: First year to scrape (default 2002)
            end_year: Last year to scrape (default 2025)
        
        Returns:
            List of champion data dictionaries
        """
        champions_data = []
        
        print(f"Scraping National Champions from {start_year} to {end_year}...")
        
        for year in range(start_year, end_year + 1):
            champion_data = self.scrape_year(year)
            
            if champion_data:
                champions_data.append(champion_data)
                print(f"  ✓ {year}: {champion_data['team_name']}")
            else:
                print(f"  ✗ {year}: No data found")
            
            # Be polite to the server
            time.sleep(2)
        
        return champions_data


def main():
    """Main function to scrape champions and save to CSV."""
    print("="*60)
    print("KenPom National Champions Scraper")
    print("="*60)
    print()
    
    scraper = ChampionsScraper()
    
    # Scrape all available years (KenPom has data from 2002 onwards)
    champions = scraper.scrape_champions(start_year=2002, end_year=2025)
    
    if not champions:
        print("\nNo champion data scraped. Exiting.")
        return
    
    # Convert to DataFrame
    df = pd.DataFrame(champions)
    
    # Add timestamp
    df['scraped_at'] = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    
    # Reorder columns
    column_order = [
        'year', 'season', 'team_name', 'conference', 'final_rank',
        'adj_em', 'adj_o', 'adj_d', 'adj_tempo', 'luck', 'sos_adj_em',
        'scraped_at'
    ]
    
    # Only include columns that exist
    column_order = [col for col in column_order if col in df.columns]
    df = df[column_order]
    
    # Save to CSV
    output_file = 'kenpom_champions.csv'
    df.to_csv(output_file, index=False)
    
    print()
    print("="*60)
    print(f"✓ Scraped {len(champions)} champions")
    print(f"✓ Saved to: {output_file}")
    print("="*60)
    print()
    print("Sample data:")
    print(df.head(10).to_string())


if __name__ == "__main__":
    main()
