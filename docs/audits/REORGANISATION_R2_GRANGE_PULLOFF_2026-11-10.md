# Réorganisation R2 — Grange et Pulloff — 10 novembre 2026

Les lecteurs La Grange UNIL et Pulloff sont déplacés dans
`samstag/collection/adapters/grange.py` et `pulloff.py`. Les réexports
historiques et le dispatch conservent les mêmes objets.

Les contrôles couvrent les dates transannuelles, jours publiés, relâches
explicites ou incertaines, descriptions isolées d'un widget voisin, catégories
Grange, dédoublonnage mobile/ordinateur, commune prouvée, fiche illisible et
limite de détails. Sept tests ciblés puis `make check` réussissent avec 143
tests Python, registres et JavaScript valides.

Aucun appel réel, collecte, base, interface, VPS ou Render n'est modifié. Le
prochain sous-lot est Folklor/MAD.
