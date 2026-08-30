# Puls-Events RAG Chatbot

Chatbot de recommandation d'événements culturels pour le Grand Paris, basé sur une architecture RAG (Retrieval-Augmented Generation).

## Technologies

- **LangChain** - orchestration du pipeline RAG (RunnableLambda, PromptTemplate)
- **Mistral AI** - mistral-embed (vecteurs 1024 dimensions) + mistral-small-latest (generation)
- **FAISS** - base vectorielle IndexFlatL2 avec seuil de pertinence (distance < 500)
- **Open Agenda API** - agenda que-faire-a-paris, jusqu'a 300 evenements avec pagination
- **Python 3.11** - python-dotenv, requests, pickle, unittest

## Prerequis

- Python 3.11+ : https://www.python.org/downloads/
- Cle API Mistral : https://console.mistral.ai/
- Cle API Open Agenda : https://openagenda.com/developers

## Installation

    git clone https://github.com/dorrazch-hue/puls-events-rag.git
    cd puls-events-rag
    python3 -m venv venv
    source venv/bin/activate
    pip install -r requirements.txt
    cp .env.example .env
    # Remplir MISTRAL_API_KEY et OPENAGENDA_API_KEY dans .env

## Utilisation

    python3 scripts/fetch_events.py
    python3 scripts/preprocess.py
    python3 scripts/vectorize.py
    python3 scripts/chatbot.py

## Tests

    python3 -m unittest tests_unitaires.py -v

8/8 tests passes - fixtures independantes (tests/fixtures_events.json)

## Structure du projet

    puls-events-rag/
    scripts/
        fetch_events.py     - Collecte Open Agenda (300 evenements, pagination)
        preprocess.py       - Nettoyage et structuration
        vectorize.py        - Vectorisation par lots (BATCH_SIZE=10)
        chatbot.py          - Pipeline RAG LangChain avec mesure des temps
    tests/
        fixtures_events.json
    tests_unitaires.py      - 8 tests unitaires
    docs/
        rapport_technique_puls_events.docx
        presentation_puls_events.pptx
        evaluation_rag.md   - Score : 73% de pertinence
    .env.example
    requirements.txt
    README.md

## Perimetre geographique

Grand Paris : Paris, Saint-Ouen, Boulogne, Vincennes, Montreuil, Saint-Denis, Nanterre, Neuilly
Evenements des 12 derniers mois.

## Evaluation RAG

Score sur 5 questions annotees : 73% de pertinence (2.2/3)
