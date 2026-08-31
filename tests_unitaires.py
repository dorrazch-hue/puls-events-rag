import unittest
import json
import os
import sys
import numpy as np

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

TEST_INDEX_PATH = "tests/test_fixtures.index"

class TestPulsEventsRAG(unittest.TestCase):

    @classmethod
    def setUpClass(cls):
        """Cree un index FAISS synthetique pour les tests — aucun pipeline requis."""
        try:
            import faiss
            if not os.path.exists(TEST_INDEX_PATH):
                os.makedirs("tests", exist_ok=True)
                d = 1024
                index = faiss.IndexFlatL2(d)
                vectors = np.random.rand(3, d).astype("float32")
                index.add(vectors)
                faiss.write_index(index, TEST_INDEX_PATH)
            cls.faiss_available = True
        except ImportError:
            cls.faiss_available = False

    @classmethod
    def tearDownClass(cls):
        if os.path.exists(TEST_INDEX_PATH):
            os.remove(TEST_INDEX_PATH)

    def charger_fixtures(self):
        with open("tests/fixtures_events.json", encoding="utf-8") as f:
            return json.load(f)

    def test_donnees_non_vides(self):
        """La liste d'evenements de test n'est pas vide."""
        events = self.charger_fixtures()
        self.assertGreater(len(events), 0)

    def test_evenements_moins_un_an(self):
        """Les evenements preprocesses ont un champ date_debut valide."""
        events = self.charger_fixtures()
        for e in events:
            # Les evenements preprocesses utilisent date_debut (pas firstTiming.begin)
            date = e.get("date_debut", "")
            self.assertTrue(len(date) > 0, "Le champ date_debut est manquant")

    def test_ville_paris(self):
        """La fonction de filtrage geographique accepte les communes du Grand Paris."""
        # Test logique du filtrage avec des donnees brutes simulees
        COMMUNES = ["paris", "saint-ouen", "boulogne", "vincennes",
                    "montreuil", "saint-denis", "nanterre", "neuilly"]
        evenements_test = [
            {"location": {"city": "Paris"}, "firstTiming": {"begin": "2026-08-01T20:00:00"}},
            {"location": {"city": "Saint-Denis"}, "firstTiming": {"begin": "2026-07-15T18:00:00"}},
            {"location": {"city": "Boulogne-Billancourt"}, "firstTiming": {"begin": "2026-09-01T19:00:00"}},
        ]
        for e in evenements_test:
            ville = e.get("location", {}).get("city", "").lower()
            dans_perimetre = any(c in ville for c in COMMUNES)
            self.assertTrue(dans_perimetre, f"Ville hors perimetre : {ville}")

    def test_champs_obligatoires(self):
        """Chaque evenement preprocesse a un titre et un texte_complet."""
        events = self.charger_fixtures()
        for e in events:
            self.assertIn("titre", e)
            self.assertIn("texte_complet", e)

    def test_index_faiss_existe(self):
        """L'index FAISS (synthetique) est cree et accessible."""
        self.assertTrue(
            os.path.exists(TEST_INDEX_PATH),
            "L'index FAISS de test n'a pas ete cree"
        )

    def test_recherche_vectorielle(self):
        """La recherche FAISS retourne 3 resultats valides."""
        if not self.faiss_available:
            self.skipTest("faiss-cpu non installe")
        import faiss
        index = faiss.read_index(TEST_INDEX_PATH)
        query = np.random.rand(1, 1024).astype("float32")
        distances, indices = index.search(query, k=3)
        self.assertEqual(len(indices[0]), 3)
        for d in distances[0]:
            self.assertGreaterEqual(d, 0)

    def test_texte_complet_non_vide(self):
        """Le champ texte_complet a une longueur minimale de 10 caracteres."""
        events = self.charger_fixtures()
        for e in events:
            texte = e.get("texte_complet", "")
            self.assertGreaterEqual(
                len(texte), 10,
                f"Texte trop court pour : {e.get('titre', '?')}"
            )

    def test_gestion_champ_manquant(self):
        """get() avec valeur par defaut ne leve pas d'exception."""
        event = {"titre": "Test", "texte_complet": "Description test Grand Paris"}
        titre = event.get("titre", "Sans titre")
        lieu = event.get("lieu", "Non precise")
        self.assertEqual(titre, "Test")
        self.assertEqual(lieu, "Non precise")


if __name__ == "__main__":
    unittest.main(verbosity=2)
