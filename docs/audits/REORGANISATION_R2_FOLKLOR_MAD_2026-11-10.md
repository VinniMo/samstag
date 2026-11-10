# Réorganisation R2 — Folklor et MAD — 10 novembre 2026

`parse_folklor` et `parse_mad_ticket` sont déplacés dans leurs modules nommés
sous `samstag/collection/adapters/`. Les anciens imports et le dispatch restent
identiques. L'orchestration MAD, sa publication automatique désactivée et ses
statuts partiels ne changent pas.

Quatre tests ciblés puis `make check` réussissent avec 144 tests. Ils couvrent
dates/heures explicites Folklor, absence d'heure, structure absente, portes
MAD, lieu hors périmètre et échec total des fiches. Aucun appel réel, base,
interface, VPS ou Render n'est modifié. Suite : R2 JazzOnze+.
