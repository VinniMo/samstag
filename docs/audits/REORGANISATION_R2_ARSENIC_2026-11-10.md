# Réorganisation R2 — Arsenic — 10 novembre 2026

## Résultat

Le lecteur du calendrier public Arsenic est dans
`samstag/collection/adapters/arsenic.py`. `expanded_adapters.py` conserve le
nom historique et son dispatch utilise le même objet `parse_arsenic`.

La lecture reste strictement fondée sur la variable publique `spectacles` :
aucune exécution JavaScript et aucune date ou heure reconstruite. Les marqueurs
`nohour`, annulations, gratuité, images et preuves sont conservés.

## Vérifications

- identité de l'ancien et du nouvel import ;
- occurrence horodatée et occurrence `nohour` de la même série ;
- titre et description HTML décodés, preuve, image, gratuité et annulation ;
- classifications club, danse et théâtre ;
- donnée absente ou format racine invalide refusés ;
- trois tests ciblés réussis ;
- `make check` réussi avec 142 tests Python, registres valides et syntaxe
  JavaScript valide.

## Limites et reprise

Aucun site réel, base, interface, VPS ou Render n'a été modifié. Ce lot ne
répare ni n'élargit le lecteur. Le prochain sous-lot R2 est Grange/Pulloff.
