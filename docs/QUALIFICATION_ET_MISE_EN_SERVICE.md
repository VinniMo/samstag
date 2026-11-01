# Samstag — qualification et préparation de mise en service

État du 17 octobre 2026, après le premier bilan de corrections locales.

## Résultat

La base locale contient **383 événements retenus**, issus de 1 084 observations : 383 approuvées, 235 exclues et 466 en revue. Cela ne signifie pas que tous les anciens canaux automatiques ont été revus intégralement à la main.

Le lot de qualification est terminé pour les événements admissibles des trois sources prioritaires :

| Source | Sorties retenues | Contrôles supplémentaires |
|---|---:|---|
| La Grange | 13 | Commune d’Écublens prouvée ; séances précises au lieu La Grange ; ateliers et séances diurnes exclus. Six séances de janvier sont au-delà de l’horizon courant de 90 jours. |
| Vidy | 59 | Toutes les séances retenues recoupées avec leur fiche officielle : date et salle exactes. Ateliers, rencontres, visites, horaires inconnus et lieux non confirmés restent hors automatisation. |
| Brasserie du Château / Château Music Club | 5 | Chaque fiche publique Hango porte exactement l’identité du lieu configuré, avec date, heure, adresse et type DJ set. Les recommandations d’autres lieux sont rejetées. |

Ces 77 sorties s’ajoutent aux 306 retenues dans la phase précédente. La publication automatique locale de ces trois canaux est limitée aux types vérifiés et aux événements complets. Aucune publication externe n’a eu lieu.

## Preuve de la commune de La Grange

Le tableau cantonal « APE par bâtiment pour la première phase du programme (4 ans) », page PDF 51 / page imprimée 15, donne explicitement **Grange de Dorigny — Ecublens**. Le document a été lu et le tableau inspecté visuellement. [Source cantonale](https://www.vd.ch/fileadmin/user_upload/organisation/gc/Compil_OJ_GC/compil_oj_gc_22jan19.pdf).

Le registre et les événements utilisent maintenant la commune physique Écublens. L’adresse postale 1015 Lausanne est conservée en tant qu’adresse postale. La preuve, l’empreinte du PDF et l’image du tableau sont sauvegardées localement.

## Vidy : qualification de la nature des événements et des séances

La revue des 185 occurrences a mis en évidence des ateliers « Tuesday is Danceday » étiquetés Danse et des rencontres avec les artistes étiquetées Théâtre. Ces étiquettes ne suffisent pas à en faire un spectacle.

Le lecteur distingue maintenant les ateliers, rencontres, lectures, podcasts et expositions des séances de théâtre, danse, musique et cinéma retenues. Une projection avec plusieurs étiquettes, dont Film, est classée en cinéma plutôt qu’en théâtre. Les séances admissibles sont ensuite comparées à la section officielle « Dates et horaires » de leur fiche. Une séance unique peut être confirmée par son en-tête si celui-ci donne explicitement un jour, un mois, une année, une heure et une salle ; une simple plage de dates ne suffit pas.

Lors de l’essai final : **21 fiches sur 21 lues, zéro erreur de fiche**, 59 événements retenus. Un échec ou une divergence de fiche garde l’événement en revue. L’absence dans le calendrier partiel ne provoque aucun retrait automatique.

## Fonctionnement permanent préparé et essayé localement

Le nouveau point d’entrée `run_service.py` lance le site et sa collecte dans deux processus surveillés utilisant le même fichier SQLite. Il exige un chemin de base explicite et absolu, désactive le mode fictif, le mode debug et les collectes déclenchées par une visite. Une interruption inattendue d’un processus arrête l’autre pour permettre le redémarrage par l’hébergeur.

L’essai réel a lancé le site et une collecte de 37 sources, puis vérifié les quatre routes principales, le mode réel, l’absence de Satellite et l’arrêt des processus. Résultat : 383 événements exposés par l’API, intégrité SQLite `ok`, aucun verrou restant après arrêt, port fermé, sortie normale du superviseur. Durée totale de l’essai : 30,35 secondes ; la collecte elle-même a duré 28,56 secondes.

**85 tests réussis avec Python 3.9 et la même suite de 85 tests réussie avec Python 3.12.14.** Les tests incluent le rejet des mauvaises identités de lieu, le changement d’heure du Château, les désaccords de séances Vidy, la panne d’un lecteur, l’arrêt d’un processus frère et l’arrêt demandé des deux processus. Les imports et réglages du lancement Gunicorn passent aussi sous Python 3.12.14.

L’essai du site en écoute locale a utilisé Python 3.9 ; la suite complète et les contrôles d’import sous Python 3.12.14 ne remplacent pas un essai de production Linux. Aucune exploitation sur 24 heures ni résistance à une charge publique n’est démontrée.

## Limites de couverture maintenues

Satellite reste exclu, y compris par les agrégateurs. Instagram reste reporté ; Buzz Club et les bibliothèques restent exclus.

Great Escape, Pavillon Bar & Kitchen et Bossette sont bien enregistrés, mais les sites consultés ne fournissent pas de programme culturel daté complet exploitable. Simplon et Montriond restent dans la même situation. Les annonces insuffisantes des autres bars restent en revue ; aucun début de soirée n’est inventé à partir d’heures d’ouverture.

La santé de la collecte reste dégradée : 24 sources techniquement `ok`, 2 calendriers vides, 6 sources partielles et 5 sans programme raccordé. Les sources partielles incluent des sélections qualifiées comme Vidy et Hango, ainsi que Lausanne Tourisme et les deux vieux liens MAD en 404. Qualification d’événements et exhaustivité d’un programme sont distinctes.

## Proposition d’hébergement et action nécessaire

La proposition détaillée est dans [deploy/README.md](../deploy/README.md) : conserver Render, avec un seul service toujours actif et un disque persistant de 1 Go. Base tarifaire publique relevée le 17 octobre : **7 USD de calcul + 0,25 USD de disque = 7,25 USD/mois**, hors taxes, conversion, autres services et dépassements. [Tarifs Render](https://render.com/pricing).

Le code et les réglages proposés sont préparés. Le fichier `render.yaml` historique n’a pas été modifié ; aucun abonnement, push GitHub ou déploiement n’a été effectué.

L’accès Render a été relié pendant la session et vérifié par des lectures réussies. Le service réel `samstag` est sur la formule gratuite, région Oregon, une instance, relié au dépôt `VinniMo/samstag`, branche `main`, avec déploiement automatique sur commit. La version en ligne est encore le commit `759326d0fc36dfb6e7b2208c3fff07182a785ba1` du 12 octobre. Les corrections locales ne sont pas déployées. Ne pas pousser sur `main` avant accord, puisque cela déclencherait une mise en ligne.

Le relevé est dans `render-inspection.json`. Les secrets et le contenu de la base distante n’ont pas été lus. L’activation payante, le stockage durable et la mise en ligne restent soumis à l’accord explicite de l’utilisateur ; aucune action Render de modification n’a été appelée.

Ensuite seulement : sauvegarder l’existant, publier une version identifiable, appliquer les réglages approuvés et surveiller les mises à jour pendant 24 heures. Le choix d’un disque persistant ne remplace pas une sauvegarde régulière hors du service.

## Preuves et continuité

Dans `validation/qualification-2026-10-17/` :

- `rapport-final.json` : état final, compteurs, types, preuve géographique et budget indicatif.
- `collecte-qualifiee.sqlite3` : copie cohérente de l’essai final ; `restauration-qualifiee.sqlite3` : restauration contrôlée.
- `service-test.json`, `service-test.log` : essai réel des deux processus, collecte complète et arrêt.
- `qualification-1.json` et ses réponses HTML : diagnostic initial à 382 événements, avant prise en charge de la fiche Vidy à horaire dans l’en-tête. Il n’est pas la référence finale.
- `fetches.json`, réponses HTML et `qualification-1-fetches.json` : preuves des pages lues.
- `canton-vd-22jan19.pdf`, `canton-page-051.png` : preuve de la commune de La Grange.
- `tests.log`, `tests-python312.log` : suites finales de 85 tests par environnement.

Le candidat sauvegardé après cette qualification est distinct de l’archive de la phase précédente. Les pages, polices et fichiers de design restent identiques à l’archive applicative originale.
