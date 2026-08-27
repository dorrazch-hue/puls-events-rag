# Puls-Events RAG Chatbot

Chatbot intelligent basé sur la technologie RAG (Retrieval-Augmented Generation) pour répondre à des questions sur les événements culturels à Paris et Grand Paris.

## Technologies utilisées

- **LangChain** : orchestration du pipeline RAG
- **Mistral AI** : embeddings () et génération ()
- **FAISS** : base de données vectorielle pour la recherche sémantique
- **Open Agenda API** : source des données événementielles

## Prérequis

- Python 3.11+
- Clé API Mistral AI
- Clé API Open Agenda

## Installation

```bash
git clone https://github.com/dorrazch-hue/puls-events-rag.git
cd puls-events-rag
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
```

Créer un fichier `.env` à la racine :

```
MISTRAL_API_KEY=ta_cle_mistral
OPENAGENDA_API_KEY=ta_cle_openagenda
```

## Utilisation

### 1. Collecter les données
```bash
python3 scripts/fetch_events.py
```

### 2. Nettoyer les données
```bash
python3 scripts/preprocess.py
```

### 3. Vectoriser et indexer
```bash
python3 scripts/vectorize.py
```

### 4. Lancer le chatbot
```bash
python3 scripts/chatbot.py
```

### 5. Lancer les tests
```bash
python3 tests_unitaires.py
```

## Structure du projet

```
puls-events-rag/
├── scripts/
│   ├── fetch_events.py    # Récupération des données Open Agenda
│   ├── preprocess.py      # Nettoyage et structuration
│   ├── vectorize.py       # Vectorisation FAISS
│   └── chatbot.py         # Chatbot RAG interactif
├── tests_unitaires.py     # Tests unitaires
├── requirements.txt       # Dépendances Python
├── .gitignore
└── README.md
```

## Périmètre géographique

Grand Paris (Paris + communes voisines), événements des 12 derniers mois.
