"""
Scrape ALL teams from historical Bart Torvik seasons to calculate 
proper season-specific mean and standard deviation for Four Factor metrics.
This is needed to properly calculate Z-scores for historical champions.
"""
from playwright.sync_api import sync_playwright, TimeoutError as PlaywrightTimeout
import pandas as pd
import re
import time
from typing import List, Dict, Optional
from datetime import datetime


class HistoricalSeasonScraper:
    """Scraper for full historical season data from Bart Torvik."""
    
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
        # No 2020 tournament
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
    
    def _parse_team_row(self, cells: List, year: int, date_used: str) -> Dict:
        """Parse a row to extract team data."""
        # Extract season year (e.g., "2007-08" for 2008 season)
        season = f"{year-1}-{str(year)[2:]}"
        
        data = {
            'year': year,
            'season': season,
            'date': date_used,
        }
        
        # Columns: 0:Rank, 1:Team, 2:Conf, 3:G, 4:Rec, 5:AdjOE, 6:AdjDE, 7:Barthag,
        #          8:EFG%, 9:EFGD%, 10:TOR, 11:TORD, 12:ORB, 13:DRB, 14:FTR, 15:FTRD,
        #          16:2P%, 17:2P%D, 18:3P%, 19:3P%D, 20:3PR, 21:3PRD, 22:AdjT, 23:WAB
        
        data['rank'] = self._parse_number(cells[0].get_text(strip=True)) if len(cells) > 0 else None
        
        # Team name - clean up any game info
        team_full = cells[1].get_text(strip=True) if len(cells) > 1 else ""
        team_name = re.split(r'(?:\([HANhant]\)|vs\.)\s*\d', team_full)[0].strip()
        data['team_name'] = team_name
        
        data['conference'] = cells[2].get_text(strip=True) if len(cells) > 2 else None
        data['games'] = self._parse_number(cells[3].get_text(strip=True)) if len(cells) > 3 else None
        data['record'] = cells[4].get_text(strip=True) if len(cells) > 4 else None
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
    
    def scrape_season(self, year: int, browser=None) -> List[Dict]:
        """
        Scrape ALL teams for a given year at Selection Sunday.
        Returns list of team data dictionaries.
        """
        selection_sunday = self.SELECTION_SUNDAY_DATES.get(year)
        if not selection_sunday:
            print(f"  Skipping {year}: No Selection Sunday date available")
            return []
        
        # Bart Torvik URL with year and date parameters
        # Use trank.php which properly handles historical dates
        url = f"{self.rankings_url}?year={year}&date={selection_sunday}"
        
        should_close = False
        if browser is None:
            should_close = True
        
        try:
            if browser is None:
                playwright = sync_playwright().start()
                browser = playwright.chromium.launch(headless=True)
            
            page = browser.new_page()
            
            print(f"  Fetching ALL teams for {year} season (Selection Sunday {selection_sunday})...")
            page.goto(url, wait_until='domcontentloaded', timeout=90000)
            
            # Wait for the main table to load
            page.wait_for_selector('table', timeout=60000)
            page.wait_for_selector('tbody tr', timeout=30000)
            
            # Wait longer for all teams to load
            print(f"    Waiting for all teams to load...")
            time.sleep(5)
            
            # Check row count
            row_count = page.locator('tbody tr').count()
            print(f"    Found {row_count} rows")
            
            # Get the page content
            html_content = page.content()
            
            # Save for debugging
            with open(f'torvik_debug_{year}.html', 'w', encoding='utf-8') as f:
                f.write(html_content)
            
            # Parse the HTML
            from bs4 import BeautifulSoup
            soup = BeautifulSoup(html_content, 'html.parser')
            
            # Find the main rankings table
            table = soup.find('table')
            if not table:
                print(f"    Warning: Could not find rankings table for {year}")
                page.close()
                if should_close:
                    browser.close()
                return []
            
            # Get all rows
            rows = table.find_all('tr')
            print(f"    Parsing {len(rows)} rows...")
            
            # Parse all team data
            teams_data = []
            
            for i, row in enumerate(rows[1:], 1):  # Skip header
                try:
                    cells = row.find_all(['td', 'th'])
                    if len(cells) < 8:
                        continue
                    
                    # Get rank
                    rank_text = cells[0].get_text(strip=True)
                    if not rank_text.isdigit():
                        continue
                    
                    # Parse this team's data
                    team_data = self._parse_team_row(cells, year, selection_sunday)
                    teams_data.append(team_data)
                    
                except Exception as e:
                    print(f"    Error parsing row {i}: {e}")
                    continue
            
            page.close()
            
            if should_close:
                browser.close()
            
            print(f"    Successfully parsed {len(teams_data)} teams for {year}")
            return teams_data
            
        except PlaywrightTimeout:
            print(f"    ERROR: Timeout loading data for {year}")
            if should_close and browser:
                browser.close()
            return []
        except Exception as e:
            print(f"    ERROR scraping {year}: {e}")
            if should_close and browser:
                browser.close()
            return []
    
    def scrape_all_seasons(self, start_year: int = 2008, end_year: int = 2025) -> pd.DataFrame:
        """
        Scrape all teams for multiple seasons.
        Returns combined DataFrame of all teams.
        """
        print("="*60)
        print("Bart Torvik Historical Seasons Scraper")
        print("="*60)
        print()
        
        all_teams = []
        
        # Use shared browser for speed
        with sync_playwright() as playwright:
            browser = playwright.chromium.launch(headless=True)
            
            for year in range(start_year, end_year + 1):
                if year == 2020:
                    print(f"\nSkipping {year}: No tournament (COVID-19)")
                    continue
                
                print(f"\nScraping {year} season...")
                season_teams = self.scrape_season(year, browser=browser)
                all_teams.extend(season_teams)
                
                # Be respectful with requests
                time.sleep(2)
            
            browser.close()
        
        print("\n" + "="*60)
        print(f"Scraping complete! Total teams: {len(all_teams)}")
        print("="*60)
        
        return pd.DataFrame(all_teams)


def main():
    """Main function to scrape historical seasons and calculate statistics."""
    scraper = HistoricalSeasonScraper()
    
    # Scrape all championship seasons
    print("Scraping historical seasons to calculate proper Z-score baselines...")
    print()
    
    df = scraper.scrape_all_seasons(start_year=2008, end_year=2025)
    
    if df.empty:
        print("\nNo data scraped. Exiting.")
        return
    
    # Save raw historical data
    output_file = 'torvik_historical_all_teams.csv'
    df.to_csv(output_file, index=False)
    print(f"\nSaved raw data: {output_file}")
    
    # Calculate the four margins/edges for all teams
    print("\nCalculating Four Factor margins/edges...")
    df['efg_margin'] = df['efg_pct'] - df['efg_pct_d']
    df['ftr_margin'] = df['ftr'] - df['ftrd']
    df['turnover_edge'] = df['tord'] - df['tor']
    df['rebounding_edge'] = df['orb'] - df['drb']
    
    # Calculate season-specific statistics
    print("Calculating season-specific means and standard deviations...")
    season_stats = df.groupby('year').agg({
        'efg_margin': ['mean', 'std', 'count'],
        'ftr_margin': ['mean', 'std'],
        'turnover_edge': ['mean', 'std'],
        'rebounding_edge': ['mean', 'std']
    }).reset_index()
    
    # Flatten column names
    season_stats.columns = ['year', 
                            'efg_margin_mean', 'efg_margin_std', 'efg_margin_count',
                            'ftr_margin_mean', 'ftr_margin_std',
                            'turnover_edge_mean', 'turnover_edge_std',
                            'rebounding_edge_mean', 'rebounding_edge_std']
    
    # Save season statistics
    stats_file = 'torvik_season_statistics.csv'
    season_stats.to_csv(stats_file, index=False)
    print(f"Saved season statistics: {stats_file}")
    
    print("\n" + "="*60)
    print("SEASON STATISTICS")
    print("="*60)
    print(season_stats.to_string(index=False))
    
    # Now calculate proper Z-scores for champions
    print("\n" + "="*60)
    print("Calculating Champion Z-Scores")
    print("="*60)
    
    # Load champions data
    champions_df = pd.read_csv('torvik_champions.csv')
    
    # Calculate margins for champions
    champions_df['efg_margin'] = champions_df['efg_pct'] - champions_df['efg_pct_d']
    champions_df['ftr_margin'] = champions_df['ftr'] - champions_df['ftrd']
    champions_df['turnover_edge'] = champions_df['tord'] - champions_df['tor']
    champions_df['rebounding_edge'] = champions_df['orb'] - champions_df['drb']
    
    # Merge with season statistics
    champions_with_stats = champions_df.merge(
        season_stats,
        on='year',
        how='left'
    )
    
    # Calculate Z-scores using season-specific statistics
    champions_with_stats['efg_margin_z'] = (
        (champions_with_stats['efg_margin'] - champions_with_stats['efg_margin_mean']) / 
        champions_with_stats['efg_margin_std']
    )
    champions_with_stats['ftr_margin_z'] = (
        (champions_with_stats['ftr_margin'] - champions_with_stats['ftr_margin_mean']) / 
        champions_with_stats['ftr_margin_std']
    )
    champions_with_stats['turnover_edge_z'] = (
        (champions_with_stats['turnover_edge'] - champions_with_stats['turnover_edge_mean']) / 
        champions_with_stats['turnover_edge_std']
    )
    champions_with_stats['rebounding_edge_z'] = (
        (champions_with_stats['rebounding_edge'] - champions_with_stats['rebounding_edge_mean']) / 
        champions_with_stats['rebounding_edge_std']
    )
    
    # Calculate Four Factor Index with weights
    # Note: Weights sum to ~1.0, so NO division by 4
    champions_with_stats['four_factor_index_z'] = (
        (0.4069 * champions_with_stats['efg_margin_z']) +
        (0.4069 * champions_with_stats['turnover_edge_z']) +
        (0.1432 * champions_with_stats['rebounding_edge_z']) +
        (0.0428 * champions_with_stats['ftr_margin_z'])
    )
    
    # Calculate 0-100 score
    import numpy as np
    champions_with_stats['four_factor_score'] = np.minimum(
        100,
        np.maximum(
            0,
            50 + 15 * champions_with_stats['four_factor_index_z']
        )
    )
    
    # Save enhanced champions data
    champions_output = 'torvik_champions_with_season_stats.csv'
    champions_with_stats.to_csv(champions_output, index=False)
    print(f"\nSaved champions with Z-scores: {champions_output}")
    
    # Display results
    print("\n" + "="*60)
    print("CHAMPIONS WITH PROPER Z-SCORES")
    print("="*60)
    display_cols = ['year', 'team_name', 
                    'efg_margin', 'efg_margin_z',
                    'turnover_edge', 'turnover_edge_z',
                    'four_factor_index_z', 'four_factor_score']
    print(champions_with_stats[display_cols].to_string(index=False))
    
    print("\n" + "="*60)
    print("COMPLETE!")
    print("="*60)
    print("\nGenerated files:")
    print(f"  1. {output_file} - All teams from all seasons")
    print(f"  2. {stats_file} - Season-specific statistics")
    print(f"  3. {champions_output} - Champions with proper Z-scores")


if __name__ == "__main__":
    main()
