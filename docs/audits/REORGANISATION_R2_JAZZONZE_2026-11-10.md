# Réorganisation R2 — JazzOnze+ — 10 novembre 2026

Les fonctions `parse_jazzonze` et `collect_jazzonze` sont dans le module nommé
`samstag/collection/adapters/jazzonze.py`; anciens imports et dispatch pointent
vers ces mêmes objets. Les adresses restent limitées aux blocs d'accès nommés,
les événements multi-lieux conservent leurs preuves, minuit reste non vérifié
et l'enrichissement des descriptions demeure borné et exige le même titre.

Cinq tests ciblés et `make check` réussissent avec 145 tests. Aucun appel réel,
base, interface, VPS ou Render n'est modifié. Suite : Docks/Romandie/D!.
