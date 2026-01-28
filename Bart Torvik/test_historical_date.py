"""Test if historical dates work with different URL patterns."""
from playwright.sync_api import sync_playwright
from bs4 import BeautifulSoup
import time

def test_url(url, desc):
    """Test a URL pattern."""
    print(f"\n{desc}")
    print(f"URL: {url}")
    
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        page = browser.new_page()
        
        try:
            page.goto(url, wait_until='domcontentloaded', timeout=30000)
            page.wait_for_selector('table', timeout=10000)
            time.sleep(2)
            
            soup = BeautifulSoup(page.content(), 'html.parser')
            table = soup.find('table')
            
            if table:
                for row in table.find_all('tr')[1:4]:
                    cells = row.find_all('td')
                    if len(cells) > 4:
                        team = cells[1].get_text(strip=True).split('\n')[0][:25]
                        games = cells[3].get_text(strip=True)
                        record = cells[4].get_text(strip=True)
                        print(f"  {team:25s} Games: {games:4s} Record: {record}")
        except Exception as e:
            print(f"  ERROR: {e}")
        finally:
            browser.close()

print("="*70)
print("Testing Different Approaches for 2008 Pre-Tournament Data")
print("="*70)

# Test various URL patterns
test_url("https://barttorvik.com/trank.php?year=2008", 
         "1. Default (all games)")

test_url("https://barttorvik.com/trank.php?year=2008&date=20080310", 
         "2. With date=March 10, 2008")

test_url("https://barttorvik.com/trank.php?year=2008&type=reg", 
         "3. With type=reg")

test_url("https://barttorvik.com/trank.php?year=2008&date=20080310&type=reg", 
         "4. With date AND type=reg")

# Try excluding post-season
test_url("https://barttorvik.com/trank.php?year=2008&conlimit=Reg", 
         "5. With conlimit=Reg")

test_url("https://barttorvik.com/trank.php?year=2008&conlimit=All", 
         "6. With conlimit=All")

# Try different date formats
test_url("https://barttorvik.com/trank.php?year=2008&date=2008-03-10", 
         "7. With date=2008-03-10 (different format)")

# Try using the history/archive endpoint if it exists
test_url("https://barttorvik.com/trank.php?year=2008&archive=1&date=20080310", 
         "8. With archive parameter")
