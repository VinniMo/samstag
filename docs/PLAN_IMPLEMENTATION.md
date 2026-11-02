# Plan d’implémentation Samstag

**État de référence : 1er novembre 2026.**
**Objectif :** rendre le développement, la collecte et l’exploitation de Samstag reproductibles, fiables et faciles à reprendre, sans modifier le design ni élargir silencieusement le périmètre éditorial.

Ce plan découle de l’[audit du 1er novembre](audits/AUDIT_2026-11-01.md). Il organise le travail en petits lots indépendants. Chaque lot doit conserver le site utilisable et produire une preuve vérifiable.

## Principes de mise en œuvre

1. Une session traite un objectif borné et se termine par des tests, un bilan et la mise à jour de la passation.
2. Aucun test de collecteur ne doit inventer de date, d’heure, d’adresse ou d’événement.
3. Les fixtures locales et bases jetables précèdent tout appel réel à une source.
4. Un changement d’organisation ne doit pas être mêlé à un changement fonctionnel.
5. Le design actuel est conservé, sauf décision explicite distincte.
6. Render reste hors périmètre. Toute intervention sur la production Infomaniak nécessite l’autorisation applicable et un retour arrière préparé.
7. Un canal inventorié, un lecteur fonctionnel et une source autorisée à publier sont trois états différents.

## Vue d’ensemble

| Lot | Résultat recherché | Dépend de | État |
|---|---|---|---|
| L0 | Référence documentaire et suivi communs | Audit | Terminé |
| L1 | Environnement local et CI reproductibles | L0 | Terminé |
| L2 | Diagnostics de collecte fiables | L1 | Terminé |
| L3 | Qualité des événements et dédoublonnage | L2 | À faire |
| L4 | Exploitation, sauvegardes et alertes prouvées | L1, L2 | À faire |
| L5 | Architecture interne progressivement clarifiée | L1 à L4 | À faire |
| L6 | Performance, SEO et accessibilité mesurés | L3 | À faire |

Le suivi quotidien se trouve dans [SUIVI_IMPLEMENTATION.md](SUIVI_IMPLEMENTATION.md). Les dépendances sont représentées dans [implementation-roadmap.mmd](diagrams/implementation-roadmap.mmd).

## L0 — Référence documentaire et suivi

### But

Disposer d’un seul point d’entrée qui indique l’état courant, les décisions actives et le prochain travail autorisé.

### Tâches

- [x] `L0.1` Auditer le site public, le code, les collecteurs et le dossier local.
- [x] `L0.2` Créer le présent plan, le suivi et les diagrammes Mermaid.
- [x] `L0.3` Créer `docs/ETAT_ACTUEL.md`, court et réécrit à chaque étape importante.
- [x] `L0.4` Réviser `README.md`, `PRODUCT.md` et `docs/EXPLOITATION.md` pour retirer les informations devenues fausses.
- [x] `L0.5` Classer les anciens documents comme historiques sans supprimer leurs preuves.
- [x] `L0.6` Ajouter un index des preuves externes absentes du dépôt et de leur emplacement.

### Critères de fin

- Un nouvel intervenant identifie en moins de cinq minutes le domaine public, le dépôt, la branche de référence, l’architecture, l’état des collecteurs et la prochaine tâche.
- Les documents actifs ne disent plus que le domaine est indécis ou que le site est uniquement accessible par tunnel.
- Les documents historiques portent une date et ne sont pas présentés comme l’état courant.

## L1 — Développement reproductible et CI

### But

Permettre à un nouveau checkout d’installer, tester et lancer Samstag avec des commandes stables et sans utiliser une base de production.

### Tâches

- [x] `L1.1` Déclarer Python 3.12 comme version de développement de référence.
- [x] `L1.2` Ajouter `.env.example` sans secret, avec une base locale absolue et la collecte sur visite désactivée.
- [x] `L1.3` Ajouter des commandes uniques : `setup`, `dev`, `test`, `e2e`, `check` et `report`.
- [x] `L1.4` Choisir et documenter un verrouillage reproductible des dépendances Python.
- [x] `L1.5` Rendre les chemins E2E indépendants d’un `.venv` portant un nom imposé.
- [x] `L1.6` Ajouter une CI Linux moderne : tests Python, syntaxe JavaScript, validation JSON et contrôle E2E selon la portée.
- [x] `L1.7` Ajouter une validation de schéma pour `sources.json`, `venues.json` et `bars.json`.

### Critères de fin

- Un checkout neuf exécute la suite Python complète avec une procédure unique documentée.
- La CI échoue sur un test métier cassé, un JSON invalide ou une erreur de syntaxe JavaScript.
- Aucune commande de développement ne contacte les 37 sources par défaut.
- Aucune donnée fictive n’apparaît sans activation explicite du mode démonstration.

## L2 — Diagnostics de collecte fiables

### But

Faire en sorte qu’un statut de source dise précisément si la source répond, si le lecteur fonctionne, quelle portion a été lue et si des événements peuvent être publiés.

### Tâches

- [x] `L2.0` Couvrir les 39 canaux du registre : diagnostic des 37 actifs et visibilité explicite des 2 désactivés, sans confondre canaux, lieux et bars inventoriés.
- [x] `L2.1` Remplacer les retours tuple résiduels Docks/Romandie par `CollectionResult`.
- [x] `L2.2` Ajouter les tests « toutes les fiches échouent » et « une partie des fiches échoue ».
- [x] `L2.3` Distinguer quatre dimensions : accès, parsing, complétude de la passe, qualification éditoriale.
- [x] `L2.4` Ajouter un identifiant de passe et des compteurs par source : pages attendues/lues, observations, candidats, refus, publications et retraits.
- [x] `L2.5` Rendre `/api/health` actionnable : incident réel séparé d’une limitation connue et permanente.
- [x] `L2.6` Diagnostiquer uniquement le MAD, préserver les preuves et corriger son lecteur si la source officielle le permet.
- [x] `L2.7` Définir la rétention des journaux et observations techniques.

### Critères de fin

- Une panne de toutes les fiches ne peut plus être déclarée `empty` ou `ok`.
- Une source volontairement bornée n’empêche pas à elle seule de voir un incident nouveau.
- Le rapport d’une passe explique l’écart entre entrées lues et sorties publiques.
- Le MAD est soit rétabli, soit explicitement désactivé de la publication automatique avec justification datée.

## L3 — Qualité des événements et dédoublonnage

### But

Réduire les doublons sans fusionner des représentations distinctes ni perdre les preuves officielles.

### Tâches

- [ ] `L3.1` Transformer le cas « Mike D / Mike D 5D » en fixture et test de régression.
- [ ] `L3.2` Calculer des candidats au rapprochement sur lieu canonique, date et heure.
- [ ] `L3.3` Donner priorité à la source officielle lorsque les occurrences sont confirmées comme identiques.
- [ ] `L3.4` Mettre en revue les rapprochements ambigus au lieu de les fusionner automatiquement.
- [ ] `L3.5` Conserver toutes les URL de preuve après rapprochement.
- [ ] `L3.6` Ajouter un rapport des doublons probables sans modifier les données.
- [ ] `L3.7` Contrôler à la source les horaires atypiques de Taco’s avant toute correction.

### Critères de fin

- Le cas Mike D ne produit plus deux sorties publiques identiques.
- Deux spectacles distincts au même lieu et à la même heure restent séparés.
- Chaque fusion est explicable par ses sources et peut être annulée.
- Le nombre de rapprochements automatiques et ambigus apparaît dans le rapport.

## L4 — Exploitation et reprise après incident

### But

Prouver que le service peut être surveillé, sauvegardé et restauré sans dépendre d’une seule machine.

### Tâches

- [ ] `L4.1` Vérifier sur le VPS les unités, versions, variables non secrètes et empreintes réellement actives.
- [ ] `L4.2` Confirmer une clé de session persistante et `COOKIE_SECURE=1` sans révéler les secrets.
- [ ] `L4.3` Désactiver ou authentifier `/api/refresh` dans Flask, en plus du blocage Nginx.
- [ ] `L4.4` Automatiser une copie chiffrée hors VPS avec rétention définie.
- [ ] `L4.5` Tester une restauration dans un fichier isolé : intégrité, comptages et lecture applicative.
- [ ] `L4.6` Définir RPO, RTO et procédure de retour arrière.
- [ ] `L4.7` Alerter avant que les événements d’une source importante deviennent invisibles après 24 heures.
- [ ] `L4.8` Définir la conservation et l’accès aux retours utilisateurs.
- [ ] `L4.9` Documenter un journal de livraison : commit, sauvegarde, vérifications et rollback.

### Critères de fin

- Une sauvegarde hors VPS et sa restauration ont été vérifiées et datées.
- Une alerte de test a été reçue sans provoquer d’incident public.
- La route de rafraîchissement reste inaccessible publiquement même si le proxy est contourné.
- La version déployée est reliée à un commit revu et à une procédure de retour arrière.

## L5 — Clarification progressive de l’architecture

### But

Réorganiser le code par responsabilités sans réécriture globale et sans modifier simultanément le comportement des collecteurs.

Le [plan détaillé de réorganisation](PLAN_REORGANISATION_CODE.md) découpe ce chantier en sessions R0 à R7, avec pilote Vidy, contrôles et retour arrière. Les changements fonctionnels L5.5 à L5.7 restent des lots distincts du rangement.

### Ordre proposé

1. `L5.1` Introduire un paquet `samstag/` et conserver temporairement les points d’entrée actuels comme wrappers.
2. `L5.2` Séparer routes web, domaine agenda, stockage et collecte.
3. `L5.3` Extraire le client HTTP et les politiques de délai/encodage.
4. `L5.4` Déplacer les lecteurs dans `collection/adapters/` avec un module nommé par source ou format.
5. `L5.5` Remplacer le dispatch conditionnel par un registre explicite d’adaptateurs.
6. `L5.6` Ajouter des migrations SQLite versionnées et testées sur une copie isolée.
7. `L5.7` Définir des objets de contrat pour événement brut, décision qualité et occurrence publique.
8. `L5.8` Séparer l’instance WSGI des effets de bord d’initialisation.

### Critères de fin

- Les anciennes commandes restent fonctionnelles pendant la transition.
- Chaque déplacement passe les tests avant le déplacement suivant.
- Une PR d’architecture ne change pas les sorties publiques attendues.
- Le schéma d’une base existante peut évoluer et revenir en arrière selon une procédure documentée.

## L6 — Produit, performance et visibilité

### Décision produit actée le 1er novembre 2026

Inclure les événements diurnes dans les catégories déjà admises, à Lausanne et dans les communes immédiatement voisines. Les expositions et longues périodes ne sont pas automatiquement incluses par cette décision. Préserver les exclusions et la validation des dates, horaires et lieux.

### Tâches

- [ ] `L6.1` Inclure les événements diurnes : retirer le rejet systématique de 6 h à 16 h 59, vérifier les filtres propres aux adaptateurs et aux registres, tester les frontières de journée et les périodes d’affichage, puis mesurer la couverture sur une base isolée. Conserver les preuves et les contrôles de qualité ; livraison de production séparée et autorisée.
- [ ] `L6.2` Définir un contrat API public allégé, distinct des preuves internes.
- [ ] `L6.3` Mesurer puis activer la compression et une stratégie de cache adaptée.
- [ ] `L6.4` Actualiser les données au retour sur un onglet ancien, avec fréquence bornée.
- [ ] `L6.5` Paginer ou charger progressivement « Plus tard » sans casser la recherche.
- [ ] `L6.6` Créer des URL événement partageables avec métadonnées sociales.
- [ ] `L6.7` Ajouter `robots.txt` et un sitemap après validation du modèle d’URL.
- [ ] `L6.8` Réaliser un audit mobile, zoom, clavier et lecteur d’écran avec correctifs bornés.
- [ ] `L6.9` Synchroniser les tokens de `DESIGN.md` avec les couleurs réellement approuvées.

### Avancement diurne au 1er novembre 2026

Code local adapté : validation sans exclusion horaire, confirmation Vidy et enrichissement JazzOnze+ en journée, période « Aujourd’hui » de 6 h à 6 h le lendemain. Contrôles synthétiques sur base isolée ; aucune mesure de couverture des programmes réels et aucune livraison en production. `L6.1` reste ouvert pour ces deux étapes.

### Critères de fin

- Les mesures avant/après montrent le gain de poids et de temps de rendu.
- Une fiche partagée expose le bon titre, la bonne description et la bonne image quand elle existe.
- Les parcours principaux restent utilisables à 320 px, au clavier et avec zoom à 200 %.
- Le design approuvé reste reconnaissable.

## Première séquence recommandée

### Session A — Base de développement

Terminée le 1er novembre 2026 : documentation actuelle, environnement local sûr, dépendances verrouillées, commandes stables, schémas JSON et CI.

### Session B — CI et registres

Traiter `L1.4` à `L1.7`. Sortie attendue : contrôle automatique d’un checkout neuf et validation des trois registres JSON.

### Session C — Premier défaut de collecte

Traiter `L2.1` et `L2.2` uniquement. Sortie attendue : une panne Docks/Romandie correctement classée, tests ciblés et aucun appel général aux sources.

### Session D — MAD ciblé

Traiter `L2.6` uniquement. Lire d’abord le diagnostic public, puis consulter la seule source MAD si nécessaire. Sortie attendue : lecteur rétabli ou décision explicite et réversible.

### Session E — Dédoublonnage conservateur

Traiter `L3.1` à `L3.6` sur fixtures et base isolée. Sortie attendue : rapport de rapprochement et correction du cas Mike D sans fusion risquée.

## Règle de mise à jour du suivi

À chaque session :

1. déplacer les tâches concernées dans la bonne section de `SUIVI_IMPLEMENTATION.md` ;
2. inscrire la date, la branche ou le commit, les tests et les limites ;
3. mettre à jour les classes `done`, `doing`, `blocked` ou `todo` dans `implementation-roadmap.mmd` ;
4. ajouter un court résumé à `PASSATION_PROJET.md` ;
5. ne marquer un lot terminé que lorsque tous ses critères de fin sont vérifiés.
