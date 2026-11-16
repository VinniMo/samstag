# Réorganisation R3 — outils de collecte — validation du 16 novembre 2026

Les lecteurs génériques JSON-LD, iCalendar et HTML vivent dans
`samstag/collection/parsers/`. Le client HTTP, le registre, le résultat de
collecte, l'orchestration et le worker vivent dans `samstag/collection/`.

Les anciens modules restent des relais de compatibilité vers le même état de
module. Deux tests dédiés figent cette identité et celle des fonctions de
lecture génériques. Une comparaison AST avec la référence Git avant déplacement
confirme que les corps de toutes les fonctions et classes déplacées sont
identiques.

`make check`, les commandes d'aide du worker historique et du worker empaqueté,
les registres et la syntaxe JavaScript sont vérifiés sans appel réseau. Aucun
site réel, base, interface, VPS, Render ou production n'est modifié. Suite : R4,
règles et stockage.
