import os
import time
import pickle
import faiss
import numpy as np
from dotenv import load_dotenv
from mistralai.client import Mistral
from langchain.schema import Document
from langchain.prompts import PromptTemplate
from langchain.schema.runnable import RunnableLambda, RunnablePassthrough

load_dotenv()

MISTRAL_API_KEY = os.getenv("MISTRAL_API_KEY")
client = Mistral(api_key=MISTRAL_API_KEY)

# Chargement index FAISS et métadonnées
index = faiss.read_index("data/events.index")
with open("data/events_metadata.pkl", "rb") as f:
    metadata = pickle.load(f)

def embed_question(question: str) -> np.ndarray:
    """Vectorise la question avec Mistral."""
    start = time.time()
    response = client.embeddings.create(model="mistral-embed", inputs=[question])
    duration = time.time() - start
    print(f"[Temps embedding] {duration:.2f}s")
    return np.array([response.data[0].embedding], dtype="float32")

def search_events(question: str) -> list[Document]:
    """Recherche les 3 événements les plus proches dans FAISS."""
    start = time.time()
    vector = embed_question(question)
    distances, indices = index.search(vector, k=3)
    duration = time.time() - start
    print(f"[Temps recherche FAISS] {duration:.2f}s")
    
    docs = []
    for i, idx in enumerate(indices[0]):
        if idx < len(metadata):
            event = metadata[idx]
            # Seuil de pertinence
            if distances[0][i] < 500:
                docs.append(Document(
                    page_content=event.get("texte_complet", ""),
                    metadata={
                        "titre": event.get("titre", "Sans titre"),
                        "lieu": event.get("lieu", "Non précisé"),
                        "date": event.get("date_debut", "Non précisée"),
                        "distance": float(distances[0][i])
                    }
                ))
    return docs

def format_context(docs: list[Document]) -> str:
    """Formate les documents en contexte pour le LLM."""
    if not docs:
        return "Aucun événement pertinent trouvé."
    context = ""
    for i, doc in enumerate(docs, 1):
        context += f"
Événement {i}: {doc.metadata['titre']}
"
        context += f"Lieu: {doc.metadata['lieu']}
"
        context += f"Date: {doc.metadata['date']}
"
        context += f"Description: {doc.page_content[:300]}
"
        context += "-" * 40
    return context

def generate_response(inputs: dict) -> str:
    """Génère une réponse avec Mistral à partir du contexte."""
    start = time.time()
    response = client.chat.complete(
        model="mistral-small-latest",
        messages=[{"role": "user", "content": inputs["prompt"]}]
    )
    duration = time.time() - start
    print(f"[Temps génération] {duration:.2f}s")
    return response.choices[0].message.content

# Prompt template LangChain
prompt_template = PromptTemplate(
    input_variables=["context", "question"],
    template="""Tu es un assistant culturel pour Puls-Events.
Réponds en français à la question en te basant sur les événements suivants.
Si aucun événement ne correspond, dis-le clairement.

Événements disponibles:
{context}

Question: {question}

Réponse:"""
)

# Chaîne RAG LangChain
rag_chain = (
    RunnablePassthrough()
    | RunnableLambda(lambda x: {
        "docs": search_events(x["question"]),
        "question": x["question"]
    })
    | RunnableLambda(lambda x: {
        "prompt": prompt_template.format(
            context=format_context(x["docs"]),
            question=x["question"]
        ),
        "sources": [d.metadata["titre"] for d in x["docs"]]
    })
    | RunnableLambda(lambda x: {
        "response": generate_response(x),
        "sources": x["sources"]
    })
)

def main():
    print("Chatbot Puls-Events (LangChain + Mistral + FAISS)")
    print("Tapez 'quit' pour quitter
")
    
    while True:
        question = input("Vous: ").strip()
        if question.lower() == "quit":
            break
        if not question:
            continue
        
        total_start = time.time()
        result = rag_chain.invoke({"question": question})
        total_duration = time.time() - total_start
        
        print(f"
Assistant: {result['response']}")
        if result["sources"]:
            print(f"
Sources utilisées: {', '.join(result['sources'])}")
        print(f"[Temps total] {total_duration:.2f}s
")

if __name__ == "__main__":
    main()
