"""Test different type parameters to find pre-tournament data."""
from playwright.sync_api import sync_playwright
from bs4 import BeautifulSoup
import time

def test_type_param(year, type_param):
    """Test a type parameter."""
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        page = browser.new_page()
        
        url = f"https://barttorvik.com/trank.php?year={year}"
        if type_param:
            url += f"&type={type_param}"
        
        print(f"\nTesting type='{type_param or 'default'}':")
        print(f"  URL: {url}")
        
        try:
            page.goto(url, wait_until='domcontentloaded', timeout=30000)
            page.wait_for_selector('table', timeout=10000)
            time.sleep(2)
            
            soup = BeautifulSoup(page.content(), 'html.parser')
            table = soup.find('table')
            
            if table:
                for row in table.find_all('tr')[1:6]:  # First 5 teams
                    cells = row.find_all('td')
                    if len(cells) > 4:
                        team = cells[1].get_text(strip=True).split('\n')[0][:30]
                        games = cells[3].get_text(strip=True)
                        record = cells[4].get_text(strip=True)
                        print(f"  {team:30s} G:{games:4s} Rec:{record}")
        except Exception as e:
            print(f"  ERROR: {e}")
        finally:
            browser.close()

# Test 2008 season with different type parameters
print("=" * 70)
print("Testing Kansas 2007-08 Season with Different Type Parameters")
print("=" * 70)

test_type_param(2008, None)  # Default
test_type_param(2008, "reg")  # Regular season?
test_type_param(2008, "conf")  # Conference only?
test_type_param(2008, "nc")  # Non-conference?
test_type_param(2008, "all")  # All games
test_type_param(2008, "post")  # Post-season?
