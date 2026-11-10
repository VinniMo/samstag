# Suivi d’implémentation Samstag

Ce fichier est le tableau de bord humain du [plan d’implémentation](PLAN_IMPLEMENTATION.md). Il doit rester court. Les détails techniques appartiennent aux PR, audits et documents de validation.

## État global

| Lot | Responsable | État | Prochaine action | Dernière preuve |
|---|---|---|---|---|
| L0 — Documentation | Codex | Terminé | Maintenir l’état actuel à chaque lot | Contrôle documentaire du 1er novembre 2026 |
| L1 — Développement et CI | Codex | Terminé | Maintenir les verrous et la CI | `make check` et 85 E2E réussis le 1er novembre 2026 |
| L2 — Diagnostics collecte | Codex | Terminé | Maintenir le tableau lors des évolutions de lecteurs | 114 tests et contrôle MAD ciblé du 2 novembre 2026 |
| L3 — Qualité et doublons | Codex | Terminé | Maintenir les règles et preuves lors des évolutions | Taco's contrôlé à la source et 119 tests le 2 novembre 2026 |
| L4 — Exploitation | Codex | En cours | Préparer séparément la livraison VPS de la correction fusionnée ; autorisation requise | PR no 14 fusionnée au commit `3708ba5` le 9 novembre 2026 |
| L5 — Architecture interne | Codex | R2 en cours localement | R2 : Docks/Romandie/D! | JazzOnze+ extrait, 145 tests le 10 novembre 2026 |
| L6 — Produit et performance | À attribuer | À faire | Livrer et mesurer la couverture diurne (`L6.1`) | Décision utilisateur du 1er novembre 2026 |

## En cours

- Le sous-lot applicatif est stable et les trois fausses alertes sont corrigées localement. La copie externe et l'activation des alertes restent séparées.

## Prêt à démarrer

- [ ] Poursuivre R2 avec Docks/Romandie/D!, sans réparation fonctionnelle ni appel réel.

## Bloqué ou soumis à décision

- [ ] Toute modification du VPS reste soumise à une nouvelle autorisation explicite.
- Décision `L6.1` actée : inclure les événements diurnes ; code local implémenté, livraison et mesure réelle à faire.

## Terminé

- [x] `L0.1` Audit complet du site, de l’architecture, des collecteurs et du dossier local.
- [x] `L0.2` Plan d’implémentation, tableau de suivi et diagrammes Mermaid.
- [x] `L0.3` État courant unique créé.
- [x] `L0.4` Documents actifs révisés.
- [x] `L0.5` Documents anciens classés comme historiques.
- [x] `L0.6` Preuves présentes et absentes indexées.
- [x] `L1.1` à `L1.7` Environnement Python 3.12, commandes, verrous, E2E portable, CI et schémas JSON.
- [x] `L2.0` à `L2.7` Tableau de santé des 39 canaux, compteurs par passe, incidents séparés des limites et MAD sécurisé.
- [x] `L3.0` Plan détaillé, règles de sécurité et diagramme de décision préparés.
- [x] `L3.1`, `L3.2` et `L3.6` Fixture Mike D, détection par lieu/date/heure et rapport en lecture seule.
- [x] `L3.3` à `L3.5` Priorité officielle, cas ambigus séparés, preuves conservées et retour arrière.
- [x] `L3.7` Horaire 20:26 de Taco's confirmé dans la source officielle et conservé sans correction.
- [x] `L4.0` Plan d'exploitation, preuves attendues et points d'autorisation préparés sans accès VPS.
- [x] `L4.3` Route de collecte manuelle désactivée par défaut, limitée à POST et protégée par un secret dédié.
- [x] `L4.5`, `L4.6` et `L4.9` Restauration locale isolée, objectifs de reprise et journal de livraison préparés.
- [x] `L4.8` Politique d'accès et de conservation des retours définie ; migration de purge reportée.

## Journal

| Date | Changement | Vérifications | Limites |
|---|---|---|---|
| 2026-11-01 | Audit et planification initiale | 102 tests Python ; syntaxe JS ; lecture des API publiques | Pas de SSH, nouvelle campagne E2E, mobile complet ni restauration |
| 2026-11-01 | Lot L0 finalisé : état courant, index, exploitation et archives | Liens relatifs, statuts, JSON, cohérence documentaire et diff contrôlés | Aucun code ni service distant modifié |
| 2026-11-01 | Lot L1 finalisé : développement reproductible et CI | Installation neuve ; suite finale de 107 tests Python ; 85 E2E sur cinq profils ; schémas JSON ; syntaxe JS ; démarrage local | Workflow GitHub ajouté mais pas encore exécuté à distance |
| 2026-11-02 | Lot L2 finalisé : santé globale des collecteurs | 114 tests ; matrice synthétique des 37 actifs ; 39 canaux visibles ; deux contrôles ciblés MAD | Aucun autre site relancé, aucun déploiement |
| 2026-11-02 | Préparation L3 : séquence détection, décision et vérification | Lecture du dédoublonnage actuel et du cas Mike D ; plan et diagramme | Aucun code métier, aucune donnée et aucun site modifiés |
| 2026-11-02 | Première étape L3 : détection sans fusion | Mike D détecté ; base isolée inchangée ; 116 tests réussis | Le rapport signale des candidats mais ne décide encore aucun rapprochement |
| 2026-11-02 | Deuxième étape L3 : décisions conservatrices | Mike D réduit à une fiche officielle sur base isolée ; preuves et fiches d'origine conservées ; 118 tests | Aucun rapprochement appliqué aux données réelles ; Taco's reste à contrôler séparément |
| 2026-11-02 | Troisième étape et clôture L3 : contrôle Taco's | Trois occurrences à 20:26 confirmées dans la source officielle ; base isolée ; 119 tests | Aucun autre site contrôlé, aucune donnée réelle ni production modifiée |
| 2026-11-02 | Préparation L4 : reprise et exploitation | Risques, six étapes, preuves et autorisations séparées documentés | Aucun accès VPS, restauration réelle, alerte ou déploiement |
| 2026-11-02 | Étape A L4 : sécurité locale | Route manuelle refusée par défaut ; 122 tests réussis sans réseau réel | Code non livré sur le VPS ; session et cookie distants non contrôlés |
| 2026-11-02 | Étape B L4 : reprise locale | Sauvegarde/restauration fictives, intégrité, comptages, lecture et refus d'écrasement ; 125 tests | Aucune sauvegarde de production ni durée distante mesurée |
| 2026-11-02 | Étape C L4 : surveillance locale | Seuils de sources/sauvegardes, copie chiffrée et rétention des retours définis ; 129 tests | Aucun message envoyé, fournisseur ou compte privé configuré |
| 2026-11-02 | Contrôle final local L4 A–C | 129 tests, registres, syntaxe, secrets et différences contrôlés | Aucun accès VPS, transfert, alerte réelle ou déploiement |
| 2026-11-02 | Étape D L4 : constat VPS en lecture seule | Service et HTTPS sains ; session/cookie confirmés ; sauvegarde quotidienne intègre ; version `ed42492` identifiée par empreintes | Flask ancien derrière Nginx ; 24 sources automatiques ; pas de copie externe, restauration distante ni alerte reçue |
| 2026-11-02 | Préparation locale de l'étape E | Paquet complet issu de Git, 43 empreintes internes, simulation isolée et 131 tests réussis ; retour arrière documenté | Aucune livraison ; copie externe et destinataires d'alerte non configurés |
| 2026-11-02 | Livraison applicative de l'étape E | Sauvegarde restaurée, version `b593dc6`, 37/37 sources, 414 sorties, route protégée et dix minutes sans redémarrage | MAD en échec mais non automatique ; trois fausses alertes partielles à corriger ; aucune copie externe |
| 2026-11-02 | Correction locale des alertes partielles | Vidy, Lausanne Tourisme et Château ne sont plus « jamais réussis » après accès/analyse corrects ; erreurs réelles conservées ; 134 tests | Aucun VPS, message ou activation ; livraison et alerte reçue restent à faire |
| 2026-11-09 | Revue locale de la correction des alertes partielles | Diff contrôlé ; 7 tests ciblés et `make check` avec 134 tests, registres et JavaScript valides | Branche non publiée ; aucun VPS, message ou mécanisme d'alerte activé |
| 2026-11-09 | L5/R2 CityClub : lecteur extrait dans le paquet | Import historique identique ; champs et erreurs sur fixtures ; `make check` avec 136 tests | Aucun site réel, VPS, base ou comportement fonctionnel modifié |
| 2026-11-10 | L5/R2 Naftule–Boulimie : deux lecteurs et aides minimales extraits | Imports identiques ; six scénarios ciblés ; `make check` avec 139 tests | Aucun site réel, VPS, base ou comportement fonctionnel modifié |
| 2026-11-10 | L5/R2 Arsenic : lecteur JavaScript public extrait | Import identique ; trois scénarios ciblés ; `make check` avec 142 tests | Aucun site réel, VPS, base ou comportement fonctionnel modifié |
| 2026-11-10 | L5/R2 Grange–Pulloff : deux lecteurs extraits | Imports identiques ; sept scénarios ciblés ; `make check` avec 143 tests | Aucun site réel, VPS, base ou comportement fonctionnel modifié |
| 2026-11-10 | L5/R2 Folklor–MAD : deux parseurs extraits | Imports identiques ; quatre scénarios ciblés ; `make check` avec 144 tests | Orchestration MAD et production inchangées ; aucun appel réel |
| 2026-11-10 | L5/R2 JazzOnze+ : parseur et enrichissement extraits | Imports identiques ; cinq scénarios ciblés ; `make check` avec 145 tests | Aucun appel réel, VPS, base ou comportement modifié |

## Modèle d’entrée de journal

Copier une ligne et remplir uniquement des faits vérifiés :

```text
| AAAA-MM-JJ | Tâches Lx.y ; résultat concret | Tests, mesures et preuves | Ce qui reste non vérifié |
```


- 1er novembre 2026 : événements diurnes ajoutés au périmètre et à L6.1 ; documentation seulement, aucun changement de collecte ou de production.

- 1er novembre 2026 : L6.1 implémenté localement ; 107 tests Python réussis, registres et syntaxe JS valides. Livraison et couverture réelle restent à faire.
- Validation finale du lot diurne : 17/17 E2E Chromium réussis sur fixture isolée ; rapport `/private/tmp/samstag-diurne-e2e/report/index.html`.

- 1er novembre 2026 : rangement documentaire et nettoyage local terminés ; guide SE_REPERER et fiche COLLECTEURS ajoutés, dix archives regroupées, caches régénérables supprimés. Aucun code applicatif déplacé.

- 1er novembre 2026 : plan détaillé L5 enregistré dans `PLAN_REORGANISATION_CODE.md` (R0–R7). Planification seulement ; prochaine action R0, prérequis L2–L4 conservés.

- 2 novembre 2026 : R0 et R1 terminés localement (référence propre `3f57d9b`, Vidy extrait, réexports conservés, 109 tests et comparaison avant/après identique). R2–R7 restent à faire ; aucun déploiement.
