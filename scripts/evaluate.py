"""
Script de replay de l'evaluation RAG — Puls-Events
Usage : python3 scripts/evaluate.py
"""
import os, json, time, pickle
import numpy as np
from datetime import datetime
from dotenv import load_dotenv
load_dotenv()
MISTRAL_API_KEY = os.getenv("MISTRAL_API_KEY")
if not MISTRAL_API_KEY:
    raise EnvironmentError("MISTRAL_API_KEY manquante dans .env")
from mistralai.client import Mistral
import faiss
from langchain_core.prompts import PromptTemplate
INDEX_PATH, META_PATH = "data/events.index", "data/events_metadata.pkl"
EVAL_PATH, RESULTS_PATH, SEUIL = "docs/evaluation_data.json", "docs/evaluation_results.json", 500
if not os.path.exists(INDEX_PATH): raise FileNotFoundError(f"Lancez d'abord scripts/vectorize.py")
index = faiss.read_index(INDEX_PATH)
with open(META_PATH,"rb") as f: metadata = pickle.load(f)
client = Mistral(api_key=MISTRAL_API_KEY)
prompt_template = PromptTemplate(input_variables=["context","question"], template="Tu es un assistant culturel Puls-Events.\nReponds en francais selon les evenements.\nSi aucun ne correspond, dis-le.\n\nEvenements:\n{context}\n\nQuestion: {question}\n\nReponse:")
def search_events(q):
    vec = np.array([client.embeddings.create(model="mistral-embed",inputs=[q]).data[0].embedding],dtype="float32")
    dists,idxs = index.search(vec,k=3)
    docs=[]
    for i,idx in enumerate(idxs[0]):
        if idx<len(metadata):
            e=metadata[idx]; d=float(dists[0][i])
            if d<SEUIL: docs.append({"titre":e.get("titre","?"),"lieu":e.get("lieu","?"),"date":e.get("date_debut","?"),"texte":e.get("texte_complet","")[:300],"distance":round(d,2)})
    return docs,[float(d) for d in dists[0]]
def format_context(docs):
    if not docs: return "Aucun evenement pertinent trouve."
    return "".join(f"\nEvenement {i}: {d['titre']}\nLieu: {d['lieu']}\nDate: {d['date']}\n{d['texte']}\n"+"-"*40 for i,d in enumerate(docs,1))
def generate(question,context):
    return client.chat.complete(model="mistral-small-latest",messages=[{"role":"user","content":prompt_template.format(context=context,question=question)}]).choices[0].message.content
def main():
    data=json.load(open(EVAL_PATH,encoding="utf-8"))
    questions=data.get("evaluations",[])
    print(f"Replay {len(questions)} questions...\n{'='*60}")
    resultats=[]
    for i,q in enumerate(questions,1):
        question=q["question"]; score_ref=q.get("score")
        print(f"\n[{i}/{len(questions)}] {question}")
        t0=time.time()
        docs,dists=search_events(question); ctx=format_context(docs); rep=generate(question,ctx)
        print(f"  Sources: {[d['titre'] for d in docs] or 'Aucune'}  |  Score ref: {score_ref}/3  |  {round(time.time()-t0,2)}s")
        print(f"  {rep[:120]}...")
        resultats.append({"question":question,"score_reference":score_ref,"reponse":rep,"sources":[d["titre"] for d in docs],"distances":[d["distance"] for d in docs],"pertinent":len(docs)>0})
        time.sleep(1)
    scores=[r["score_reference"] for r in resultats if r["score_reference"]]
    rapport={"date_replay":datetime.now().isoformat(),"score_moyen":round(sum(scores)/len(scores),2) if scores else None,"taux_pct":round(100*sum(1 for r in resultats if r["pertinent"])/len(resultats),1),"resultats":resultats}
    json.dump(rapport,open(RESULTS_PATH,"w",encoding="utf-8"),ensure_ascii=False,indent=2)
    print(f"\nScore moyen: {rapport['score_moyen']}/3  |  Taux: {rapport['taux_pct']}%  |  Sauvegarde: {RESULTS_PATH}")
if __name__=="__main__": main()
