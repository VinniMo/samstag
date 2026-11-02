# Preuves et archives

**Index au 1er novembre 2026.** Cet index indique ce qui est disponible dans le checkout et ce qui reste à retrouver ou à produire. Il ne remplace pas les preuves elles-mêmes.

## Présent dans le dépôt

| Preuve | Emplacement | Portée |
|---|---|---|
| Audit public et local | `docs/audits/AUDIT_2026-11-01.md` | architecture, site, collecteurs, organisation |
| Contrôle VPS L4 | `docs/audits/L4_VPS_LECTURE_SEULE_2026-11-02.md` | services, version, options non secrètes, sauvegarde et santé en lecture seule |
| Mesures publiques | `docs/audits/2026-11-01-mesures.json` | comptages et santé au 1er novembre |
| Diagnostics de collecte | `docs/archives/collecte_diagnostic.json`, `docs/archives/diagnostic_collecte_v2.json` | instantanés historiques |
| Validation locale v2 | `docs/archives/validation_locale_v2.json` | validation historique |
| Fixture publique E2E | `e2e/fixtures/public-snapshot.json` | jeu de référence E2E |
| Historique de décisions | `docs/PASSATION_PROJET.md` et documents historiques indexés | contexte et limites datés |

## Référencé mais absent du checkout

Les anciens comptes rendus mentionnent des dossiers `validation/`, `reprise/`, `sauvegardes/` et `apercus/`. Ils ne sont pas présents dans le checkout contrôlé le 1er novembre 2026 et peuvent avoir été ignorés par Git, conservés sur une autre machine ou supprimés. Leur contenu ne doit pas être considéré comme disponible tant qu’il n’a pas été retrouvé et vérifié.

## Preuves distantes

Le contrôle SSH en lecture seule du 2 novembre confirme l'installation Infomaniak, les services, les options non secrètes, la sauvegarde quotidienne et la version `ed42492` par empreintes. Le rapport ne contient aucun secret ni donnée de production.

La copie hors VPS, la restauration d’une sauvegarde, l'observation sur 24 heures, la réception d'une alerte et un audit mobile complet restent à produire dans les lots correspondants. Les campagnes E2E locales récentes sont consignées dans la passation ; elles ne certifient pas le fonctionnement de la production.

## Données à ne pas versionner

- secrets, clés de session et fichiers d’environnement réels ;
- base de production et sauvegardes contenant des retours utilisateurs ;
- journaux bruts contenant des données personnelles ou des en-têtes sensibles ;
- captures privées d’administration.

## Convention pour les prochaines preuves

Une preuve doit indiquer la date, le périmètre, la commande ou méthode, le résultat, les limites et le commit concerné. Les petits résultats structurés peuvent être versionnés dans `docs/audits/`. Les sauvegardes et données sensibles doivent rester dans un stockage privé documenté par un identifiant, une date et une politique de rétention.

## Rangement local du 1er novembre 2026

Dix bilans et diagnostics ont été regroupés dans [archives/](archives/README.md). Les trois diagnostics JSON ont été conservés à l’identique. Seuls `.DS_Store`, `scripts/__pycache__/` et `e2e/__pycache__/` ont été supprimés : ce sont des métadonnées système ou du bytecode régénérable. Les entrées répétées `.venv/` du fichier `.gitignore` ont été dédupliquées.

Les rapports de `.artifacts/`, les données de `.local/`, les dépendances, les ressources `.claude/` et `.impeccable/`, les fixtures et les preuves versionnées sont conservés. Aucun fichier de sauvegarde ou de production n’a été supprimé. Le [guide du dossier](SE_REPERER.md) indique leur rôle.
