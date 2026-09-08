"""
Script de replay de l'evaluation RAG — Puls-Events
Rejoue les 5 questions via rag_chain (chatbot.py) — meme pipeline que le chatbot reel.

Note : les scores affiches sont les annotations manuelles de reference stockees dans
docs/evaluation_data.json. Les nouvelles reponses generees sont sauvegardees dans
docs/evaluation_results.json pour une relecture et notation manuelle.

Usage : python3 scripts/evaluate.py
"""
import os
import json
import time
import sys
from datetime import datetime
from dotenv import load_dotenv

load_dotenv()

# Importer rag_chain depuis chatbot.py (meme pipeline, pas de reimplementation)
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from chatbot import rag_chain

EVAL_PATH = "docs/evaluation_data.json"
RESULTS_PATH = "docs/evaluation_results.json"


def main():
    with open(EVAL_PATH, encoding="utf-8") as f:
        data = json.load(f)

    questions = data.get("evaluations", [])
    if not questions:
        raise ValueError("Cle 'evaluations' introuvable dans evaluation_data.json")

    print("Replay " + str(len(questions)) + " questions...\n" + "=" * 60)
    resultats = []

    for i, q in enumerate(questions, 1):
        question = q["question"]
        score_ref = q.get("score")

        print("\n[" + str(i) + "/" + str(len(questions)) + "] " + question)
        t0 = time.time()

        result = rag_chain.invoke({"question": question})
        reponse = result["response"]
        sources = result["sources"]
        duree = round(time.time() - t0, 2)

        print("  Sources   : " + str(sources if sources else "Aucune"))
        print("  Score ref : " + str(score_ref) + "/3  (annotation manuelle — a reevaluer)")
        print("  Duree     : " + str(duree) + "s")
        print("  Reponse   : " + reponse[:150] + "...")

        resultats.append({
            "question": question,
            "score_reference_manuel": score_ref,
            "note_score": "Score issu de l'annotation manuelle initiale. Relire la reponse generee pour reevaluer.",
            "reponse_generee": reponse,
            "sources": sources,
            "pertinent": len(sources) > 0,
            "duree_s": duree
        })
        time.sleep(1)

    scores = [r["score_reference_manuel"] for r in resultats if r["score_reference_manuel"] is not None]
    rapport = {
        "date_replay": datetime.now().isoformat(),
        "modele_generation": "mistral-small-latest",
        "modele_embedding": "mistral-embed",
        "note_evaluation": (
            "Les scores de reference proviennent de l'annotation manuelle initiale (evaluation_data.json). "
            "Pour une evaluation a jour, relire les reponses generees et noter manuellement."
        ),
        "score_moyen_reference": round(sum(scores) / len(scores), 2) if scores else None,
        "taux_documents_retrouves_pct": round(
            100 * sum(1 for r in resultats if r["pertinent"]) / len(resultats), 1
        ),
        "resultats": resultats
    }

    with open(RESULTS_PATH, "w", encoding="utf-8") as f:
        json.dump(rapport, f, ensure_ascii=False, indent=2)

    print("\n" + "=" * 60)
    print("Reponses sauvegardees dans : " + RESULTS_PATH)
    print("Score moyen (reference manuelle) : " + str(rapport["score_moyen_reference"]) + "/3")
    print("Documents retrouves par FAISS    : " + str(rapport["taux_documents_retrouves_pct"]) + "%")
    print("-> Relire les reponses generees pour noter manuellement la pertinence.")


if __name__ == "__main__":
    main()
