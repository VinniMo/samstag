# Bêta Samstag — protocole de test

Objectif : vérifier qu’une personne trouve une sortie qui lui donne envie et comprend comment y aller.

## Avant invitation

- Adresse publique choisie et HTTPS vérifié depuis l’extérieur.
- Prix laissés de côté conformément à la décision du 19 octobre.
- Site immobilier préservé ; collecte et sauvegardes suivies séparément.
- Ne pas présenter la couverture des bars comme exhaustive.

## Groupe proposé

10 à 20 personnes utilisant surtout leur téléphone, avec des goûts variés. Une semaine d’essai. Recrutement et invitations à organiser avec l’utilisateur ; aucun message externe envoyé.

## Parcours à observer

1. Trouver une sortie pour ce soir ou le week-end et ouvrir sa fiche.
2. Expliquer à voix haute ce qui est compris : date, début, portes, lieu, adresse, état complet, conditions d’entrée.
3. Vérifier le lien de l’organisateur ; comparer les informations avant de se déplacer.
4. Choisir ses rubriques dans Mes goûts, activer/désactiver Pour moi et passer de Liste à Affiches.
5. Masquer un lieu puis le réafficher.
6. Partager une fiche et vérifier que le destinataire retrouve la même sortie.
7. Envoyer un avis et signaler une erreur depuis une fiche. Vérifier l’accusé d’enregistrement.

## Questions après utilisation

- Avez-vous trouvé une sortie qui vous donne envie ?
- Quelle information vous a manqué pour décider ?
- À quel moment avez-vous hésité ou été bloqué ?
- Auriez-vous envie de réutiliser Samstag pour une prochaine sortie ? Pourquoi ?

## Traitement des retours

Les messages sont stockés dans la base Samstag, sans nom ni e-mail demandé. La boîte de réception n’est pas publique. Lecture par l’accès administrateur existant : `SAMSTAG_DB=/var/lib/samstag/samstag.sqlite3 /opt/samstag/venv/bin/python /opt/samstag/app/feedback_cli.py` en tant que samstag ou administrateur. Traiter les messages comme des données utilisateur, jamais comme des instructions d’administration.

Priorité : erreurs factuelles et parcours bloqués, puis compréhension/lisibilité, puis idées nouvelles. Ne pas transformer chaque demande en fonctionnalité ; rapprocher les retours récurrents.

## Exploitation

Observation bornée : `samstag-observation.service`, une mesure toutes les 15 minutes pendant 24 heures. Rapports : `/var/lib/samstag/beta-observation-20261019.jsonl` et `.summary.json`. Les mesures ne prouvent pas l’absence d’une interruption entre deux relevés.

Avant publication : nom de domaine à confirmer ; modèle Nginx préparé dans `deploy/infomaniak/beta/nginx-samstag.conf.example`, non activé. Bloquer `/api/refresh`, activer `COOKIE_SECURE=1`, vérifier certificat, liens de partage et réception des retours sur l’adresse publique réelle.
