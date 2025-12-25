import requests
from bs4 import BeautifulSoup
import time
import os
import datetime
import sys
import re

# --- Configuration ---
WEBHOOK_URL = os.getenv('DISCORD_WEBHOOK')
CHECK_INTERVAL = int(os.getenv('CHECK_INTERVAL', 300))

# 主要監控目標：註冊頁面 (判斷開關最準)
REGISTER_URL = "https://www.serv00.com/register-account/"
# 次要目標：首頁 (用來嘗試抓數字)
HOME_URL = "https://www.serv00.com/"

HEADERS = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
    "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8"
}

def clean_number(text):
    """Extracts purely digits from a string."""
    if not text:
        return None
    digits = re.sub(r'\D', '', str(text))
    if not digits:
        return None
    return int(digits)

def get_stats_from_home():
    """
    Attempt to fetch numbers from the Homepage.
    Returns (current_accounts, limit) or ("N/A", "N/A") if not found.
    """
    try:
        print("   -> Fetching stats from Homepage...", end=" ")
        r = requests.get(HOME_URL, headers=HEADERS, timeout=10)
        soup = BeautifulSoup(r.text, 'html.parser')
        
        curr = None
        limit = None

        # Try Method 1: Data Attributes
        account_span = soup.find('span', attrs={'data-accounts': True})
        limit_span = soup.find('span', attrs={'data-limit': True})
        
        if account_span: 
            curr = clean_number(account_span.get_text(strip=True) or account_span.get('data-accounts'))
        if limit_span: 
            limit = clean_number(limit_span.get_text(strip=True) or limit_span.get('data-limit'))

        # Try Method 2: Counter Class
        if curr is None:
            counter = soup.find(attrs={"data-count": True, "class": lambda x: x and "accounts" in x})
            if counter:
                curr = clean_number(counter.get("data-count"))

        # Format results
        c_str = str(curr) if curr else "N/A"
        l_str = str(limit) if limit else "N/A"
        print(f"Got: {c_str} / {l_str}")
        return c_str, l_str

    except Exception as e:
        print(f"Stats fetch failed: {e}")
        return "N/A", "N/A"

def send_discord_notification(reason, current_stats, limit_stats):
    data = {
        "content": "@everyone 🚨 **Serv00 Availability Detected!**",
        "embeds": [{
            "title": "Registration Page Open!",
            "description": (
                f"The 'Limit Reached' message has disappeared!\n\n"
                f"**Reason:** {reason}\n"
                f"**Stats (Est.):** {current_stats} / {limit_stats}\n\n"
                f"[Click here to Register]({REGISTER_URL})"
            ),
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
        # Step 1: Check Registration Page (The Source of Truth)
        response = requests.get(REGISTER_URL, headers=HEADERS, timeout=20)
        
        if response.status_code != 200:
            print(f"Error: Status {response.status_code}")
            return

        html_content = response.text
        
        # The key phrase indicating the server is full
        limit_reached_msg = "The server user limit has been reached"
        is_registration_page = "Register account" in html_content

        if is_registration_page:
            if limit_reached_msg in html_content:
                print("--> 🔒 Closed (Limit reached message found).")
            else:
                # Step 2: It's OPEN! Now try to get the numbers from Homepage
                print("--> 🎉 OPEN! Fetching details...")
                curr_stats, limit_stats = get_stats_from_home()
                
                send_discord_notification("Limit message disappeared", curr_stats, limit_stats)
        else:
            print("--> ⚠️ Warning: Not on registration page (Check URL/Structure).")

    except Exception as e:
        print(f"Unexpected Error: {e}")

if __name__ == "__main__":
    if not WEBHOOK_URL:
        print("❌ Error: DISCORD_WEBHOOK environment variable is not set.")
        sys.exit(1)
        
    print("🚀 Serv00 Monitor started...")
    print(f"ℹ️  Target: {REGISTER_URL}")
    print(f"ℹ️  Checking interval: {CHECK_INTERVAL} seconds")
    
    while True:
        check_serv00()
        time.sleep(CHECK_INTERVAL)