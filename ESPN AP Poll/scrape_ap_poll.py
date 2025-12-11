"""
Scraper for ESPN AP Poll Week 6 - Men's College Basketball
Extracts rankings and normalizes team names to match KenPom format.
"""
from playwright.sync_api import sync_playwright, TimeoutError as PlaywrightTimeout
import pandas as pd
from datetime import datetime


# Team name mapping from ESPN to KenPom format
ESPN_TO_KENPOM = {
    'UConn': 'Connecticut',
    'Michigan State': 'Michigan St.',
    'North Carolina': 'North Carolina',
    'Texas Tech': 'Texas Tech',
    'St. John\'s': 'St. John\'s',
    'Saint Mary\'s': 'Saint Mary\'s',
    # Most teams match already
}


def normalize_team_name(espn_name: str) -> str:
    """Normalize ESPN team name to KenPom format."""
    if espn_name in ESPN_TO_KENPOM:
        return ESPN_TO_KENPOM[espn_name]
    return espn_name


def scrape_ap_poll():
    """Scrape AP Poll Week 6 from ESPN."""
    url = "https://www.espn.com/mens-college-basketball/rankings"
    
    print(f"Scraping AP Poll from ESPN...")
    print(f"URL: {url}\n")
    
    try:
        with sync_playwright() as p:
            browser = p.chromium.launch(headless=True)
            page = browser.new_page()
            
            # Navigate to ESPN rankings
            print("Loading ESPN rankings page...")
            page.goto(url, wait_until='domcontentloaded', timeout=90000)
            
            # Wait for the rankings table to load
            print("Waiting for AP Poll table...")
            import time
            time.sleep(3)
            page.wait_for_selector('table', timeout=60000)
            
            # Get page content
            html_content = page.content()
            
            # Parse with BeautifulSoup
            from bs4 import BeautifulSoup
            soup = BeautifulSoup(html_content, 'html.parser')
            
            # Find all tables (AP Poll should be first)
            tables = soup.find_all('table')
            
            if not tables:
                print("ERROR: No tables found on page")
                browser.close()
                return None
            
            print(f"Found {len(tables)} tables on page")
            
            # Parse AP Poll table (first table)
            ap_poll_data = []
            ap_table = tables[0]
            rows = ap_table.find_all('tr')
            
            print(f"Parsing AP Poll - found {len(rows)} rows\n")
            
            for row in rows:
                cells = row.find_all(['td', 'th'])
                
                if len(cells) < 4:
                    continue
                
                # Extract rank (first cell)
                rank_text = cells[0].get_text(strip=True)
                if not rank_text.isdigit():
                    continue
                
                rank = int(rank_text)
                
                # Extract team name - ESPN has multiple links, need the last one with actual team name
                team_links = cells[1].find_all('a')
                if len(team_links) >= 2:
                    # The last link usually has the full team name
                    team_name = team_links[-1].get_text(strip=True)
                elif team_links:
                    team_name = team_links[0].get_text(strip=True)
                else:
                    # Fallback: parse from text
                    team_cell = cells[1].get_text(strip=True)
                    # Team name appears like "ARIZArizona(33)"
                    # Find the parentheses and work backwards
                    if '(' in team_cell:
                        before_paren = team_cell.split('(')[0].strip()
                        # Remove abbreviation at start (usually 3-4 chars)
                        import re
                        # Match pattern like "ARIZArizona" - remove first occurrence
                        match = re.search(r'[A-Z]{3,4}([A-Z][a-z]+.*)', before_paren)
                        if match:
                            team_name = match.group(1)
                        else:
                            team_name = before_paren
                    else:
                        team_name = team_cell
                
                # Extract record (third cell)
                record = cells[2].get_text(strip=True)
                
                # Extract points (fourth cell)
                points = cells[3].get_text(strip=True)
                
                # Extract previous rank (fifth cell)
                prev_rank = cells[4].get_text(strip=True) if len(cells) > 4 else 'NR'
                
                ap_poll_data.append({
                    'rank': rank,
                    'team_espn': team_name,
                    'team_kenpom': normalize_team_name(team_name),
                    'record': record,
                    'points': points,
                    'previous_rank': prev_rank,
                    'poll': 'AP',
                    'week': 6,
                    'date': '2025-12-08'
                })
            
            browser.close()
            
            print(f"Successfully scraped {len(ap_poll_data)} teams from AP Poll")
            return ap_poll_data
            
    except PlaywrightTimeout:
        print("ERROR: Timeout loading ESPN page")
        return None
    except Exception as e:
        print(f"ERROR: {e}")
        import traceback
        traceback.print_exc()
        return None


def export_to_csv(data, filename='ap_poll_week6.csv'):
    """Export AP Poll data to CSV."""
    if not data:
        print("No data to export")
        return False
    
    df = pd.DataFrame(data)
    
    # Reorder columns
    columns = ['rank', 'team_espn', 'team_kenpom', 'record', 'points', 'previous_rank', 'poll', 'week', 'date']
    df = df[columns]
    
    # Export
    df.to_csv(filename, index=False)
    print(f"\n[SUCCESS] Exported {len(df)} teams to {filename}")
    
    # Show preview
    print("\nTop 10 AP Poll Week 6:")
    print("-" * 70)
    for _, row in df.head(10).iterrows():
        prev = row['previous_rank'] if row['previous_rank'] != 'NR' else 'NR'
        print(f"  {row['rank']:2d}. {row['team_kenpom']:20s} {row['record']:6s} ({row['points']} pts) [Prev: {prev}]")
    
    return True


def main():
    """Main function."""
    print("=" * 70)
    print("ESPN AP Poll Week 6 Scraper")
    print("=" * 70)
    print()
    
    # Scrape data
    data = scrape_ap_poll()
    
    if data:
        # Export to CSV
        export_to_csv(data)
        print("\n" + "=" * 70)
        print("Scraping completed successfully!")
        print("=" * 70)
    else:
        print("\nScraping failed!")


if __name__ == '__main__':
    main()
