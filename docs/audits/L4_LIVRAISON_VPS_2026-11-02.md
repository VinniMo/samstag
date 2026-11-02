# L4 — livraison applicative sur le VPS

**Date :** 2 novembre 2026  
**Autorisation :** application du sous-lot applicatif avec sauvegarde préalable et retour arrière préparé  
**Résultat :** version maintenue après contrôles et observation

## Résultat simple

La production utilise maintenant le paquet applicatif relié au commit `b593dc6`. L'accueil et les API publiques répondent, les 37 sources actives ont terminé un cycle, le MAD ne publie plus automatiquement et la route administrative est protégée à la fois par Nginx et Flask.

Une sauvegarde cohérente a été créée puis restaurée dans un fichier isolé avant le remplacement. L'ancienne application `ed42492` est conservée entière pour un retour arrière. Aucun retour arrière n'a été nécessaire.

## Preuves avant changement

| Contrôle | Résultat |
|---|---|
| Version active | `ed42492`, confirmée par quatre empreintes |
| Service | actif et activé au démarrage |
| Sauvegarde planifiée | minuteur actif |
| Dépendances Python | aucune incohérence déclarée |
| Santé | `ok`, aucun incident déclaré par l'ancienne version |
| Sources | 37 actives, 24 automatiques |
| Archive | empreinte extérieure correcte et 43 fichiers internes vérifiés |

## Sauvegarde et reprise

- sauvegarde préalable : `samstag-20261102T210014737231Z.sqlite3` ;
- restauration isolée : `pre-20261102T210014Z.sqlite3` ;
- intégrité SQLite : `ok` ;
- empreinte de la copie restaurée : `1af51781aaa521d30d0a7631fc686130c324b5c150b89f088f7a1c23c343fc6e` ;
- ancienne application conservée sous `/opt/samstag/rollback/app-20261102T210014Z-ed42492`.

La base active n'a pas été remplacée. Les nouvelles structures ont été créées de façon additive au démarrage.

## Contrôles après changement

| Contrôle | Résultat |
|---|---|
| Version déclarée | `b593dc6fea28eb7072e785f8d4cb3a833fd3bad3` |
| Service | actif, aucun redémarrage automatique |
| Accueil public | HTTP 200 |
| Événements publics | HTTP 200, 414 sorties |
| Sources | 39 configurées, 37 actives, 23 automatiques |
| Route publique `/api/refresh` | HTTP 403 par Nginx |
| Route Flask directe | GET 405, POST sans autorisation 404 |
| Sources exclues | aucune occurrence Buzz Club, Satellite ou bibliothèque dans les lieux publiés |
| Sauvegarde quotidienne | minuteur toujours actif |
| Erreurs du service | aucune entrée de niveau erreur depuis le démarrage |

Le premier cycle a duré environ 45 secondes et a contrôlé les 37 sources : 1 093 observations, 428 candidates, 665 refusées et 414 sorties publiques. Il se termine en état dégradé uniquement à cause du MAD : ses six fiches restent illisibles, mais sa publication automatique est désactivée.

## Observation de stabilité

Le service a été observé de 21:00:15 à 21:11:06 UTC. Les contrôles successifs ont conservé 414 sorties et un seul incident connu. Le service est resté actif sans redémarrage. Les critères de retour arrière n'ont pas été atteints ; la nouvelle version a donc été maintenue.

## Limite découverte

Le rapport d'alerte local classe Lausanne Tourisme, Vidy et Château Music Club en « jamais réussis ». Leur cycle réel montre pourtant un accès et une lecture corrects, avec une couverture qualifiée de partielle. L'envoi d'alertes n'est pas activé : sa logique doit considérer une lecture partielle réussie avant tout branchement vers un destinataire.

Cette limite ne réduit pas la publication actuelle : Vidy fournit 175 observations et 86 sorties, Lausanne Tourisme 40 observations conservées en contrôle, et Château Music Club signale proprement un programme vide. Elle devient la prochaine correction locale bornée du L4.

## Éléments non modifiés

Nginx, les unités systemd, les secrets, le fichier d'environnement, l'environnement Python, Render et les autres services n'ont pas été modifiés. La copie chiffrée hors VPS et l'envoi d'une alerte de test restent à réaliser séparément.
