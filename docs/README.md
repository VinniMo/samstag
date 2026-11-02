# Index documentaire Samstag

Commencer par [Se repérer](SE_REPERER.md), [État actuel](ETAT_ACTUEL.md) ou [Collecteurs](COLLECTEURS.md), selon votre besoin.

## Références actives

| Document | Usage |
|---|---|
| [SE_REPERER.md](SE_REPERER.md) | carte du dossier et règles de rangement |
| [COLLECTEURS.md](COLLECTEURS.md) | lieux couverts, fréquence, état et limites |
| [ETAT_ACTUEL.md](ETAT_ACTUEL.md) | état courant, limites et prochaine étape |
| [PLAN_IMPLEMENTATION.md](PLAN_IMPLEMENTATION.md) | lots, tâches et critères de fin |
| [PLAN_L3_QUALITE_DOUBLONS.md](PLAN_L3_QUALITE_DOUBLONS.md) | déroulement simple et contrôles du lot L3 |
| [PLAN_L4_EXPLOITATION.md](PLAN_L4_EXPLOITATION.md) | sauvegardes, restauration, alertes et autorisations du lot L4 |
| [L4_LOT_LIVRAISON.md](L4_LOT_LIVRAISON.md) | paquet applicatif prêt, contrôles et retour arrière avant autorisation VPS |
| [SUIVI_IMPLEMENTATION.md](SUIVI_IMPLEMENTATION.md) | avancement court et journal des lots |
| [EXPLOITATION.md](EXPLOITATION.md) | contrôles, livraison et retour arrière |
| [JOURNAL_LIVRAISON_MODELE.md](JOURNAL_LIVRAISON_MODELE.md) | preuve à remplir pour chaque livraison autorisée |
| [POLITIQUE_ALERTES_ET_DONNEES.md](POLITIQUE_ALERTES_ET_DONNEES.md) | seuils d'alerte, copie externe et conservation des retours |
| [DEVELOPPEMENT.md](DEVELOPPEMENT.md) | environnement local, commandes, verrous et CI |
| [PREUVES_ET_ARCHIVES.md](PREUVES_ET_ARCHIVES.md) | preuves présentes, externes ou absentes |
| [PASSATION_PROJET.md](PASSATION_PROJET.md) | journal chronologique de reprise |
| [audits/AUDIT_2026-11-01.md](audits/AUDIT_2026-11-01.md) | audit technique et public détaillé |

## Diagrammes actifs

- [implementation-roadmap.mmd](diagrams/implementation-roadmap.mmd) : dépendances et état des lots ;
- [development-workflow.mmd](diagrams/development-workflow.mmd) : cycle d’une tâche ;
- [target-architecture.mmd](diagrams/target-architecture.mmd) : architecture cible progressive.
- [l3-deduplication.mmd](diagrams/l3-deduplication.mmd) : décision prudente face à deux fiches probablement identiques.
- [l4-operations.mmd](diagrams/l4-operations.mmd) : étapes locales, autorisations et preuves d'exploitation.

## Documents historiques

Les anciens bilans et diagnostics sont regroupés dans [archives/](archives/README.md). L’audit du 1er novembre et ses mesures restent dans [audits/](audits/AUDIT_2026-11-01.md). La [réconciliation du déploiement](RECONCILIATION_SAMSTAG_2026-11-01.md) reste disponible comme référence datée, sans confirmer l’état distant actuel.

La [passation](PASSATION_PROJET.md) reste à son emplacement stable : c’est le journal de reprise, pas un tableau de bord courant. Les rapports générés et preuves locales sont expliqués dans [Preuves et archives](PREUVES_ET_ARCHIVES.md).

Le [plan d’action de réorganisation du code](PLAN_REORGANISATION_CODE.md) détaille le troisième point : étapes R0 à R7, fichiers à déplacer, tests et livraison séparée. R0 et le pilote R1 Vidy sont terminés localement ; R2 à R7 restent à faire.
