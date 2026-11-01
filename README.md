# Samstag

Samstag est un agenda public des sorties à Lausanne et dans les communes immédiatement voisines. Le site de référence est [samstagloz.ch](https://samstagloz.ch), servi par l’application Flask/Python hébergée sur un VPS Infomaniak.

## Où aller ?

| Vous voulez… | Ouvrez… |
|---|---|
| Comprendre où en est Samstag | [État actuel](docs/ETAT_ACTUEL.md) |
| Voir les lieux collectés, la fréquence et les limites | [Collecteurs](docs/COLLECTEURS.md) |
| Vous repérer dans les dossiers | [Guide du dossier](docs/SE_REPERER.md) |
| Voir les prochaines tâches | [Suivi](docs/SUIVI_IMPLEMENTATION.md) |
| Démarrer le site sur votre ordinateur | [Développement local](docs/DEVELOPPEMENT.md) |
| Comprendre le serveur et les sauvegardes | [Exploitation](docs/EXPLOITATION.md) |
| Retrouver une ancienne décision | [Passation](docs/PASSATION_PROJET.md), puis [archives](docs/archives/README.md) |

## État du projet

La référence opérationnelle et les limites connues sont consignées dans [docs/ETAT_ACTUEL.md](docs/ETAT_ACTUEL.md). Le plan de travail se trouve dans [docs/PLAN_IMPLEMENTATION.md](docs/PLAN_IMPLEMENTATION.md) et son avancement dans [docs/SUIVI_IMPLEMENTATION.md](docs/SUIVI_IMPLEMENTATION.md).

Au 1er novembre 2026, l’instantané public contrôlé contient 322 événements répartis sur 19 lieux. Le registre comprend 39 sources, dont 37 actives et 24 autorisées à publier sous conditions. Ces nombres décrivent un instantané, pas une garantie de couverture ni de fonctionnement futur.

## Architecture actuelle

| Couche | Éléments principaux |
|---|---|
| Web | Flask, `app.py`, `templates/`, `static/` |
| Collecte | `scraper.py`, modules `*_adapters.py`, `collection_worker.py`, `collection_cli.py` |
| Données | SQLite via `db.py`; registres dans `data/` |
| Exploitation | VPS Infomaniak, Gunicorn, Nginx, unités systemd documentées dans `deploy/infomaniak/` |

Le flux général est : sources officielles → lecteurs → observations et décisions qualité → SQLite → API Flask → interface mobile. Une source inventoriée n’est pas nécessairement lisible ni autorisée à publier.

## Fonctions principales

- agenda par périodes et catégories, recherche et fiches détaillées ;
- préférences locales de thèmes et de lieux ;
- partage et retours utilisateurs ;
- collecte avec conservation des preuves et diagnostic par source ;
- API de consultation et de santé.

## Développement local

Python 3.12 est la version de référence. Depuis un checkout neuf :

```sh
make setup
make check
make dev
```

Les commandes disponibles sont `setup`, `dev`, `test`, `e2e`, `check` et `report`. Elles utilisent une base absolue sous `.local/`, désactivent la collecte sur visite et gardent les données fictives désactivées. La procédure, le verrouillage et la CI sont décrits dans [docs/DEVELOPPEMENT.md](docs/DEVELOPPEMENT.md).

Ne jamais utiliser une copie de la base de production comme base de développement. Les collecteurs réels ne sont pas lancés par ces commandes.

## Périmètre éditorial

Samstag couvre bars, clubs, concerts, spectacles et cinéma, sur plusieurs semaines. Les événements diurnes sont pris en charge dans le code local ; leur livraison au site public reste à faire. Instagram est reporté. Buzz Club, Satellite et les bibliothèques sont exclus. Une annonce de location de salle ne constitue pas un événement public. Aucune date, heure, adresse ou sortie ne doit être inventée.

## Documentation

L’[index documentaire](docs/README.md) distingue les références actives des archives. La [passation](docs/PASSATION_PROJET.md) sert de journal chronologique. Les procédures d’exploitation sont dans [docs/EXPLOITATION.md](docs/EXPLOITATION.md).

## Licence

MIT.
