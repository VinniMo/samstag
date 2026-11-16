# Réorganisation R2 — La Brèche et Oblò — validation du 16 novembre 2026

`parse_breche` et `parse_oblo` vivent dans leurs modules nommés sous
`samstag/collection/adapters/`. `expanded_adapters.py` réexporte ces mêmes
objets et son dispatch les utilise sans copie.

Quatre tests ciblés conservent horaires de portes et de début, preuves,
classification, identité des occurrences et refus des programmes absents. Le
corps des deux fonctions est identique à la référence Git avant déplacement.
`make check` réussit avec 156 tests, registres et JavaScript valides dans
l'arbre complet de reprise.

Aucun site réel, collecte, base, interface, VPS, Render ou production n'est
modifié. Ce sous-lot clôt les adaptateurs R2 ; les travaux R3 présents dans
l'arbre sont conservés dans un commit et une PR séparés.
