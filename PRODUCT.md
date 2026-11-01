# Produit Samstag

**Référence produit au 1er novembre 2026.**

Samstag aide les habitants de Lausanne à choisir rapidement une sortie et à découvrir des lieux. Le service public est disponible sur [samstagloz.ch](https://samstagloz.ch). L’application Flask sur le VPS Infomaniak est la production de référence.

## Promesse

> Les sorties à Lausanne, réunies dans un agenda pratique pensé d’abord pour mobile.

Le périmètre actif comprend bars, clubs, concerts, spectacles et cinéma à Lausanne et dans les communes immédiatement voisines. La collecte doit couvrir plusieurs semaines. Décision du 1er novembre 2026 : inclure également les événements diurnes dans ces catégories. Le code local accepte les horaires diurnes et les affiche dans « Aujourd’hui », avec les sorties nocturnes jusqu’à 6 h le lendemain. Livraison en production et mesure de couverture réelle restent à faire. Cette décision n’élargit pas automatiquement les types admis aux expositions ou aux longues périodes.

## Utilisateurs et usages

Le public cherche quoi faire en journée, ce soir, ce week-end ou dans les semaines à venir. Il doit pouvoir :

- parcourir les événements par période et catégorie ;
- rechercher un artiste, un lieu ou un type de sortie ;
- ouvrir une fiche et rejoindre la source officielle ;
- adapter l’affichage à ses thèmes et lieux préférés ;
- partager une sortie et transmettre un retour.

Le service est en français, utilise les prix en francs suisses lorsqu’ils sont connus et ne nécessite pas de compte. Les préférences restent locales au navigateur.

## Données et qualité

Au 1er novembre 2026, le registre contient 39 sources, dont 37 actives et 24 autorisées à publier sous conditions. L’instantané public contrôlé contient 322 événements sur 19 lieux. Ces chiffres varient avec les programmes et la fraîcheur des sources.

Les données manquantes restent manquantes. Aucune date, heure, adresse ou sortie n’est complétée par supposition. Les preuves doivent être conservées et les lieux physiques distingués des programmateurs et agrégateurs.

Instagram est reporté. Buzz Club, Satellite et les bibliothèques sont exclus. Les annonces de location de salle sans événement public sont rejetées.

## Principes produit

1. **Décider vite.** Les périodes, catégories et informations essentielles sont immédiatement visibles.
2. **Faire découvrir.** Les petits lieux et scènes indépendantes ont leur place avec les institutions.
3. **Rester honnête.** Une information inconnue n’est jamais inventée.
4. **Préserver les preuves.** Une sortie publiée doit rester reliée à ses sources.
5. **Respecter les préférences.** La personnalisation fonctionne sans compte et reste récupérable.
6. **Préserver le design.** Les travaux techniques ne redessinent pas silencieusement le produit.

## Décisions encore ouvertes

- règle éditoriale de mise en avant ;
- mesure réelle des usages et de la couverture ;
- modèle économique éventuel.

Les travaux correspondants sont suivis dans [docs/PLAN_IMPLEMENTATION.md](docs/PLAN_IMPLEMENTATION.md). L’état mesuré et les limites sont dans [docs/ETAT_ACTUEL.md](docs/ETAT_ACTUEL.md).
