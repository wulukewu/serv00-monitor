import requests
import time
import os
import datetime
import sys

# --- Configuration ---
WEBHOOK_URL = os.getenv('DISCORD_WEBHOOK')
CHECK_INTERVAL = int(os.getenv('CHECK_INTERVAL', 300))
TARGET_URL = "https://www.serv00.com/register-account/"

HEADERS = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
    "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8"
}

def send_discord_notification(reason):
    data = {
        "content": "@everyone 🚨 **Serv00 Availability Detected!**",
        "embeds": [{
            "title": "Registration Page Open!",
            "description": f"The 'Limit Reached' message has disappeared!\n\n**Reason:** {reason}\n\n[Click here to Register]({TARGET_URL})",
            "color": 5763719
        }]
    }
    try:
        requests.post(WEBHOOK_URL, json=data)
        print("✅ Discord notification sent successfully.")
    except Exception as e:
        print(f"❌ Failed to send Discord notification: {e}")

def check_serv00():
    timestamp = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    print(f"[{timestamp}] Checking...", end=" ")
    
    try:
        response = requests.get(TARGET_URL, headers=HEADERS, timeout=20)
        
        if response.status_code != 200:
            print(f"Error: Status {response.status_code}")
            return

        html_content = response.text
        
        # --- Logic: Based on the specific HTML structure you provided ---
        # The key phrase indicating the server is full:
        limit_reached_msg = "The server user limit has been reached"
        
        # Check if we are actually on the registration page (to avoid 404s or redirects triggering false positives)
        is_registration_page = "Register account" in html_content

        if is_registration_page:
            if limit_reached_msg in html_content:
                print("--> 🔒 Closed (Limit reached message found).")
            else:
                # If we are on the page, but the limit message is GONE, it's open!
                print("--> 🎉 OPEN! Limit message is gone. Sending notification...")
                send_discord_notification("Limit message disappeared")
        else:
            print("--> ⚠️ Warning: Page content unreadable or not registration page.")
            # Optional: Print snippet if confused
            # print(html_content[:200])

    except Exception as e:
        print(f"Unexpected Error: {e}")

if __name__ == "__main__":
    if not WEBHOOK_URL:
        print("❌ Error: DISCORD_WEBHOOK environment variable is not set.")
        sys.exit(1)
        
    print("🚀 Serv00 Monitor started (v6 - Exact HTML Match)...")
    print(f"ℹ️  Target: {TARGET_URL}")
    print(f"ℹ️  Checking interval: {CHECK_INTERVAL} seconds")
    
    while True:
        check_serv00()
        time.sleep(CHECK_INTERVAL)