# Samstag sur le VPS Lite Infomaniak

Installation isolée réalisée le 18 octobre 2026. Aucun changement Render, DNS, Nginx ou application immobilière.

## Organisation

- Code : `/opt/samstag/app` (propriétaire root, lecture seule pour le service).
- Python 3.12 et dépendances propres : `/opt/samstag/venv`.
- Utilisateur système sans connexion interactive : `samstag`.
- Base persistante : `/var/lib/samstag/samstag.sqlite3`.
- Configuration : `/etc/samstag/samstag.env` ; unité `/etc/systemd/system/samstag.service`.
- Écoute uniquement sur `127.0.0.1:8011`, un processus web et deux fils de collecte ; aucune publication réseau directe.
- Collecte à intervalle d’une heure après la fin de la passe précédente. Démonstration, debug et collecte sur visite désactivés.
- Limites : 512 Mio de mémoire, quota CPU 50 %, priorité réduite. Mémoire disponible avant installation environ 1,4 Gio ; disque environ 15 Go libres.
- Application immobilière inchangée sur le port local 8000. Aucun redémarrage de ses services.

## Vérification et exploitation

85 tests réussis sur le VPS sous Python 3.12.3. Unité vérifiée avec systemd ; service démarré en interne. Son démarrage automatique au boot reste désactivé jusqu’à la mise en ligne. Le service reste actif tant que le serveur ne redémarre pas, avec reprise après échec.

Consulter : `systemctl status samstag.service` et `journalctl -u samstag.service`. Vérifier les quatre routes `/`, `/api/events`, `/api/health`, `/api/sources` sur le port local 8011. Le statut web `ok` ne signifie pas que toutes les sources sont qualifiées ; lire `collection`.

Sauvegarde quotidienne locale à 04:15 UTC (décalage aléatoire jusqu’à 5 minutes), sept copies dans `/var/lib/samstag/backups`. Sauvegarde SQLite cohérente par API et contrôle d’intégrité ; minuterie activée. Ces copies restent sur le même VPS et ne protègent pas contre sa perte complète. Après la première collecte terminée, produire une nouvelle sauvegarde et contrôler la restauration.

Pour arrêter le candidat : `sudo systemctl stop samstag.service`. Ne pas toucher à `cockpit-immobilier.service`, MariaDB, Nginx ou aux clés existantes.

## Avant publication

Confirmer le nom de domaine avec l’utilisateur ; préparer un hôte Nginx séparé et HTTPS. Bloquer l’accès public à `/api/refresh` (collecte interne planifiée suffisante), conserver le site immobilier inchangé, tester la configuration avant toute recharge Nginx et préparer le retour arrière. Pas de nouvel achat ou abonnement. Aucun accès public tant que cette étape n’est pas effectuée.

Après publication : activer le démarrage automatique de Samstag, vérifier depuis l’extérieur, puis observer plusieurs cycles et sauvegardes sur 24 heures. Une courte observation ne constitue pas une validation de disponibilité sur une journée.
