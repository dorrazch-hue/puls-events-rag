import unittest
import json
import os
import faiss
import numpy as np
from datetime import datetime, timedelta

FIXTURES_PATH = "tests/fixtures_events.json"
INDEX_PATH = "data/events.index"

class TestPulsEvents(unittest.TestCase):

    def setUp(self):
        with open(FIXTURES_PATH, "r", encoding="utf-8") as f:
            self.events = json.load(f)

    def test_donnees_non_vides(self):
        self.assertGreater(len(self.events), 0, "La liste d evenements est vide")

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
            "Index FAISS absent. Lancez scripts/vectorize.py")

    def test_recherche_vectorielle(self):
        if not os.path.exists(INDEX_PATH):
            self.skipTest("Index FAISS absent, test ignore")
        index = faiss.read_index(INDEX_PATH)
        self.assertGreater(index.ntotal, 0, "Index FAISS vide")
        vecteur_test = np.random.rand(1, index.d).astype("float32")
        distances, indices = index.search(vecteur_test, k=3)
        self.assertEqual(len(indices[0]), 3, "La recherche doit retourner 3 resultats")
        self.assertTrue(all(d >= 0 for d in distances[0]), "Distances doivent etre positives")

    def test_texte_complet_non_vide(self):
        for e in self.events:
            texte = e.get("texte_complet", "")
            self.assertGreater(len(texte), 10,
                f"texte_complet trop court pour: {e.get('titre')}")

    def test_gestion_champ_manquant(self):
        event_incomplet = {"titre": "Test", "lieu": "Paris"}
        texte = event_incomplet.get("texte_complet", "")
        self.assertEqual(texte, "", "Un champ absent doit retourner une chaine vide")

if __name__ == "__main__":
    unittest.main(verbosity=2)
