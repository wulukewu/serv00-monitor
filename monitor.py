import requests
from bs4 import BeautifulSoup
import time
import os
import datetime
import sys

# --- Configuration ---
# Get configuration from Environment Variables
WEBHOOK_URL = os.getenv('DISCORD_WEBHOOK')
# Default check interval: 300 seconds (5 minutes)
CHECK_INTERVAL = int(os.getenv('CHECK_INTERVAL', 300))
TARGET_URL = "https://www.serv00.com/"

# User-Agent to mimic a standard browser
HEADERS = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
}

def send_discord_notification(current, limit):
    """Sends a formatted notification to Discord via Webhook."""
    data = {
        "content": "@everyone 🚨 **Serv00 Availability Detected!**",
        "embeds": [{
            "title": "Register Now!",
            "description": f"Slots are open!\n\n**Current Accounts:** {current}\n**Limit:** {limit}\n\n[Click here to Register]({TARGET_URL})",
            "color": 5763719  # Green color
        }]
    }
    try:
        requests.post(WEBHOOK_URL, json=data)
        print("✅ Discord notification sent successfully.")
    except Exception as e:
        print(f"❌ Failed to send Discord notification: {e}")

def check_serv00():
    """Scrapes the target page and compares account numbers."""
    timestamp = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    print(f"[{timestamp}] Checking...", end=" ")
    
    try:
        response = requests.get(TARGET_URL, headers=HEADERS, timeout=15)
        if response.status_code != 200:
            print(f"Error: Page returned status code {response.status_code}")
            return

        soup = BeautifulSoup(response.text, 'html.parser')
        
        # Locate the specific data spans based on HTML structure
        account_span = soup.find('span', attrs={'data-accounts': True})
        limit_span = soup.find('span', attrs={'data-limit': True})

        if account_span and limit_span:
            try:
                # Logic: Try attribute first, fall back to text content if attribute is empty
                curr_text = account_span.get('data-accounts') or account_span.text.strip()
                limit_text = limit_span.get('data-limit') or limit_span.text.strip()
                
                curr_num = int(curr_text)
                limit_num = int(limit_text)
                
                print(f"Status: {curr_num}/{limit_num}", end=" ")

                if curr_num < limit_num:
                    print("--> 🎉 SLOTS OPEN! Sending notification...")
                    send_discord_notification(curr_num, limit_num)
                else:
                    print("--> Full.")
            except ValueError:
                print("Error parsing numbers from HTML.")
        else:
            print("Could not find the data elements. HTML structure might have changed.")

    except Exception as e:
        print(f"Connection Error: {e}")

if __name__ == "__main__":
    # Validate environment variables
    if not WEBHOOK_URL:
        print("❌ Error: DISCORD_WEBHOOK environment variable is not set.")
        sys.exit(1)
        
    print("🚀 Serv00 Monitor started...")
    print(f"ℹ️  Checking interval: {CHECK_INTERVAL} seconds")
    
    # Main Loop
    while True:
        check_serv00()
        time.sleep(CHECK_INTERVAL)