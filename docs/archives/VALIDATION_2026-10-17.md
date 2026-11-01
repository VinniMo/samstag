# Samstag — bilan du 17 octobre 2026

> **Archive historique du 17 octobre 2026.** Cette campagne reste une preuve datée et ne décrit pas l’état courant. Voir [ETAT_ACTUEL.md](../ETAT_ACTUEL.md).

**Bilan de la première phase.** Pour l’état courant (383 événements, qualification de La Grange/Vidy/Château et préparation du lancement commun), lire [QUALIFICATION_ET_MISE_EN_SERVICE.md](QUALIFICATION_ET_MISE_EN_SERVICE.md).

## Résultat pour le projet

Les corrections sont locales. Deux collectes successives donnent le même résultat : **1 084 observations distinctes et 306 événements visibles selon les règles de qualification**, sans ajout de doublons à la seconde passe. Ce résultat n’est pas une revue humaine exhaustive de tous les événements issus des anciens canaux automatisés.

**74 tests réussis.** Les routes du site répondent, le mode fictif est désactivé, une sauvegarde SQLite a été restaurée et contrôlée. Les événements non revérifiés disparaissent après 24 heures. Deux processus ne peuvent pas lancer une collecte simultanée ; le verrou est libéré ensuite. La reprise après exception reste couverte par les tests.

Les 37 sources actives ont été contrôlées : 24 états techniques `ok`, 2 calendriers vides, 6 lectures partielles et 5 sources sans programme daté raccordé. Aucun échec complet de source lors des deux passes finales. Le bilan global reste **dégradé**, car ces limites ne sont pas résolues. Un état `ok` ne garantit pas la publication de chaque annonce.

## Corrections et qualification

| Lieu / source | Résultat vérifié | Publication |
|---|---|---|
| La Grange | Horaires et lieu lus dans les blocs séparés ; doublons mobile/ordinateur supprimés ; programme annoncé parcouru ; 20 séances extraites. | En revue : commune physique du campus à confirmer. Aucune commune déduite de l’adresse postale. |
| Pulloff | Périodes dans un même mois reconnues ; 4 relâches exceptionnelles du 10 au 13 novembre retirées de John G. Picture ; horaires séparés de l’exposition extérieure. Adresse corrigée : **Rue de l’Industrie 10**, et non l’administration Rue de la Barre 14. | Automatisation qualifiée pour les séances de théâtre complètes : 20 événements futurs dans l’horizon. Année à deux chiffres laissée en revue. |
| L’Agenda | Limite de pagination rendue configurable, portée de 4 à 20 pages par région ; navigation terminée après 8 pages au total ; 167 observations. | Règles conservées ; sélection par catégories et régions, pas une garantie d’exhaustivité générale. |
| Brasserie du Château / Château Music Club | Même établissement, identifiant conservé ; le lien programme officiel est toujours en 404. Canal public Hango raccordé : 5 soirées datées, heure locale et adresse recoupées avec les fiches. | 5 candidates, pas d’automatisation ; source explicitement classée comme agrégateur. |
| Vidy | Calendrier public JSON lu sans exécuter de JavaScript ; 185 occurrences. Les salles de Vidy sont distinguées des lieux extérieurs, notamment Genève ; un minuit générique reste non vérifié. | 68 candidates, pas d’automatisation ; sélection annoncée, donc état partiel. |
| Bleu Lézard | Variante `www` accessible ; message officiel « aucun événement » reconnu. Aucun PDF 2025 recyclé. | Vide ; aucune conclusion sur la fermeture du lieu. |
| Holy Monkey | 3 annonces extraites avec preuve ; dates sans année et heures absentes. | En revue, sans déduire d’horaires des heures d’ouverture. |
| Hungry Bear | 2 annonces extraites, dont tournoi du 18/10/2026 sans heure. | En revue ; type culturel et horaire insuffisants. |
| Lausanne Tourisme | 40 fiches lues sur 1 193 liens repérés, zéro erreur de fiche sur ces passes. | Partiel, limite explicite conservée ; aucun contournement du filtre précédemment bloqué. |
| MAD | 16 fiches lues ; 2 anciens liens du 16 octobre en 404. | Partiel, événements valides conservés ; une absence partielle ne retire rien. |

Les 104 occurrences Pulloff comprennent les anciennes séances et les spectacles lointains : seuls 20 événements entrent actuellement dans la publication. Les dates lointaines restent soumises à l’horizon de 90 jours. La validation de John G. Picture et Music-hall repose sur les périodes et horaires explicitement publiés, après retrait des relâches.

## Bars demandés et exclusion

- **Satellite retiré**, à la demande de l’utilisateur : canal désactivé, lieu hors sélection, événements invisibles même s’ils arrivent par un agrégateur. Le registre conserve une trace d’exclusion pour éviter sa réintroduction. Aucun nouvel appel à ce canal après la demande.
- **The Great Escape** : déjà inventorié, maintenant relié à son site officiel et à son adresse confirmée, Rue de la Madeleine 18. Le site consulté publie essentiellement des retransmissions sportives ; pas de programme culturel complet qualifié. Aucune séance créée à partir des jours incomplets.
- **Le Pavillon / Pavillon Bar & Kitchen** : ajouté à Place de la Riponne 10, distinct du Pavillon Naftule et du Pavillon de Vidy. Le site annonce des DJ sets récurrents sans séances individuelles datées ni heure de début vérifiable ; les émissions radio de 2018 ne sont pas un programme actuel.
- **La Bossette** : ajoutée à Place du Nord 4, site actuel `bo7.ch` contrôlé ; pas de programme daté trouvé. Ancien domaine `bossette.ch` en 403, sans contournement.
- **Brasserie du Château** : nom rendu explicite dans le registre ; aucun doublon de lieu créé.

Le registre compte désormais 159 entités et 39 descripteurs de sources, dont 37 actifs. Ces nombres ne mesurent pas les collecteurs qualifiés. Les nouveaux bars restent sans publication automatique.

## Revue des autres bars demandés dans la feuille de route

- **La Datcha** : annonces toujours en revue. Une fiche détaillée du concert Louis Jucker précise Château-d’Œx ; elle ne doit pas hériter de l’adresse lausannoise du producteur. Les dates sans année restent non qualifiées.
- **Captain Cook** : calendrier public lisible ; plusieurs annonces mêlent offre commerciale et début non vérifié. Les 12 observations ne sont pas une couverture publiée ; 9 en revue, 3 exclues.
- **Bruxelles Café** : 9 articles récupérés ; dates/heures et qualification insuffisantes pour l’automatisation.
- **Barberousse** : 7 données structurées archivées en 2025, insuffisantes pour publier un programme actuel.
- **Ta Cave** : les étiquettes « Lausanne » ne prouvent pas le lieu réel ; fiches visibles à Bâle, Ascona et Aran. Aucune nouvelle automatisation.
- **Simplon** : page et fichier JavaScript public inspectés ; réservations et privatisations ne constituent pas un programme d’événements datés.
- **Montriond** : lien `/home` accessible, coordonnées présentes, sans programme daté exploitable.

Simplon et Montriond restent à raccorder, tout comme les trois bars nouvellement enregistrés. Un lecteur ne peut pas remplacer des dates ou des horaires que le site ne publie pas. Instagram demeure reporté.

## Preuves et reproduction

Dans `validation/2026-10-17/` :

- `pass-1.json` et `pass-1-fetches.json` : diagnostic intermédiaire avant correction des relâches Pulloff, pas le bilan final.
- `final-1.json` et `final-2.json` : passes finales de 28,68 et 28,58 secondes ; mêmes comptes et décisions.
- `final-1-fetches.json`, `final-2-fetches.json` : URL, heure de lecture, fichier et empreinte des réponses publiques ; instantanés séparés par passe.
- `collecte-finale.sqlite3` : base finale locale ; `restauration.sqlite3` : restauration vérifiée, intégrité `ok` et 1 084 éléments.
- `verification.json` : répétition, protection contre la concurrence entre processus, reprise du verrou, fraîcheur, réponses HTTP et absence de Satellite.
- `tests.log` : résultat de la suite finale.

La collecte initiale `collecte.sqlite3` est un diagnostic avant les dernières corrections ; ne pas l’utiliser comme base finale. Les scripts de validation ne sont pas des services permanents.

## Ce qui reste avant une mise en ligne

La préparation et les contraintes d’hébergement sont dans [EXPLOITATION.md](../EXPLOITATION.md). Le fichier SQLite doit être persistant et partagé entre le site et le processus de collecte. La configuration Render gratuite du dépôt ne fournit pas cette garantie ; la configuration réelle du compte n’a pas été inspectée.

**Aucun push GitHub, déploiement Render, changement de plan ou service permanent effectué.** Il reste à choisir l’hébergement, tester la supervision adaptée, obtenir l’accord explicite avant mise en production puis observer les mises à jour sur 24 heures. Les deux passes rapprochées et les tests simulés ne démontrent pas une stabilité sur plusieurs jours.
