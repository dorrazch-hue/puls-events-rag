import os
import json
import requests
import time
from datetime import datetime, timedelta
from dotenv import load_dotenv

load_dotenv()
os.makedirs('data', exist_ok=True)

API_KEY = os.getenv("OPENAGENDA_API_KEY")
AGENDA_SLUG = "que-faire-a-paris"
DATE_MIN = (datetime.now() - timedelta(days=365)).strftime("%Y-%m-%dT%H:%M:%S")
URL = f"https://api.openagenda.com/v2/agendas/{AGENDA_SLUG}/events"
MAX_EVENTS = 300
PAGE_SIZE = 100

tous_les_evenements = []
after = None

print(f"Collecte des evenements (max {MAX_EVENTS})...")

while len(tous_les_evenements) < MAX_EVENTS:
    params = {
        "key": API_KEY,
        "size": PAGE_SIZE,
        "timings[gte]": DATE_MIN,
        "lang": "fr"
    }
    if after:
        params["after"] = after

    response = requests.get(URL, params=params)
    if response.status_code != 200:
        print(f"Erreur API : {response.status_code}")
        break

    data = response.json()
    events = data.get("events", [])
    if not events:
        print("Plus d evenements disponibles.")
        break

    tous_les_evenements.extend(events)
    print(f"  Page recue : {len(events)} evenements | Total : {len(tous_les_evenements)}")

    after = data.get("after")
    if not after:
        break

    time.sleep(0.5)

tous_les_evenements = tous_les_evenements[:MAX_EVENTS]

with open("data/events.json", "w", encoding="utf-8") as f:
    json.dump(tous_les_evenements, f, ensure_ascii=False, indent=2)

print(f"{len(tous_les_evenements)} evenements sauvegardes dans data/events.json")
