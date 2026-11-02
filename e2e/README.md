# Parcours Samstag avec Playwright

La suite lance la vraie application Flask, ses modèles et ses fichiers statiques sur le port local 8768. La base est jetable et distincte du VPS. Les événements proviennent de la réponse publique enregistrée dans `e2e/fixtures/public-snapshot.json` (copie des données publiques vérifiées le 19 octobre). L’horloge produit est figée à la date de cet instantané pour que les tests ne deviennent pas caducs au fil des jours. Les sessions et les retours utilisent leurs véritables routes ; aucune collecte distante n’est déclenchée.

## Exécution

Depuis la racine, `make setup` installe les dépendances et navigateurs, puis `make e2e` lance la suite. Le chemin Python est transmis par `SAMSTAG_PYTHON` et ne dépend plus d’un dossier `.venv` imposé. `make e2e E2E_ARGS=--project=chromium` limite la passe à Chromium. Playwright 1.48.2 reste verrouillé pour préserver la campagne historique ; les versions actuelles devront aussi être vérifiées sur un hôte pris en charge avant de revendiquer une compatibilité avec les navigateurs les plus récents.

Cinq profils : Chromium, Firefox, WebKit, Chromium mobile émulé et WebKit mobile émulé. Douze parcours par profil, sans nouvelle tentative automatique. Les moteurs mobiles émulés ne remplacent pas un téléphone physique.

Les tests de partage simulent les API système natives et le presse-papiers pour vérifier les informations transmises et le lien profond. Ils ne valident pas la feuille de partage d’iOS/Android.

Les liens externes sont vérifiés comme destinations dans les fiches ; la suite ne garantit pas la disponibilité de chaque site d’organisateur. Les rapports ne constituent pas un audit complet de sécurité, de performances ou d’accessibilité.

Les retours envoyés portent le préfixe TEST PLAYWRIGHT et restent dans `.local/samstag-e2e.sqlite3`. Le serveur est arrêté par Playwright après l’exécution. Rapport HTML et traces d’échec dans `.artifacts/playwright/`. Ne pas archiver `node_modules/`, `.local/` ni `.artifacts/` dans un candidat de livraison.
