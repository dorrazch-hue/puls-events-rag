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
    """Transforme une question en vecteur."""
    while True:
        try:
            response = client.embeddings.create(
                model="mistral-embed",
                inputs=[texte]
            )
            return response.data[0].embedding
        except Exception as e:
            if "429" in str(e):
                time.sleep(10)
            else:
                raise e

def rechercher_evenements(question, index, metadonnees, k=3):
    """Cherche les k événements les plus pertinents."""
    vecteur = obtenir_embedding(question)
    vecteur_np = np.array([vecteur], dtype='float32')
    distances, indices = index.search(vecteur_np, k)
    
    resultats = []
    for idx in indices[0]:
        if idx < len(metadonnees):
            resultats.append(metadonnees[idx])
    return resultats

def generer_reponse(question, evenements):
    """Génère une réponse avec Mistral basée sur les événements trouvés."""
    contexte = "\n\n".join([
        f"- {e['titre']} | {e['lieu']}, {e['ville']} | {e['date_debut'][:10]}\n  {e['description'][:200]}"
        for e in evenements
    ])
    
    prompt = f"""Tu es un assistant spécialisé en événements culturels à Paris.
Basé sur les événements suivants, réponds à la question de l'utilisateur.

Événements disponibles :
{contexte}

Question : {question}

Réponds de manière naturelle et précise en français."""

    response = client.chat.complete(
        model="mistral-small-latest",
        messages=[{"role": "user", "content": prompt}]
    )
    return response.choices[0].message.content

def lancer_chatbot():
    # Charger l'index et les métadonnées
    print("Chargement de la base vectorielle...")
    index = faiss.read_index('data/events.index')
    with open('data/events_metadata.pkl', 'rb') as f:
        metadonnees = pickle.load(f)
    print(f"✅ {index.ntotal} événements chargés !")
    print("\n🎭 Chatbot Puls-Events prêt ! (tapez 'quit' pour quitter)\n")
    
    while True:
        question = input("Vous : ")
        if question.lower() == 'quit':
            break
        
        print("🔍 Recherche en cours...")
        evenements = rechercher_evenements(question, index, metadonnees)
        
        print("🤖 Génération de la réponse...")
        reponse = generer_reponse(question, evenements)
        
        print(f"\nAssistant : {reponse}\n")

if __name__ == "__main__":
    lancer_chatbot()