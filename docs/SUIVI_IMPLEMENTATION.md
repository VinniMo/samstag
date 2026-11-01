# Suivi d’implémentation Samstag

Ce fichier est le tableau de bord humain du [plan d’implémentation](PLAN_IMPLEMENTATION.md). Il doit rester court. Les détails techniques appartiennent aux PR, audits et documents de validation.

## État global

| Lot | Responsable | État | Prochaine action | Dernière preuve |
|---|---|---|---|---|
| L0 — Documentation | Codex | Terminé | Maintenir l’état actuel à chaque lot | Contrôle documentaire du 1er novembre 2026 |
| L1 — Développement et CI | Codex | Terminé | Maintenir les verrous et la CI | `make check` et 85 E2E réussis le 1er novembre 2026 |
| L2 — Diagnostics collecte | À attribuer | À faire | Corriger le statut partiel Docks/Romandie | Reproduction isolée du statut `empty` erroné |
| L3 — Qualité et doublons | À attribuer | À faire | Transformer Mike D en test de régression | Doublon public observé le 1er novembre 2026 |
| L4 — Exploitation | À attribuer | À faire | Préparer le contrôle VPS et la restauration | Procédures versionnées, état distant non audité par SSH |
| L5 — Architecture interne | À attribuer | À faire | Attendre la stabilisation L1 à L4 | Architecture cible documentée |
| L6 — Produit et performance | À attribuer | À faire | Livrer et mesurer la couverture diurne (`L6.1`) | Décision utilisateur du 1er novembre 2026 |

## En cours

- Aucun lot en cours. Prochaine session bornée : `L2.1` et `L2.2`.

## Prêt à démarrer

- [ ] `L2.1` Remplacer les retours tuple résiduels Docks/Romandie par `CollectionResult`.
- [ ] `L2.2` Ajouter les tests des échecs complets et partiels de fiches.

## Bloqué ou soumis à décision

- [ ] `L4.1` à `L4.9` — les vérifications et changements sur le VPS restent soumis à l’autorisation applicable.
- Décision `L6.1` actée : inclure les événements diurnes ; code local implémenté, livraison et mesure réelle à faire.

## Terminé

- [x] `L0.1` Audit complet du site, de l’architecture, des collecteurs et du dossier local.
- [x] `L0.2` Plan d’implémentation, tableau de suivi et diagrammes Mermaid.
- [x] `L0.3` État courant unique créé.
- [x] `L0.4` Documents actifs révisés.
- [x] `L0.5` Documents anciens classés comme historiques.
- [x] `L0.6` Preuves présentes et absentes indexées.
- [x] `L1.1` à `L1.7` Environnement Python 3.12, commandes, verrous, E2E portable, CI et schémas JSON.

## Journal

| Date | Changement | Vérifications | Limites |
|---|---|---|---|
| 2026-11-01 | Audit et planification initiale | 102 tests Python ; syntaxe JS ; lecture des API publiques | Pas de SSH, nouvelle campagne E2E, mobile complet ni restauration |
| 2026-11-01 | Lot L0 finalisé : état courant, index, exploitation et archives | Liens relatifs, statuts, JSON, cohérence documentaire et diff contrôlés | Aucun code ni service distant modifié |
| 2026-11-01 | Lot L1 finalisé : développement reproductible et CI | Installation neuve ; suite finale de 107 tests Python ; 85 E2E sur cinq profils ; schémas JSON ; syntaxe JS ; démarrage local | Workflow GitHub ajouté mais pas encore exécuté à distance |

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
