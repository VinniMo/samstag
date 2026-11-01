# Proposition de mise en service — REFUSÉE, ne pas activer

Préparée le 17 octobre 2026, puis explicitement refusée par l’utilisateur pour raison de coût. Conservée comme historique technique. Priorité aux solutions gratuites et à l’achat Infomaniak existant ; produit exact à identifier. Aucun réglage du compte Render modifié.

## Service réellement inspecté en lecture seule

- Service : `lausanne-cultura`, [tableau de bord Render](https://dashboard.render.com/web/srv-db6lb6rl550s73bf6jcg).
- Formule actuelle : **free**, une instance, région Oregon.
- Dépôt : `https://github.com/VinniMo/lausanne-cultura`, branche `main`.
- Déploiement automatique activé sur les commits de cette branche. **Ne pas pousser la nouvelle version sur `main` avant accord de mise en ligne.**
- Dernière version en ligne : `759326d0fc36dfb6e7b2208c3fff07182a785ba1`, déploiement du 12 octobre 2026. Les corrections locales v3 ne sont pas sur cette version.
- Commande actuelle : `gunicorn app:app --bind 0.0.0.0:$PORT --workers 2 --timeout 60` ; commande proposée après accord : `python run_service.py`.
- Le compte Render est maintenant accessible par la connexion dédiée. Les variables secrètes et le contenu de la base distante n’ont pas été lus ; les protections existantes devront être conservées lors de la mise en service.

Le relevé non secret est sauvegardé dans `validation/qualification-2026-10-17/render-inspection.json`. Aucune action de modification ou de déploiement n’a été appelée.

## Proposition simple

Conserver Render et utiliser **un seul service toujours actif avec un disque persistant**, qui héberge le site et sa collecte. Le nouveau point d’entrée `run_service.py` démarre et surveille les deux processus avec la même base SQLite. Si l’un s’arrête inopinément, l’autre est arrêté et le service sort en erreur pour permettre un redémarrage par l’hébergeur. Une source culturelle partielle ne provoque pas le redémarrage du service : le collecteur poursuit ses cycles.

Le stockage doit être réellement monté sur le chemin prévu ; le logiciel ne peut pas vérifier à lui seul que l’hébergeur rend un dossier persistant.

## Budget à valider

Tarifs publics relevés le 17 octobre 2026 sur [Render Pricing](https://render.com/pricing) :

| Élément | Proposition | Coût mensuel de base |
|---|---|---:|
| Espace de travail | Hobby | 0 USD, hors services |
| Calcul toujours actif | 0,5 CPU / 512 Mo (`0.5c-512mb`) | 7 USD |
| Disque persistant | 1 Go à 0,25 USD/Go | 0,25 USD |
| **Total indicatif** | | **7,25 USD/mois** |

Hors taxes, conversion monétaire et dépassements éventuels. Aucun achat ni abonnement créé. L’essai local ne démontre pas la consommation mémoire sur l’instance Linux de 512 Mo : commencer avec un seul processus web et surveiller la mémoire. Si cette taille est insuffisante, présenter une nouvelle proposition avant toute augmentation payante ; ne pas changer automatiquement de formule.

## Activation à réaliser seulement après accord explicite

1. Le service, le dépôt et la branche ont été confirmés en lecture seule. Avant activation, vérifier les protections d’accès et sauvegarder les données existantes, dont le contenu n’a pas été inspecté. Le fichier `render.yaml` historique ne suffit pas à établir l’état réel du compte.
2. Sauvegarder le code et la base de production avant migration ; vérifier leur restauration séparée. Si un stockage persistant contient déjà une base, ne pas la remplacer par la base de tests.
3. Préparer une version Git identifiable contenant le candidat validé ; les archives locales ne sont pas encore un commit publié. Revoir le changement avant de publier le code et déclencher un déploiement.
4. Après confirmation du budget : choisir le calcul toujours actif et attacher un disque de 1 Go à `/var/data` sur **ce même service web**. Un disque Render ne peut pas être partagé avec un worker séparé : voir la [documentation des disques](https://render.com/docs/disks).
5. Configurer :

```text
LAUSANNE_DB=/var/data/cultura.sqlite3
HOST=0.0.0.0
WEB_WORKERS=1
SCRAPE_INTERVAL=3600
COLLECTION_WORKERS=2
SERVICE_STOP_GRACE=25
FLASK_DEBUG=0
DEMO_ENABLED=0
COLLECTION_ON_VISIT=0
```

6. Utiliser Python 3.11 ou plus récent (suite testée avec Python 3.12.14), installer `requirements.txt` et remplacer la commande de lancement par `python run_service.py`. Garder le port fourni par Render (`PORT`) et les protections d’accès existantes. Ne pas saisir de secrets dans le dépôt.
7. Vérifier la configuration avec `python run_service.py --check-config`. Cette commande ne démarre ni site ni collecte et n’affiche pas les identifiants d’accès.
8. Déployer, vérifier la collecte initiale, les pages et les sorties de plusieurs semaines, puis les mises à jour sans visite. Contrôler l’absence de Satellite, Buzz Club et événements fictifs.
9. Observer au moins 24 heures, y compris un redémarrage contrôlé, vérifier la conservation des données, la mémoire et les sauvegardes. L’essai local ne remplace pas cette observation.

Le `render.yaml` existant est laissé inchangé. Cette proposition n’active pas un second service et ne change pas la formule actuelle.

## Arrêt et sauvegardes

`SIGTERM`/`SIGINT` déclenchent l’arrêt des deux processus. Ils disposent d’un délai configurable ; au-delà, les groupes de processus sont arrêtés de force. Utiliser 25 secondes si le délai de l’hébergeur est de 30 secondes ; vérifier cette valeur dans les réglages réels avant activation. Une interruption brutale peut laisser un verrou SQLite jusqu’à son expiration ; le prochain cycle évite les écritures concurrentes.

Prévoir des exports SQLite cohérents et une copie **hors du service**. La présence d’un disque et d’un script de restauration local ne constitue pas une sauvegarde externe automatisée. Aucun stockage externe ni plan de sauvegarde payant n’a été activé par cette préparation.

En cas d’échec après activation, arrêter les écritures et restaurer ensemble le code et la sauvegarde validée. Ne pas revenir au service éphémère en pensant que sa base temporaire remplacera le disque durable.
