import unittest
import json
import os
import faiss
from datetime import datetime, timedelta

FIXTURES_PATH = "tests/fixtures_events.json"
INDEX_PATH = "data/events.index"

class TestPulsEvents(unittest.TestCase):

    def setUp(self):
        with open(FIXTURES_PATH, "r", encoding="utf-8") as f:
            self.events = json.load(f)

    def test_donnees_non_vides(self):
        self.assertGreater(len(self.events), 0, "La liste d'evenements est vide")

    def test_evenements_moins_un_an(self):
        un_an = datetime.now() - timedelta(days=365)
        for e in self.events:
            date_str = e.get("date_debut", "")
            if date_str:
                date = datetime.strptime(date_str[:10], "%Y-%m-%d")
                self.assertGreater(date, un_an, f"Evenement trop ancien: {e.get('titre')}")

    def test_ville_paris(self):
        communes = ['paris', 'saint-ouen', 'boulogne', 'vincennes',
                    'montreuil', 'saint-denis', 'nanterre', 'neuilly']
        for e in self.events:
            ville = e.get("ville", e.get("lieu", "")).lower()
            ok = any(c in ville for c in communes)
            self.assertTrue(ok, f"Ville hors perimetre: {ville}")

    def test_champs_obligatoires(self):
        champs = ["titre", "texte_complet"]
        for e in self.events:
            for champ in champs:
                self.assertIn(champ, e, f"Champ manquant: {champ}")
                self.assertTrue(e[champ], f"Champ vide: {champ}")

    def test_index_faiss_existe(self):
        self.assertTrue(os.path.exists(INDEX_PATH),
            "Index FAISS absent. Lancez d'abord scripts/vectorize.py")

if __name__ == "__main__":
    unittest.main(verbosity=2)
