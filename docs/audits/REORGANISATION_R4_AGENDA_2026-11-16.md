# Réorganisation R4 — règles de programme — 16 novembre 2026

Les règles de périodes, rubriques, prix et recherche vivent dans
`samstag/domain/agenda.py`. Le module historique `agenda.py` pointe vers le
même état Python, ce qui conserve les imports et les remplacements d'horloge
utilisés par les tests et le serveur E2E.

Les onze tests ciblés passent, dont l'identité du relais historique. Les corps
de toutes les fonctions sont identiques à la référence Git avant déplacement.
`make check` réussit avec 159 tests, registres et JavaScript valides.

Aucune base, interface, collecte réelle, VPS, Render ou production n'est
modifiée. Suite R4 : règles de qualité, puis stockage SQLite dans des lots
séparés.
