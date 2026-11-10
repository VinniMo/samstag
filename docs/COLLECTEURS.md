# Collecteurs de Samstag

Référence documentaire au 1er novembre 2026. Ce tableau rapproche le registre local et le dernier instantané public sauvegardé. Il ne lance aucune collecte et ne garantit pas l’état actuel des sites.

## Comprendre les chiffres

39 canaux configurés, 37 actifs et 23 autorisés à publier après contrôles dans le code local. Le total était de 24 dans l’instantané public précédent ; le MAD a été retiré de la publication automatique le 2 novembre après un contrôle ciblé. Cinq canaux actifs sont sans adaptateur : une inscription dans le registre ne constitue pas un collecteur opérationnel. L’instantané public contient 322 sorties sur 19 lieux, sans garantie d’exhaustivité.

## Fréquence et périmètre

La configuration versionnée lance une passe au démarrage, puis attend 3 600 secondes après sa fin. Le rythme est commun aux sources actives, indépendant des visites, pour un horizon de 90 jours selon les programmes publiés. La configuration installée sur le VPS n’a pas été revérifiée par SSH. Les événements non revérifiés depuis plus de 24 heures sont masqués.

Le code local accepte aussi les événements diurnes et les affiche dans « Aujourd’hui » ; cette évolution n’est pas encore livrée en production. Les exclusions de lieux et les exigences de preuves restent applicables.

## Sources autorisées à publier sous conditions

« OK » signifie que la lecture a fonctionné au contrôle, pas que tous les événements futurs sont couverts. Le nombre de sorties est attribué à la source retenue, et ne correspond pas forcément au total du lieu.

| Source ou lieu | Canal | État au contrôle | Sorties publiques |
|---|---|---|---:|
| Les Docks | [Programme](https://www.docks.ch/programme/) | OK | 21 |
| Le Romandie | [Programme](https://www.leromandie.ch/programmation) | OK | 2 |
| D! Club | [Programme](https://dclub.ch/agenda/) | OK | 15 |
| MAD Club | [Programme](https://www.mad.club/agenda/) | Erreur | 0 |
| Folklor | [Programme](https://www.folklor.club/events/) | OK | 10 |
| Jumeaux Jazz Club | [Programme](https://www.jumeaux.club/) | OK | 24 |
| Chorus Jazz Club | [Programme](https://chorus.ch/) | OK | 0 |
| Théâtre Boulimie | [Programme](https://theatreboulimie.com/) | OK | 14 |
| Brasserie du Château / Château Music Club | [Programme](https://app.hango.ch/venues/chateau-music-club-zofhmvrmaepaiykgh08megmv) | Partiel | 0 |
| Cinéma Bellevaux | [Programme](https://www.cinemabellevaux.ch/) | Vide | 0 |
| Taco’s Bar | [Programme](https://tacos-bar.ch/events) | OK | 9 |
| L’Étoile Blanche | [Programme](https://etoileblanche.ch/) | OK | 18 |
| Les Gosses du Québec — Lausanne | [Programme](https://gossesduquebec.ch/pub-lausanne/) | Vide | 0 |
| Lausanne Tourisme | [Programme](https://www.lausanne-tourisme.ch/fr/evenement/) | Partiel | 0 |
| L’Agenda | [Programme](https://www.l-agenda.ch/evenements/) | OK | 13 |
| La Brèche | [Programme](https://www.la-breche.fun/) | OK | 3 |
| Cinéma CityClub | [Programme](https://www.cityclubpully.ch/) | OK | 45 |
| Pavillon Naftule | [Programme](https://naftule.ch/programme/) | OK | 39 |
| JazzOnze+ | [Programme](https://jazzonzeplus.ch/) | OK | 0 |
| Arsenic | [Programme](https://arsenic.ch/) | OK | 11 |
| La Grange UNIL | [Programme](https://www.grange-unil.ch/) | OK | 19 |
| Théâtre Vidy-Lausanne | [Programme](https://www.vidy.ch/fr/calendrier/) | Partiel | 57 |
| Pulloff Théâtres | [Programme](https://www.pulloff.ch/) | OK | 17 |
| Cinéma Oblò | [Programme](https://oblo.ch/cinema) | OK | 5 |

## Sources actives en revue

Aucune publication automatique attribuée à ces canaux dans l’instantané.

| Source ou lieu | Canal | État au contrôle |
|---|---|---|
| Cave du Bleu Lézard | [Programme](https://www.bleu-lezard.ch/programmation/) | Vide |
| Barberousse | [Programme](https://www.barberoussebar.ch/agenda) | OK |
| La Datcha | [Programme](https://la-datcha.ch/programmation/) | OK |
| Bruxelles Café | [Programme](https://www.bruxellescafe.ch/) | OK |
| Captain Cook | [Programme](https://captaincook.ch/) | OK |
| Holy Monkey | [Programme](https://holymonkey.ch/next-events/) | Partiel |
| Le Montriond | [Programme](https://www.lemontriond.ch/home) | Sans adaptateur |
| Hungry Bear | [Programme](https://www.hungrybearfood.ch/events) | Partiel |
| Ta Cave | [Programme](https://www.tacave.ch/evenements) | OK |
| Café du Simplon | [Programme](https://www.cafedusimplon.ch/) | Sans adaptateur |
| The Great Escape | [Programme](https://the-great.ch/) | Sans adaptateur |
| Le Pavillon / Pavillon Bar & Kitchen | [Programme](https://pavillonbar.ch/) | Sans adaptateur |
| La Bossette | [Programme](https://bo7.ch/) | Sans adaptateur |

## Limites à connaître

- Romandie : automatisation limitée aux soirées club. Vidy : sélection partielle avec confirmation des fiches.
- Taco's : contrôle ciblé du 2 novembre 2026, les trois horaires 20:26 de « Combat de chiens » sont écrits ainsi dans la source officielle et sa description ; ils ne doivent pas être arrondis.
- MAD : agenda accessible, mais les six fiches liées ont toutes échoué au contrôle ciblé du 2 novembre ; publication automatique locale désactivée. Bellevaux, Gosses du Québec et Bleu Lézard : programmes lus vides, sans conclusion de fermeture.
- Lausanne Tourisme : seulement 40 fiches lues sur 1 148 liens repérés. L’Agenda : sélection filtrée et pagination bornée.
- Barberousse : données structurées anciennes. Datcha, Captain Cook, Bruxelles Café, Ta Cave, Holy Monkey et Hungry Bear : qualification incomplète.
- JazzOnze+ est un programme multi-lieux ; les agrégateurs ne représentent pas une salle physique unique.
- Satellite et Guidle sont désactivés. Buzz Club et les bibliothèques sont exclus. Instagram reste reporté.

## Où modifier et vérifier ?

Le [registre des sources](../data/sources.json) contient les URL et autorisations ; les [lieux](../data/venues.json) et [bars](../data/bars.json) sont des inventaires distincts. `scraper.py` répartit la lecture entre `venue_adapters.py`, `bar_adapters.py`, `hango_adapter.py`, `expanded_adapters.py` et `programme_adapters.py`, avec des lecteurs génériques en complément.

Pour consulter un rapport local sans contacter les sites : `make report`. Pour développer : [guide de développement](DEVELOPPEMENT.md). Pour les constats détaillés : [audit](audits/AUDIT_2026-11-01.md) et [mesures datées](audits/2026-11-01-mesures.json).

La priorité reste de fiabiliser les diagnostics, réparer les sources en panne et mesurer les programmes réellement couverts avant d’annoncer une couverture exhaustive.

## Où trouver les lecteurs déjà réorganisés ?

Les lecteurs réorganisés jusqu'à Grange/Pulloff se trouvent dans les modules nommés de [samstag/collection/adapters/](../samstag/collection/adapters/). Les imports historiques restent compatibles pendant la migration. Les autres lecteurs restent dans les modules racine. Les bilans sont liés depuis le [plan de réorganisation](PLAN_REORGANISATION_CODE.md). Aucun changement de programme extrait ni livraison en production.
