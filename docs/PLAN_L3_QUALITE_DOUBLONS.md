# L3 — qualité et doublons

**État au 2 novembre 2026 : étape A terminée, étape B à démarrer.** Le détecteur et son rapport sont en lecture seule ; aucune sortie n'a été fusionnée.

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
| B — Décider | Identifier les cas certains, privilégier la source officielle, classer les cas ambigus et conserver tous les liens | Mike D n'apparaît plus deux fois ; les exemples ambigus restent séparés |
| C — Vérifier | Rejouer les contrôles sur une base isolée, mesurer les décisions automatiques et manuelles, puis contrôler Taco's séparément | Rapport final compréhensible, aucune perte de preuve, aucune fusion risquée |

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

La prochaine session couvre `L3.3` à `L3.5` : décider quels candidats peuvent être rapprochés, privilégier la source officielle et conserver toutes les preuves. Le contrôle Taco's (`L3.7`) reste séparé.

