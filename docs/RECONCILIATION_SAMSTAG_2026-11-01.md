# Réconciliation Samstag — 1er novembre 2026

## Décision

Le produit public s'appelle **Samstag**. La version Flask servie sur le VPS
Infomaniak constitue la référence fonctionnelle. Cette branche réconcilie cette
version avec l'historique du dépôt Git `VinniMo/lausanne-cultura`.

Les noms techniques historiques (`cultura.service`, `/opt/cultura` et les
variables `CULTURA_*`) restent en place pour préserver l'exploitation.

## Source reprise

- Source locale correspondant au déploiement : `cultura-v3/lausanne-cultura/`.
- Dépôt de destination : `cultura-code/`.
- Branche locale : `chore/samstag-reconciliation-20261101`.
- Fichiers exclus : environnements Python, bases SQLite, journaux, secrets,
  résultats de validation, captures, dépendances JavaScript et caches.

Le projet `lausanne-events`, associé à Vercel, reste une tentative distincte et
n'est pas fusionné dans Samstag.

## Vérifications réalisées

- Compilation Python : réussie.
- Tests Python : **102 réussis**.
- Parcours Playwright sur Chromium ordinateur et mobile : **34 réussis**.
- Contrôle Git des espaces et marqueurs de conflit : réussi.

Les tests navigateur ont permis de corriger un cas où une fiche sans
description ni lien source affichait à tort qu'une description était disponible
sur le site de l'événement.

## État de publication

Cette réconciliation est locale. Elle n'a déclenché ni envoi vers GitHub, ni
renommage du dépôt, ni déploiement sur Infomaniak. La publication devra passer
par une revue de cette branche, puis un envoi contrôlé sur GitHub. Le renommage
du dépôt en `VinniMo/samstag` pourra suivre après validation.
