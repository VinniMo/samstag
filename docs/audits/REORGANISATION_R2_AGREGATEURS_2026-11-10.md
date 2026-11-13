# Réorganisation R2 — agrégateurs — 10 novembre 2026

`parse_tourisme` vit dans `samstag/collection/adapters/tourisme.py` et les
fonctions `parse_lagenda` / `collect_lagenda` dans `lagenda.py`. Les imports
historiques et les dispatchs utilisent les mêmes objets.

Les fixtures conservent adresses prouvées, occurrences nocturnes, plages non
inventées, catégories, lieux vérifiés, régions, horizon et pagination bornée.
Quatre tests ciblés puis `make check` réussissent avec 152 tests, registres et
JavaScript valides.

Aucun site réel, collecte, base, interface, VPS, Render ou production n'est
modifié. R2 doit encore extraire les lecteurs officiels résiduels La Brèche et
Oblò avant de passer à R3.
