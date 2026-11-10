# Réorganisation R2 — bars et widgets Hango — 10 novembre 2026

Les calendriers publics Taco's, Captain Cook, Bruxelles Café et La Datcha sont
regroupés dans `samstag/collection/adapters/bars.py`. Le widget officiel Hango
vit dans `samstag/collection/adapters/hango.py`. Les anciens modules racine ne
contiennent plus que des imports de compatibilité vers les mêmes objets.

Les fixtures conservent horaires atypiques, fins nocturnes, incertitudes,
exclusions commerciales, identité du widget, pagination, attribution au lieu et
preuves. Douze tests ciblés puis `make check` réussissent avec 150 tests,
registres et JavaScript valides.

Aucun site réel, collecte, base, interface, VPS, Render ou production n'est
modifié. Suite : agrégateurs.
