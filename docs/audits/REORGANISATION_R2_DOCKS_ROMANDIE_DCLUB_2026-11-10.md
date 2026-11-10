# Réorganisation R2 — Docks, Romandie et D! — 10 novembre 2026

Les lecteurs `parse_docks`, `parse_dclub` et `collect_dclub` vivent désormais
dans leurs modules nommés. Le parcours borné des fiches Docks et Romandie est
isolé dans `docks_romandie.py`. `venue_adapters.py` conserve des réexports
compatibles et délègue son dispatch aux mêmes objets.

Les fixtures conservent les horaires artistiques et de portes, les salles D!,
les preuves d'inscription, les états Docks, les diagnostics de pages et le rôle
« portes » des données Romandie. Seize scénarios ciblés puis `make check`
réussissent avec 147 tests, registres et JavaScript valides.

Aucun site réel, collecte, base, interface, VPS, Render ou production n'est
modifié. Suite : Jumeaux, Chorus et Bellevaux.
