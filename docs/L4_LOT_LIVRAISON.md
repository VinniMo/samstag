# L4 — lot de livraison préparé

**État au 2 novembre 2026 : sous-lot applicatif livré et maintenu après contrôles.**

## Vue simple

Ce lot met la production au niveau du code validé depuis `ed42492` : événements diurnes, diagnostics des 39 canaux, rapprochements prudents des doublons, désactivation automatique du MAD et protection Flask de la route administrative.

La livraison remplace le dossier applicatif complet afin d'éviter un mélange entre ancienne et nouvelle version. L'ancienne application est conservée entière jusqu'à validation. La base, les secrets, Nginx, les unités systemd et l'environnement Python ne sont pas remplacés.

Ce lot couvre l'application et les outils locaux de sauvegarde. La copie chiffrée hors VPS et l'envoi d'alertes restent un lot séparé, car leur fournisseur et leurs destinataires privés ne sont pas encore configurés.

La livraison autorisée a été effectuée le 2 novembre. Le [rapport de livraison](audits/L4_LIVRAISON_VPS_2026-11-02.md) conserve la sauvegarde, les contrôles, l'observation et les limites. La procédure ci-dessous reste la référence pour comprendre ou reproduire le retour arrière.

## Paquet prêt

| Élément | Valeur |
|---|---|
| Commit d'exécution | `b593dc6fea28eb7072e785f8d4cb3a833fd3bad3` |
| Archive locale | `.artifacts/releases/samstag-b593dc6fea28.tar.gz` |
| Taille | 415 933 octets |
| Empreinte SHA-256 | `2134ec6293c810baf21daf09d3d2d564a6512d3368918888a24b695f966ed686` |
| Contenu contrôlé | 42 fichiers d'exécution, plus métadonnées et empreintes |
| Exclus | bases, secrets, fichiers d'environnement, journaux, tests, E2E et documentation |

Le paquet est généré depuis Git, jamais depuis les fichiers non enregistrés du dossier de travail. Chaque fichier possède sa propre empreinte dans `SHA256SUMS`.

## Contrôles locaux réussis

- 131 tests Python, registres et syntaxe JavaScript réussis ;
- archive extérieure et 43 fichiers internes vérifiés par empreinte ;
- compilation de tous les fichiers Python du paquet ;
- démarrage applicatif simulé sur une base SQLite neuve et isolée ;
- accueil, santé et sources accessibles dans cette simulation ;
- 39 canaux visibles et 23 autorisés à publier après contrôles ;
- GET `/api/refresh` refusé avec 405 et POST sans autorisation refusé avec 404 ;
- absence de base, secret, test, E2E ou document dans l'archive.

## Ce qui changera lors d'une livraison autorisée

- remplacement atomique de `/opt/samstag/app` par le dossier vérifié ;
- création additive des tables de diagnostic et de rapprochement absentes ;
- passage du MAD de 24 à 23 canaux autorisés à publier automatiquement ;
- activation de la protection Flask de `/api/refresh` derrière la protection Nginx existante ;
- installation des outils améliorés de sauvegarde, restauration isolée et rapport d'exploitation.

Les dépendances directes restent identiques à celles de la production actuelle. Le premier lot ne met donc pas à jour l'environnement Python, ce qui réduit le risque.

## Conditions avant intervention

1. Obtenir une autorisation explicite de modification du VPS.
2. Vérifier que la production correspond toujours à `ed42492`. Arrêter si ses empreintes ont changé.
3. Éviter la fenêtre de sauvegarde quotidienne de 04:10 à 04:25 UTC.
4. Relever l'état des services, la santé, les 37 sources actives et les 24 publications automatiques actuelles.
5. Créer une sauvegarde SQLite cohérente, vérifier son intégrité et la restaurer dans un nouveau fichier isolé.
6. Conserver l'intégralité de l'ancien dossier applicatif sous un nom daté.
7. Vérifier l'archive extérieure puis toutes les empreintes internes avant l'arrêt du service.

Si une condition échoue, la livraison s'arrête avant de remplacer l'application.

## Séquence d'application préparée

Les commandes précises seront exécutées uniquement après autorisation. Elles suivent cet ordre :

1. transférer l'archive dans un dossier d'arrivée privé ;
2. contrôler son empreinte, l'extraire dans un dossier de version et exécuter `verify_release.py` ;
3. vérifier la configuration sans afficher les secrets ;
4. créer et restaurer la sauvegarde préalable dans un fichier isolé ;
5. arrêter uniquement `samstag.service` ;
6. déplacer l'application actuelle vers le dossier de retour arrière ;
7. déplacer la nouvelle version vérifiée vers `/opt/samstag/app` et rétablir son propriétaire ;
8. redémarrer uniquement `samstag.service` ;
9. contrôler l'accueil, les événements, la santé, les sources et les deux refus de la route administrative ;
10. vérifier les journaux, le minuteur de sauvegarde et l'absence d'impact sur les services voisins.

## Conditions de maintien

La nouvelle version est conservée seulement si, dans les dix minutes :

- le service reste actif sans boucle de redémarrage ;
- l'accueil, `/api/events`, `/api/health` et `/api/sources` répondent ;
- aucun incident nouveau n'apparaît par rapport au relevé initial ;
- la production affiche 39 canaux configurés, 37 actifs et 23 publications automatiques ;
- Nginx répond 403 sur `/api/refresh` et Flask refuse directement GET et POST sans autorisation ;
- aucune donnée fictive ou source exclue n'est publiée ;
- le minuteur de sauvegarde reste actif.

Le cycle de collecte suivant devra ensuite être observé avant de déclarer la livraison stabilisée.

## Retour arrière préparé

Le retour arrière applicatif est déclenché si le service ne démarre pas, si une API essentielle échoue, si la route administrative devient accessible ou si une régression publique importante apparaît.

1. arrêter uniquement `samstag.service` ;
2. conserver la version en échec dans un dossier daté pour diagnostic ;
3. remettre l'ancien dossier applicatif `ed42492` à son emplacement ;
4. redémarrer le service et répéter tous les contrôles publics ;
5. consigner les heures, le motif et l'état final.

Les nouvelles tables sont additives et ignorées par l'ancien code : un retour applicatif ne restaure donc pas automatiquement la base. Si une corruption ou une modification de données est constatée, préserver d'abord la base en échec puis décider séparément d'une restauration de la sauvegarde préalable. Cette décision évite de perdre inutilement des données reçues après la livraison.

## Après stabilisation

Conserver l'ancien dossier et la sauvegarde préalable jusqu'à la réussite du prochain cycle de collecte et de la prochaine sauvegarde planifiée. Compléter le [journal de livraison](JOURNAL_LIVRAISON_MODELE.md). La copie externe, l'alerte reçue et la mesure du temps de reprise resteront à traiter dans la suite du L4.
