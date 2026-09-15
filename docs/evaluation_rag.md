# Évaluation du Système RAG — Puls-Events

## Méthodologie

5 questions types ont été posées au chatbot. Chaque réponse est notée de 1 à 3 selon sa pertinence :
- **3** : réponse complète et précise
- **2** : réponse correcte mais incomplète
- **1** : réponse hors sujet ou manquante

---

## Questions annotées

### Q1 : "Quels concerts ont lieu à Paris ce mois-ci ?"
**Réponse du chatbot :** Liste 3 événements musicaux avec lieu et date.
**Score : 3/3**
*La recherche sémantique via mistral-embed est excellente pour les requêtes musicales générales.*

---

### Q2 : "Y a-t-il des expositions d'art moderne cette semaine ?"
**Réponse du chatbot :** Cite 3 expositions d'art contemporain avec description (Basquiat/Pompidou, MEP, Palais de Tokyo).
**Score : 3/3**
*La sémantique artistique est bien capturée par le modèle d'embedding.*

---

### Q3 : "Quelles activités pour enfants à Saint-Ouen ce weekend ?"
**Réponse du chatbot :** Propose 1 événement à Saint-Ouen (spectacle de marionnettes) — couverture banlieue limitée.
**Score : 2/3**
*Le filtre géographique précis sur une commune est perfectible.*

---

### Q4 : "Quels événements gratuits peut-on voir cette semaine ?"
**Réponse du chatbot :** Ne peut pas filtrer par prix, donne des événements génériques.
**Score : 1/3**
*L'API Open Agenda ne fournit pas systématiquement le champ prix. Amélioration future : enrichissement des données.*

---

### Q5 : "Quels festivals se déroulent en juillet ?"
**Réponse du chatbot :** Donne des festivals mais sans filtre temporel strict sur juillet.
**Score : 2/3**
*Le filtre temporel précis sur un mois donné est perfectible.*

---

## Résultats

| Question | Score |
|---|---|
| Concerts à Paris | 3/3 |
| Expositions art moderne | 3/3 |
| Activités famille Saint-Ouen | 2/3 |
| Événements gratuits | 1/3 |
| Festivals juillet | 2/3 |
| **TOTAL** | **11/15** |

**Score moyen : 2.2/3 = 73% de pertinence**

---

## Analyse

**Points forts :**
- Recherche sémantique générale : excellente (concerts, expositions)
- Couverture événementielle : 300 événements indexés via pagination Open Agenda
- Temps de réponse : 2 à 3 secondes (mesuré sur les 5 questions, min 1.89s / max 2.67s)

**Axes d'amélioration :**
- Enrichir les données avec le champ prix (actuellement absent de l'API)
- Affiner le filtre géographique par commune (Saint-Ouen, Boulogne, etc.)
- Améliorer le filtre temporel précis (par mois ou semaine)
- Ajouter des métadonnées : catégorie, public cible (famille, adulte, enfant)
