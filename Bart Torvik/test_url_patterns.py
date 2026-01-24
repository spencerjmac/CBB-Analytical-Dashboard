"""
Test different URL patterns for Bart Torvik historical data
"""
from playwright.sync_api import sync_playwright
import time

test_urls = [
    # Different URL patterns to try
    ("Standard with end date", "https://barttorvik.com/#?year=2008&end=20080316"),
    ("With begin and end", "https://barttorvik.com/#?year=2008&begin=20080316&end=20080316"),
    ("Trank with parameters", "https://barttorvik.com/trank.php?year=2008&date=20080316"),
    ("Trank with end only", "https://barttorvik.com/trank.php?year=2008&end=20080316"),
]

with sync_playwright() as p:
    browser = p.chromium.launch(headless=False)  # Show browser to see what happens
    
    for name, url in test_urls:
        print(f"\nTrying: {name}")
        print(f"URL: {url}")
        
        page = browser.new_page()
        page.goto(url, wait_until='domcontentloaded', timeout=90000)
        
        # Wait for table
        page.wait_for_selector('table', timeout=10000)
        time.sleep(3)
        
        # Get first team name
        first_row = page.locator('tbody tr').first
        team_cell = first_row.locator('td').nth(1)
        team_name = team_cell.inner_text()
        
        print(f"  First team: {team_name}")
        
        # Check the actual URL in browser
        current_url = page.url
        print(f"  Actual URL: {current_url}")
        
        page.close()
        time.sleep(2)
    
    browser.close()

print("\nTest complete!")
