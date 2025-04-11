import requests
from bs4 import BeautifulSoup
import hashlib
import schedule
import time
import datetime
from keep_alive import keep_alive  # Flask web server to keep Replit alive

# === TELEGRAM CONFIGURATION ===
TELEGRAM_TOKEN = '7421213642:AAFAtuwvlwODCiGrzRhnsvC6V_lFPPEwz54'  # Replace this with your actual token
CHAT_IDS = ['5230902484']  # Replace with your Telegram user ID

# === APARTMENT SOURCES TO MONITOR ===
urls = {
    "Migra": "https://www.migra.at/immobilienangebot/wohnen/",
    "Wohnen.at": "https://www.wohnen.at/angebot/unser-wohnungsangebot/",
    "EBG": "https://www.ebg-wohnen.at/immobilien/wohnung",
    "EGW": "https://www.egw.at/suche",
    "ÖSW": "https://www.oesw.at/immobilienangebot/sofort-wohnen.html?financingType=2&rooms=3",
    "ÖVW": "https://www.oevw.at/suche",
    "WienSüd": "https://www.wiensued.at/wohnen/?dev=&city=&search=&space-from=&space-to=&room-from=3&room-to=3&rent=1&state%5B%5D=sofort#search-results",
    "Heimbau": "https://www.heimbau.at/wiedervermietung",
    "NHG": "https://www.nhg.at/immobilienangebot/wohnungsangebot/",
    "Gebös": "https://www.geboes.at/app/suche/ergebnisse?stocktype=Wohnung&state=Wien",
    "Sofort-Wohnen": "https://sofort-wohnen.at/wohnungen?keywordSearch=wien&ordering=-date_posted&owning=true&renting=true&subsidized=true&private=true&page=1&pageSize=10"
}

# === STORE PREVIOUS STATES ===
previous_hashes = {}

# === TELEGRAM MESSAGE FUNCTION ===
def send_telegram_message(message):
    for chat_id in CHAT_IDS:
        url = f'https://api.telegram.org/bot{TELEGRAM_TOKEN}/sendMessage'
        data = {'chat_id': chat_id, 'text': message}
        response = requests.post(url, data=data)
        print(f"📨 Sent to {chat_id} → {response.status_code} | {response.text}")

# === FETCH AND HASH WEBSITE CONTENT ===
def get_content_hash(url):
    try:
        response = requests.get(url, timeout=10)
        soup = BeautifulSoup(response.text, 'html.parser')
        content = soup.get_text()
        return hashlib.md5(content.encode('utf-8')).hexdigest()
    except Exception as e:
        print(f"[ERROR] Could not fetch {url}: {e}")
        return None

# === CHECK WEBSITES FOR CHANGES ===
def check_websites():
    print(f"🔁 Checked at {datetime.datetime.utcnow().strftime('%H:%M:%S')} UTC")
    now = datetime.datetime.now().time()

    # Run only between 9:00–17:00 CEST = 7:00–15:00 UTC
    if now >= datetime.time(7, 0) and now <= datetime.time(15, 0):
        print(f"🕒 Inside monitoring hours ({now}) UTC")
        for name, url in urls.items():
            current_hash = get_content_hash(url)
            if current_hash is None:
                continue

            if name in previous_hashes and previous_hashes[name] != current_hash:
                message = f"🔄 {name} has been updated!\n{url}"
                print(f"✅ Change detected: {name}")
                send_telegram_message(message)
            else:
                print(f"➖ No change: {name}")

            previous_hashes[name] = current_hash
    else:
        print(f"⏸️ Outside monitoring hours ({now}) UTC")

# === KEEP THE BOT ALIVE (Replit) ===
keep_alive()

# === OPTIONAL: Notify that bot started ===
send_telegram_message("🚀 Apartment bot is running and watching listings!")

# === SCHEDULE EVERY 5 MINUTES ===
schedule.every(5).minutes.do(check_websites)

print("🟢 Website monitor is running. Press Ctrl+C to stop.")

while True:
    schedule.run_pending()
    time.sleep(1)
