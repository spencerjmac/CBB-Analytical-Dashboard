"""Debug script to find the login button and understand the page structure"""

import os
import time
from playwright.sync_api import sync_playwright
from dotenv import load_dotenv

load_dotenv()

with sync_playwright() as p:
    browser = p.chromium.launch(headless=False)
    page = browser.new_page()
    
    print("Navigating to CBBAnalytics...")
    page.goto("https://cbbanalytics.com/teamstats")
    page.wait_for_load_state('networkidle')
    
    # Save the initial page HTML
    with open('debug_initial_page.html', 'w', encoding='utf-8') as f:
        f.write(page.content())
    print("Saved initial page HTML to debug_initial_page.html")
    
    # Try to find all buttons
    print("\n=== Looking for buttons ===")
    buttons = page.locator('button').all()
    print(f"Found {len(buttons)} buttons")
    
    for i, button in enumerate(buttons):
        try:
            if button.is_visible():
                text = button.inner_text()
                print(f"Button {i}: '{text}'")
        except:
            pass
    
    # Try to find links with "login" or "subscribe"
    print("\n=== Looking for login/subscribe links ===")
    links = page.locator('a').all()
    for i, link in enumerate(links):
        try:
            if link.is_visible():
                text = link.inner_text().lower()
                if 'login' in text or 'subscribe' in text or 'sign' in text:
                    print(f"Link {i}: '{link.inner_text()}'")
                    print(f"  href: {link.get_attribute('href')}")
        except:
            pass
    
    print("\n=== Checking for modal/dialog elements ===")
    # Check if there's already a login modal visible
    modals = page.locator('[role="dialog"]').all()
    print(f"Found {len(modals)} dialog elements")
    
    print("\nBrowser will stay open for 60 seconds so you can inspect...")
    print("Look for the login button and note its text/selector")
    time.sleep(60)
    
    browser.close()
