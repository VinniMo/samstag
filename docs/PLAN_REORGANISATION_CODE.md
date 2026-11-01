# Plan d’action — réorganisation du code Samstag

**Préparé le 1er novembre 2026. Statut : plan à exécuter, aucun déplacement de code réalisé.**

## Objectif pour vous

Pouvoir retrouver un collecteur par son nom, distinguer le site des règles de publication et comprendre où intervenir. Le [guide du dossier](SE_REPERER.md) restera l’entrée simple ; ce document décrit les travaux techniques du troisième point.

Les deux premières étapes de rangement sont faites : documentation accessible et archives regroupées. Le code Python est encore à la racine.

## Périmètre et ordre de départ

Le rangement doit conserver les événements extraits, les URL, les règles qualité, la base SQLite, les commandes et le design. Les événements diurnes déjà implémentés localement font partie de la référence à préserver.

Avant de commencer, terminer les corrections de fiabilité identifiées dans L2/L3 et les vérifications d’exploitation L4 prévues par le plan global. La préparation locale (cartographie et référence de tests) peut avancer indépendamment. Une extraction pilote anticipée reste possible comme lot local explicitement séparé, sans annoncer que tout L5 est débloqué.

Le dossier contient de nombreux travaux locaux non commités : les inventorier et établir un point de reprise Git identifiable avant d’ajouter une migration. Ne pas les écraser ni les attribuer à la réorganisation.

## Architecture cible

```text
samstag/
├── __init__.py              # sans démarrage ni accès à la base à l’import
├── config.py                # réglages
├── domain/
│   ├── agenda.py            # périodes, rubriques et recherche
│   └── quality.py           # règles de publication
├── storage/
│   └── sqlite.py            # accès SQLite, schéma actuel conservé
├── collection/
│   ├── registry.py          # lieux et sources, lecture des JSON
│   ├── result.py            # résultat d’une collecte
│   ├── http.py              # requêtes, délais et erreurs
│   ├── runner.py            # orchestration
│   ├── worker.py            # répétition des passes
│   ├── cli.py               # commandes de collecte
│   ├── report.py            # rapport de collecte
│   ├── health.py            # santé des sources
│   ├── parsers/             # lecteurs génériques : JSON-LD, ICS, HTML
│   └── adapters/            # lecteurs nommés : vidy.py, docks.py…
├── web/
│   ├── app.py               # création de l’application
│   ├── routes.py            # API et pages
│   ├── feedback.py          # retours utilisateurs
│   └── wsgi.py              # instance utilisée par Gunicorn
├── templates/
└── static/
```

`data/`, `docs/`, `tests/`, `e2e/`, `scripts/` et `deploy/` restent à la racine. Les chemins de base et les secrets restent externes au paquet. `run_service.py` peut rester un lanceur à la racine. Le dossier cible s’appelle `samstag` ; sa coexistence avec la racine du projet est normale en Python.

## Sessions d’implémentation

Chaque ligne est un lot autonome : modification, vérification, documentation, puis arrêt avant le lot suivant. Prévoir une à deux séances courtes pour un lot ; le nombre exact dépend des dépendances découvertes.

| Étape | Action concrète | Critère de fin |
|---|---|---|
| R0 — Référence | Inventorier l’arbre Git, les imports, chemins et commandes ; figer une référence locale identifiable et les sorties des fixtures | Changements antérieurs distingués ; tests de référence et limites enregistrés |
| R1 — Pilote Vidy | Créer le paquet et extraire uniquement les fonctions Vidy de `programme_adapters.py` vers `samstag/collection/adapters/vidy.py` | Ancien import compatible ; séances, confirmations et erreurs identiques sur fixtures |
| R2 — Autres lecteurs | Extraire les autres adaptateurs, un site ou petit groupe par séance | Chaque source conserve ses identifiants, preuves, horaires et résultats ; inventaire documentaire actualisé |
| R3 — Outils de collecte | Extraire lecteurs génériques, client HTTP, registre, résultats, puis orchestration et worker | Dispatch, limites réseau, verrou, statuts et commandes inchangés |
| R4 — Règles et stockage | Déplacer `agenda.py`, `collection_quality.py` et `db.py`, en plusieurs sous-lots | Même programme public et mêmes décisions sur la base isolée ; schéma SQLite inchangé |
| R5 — Web | Séparer création Flask, routes, retours et instance WSGI ; déplacer templates et ressources avec chemins explicites | API, cookies, retours, assets et parcours navigateur inchangés ; import du paquet sans initialisation de base |
| R6 — Finalisation locale | Faire utiliser les nouveaux chemins aux scripts, tests et modèles de déploiement ; retirer les anciens relais devenus inutiles | Aucun import ancien restant, commandes documentées fonctionnelles, guides et tests à jour |
| R7 — Livraison séparée | Préparer une version revue, sauvegarde et retour arrière ; livrer uniquement après autorisation explicite | Version servie identifiable, contrôles publics et prochaine passe de collecte vérifiés |

### R1 : première implémentation détaillée

1. Relever les fonctions `vidy_kind`, `vidy_blocks`, `confirm_vidy`, `parse_vidy` et leurs dépendances dans `programme_adapters.py`.
2. Créer les fichiers `__init__.py` nécessaires, sans effet de bord.
3. Déplacer les fonctions Vidy sans changer leur logique. Laisser Hango dans le module actuel à ce stade.
4. Garder des réexports explicites dans `programme_adapters.py` pour les anciens imports ; ne pas copier les fonctions. Le dispatch existant utilise le nouveau lecteur.
5. Vérifier les dépendances vers `agenda`, `bar_adapters` et `venue_adapters`. Ne pas déplacer ces modules entiers pour le pilote ; déplacer un utilitaire minimal seulement si cela évite un cycle d’import.
6. Adapter les tests aux vrais points d’utilisation : les remplacements de fonctions, de configuration et d’horloge doivent viser le module qui les consulte.
7. Exécuter les cas Vidy : séance diurne, soirée, mauvais horaire, mauvais lieu, annulation, fiche inaccessible et confirmation obligatoire ; puis `make check`.
8. Consigner le nouveau chemin dans COLLECTEURS et SE_REPERER, et le résultat dans la passation. Fin de session.

### R2 : ordre conseillé des lecteurs

Après Vidy : CityClub ; Naftule/Boulimie ; Arsenic ; Grange/Pulloff ; Folklor/MAD ; JazzOnze+ ; Docks/Romandie/D! ; Jumeaux/Chorus/Bellevaux ; bars et widgets Hango ; agrégateurs. Adapter le découpage aux dépendances constatées. Ne pas embarquer une réparation de source dans son déplacement.

Les lecteurs d’un format partagé peuvent rester regroupés (par exemple Hango). Un petit fichier de compatibilité peut conserver les anciens imports durant la transition, avec une tâche explicite pour sa suppression. Les aides communes doivent avoir un rôle précis, pas devenir un nouveau gros module `utils.py`.

## Contrôles et preuve d’équivalence

- **Tous les lots :** `make check`, imports et chemins concernés ; aucune collecte réelle par défaut.
- **Adaptateurs :** comparer les champs des mêmes fixtures avant/après, y compris les cas refusés et les erreurs. Ne pas comparer uniquement le nombre de sorties.
- **Stockage et orchestration :** utiliser une base isolée ; vérifier observations, décisions, publication, dédoublonnage existant, verrou et erreurs partielles.
- **Web et finalisation :** `make report`, lancement local, contrôle des API et assets ; E2E Chromium, puis matrice complète pour la validation finale.
- **Changements d’imports :** attention à `patch()`, aux objets de configuration et aux imports circulaires. Un réexport ne redirige pas automatiquement tous les remplacements utilisés par les tests.
- **Chemins :** vérifier `Path(__file__)`, lecture des JSON, templates, fichiers statiques, base absolue, fixture E2E, Makefile et commandes Gunicorn/systemd. Ne pas dépendre du répertoire courant pour trouver les ressources.

Les vérifications doivent conserver les règles diurnes, les soirées après minuit, les changements d’heure suisses, la fraîcheur et les exclusions. Les fichiers sources de preuve ne sont pas supprimés. Une vérification réseau ciblée n’est envisagée que si une incertitude ne peut pas être résolue sur fixture, dans un lot distinct et borné.

## Ce qui reste hors de ce rangement

Les migrations de schéma SQLite (L5.6), nouveaux contrats de données (L5.7), changement de dispatch (L5.5), allègement API, correctifs de collecteurs et nouvelles sources sont des évolutions séparées. Le rangement n’exige ni changement de framework ni changement de base. Le registre d’adaptateurs pourra être introduit après les extractions, dans une PR dédiée.

Le déplacement du code ne doit pas servir à livrer implicitement les autres modifications locales. La livraison devra préciser exactement ce qu’elle contient, notamment l’évolution diurne si elle est encore non déployée.

## Retour arrière et suivi

Un lot correspond à un commit ou une PR identifiable, avec problème, nouveaux chemins, vérifications et limites. En cas de régression locale, revenir sur ce lot uniquement, en préservant les travaux antérieurs. Ne jamais utiliser une remise à zéro globale de l’arbre de travail.

R1 à R6 ne nécessitent aucune modification du VPS. Pour R7, sauvegarder code et base compatibles, préparer la restauration et demander l’autorisation de production selon les consignes du projet. Render reste hors périmètre.

À chaque fin de séance : mettre à jour ce tableau, le suivi global, la passation et le guide des dossiers. Les anciens chemins ne sont supprimés qu’après vérification de leurs consommateurs.

| Étape | État | Preuve |
|---|---|---|
| Plan | Prêt | Document relu, liens locaux vérifiés |
| R0 | À faire | — |
| R1 | À faire | — |
| R2 | À faire, par petits lots | — |
| R3 | À faire | — |
| R4 | À faire | — |
| R5 | À faire | — |
| R6 | À faire | — |
| R7 | À faire, autorisation requise | — |

**Prochaine action recommandée : R0.** Le pilote Vidy vient ensuite, quand la référence est stabilisée et que les prérequis du plan global sont levés ou qu’un lot pilote anticipé a été explicitement retenu.
