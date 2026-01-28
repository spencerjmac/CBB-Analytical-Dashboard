"""Test if Torvik's date parameter actually filters games."""
from playwright.sync_api import sync_playwright
from bs4 import BeautifulSoup
import time

def get_kansas_games(year, date):
    """Get Kansas games count for a specific date."""
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        page = browser.new_page()
        
        url = f"https://barttorvik.com/trank.php?year={year}&date={date}"
        print(f"Fetching: {url}")
        page.goto(url, wait_until='domcontentloaded')
        page.wait_for_selector('table')
        time.sleep(3)
        
        soup = BeautifulSoup(page.content(), 'html.parser')
        table = soup.find('table')
        
        if table:
            for row in table.find_all('tr'):
                if 'Kansas' in str(row):
                    cells = row.find_all('td')
                    if len(cells) > 3:
                        team = cells[1].get_text(strip=True)
                        games = cells[3].get_text(strip=True)
                        record = cells[4].get_text(strip=True)
                        print(f"  Team: {team}")
                        print(f"  Games: {games}")
                        print(f"  Record: {record}")
                        browser.close()
                        return games
        
        browser.close()
        return None

# Test current 2025 season (should have ~23-24 games as of Jan 28)
print("=" * 60)
print("Testing 2025 season with TODAY's date (Jan 28, 2026):")
print("=" * 60)
get_kansas_games(2025, "20260128")

print("\n" + "=" * 60)
print("Testing 2008 season with March 1, 2008:")
print("=" * 60)
get_kansas_games(2008, "20080301")

print("\n" + "=" * 60)
print("Testing 2008 season with April 1, 2008 (after tournament):")
print("=" * 60)
get_kansas_games(2008, "20080401")
