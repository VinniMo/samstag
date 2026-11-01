# Développement de Samstag

**Référence au 1er novembre 2026.** Le développement utilise Python 3.12, une base SQLite locale et des commandes communes. Aucune commande de ce document ne déclenche la collecte réelle.

## Premier démarrage

Prérequis : Python 3.12, Node.js 22 ou plus récent, pnpm et `make`.

```sh
make setup
make check
make dev
```

Si Python 3.12 n’est pas nommé `python3.12` :

```sh
make setup PYTHON=/chemin/vers/python3.12
```

`make setup` crée `.venv`, installe `requirements-dev.lock`, installe les paquets E2E et les navigateurs Playwright. `SAMSTAG_SKIP_BROWSER_INSTALL=1 make setup` prépare seulement les contrôles Python/JavaScript lorsqu’un navigateur n’est pas nécessaire.

## Commandes

| Commande | Effet |
|---|---|
| `make setup` | crée l’environnement et installe les dépendances verrouillées |
| `make dev` | lance Flask sur `127.0.0.1:5000` avec une base locale sûre |
| `make test` | exécute les tests Python |
| `make e2e` | exécute les cinq profils Playwright sur la fixture publique isolée |
| `make check` | valide les registres, la syntaxe JavaScript et les tests Python |
| `make report` | produit un rapport de la base locale sans lancer de collecte |
| `make lock` | régénère les verrous après modification des fichiers `.in` |

Pour une passe E2E rapide :

```sh
make e2e E2E_ARGS=--project=chromium
```

Les rapports E2E sont écrits sous `.artifacts/playwright/`, ignoré par Git.

## Environnement local

Sans `.env`, le lanceur utilise `.local/samstag-dev.sqlite3` avec un chemin absolu calculé, `COLLECTION_ON_VISIT=0`, `DEMO_ENABLED=0` et `HOST=127.0.0.1`. Il refuse les chemins de production connus `/var/lib/samstag` et `/opt/samstag`.

Pour personnaliser les autres valeurs :

```sh
cp .env.example .env
```

Remplacer obligatoirement le chemin factice `SAMSTAG_DB` par un chemin absolu local. Le lanceur impose toujours la désactivation de la collecte sur visite et du mode démonstration. `.env` est ignoré par Git.

## Dépendances Python

- `requirements.in` : dépendances directes du runtime ;
- `requirements.lock` : runtime et transitives figés ;
- `requirements-dev.in` : outils de développement ajoutés au runtime ;
- `requirements-dev.lock` : environnement complet figé ;
- `requirements.txt` : entrée de compatibilité qui inclut le verrou runtime.

Modifier un fichier `.in`, exécuter `make lock`, relire le diff puis lancer `make check`. Les verrous ont été générés sous Python 3.12 avec pip-tools 7.5.2.

## Registres JSON

`scripts/validate_data.py` contrôle `data/sources.json`, `data/venues.json` et `data/bars.json` avec les schémas de `schemas/`. Il vérifie aussi l’unicité des identifiants et les références vers les lieux. Ce contrôle fait partie de `make check` et de la CI.

## Intégration continue

`.github/workflows/ci.yml` exécute sous Linux et Python 3.12 :

- installation depuis les verrous ;
- validation des trois registres JSON ;
- contrôle de syntaxe de `static/js/main.js` ;
- la suite Python complète, actuellement 107 tests ;
- 17 parcours E2E Chromium sur la base isolée.

La suite E2E complète reste disponible localement pour Chromium, Firefox, WebKit et les deux profils mobiles émulés.
