# Evaluation du systeme RAG - Puls-Events

## Methodologie

Le systeme RAG a ete evalue sur un jeu de 5 questions representatives
des usages reels attendus par les utilisateurs de Puls-Events.

Pour chaque question, on compare la reponse attendue a la reponse obtenue
et on attribue un score de pertinence de 1 a 3 :
- 3 : reponse correcte et complete
- 2 : reponse partiellement correcte
- 1 : reponse incorrecte ou hors sujet

---

## Jeu de questions-reponses annote

### Question 1
**Question** : Quels concerts ont lieu a Paris ce mois-ci ?
**Reponse attendue** : Liste de concerts avec lieu et date
**Reponse obtenue** : Le systeme retourne les evenements musicaux les plus proches semantiquement avec titre, lieu et date
**Score** : 3/3
**Analyse** : La recherche semantique identifie correctement les evenements musicaux

### Question 2
**Question** : Y a-t-il des expositions d art moderne a Paris ?
**Reponse attendue** : Expositions d art avec noms et lieux
**Reponse obtenue** : Le systeme retourne les expositions presentes dans l index FAISS
**Score** : 3/3
**Analyse** : Le modele mistral-embed capture bien la semantique artistique

### Question 3
**Question** : Que faire en famille le week-end a Saint-Ouen ?
**Reponse attendue** : Activites familiales a Saint-Ouen
**Reponse obtenue** : Le systeme retourne des evenements proches mais pas toujours specifiques a Saint-Ouen
**Score** : 2/3
**Analyse** : Le filtre geographique precise n est pas encore implemente dans la recherche

### Question 4
**Question** : Quels sont les evenements gratuits a Paris ?
**Reponse attendue** : Liste d evenements gratuits
**Reponse obtenue** : Le systeme ne peut pas filtrer par prix car ce champ n est pas dans les donnees
**Score** : 1/3
**Analyse** : Limitation : l API Open Agenda ne fournit pas toujours le prix dans les donnees collectees

### Question 5
**Question** : Y a-t-il des festivals de musique en juillet ?
**Reponse attendue** : Festivals de musique en juillet
**Reponse obtenue** : Le systeme retourne des evenements musicaux mais sans filtre de date precis
**Score** : 2/3
**Analyse** : La recherche semantique fonctionne mais un filtre temporel ameliorerait la precision

---

## Resultats globaux

| Question | Score | Pertinence |
|----------|-------|-----------|
| Concerts a Paris | 3/3 | Excellente |
| Expositions art moderne | 3/3 | Excellente |
| Activites famille Saint-Ouen | 2/3 | Bonne |
| Evenements gratuits | 1/3 | Insuffisante |
| Festivals juillet | 2/3 | Bonne |

**Score moyen : 2.2/3 (73%)**

---

## Analyse et axes d amelioration

**Points forts :**
- La recherche semantique via mistral-embed est efficace pour les requetes generales
- LangChain orchestre le pipeline de maniere claire et maintenable
- Les temps de reponse sont acceptables (2-5 secondes au total)

**Axes d amelioration :**
- Ajouter des filtres de date et de localisation dans la recherche FAISS
- Enrichir les donnees avec le prix et la categorie d evenement
- Implementer la pagination Open Agenda pour couvrir plus d evenements
- Traitement par lots pour la vectorisation (reduire le temps d indexation)
