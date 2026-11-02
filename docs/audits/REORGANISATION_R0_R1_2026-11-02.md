# Réorganisation R0–R1 — 2 novembre 2026

## Résultat

Le paquet `samstag/` existe. Le lecteur Vidy est dans [vidy.py](../../samstag/collection/adapters/vidy.py). `programme_adapters.py` conserve le dispatch et réexporte les anciens noms pour les consommateurs existants. Une seule implémentation des fonctions est conservée.

Ce lot est le pilote local anticipé autorisé par la demande de réorganisation du 2 novembre. Les corrections L2/L3 et les contrôles L4 ne sont pas déclarés terminés. Les autres adaptateurs et les couches web, domaine et stockage restent à déplacer dans les prochains lots.

## Référence R0

- Arbre Git propre avant modification ; HEAD de départ `3f57d9b` (`docs: organize audit and implementation roadmap`).
- `make check` avant déplacement : 107 tests Python réussis, registres et syntaxe JavaScript valides.
- Empreintes des modules racine et scénarios synthétiques Vidy enregistrés sous `.artifacts/reorganisation-2026-11-02/` (ignoré par Git).
- Aucun changement antérieur non commité à préserver au début de ce lot. Cette observation remplace l’avertissement daté du plan sur les nombreux changements non commités.

## Déplacement R1

Les cinq fonctions `vidy_kind`, `vidy_blocks`, `confirm_vidy`, `parse_vidy`, `unescape_title` et la constante `VIDY_ROOMS` sont extraites de `programme_adapters.py`. Les instructions des fonctions sont inchangées ; les dépendances sur les aides de date, événements de base, configuration et résultats restent explicites.

Les `__init__.py` du paquet et des sous-paquets ne lancent aucune collecte ni initialisation de base. Les imports existants depuis `programme_adapters` restent possibles via des réexports explicites. Le lecteur utilise encore les modules communs racine ; ils seront déplacés séparément.

## Vérifications

- Comparaison des arbres syntaxiques des cinq fonctions avec la référence Git : identiques.
- Deux scénarios avant/après, contenant chacun cinq observations : séance diurne, séance du soir, minuit non vérifié, annulation, lieu extérieur ; confirmations exactes et horaires contradictoires. Tous les champs des événements, la méthode et le statut partiel sont identiques.
- Tests Vidy existants importés depuis le nouveau module ; deux régressions ajoutées : identité des anciens imports et confirmation d’une séance diurne via le dispatch utilisé par l’application.
- `make check` final : **109 tests Python réussis**, registres valides (39 sources, 159 lieux, 28 bars), syntaxe JavaScript valide.
- Vérification d’import des trois paquets dans un processus isolé : aucune base créée et aucun module applicatif chargé par ces seuls imports.

Les fichiers JSON avant/après et le manifeste restent dans `.artifacts/`. Ce bilan versionné en conserve la portée et les résultats.

## Limites et reprise

Aucun site source contacté, aucune collecte réelle, aucune écriture VPS, aucun déploiement et aucun changement d’interface. Pas de nouvelle campagne E2E : routes et ressources web inchangées ; le dispatch est couvert par le test local.

Prochaine séance : R2, sous-lot CityClub uniquement, avec comparaison de fixtures et maintien des anciens imports. Les anciens modules ne sont pas à supprimer tant que leurs consommateurs n’ont pas migré.
