import os
import time
import pickle
import faiss
import numpy as np
from dotenv import load_dotenv
from mistralai import Mistral
from langchain.schema import Document
from langchain.prompts import PromptTemplate
from langchain.schema.runnable import RunnableLambda, RunnablePassthrough

load_dotenv()

MISTRAL_API_KEY = os.getenv("MISTRAL_API_KEY")
client = Mistral(api_key=MISTRAL_API_KEY)

# Chargement index FAISS et metadonnees
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


def search_events(question: str) -> list:
    """Recherche les 3 evenements les plus proches dans FAISS."""
    start = time.time()
    vector = embed_question(question)
    distances, indices = index.search(vector, k=3)
    duration = time.time() - start
    print(f"[Temps recherche FAISS] {duration:.2f}s")

    docs = []
    for i, idx in enumerate(indices[0]):
        if idx < len(metadata):
            event = metadata[idx]
            if distances[0][i] < 500:
                docs.append(Document(
                    page_content=event.get("texte_complet", ""),
                    metadata={
                        "titre": event.get("titre", "Sans titre"),
                        "lieu": event.get("lieu", "Non precise"),
                        "date": event.get("date_debut", "Non precisee"),
                        "distance": float(distances[0][i])
                    }
                ))
    return docs


def format_context(docs: list) -> str:
    """Formate les documents en contexte pour le LLM."""
    if not docs:
        return "Aucun evenement pertinent trouve."
    context = ""
    for i, doc in enumerate(docs, 1):
        context += f"\nEvenement {i}: {doc.metadata['titre']}\n"
        context += f"Lieu: {doc.metadata['lieu']}\n"
        context += f"Date: {doc.metadata['date']}\n"
        context += f"Description: {doc.page_content[:300]}\n"
        context += "-" * 40
    return context


def generate_response(inputs: dict) -> str:
    """Genere une reponse avec Mistral a partir du contexte."""
    start = time.time()
    response = client.chat.complete(
        model="mistral-small-latest",
        messages=[{"role": "user", "content": inputs["prompt"]}]
    )
    duration = time.time() - start
    print(f"[Temps generation] {duration:.2f}s")
    return response.choices[0].message.content


# Prompt template LangChain
prompt_template = PromptTemplate(
    input_variables=["context", "question"],
    template=(
        "Tu es un assistant culturel pour Puls-Events.\n"
        "Reponds en francais a la question en te basant sur les evenements suivants.\n"
        "Si aucun evenement ne correspond, dis-le clairement.\n\n"
        "Evenements disponibles:\n{context}\n\n"
        "Question: {question}\n\n"
        "Reponse:"
    )
)

# Chaine RAG LangChain
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
    print("Tapez 'quit' pour quitter\n")

    while True:
        question = input("Vous: ").strip()
        if question.lower() == "quit":
            break
        if not question:
            continue

        total_start = time.time()
        result = rag_chain.invoke({"question": question})
        total_duration = time.time() - total_start

        print(f"\nAssistant: {result['response']}")
        if result["sources"]:
            print(f"\nSources utilisees: {', '.join(result['sources'])}")
        print(f"[Temps total] {total_duration:.2f}s\n")


if __name__ == "__main__":
    main()
