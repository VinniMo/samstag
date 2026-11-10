# Réorganisation R2 — Naftule et Boulimie — 10 novembre 2026

## Résultat

Les lecteurs `parse_naftule` et `parse_boulimie` se trouvent désormais dans
`samstag/collection/adapters/naftule.py` et `boulimie.py`. Leurs anciens noms
restent réexportés depuis `expanded_adapters.py`, et le dispatch existant
utilise les mêmes objets.

Le constructeur d'événement officiel et la lecture d'une date française ont
été placés dans `adapters/common.py`. Ce module a un rôle limité et remplace
les définitions auparavant présentes dans `expanded_adapters.py`. CityClub
utilise aussi ce constructeur partagé sans changement de sortie.

## Vérifications

- anciens et nouveaux imports identiques par identité d'objet ;
- Naftule : séances distinctes malgré une billetterie commune, champs complets,
  genre, image, heure unique, heures ambiguës non inventées et calendrier
  absent refusé ;
- Boulimie : plage datée, horaires explicites par jour, titre, description,
  hors-les-murs sans lieu hérité et absence d'horaire laissée en revue ;
- CityClub rejoué après mutualisation du constructeur ;
- six tests ciblés réussis ;
- `make check` réussi avec 139 tests Python, 39 sources, 159 lieux, 28 bars et
  syntaxe JavaScript valide.

## Limites et reprise

Aucun site réel n'a été contacté. Aucune collecte, base, interface, production
VPS ou configuration Render n'a été modifiée. Aucun correctif de source n'est
inclus. Le prochain sous-lot R2 conseillé est Arsenic.
