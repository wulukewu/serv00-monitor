import os
import time
import sys
import re
import requests
from playwright.sync_api import sync_playwright

# --- Configuration ---
WEBHOOK_URL = os.getenv('DISCORD_WEBHOOK')
# Check interval for Docker mode (default: 300 seconds)
CHECK_INTERVAL = int(os.getenv('CHECK_INTERVAL', 300))
# One-shot mode for GitHub Actions (true/false)
ONCE_MODE = os.getenv('ONCE_MODE', 'false').lower() == 'true'

# Target URL (Homepage only)
TARGET_URL = "https://www.serv00.com/"

# Fallback limit if scraping fails
DEFAULT_LIMIT = 170000

def clean_number(text):
    """Extracts integers from a string (e.g., '170,000' -> 170000)."""
    if not text:
        return None
    digits = re.sub(r'\D', '', str(text))
    if not digits:
        return None
    return int(digits)

def send_discord_notification(current, limit):
    """Sends a notification to Discord via Webhook."""
    embed_color = 5763719 # Green

    data = {
        "content": "@everyone 🚨 **Serv00 Availability Detected!**",
        "embeds": [{
            "title": "Slots Available!",
            "description": (
                f"The homepage counter indicates available slots.\n\n"
                f"**Current Accounts:** {current}\n"
                f"**Limit:** {limit}\n\n"
                f"[Click here to Register]({TARGET_URL})"
            ),
            "color": embed_color,
            "timestamp": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime())
        }]
    }
    
    try:
        requests.post(WEBHOOK_URL, json=data)
        print("✅ Discord notification sent.")
    except Exception as e:
        print(f"❌ Failed to send Discord notification: {e}")

def check_serv00():
    timestamp = time.strftime('%Y-%m-%d %H:%M:%S')
    print(f"[{timestamp}] Starting check via Playwright...", end=" ")

    try:
        with sync_playwright() as p:
            # Launch Chromium in headless mode
            browser = p.chromium.launch(headless=True)
            
            # Create a context with a realistic User-Agent
            context = browser.new_context(
                user_agent="Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
            )
            page = context.new_page()

            # Navigate to the homepage
            page.goto(TARGET_URL, timeout=60000)
            
            # Wait for the counter element to be present in the DOM
            # Selector based on the HTML provided: strong class="is--counter--accounts"
            try:
                page.wait_for_selector(".is--counter--accounts", state="attached", timeout=15000)
            except Exception:
                print("Timeout waiting for selector.")
                browser.close()
                return

            # Retrieve the text content. 
            # Note: The data might be in 'data-count' attribute OR text content depending on JS state.
            account_elem = page.locator(".is--counter--accounts").first
            
            # Try getting text content (rendered number)
            raw_current = account_elem.text_content()
            
            # If text is empty, try getting the 'data-count' attribute
            if not raw_current:
                raw_current = account_elem.get_attribute("data-count")

            # Try to find the limit element
            # Usually: <span data-limit> or similar. If not found, use default.
            limit_elem = page.locator("span[data-limit]").first
            raw_limit = None
            if limit_elem.count() > 0:
                raw_limit = limit_elem.text_content() or limit_elem.get_attribute("data-limit")
            
            browser.close()

            # Parse numbers
            curr_num = clean_number(raw_current)
            limit_num = clean_number(raw_limit)

            # Use fallback limit if not found
            if not limit_num:
                limit_num = DEFAULT_LIMIT

            # Logic Check
            if curr_num is not None:
                print(f"Stats: {curr_num} / {limit_num}", end=" ")
                
                if curr_num < limit_num:
                    print("--> 🎉 OPEN! Sending notification...")
                    send_discord_notification(curr_num, limit_num)
                else:
                    print("--> Full.")
            else:
                print(f"Failed to parse numbers. Raw: '{raw_current}'")

    except Exception as e:
        print(f"\n❌ Error during execution: {e}")

if __name__ == "__main__":
    if not WEBHOOK_URL:
        print("❌ Error: DISCORD_WEBHOOK environment variable is not set.")
        sys.exit(1)

    if ONCE_MODE:
        print("🚀 Mode: ONE-SHOT (GitHub Actions)")
        check_serv00()
        print("Done.")
    else:
        print(f"🚀 Mode: DAEMON (Docker Loop), Interval: {CHECK_INTERVAL}s")
        while True:
            check_serv00()
            time.sleep(CHECK_INTERVAL)