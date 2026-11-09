# Réorganisation R2 — CityClub — 9 novembre 2026

## Résultat

Le lecteur mensuel du Cinéma CityClub est désormais dans
`samstag/collection/adapters/cityclub.py`. `expanded_adapters.py` conserve un
réexport explicite et son dispatch utilise exactement cette implémentation.
Il n'existe donc qu'une fonction `parse_cityclub` active.

Le déplacement ne change ni les sources suivies, ni les règles de dates, ni
les événements produits. Les séances du mois suivant restent acceptées
uniquement lorsqu'elles sont écrites dans le programme mensuel ; le passage
de décembre à janvier conserve l'année correcte.

## Vérifications

- ancien import et nouvel import identiques par identité d'objet ;
- fixture détaillée contrôlant titre, URL, preuve, lieu, commune, type,
  catégorie, adaptateur, date, heure, fuseau, description, image et identité ;
- séance d'un mois non annoncé ignorée ; structure mensuelle absente refusée ;
- trois tests CityClub ciblés réussis ;
- `make check` réussi avec 136 tests Python, 39 sources, 159 lieux, 28 bars et
  syntaxe JavaScript valide.

## Limites et reprise

Aucun site n'a été contacté, aucune collecte réelle ni base modifiée, aucun
VPS ou service distant utilisé et aucun changement fonctionnel introduit.
Le sous-lot suivant conseillé est R2 Naftule/Boulimie, séparé de toute
réparation de source.
