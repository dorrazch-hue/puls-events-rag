# Puls-Events RAG Chatbot

![Tests](https://github.com/dorrazch-hue/puls-events-rag/actions/workflows/tests.yml/badge.svg)

Chatbot intelligent de recommandation d'événements culturels pour le Grand Paris, basé sur une architecture RAG (Retrieval-Augmented Generation).

## Technologies

- **LangChain** — orchestration du pipeline RAG (RunnableLambda, PromptTemplate)
- **Mistral AI** — `mistral-embed` (vecteurs 1024 dimensions) + `mistral-small-latest` (génération)
- **FAISS** — base vectorielle IndexFlatL2 avec seuil de pertinence (distance < 500)
- **Open Agenda API** — agenda `que-faire-a-paris`, jusqu'à **300 événements** avec pagination
- **Python 3.11** — python-dotenv, requests, pickle, unittest

## Prérequis

- Python 3.11+ → https://www.python.org/downloads/
- Clé API Mistral → https://console.mistral.ai/
- Clé API Open Agenda → https://openagenda.com/developers

## Installation

```bash
git clone https://github.com/dorrazch-hue/puls-events-rag.git
cd puls-events-rag
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
cp .env.example .env
# Remplir MISTRAL_API_KEY et OPENAGENDA_API_KEY dans .env
```

## Utilisation

```bash
# 1. Collecter les événements (jusqu'à 300 via pagination)
python3 scripts/fetch_events.py

# 2. Prétraitement (filtre temporel + géographique Grand Paris)
python3 scripts/preprocess.py

# 3. Vectorisation par lots de 10 (avec retry 429)
python3 scripts/vectorize.py

# 4. Lancer le chatbot
python3 scripts/chatbot.py
```

## Tests

```bash
python3 -m unittest tests_unitaires.py -v
```

**8/8 tests passés** — utilise des fixtures indépendantes (`tests/fixtures_events.json`) et un index FAISS synthétique créé automatiquement. Aucune clé API requise.

## Structure du projet

```
puls-events-rag/
├── scripts/
│   ├── fetch_events.py     # Collecte Open Agenda (300 événements, pagination)
│   ├── preprocess.py       # Nettoyage, filtre temporel et géographique
│   ├── vectorize.py        # Vectorisation par lots (BATCH_SIZE=10)
│   └── chatbot.py          # Pipeline RAG LangChain avec mesure des temps
├── tests/
│   └── fixtures_events.json
├── tests_unitaires.py      # 8 tests unitaires
├── docs/
│   ├── rapport_technique_puls_events.docx
│   ├── presentation_puls_events.pptx
│   ├── evaluation_rag.md          # Score : 73% de pertinence
│   └── evaluation_data.json       # Données reproductibles (5 questions, scores, justification seuil FAISS)
├── .github/
│   └── workflows/
│       └── tests.yml              # CI GitHub Actions
├── .env.example
├── requirements.txt
└── README.md
```

## Périmètre géographique

Grand Paris : Paris, Saint-Ouen, Boulogne, Vincennes, Montreuil, Saint-Denis, Nanterre, Neuilly — événements des **12 derniers mois**.

## Évaluation RAG

Score mesuré sur 5 questions annotées : **73% de pertinence (2.2/3)**

Données complètes dans `docs/evaluation_data.json` (questions, réponses, distances FAISS, justification du seuil 500).
