# Samstag

Samstag est l'agenda des sorties à Lausanne. Cette branche réconcilie le dépôt
historique avec la version Flask réellement installée sur le VPS Infomaniak.
La marque publique est **Samstag** ; les noms `Samstag` conservés dans certains
services, chemins et variables restent provisoirement des identifiants techniques.

État de référence au 1er novembre 2026 : application active sur Infomaniak,
interface Samstag vérifiée et accès de travail par tunnel sur
`http://127.0.0.1:8011/`. Voir [la procédure Infomaniak](deploy/infomaniak/README.md),
[la passation](docs/PASSATION_PROJET.md) et [l'exploitation](docs/EXPLOITATION.md).

> Les sorties à Lausanne, réunies dans un agenda pratique pensé d'abord pour mobile.

Concerts, soirées, scène, cinéma et expositions : le programme des lieux et
agendas lausannois dans une interface rapide à parcourir.

## Stack

| Couche       | Choix                                                                    |
|--------------|--------------------------------------------------------------------------|
| Backend      | Flask 3 · application factory · SQLite (persistance)                     |
| Scraping     | `requests` + `BeautifulSoup` (JSON-LD prioritaire, fallback HTML)        |
| Frontend     | HTML5 sémantique · CSS mobile-first · Vanilla JS                         |
| Typographie  | Archivo, auto-hébergée                                                     |

## Architecture

```
.
├── app.py          # Flask factory + routes
├── config.py       # Config immuable (env vars)
├── db.py           # Couche SQLite (init, upsert, queries)
├── scraper.py      # Scraping JSON-LD + fallback HTML
├── seed_data.py    # Dataset de fallback (25 événements)
├── templates/
│   └── index.html
├── static/
│   ├── css/style.css
│   └── js/main.js
└── .devcontainer/
    └── devcontainer.json
```

## Endpoints

| Méthode | URL               | Rôle                                          |
|---------|-------------------|-----------------------------------------------|
| GET     | `/`               | Application                                   |
| GET     | `/api/events`     | Liste filtrable (`?category=…&search=…`)      |
| GET     | `/api/categories` | Catégories disponibles + comptes              |
| GET/POST| `/api/refresh`    | Force un scrape immédiat                      |
| GET     | `/api/sources`    | Diagnostic : état et nombre d'événements par source |
| GET     | `/api/health`     | Statut + nombre d'événements + dernier scrape |

## Lancer en local

```bash
pip install -r requirements.txt
python app.py
# → http://localhost:5000
```

Au premier démarrage, la base locale est initialisée sans événement fictif.
Le moteur utilise l'inventaire consolidé des sorties du soir (`data/venues.json`)
et les canaux configurés dans `data/sources.json`. Les sources qualifiées publient
automatiquement les événements complets ; les autres alimentent une file de
vérification. Les preuves et observations de chaque source restent conservées.
Les événements périmés ou hors périmètre ne sont pas affichés.

Le récapitulatif lisible, les limites et les commandes locales sont dans
[docs/RECAP_COLLECTE.md](docs/RECAP_COLLECTE.md). Le diagnostic mesuré est dans
[docs/diagnostic_collecte_v2.json](docs/diagnostic_collecte_v2.json).
Le document `BARS_PILOT.md` décrit uniquement la première version historique.
Les listes historiques d'institutions dans `config.py` ne sont plus utilisées.
Le mode fictif reste disponible uniquement avec `DEMO_ENABLED=1`.

```bash
export SAMSTAG_DB="$PWD/preview.db"
python collection_cli.py collect
python collection_cli.py report
python app.py
```

La collecte se relance en arrière-plan à la consultation lorsque le TTL expire
(défaut une heure). Aucun cron externe n'est créé par ce code. Le verrou de collecte
est partagé entre les workers via SQLite. Un canal en panne n'est pas assimilé à
un lieu fermé. Le schéma SQLite s'étend sans effacer la table historique `events`.
Les données validées sont maintenant stockées dans `collection_items` et les
preuves par source dans `collection_observations`.

## Lancer dans GitHub Codespaces

1. Sur GitHub, ouvre le repo → **Code** → **Codespaces** → **Create codespace**.
2. Le devcontainer installe les dépendances et démarre Flask automatiquement.
3. Une notification *Open in Browser* apparaît pour le port 5000.

Pas besoin d'API key GitHub CLI — tout est piloté par
`.devcontainer/devcontainer.json`.

## Variables d'environnement

| Variable          | Défaut         | Description                       |
|-------------------|----------------|-----------------------------------|
| `HOST`            | `0.0.0.0`      | Adresse d'écoute Flask            |
| `PORT`            | `5000`         | Port HTTP                         |
| `FLASK_DEBUG`     | `1`            | Mode debug Flask                  |
| `SAMSTAG_DB`     | `./events.db`  | Chemin SQLite                     |
| `SCRAPE_INTERVAL` | `3600`         | TTL du cache scraping (secondes)  |
| `DEMO_ENABLED` | `0` | Mode démonstration fictive, activation explicite uniquement |
| `SCRAPE_TIMEOUT`  | `12`           | Timeout HTTP du scraper           |

## Design

- **Mobile-first** — liste horaire dense et affiches en vue secondaire.
- **Programme imprimé** — papier clair, encre noire, Archivo et étiquettes de
  catégories franches.
- **Identité Samstag** — logo noir avec dernier « a » miroir bleu outremer et
  signature « Les sorties à Lausanne ».
- **Données honnêtes** — les informations manquantes sont signalées, jamais
  inventées.

## Licence

MIT.
