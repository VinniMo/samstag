# Se repérer dans le dossier Samstag

Commencez par le [README principal](../README.md). Pour suivre le projet au quotidien, les deux documents utiles sont [État actuel](ETAT_ACTUEL.md) et [Collecteurs](COLLECTEURS.md).

## La carte du dossier actuel

| Emplacement | Ce qu’on y trouve | Quand l’ouvrir |
|---|---|---|
| `docs/` | guides actuels, état et suivi | pour comprendre le projet |
| `docs/archives/` | anciens bilans et diagnostics conservés | pour retrouver une mesure passée |
| `docs/audits/` | audit daté et mesures qui l’accompagnent | pour vérifier les constats |
| `docs/diagrams/` | schémas de travail et architecture cible | pour voir la suite prévue |
| `data/` | listes des lieux, bars et sources | pour savoir ce qui est recensé |
| `templates/` et `static/` | page, textes, styles, images et interactions | pour comprendre l’interface |
| `samstag/collection/adapters/` | collecteurs déjà réorganisés (Vidy pour le moment) | pour trouver leur implémentation |
| fichiers Python à la racine | reste du moteur, migration progressive | pour les modifications techniques |
| `tests/` | vérifications du moteur | pour contrôler les règles et collecteurs |
| `e2e/` | parcours automatiques dans un navigateur | pour vérifier l’utilisation du site |
| `deploy/infomaniak/` | installation et exploitation du serveur | lors d’une livraison autorisée |
| `scripts/`, `schemas/`, `Makefile` | commandes et validation des registres | pour préparer et vérifier le développement |

## Les fichiers techniques, en langage simple

- `app.py` reçoit les demandes du navigateur ; `agenda.py` classe les sorties par période.
- `scraper.py` organise la collecte ; les fichiers `*_adapters.py` lisent les différents sites.
- `collection_quality.py` vérifie si une sortie peut être publiée.
- `db.py` conserve les données ; `source_registry.py` lit les registres de `data/`.
- `collection_worker.py` répète la collecte ; `run_service.py` supervise le site et ce collecteur.
- `feedback.py` et `feedback_cli.py` gèrent les retours des utilisateurs.
- `PRODUCT.md` décrit le produit ; `DESIGN.md` documente son apparence ; `AGENTS.md` donne les consignes de travail.

Les noms techniques historiques sont conservés pour éviter de casser le fonctionnement. La migration a commencé le 2 novembre : Vidy est dans `samstag/collection/adapters/vidy.py`. Les autres modules restent à la racine ; `programme_adapters.py` garde les imports compatibles et le dispatch.

## Dossiers masqués : généralement rien à faire

Finder peut cacher les noms commençant par un point. `.venv/` et `e2e/node_modules/` contiennent les outils installés ; `.local/` contient les données de développement ; `.artifacts/` reçoit les rapports locaux. Ils ne doivent pas être confondus avec le catalogue de production.

`.git/` conserve l’historique, `.github/` les contrôles automatiques, `.devcontainer/` l’environnement de développement. `.claude/` et `.impeccable/` contiennent des ressources d’assistance et de design déjà présentes : elles sont conservées.

## Règles de rangement

1. Un guide courant va dans `docs/` ; un ancien bilan va dans `docs/archives/` avec sa date.
2. Une mesure datée utile va dans `docs/audits/` ; un rapport généré reste dans `.artifacts/`.
3. Les bases, secrets et sauvegardes privées ne se mettent pas dans Git.
4. Une preuve utile n’est pas supprimée pour gagner de la place. On la classe et on indique où elle se trouve.

Les sauvegardes serveur ne sont pas gérées depuis ce guide. Voir [Exploitation](EXPLOITATION.md) et [Preuves et archives](PREUVES_ET_ARCHIVES.md).

## La vision d’ensemble proposée

Le rangement documentaire est en place. Le paquet `samstag/` est créé et contient le lecteur Vidy ; les autres branches ci-dessous restent une cible progressive.

```text
Samstag/
├── README.md             ← votre point d’entrée
├── PRODUCT.md            ← ce que le produit doit proposer
├── DESIGN.md             ← son apparence
├── docs/
│   ├── SE_REPERER.md      ← ce récapitulatif
│   ├── ETAT_ACTUEL.md     ← ce qui fonctionne et les limites
│   ├── COLLECTEURS.md     ← lieux couverts, fréquence et limites
│   ├── SUIVI_IMPLEMENTATION.md ← prochaines tâches et avancement
│   ├── DEVELOPPEMENT.md   ← démarrer et vérifier en local
│   ├── EXPLOITATION.md    ← serveur, sauvegardes et livraison
│   ├── PASSATION_PROJET.md ← journal des sessions
│   ├── audits/           ← constats et mesures datés
│   └── archives/         ← anciens bilans et diagnostics
├── samstag/              ← créé ; seul le lecteur Vidy est déplacé
│   ├── web/              ← pages et API
│   ├── collection/       ← moteur et collecteurs par source
│   ├── domain/           ← règles des événements et périodes
│   ├── storage/          ← accès à la base
│   ├── templates/        ← structure des pages
│   └── static/           ← styles, images et interactions
├── data/                 ← registres des lieux et sources
├── tests/                ← vérifications Python
├── e2e/                  ← vérifications navigateur
├── deploy/               ← installation sur le serveur
└── .artifacts/           ← résultats temporaires, ignorés par Git
```

Les trois étapes conseillées : rendre la documentation lisible, nettoyer seulement ce qui est confirmé inutile, puis réorganiser progressivement le code avec des tests à chaque déplacement. Les deux premières sont le périmètre de cette session ; la troisième reste un chantier distinct.

Le [plan d’action de réorganisation du code](PLAN_REORGANISATION_CODE.md) détaille le troisième point : étapes R0 à R7, fichiers à déplacer, tests et livraison séparée. Le pilote Vidy est déplacé ; les autres étapes restent à réaliser.
