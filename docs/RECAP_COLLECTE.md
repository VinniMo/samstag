# Lausanne Cultura — récapitulatif du moteur et des collecteurs

Version locale du 16 octobre 2026. **Aucun changement sur Render ni sur GitHub.**

Le moteur travaille maintenant sur la base élargie des sorties du soir. Les bars
complètent les concerts, clubs, spectacles et cinémas de l’inventaire initial.
Le registre contient les 154 entités consolidées, avec 58 retenues pour les
sorties du soir, 32 à vérifier et 64 écartées. Ces nombres ne désignent pas des
collecteurs opérationnels. Bibliothèques, salles génériques et Buzz Club restent
hors du flux. Le design existant est conservé.

## Ce qui a été fait

**1. Relier la recherche au vrai moteur Python.** L’application Flask lit
maintenant le registre consolidé et une configuration de sources distincte.
Une institution, une salle et son programmateur ne deviennent plus trois
sources équivalentes par simple présence dans l’inventaire. La commune et le
lieu réels de chaque événement restent nécessaires.

**2. Écrire des collecteurs adaptés aux sites.** Les programmes officiels sont
lus selon leur format réel : fiches des Docks, programme de Jumeaux, calendrier
de Chorus, séances de Bellevaux, agenda du D! Club, fiches du Romandie, calendrier
public de Taco’s et calendriers publics Hango intégrés aux sites des bars.
Lausanne Tourisme apporte une couverture complémentaire. Bruxelles, Datcha et
Captain Cook alimentent une file de vérification tant que leurs données ne
suffisent pas à une publication automatique.

**3. Automatiser uniquement les données qualifiées.** Une source connue ne
suffit pas : l’événement doit avoir un lieu admis, une commune autorisée, une
catégorie pertinente et une date avec un horaire cohérent. Les séances diurnes,
les événements privés ou annulés explicitement signalés, les promotions
identifiées et les programmes globaux ne remplissent pas l’application.
Les cas incomplets restent invisibles dans le programme public.

**4. Distinguer les horaires.** Le début artistique est séparé des portes.
Pour une soirée club dont seule l’ouverture est publiée, le libellé « Portes »
est visible. Pour un concert, cette seule heure ne suffit pas. Les changements
d’heure et les fins après minuit sont traités ; une heure locale ambiguë n’est
pas transformée en un fuseau inventé. Chaque séance de cinéma conserve son
propre horaire. Aucune durée de film ou de concert n’est inventée.

**5. Éviter les doublons et conserver les preuves.** Le rapprochement exact
utilise titre normalisé, lieu canonique, date et heure. Le site officiel prime
sur l’agrégateur, et les deux preuves sont conservées. Une correction d’horaire
sur une fiche identifiée peut remplacer l’ancienne occurrence. Les identifiants
de séries ne remplacent pas ceux des occurrences. Les salles différentes et
les séances à des heures différentes restent distinctes.

Un cas réel a été contrôlé : **AMOR x NAVA, au Romandie le 16 octobre à 23 h**,
présent sur le site officiel et Lausanne Tourisme, ne produit qu’une occurrence.
Le rapprochement de titres différents reste à examiner ; il n’existe pas de
fusion approximative susceptible de réunir deux soirées distinctes.

**6. Fiabiliser les mises à jour.** Les sources sont interrogées avec une
concurrence limitée. Une source défaillante n’arrête pas les autres. Un verrou
SQLite renouvelé pendant le travail évite des collectes simultanées entre les
processus Flask et le programme de collecte. Les entrées non revérifiées depuis
plus de 24 heures ne sont plus affichées. Pour un calendrier Hango intégralement
parcouru, une disparition est prise en compte après deux lectures complètes
réussies ; une panne ou une pagination incomplète ne déclenche pas ce retrait.
Une disparition n’est pas présentée comme une annulation confirmée.

## Résultat mesuré localement

| Indicateur | Résultat |
|---|---:|
| Canaux activés dans la configuration | 26 |
| Canaux qualifiés pour une automatisation conditionnelle | 10 |
| Sorties affichables lors du contrôle Flask | 70 |
| Concerts | 38 |
| Soirées et clubs | 21 |
| Séances de cinéma | 10 |
| Scène / humour | 1 |
| Tests automatiques sans réseau réussis | 51 |
| Routes Flask contrôlées avec réponse HTTP 200 | 5 |

Ces nombres sont un instantané, pas une promesse de volume quotidien. Les 26
canaux ne sont pas tous opérationnels : 10 demandent encore un adaptateur,
un canal de programme a échoué, et le calendrier des Gosses du Québec n’a pas
fourni d’occurrence future lors de cette lecture. Cela ne signifie pas que le
bar est fermé. Les canaux qui livrent des entrées peuvent aussi contenir des
archives ou des cas à vérifier.

Le programme observé est actuellement centré sur Lausanne. Les communes voisines
sont admises par le moteur, mais leurs collecteurs restent à étendre et qualifier.

Les cinq routes contrôlées sont l’accueil, les événements, les catégories,
le diagnostic des sources et l’état du service. Le programme testé utilise
les données réellement collectées, sans démonstration fictive. Les feuilles de
style et les modèles HTML sont inchangés ; seuls les libellés nécessaires pour
identifier les heures de portes ont été précisés dans le JavaScript existant.

## Ce qui reste incomplet

- **MAD, Folklor, Bleu Lézard, Satellite et Boulimie :** adapter leurs programmes
  actuels. La présence de titres dans une page ne suffit pas à fabriquer des événements.
- **Bruxelles, Datcha et Captain Cook :** compléter et qualifier les horaires,
  catégories, années et lieux, en conservant les cas hors-les-murs.
- **Sous-Gare :** approfondir Montriond, Hungry Bear, Ta Cave et Café du Simplon.
  Des canaux existent, mais tous ne fournissent pas encore des sorties nocturnes
  datées exploitables. Les autres villes publiées par Ta Cave ne sont pas importées
  comme des événements lausannois.
- **Château Music Club :** le lien PROGRAMME officiel testé renvoie HTTP 404.
  Le lieu n’est pas déclaré fermé ; le canal est à réparer ou à remplacer sur preuve.
- **Barberousse :** les données structurées du site contiennent encore des dates
  de 2025. Des événements actuels peuvent être obtenus via les agendas, sous contrôle.
- **L’Agenda :** ses filtres et son programme doivent être adaptés. La page
  générale consultée commence par des expositions longues et ne définit pas notre flux.
  La documentation Guidle est conservée comme documentation, désactivée comme collecteur.

La comparaison de couverture porte uniquement sur les données effectivement
récupérées. Le contrôle Lausanne Tourisme est limité à 16 fiches par passage de
validation ; les listes peuvent être paginées. Le relevé contient une occurrence
retrouvée des deux côtés, 67 relevées uniquement du côté officiel et 2 uniquement
via l’agrégateur. **Cela ne démontre pas que 67 événements sont absents des agendas.**
Ce n’est ni une recherche exhaustive ni un taux de couverture global.

## Fonctionnement et limites à connaître

L’application conserve le déclenchement existant : une consultation lance une
collecte en arrière-plan lorsque la dernière tentative a plus d’une heure.
La commande ci-dessous permet aussi une collecte indépendante. Aucun cron ni
nouveau service Render n’a été installé. Une planification indépendante du
trafic reste à configurer au moment de préparer l’exploitation.

« Ce soir » couvre 17 h–6 h, avec rattachement à la soirée précédente avant 6 h.
Les occurrences recherchées sont dans les 28 prochains jours. Une sortie déjà
commencée sans heure de fin connue est masquée par prudence ; aucune durée n’est
supposée. Les longs festivals doivent être décomposés en véritables soirées.
Les récurrences iCalendar complexes ne sont pas encore qualifiées.

Le suivi des disparitions est activé uniquement lorsqu’un lecteur peut affirmer
avoir parcouru un calendrier complet. Pour les autres sources, une absence
ponctuelle ne vaut pas annulation ; l’expiration après 24 heures constitue le
filet de sécurité. Les entrées signalées complètes conservent cette information
technique, mais un indicateur visuel « complet » reste à ajouter si souhaité.

## Essai local et prochaine étape

```bash
python -m venv .venv
.venv/bin/pip install -r requirements.txt
export LAUSANNE_DB="$PWD/preview.db"
.venv/bin/python collection_cli.py collect
.venv/bin/python app.py
```

Puis ouvrir `http://localhost:5000`. La collecte doit être exécutée pour remplir
la base locale ; l’archive de code ne contient pas une base d’événements préchargée.

Pour le diagnostic :

```bash
.venv/bin/python collection_cli.py sources
.venv/bin/python collection_cli.py report
.venv/bin/python -m unittest discover tests
```

La priorité suivante est de qualifier les programmes manquants des clubs et bars,
puis de préparer la planification régulière et une prévisualisation de l’application
avec sa base fraîche. **Aucune mise en production ne sera faite sans autorisation
explicite.** Le code n’a pas été envoyé sur une branche GitHub distante.

Les résultats détaillés et les URL de contrôle sont dans
`diagnostic_collecte_v2.json` et `validation_locale_v2.json`.
