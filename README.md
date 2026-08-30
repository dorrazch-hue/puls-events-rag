# Puls-Events RAG Chatbot

Chatbot RAG pour les evenements culturels a Paris et Grand Paris.

## Technologies

- **LangChain** : orchestration RAG (RunnableLambda, PromptTemplate)
- **Mistral AI** : embeddings (mistral-embed) et generation (mistral-small-latest)
- **FAISS** : index vectoriel IndexFlatL2
- **Open Agenda API** : agenda que-faire-a-paris

## Prerequis

- Python 3.11+
- Cle API Mistral AI : https://console.mistral.ai
- Cle API Open Agenda : https://openagenda.com

## Installation

1. Cloner le depot : git clone https://github.com/dorrazch-hue/puls-events-rag.git
2. Creer le venv : python3 -m venv venv
3. Activer : source venv/bin/activate
4. Installer : pip install -r requirements.txt
5. Copier : cp .env.example .env  puis remplir vos cles API

## Utilisation

1. Collecter les donnees : python3 scripts/fetch_events.py
2. Nettoyer : python3 scripts/preprocess.py
3. Vectoriser : python3 scripts/vectorize.py
4. Lancer le chatbot : python3 scripts/chatbot.py
5. Lancer les tests : python3 tests_unitaires.py

## Structure

- scripts/fetch_events.py : recuperation Open Agenda (100 evenements)
- scripts/preprocess.py : nettoyage et structuration
- scripts/vectorize.py : vectorisation FAISS
- scripts/chatbot.py : chatbot RAG LangChain + Mistral
- tests/fixtures_events.json : donnees de test
- tests_unitaires.py : 5 tests unitaires
- .env.example : modele de configuration

## Perimetre geographique

Grand Paris (Paris, Saint-Ouen, Boulogne, Vincennes, Montreuil, Saint-Denis, Nanterre, Neuilly).
Evenements des 12 derniers mois.
