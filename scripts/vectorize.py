import os
import json
import time
import pickle
import faiss
import numpy as np
from dotenv import load_dotenv
from mistralai import Mistral

load_dotenv()
client = Mistral(api_key=os.getenv("MISTRAL_API_KEY"))

CLEAN_PATH = "data/events_clean.json"
INDEX_PATH = "data/events.index"
META_PATH = "data/events_metadata.pkl"
BATCH_SIZE = 10

with open(CLEAN_PATH, "r", encoding="utf-8") as f:
    events = json.load(f)

print(f"{len(events)} evenements a vectoriser (lots de {BATCH_SIZE})")

textes = [e.get("texte_complet", "") for e in events]
embeddings = []

for i in range(0, len(textes), BATCH_SIZE):
    batch = textes[i:i + BATCH_SIZE]
    print(f"Lot {i//BATCH_SIZE + 1}/{(len(textes)-1)//BATCH_SIZE + 1} ({len(batch)} evenements)...")

    while True:
        try:
            start = time.time()
            response = client.embeddings.create(model="mistral-embed", inputs=batch)
            duration = time.time() - start
            print(f"  -> OK en {duration:.2f}s")
            for item in response.data:
                embeddings.append(item.embedding)
            time.sleep(0.5)
            break
        except Exception as e:
            if "429" in str(e):
                print("  -> Rate limit, attente 10s...")
                time.sleep(10)
            else:
                raise e

vectors = np.array(embeddings, dtype="float32")
dimension = vectors.shape[1]
index = faiss.IndexFlatL2(dimension)
index.add(vectors)

faiss.write_index(index, INDEX_PATH)
with open(META_PATH, "wb") as f:
    pickle.dump(events, f)

print(f"Index FAISS cree : {index.ntotal} vecteurs de dimension {dimension}")
print(f"Sauvegarde : {INDEX_PATH} et {META_PATH}")
