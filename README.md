# Sélection d'applications — uneIAparjour

Page complète (roue interactive HTML/SVG + liste des applications + archives) des
applications d'IA générative sélectionnées par
[Une IA par jour](https://www.uneiaparjour.fr), classées en 10 catégories × 3 niveaux
d'appropriation (Pour découvrir / Pour aller plus loin / Usage avancé).

**Démo en ligne :** `selection-outils.html` (FR) et `selection-outils-en.html` (EN) —
hébergées via GitHub Pages et embarquées en iframe sur la page
[/selection/](https://www.uneiaparjour.fr/selection/) du site. Chaque page reprend
la mise en page de cette page WordPress à l'identique — version courante (texte, roue,
liste des applications) puis Archives (une même section répétée pour chaque version
historique) — sauf que la roue Canva y est remplacée par la roue interactive et que
chaque version, y compris les archives, a désormais sa propre liste d'applications.

## Pourquoi ce dépôt

La roue était jusqu'ici un design Canva embarqué en iframe. Ça fonctionnait, mais :

- **Impossible à traduire** — un embed Canva ne peut pas avoir de version anglaise sans
  dupliquer et maintenir le design à la main dans l'outil.
- **Impossible à corriger rapidement** — le moindre changement (un outil renommé, un lien
  mort) nécessite de rouvrir Canva, retrouver le bon calque, republier, régénérer l'export.
- **Dépendance à un outil propriétaire** — aucune version du design n'est versionnée ou réutilisable en dehors de Canva.

Ce dépôt reprend la main : la roue est régénérée par un script Python à partir de données
structurées (le tableau des 60 outils) et des vrais logos des outils, extraits une fois
pour toutes depuis les exports Canva existants. Le résultat est un fichier HTML autonome
(SVG inline, logos encodés en base64, aucune dépendance externe hors Google Fonts) —
éditable, traduisible, versionné avec Git.

La mise en page (couleurs par catégorie, position des anneaux, légende, proportions) a été
mesurée directement sur l'export PDF officiel de la version courante pour reproduire le
design original à l'identique, plutôt que d'en proposer une réinterprétation.

## Structure du dépôt

```
selection-outils.html         → page FR en ligne (URL stable, embarquée en iframe) : version
                                  courante (texte, roue, liste) puis Archives (idem pour
                                  chaque version historique, v5 → v1)
selection-outils-en.html      → même chose en EN

build/                        → générateur
  generate.py                   script qui produit le HTML des versions v2 à v6 (modèle
                                  commun) ainsi que la page combinée ci-dessus
                                  (build_full_page) ; VERSION_INFO / VERSION_DESCRIPTIONS
                                  y listent la date "Version du…", la description et l'URL
                                  du PDF officiel de chaque version — à mettre à jour à
                                  la main quand une nouvelle version sort
  generate_v1.py                 générateur séparé pour v1, dont le design d'origine diffère
                                  (7 catégories, pas de trou de légende à 180°, etc.) —
                                  build_full_page l'importe pour le bloc v1 de la page combinée
  data.json / data-vN.json      les outils de chaque version : catégorie / niveau / slug (source de vérité)
  tools-lookup.json / -vN       slug → nom affiché + URL sur uneiaparjour.fr, par version
  logo-sizes.json / -vN         dimensions natives de chaque logo (calcul de mise à l'échelle)
  logo-frame-colors.json / -vN  couleur de fond échantillonnée par logo (cadre arrondi)
  meta.json / meta-vN.json      libellé de version + date affichés au centre de la roue
  transparent-logos.json        logos à fond transparent (repérés automatiquement)
  cc-by-badge.png                badge CC BY réel, extrait du design Canva original

logos/                        → un sous-dossier par version, mêmes slugs que dans data-vN.json
  v1-0724/ … v6-0926/            (v6-0926 = version courante)
logos-mapping.md              → tableau de correspondance outil / logo / résolution / export source

source/                       → exports Canva originaux (.pptx + archive dézippée), un
  v1-0724/  …  v6-0926/          dossier par version historique, conservés pour référence
                                  et pour ré-extraire des logos si une future version en a besoin

versions/                     → instantané figé du HTML publié à chaque version
  v1-0724/ … v6-0926/            (v6 = version actuelle ; historique complet, v1 à v6)
```

### Pourquoi garder `source/` ET `versions/`

Le dépôt garde l'historique complet de la roue, de v1 (juillet 2024) à v6 (version
actuelle), chacune en FR + EN :

- `source/vN-XXXX/` garde l'export Canva d'origine de chaque version — utile si on doit
  un jour ré-extraire un logo ou vérifier un détail de mise en page historique.
- `versions/vN-XXXX/` garde l'instantané HTML figé de chaque version toute seule (sans le
  reste de la page) — utile pour lier directement à une version précise.
- Les fichiers à la **racine** (`selection-outils.html` / `-en.html`) sont les deux seules
  URLs à ne jamais changer, puisque ce sont elles qui sont embarquées en iframe sur le
  site ; ils contiennent la page combinée (version courante + toutes les archives), pas
  juste la dernière roue.

### Cas particulier : v1 (juillet 2024)

Le design Canva de la toute première version diffère réellement des suivantes, pas
seulement par ses outils : 7 catégories au lieu de 10 (pas encore de "Applications et
agents", "Voix" et "Musique" encore fusionnées, "Chatbots" s'appelait "Texte et
Chatbot"), un fond crème, une palette pastel avec anneaux de légende gris, et une police
arrondie pour les textes hors noms de catégorie. `generate_v1.py` reproduit cette mise en
page spécifique plutôt que de forcer v1 dans le modèle à 10 secteurs de `generate.py`.
Seule exception volontaire à la fidélité totale : les logos y reçoivent le même
traitement coins arrondis + cadre coloré que les autres versions (l'original les posait
bruts, sans cadre).

## Démarche pas à pas

Pour une nouvelle version qui remplace l'actuelle :

1. Exporter le nouveau design Canva en `.pptx`, le dézipper dans `source/vN-XXXX/`.
2. Mettre à jour `build/data.json` (catégories/outils) à partir du tableau de la page
   Sélection sur le site.
3. Extraire les nouveaux logos si besoin (voir la méthode dans `logos-mapping.md` :
   les liens hypertexte du pptx pointent directement vers l'image associée).
4. Renommer l'ancienne version courante en `-vN` (data.json → data-vN.json, etc.,
   logos/v6-0926 → logos/vN-MMYY) et ajouter son entrée en tête de `VERSION_INFO` /
   `VERSION_DESCRIPTIONS` dans `build/generate.py` (date "Version du…", texte, URL du
   PDF officiel — copiés depuis la page Sélection du site).
5. `python3 build/generate.py` → régénère chaque `versions/vN-XXXX/selection-outils*.html`
   et la page combinée `selection-outils.html` / `-en.html` à la racine.

## Licence

Contenu sous licence CC BY 4.0, comme le reste du site uneiaparjour.fr.
