# Validation locale des collecteurs — 16 octobre 2026

Base isolée : `validation/collecte.sqlite3`. Aucun déploiement ni envoi GitHub.

## Résultat de la passe réelle

35 sources activées sur 36 configurées ; 794 observations distinctes, 290 événements publics selon les règles actuelles. Ces 290 événements ne constituent pas une validation éditoriale manuelle.

États techniques : {'ok': 24, 'needs_adapter': 7, 'error': 1, 'empty': 2, 'partial': 1}. Un état ok signifie que le lecteur a produit des données, pas que chaque événement est publiable.

311 observations en revue, 175 exclues, 18 candidates à une première qualification. Les drapeaux automatiques provisoires n’ont pas été élargis.

| Source | État de la passe | Observations | Publication automatique configurée |
|---|---|---:|---|
| Arsenic | ok | 56 | oui |
| Cave du Bleu Lézard | needs_adapter | 0 | non |
| Château Music Club | error | 0 | non |
| Captain Cook | ok | 12 | non |
| Chorus Jazz Club | ok | 6 | oui |
| D! Club | ok | 27 | oui |
| L’Étoile Blanche | ok | 43 | oui |
| Les Gosses du Québec — Lausanne | empty | 0 | oui |
| Holy Monkey | needs_adapter | 0 | non |
| JazzOnze+ | ok | 33 | oui |
| La Datcha | ok | 14 | non |
| Pavillon Naftule | ok | 100 | oui |
| Cinéma Oblò | ok | 5 | oui |
| Satellite | needs_adapter | 0 | non |
| Taco’s Bar | ok | 43 | oui |
| Théâtre Boulimie | ok | 21 | oui |
| Barberousse | ok | 7 | non |
| Bruxelles Café | ok | 9 | non |
| Café du Simplon | needs_adapter | 0 | non |
| Cinéma Bellevaux | ok | 20 | oui |
| Cinéma CityClub | ok | 50 | oui |
| Les Docks | ok | 28 | oui |
| Folklor | ok | 8 | oui |
| La Grange UNIL | empty | 0 | non |
| Hungry Bear | needs_adapter | 0 | non |
| Jumeaux Jazz Club | ok | 39 | oui |
| L’Agenda | partial | 129 | oui |
| La Brèche | ok | 10 | oui |
| Lausanne Tourisme | ok | 40 | oui |
| Le Montriond | needs_adapter | 0 | non |
| Le Romandie | ok | 34 | oui |
| MAD Club | ok | 18 | oui |
| Pulloff Théâtres | ok | 54 | non |
| Ta Cave | ok | 14 | non |
| Théâtre Vidy-Lausanne | needs_adapter | 0 | non |

## Corrections vérifiées

- Une collecte partielle ou contenant des enregistrements impossibles à évaluer ne déclenche plus le retrait des événements absents.
- L’Agenda signale partial lorsque la limite de quatre pages par région est atteinte avec une page suivante annoncée.
- La Grange signale une limite de fiches et classe les concerts en musique.
- Le lecteur générique de pages de détail signale les échecs et limites de lecture. Cette dernière correction a été faite après la passe réelle : le statut ok de Lausanne Tourisme dans le JSON est historique et ne garantit pas une lecture complète.
- Régressions ajoutées : Pulloff au changement d’année, Grange, pagination, retrait, verrou du worker, erreurs partielles, sources jamais collectées et fraîcheur.

## Limites et suite ciblée

- La Grange : trois fiches lues, aucune séance extraite ; conserver la publication automatique désactivée et inspecter les pages avant qualification.
- Pulloff : 54 séances extraites ; publication automatique toujours désactivée, validation éditoriale à terminer.
- Château Music Club : ancien lien HTTP 404, aucune conclusion sur la fermeture du lieu.
- Sept sources needs_adapter : Bleu Lézard, Holy Monkey, Satellite (canal direct), Simplon, Hungry Bear, Montriond, Vidy.
- Datcha, Captain Cook, Bruxelles, Barberousse et Ta Cave : extractions à ne pas confondre avec des événements qualifiés.
- Worker : tests locaux du verrou, des dégradations et de la reprise après exception ; aucun service permanent installé.
- Environnement local Python 3.9 : avertissement LibreSSL/urllib3 observé. Les requêtes de cette passe ont abouti ; préférer Python récent pour l’exploitation.

Rapport brut : `validation/rapport-collecte.json`. Tests : `validation/tests.log`.

Vérification finale après toutes les corrections : **64 tests réussis** (`validation/tests.log`).
