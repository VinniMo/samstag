# L3 — qualité et doublons

**État au 2 novembre 2026 : L3 terminé.** Les rapprochements certains sont réversibles, les fiches d'origine restent conservées et l'horaire atypique de Taco's a été contrôlé à la source.

## Résultat attendu

Une même sortie ne doit apparaître qu'une fois lorsque plusieurs sources la décrivent différemment. La fiche officielle doit être privilégiée, toutes les preuves doivent rester consultables et toute décision doit pouvoir être annulée.

Le cas de départ est le concert publié sous deux titres, « Mike D » par L'Agenda et « Mike D 5D » par Les Docks, au même lieu, à la même date et à la même heure.

## Règles de sécurité

- Aucun rapprochement fondé uniquement sur la ressemblance des titres.
- Le lieu reconnu, la date et l'heure doivent correspondre.
- Deux spectacles réellement distincts au même endroit et au même moment restent séparés.
- Une situation ambiguë est signalée pour contrôle humain.
- Les fiches d'origine et leurs liens de preuve sont conservés.
- Le premier rapport fonctionne en lecture seule avant toute modification des sorties visibles.

## Ordre d'exécution

| Étape | Travail | Résultat contrôlable |
|---|---|---|
| A — Détecter — terminée | Reproduire Mike D avec une petite donnée de test, repérer les candidats qui partagent lieu, date et heure, produire un rapport sans modifier les données | Mike D détecté comme un groupe de deux fiches ; base isolée inchangée |
| B — Décider — terminée | Identifier les cas certains, privilégier la source officielle, classer les cas ambigus et conserver tous les liens | Mike D n'apparaît plus deux fois sur la base isolée ; les exemples ambigus restent séparés |
| C — Vérifier — terminée | Rejouer les contrôles sur une base isolée, mesurer les décisions automatiques et manuelles, puis contrôler Taco's séparément | Rapport final compréhensible, aucune perte de preuve, aucune fusion risquée |

## Décision pour un candidat

Un candidat peut être rapproché automatiquement seulement si une source officielle confirme l'occurrence, les informations pratiques correspondent et aucune autre sortie concurrente n'existe au même créneau. Dans les autres cas, il reste visible séparément ou passe en revue selon son état actuel.

Le rapprochement sera enregistré à côté des fiches d'origine. Il ne supprimera pas les observations collectées. La sortie publique choisie utilisera la source officielle et réunira les liens de preuve disponibles.

## Contrôles obligatoires

- Mike D / Mike D 5D produit une seule sortie publique.
- Deux titres différents correspondant à deux spectacles distincts restent deux sorties.
- Une heure inconnue ou contradictoire interdit le rapprochement automatique.
- Une source générale ne remplace jamais une source officielle valide.
- Toutes les URL de preuve restent présentes après rapprochement.
- Une nouvelle collecte peut réviser ou annuler un rapprochement sans supprimer l'historique.
- Le rapport indique séparément les cas rapprochés, ambigus et laissés inchangés.

## Résultat de la première session

`L3.1`, `L3.2` et `L3.6` sont terminés. Le rapport détecte les fiches distinctes qui partagent un lieu reconnu, une date et une heure. Il distingue le cas officiel + agrégateur des autres coïncidences à contrôler. Il ignore les horaires incomplets et ne modifie aucune donnée.

Le cas Mike D produit un groupe contenant deux fiches et leurs preuves. Un exemple de deux spectacles distincts au même créneau reste intact et est seulement signalé. 116 tests réussissent. Aucun site n'a été contacté.

## Résultat de la deuxième session

`L3.3`, `L3.4` et `L3.5` sont terminés sur une base isolée. Un rapprochement automatique exige exactement une fiche officielle et une fiche d'agrégateur déjà validées, au même lieu, à la même date et à la même heure, avec des titres compatibles selon une règle volontairement étroite.

La fiche officielle reste visible et récupère les liens de preuve des deux fiches. Les données d'origine ne sont ni modifiées ni supprimées. Si la fiche officielle n'est plus publiable ou si une passe ultérieure ne confirme plus la décision, l'autre fiche redevient visible. Les titres incompatibles, plusieurs fiches officielles ou tout autre doute restent séparés.

118 tests réussissent. Aucun site n'a été contacté pendant les étapes A et B.

## Résultat de la troisième session

`L3.7` est terminé après une collecte limitée à Taco's dans une base isolée. La source officielle contient trois occurrences de « Combat de chiens », les 18 novembre 2026, 16 décembre 2026 et 20 janvier 2027, avec le champ `time` fixé à `20:26`. La description confirme aussi « Début des matchs à 20h26 ».

L'horaire atypique est donc volontaire et reste inchangé. Un test protège désormais sa lecture exacte contre un futur arrondi. La passe ciblée a lu 64 entrées, dont 9 publiables selon les règles actuelles, sans candidat au doublon. Aucun autre site, aucune donnée réelle et aucun service distant n'ont été modifiés.

