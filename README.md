# Puls-Events RAG Chatbot

Chatbot RAG pour les evenements culturels a Paris et Grand Paris.

## Technologies

- **LangChain** : orchestration RAG (RunnableLambda, PromptTemplate)
- **Mistral AI** : embeddings (mistral-embed, 1024 dimensions) et generation (mistral-small-latest)
- **FAISS** : index vectoriel IndexFlatL2 avec seuil de pertinence
- **Open Agenda API** : agenda que-faire-a-paris (100 evenements, Grand Paris)

## Prerequis

- Python 3.11+
- Cle API Mistral AI : https://console.mistral.ai
- Cle API Open Agenda : https://openagenda.com

## Installation

1. Cloner : git clone https://github.com/dorrazch-hue/puls-events-rag.git
2. Creer le venv : python3 -m venv venv
3. Activer : source venv/bin/activate
4. Installer : pip install -r requirements.txt
5. Configurer : cp .env.example .env  puis remplir vos cles API

## Utilisation

1. Collecter les donnees : python3 scripts/fetch_events.py
2. Nettoyer : python3 scripts/preprocess.py
3. Vectoriser par lots : python3 scripts/vectorize.py
4. Lancer le chatbot : python3 scripts/chatbot.py
5. Lancer les tests : python3 tests_unitaires.py

## Structure

- scripts/fetch_events.py : recuperation Open Agenda (cree data/ automatiquement)
- scripts/preprocess.py : nettoyage et structuration
- scripts/vectorize.py : vectorisation par lots de 10 (mistral-embed)
- scripts/chatbot.py : chatbot RAG LangChain + Mistral avec mesure des temps
- tests/fixtures_events.json : donnees de test independantes
- tests_unitaires.py : 8 tests unitaires (donnees, FAISS, erreurs)
- docs/rapport_technique_puls_events.docx : rapport technique
- docs/presentation_puls_events.pptx : presentation 12 slides
- docs/evaluation_rag.md : evaluation RAG sur 5 questions annotees (score : 73%)
- .env.example : modele de configuration

## Perimetre geographique

Grand Paris (Paris, Saint-Ouen, Boulogne, Vincennes, Montreuil, Saint-Denis, Nanterre, Neuilly).
Evenements des 12 derniers mois.
