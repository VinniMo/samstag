# Premier lot bars — préparation locale

> Archive de la première version. Le moteur élargi et ses résultats actuels sont
> décrits dans `RECAP_COLLECTE.md` ; les restrictions à sept bars ci-dessous ne
> sont plus celles de la version courante.

Ce changement porte sur le moteur Python de **VinniMo/samstag**,
application Flask destinée à Render. Le dépôt `lausanne-events`, qui utilise
Astro et Vercel, est une autre application et n'est pas modifié.

Les modifications restent locales. Aucun push, aucune modification de Render,
aucun déploiement. **Ce pilote affiche une page vide tant qu'aucun événement
n'a été validé** : ce comportement doit être connu avant toute intégration.

## Ce qui fonctionne

- Registre extensible de 28 bars, avec liens de preuve, quartier et incertitudes.
  Il ne constitue pas une liste de 28 collecteurs opérationnels.
- Sept sources de diagnostic sont activées : Taco’s Bar, Bruxelles Café,
  La Datcha, Brasserie du Château, Barberousse, Captain Cook et L’Étoile Blanche.
- Adaptateurs Taco’s (littéraux JSON5 publics, sans exécuter le JavaScript),
  Captain Cook (JSON public référencé par sa page), Bruxelles (articles) et
  Datcha (titres de programme à compléter).
- Lecture JSON-LD imbriquée, notamment les sous-événements d'un agenda.
- Conservation de l'URL de collecte et de la preuve de l'événement, de l'heure
  du contrôle, du motif de classement et des preuves des doublons exacts.
- File SQLite `collection_items`, distincte des anciennes données. Les anciennes
  entrées ne sont ni effacées ni affichées automatiquement.
- Rejet des soirées privées et annulées signalées par Taco's ; offres commerciales
  et programmes hebdomadaires structurés de Captain Cook exclus. Les rubriques
  non reconnues restent à vérifier : aucun filtre universel ne prétend comprendre
  toutes les annonces.
- Aucun événement fictif par défaut. `DEMO_ENABLED=1` réactive explicitement la démo.
- « Ce soir » couvre 17 h–6 h, avec rattachement à la soirée précédente avant 6 h.

## Résultat et obstacles

Le relevé horodaté est dans `collecte_diagnostic.json` : **84 entrées**,
dont **2 candidats**, **71 à vérifier** et **11 exclus**. **Zéro publication**.
Le premier passage a livré 71 entrées ; l’adaptateur Datcha a ensuite ajouté
13 titres depuis une nouvelle lecture réelle du programme. Un résultat HTTP 200
confirme seulement que la page répond, pas que son programme est actuel.

| Source | Lecture concrète | Reste à faire |
|---|---|---|
| Taco’s Bar | Calendrier public `events-data.js` et complément `events-extra.php`, référencés par les balises script officielles | Qualifier tous les tags, examiner les événements sans tag ; adresse officielle Port-Franc 6 opposée à certains annuaires |
| Bruxelles Café | Neuf articles avec titre, lien, description et affiche ; certaines dates complètes | Lire les détails et horaires explicites ; ne pas confondre carte du bar et heure d'événement |
| La Datcha | Titres et liens du programme, dont des annonces hors-les-murs et reportées | Lire chaque détail : aucune année ni adresse d'événement n'est déduite du pied de page |
| Château Music Club | Premier contrôle HTTP 404 ; passage complet ensuite en timeout | Lien PROGRAMME exact sans slash trouvé sur le site officiel : également HTTP 404 ; programme actuel à retrouver |
| Barberousse | Sept entrées JSON-LD datées de mars 2025, présentes malgré un agenda visuellement vide | Trouver le programme actuel ; ces archives ne sont pas des sorties 2026 |
| Captain Cook | Douze entrées JSON avec début, fin, image, type et catégorie | L'heure 17 h correspond parfois à l'ouverture ; vérifier l'heure réelle. Anniversaires à examiner, pas de publication automatique |
| L’Étoile Blanche | Page officielle et iframe publique Hango identifiée | Adapter le calendrier intégré ; zéro résultat du parseur principal ne signifie pas absence d'événements |

Les bars de Sous-Gare figurent dans le registre pour le lot suivant, notamment
Montriond, Hungry Bear, Ta Cave et Café du Simplon. Cette étape ne prétend pas
encore collecter tous les bars du centre et de Sous-Gare. Les clubs et autres
sorties dynamiques devront être intégrés au même mécanisme après qualification.
Les anciennes sources généralistes, musées, théâtres et salles ne sont pas
parcourues par le pilote de sept bars. La comparaison de couverture avec les
agendas généralistes reste à automatiser, à partir du dossier de recherche.

## Règles de qualité et doublons

Trois issues à la collecte : `candidate`, `review`, `excluded`. Un candidat
requiert un lieu canonique du registre, une commune d'événement explicitement
lausannoise, une catégorie reconnue, un début avec date, heure et fuseau
cohérents, un lien de preuve et une date dans les 28 prochains jours. Un lieu
dans le registre ne prouve pas l'emplacement de chacun de ses événements.

Un candidat n'est pas publié : la première validation est explicite. L'API
n'affiche que les entrées `approved`, vérifiées depuis moins de 24 heures et
toujours conformes. Un changement de contenu impose une nouvelle validation.
Une panne de source laisse donc une ancienne entrée visible au maximum pendant
ce délai. Les candidats incomplets ne peuvent pas être approuvés avec le CLI.

Identité d'une occurrence : titre normalisé + identifiant du lieu + date +
heure. Deux heures différentes créent deux séances. Deux lieux à la même
adresse restent distincts. En l'absence d'heure ou de lieu fiable, l'URL de
preuve participe aussi à l'identité. Aucun rapprochement flou automatique :
des titres différents peuvent encore produire des doublons à examiner. Une
modification d'horaire demande de retirer l'ancienne occurrence ; elle ne peut
pas être reconnue comme un simple doublon par cette première version.

Le parseur iCalendar historique reste disponible, mais ne fournit pas encore
toutes les preuves nécessaires pour publication : les récurrences et fuseaux
TZID complexes nécessitent un adaptateur dédié. Aucune récurrence n'est créée
à partir d'une formule comme « chaque vendredi ».

## Utilisation locale

Depuis une copie du dépôt, avec une base de test dédiée :

```bash
python -m venv .venv
.venv/bin/pip install -r requirements.txt
export SAMSTAG_DB="$PWD/pilot-bars.db"
.venv/bin/python collection_cli.py collect
.venv/bin/python collection_cli.py list
# Après examen de la preuve, seulement pour un candidat complet :
.venv/bin/python collection_cli.py approve IDENTIFIANT
.venv/bin/python app.py
```

`/api/sources` sépare entrées extraites, candidats, entrées à vérifier, exclusions
et événements affichables. `/api/refresh` collecte en file de validation et
n'effectue aucune approbation. Les opérations du CLI agissent sur le chemin
`SAMSTAG_DB` ; utiliser exclusivement une base locale pour cette préparation.

## Priorités suivantes

1. Valider visuellement les candidats Taco's et vérifier leur adresse, puis
   décider de l'automatisation de cette source. Le premier lot requiert une
   validation ; cette politique n'est pas encore un agenda entièrement autonome.
2. Enrichir Bruxelles et Datcha depuis les fiches détaillées. Priorité aux dates
   explicites, aux horaires de début et aux lieux hors-les-murs.
3. Résoudre Château, Hango et Barberousse avant de les considérer opérationnels.
4. Ajouter les bars de Sous-Gare puis les autres lieux animés ; ajouter une entrée
   au registre et un adaptateur ne nécessite pas de refonte de l'application.
5. Ajouter rapprochement avec les agrégateurs, suivi des annulations/disparitions,
   et une petite interface de validation. La validation source par source permettra
   ensuite d'automatiser les événements complets sans travail manuel quotidien.
6. Présenter une prévisualisation et les résultats de tests avant toute demande
   de mise en production. Render nécessite une autorisation explicite distincte.

Validation : tests unitaires sans réseau, contrôle de compilation et passage
réel sur les sept sources. Le relevé local n'est pas une garantie de stabilité
des sites externes. Le verrou de collecte existant est limité à chaque processus
Gunicorn ; un verrou partagé est encore nécessaire pour éviter des collectes
concurrentes avec plusieurs workers.
