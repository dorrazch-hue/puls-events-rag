import json
import os
import faiss
import numpy as np
import pickle
import time
from mistralai.client import Mistral
from dotenv import load_dotenv

load_dotenv()
client = Mistral(api_key=os.getenv("MISTRAL_API_KEY"))

def obtenir_embedding(texte):
    """Transforme un texte en vecteur avec Mistral."""
    while True:
        try:
            response = client.embeddings.create(
                model="mistral-embed",
                inputs=[texte]
            )
            return response.data[0].embedding
        except Exception as e:
            if "429" in str(e):
                print("    ⏳ Limite atteinte, pause 10 secondes...")
                time.sleep(10)
            else:
                raise e

def vectoriser_evenements():
    with open('data/events_clean.json', 'r', encoding='utf-8') as f:
        evenements = json.load(f)
    
    print(f"Vectorisation de {len(evenements)} événements...")
    
    vecteurs = []
    for i, e in enumerate(evenements):
        print(f"  {i+1}/{len(evenements)} - {e['titre'][:50]}...")
        embedding = obtenir_embedding(e['texte_complet'])
        vecteurs.append(embedding)
        time.sleep(0.5)
    
    vecteurs_np = np.array(vecteurs, dtype='float32')
    dimension = len(vecteurs[0])
    index = faiss.IndexFlatL2(dimension)
    index.add(vecteurs_np)
    
    faiss.write_index(index, 'data/events.index')
    with open('data/events_metadata.pkl', 'wb') as f:
        pickle.dump(evenements, f)
    
    print(f"Index FAISS créé avec {index.ntotal} vecteurs !")

if __name__ == "__main__":
    vectoriser_evenements()