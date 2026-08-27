import json
import unittest
from datetime import datetime, timedelta

class TestEvenementsRAG(unittest.TestCase):
    
    def setUp(self):
        """Charge les données avant chaque test."""
        with open('data/events_clean.json', 'r', encoding='utf-8') as f:
            self.evenements = json.load(f)
    
    def test_donnees_non_vides(self):
        """Vérifie qu'on a bien récupéré des événements."""
        self.assertGreater(len(self.evenements), 0)
        print(f"✅ {len(self.evenements)} événements chargés")
    
    def test_evenements_moins_un_an(self):
        """Vérifie que tous les événements datent de moins d'un an."""
        date_limite = datetime.now() - timedelta(days=365)
        for e in self.evenements:
            date_str = e.get('date_debut', '')
            if date_str:
                date = datetime.fromisoformat(date_str[:19])
                self.assertGreaterEqual(
                    date, date_limite,
                    f"Événement trop ancien : {e['titre']} ({date_str[:10]})"
                )
        print("✅ Tous les événements datent de moins d'un an")
    
    def test_ville_paris(self):
        """Vérifie que les événements sont bien dans le Grand Paris."""
        communes_grand_paris = [
            'paris', 'saint-ouen', 'boulogne', 'vincennes',
            'montreuil', 'saint-denis', 'nanterre', 'neuilly'
        ]
        for e in self.evenements:
            ville = e.get('ville', '').lower()
            est_grand_paris = any(c in ville for c in communes_grand_paris)
            self.assertTrue(
                est_grand_paris,
                f"Événement hors Grand Paris : {e['titre']} ({e['ville']})"
            )
        print("✅ Tous les événements sont dans le Grand Paris")
    
    def test_champs_obligatoires(self):
        """Vérifie que chaque événement a les champs requis."""
        champs = ['uid', 'titre', 'description', 'lieu', 'ville', 'date_debut']
        for e in self.evenements:
            for champ in champs:
                self.assertIn(champ, e, f"Champ manquant : {champ}")
                self.assertTrue(e[champ], f"Champ vide : {champ}")
        print("✅ Tous les champs obligatoires sont présents")
    
    def test_index_faiss_existe(self):
        """Vérifie que l'index FAISS a bien été créé."""
        import os
        self.assertTrue(
            os.path.exists('data/events.index'),
            "L'index FAISS n'existe pas !"
        )
        print("✅ Index FAISS présent")

if __name__ == "__main__":
    unittest.main(verbosity=2)