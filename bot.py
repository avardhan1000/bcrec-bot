from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from webdriver_manager.chrome import ChromeDriverManager
from urllib.parse import urljoin
import time
import json
import requests
import os

# ---------- ENV VARIABLES ----------
BOT_TOKEN = os.environ.get("8549877130:AAHV3BGt90sE93YwUMxlobaZCqEVP-kxbyY")
CHAT_ID = os.environ.get("5246585884")

# ---------- TELEGRAM ----------
def send_telegram(msg):
    url = f"https://api.telegram.org/bot{BOT_TOKEN}/sendMessage"
    requests.post(url, data={"chat_id": CHAT_ID, "text": msg})

# ---------- STORAGE ----------
def load_old():
    try:
        with open("notices.json", "r") as f:
            return json.load(f)
    except:
        return []

def save_new(data):
    with open("notices.json", "w") as f:
        json.dump(data, f)

# ---------- SCRAPER (UPDATED PAGE) ----------
def get_notices():
    chrome_options = Options()
    chrome_options.add_argument("--headless")
    chrome_options.add_argument("--no-sandbox")
    chrome_options.add_argument("--disable-dev-shm-usage")

    service = Service(ChromeDriverManager().install())
    driver = webdriver.Chrome(service=service, options=chrome_options)

    driver.get("https://www.bcrec.ac.in/notice-list")
    time.sleep(8)

    notices = []
    base_url = "https://www.bcrec.ac.in/"

    # 🔥 TARGET NOTICE SECTION
    rows = driver.find_elements(By.TAG_NAME, "a")

    for row in rows:
        text = row.text.strip()
        href = row.get_attribute("href")

        if href:
            href = urljoin(base_url, href)

        # only notice PDFs
        if href and ".pdf" in href.lower() and len(text) > 5:
            notices.append((text, href))

    driver.quit()
    return notices

# ---------- MAIN LOOP ----------
print("🚀 Bot running (Notice Page)...")

while True:
    try:
        old = load_old()
        current = get_notices()

        new_items = [n for n in current if n not in old]

        if new_items:
            print("📢 New notice found!")

            for notice in new_items:
                message = f"📢 New Notice:\n{notice[0]}\n{notice[1]}"
                print("Sending:", message)
                send_telegram(message)
                time.sleep(5)

        else:
            print("No new notices...")

        save_new(current)

    except Exception as e:
        print("Error:", e)

    time.sleep(120)  # check every 2 minutes