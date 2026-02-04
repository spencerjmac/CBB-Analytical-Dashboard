"""
Test which URL pattern gives us actual pre-tournament data
"""
from playwright.sync_api import sync_playwright
import time

test_urls = [
    ("trank with end date", "https://barttorvik.com/trank.php?year=2021&end=20210314"),
    ("trank with type=reg", "https://barttorvik.com/trank.php?year=2021&type=reg"),
    ("homepage with end date", "https://barttorvik.com/#?year=2021&end=20210314"),
]

print("Testing URLs for 2021 Baylor (should have 24 games pre-tournament)")
print("="*70)

with sync_playwright() as p:
    browser = p.chromium.launch(headless=False)
    
    for name, url in test_urls:
        print(f"\n{name}")
        print(f"URL: {url}")
        
        page = browser.new_page()
        page.goto(url, wait_until='domcontentloaded', timeout=90000)
        
        time.sleep(5)  # Wait for data to load
        
        # Find Baylor in the table
        rows = page.locator('tbody tr')
        for i in range(min(10, rows.count())):
            row = rows.nth(i)
            text = row.inner_text()
            if 'Baylor' in text:
                cells = row.locator('td')
                team_name = cells.nth(1).inner_text()
                games = cells.nth(3).inner_text()
                print(f"  Baylor: {games} games - {team_name}")
                break
        
        page.close()
    
    browser.close()
