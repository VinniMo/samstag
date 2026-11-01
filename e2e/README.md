# Parcours Samstag avec Playwright

La suite lance la vraie application Flask, ses modèles et ses fichiers statiques sur le port local 8768. La base est jetable et distincte du VPS. Les événements proviennent de la réponse publique enregistrée dans `e2e/fixtures/public-snapshot.json` (copie des données publiques vérifiées le 19 octobre). L’horloge produit est figée à la date de cet instantané pour que les tests ne deviennent pas caducs au fil des jours. Les sessions et les retours utilisent leurs véritables routes ; aucune collecte distante n’est déclenchée.

## Exécution

Installer les dépendances de ce dossier avec `pnpm install --frozen-lockfile --ignore-scripts`, puis exécuter `pnpm test`. Python est pris dans le `.venv` applicatif existant. Playwright 1.48.2 correspond aux navigateurs disponibles compatibles avec macOS 13 ; les versions actuelles devront aussi être vérifiées sur un hôte pris en charge avant de revendiquer une compatibilité avec les navigateurs les plus récents.

Cinq profils : Chromium, Firefox, WebKit, Chromium mobile émulé et WebKit mobile émulé. Douze parcours par profil, sans nouvelle tentative automatique. Les moteurs mobiles émulés ne remplacent pas un téléphone physique.

Les tests de partage simulent les API système natives et le presse-papiers pour vérifier les informations transmises et le lien profond. Ils ne valident pas la feuille de partage d’iOS/Android.

Les liens externes sont vérifiés comme destinations dans les fiches ; la suite ne garantit pas la disponibilité de chaque site d’organisateur. Les rapports ne constituent pas un audit complet de sécurité, de performances ou d’accessibilité.

Les retours envoyés portent le préfixe TEST PLAYWRIGHT et restent dans `validation/playwright-2026-10-19/parcours-test.sqlite3`. Le serveur est arrêté par Playwright après l’exécution. Rapport HTML et traces d’échec dans `validation/playwright-2026-10-19/`. Ne pas archiver `node_modules/` dans un candidat de livraison.
