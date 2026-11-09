# État actuel de Samstag

**Référence mise à jour le 9 novembre 2026.** Ce document est le point d’entrée pour reprendre le projet. La passation conserve l’historique détaillé ; ce fichier décrit uniquement l’état courant vérifié ou explicitement limité.

## Références

| Élément | Valeur |
|---|---|
| Site public | [samstagloz.ch](https://samstagloz.ch) |
| Production de référence | application Flask sur VPS Infomaniak |
| Dépôt | `https://github.com/VinniMo/samstag.git` |
| Branche locale auditée | `codex/l4-vps-readonly-audit` |
| HEAD de départ | `5722569`, fusion de la PR L4 A–C |
| Commit déployé vérifié | `b593dc6`, livré et contrôlé le 2 novembre |
| Autre application | `VinniMo/lausanne-events` / Vercel, hors production Samstag |

## Instantané public contrôlé

Le 1er novembre 2026, les API publiques ont renvoyé 322 événements, 19 lieux représentés et 2 675 éléments de collecte. La configuration publique comprenait 39 sources, dont 37 actives et 24 autorisées à publier sous conditions. Le code local en autorise désormais 23 après la désactivation automatique du MAD.

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

Python 3.12 est la référence reproductible. Les commandes `make setup`, `dev`, `test`, `e2e`, `check` et `report` utilisent un environnement local protégé. Le workflow GitHub est actif. Le 2 novembre, le service, HTTPS, la session, le cookie sécurisé, la sauvegarde quotidienne et une restauration distante isolée ont été contrôlés. Aucune observation sur 24 heures ni audit mobile complet n'a été réalisé.

## Points restant à traiter

- le MAD reste suivi mais sa publication automatique locale est désactivée tant que ses fiches liées sont illisibles ;
- la sauvegarde locale et la restauration isolée sont prouvées, mais la copie hors VPS ne l'est pas encore ;
- le calcul des trois fausses alertes est corrigé et revu localement ; aucun envoi n'est activé et cette correction n'est pas encore publiée ni livrée.

## Prochaine étape

Les lots L0 à L3 sont terminés localement. L3 rapproche le cas Mike D vers la fiche officielle sur une base isolée, conserve toutes les preuves et laisse les cas ambigus séparés. Le contrôle ciblé de Taco's confirme que l'horaire 20:26 est explicitement publié par la source officielle ; aucune correction n'est nécessaire.

L4 a livré son sous-lot applicatif le 2 novembre après sauvegarde et restauration isolée. La production exécute `b593dc6` : Nginx et Flask protègent la route administrative, 39 canaux sont visibles, 37 actifs et 23 automatiques. Le premier cycle complet a publié 414 sorties et la version est restée stable sans redémarrage pendant dix minutes. L'ancien dossier `ed42492` reste disponible pour retour arrière. Le calcul des trois fausses alertes découvertes après livraison est corrigé et revu localement : 7 tests ciblés et les 134 tests du projet réussissent le 9 novembre, sans activation ni envoi. La publication de la branche, la copie externe, la livraison de cette correction et la réception d'une alerte de test restent à réaliser. Voir le [rapport de livraison](audits/L4_LIVRAISON_VPS_2026-11-02.md) et le [plan L4](PLAN_L4_EXPLOITATION.md).

Le détail et les critères de fin se trouvent dans [PLAN_IMPLEMENTATION.md](PLAN_IMPLEMENTATION.md). Le statut court se trouve dans [SUIVI_IMPLEMENTATION.md](SUIVI_IMPLEMENTATION.md).

## Réorganisation locale — 2 novembre 2026

R0 et R1 sont terminés : le lecteur Vidy est dans `samstag/collection/adapters/vidy.py`, avec anciens imports compatibles. Les autres modules restent à la racine. 109 tests passent et les scénarios Vidy donnent des résultats identiques avant/après. Suite : R2, CityClub. Aucun changement serveur ; les prérequis L2–L4 ne sont pas déclarés achevés. Voir le [bilan](audits/REORGANISATION_R0_R1_2026-11-02.md).
