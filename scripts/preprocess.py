import json
import os
from datetime import datetime, timedelta

DATE_MIN = datetime.now() - timedelta(days=365)

def extraire_texte(champ):
    """Extrait le texte français d'un champ multilingue."""
    if isinstance(champ, dict):
        return champ.get('fr', '') or champ.get('en', '') or ''
    return champ or ''

def nettoyer_evenement(e):
    """Transforme un événement brut en version propre."""
    titre = extraire_texte(e.get('title'))
    description = extraire_texte(e.get('description'))
    lieu = e.get('location', {}).get('name', '')
    ville = e.get('location', {}).get('city', '')
    date_debut = e.get('firstTiming', {}).get('begin', '')
    
    return {
        'uid': e.get('uid'),
        'titre': titre,
        'description': description,
        'lieu': lieu,
        'ville': ville,
        'date_debut': date_debut,
        'texte_complet': f"{titre}. {description} Lieu: {lieu}, {ville}."
    }

COMMUNES_GRAND_PARIS = [
    'paris', 'saint-ouen', 'boulogne', 'vincennes',
    'montreuil', 'saint-denis', 'nanterre', 'neuilly'
]

def filtrer_evenements(evenements):
    """Garde uniquement les événements de moins d'un an dans le Grand Paris."""
    resultats = []
    for e in evenements:
        date_str = e.get('firstTiming', {}).get('begin', '')
        ville = e.get('location', {}).get('city', '').lower()
        if date_str:
            try:
                date = datetime.fromisoformat(date_str[:19])
                dans_perimetre = any(c in ville for c in COMMUNES_GRAND_PARIS)
                if date >= DATE_MIN and dans_perimetre:
                    resultats.append(e)
            except:
                pass
    return resultats

if __name__ == "__main__":
    with open('data/events.json', 'r', encoding='utf-8') as f:
        evenements = json.load(f)
    
    print(f"Événements bruts : {len(evenements)}")
    
    filtres = filtrer_evenements(evenements)
    print(f"Après filtre (moins d'un an) : {len(filtres)}")
    
    propres = [nettoyer_evenement(e) for e in filtres]
    
    with open('data/events_clean.json', 'w', encoding='utf-8') as f:
        json.dump(propres, f, ensure_ascii=False, indent=2)
    
    print("Données nettoyées sauvegardées dans data/events_clean.json")