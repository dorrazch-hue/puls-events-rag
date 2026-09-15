"""
Script de replay de l'evaluation RAG — Puls-Events
Rejoue les 5 questions via rag_chain (chatbot.py) — meme pipeline que le chatbot reel.

Note : les scores affiches sont les annotations manuelles de reference stockees dans
docs/evaluation_data.json. Les nouvelles reponses generees sont sauvegardees dans
docs/evaluation_results.json pour une relecture et notation manuelle.

Les annotations manuelles existantes (score_nouvelle_annotation, distances_faiss,
note_score, synthese) sont preservees si le fichier de resultats existe deja.

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

# Champs ajoutes manuellement apres relecture — a preserver entre les replays
CHAMPS_MANUELS = ("score_nouvelle_annotation", "note_score", "distances_faiss")


def charger_annotations_existantes(results_path):
    """
    Charge les annotations manuelles depuis un fichier de resultats existant.
    Retourne (annotations_par_question, synthese, note_evaluation, score_moyen_nouvelle_annotation).
    Les annotations sont indexees par texte de question pour une correspondance exacte.
    """
    if not os.path.exists(results_path):
        return {}, None, None, None
    try:
        with open(results_path, encoding="utf-8") as f:
            existing = json.load(f)
    except (json.JSONDecodeError, IOError):
        return {}, None, None, None

    annotations = {}
    for r in existing.get("resultats", []):
        question = r.get("question", "")
        annotations[question] = {
            champ: r[champ] for champ in CHAMPS_MANUELS if champ in r
        }

    return (
        annotations,
        existing.get("synthese"),
        existing.get("note_evaluation"),
        existing.get("score_moyen_nouvelle_annotation"),
    )


def main():
    with open(EVAL_PATH, encoding="utf-8") as f:
        data = json.load(f)

    questions = data.get("evaluations", [])
    if not questions:
        raise ValueError("Cle 'evaluations' introuvable dans evaluation_data.json")

    # Charger les annotations manuelles avant d'ecraser le fichier
    annotations_existantes, synthese_existante, note_existante, score_nouvelle_existant = \
        charger_annotations_existantes(RESULTS_PATH)

    if annotations_existantes:
        print("Annotations manuelles existantes preservees pour "
              + str(len(annotations_existantes)) + " question(s).")

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

        entree = {
            "question": question,
            "score_reference_manuel": score_ref,
            "note_score": "Score issu de l'annotation manuelle initiale. Relire la reponse generee pour reevaluer.",
            "reponse_generee": reponse,
            "sources": sources,
            "pertinent": len(sources) > 0,
            "duree_s": duree
        }

        # Fusionner les annotations manuelles existantes (ecrasent les valeurs par defaut)
        if question in annotations_existantes:
            entree.update(annotations_existantes[question])

        resultats.append(entree)
        time.sleep(1)

    scores = [r["score_reference_manuel"] for r in resultats if r["score_reference_manuel"] is not None]
    rapport = {
        "date_replay": datetime.now().isoformat(),
        "modele_generation": "mistral-small-latest",
        "modele_embedding": "mistral-embed",
        "note_evaluation": note_existante if note_existante else (
            "Les scores de reference proviennent de l'annotation manuelle initiale (evaluation_data.json). "
            "Pour une evaluation a jour, relire les reponses generees et noter manuellement."
        ),
        "score_moyen_reference": round(sum(scores) / len(scores), 2) if scores else None,
        "taux_documents_retrouves_pct": round(
            100 * sum(1 for r in resultats if r["pertinent"]) / len(resultats), 1
        ),
        "resultats": resultats
    }

    # Preserver les champs de niveau superieur ajoutes manuellement
    if score_nouvelle_existant is not None:
        rapport["score_moyen_nouvelle_annotation"] = score_nouvelle_existant
    if synthese_existante is not None:
        rapport["synthese"] = synthese_existante

    with open(RESULTS_PATH, "w", encoding="utf-8") as f:
        json.dump(rapport, f, ensure_ascii=False, indent=2)

    print("\n" + "=" * 60)
    print("Reponses sauvegardees dans : " + RESULTS_PATH)
    print("Score moyen (reference manuelle) : " + str(rapport["score_moyen_reference"]) + "/3")
    print("Documents retrouves par FAISS    : " + str(rapport["taux_documents_retrouves_pct"]) + "%")
    if synthese_existante:
        print("Annotations manuelles preservees (synthese, scores_nouvelle_annotation, distances_faiss).")
    print("-> Relire les reponses generees pour noter manuellement la pertinence.")


if __name__ == "__main__":
    main()
