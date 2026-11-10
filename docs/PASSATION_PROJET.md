# Lausanne Samstag — dossier de reprise

## 1er novembre 2026 — bilan demandé des collecteurs
- Lecture des registres, du worker et de l’audit existant, sans relancer les sources ni accéder au VPS. Bilan communiqué : 39 canaux configurés, 37 actifs, 24 autorisés à publier sous conditions ; cinq canaux actifs sans adaptateur ne constituent pas des collecteurs opérationnels.
- Fréquence versionnée : passe immédiate au démarrage, puis attente de 3 600 secondes après chaque passe ; rythme commun aux sources actives. Configuration réellement installée non revérifiée par SSH.
- Couverture jugée utile pour une bêta, mais exhaustivité non démontrée : 322 sorties et 19 lieux dans l’instantané public de l’audit ; lacunes bars, cinéma et sources partielles/en erreur. Aucun changement applicatif ou distant.

**Journal chronologique mis à jour le 1er novembre 2026.** L’état courant, la prochaine tâche et les limites vérifiées se trouvent dans [ETAT_ACTUEL.md](ETAT_ACTUEL.md). Le site public de référence est [samstagloz.ch](https://samstagloz.ch), servi par l’application Flask sur le VPS Infomaniak.

Les sections suivantes conservent l’historique depuis le 16 octobre. Leurs mentions de domaine non choisi, de service interne, de branches, de compteurs ou de travaux à faire restent des faits datés et ne doivent pas être interprétées comme l’état actuel.

## Archive chronologique

## Objectif et décisions à conserver

Agenda lausannois rapide, simple et régulièrement actualisé : concerts, clubs, soirées de bars, spectacles et cinéma, à Lausanne et dans les communes immédiatement voisines. Les bars complètent une base culturelle large. Priorité aux bars du centre et de Sous-Gare. Plusieurs temporalités : ce soir, ce week-end, la semaine prochaine et sorties futures. L’expression « ce soir » ne limite pas la collecte à la journée.

Instagram est reporté à une phase ultérieure. Ne pas inventer des événements à partir des heures d’ouverture. Exclure Buzz Club, les bibliothèques et les annonces de location de salles sans véritable programmation publique. Préserver le design existant. Conserver les preuves et distinguer lieux, salles physiques, organisateurs et agrégateurs.

**Ne jamais modifier ni déployer le site Render en production sans autorisation explicite.** Aucun déploiement ni envoi GitHub n’a été effectué dans ce travail.

L’utilisateur souhaite des sessions courtes et ciblées, avec un récapitulatif clair des changements et des points réellement vérifiés. Éviter les longues recherches autonomes sans objectif de session borné.

## Dépôt et récupération

- Dépôt : https://github.com/VinniMo/samstag
- Branche locale : `codex/nightlife-collectors`.
- Dernier commit local avant les travaux inachevés : `248e641`.
- L’autre dépôt `VinniMo/lausanne-events` correspond à une autre application : ne pas le substituer.
- Les modifications les plus récentes sont **non commitées et non envoyées sur GitHub**. Elles sont incluses dans l’archive de reprise. Un simple clonage GitHub ne permet pas de les récupérer.
- Extraire `samstag/` de l’archive pour retrouver le code courant. Les anciens chemins du bac de travail ne sont pas garantis dans une nouvelle session.
- `reprise/collection-v3-partielle.sqlite3` est une copie cohérente de la base locale, issue d’essais partiels. Ce n’est pas une base de production ni la preuve d’une collecte finale réussie.

## Dernière version validée et travaux en cours

### Version v2, avant l’élargissement

Le récapitulatif historique `docs/archives/RECAP_COLLECTE.md` et les diagnostics v2 décrivent la version précédente : 51 tests, 70 événements lors de son contrôle local, 10 canaux qualifiés. Les neuf lieux alimentés alors étaient Docks, Jumeaux, Chorus, Bellevaux, D! Club, Romandie (soirées DJ), Taco’s, Étoile Blanche et Satellite (via Lausanne Tourisme). Le calendrier des Gosses du Québec était lisible mais vide. Ces chiffres sont historiques, pas une mesure actuelle ou exhaustive.

Le moteur possède déjà une validation des dates/heures/lieux, des preuves par source, une préférence officielle sur agrégateur, un dédoublonnage exact et un verrou SQLite partagé. Les événements incomplets restent en revue. Les événements non revérifiés depuis plus de 24 heures sont masqués. Les disparitions ne sont traitées que dans les calendriers complets qualifiés.

### Élargissement v3, arrêté en cours

Fichiers principaux : `expanded_adapters.py`, `collection_worker.py`, `collection_health.py`, `tests/test_expanded_adapters.py`, et modifications de Flask, SQLite, du scraper, de la qualité, de la configuration et des registres.

Lecteurs ajoutés ou en cours : Folklor, billetterie du MAD liée depuis son agenda, La Brèche, CityClub Pully, Boulimie, Naftule, Oblò, JazzOnze+, calendrier public Arsenic, recherche filtrée de L’Agenda, La Grange et Pulloff.

La configuration contient 36 descripteurs de sources, dont un descripteur Guidle désactivé, et 20 drapeaux de publication automatique. **Ce sont des réglages provisoires du chantier : ne pas les présenter comme 20 collecteurs définitivement validés.** La Grange et Pulloff ont été ajoutés au lecteur après la dernière campagne de tests ; leur publication automatique reste désactivée dans le registre.

Une campagne de 58 tests est passée AVANT les dernières modifications. Les changements ultérieurs — santé des sources, statut partiel, ajustements MAD, Grange et Pulloff notamment — n’ont pas subi de validation finale. La collecte complète lancée durant ce chantier n’a pas produit de rapport final exploitable avant l’arrêt. Aucun total final v3 n’est annoncé.

Le nouvel horizon configurable est de 90 jours (`COLLECTION_HORIZON_DAYS`), au lieu de 28. Le worker indépendant des visites est préparé, mais aucun service régulier de production n’a été installé.

Le registre est passé de 154 à 157 entités : ajout de trois espaces physiques indiqués par le programme officiel JazzOnze+ (BCV Concert Hall, Atrium et Auditorium de l’EJMA). Salle Paderewski a été retenue pour ses concerts publics explicitement programmés ; cela ne réintroduit pas les annonces de location de salles. Les nouveaux espaces ne sont pas géocodés. Les classeurs historiques ne reflètent pas encore toutes ces modifications.

## Résultats documentaires et difficultés concrètes

- Folklor : huit soirées datées avec horaires explicitement publiés lors du contrôle.
- MAD : agenda et billetterie officiels accessibles. Les heures sont des portes et doivent être étiquetées. Des dates divergent entre agenda et billetterie (ex. Equis X) ; le code récent les met en revue. Vérifier également l’identification Jetlag et ne pas importer les manifestations hors Lausanne du groupe MAD.
- CityClub : programme mensuel avec séances distinctes et identifiants de billetterie. Vérifier les changements de mois/année et les soirées combinant film et concert.
- Boulimie : certaines séances se déduisent d’une plage datée et d’horaires de jours de semaine explicitement publiés. Le Boulimy Comedy Jeudy se déroule à Jumeaux, pas à Boulimie : pas d’adresse héritée du producteur.
- Naftule : dates civiles et horaires présents dans le calendrier HTML. Ne pas transformer une page de série en identifiant unique de séance.
- Arsenic : calendrier JSON public dans `var spectacles`, à lire sans exécuter le JavaScript. Certains spectacles n’ont pas de catégorie exploitable et restent en revue.
- L’Agenda : formulaire public exploitable avec catégories et régions. Pagination bornée ; ne pas prétendre à l’exhaustivité. Les périodes « divers horaires » ne suffisent pas pour publier une séance.
- JazzOnze+ : programme multi-lieux précis. Les heures « 00h » rattachées à la soirée précédente sont laissées en revue jusqu’à vérification de la date civile. Une annulation explicite figure dans le programme et doit rester exclue.
- Datcha : détails utiles, mais année et lieu à qualifier ; certaines soirées sont à Château-d’Oex, hors périmètre.
- Bleu Lézard : aucune occurrence affichée par le programme consulté ; ne pas reprendre le PDF 2025 comme agenda actuel.
- Barberousse : données structurées archivées en 2025 ; pas de qualification actuelle sur cette seule base.
- Château Music Club : ancien lien programme HTTP 404 ; rechercher un autre canal officiel sans déclarer le lieu fermé.
- Lapin Vert : site officiel indiquant que l’information est sur Instagram ; phase reportée.
- Montriond : site en construction lors de la consultation.
- King Size : ancien lien music-live HTTP 404 ; accueil accessible, pas de programmation datée constatée.
- Holy Monkey, Bruxelles, Captain Cook, Hungry Bear, Ta Cave et Simplon : recherches inachevées, insuffisances variables de dates, heures, localisation ou programme actuel. Ne pas les considérer comme couverts.
- Lausanne Tourisme : collecteur v2 fonctionnel, couverture limitée aux fiches parcourues. Son endpoint de filtre public a renvoyé HTTP 403 au dernier essai : ne pas contourner ce blocage.

## Prochaines sessions proposées

1. **Stabilisation v3 uniquement.** Lire les changements non validés, exécuter les tests, corriger les défauts et qualifier/désactiver chaque nouveau lecteur. Ne pas lancer de nouvelle recherche large.
2. **Mesure de couverture.** Une seule collecte locale sur une base isolée ; tableau par lieu : données directes, données via agenda, aucun résultat, panne, à raccorder. Ne pas confondre inventaire et couverture réelle.
3. **Exploitation.** Tester le worker, la reprise après panne, la fraîcheur et les erreurs partielles ; préparer une procédure d’installation sans déployer.
4. **Collecteurs restants par petits lots.** Prioriser les bars centre/Sous-Gare et les grands lieux encore absents ; chercher des solutions vérifiables. Instagram reste séparé.
5. **Revue puis autorisation explicite avant toute mise en production.**

## Commandes de reprise locale

Créer un environnement virtuel neuf si les anciens liens Python ne fonctionnent plus.

```bash
python3 -m venv .venv
.venv/bin/pip install -r requirements.txt
.venv/bin/python -m unittest discover tests
```

Utiliser ensuite un chemin de base LOCAL explicite avec `SAMSTAG_DB` : `collection_cli.py collect`, éventuellement `--source SRC_L005`, puis `collection_cli.py report`. Ne pas relancer tous les sites pour une simple question de statut. Les états déjà sauvegardés doivent être lus d’abord.

`collection_worker.py --once` est prévu pour une passe supervisée et `collection_worker.py --interval 3600` pour une boucle locale ; ce code récent doit encore être validé. Le worker et Flask doivent lire le même fichier SQLite pour partager le verrou et les données.

## Message à utiliser dans une nouvelle session

« Reprends Lausanne Samstag. Lis d’abord PASSATION_PROJET.md dans les sources du projet et le code de l’archive de reprise. Pour cette session, limite-toi à [objectif précis]. Conserve le design. Ne déploie rien sur Render. Termine par les changements faits, les vérifications et les limites ; actualise la passation. »

## Reprise locale du 16 octobre 2026

Voir `VALIDATION_COLLECTE_V3.md` pour les corrections, résultats et limites actuels. La passe isolée a produit 794 observations et 290 événements publics selon les règles configurées. Aucun déploiement. Les drapeaux automatiques restent provisoires ; Grange et Pulloff restent désactivés pour publication automatique. Le rapport JSON précède la dernière correction du lecteur générique de pages de détail.


## 18 octobre 2026 — cartes compactes et liens directs

- Demande utilisateur appliquée : sous le titre, extrait de la sous-catégorie ou de la description existante, limité à 110 caractères et une ligne visuelle. Aucun enrichissement inventé ; lieu, horaire, date groupée et prix connus conservés.
- Liste et affiches ouvrent directement le lien HTTP(S) collecté dans un nouvel onglet (page source ou billetterie) ; aucune fiche intermédiaire pour ces cartes. Sans lien valide, événement non cliquable.
- Modification limitée à static/js/main.js et static/css/style.css, appliquée sur le VPS interne sans redémarrage ni changement de base. Copie préalable dans /opt/samstag/ui-backup-20261018/. Aucun changement Render, DNS, Nginx ou immobilier.
- Syntaxe JavaScript vérifiée. Aperçu réel contrôlé à 390 et 1100 px : liens directs présents, extraits visibles, aucun débordement horizontal sur la vue Ce soir. Détecteur visuel : avis sur styles préexistants. Pas de nouvelle suite backend pour ces seuls fichiers statiques.
- Limite : description absente pour une partie des événements ; aucune nouvelle collecte de détails réalisée. Publication publique et observation 24 h restent à faire.


## 18 octobre 2026 — rythme visuel de la liste
- Compteurs supprimés des rubriques uniquement ; compteurs temporels conservés. Espacement accru avant les catégories, heures moins grasses, survol/focus rose pâle avec flèche de lien.
- Appliqué aux deux fichiers statiques sur le VPS interne après sauvegarde dans /opt/samstag/ui-backup-20261018-rythme/. Liens directs et base préservés.
- Syntaxe JavaScript vérifiée, compteurs absents et liens présents vérifiés dans le navigateur ; vues mobile et ordinateur inspectées. Aucun changement aux collecteurs ou à la publication publique.


## 18 octobre 2026 — couleurs fixes et fin du survol rose
- Couleurs par nom de rubrique, indépendantes de leur ordre : Concerts magenta #a3004f, Soirées & clubs noir/jaune, Scène jaune/noir, Cinéma bleu #244bc0, Expos vert #176449, Autres orange #f5a54b. Identité commune aux étiquettes et choix Mes goûts sélectionnés. Décision utilisateur : conserver l’esprit programme/affiche imprimé, couleurs franches.
- Survol rose supprimé : sur pointeur, fond papier neutre, titre souligné et flèche noire. Le survol de fond est désactivé pour les appareils sans survol ; focus clavier conservé. Compteurs de catégories toujours supprimés, liens directs préservés.
- Deux fichiers statiques appliqués sur VPS interne ; sauvegarde précédente /opt/samstag/ui-backup-20261018-couleurs/. Syntaxe JS contrôlée ; navigateur : Concerts magenta et Cinéma bleu confirmés, trois liens directs, aucun compteur de rubrique ni débordement dans la vue courante. Aucun changement de base ou de publication.


## 18 octobre 2026 — correction des liens Lausanne Tourisme pour lieux couverts
- Diagnostic réel dans la base VPS : concert LUM x Pat Burgener collecté officiellement mais en revue (`doors_not_artistic_start`), titre officiel enrichi des artistes différent du titre LT ; la fiche LT était approuvée indépendamment. Le lieu D! est correctement reconnu ; le fragment d-club-live n’est PAS la cause du rejet.
- Correction LOCALE : `collection_quality.py` bloque toute destination/provenance LT pour les lieux ayant un canal officiel activé, à la collecte et lors de la revalidation des anciennes approbations. Motif interne `official_source_required_for_covered_venue` ; aucune suppression de preuve ni fusion approximative.
- `venue_adapters.py` lit les détails officiels des concerts D! dans la limite des pages configurée. Pour l’inscription Swoogo liée officiellement, vérifie le lieu, le jour/mois et tous les artistes, puis n’accepte qu’une heure artistique explicite unique. Sans confirmation ou en panne : concert reste en revue, pas de remplacement LT. Le titre officiel des concerts n’est plus suffixé artificiellement avec les artistes ; titres club préservés.
- Concert concerné : date officielle 20 octobre 2026 ; portes 20 h, concert 20 h 30, gratuit sur inscription. Page D! et inscription officielle sauvegardées dans `validation/official-links-2026-10-18/`. Tarif 20 CHF de LT non repris.
- 88 tests locaux réussis, dont trois nouvelles régressions : blocage d’une ancienne approbation LT même avec titre différent, destination LT masquée sous source officielle, confirmation artistique avec refus de mauvaises identités/horaires ambigus/panne.
- Audit VPS en lecture seule : 2 fiches publiques concernées par la règle (D! Club et Jumeaux Jazz Club). L’événement Jumeaux reste à rapprocher de sa source officielle ; aucune affirmation de correction de sa collecte.
- NON APPLIQUÉ AU VPS : transfert des deux modules et du test refusé par le contrôle automatique, qui exige une autorisation explicite de l’utilisateur pour exporter le code vers ubuntu@179.237.81.208, même après vérification SSH du service Samstag existant. Aucun fichier distant modifié, aucun redémarrage, aucune base distante changée. Archive locale prête `/tmp/samstag-official-links-fix.tar.gz`.
- Suite après autorisation : sauvegarder les modules et la base sur le VPS, appliquer les fichiers, exécuter les tests sur place, relancer uniquement Samstag et collecter D! ; requalifier les anciennes fiches LT en revue, puis vérifier API (concert officiel unique à 20 h 30 ; aucun lien LT pour lieu couvert). Préserver immobilier, Nginx, Render et le design.


## 18 octobre 2026 — correction appliquée au VPS après autorisation explicite
- L’utilisateur a autorisé le transfert et l’application sur 179.237.81.208. Blocage de transfert levé ; correction effectivement appliquée à Samstag interne.
- Sauvegardes : code `/opt/samstag/official-links-backup-20261018/`, base cohérente `/var/lib/samstag/backups/before-official-links-20261018.sqlite3` ; intégrité ok. 88 tests réussis sur le VPS avant redémarrage.
- Anciennes observations LT de lieux couverts requalifiées en revue, preuves conservées (11 entrées, dont seules 2 étaient publiques lors de l’audit). Collecte ciblée D! relancée ; redémarrage Samstag seul, collecte périodique reprise.
- Réponse réelle `/api/events` : 369 événements, un seul concert LUM x Pat Burgener, le 20 octobre à 20 h 30, gratuit sur inscription, URL officielle `https://dclub.ch/agenda/20261020/pat-burgener#d-club-live`. Portes 20 h conservées distinctement. Aucun lien LT publié pour lieu possédant un canal officiel activé.
- L’ancienne fiche Jumeaux LT est retirée de la publication tant qu’une fiche officielle qualifiée ne la remplace pas ; aucune correction de son collecteur annoncée.
- Services Samstag et Cockpit Immobilier actifs, intégrité SQLite ok. Aucun changement de design, Render, DNS ou Nginx. Preuves : `validation/official-links-2026-10-18/result.json` et `result-vps.json`. Vérification ponctuelle ; pas d’observation sur 24 heures.

## 18 octobre 2026 — proposition visuelle de fiche Samstag

L’utilisateur ne retient pas les autres propositions de l’audit sans aperçu visuel. Le point sur la clarté de « Pour moi » est accepté. Nouvelle direction explicite : un clic sur un événement doit ouvrir une fiche Samstag plus complète, avec possibilité de partager et masquer le lieu, puis accès au lien externe. Les liens externes immédiats donnent une impression de simple relais.

Aperçu isolé dans `apercus/fiche-evenement/` à la racine du projet Samstag : réutilisation du panneau existant, informations réellement collectées, aucune invention. Copie du 17 octobre en lecture seule comme source ; préférences de l’aperçu isolées. Programme → fiche et action masquer/annuler vérifiés dans le navigateur. Vue 390 px examinée. Description parfois tronquée dès les données source : enrichissement à traiter séparément si demandé. Aucun changement des fichiers applicatifs courants, aucun déploiement ou changement distant. Aperçu encore à discuter avec l’utilisateur.

## 18 octobre 2026 — fiches structurées généralisées

Demande utilisateur : appliquer partout la structure proposée. Code courant et aperçu mis à jour : Liste et Affiches ouvrent une fiche Samstag pour chaque événement, y compris sans lien externe. Identité et informations pratiques regroupées, Le film et Synopsis pour les métadonnées cinéma reconnues explicitement, À propos pour les autres sorties, prix et actions en bas. Lien externe principal, Partager secondaire, Masquer discret. Texte de Pour moi clarifié. Aucun fait ajouté ; descriptions de 400 caractères sans fin de phrase affichées comme extraits, fin de phrase disponible conservée.

Syntaxe des deux scripts vérifiée ; fonction de lecture parcourue sur les événements de l’aperçu, contrôles film/extrait/absence de description réussis. Fiches cinéma et soirée examinées dans le navigateur ; vue 390 px examinée. Contrôle Impeccable conservé dans l’aperçu. Les nouvelles règles cinéma sont conditionnelles : les autres formats restent présentés en texte, sans extraction spéculative.

VPS : service actif vérifié en lecture seule. TRANSFERT BLOQUÉ par le contrôle automatique d’approbation : demande une autorisation explicite d’envoyer les trois fichiers `static/js/main.js`, `static/css/style.css`, `templates/index.html` vers le VPS existant `179.237.81.208`. Aucun transfert, fichier distant modifié ni redémarrage effectué. Suite : obtenir cet accord, sauvegarder ces fichiers sur le VPS, transférer seulement les trois fichiers, vérifier le résultat. Ne pas transférer les données d’aperçu ou modifier les collecteurs.


## 18 octobre 2026 — fiches structurées appliquées au VPS
- Accord explicite reçu après le blocage de transfert. Trois fichiers transférés : static/js/main.js, static/css/style.css et templates/index.html.
- Sauvegarde préalable : /opt/samstag/ui-backup-fiches-20261018T171303Z. Empreintes SHA-256 locales et distantes identiques pour les trois fichiers.
- Samstag seul redémarré pour charger le modèle de page. Samstag et Cockpit Immobilier actifs après opération. Routes /, fichiers CSS/JS et /api/events HTTP 200 ; contenu structuré et texte Pour moi confirmés dans les réponses réellement servies ; 369 événements exposés à ce contrôle.
- Aucun changement Render, Nginx, DNS, collecteurs ou schéma de base. Descriptions tronquées toujours signalées comme extraits : récupération complète non incluse. Prévisualisation locale conservée sur le port 8766.


## 19 octobre 2026 — audit initial des données pour la bêta

Contrôle réel du VPS en lecture seule vers 10 h 37 (Paris). Preuves : `validation/audit-beta-2026-10-19/snapshot.json` et `metrics.json`. Aucun changement distant.

- Samstag actif, aucun redémarrage automatique compté depuis le lancement du 18 octobre à 19 h 13 Paris ; démarrage au boot toujours désactivé. Ce relevé ponctuel ne prouve pas une disponibilité continue de 24 h.
- 369 événements réels, démonstration désactivée, 23 noms de lieux distincts ; dates du 19 octobre 2026 au 16 janvier 2027. Chaque fiche publiée possède titre/date/heure/lieu/lien ; contrôle de présence uniquement, pas validation éditoriale exhaustive.
- Dernière mise à jour API : 10 h 30 ; âge maximal checked_at des fiches environ 7,5 minutes. Aucun doublon exact titre normalisé + identifiant lieu + date + heure détecté ; doublons approximatifs non exclus.
- 37 sources : 25 ok, 5 partielles, 5 à raccorder, 2 vides. Aucune périmée selon la santé actuelle. Un statut ok ne garantit pas une publication : Datcha, Ta Cave, Captain Cook, Bruxelles Café et Barberousse ont zéro fiche publique.
- Manques : 128 descriptions (35 %), 276 prix (75 %), 56 adresses (15 %), 92 images (25 %). 98 descriptions font exactement 400 caractères : indice de troncature à examiner, pas preuve pour chacune.
- Couverture : Scène 164 séances, Concerts 107, Soirées & clubs 58, Cinéma 40. Il s’agit de séances, pas de 369 spectacles distincts. Great Escape, Pavillon Bar & Kitchen et Bossette restent sans programme qualifié ; Simplon et Montriond également.

### Contre-vérifications éditoriales limitées

- Cat Power : titre/date 23 octobre/début 20 h 30 concordent avec https://www.docks.ch/evenement/concerts/20261023/cat-power-3/ ; la page indique « Complet » et bourse aux billets, absents du payload Samstag. Description collectée réduite à une accroche malgré un paragraphe officiel disponible. Priorité : collecte et affichage du statut de disponibilité, puis enrichissement description.
- D! LUM x Pat Burgener : titre/date et gratuité confirmés sur https://dclub.ch/agenda/20261020/pat-burgener/ ; heure 20 h 30 sur la page liée https://visaevents.swoogo.com/visa-moving-music-lausanne?lang=fr. La FAQ mentionne un tirage au sort des inscrits : « gratuit sur inscription » ne décrit pas toute la condition d’accès. À clarifier dans la fiche, sans promettre une entrée garantie. Adresses différentes entre inscription et club : conserver la priorité au contact officiel, ne pas écraser automatiquement.
- Pages billetterie CityClub et Hango NABS non accessibles via l’outil web de contrôle ; pas de conclusion sur leur disponibilité pour les utilisateurs.

### Ordre du prochain lot

1. Corriger et tester localement le statut complet/annulé et les conditions d’accès, en commençant par les Docks et D! ; ne pas prétendre à une couverture universelle.
2. Enrichir les descriptions depuis les fiches officielles et mesurer les prix/adresses récupérables sans invention.
3. Qualifier la couverture des bars prioritaires ; distinguer absence d’annonce et panne de collecte.
4. Vérifier plusieurs cycles et sauvegardes ; publication, démarrage au boot et formulaire de retour restent à préparer.


## 19 octobre 2026 — validation utilisateur de la checklist bêta

Choix transmis depuis la checklist interactive, sans remarque libre :
- Validés par l’utilisateur : actualisation automatique ; installation serveur ; principe de l’adresse publique et de l’accès sécurisé. Ce dernier choix ne prouve pas une publication effective, ne choisit pas de domaine et ne remplace pas les contrôles HTTPS.
- À corriger : date/heure/lieu/lien ; prix/adresses ; identité visuelle/lisibilité ; fiches événements ; confort mobile ; filtres/préférences/partage/liens.
- À tester ensemble : complet/annulé/conditions d’entrée ; descriptions ; couverture des bars prioritaires ; fonctionnement durable/sauvegardes ; retour utilisateur/signalement ; premier groupe de testeurs.
- Recommandation de prochain lot : parcours « trouver une sortie et décider » sur mobile. Contrôler puis corriger les informations pratiques sur un échantillon varié, présenter une proposition visuelle concrète liste + fiche avant généralisation, puis tester les filtres et liens. Distinguer les défauts mesurés des préférences visuelles encore à préciser. Conserver la direction programme culturel et les couleurs validées antérieurement tant qu’une nouvelle direction n’est pas choisie.
- À ne pas déclarer terminé : publication publique, HTTPS, sauvegarde externe, observation 24 h, formulaire de retour et qualification exhaustive des informations.


## 19 octobre 2026 — candidat mobile et corrections ciblées pour la bêta
- Réalisé LOCAL uniquement : prix et conditions d’inscription conservés dans la liste et la fiche, prix inconnu renommé « Prix à vérifier », badge Complet, portes et début séparés, salle et adresse regroupées ; adresse manquante explicitée. Accès externe et partage placés avant la description. Cibles tactiles principales 44 px, liste aérée et extraits sur deux lignes en mobile. Identité et couleurs conservées.
- Collecteur Docks : statut complet/annulé recherché dans le bloc informations/billetterie, sans lire les recommandations ; paragraphes officiels de présentation conservés au lieu de la seule accroche de 400 caractères. Relecture réelle de Cat Power : date/heure conservées, sold_out détecté, description de 445 caractères récupérée.
- D! : condition de tirage au sort ajoutée uniquement après confirmation d’identité de la fiche d’inscription liée et présence du texte explicite. Aucun prix/adresse inventé.
- Défaut trouvé au test et corrigé : « Afficher les masqués » en recherche utilisait les jours de l’onglet courant ; utilise désormais tous les jours des résultats. Libellé accessible des résultats corrigé également.
- Aperçu isolé : `apercus/beta-mobile/`, instantané API du 19 octobre à 10 h 37, enrichissements ciblés des pages officielles Docks et des preuves D! du 18 octobre. Préférences séparées. Serveur local 127.0.0.1:8767 ; vue de validation `/mobile.html`. Les 369 fiches ne sont pas toutes enrichies.
- Vérifié : 91 tests locaux réussis, syntaxe JavaScript ; contrôle navigateur à 320/390 px (fiche sans débordement horizontal) et 1100 px (page sans débordement). Recherche Cat Power, ouverture fiche, statut complet, conditions D!, filtre petit prix et état vide, masquage/réaffichage/restauration du lieu contrôlés. Capture liste + fiche disponible dans l’aperçu. Détecteur design : 19 avis, aucune erreur bloquante signalée ; ce n’est pas une certification d’accessibilité.
- Limites : pas de test sur téléphone physique, partage natif non testé, liens externes présents mais destinations non toutes parcourues ; préférences par rubrique et Affiches restent à contrôler dans le prochain lot. Aucune correction globale des 276 prix et 56 adresses manquants. Aucun transfert, redémarrage distant ni publication.
- Suite proposée : validation du rendu liste/fiche, puis enrichissement des prix/adresses par petits lots de sources officielles ; terminer contrôle des préférences et du partage avant préparation bêta.


## 19 octobre 2026 — prix mis de côté à la demande utilisateur
- Liste, Affiches et fiche : prix et mentions de prix manquant retirés de la présentation locale et de l’aperçu bêta. Filtre Gratuit / petit prix masqué ; anciennes préférences de prix ignorées au chargement pour éviter une liste filtrée sans contrôle visible.
- Données de prix conservées, collecte inchangée. Complet et conditions d’entrée conservés. Les descriptions officielles peuvent encore mentionner un tarif dans leur texte. Aucun déploiement distant.


## 19 octobre 2026 — lot bêta lancé et appliqué au VPS interne
- Autorisation utilisateur : « ok go tu peux tout lancer ». Lot appliqué à Samstag uniquement, sans publication externe, Nginx, DNS, Render ni modification de l’application immobilière. Sauvegardes préalables code `/opt/samstag/beta-backup-20261019T165343Z/code.tar.gz` et base `/var/lib/samstag/backups/before-beta-20261019T165343Z.sqlite3`.
- 100 tests réussis localement puis sur VPS. Empreintes des sept fichiers applicatifs vérifiées ; style final vérifié séparément. Service Samstag actif, application immobilière active. Démarrage automatique Samstag au boot activé.
- Formulaire réel sans nom/e-mail : avis général via bouton toujours accessible, signalement lié à une sortie. Stockage privé SQLite ; contrôle de session/origine, limites de longueur et fréquence. API de lecture des messages non exposée ; `feedback_cli.py` pour lecture par accès administrateur existant. Un signalement technique VPS a reçu HTTP 201, a été relu en base puis seul ce retour de test a été retiré. Tests de CSRF, validation, persistance et limitation réussis.
- Parcours navigateur : Liste/Affiches, Mes goûts avec Concerts puis désactivation Pour moi, masquage/réaffichage et recherche vérifiés. Formulaire soumis réellement sur l’aperçu isolé ; contexte Cat Power et confirmation reçue. Contrôle 390 px sans débordement formulaire. Partage natif tenté mais résultat système non observable ; ne pas le déclarer validé sur téléphone physique.
- JazzOnze+ : 26 fiches officielles lues, sans échec, descriptions récupérées ; adresses issues des blocs d’accès nommés, pas de l’administration. 22 concerts retenus avec adresse. Tests contre mauvais titre et mauvaise adresse ajoutés. Cat Power : complet et texte officiel 445 caractères ; D! : conditions d’accès avec tirage au sort conservées. Prix masqués conformément à la décision utilisateur, données conservées.
- Mesure réelle sur les 14 jours à partir du 19 octobre : 126 sorties ; adresses manquantes 30 → 8 ; descriptions absentes 43 → 19. Total API au contrôle : 368 sorties. Le reste du catalogue n’est pas déclaré intégralement vérifié.
- Observation bornée lancée : `samstag-observation.service`, début 19 octobre 16:53 UTC / 18:53 Paris, une mesure toutes les 15 minutes pendant 24 heures. Rapport `/var/lib/samstag/beta-observation-20261019.jsonl`, synthèse attendue `.summary.json` après fin. Premier relevé web ok, aucune source périmée/en échec ; limites de couverture connues. Historique préalable : deux erreurs ponctuelles de source sur la journée, sources rétablies au contrôle. Une observation complète sans interruption n’est pas encore prouvée.
- Sauvegarde quotidienne locale confirmée (copie du 19 octobre 04:18 UTC). Nouvelle sauvegarde cohérente `/var/lib/samstag/backups/samstag-beta-20261019.sqlite3`. Copie hors VPS sur Mac `sauvegardes/hors-vps/samstag-beta-20261019.sqlite3`, intégrité et restauration contrôlées. Premier export refusé par auto-review pour risque de retours privés ; vérification de la sauvegarde figée : table feedback vide (0 ligne), autres tables d’agenda public ; copie ensuite autorisée. La copie hors VPS n’est pas automatisée.
- Préparation publication : modèle Nginx séparé non activé dans `deploy/infomaniak/beta/nginx-samstag.conf.example` ; protocole 10–20 testeurs/une semaine dans `docs/archives/TEST_BETA.md`. Question adresse publique posée ; attendre le choix avant configuration DNS/HTTPS. Aucun recrutement/invitation externe réalisé.
- À terminer : choix adresse et ouverture HTTPS avec blocage public de `/api/refresh`, COOKIE_SECURE=1, vérification extérieure, observation 24 h, test du partage sur appareils physiques, qualification des bars Great Escape/Pavillon/Bossette toujours sans programme admissible. Aucun prix à enrichir en priorité pour cette bêta.
- Preuves : `validation/beta-2026-10-19/` (tests, avant/après, déploiement, qualification JazzOnze+, copie/restauration). Aperçu `/mobile.html` port 8767 maintenant fondé sur la réponse réelle du VPS après corrections ; retours de l’aperçu stockés uniquement dans sa base locale de test.

- Finalisation observation : sélection de la sauvegarde par date de modification (pas par nom), puis relance du seul observateur le 19 octobre à 18:59:36 Paris ; fin des 24 heures attendue le 20 octobre à 18:59:36 Paris. Samstag non redémarré à cette étape. Les premiers relevés antérieurs restent conservés.


## 19 octobre 2026 — choix de l’adresse publique reporté
- Réponse explicite utilisateur à la question d’adresse : option 3, « Je préfère choisir l’adresse plus tard ».
- Ne pas choisir ni configurer samstag.kadrant.ch ou une autre adresse à sa place. Publication publique, DNS et HTTPS reportés jusqu’à son choix ; Samstag reste interne.
- L’observation bornée de 24 h déjà lancée et les sauvegardes serveur continuent indépendamment. Aucun changement distant effectué dans cet échange.
- Priorité suivante : exploiter le bilan d’observation une fois disponible, traiter les données encore incomplètes et préparer les tests sans dépendre d’une publication.


## 19 octobre 2026 — poursuite autonome : adresses et descriptions restantes
- Instruction explicite : « poursuis sans demander ». Le choix d’adresse publique reste reporté ; aucune publication, DNS, HTTPS ni modification immobilière.
- Taco’s et Étoile Blanche : adresses confirmées sur leurs pages officielles Contact, preuves HTML conservées. Registre des lieux actualisé avec preuve/date ; aucune adresse ajoutée à l’Oblò sans confirmation officielle suffisante.
- Pulloff : description récupérée dans le seul widget du spectacle, en excluant l’exposition voisine. La Brèche : paragraphes des blocs artistes récupérés, hors navigation/pied de page. Deux tests de régression ajoutés.
- 102 tests réussis localement et sur le VPS. Corrections appliquées après sauvegardes dédiées dans `/opt/samstag/adresses-backup-20261019T173255Z` et `/opt/samstag/descriptions-backup-20261019T173423Z`. Samstag seul redémarré pour charger les données/modules ; observation et immobilier préservés.
- Vérification réelle API après collecte : 368 sorties au total ; sur les 126 sorties des deux prochaines semaines, adresses absentes 8 → 3 et descriptions absentes 19 → 13. Les trois adresses concernent l’Oblò ; les descriptions restantes concernent le MAD (10) et le Romandie (3). Aucun texte ni tarif inventé.
- Samstag, observateur et immobilier actifs. Quatre mesures d’observation présentes à ce contrôle ; observation de 24 heures toujours en cours, pas déclarée achevée.
- Aperçu local mis à jour avec les données réellement servies après corrections. Preuves dans `validation/adresses-2026-10-19/`. Restent : qualification des trois adresses Oblò et des descriptions MAD/Romandie, partage sur téléphone réel, bilan d’observation après son terme ; publication dépend toujours du choix ultérieur de l’utilisateur.


## 19 octobre 2026 — campagne Playwright complète et correction WebKit
- Suite reproductible dans `e2e/`, vraie application et base isolée, instantané public de 368 sorties et horloge produit figée. Cinq profils, douze scénarios chacun. Dépendance officielle verrouillée Playwright 1.48.2, compatible macOS 13 ; version fournie 1.62.1 incompatible avec cet OS.
- Première passe : 58/60, deux échecs sur le retour de focus WebKit ordinateur/mobile. Correction : carte ouvrante explicitement mémorisée, sans dépendre du focus implicite du navigateur. Deuxième passe complète : 60/60, aucun ignoré, aucun retry/flaky. Dix messages de test persistés vérifiés dans la seule base isolée.
- Correction du seul fichier `static/js/main.js` appliquée au VPS interne, sauvegarde /opt/samstag/focus-backup-20261019T185812Z. Fichier réellement servi comparé par SHA-256 au local : identique. Aucun redémarrage ; Samstag, observation et immobilier actifs au contrôle. Aperçu local corrigé également.
- Couverture et limites : recherche, filtres, préférences, fiches, liste/affiches, retours, erreurs réseau, partage simulé, liens profonds, tailles et clavier. Chromium 130, Firefox 131, WebKit 18 : versions anciennes, pas de certification des versions actuelles. Appareils physiques/partage natif, performance, audit sécurité/accessibilité complet et accès public non validés. Prix restent masqués, adresse publique toujours reportée.
- Preuves et bilan : `validation/playwright-2026-10-19/BILAN.md`, `results.json`, `synthese.json`, `report/index.html`, `first-run/`, `deploiement-focus.json`. Les 102 tests Python antérieurs ne sont pas présentés comme une nouvelle campagne dans cet échange.


## 21 octobre 2026 — nouvelle fiche appliquée à tout le catalogue
- Autorisation utilisateur : « ok applique cela à tout le site ». Modèle commun V4 appliqué aux fiches de toutes les rubriques, via `static/js/main.js` et `static/css/style.css`. Photo compacte à droite, date/heure hiérarchisées, texte avant les actions, petits boutons Voir le site/Partager et utilitaires dans Autres actions. Couleurs des catégories préservées, poignée uniquement sur mobile.
- Textes collectés conservés sans reformulation globale ; films/crédits/métadonnées, portes, salle, conditions d’accès et état complet conservés. Prix toujours masqués. Photos manquantes/en panne retirées sans espace vide ; descriptions manquantes/tronquées signalées. ClubNight de nuit distingué d’un vrai programme multi-jours à partir de l’instant de fin explicite en heure suisse.
- Menu accessible au clavier, fermeture extérieure/Échap et retour du focus vérifiés. Changement de fiche par lien profond corrigé ; erreur d’une ancienne photo sans effet sur la fiche suivante.
- Tests : première passe 76/80 (formatage horaire nocturne corrigé), passe complète 80/80 sur cinq profils, puis 25/25 cas ciblés sur les fichiers finaux après protection contre l’échec tardif d’une photo. Aucun ignoré, retry ou flaky. Chromium 130/Firefox 131/WebKit 18 et mobiles émulés : pas une certification des navigateurs actuels ni de téléphones physiques. Partage natif simulé, retours envoyés uniquement sur la base locale isolée. Pas de nouvelle campagne Python, moteur inchangé.
- Déploiement Infomaniak effectué sans redémarrage. Sauvegarde distante : `/opt/samstag/fiche-backup-20261021T183554Z`. Empreintes des fichiers réellement servis identiques au local ; accueil HTTP 200, santé ok, Samstag et immobilier actifs. Aucun changement Render, DNS, Nginx ou base de production.
- Contrôle navigateur réel via tunnel privé : 4 rubriques × 2 formats, aucun débordement horizontal ni erreur JavaScript, menus fonctionnels ; photos distantes selon disponibilité. 364 sorties au contrôle. Aucune écriture externe pendant cette vérification. Captures et preuves : `validation/fiche-2026-10-21/`, rapports complets et ciblés, `verification-vps.json`, `deploiement.json`, copies avant modification.
- Charte et tests de parcours actualisés. Accès existant http://127.0.0.1:8011/ à recharger ; publication publique toujours reportée selon choix antérieur de l’utilisateur. Les photos/descriptions absentes à la source ne sont pas créées par la nouvelle mise en page.


## 22 octobre 2026 — samstag intégré
- Nom et logo gras noir / dernier a en miroir bleu adoptés. En-tête blanc, signature « Les sorties à Lausanne », accents d'interaction bleus ; couleurs des catégories conservées. Titres et textes publics actualisés.
- Demande rédactionnelle appliquée : « Choisissez les sorties qui vous intéressent. » ; consignes Mes goûts simplifiées, sans précision technique de stockage.
- Vérification locale 320/390/1226 px : aucun débordement ni erreur JS, logo chargé, recherche, préférences, modes Liste/Affiches et ouverture du retour vérifiés. Instantané de test daté, pas données actuelles.
- Appliqué au VPS après sauvegarde `/opt/samstag/samstag-backup-20261022T100116Z` ; seul service samstag redémarré pour charger le template. HTTP 200, santé ok, 360 événements au contrôle, immobilier actif. Empreintes statiques servies conformes. Aucune modification Render, DNS ou base.
- Preuves `validation/samstag-2026-10-22/`. Logo raster, vectorisation restante ; aucune nouvelle campagne complète moteur/collecteurs. Publication publique toujours reportée.


### Complément — simplification de toute l’interface
À la demande de l’utilisateur, suppression des explications techniques superflues dans l’accueil, Mes goûts, formulaire de retour, pied de page et messages d’état. Date de mise à jour, erreurs actionnables et signalements de données manquantes conservés. Nouveau déploiement après sauvegarde `/opt/samstag/samstag-backup-20261022T100302Z`, HTTP 200 et santé ok, deux services actifs. Préférence durable : consignes courtes, pratiques, sans détails d’implémentation.


## 22 octobre 2026 — accueil allégé
- Accord utilisateur sur l’allègement : les six choix de rubriques et le grand cadre sont remplacés par une invitation compacte « Vos sorties, selon vos goûts », Personnaliser et Pas maintenant. Personnaliser ouvre Mes goûts ; aucun changement aux préférences existantes.
- Contrôles locaux 320/390/1226 px réussis : hauteur 83 px mobile / 61 px ordinateur, sans débordement ni erreur JavaScript ; choix, enregistrement, refus et persistance après rechargement vérifiés.
- Appliqué sur VPS après sauvegarde `/opt/samstag/samstag-backup-20261022T100557Z`, seul service Samstag redémarré ; HTTP 200, santé ok, deux services actifs, empreintes statiques conformes. Preuves `validation/accueil-compact-2026-10-22/`. Aucun changement moteur, DNS ou publication publique.


## 1er novembre 2026 — audit architecture, collecteurs et organisation
- Audit demandé par l’utilisateur, sans modification applicative ni déploiement. Rapport courant : `docs/audits/AUDIT_2026-11-01.md` ; mesures publiques versionnées : `docs/audits/2026-11-01-mesures.json`.
- Mise à jour factuelle : **https://samstagloz.ch est public et répond HTTP 200**. Les mentions anciennes « domaine non choisi / publication reportée » décrivent l’historique et ne sont plus l’état courant. Aucun DNS, proxy ou certificat modifié pendant l’audit.
- Contrôle vers 22 h 31–33 Paris : 322 sorties publiques, 19 lieux représentés, 2 675 éléments conservés ; 37 sources actives sur 39, dont 24 autorisées à publier sous conditions. Collecte dégradée : 23 OK, 5 partielles, 5 sans adaptateur, 3 vides, MAD en erreur. Pas une mesure d’exhaustivité régionale.
- 102 tests Python réussis dans un environnement temporaire Python 3.9 (avertissement LibreSSL), syntaxe JS correcte ; JS et CSS publics identiques au local par SHA-256. Pas de nouvelle campagne E2E, contrôle mobile complet, SSH, restauration ni observation 24 h.
- Défauts confirmés : doublon Mike D / Mike D 5D aux Docks le 3 novembre à 20 h 30 entre L’Agenda et officiel ; reproduction isolée d’une panne de fiche Docks enregistrée `empty` au lieu d’erreur/partiel. Aucun correctif appliqué.
- Recommandation : conserver Flask/SQLite et le design ; fiabiliser d’abord documentation actuelle, environnement et CI, puis statuts/rapprochement des collecteurs, sauvegardes/alertes, organisation progressive du code. Les lots suivants restent à décider ; aucun élargissement autonome de la collecte lancé.


## 1er novembre 2026 — plan d’implémentation et suivi
- Plan opérationnel ajouté dans `docs/PLAN_IMPLEMENTATION.md`, avec lots L0 à L6, dépendances, tâches identifiables et critères de fin. Tableau de bord court dans `docs/SUIVI_IMPLEMENTATION.md`.
- Diagrammes Mermaid ajoutés dans `docs/diagrams/` : feuille de route, processus de développement et architecture cible. Leur état doit être actualisé avec le tableau de suivi à la fin de chaque session.
- Première séquence recommandée : actualiser les documents actifs et l’environnement local, ajouter la CI et la validation des registres, puis corriger le statut partiel Docks/Romandie avant le diagnostic ciblé MAD et le dédoublonnage.
- Aucun code applicatif, collecteur, serveur ou site public modifié. La décision « agenda nocturne ou culturel étendu » reste ouverte et bloque uniquement le lot produit L6.


## 1er novembre 2026 — lot L0 finalisé
- `docs/ETAT_ACTUEL.md` devient le point d’entrée réécrit pour l’état courant. `docs/PASSATION_PROJET.md` reste le journal chronologique et les anciens bilans portent désormais un bandeau d’archive.
- `README.md`, `PRODUCT.md`, `docs/EXPLOITATION.md` et `deploy/infomaniak/README.md` ont été alignés sur le domaine public, la production Flask/Infomaniak, les fonctions présentes et les limites réellement vérifiées.
- `docs/README.md` indexe les références actives et historiques. `docs/PREUVES_ET_ARCHIVES.md` distingue les preuves versionnées, les dossiers cités mais absents et les contrôles distants non réalisés.
- Les tâches `L0.1` à `L0.6`, le tableau de suivi et la feuille de route Mermaid sont marqués terminés. Prochaine session bornée : `L1.1` à `L1.3`, sans modification des collecteurs.
- Session documentaire uniquement : aucun code applicatif, appel de collecteur, commit, envoi GitHub, accès SSH ou changement de production.


## 1er novembre 2026 — lot L1 finalisé
- Python 3.12 déclaré dans `.python-version` et le devcontainer. `.env.example` documente une base absolue locale ; le lanceur impose `COLLECTION_ON_VISIT=0`, `DEMO_ENABLED=0`, l’écoute locale et refuse les chemins de production connus.
- Interface commune ajoutée : `make setup`, `dev`, `test`, `e2e`, `check`, `report` et `lock`. Installation neuve vérifiée dans `.venv` depuis `requirements-dev.lock`.
- Dépendances directes séparées dans les fichiers `.in` et transitives figées dans `requirements.lock` et `requirements-dev.lock`, générés pour Python 3.12 avec pip-tools 7.5.2.
- Les E2E prennent désormais `SAMSTAG_PYTHON`, écrivent leurs rapports sous `.artifacts/` et gardent leur base sous `.local/`, sans supposer un `.venv` nommé. Une première matrice a révélé une collision entre base et sorties nettoyées par Playwright ; séparation appliquée puis matrice complète réussie : 85/85 sur cinq profils et 368 événements de fixture, aucune collecte externe.
- Schémas JSON ajoutés pour sources, lieux et bars. Validation réussie : 39 sources, 159 lieux et 28 bars, avec identifiants uniques et références croisées.
- Workflow GitHub Actions ajouté : Python 3.12, dépendances verrouillées, schémas JSON, syntaxe JavaScript, 102 tests Python et E2E Chromium. Le fichier est local et n’a pas encore été exécuté sur GitHub.
- `make check` réussi : 102 tests Python. `make report` et `make dev` vérifiés sur la base locale vide ; santé HTTP 200. Aucun collecteur réel, service distant ou déploiement utilisé.


## 1er novembre 2026 — événements diurnes au périmètre
- Décision utilisateur : inclure les événements diurnes. Périmètre produit, état actuel, tâche L6.1, suivi et feuille de route actualisés.
- Mise en œuvre à faire : `collection_quality.py` rejette encore les départs de 6 h à 16 h 59 ; vérifier aussi les restrictions propres aux adaptateurs et registres, puis les périodes de l’interface. Les expositions et longues périodes ne sont pas implicitement autorisées.
- Documentation uniquement ; aucune collecte, modification applicative ni intervention en production.


## 1er novembre 2026 — prise en charge locale des événements diurnes
- Demande utilisateur appliquée au code local : retrait du rejet global des départs de 6 h à 16 h 59 ; confirmation des séances Vidy et enrichissement JazzOnze+ également en journée. Notes du registre Chorus, Bellevaux et Grange alignées, sans changement des drapeaux de publication ni des lieux admis.
- Première période renommée « Aujourd’hui » et étendue de 6 h à 6 h le lendemain en heure suisse ; clé API historique `tonight` conservée. Avant 6 h, rattachement à la nuit précédente maintenu. Aucun changement CSS ou de structure visuelle.
- 107 tests Python réussis via `make check`, registres et syntaxe JS valides. Régressions : frontières horaires, séance cinéma diurne, confirmation Vidy contradictoire, description JazzOnze+, publication SQLite isolée et présence dans Aujourd’hui, refus des annulations/horaires non vérifiés/expositions/longues périodes.
- Tests navigateur lancés sur port local séparé 8779 et sortie `/private/tmp/samstag-diurne-e2e` (port 8768 déjà occupé). Paramètre `SAMSTAG_E2E_PORT` ajouté au lanceur/config E2E pour éviter les conflits.
- Aucune collecte réelle ni mesure d’exhaustivité ; les anciennes exclusions seront réévaluées lors d’une prochaine collecte avec le nouveau code. Aucun accès VPS, transfert, déploiement, commit ou envoi GitHub. `L6.1` reste ouvert pour livraison et mesure réelle de couverture.

- Résultat final navigateur : 17/17 scénarios Chromium réussis sur le catalogue de fixture, dont contrôle sans débordement à 320/390/1100 px. Rapport `/private/tmp/samstag-diurne-e2e/report/index.html`. Pas de contrôle sur téléphone physique ni de certification des autres navigateurs.


## 1er novembre 2026 — rangement documentaire et nettoyage local
- Deux lots demandés effectués : README orienté navigation, guide `docs/SE_REPERER.md` avec récapitulatif durable et architecture cible clairement distincte de l’arborescence actuelle, fiche `docs/COLLECTEURS.md` issue du registre et des mesures déjà sauvegardées.
- Dix anciens bilans et diagnostics déplacés dans `docs/archives/`, avec index et adaptation des liens. Passation laissée à son chemin stable. Références erronées à `collection_engine.py` et `collection_readers.py` corrigées dans le README.
- Suppression limitée à `.DS_Store` et aux caches Python de `scripts/` et `e2e/` ; déduplication de `.venv/` dans `.gitignore`. Rapports, bases locales, dépendances, ressources de design, preuves et sauvegardes conservés.
- Aucun déplacement du code applicatif, aucune collecte, aucun accès distant ni déploiement. La réorganisation du code reste un lot ultérieur.


## 1er novembre 2026 — contrôle final du lot L1
- `make check` rejoué sur l’état local final : 107 tests Python réussis, syntaxe JavaScript valide et registres conformes (39 sources, 159 lieux, 28 bars).
- Le résultat initial de 102 tests dans l’entrée L1 ci-dessus correspond à l’état précédant l’ajout parallèle des tests sur les événements diurnes. Le contrôle final couvre l’ensemble actuel sans attribuer ces changements applicatifs au lot L1.
- Aucun collecteur réel, accès distant, commit, envoi GitHub ou déploiement effectué pendant ce contrôle.


## 1er novembre 2026 — préparation de la publication GitHub
- Changements séparés en commits cohérents sur `chore/samstag-full-rename-20261101` : `21ac481` pour la prise en charge locale des événements diurnes et `2f039ee` pour l’environnement reproductible L1 et la CI. Le présent commit documentaire regroupe l’audit L0, le rangement, les plans et la passation.
- Contrôle avant publication : `make check` réussi avec 107 tests, 85/85 scénarios E2E déjà validés sur cinq profils, schémas JSON et syntaxe JavaScript valides, liens Markdown locaux contrôlés et `git diff --check` propre.
- Branche préparée localement seulement : aucun envoi GitHub, aucune pull request, aucun accès VPS et aucun déploiement de production dans cette session.
- Vérifications : liens locaux de 12 documents valides, trois diagnostics JSON identiques octet par octet à HEAD, `git diff --check` sans erreur. Aucun nouveau test applicatif nécessaire pour ce lot documentaire.


## 1er novembre 2026 — plan du troisième point : réorganisation du code
- Plan demandé enregistré dans `docs/PLAN_REORGANISATION_CODE.md`, relié au plan L5, à l’index et au guide SE_REPERER. Sessions R0 à R7 : référence Git/tests, pilote Vidy, autres lecteurs, collecte, domaine/stockage, web, finalisation, livraison séparée.
- Dépendances globales L2–L4 conservées ; préparation locale possible. Migrations de schéma, nouveaux contrats et changement de dispatch distingués du simple rangement.
- Aucun code déplacé, test applicatif relancé, collecteur ou serveur utilisé. Vérification des liens documentaires uniquement.


## 2 novembre 2026 — réorganisation locale, R0 et pilote R1
- Demande utilisateur de réorganiser le code : premier lot borné du plan appliqué, R0 puis R1 Vidy. Référence initiale propre `3f57d9b`, 107 tests réussis avant modification.
- Création de `samstag/collection/adapters/vidy.py` et des paquets sans effet de bord. Cinq fonctions et VIDY_ROOMS déplacés ; réexports explicites et dispatch conservés dans `programme_adapters.py`.
- Équivalence : AST des fonctions identique à HEAD ; deux scénarios / dix observations, tous les champs et statuts identiques. 109 tests réussis après déplacement, registres et syntaxe JS valides. Bilan versionné `docs/audits/REORGANISATION_R0_R1_2026-11-02.md`, preuves locales `.artifacts/reorganisation-2026-11-02/`.
- Guide, collecteurs, état et plan actualisés. Prochaine séance R2 : CityClub uniquement. L2–L4 restent ouverts ; aucun autre lecteur déplacé, aucune collecte réelle, accès VPS ou livraison. Aucune nouvelle campagne E2E, interface inchangée.


## 2 novembre 2026 — lot L2 finalisé
- Le suivi couvre les 39 canaux configurés : 37 actifs contrôlés à chaque passe et 2 désactivés toujours visibles. Chaque source distingue désormais accès, lecture, couverture et autorisation éditoriale, avec les principaux compteurs expliquant le passage des pages aux sorties publiques.
- Les limites connues sont séparées des pannes nouvelles dans `/api/health`. Les journaux techniques sont conservés 90 jours ; les preuves liées aux événements sont préservées.
- Contrôle réseau limité au MAD sur une base isolée : agenda accessible, six liens détectés, six fiches en échec, aucune sortie publiée. Le MAD reste actif dans le suivi mais sa publication automatique locale est désactivée et justifiée dans le registre.
- Docks et Romandie signalent correctement un échec total ou partiel des fiches. 114 tests Python réussis ; registres et syntaxe JavaScript valides. Contrôle navigateur : 83/85 réussis dans la série complète, puis les deux scénarios ralentis réussis séparément ; aucun défaut fonctionnel reproduit. Aucun autre site relancé, aucun accès VPS, aucun déploiement.
- Après publication, le premier contrôle GitHub a échoué avant les scénarios navigateur à cause d’un séparateur d’arguments superflu dans le workflow. Commande corrigée et reproduite localement dans les mêmes conditions : 17/17 scénarios Chromium réussis. Correctif livré séparément ; le nouveau contrôle GitHub est entièrement réussi.


## 2 novembre 2026 — fusion L0–L2 et préparation L3
- Pull request GitHub no 8 fusionnée dans `main` au commit `ba95f158`, après réussite du contrôle GitHub. Aucun déploiement ni intervention sur le VPS ou Render.
- Nouvelle branche locale `codex/l3-quality-dedup-plan` créée depuis la branche principale fusionnée.
- L3 préparé sans modification métier : plan en trois étapes, règles conservatrices, contrôles obligatoires et diagramme de décision. Première session bornée à la reproduction Mike D, la détection et un rapport en lecture seule sur une base isolée.
- Le contrôle ciblé des horaires Taco's reste une session distincte. Aucun site contacté, aucune donnée d'événement modifiée.


## 2 novembre 2026 — première étape L3 terminée
- Fixture minimale ajoutée pour le doublon « Mike D » / « Mike D 5D ». Le détecteur regroupe les fiches distinctes qui partagent un lieu canonique, une date et une heure explicite ; il ne rapproche pas les horaires incomplets.
- Rapport en lecture seule ajouté à la commande de diagnostic. Le cas Mike D apparaît comme un groupe officiel + agrégateur avec les deux liens de preuve. Deux spectacles distincts au même créneau sont seulement signalés pour revue et restent inchangés.
- Contrôle sur base SQLite isolée : contenu strictement identique avant et après le rapport. `make check` réussi avec 116 tests, registres conformes et syntaxe JavaScript valide.
- Tâches `L3.1`, `L3.2` et `L3.6` terminées. Prochaine session bornée : `L3.3` à `L3.5`. Aucun site contacté, aucune collecte réelle, aucun accès VPS, aucun déploiement.


## 2 novembre 2026 — deuxième étape L3 terminée
- Rapprochement conservateur ajouté : exactement une fiche officielle et une fiche d'agrégateur validées, même lieu canonique/date/heure et titres compatibles selon une règle étroite. Les autres groupes restent séparés pour contrôle.
- Les rapprochements sont enregistrés à côté des fiches d'origine, jamais à leur place. La sortie publique privilégie l'officiel et réunit tous les liens de preuve. Si l'officiel n'est plus publiable ou si la décision n'est plus confirmée, l'autre fiche redevient visible.
- Base SQLite isolée : Mike D passe de deux sorties à une fiche Docks, les deux observations restent présentes, puis le retour arrière restaure deux sorties. Titres incompatibles et concurrence officielle non rapprochés.
- `make check` réussi avec 118 tests ; registres et syntaxe JavaScript valides. Tâches `L3.3` à `L3.5` terminées. Prochaine session bornée : `L3.7` Taco's, sans campagne générale. Aucun site contacté, accès VPS ou déploiement.


## 2 novembre 2026 — troisième étape et clôture L3
- Contrôle réseau limité à Taco's sur une base SQLite isolée. Une seule source a été appelée ; 64 entrées lues, 9 publiables selon les règles locales et aucun candidat au doublon. Aucun autre site n'a été relancé.
- La preuve officielle `events-data.js?v=2026-10-06b` contient trois « Combat de chiens », les 18 novembre 2026, 16 décembre 2026 et 20 janvier 2027, avec `time: '20:26'`. Chaque description précise aussi « Début des matchs à 20h26 ».
- Conclusion : l'horaire atypique est volontaire. Aucune correction ni arrondi appliqué. Un test synthétique protège la conservation exacte des minutes et la note du registre documente la décision.
- `make check` réussi avec 119 tests ; registres et syntaxe JavaScript valides. L3 est terminé localement. Aucun accès VPS, changement de production, Render ou déploiement.


## 2 novembre 2026 — préparation L4 sans accès VPS
- Branche `codex/l4-operations-plan` créée depuis `main` après la fusion du L3. Lecture des procédures, unités, sauvegarde locale, route `/api/refresh`, configuration de session et retours utilisateurs ; aucun état distant supposé vérifié.
- Plan L4 découpé en six étapes : sécurité locale, reprise isolée, surveillance, constat VPS en lecture seule, application autorisée et preuve finale. Le constat distant et les modifications demandent deux autorisations distinctes.
- Cibles proposées : RPO 24 heures et RTO 4 heures, à confirmer par restauration chronométrée. Les preuves excluent secrets, bases réelles et contenu des retours.
- Première session recommandée : protéger `/api/refresh` dans Flask et la tester localement. Aucun accès VPS, collecte réelle, restauration de production, alerte ou déploiement effectué.


## 2 novembre 2026 — étape A L4 terminée localement
- `/api/refresh` n'accepte plus GET. POST répond 404 par défaut et ne peut atteindre le collecteur que si `MANUAL_REFRESH_ENABLED=1` et un secret dédié d'au moins 32 caractères correspondent en temps constant.
- Les exemples d'environnement gardent cette route désactivée. L'exemple serveur indique `COOKIE_SECURE=1` et rappelle que la clé de session reste dans le fichier privé, sans valeur versionnée.
- Trois tests locaux vérifient la désactivation, les configurations incomplètes, le mauvais secret et le chemin autorisé avec collecteur simulé. `make check` réussit avec 122 tests ; registres et syntaxe JavaScript valides. Aucun site n'est contacté par ces tests.
- Prochaine session : étape B, sauvegarde et restauration dans un dossier isolé. Aucun accès VPS, changement de production, secret, collecte réelle ou déploiement.


## 2 novembre 2026 — étape B L4 terminée localement
- `backup.py` accepte des chemins explicites tout en conservant les chemins VPS par défaut. Copie SQLite cohérente, intégrité, comptages, empreinte, permissions 0640 et rétention ciblée sont contrôlés sans exposer de contenu privé.
- `restore_check.py` restaure uniquement vers un nouveau fichier, refuse tout écrasement et vérifie la copie. Une base fictive contenant un événement synthétique est sauvegardée, restaurée puis relue par `db.py` ; aucune base réelle utilisée. `make check` réussit avec 125 tests, registres et syntaxe JavaScript valides.
- Objectifs de travail fixés à RPO 24 h et RTO 4 h, à confirmer par un exercice distant chronométré. Modèle de journal ajouté pour relier commit, sauvegarde, vérifications et retour arrière.
- Prochaine session : étape C, alertes, copie externe chiffrée et conservation des retours. Aucun accès VPS, sauvegarde de production, transfert externe ou déploiement.


## 2 novembre 2026 — étape C L4 terminée localement
- `operations_report.py` calcule sans réseau les alertes des sources automatiques : erreur courante, attention après 18 heures sans réussite, critique à 24 heures. La dernière sauvegarde passe en attention à 20 heures et critique à 24 heures.
- Politique locale : copie quotidienne chiffrée avant transfert vers un stockage objet privé distinct du VPS, 30 quotidiennes et 12 mensuelles ; boîte e-mail d'exploitation privée et second canal à confirmer avant activation.
- Retours : accès administratif seulement, lecture hebdomadaire, suppression sous 90 jours après résolution, réévaluation à 12 mois. L'automatisation de purge attend une migration SQLite versionnée ; aucune donnée supprimée.
- Tests entièrement synthétiques ; `make check` réussit avec 129 tests, registres et syntaxe JavaScript valides. Aucun message envoyé, transfert externe, fournisseur, compte privé, accès VPS ou déploiement. Prochaine action : contrôle final local et pull request des étapes A–C.


## 2 novembre 2026 — contrôle final local L4 A–C
- Branche comparée à `main` : quatre commits cohérents couvrent la préparation, la route administrative, la reprise isolée et les alertes. Arbre de travail propre avant publication de la pull request.
- `make check` rejoué : 129 tests réussis, registres et syntaxe JavaScript valides. Différences sans erreur de format ; recherche ciblée sans clé privée, jeton réel, mot de passe ou base versionnée.
- Revue manuelle : route refusée avant toute collecte, restauration sans écrasement, rapport d'alerte sans envoi ni collecte. Aucune anomalie bloquante trouvée.
- Aucun accès VPS, sauvegarde réelle, transfert, message ou déploiement. Après fusion et réussite GitHub, le constat VPS en lecture seule demandera une autorisation explicite distincte.


## 2 novembre 2026 — étape D L4, contrôle VPS en lecture seule
- Autorisation explicite reçue pour un constat distant strictement en lecture seule. Aucun fichier, service, minuteur, secret, certificat, base ou donnée n'a été modifié ; aucune collecte n'a été lancée.
- Service Samstag actif et activé au démarrage ; page publique et santé HTTP 200, état `ok`, aucun incident déclaré. Python 3.12.3, debug/démo/collecte à la visite désactivés. Clé de session persistante présente et cookie sécurisé activé, sans lecture ni consignation du secret.
- La copie active ne contient pas Git, mais les empreintes de `app.py`, du script de sauvegarde, du JavaScript et du CSS correspondent toutes au commit `ed42492`. La production n'intègre donc pas encore les lots fusionnés ensuite. Elle annonce 37 sources actives et 24 automatiques, contre 23 dans le code actuel après désactivation du MAD.
- Nginx refuse publiquement `/api/refresh` en HTTP 403. Flask utilise encore l'ancienne route GET/POST si le proxy est contourné ; la défense locale fusionnée en L4 A doit être livrée dans un lot autorisé.
- Minuteur quotidien actif : dernier passage réussi le 2 novembre à 04:16 UTC. Sept copies locales, dernière copie SQLite intègre et permissions privées. Aucune copie chiffrée hors VPS, restauration chronométrée ou alerte reçue n'a été prouvée.
- Rapport : `docs/audits/L4_VPS_LECTURE_SEULE_2026-11-02.md`. Prochaine session bornée : préparer localement le lot de livraison, ses contrôles et son retour arrière. Toute application sur le VPS exige une nouvelle autorisation explicite.


## 2 novembre 2026 — lot applicatif L4 préparé localement
- Branche `codex/l4-deployment-preparation` créée depuis `main` après fusion de la PR no 11. Aucun accès VPS, Render, transfert externe ou modification de production.
- Outils ajoutés : construction d'une archive depuis un commit Git revu et vérification de chaque empreinte après extraction. Sélection limitée au moteur Flask, ressources, registres, paquet `samstag/`, dépendances verrouillées et outils d'exploitation ; bases, secrets, environnement, journaux, tests, E2E et documentation exclus.
- Paquet local `.artifacts/releases/samstag-b593dc6fea28.tar.gz`, commit `b593dc6fea28eb7072e785f8d4cb3a833fd3bad3`, 415 933 octets, 42 fichiers d'exécution, empreinte SHA-256 `2134ec6293c810baf21daf09d3d2d564a6512d3368918888a24b695f966ed686`. L'archive reste locale et ignorée par Git.
- Contrôles : 131 tests réussis, registres et JavaScript valides ; archive et 43 fichiers internes vérifiés ; compilation Python ; simulation sur base isolée avec accueil/santé/sources, 39 canaux, 23 automatiques, GET refresh 405 et POST sans autorisation 404. Aucun réseau de collecte.
- Procédure `docs/L4_LOT_LIVRAISON.md` : sauvegarde et restauration isolée avant changement, conservation entière de `ed42492`, échange du dossier applicatif, critères de maintien sur dix minutes et retour applicatif sans restauration automatique de la base. Les ajouts de schéma sont uniquement additifs.
- Le premier sous-lot ne modifie ni dépendances, ni Nginx, ni unités, ni secrets. La copie chiffrée hors VPS et l'envoi d'alertes restent séparés faute de fournisseur et destinataires privés configurés. Toute application du paquet exige une nouvelle autorisation explicite.


## 2 novembre 2026 — sous-lot applicatif L4 livré sur le VPS
- Autorisation explicite reçue pour appliquer le sous-lot avec sauvegarde et retour arrière. Précontrôle conforme : `ed42492` confirmé par quatre empreintes, service et minuteur actifs, dépendances saines, santé `ok`, 37 sources actives et 24 automatiques.
- Archive `b593dc6` vérifiée extérieurement puis sur 43 fichiers internes. Configuration contrôlée sans afficher de secret. Aucun changement de dépendance, Nginx, unité systemd, environnement privé, Render ou service voisin.
- Sauvegarde préalable `samstag-20261102T210014737231Z.sqlite3`, restaurée dans `pre-20261102T210014Z.sqlite3` : intégrité `ok`, empreinte `1af51781aaa521d30d0a7631fc686130c324b5c150b89f088f7a1c23c343fc6e`. Base active non remplacée. Ancienne application conservée dans `/opt/samstag/rollback/app-20261102T210014Z-ed42492`.
- Application remplacée puis démarrée sans retour arrière. Contrôles : accueil, événements, santé et sources HTTP 200 ; public refresh 403 ; Flask direct GET 405 et POST sans autorisation 404 ; 39 canaux configurés, 37 actifs, 23 automatiques ; aucun lieu Buzz Club, Satellite ou bibliothèque dans les 414 sorties.
- Premier cycle en 45 secondes : 37/37 sources, 1 093 observations, 428 candidates, 665 refusées, 414 sorties, un seul échec MAD. Le MAD est non automatique. État : 20 ok, 16 limités, 1 erreur de lecture connue.
- Observation 21:00:15–21:11:06 UTC : 414 sorties constantes, service actif, zéro redémarrage et aucune erreur système. Version maintenue ; rollback disponible.
- Limite : le rapport d'alerte classe à tort Lausanne Tourisme, Vidy et Château Music Club comme « jamais réussis » alors que leur accès et leur lecture sont corrects mais partiels. Aucun envoi n'est activé. Prochaine session bornée : corriger ce calcul localement sur données isolées avant activation. Copie externe toujours absente.
- Preuve : `docs/audits/L4_LIVRAISON_VPS_2026-11-02.md`.


## 2 novembre 2026 — fausses alertes L4 corrigées localement
- Branche `codex/l4-alert-freshness-fix` créée depuis `main`. Aucun accès VPS, collecte réelle, tâche planifiée, destinataire ou message.
- Cause : `operations_report.py` utilisait uniquement l'ancien historique `ok/empty`. Les diagnostics récents de Vidy, Lausanne Tourisme et Château indiquaient `access_status=ok` et `parse_status=ok`, mais une couverture partielle ; ils étaient donc classés à tort « jamais réussis ».
- Correction : l'heure d'un diagnostic avec accès et analyse réussis compte comme dernière réussite, même si la couverture est partielle ou soumise à revue. Une erreur d'accès ou d'analyse ne renouvelle jamais cette heure.
- Régressions : les trois identifiants observés ne déclenchent plus d'alerte récente ; les seuils 18 h/24 h restent appliqués ; une analyse en erreur sans réussite antérieure reste critique. `make check` réussit avec 134 tests, registres et JavaScript valides.
- Correction locale seulement. La production reste sur `b593dc6`, le mécanisme d'envoi reste inactif et la copie externe absente. Prochaine action : contrôle et publication de cette correction, sans activation.


## 9 novembre 2026 — correction L4 revue localement
- Branche `codex/l4-alert-freshness-fix`, commits `3dd0ee4` et `25acef3`, comparés à `main`. Aucun défaut bloquant relevé et `git diff --check` propre.
- La règle reste bornée : accès et analyse doivent être `ok` pour renouveler la fraîcheur ; une couverture partielle est admise, une erreur réelle ne renouvelle pas l'heure de réussite. L'ancien historique réussi reste pris en compte.
- Vérifications : 7 tests ciblés de `tests.test_operations_report`, puis `make check` avec 134 tests réussis, 39 sources/159 lieux/28 bars validés et syntaxe JavaScript valide.
- Aucun accès VPS, collecte réelle, envoi, activation d'alerte, changement Render ou déploiement. Prochaine action : publier et fusionner la branche revue ; toute livraison VPS reste une étape séparée soumise à autorisation explicite.


## 9 novembre 2026 — réorganisation L5/R2 CityClub
- Branche `codex/l5-r2-cityclub` créée depuis `main` après la fusion de la PR L4 no 14. Sous-lot limité au déplacement du lecteur CityClub, sans réparation de source.
- `parse_cityclub` vit dans `samstag/collection/adapters/cityclub.py`. `expanded_adapters.py` le réexporte et son dispatch utilise le même objet, afin de préserver les anciens consommateurs.
- Fixtures renforcées : tous les champs d'une séance, passage décembre–janvier, identité de billetterie, mois non annoncé ignoré et structure invalide refusée. Trois tests ciblés puis `make check` réussis avec 136 tests, registres et JavaScript valides.
- Aucun appel au site, aucune collecte réelle, base, interface, VPS, Render ou production modifiés. Prochaine étape autonome : R2 Naftule/Boulimie. Preuve : `docs/audits/REORGANISATION_R2_CITYCLUB_2026-11-09.md`.


## 10 novembre 2026 — réorganisation L5/R2 Naftule–Boulimie
- État de départ propre sur `main` au commit de fusion CityClub `8fa2510`. La correction L4 a été fusionnée auparavant au commit `3708ba5`, mais reste non livrée sur le VPS.
- `parse_naftule` et `parse_boulimie` vivent dans leurs modules nommés sous `samstag/collection/adapters/`. Les réexports historiques et le dispatch utilisent les mêmes objets.
- `event_at` et `french_day` sont mutualisés dans `adapters/common.py`; CityClub utilise aussi ce constructeur sans changement de champs.
- Six tests ciblés couvrent les champs, séances distinctes, heures ambiguës, calendrier absent, plages et jours explicites, hors-les-murs et absence d'heure. `make check` réussit avec 139 tests, registres et JavaScript valides.
- Aucun appel de source réelle, collecte, base, interface, VPS, Render ou production modifiés. Prochaine étape autonome : R2 Arsenic. Preuve : `docs/audits/REORGANISATION_R2_NAFTULE_BOULIMIE_2026-11-10.md`.


## 10 novembre 2026 — réorganisation L5/R2 Arsenic
- Branche `codex/l5-r2-arsenic` créée depuis `main` après la fusion de la PR Naftule/Boulimie no 16 au commit `b9dd446`.
- `parse_arsenic` vit dans `samstag/collection/adapters/arsenic.py`; l'ancien import et le dispatch utilisent le même objet.
- Trois tests ciblés figent occurrence horodatée, `nohour`, annulation, gratuité, preuves, classifications et formats invalides. `make check` réussit avec 142 tests, registres et JavaScript valides.
- Aucun site réel, collecte, base, interface, VPS, Render ou production modifiés. Prochaine étape autonome : R2 Grange/Pulloff. Preuve : `docs/audits/REORGANISATION_R2_ARSENIC_2026-11-10.md`.


## 10 novembre 2026 — réorganisation L5/R2 Grange–Pulloff
- Branche `codex/l5-r2-grange-pulloff` créée depuis `main` après fusion de la PR Arsenic no 17 au commit `89c6e66`.
- `collect_grange` et `parse_pulloff` vivent dans leurs modules nommés ; anciens imports et dispatch conservent les mêmes objets. Le test de limite Grange vise désormais la configuration du module consommateur.
- Sept scénarios ciblés puis `make check` réussissent avec 143 tests, registres et JavaScript valides.
- Aucun appel réel, collecte, base, interface, VPS, Render ou production modifiés. Prochaine étape autonome : R2 Folklor/MAD. Preuve : `docs/audits/REORGANISATION_R2_GRANGE_PULLOFF_2026-11-10.md`.


## 10 novembre 2026 — réorganisation L5/R2 Folklor–MAD
- `parse_folklor` et `parse_mad_ticket` déplacés dans leurs modules nommés avec réexports compatibles ; orchestration MAD inchangée.
- Quatre tests ciblés et `make check` réussissent avec 144 tests, registres et JavaScript valides.
- Aucun appel réel, collecte, base, interface, VPS, Render ou production modifiés. Prochaine étape autonome : R2 JazzOnze+. Preuve : `docs/audits/REORGANISATION_R2_FOLKLOR_MAD_2026-11-10.md`.
