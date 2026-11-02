# État actuel de Samstag

**Référence réécrite le 1er novembre 2026.** Ce document est le point d’entrée pour reprendre le projet. La passation conserve l’historique détaillé ; ce fichier décrit uniquement l’état courant vérifié ou explicitement limité.

## Références

| Élément | Valeur |
|---|---|
| Site public | [samstagloz.ch](https://samstagloz.ch) |
| Production de référence | application Flask sur VPS Infomaniak |
| Dépôt | `https://github.com/VinniMo/samstag.git` |
| Branche locale auditée | `chore/samstag-full-rename-20261101` |
| HEAD local au contrôle | `dd49073` |
| Commit déployé documenté | `ed42492` ; non revérifié par SSH dans cette session |
| Autre application | `VinniMo/lausanne-events` / Vercel, hors production Samstag |

## Instantané public contrôlé

Le 1er novembre 2026, les API publiques ont renvoyé 322 événements, 19 lieux représentés et 2 675 éléments de collecte. La configuration comprend 39 sources, dont 37 actives et 24 autorisées à publier sous conditions.

La santé déclarée était dégradée : 23 sources `ok`, 5 `partial`, 5 `needs_adapter`, 3 `empty` et 1 `error` pour le MAD. Ces états sont provisoires : l’inventaire ne prouve pas le bon fonctionnement d’un lecteur et les drapeaux v3 demandent encore validation.

Les mesures détaillées sont dans [audits/AUDIT_2026-11-01.md](audits/AUDIT_2026-11-01.md) et [audits/2026-11-01-mesures.json](audits/2026-11-01-mesures.json).

## Architecture active

L’application est un monolithe Flask/Python avec interface HTML/CSS/JavaScript et persistance SQLite. Les lecteurs de sources alimentent des observations, une décision qualité et des éléments publiables. Gunicorn sert l’application derrière Nginx ; la collecte planifiée est documentée avec systemd.

Les responsabilités sont encore concentrées dans quelques gros modules. Leur séparation progressive est prévue au lot L5, après stabilisation de l’environnement, des diagnostics et des données.

## Fonctions présentes

- navigation par périodes, catégories et recherche ;
- fiches détaillées et liens vers les preuves officielles ;
- préférences locales de thèmes et lieux ;
- partage et collecte de retours ;
- diagnostics de santé et de sources ;
- conservation des observations de collecte.

## Périmètre et règles actives

Bars, clubs, concerts, spectacles et cinéma ; Lausanne et communes immédiatement voisines ; plusieurs semaines de programme. Décision du 1er novembre : inclure les événements diurnes dans les catégories déjà admises (tâche `L6.1` : code local adapté et testé ; livraison et mesure réelle de couverture à faire). Instagram est reporté. Buzz Club, Satellite et les bibliothèques sont exclus. Une annonce de location de salle sans événement public est rejetée. Aucune information manquante ne doit être inventée.

## Validation disponible

- 107 tests Python réussis sous Python 3.12 avec les dépendances verrouillées ;
- 85 parcours E2E réussis sur cinq profils avec la base isolée et syntaxe JavaScript contrôlée ;
- trois registres JSON validés par schéma, unicité et références croisées ;
- CSS et JavaScript publics identiques aux fichiers locaux par empreinte ;
- réponses publiques et comptages archivés dans l’audit.

Python 3.12 est la référence reproductible. Les commandes `make setup`, `dev`, `test`, `e2e`, `check` et `report` utilisent un environnement local protégé. Le workflow GitHub a été ajouté mais n’a pas encore été exécuté à distance. Aucune vérification SSH, restauration de sauvegarde, observation sur 24 heures ni audit mobile complet n’a été réalisée pendant cette session.

## Défauts confirmés ou à reproduire

- certaines erreurs de détail Docks/Romandie peuvent être enregistrées comme `empty` au lieu d’un échec partiel ;
- un doublon visible « Mike D » / « Mike D 5D » demande une règle conservatrice et un test ;
- le MAD était en erreur dans l’instantané public ;
- la sauvegarde hors VPS et la restauration ne sont pas encore prouvées.

## Prochaine étape

Les lots L0 et L1 sont terminés. La prochaine session bornée est `L2.1` et `L2.2` : corriger le contrat de résultat Docks/Romandie et couvrir les échecs complets ou partiels par des tests. Aucun autre collecteur ne doit être relancé dans cette session.

Le détail et les critères de fin se trouvent dans [PLAN_IMPLEMENTATION.md](PLAN_IMPLEMENTATION.md). Le statut court se trouve dans [SUIVI_IMPLEMENTATION.md](SUIVI_IMPLEMENTATION.md).

## Réorganisation locale — 2 novembre 2026

R0 et R1 sont terminés : le lecteur Vidy est dans `samstag/collection/adapters/vidy.py`, avec anciens imports compatibles. Les autres modules restent à la racine. 109 tests passent et les scénarios Vidy donnent des résultats identiques avant/après. Suite : R2, CityClub. Aucun changement serveur ; les prérequis L2–L4 ne sont pas déclarés achevés. Voir le [bilan](audits/REORGANISATION_R0_R1_2026-11-02.md).
