# Réorganisation R2 — Jumeaux, Chorus et Bellevaux — 10 novembre 2026

Les fonctions `parse_jumeaux`, `parse_chorus` et `parse_bellevaux` sont dans
leurs modules nommés sous `samstag/collection/adapters/`. Les imports historiques
et le dispatch de `venue_adapters.py` utilisent ces mêmes objets.

Les fixtures conservent les éléments masqués, portes et débuts distincts chez
Jumeaux, le mois et l'année publiés chez Chorus, ainsi que la période explicite
et les séances séparées chez Bellevaux. Treize scénarios du bloc lecteurs puis
`make check` réussissent avec 148 tests, registres et JavaScript valides.

Aucun site réel, collecte, base, interface, VPS, Render ou production n'est
modifié. Suite : bars et widgets Hango.
