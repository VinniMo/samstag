# Politique locale — alertes, sauvegardes et retours

**Définie et corrigée localement le 2 novembre 2026, sans activation distante.** Les adresses, identifiants de stockage et secrets restent dans la configuration privée.

## Alertes de collecte

Les alertes concernent d'abord les sources actives autorisées à publier automatiquement. Une limite connue ou une source en revue reste visible dans le rapport, mais ne déclenche pas la même urgence.

| Situation | Niveau | Action attendue |
|---|---|---|
| Nouvelle erreur d'accès ou de lecture | Attention | vérifier le diagnostic lors du prochain passage |
| Aucune collecte réussie depuis 18 heures | Attention | contrôler la source avant le masquage à 24 heures |
| Aucune collecte réussie depuis 24 heures | Critique | intervenir ou désactiver proprement la publication concernée |
| Source automatique jamais collectée avec succès | Critique | empêcher qu'elle soit considérée comme opérationnelle |

Le rapport local `operations_report.py` calcule ces niveaux sans lancer de collecte et sans envoyer de message. Une future activation l'exécutera au moins chaque heure. Deux alertes identiques ne devront pas être renvoyées plus d'une fois en six heures ; un message de rétablissement devra suivre le retour à la normale.

Une lecture est réussie pour la fraîcheur lorsque l'accès et l'analyse sont tous deux `ok`, même si la couverture reste partielle ou exige une revue éditoriale. Une erreur d'accès ou d'analyse ne renouvelle jamais cette heure de réussite. Cette distinction évite de classer Vidy, Lausanne Tourisme et Château Music Club comme « jamais réussis » alors que leur dernier passage technique a abouti.

Le canal retenu est une adresse e-mail d'exploitation privée, indépendante du VPS. L'adresse exacte ne sera stockée que dans la configuration privée. Une alerte critique non traitée sous une heure devra être transmise au propriétaire du service par un second moyen à définir avant activation.

## Sauvegardes

- copie locale cohérente chaque jour, sept exemplaires ;
- attention si la dernière copie date de 20 heures, critique à 24 heures ;
- copie externe après chaque sauvegarde locale, chiffrée avant transfert ;
- stockage objet privé distinct du VPS, avec accès limité au dépôt et à la restauration ;
- rétention externe : 30 copies quotidiennes et 12 copies mensuelles ;
- reçu sans donnée privée : date, identifiant, taille, empreinte et résultat du transfert ;
- test de restauration isolée chaque trimestre et avant un changement important du stockage.

Le fournisseur et le compte exacts restent à choisir. Aucun transfert ne sera activé tant que les identifiants privés, le coût et la procédure de récupération n'auront pas été validés.

## Retours utilisateurs

Les retours ne contiennent ni nom, ni e-mail, ni adresse IP, mais leur texte peut rester privé.

- accès réservé au compte de service et aux administrateurs autorisés via SSH ;
- aucune route web de lecture, aucun export dans Git ou dans les journaux ;
- lecture au moins une fois par semaine ;
- retour résolu supprimé au plus tard 90 jours après sa résolution ;
- retour non résolu réévalué après 12 mois et supprimé s'il n'est plus nécessaire ;
- sauvegardes contenant des retours soumises aux mêmes règles de chiffrement et d'accès ;
- toute exportation exceptionnelle doit être chiffrée, datée et supprimée après usage.

L'automatisation de la suppression demandera un champ de date de résolution et une migration SQLite versionnée. Jusqu'à cette migration, la suppression reste une opération administrative explicite et ne doit jamais être déclenchée pendant un simple contrôle.

## Informations à conserver dans une preuve

Conserver le niveau, l'heure, la source concernée, l'ancienneté, la réception et la résolution. Ne jamais conserver dans la preuve l'adresse privée du destinataire, un secret, le contenu d'un retour ou une base de données.
