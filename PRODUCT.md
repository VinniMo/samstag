# Product

<!-- impeccable:product-schema 1 -->

## Platform

web

## Users

Habitants de Lausanne, en priorité les jeunes (tranche d'âge exacte non fixée). Ils cherchent quoi faire ce soir ou ce week-end et veulent trouver vite une sortie, y compris dans des lieux qu'ils ne connaissent pas encore.

« Jeune » renvoie d'abord à un usage pratique, pas à un style : un visuel clair, des événements qui les concernent, un outil qui va droit au but.

Le site est pensé d'abord pour le mobile (selon le README ; usage mobile majoritaire non mesuré).

## Product Purpose

Rassembler en un seul endroit toute la vie culturelle et nocturne de Lausanne, des grandes institutions jusqu'aux bars et petits lieux, pour aider à **décider vite** et à **découvrir**.

Succès, dans l'ordre :
1. Devenir la référence de l'agenda culturel lausannois pour les jeunes.
2. Ensuite, éventuellement, monétiser : publicité ou petit abonnement (ordre de grandeur évoqué : CHF 5 par an). Modèle non décidé.

## Positioning

L'agenda officiel de la Ville (agenda.lausanne.ch) a un registre très classique et n'affiche pas les événements des bars et des petits lieux. Samstag s'adresse aux jeunes et combine les agendas officiels avec les programmes des salles indépendantes, clubs et petits lieux, que personne ne réunit aujourd'hui en un seul endroit.

## Operating Context

- Les événements sont collectés automatiquement (scraping) sur 27 sources : 5 agendas généralistes et 22 lieux (théâtres, salles de concert, clubs, musique classique, musées, cinémas). Liste dans `config.py`.
- La collecte se relance au plus une fois par heure, quand quelqu'un consulte le site ; elle peut aussi être forcée via `/api/refresh`.
- Chaque événement est classé automatiquement par mots-clés dans un thème. En cas de doute, il tombe dans « Culture ».
- La qualité des données collectées varie selon la source : prix souvent absent (« Voir détails »), horaire, image ou adresse parfois manquants, lieu parfois réduit à « Lausanne ». L'interface doit fonctionner avec des fiches incomplètes.

## Capabilities and Constraints

- Fonctions actuelles : recherche par mot-clé, filtre par thème, sélection « À ne pas manquer », fiche détaillée avec lien vers le site officiel de l'événement.
- Thèmes : Musique, Théâtre, Exposition, Cinéma, Danse, Festival, Famille, Conférence, Sport, Humour, Atelier, Marché, Clubbing (+ « Culture » par défaut).
- Pas de compte utilisateur ni de billetterie.
- Prévu dans la refonte de l'accueil : partager un événement ; filtre « gratuit / petit prix » (limité tant que les prix collectés manquent souvent) ; **mes goûts** : choisir les thèmes et lieux qui intéressent, masquer ceux qui n'intéressent jamais (exemple : ne plus voir l'Opéra), enregistrés sur le téléphone, sans compte.
- Langue : français uniquement. Contexte suisse (prix en CHF).
- Hébergement de référence : VPS Lite Infomaniak, service Flask interne accessible
  par tunnel. Aucun domaine public dédié n'est encore configuré.
- Décisions ouvertes :
  - **Bars et petits lieux** : objectif central, mais aucun bar ne figure encore dans les sources collectées.
  - Tranche d'âge exacte du public cible.
  - Modèle de monétisation (publicité ou abonnement) et calendrier.
  - Date d'ouverture publique (retrait du mot de passe).
  - La mise en avant « À ne pas manquer » repose sur un marqueur que les événements collectés ne reçoivent jamais ; faute de marqueur, le site affiche les premiers événements avec image. Règle de sélection éditoriale à définir.

## Brand Commitments

- Nom : **Samstag**.
- Logo approuvé : minuscules grasses, dernier « a » en miroir bleu outremer ;
  signature « Les sorties à Lausanne ».
- Registre voulu : direct et pratique, à l'opposé du ton institutionnel et classique de l'agenda officiel.

## Evidence on Hand

- `seed_data.py` : 25 événements de **démonstration fictifs** (photos de banque d'images Unsplash, liens vides `#`). Ils servent seulement quand la collecte ne renvoie rien. Ne jamais les présenter comme de vrais événements.
- Le pied de page crédite agenda.lausanne.ch comme source de données.
- Absents du dépôt, à ne pas inventer : chiffres d'audience, témoignages d'utilisateurs, partenariats avec des lieux, articles de presse, nombre d'abonnés ou tarifs définitifs.

## Product Principles

1. **Décider vite.** La question « que faire ce soir ou ce week-end ? » doit trouver une réponse en quelques secondes.
2. **Faire découvrir.** Les petits lieux et les scènes alternatives ont autant de place que les grandes institutions.
3. **Droit au but.** Un visuel clair et pratique : chaque élément aide à choisir, rien ne retarde la décision. Ton direct, loin du registre institutionnel.
4. **Honnêteté des données.** Afficher ce qui est connu, signaler clairement ce qui manque, ne jamais combler un trou par une information inventée.
5. **Chacun son fil.** Chacun voit d'abord ce qui l'intéresse ; ce qui est masqué reste signalé et récupérable d'un geste.


## Pilote bars — préparation locale du 16 octobre 2026

La demande actuelle recentre le premier lot sur les sorties animées, en priorité
les bars du centre et de Sous-Gare. Salles et bibliothèques restent hors de ce
premier périmètre. Le Buzz Club est exclu. Le registre comprend 28 bars repérés,
avec leurs preuves et incertitudes ; sept sources sont consultées par le pilote.
Les anciens thèmes et lieux décrits ci-dessus constituent le contexte historique.
La validation initiale des sources est manuelle ; une automatisation complète
reste à qualifier source par source. Aucune mise en production n'est autorisée.


## Moteur élargi — version locale du 16 octobre 2026

Le pilote bars est remplacé par le registre consolidé des sorties du soir.
La configuration courante comporte 26 canaux activés, dont 10 qualifiés pour
publication conditionnelle automatique. Le contrôle local a exposé 70 sorties
réelles : concerts, clubs, séances de cinéma et humour. Ce volume est un instantané.
Le détail des actions et limites est dans `docs/RECAP_COLLECTE.md`. Les salles
génériques, bibliothèques et Buzz Club restent écartés. Le design existant est
conservé ; le texte distingue les portes du début artistique. Render reste intact.


## 22 octobre 2026 — nom adopté et consignes rédactionnelles
- Marque publique : **samstag**, en remplacement de Lausanne Cultura. Le nom des services et les clés de préférences existantes restent techniques et inchangés.
- Logo gras approuvé, dernier a en miroir bleu outremer. Le lettrage léger n'est pas retenu.
- L'agenda conserve toutes ses périodes ; « Les sorties à Lausanne » précise son rôle.
- Préférence utilisateur : textes pratiques et courts ; supprimer les précisions inutiles sur l'enregistrement local dans la personnalisation.
