# L4 — contrôle du VPS en lecture seule

**Date :** 2 novembre 2026  
**Périmètre :** étape D du plan L4  
**Accès :** lecture seule, autorisé explicitement par l'utilisateur

## Résultat simple

Le site public fonctionne et le socle d'exploitation est sain. Le service est actif, HTTPS répond, la configuration de production est appliquée, la session possède une clé persistante et les cookies sont sécurisés. La sauvegarde quotidienne a réussi ; la dernière des sept copies locales est intègre.

Le VPS exécute encore la version `ed42492` du 1er novembre. La copie déployée ne contient pas le dossier Git, mais les empreintes des quatre fichiers contrôlés correspondent toutes exactement à ce commit. Les améliorations L2 à L4 fusionnées depuis ne sont donc pas encore en production.

## Contrôles effectués

| Point | Résultat |
|---|---|
| Application | service actif et démarré automatiquement |
| Version Python | 3.12.3 |
| Version déployée | empreintes identiques au commit `ed42492` |
| Site public | page d'accueil HTTP 200 |
| Santé publique | HTTP 200, état `ok`, aucun incident déclaré |
| Sources publiques | 37 actives, dont 24 encore marquées pour publication automatique |
| Mode production | debug, démo et collecte à la visite désactivés |
| Session | secret persistant configuré, valeur non consultée ni consignée |
| Cookies | mode sécurisé activé |
| Actualisation manuelle publique | HTTP 403 par Nginx |
| Sauvegarde | minuteur actif, dernier passage réussi, prochaine exécution planifiée |
| Dernière copie locale | 2 novembre à 04:16 UTC, intégrité SQLite `ok`, permissions privées |
| Rétention locale | 7 copies |

## Écarts à traiter

1. **Protection Flask pas encore livrée.** Nginx bloque bien `/api/refresh` sur Internet, mais la version Flask active accepte encore GET et POST si elle est appelée en contournant le proxy. Le correctif local fusionné doit être livré lors d'une intervention autorisée.
2. **Production en retard sur le dépôt.** Les corrections et diagnostics fusionnés après `ed42492`, dont la désactivation automatique du MAD décidée le 2 novembre, ne sont pas déployés. La production annonce encore 24 sources automatiques, contre 23 dans le code actuel.
3. **Traçabilité indirecte.** Le dossier actif n'est pas un checkout Git. La version reste identifiable par empreintes, mais une livraison future devra enregistrer clairement commit, sauvegarde, contrôles et retour arrière.
4. **Sauvegardes sur le même VPS.** La sauvegarde locale protège contre une erreur de fichier, mais aucune copie chiffrée hors serveur n'est encore prouvée.
5. **Reprise et alertes non prouvées à distance.** Aucun test de restauration chronométré ni aucune alerte de test n'a été déclenché pendant ce contrôle en lecture seule.

## Limites du contrôle

Aucun fichier, service, minuteur, secret, certificat, base ou donnée n'a été modifié. Aucune collecte n'a été lancée. Les valeurs secrètes et le contenu des retours utilisateurs n'ont pas été lus. La restauration, le transfert externe et l'envoi d'alertes nécessitent des étapes séparées et autorisées.

## Décision proposée

Préparer localement un lot de livraison précis reliant le commit actuel à une sauvegarde et à un retour arrière. Ce lot devra inclure la protection Flask, l'alignement des diagnostics et du registre des sources, puis la copie chiffrée hors VPS. Son application sur le serveur demandera une nouvelle autorisation explicite.
