# Réconciliation Samstag — 1er novembre 2026

## Décision

**Samstag** est l'unique nom du produit, du dépôt, du code et de
l'exploitation. Le dossier `/Users/lauresenechal/Documents/ChatGPT/Samstag`
est la seule base locale active.

## Références

- Dépôt : `https://github.com/VinniMo/samstag`.
- Branche : `chore/samstag-full-rename-20261101`.
- Commit déployé : `ed42492`.
- Pull request : `https://github.com/VinniMo/samstag/pull/7`.
- Service VPS : `samstag.service`.
- Code VPS : `/opt/samstag/app`.
- Base VPS : `/var/lib/samstag/samstag.sqlite3`.
- Configuration VPS : `/etc/samstag/samstag.env`.

## Vérifications réalisées

- Compilation Python locale et sur le VPS : réussie.
- Tests Python locaux et sur le VPS : **102 réussis**.
- Tests Playwright sur Chromium, Firefox, WebKit et vues mobiles :
  **85 réussis**.
- Base SQLite après migration : intégrité `ok`.
- Accueil VPS : HTTP 200.
- API de santé : statut `ok` ; collecte encore `degraded`.
- Services `samstag.service`, `samstag-backup.timer` et
  `cockpit-immobilier.service` : actifs.
- Démarrage automatique du service et de la sauvegarde : activé.

## Sauvegarde et retour arrière

La migration a créé une base cohérente et une archive du code et de la
configuration dans `/var/backups/samstag-migration-20261101T101511Z/`.
La copie applicative de retour arrière est conservée sur le VPS jusqu'à une
décision explicite de suppression.

## Publication

Le dépôt GitHub a été renommé et la branche a été publiée. La pull request reste
ouverte afin que la fusion sur `main` soit décidée après revue. Le commit testé
est déjà installé sur Infomaniak.
