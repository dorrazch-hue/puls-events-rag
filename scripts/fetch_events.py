import requests
import json
import os
from datetime import datetime, timedelta
from dotenv import load_dotenv

load_dotenv()
API_KEY = os.getenv("OPENAGENDA_API_KEY")

AGENDA_SLUG = "que-faire-a-paris"
DATE_MIN = (datetime.now() - timedelta(days=365)).strftime("%Y-%m-%dT%H:%M:%S")

def recuperer_evenements():
    url = f"https://api.openagenda.com/v2/agendas/{AGENDA_SLUG}/events"
    
    tous_les_evenements = []
    params = {
        "key": API_KEY,
        "size": 100,
        "timings[gte]": DATE_MIN,
        "lang": "fr"
    }
    
    print("Récupération des événements de Paris...")
    response = requests.get(url, params=params)
    
    if response.status_code == 200:
        data = response.json()
        tous_les_evenements = data.get("events", [])
        print(f"{len(tous_les_evenements)} événements récupérés !")
    else:
        print(f"Erreur : {response.status_code}")
    
    return tous_les_evenements

if __name__ == "__main__":
    evenements = recuperer_evenements()
    
    with open("data/events.json", "w", encoding="utf-8") as f:
        json.dump(evenements, f, ensure_ascii=False, indent=2)
    
    print("Événements sauvegardés dans data/events.json")