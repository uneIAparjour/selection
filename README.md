# Sélection d'applications — uneIAparjour

Roue interactive HTML/SVG des 60 applications d'IA générative sélectionnées par
[Une IA par jour](https://www.uneiaparjour.fr), classées en 10 catégories × 3 niveaux
d'appropriation (Pour découvrir / Pour aller plus loin / Usage avancé).

**Démo en ligne :** `selection-outils.html` (FR) et `selection-outils-en.html` (EN) —
hébergées via GitHub Pages et embarquées en iframe sur la page
[/selection/](https://www.uneiaparjour.fr/selection/) du site.

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
selection-outils.html         → version FR en ligne (URL stable, embarquée en iframe)
selection-outils-en.html      → version EN en ligne (URL stable, embarquée en iframe)

build/                        → générateur
  generate.py                   script qui produit tous les HTML (modèle commun, toutes versions)
  data.json / data-vN.json      les outils de chaque version : catégorie / niveau / slug (source de vérité)
  tools-lookup.json / -vN       slug → nom affiché + URL sur uneiaparjour.fr, par version
  logo-sizes.json / -vN         dimensions natives de chaque logo (calcul de mise à l'échelle)
  logo-frame-colors.json / -vN  couleur de fond échantillonnée par logo (cadre arrondi)
  meta.json / meta-vN.json      libellé de version + date affichés au centre de la roue
  transparent-logos.json        logos à fond transparent (repérés automatiquement)
  cc-by-badge.png                badge CC BY réel, extrait du design Canva original

logos/                        → un sous-dossier par version, mêmes slugs que dans data-vN.json
  v2-1024/ … v6-0926/            (v6-0926 = version courante)
logos-mapping.md              → tableau de correspondance outil / logo / résolution / export source

source/                       → exports Canva originaux (.pptx + archive dézippée), un
  v1-0724/  …  v6-0926/          dossier par version historique, conservés pour référence
                                  et pour ré-extraire des logos si une future version en a besoin

versions/                     → instantané figé du HTML publié à chaque version
  v2-1024/ … v6-0926/            (v6 = version actuelle ; seule v1-0724 reste à construire)
```

### Pourquoi garder `source/` ET `versions/`

Le dépôt est organisé pour accueillir l'historique complet de la roue, chacune en FR + EN,
en plus de la v6 actuelle :

- `source/vN-XXXX/` garde l'export Canva d'origine de chaque version — utile si on doit
  un jour ré-extraire un logo ou vérifier un détail de mise en page historique.
- `versions/vN-XXXX/` garde l'instantané HTML figé de chaque version une fois générée,
  pour l'historique — un peu comme la section "Archives" de la page Sélection sur le site.
- Seule la **dernière version** vit à la racine (`selection-outils.html` /
  `-en.html`) : ce sont les deux seules URLs à ne jamais changer, puisque ce sont elles
  qui sont embarquées en iframe sur le site.

## Démarche pas à pas

1. Exporter le nouveau design Canva en `.pptx`, le dézipper dans `source/vN-XXXX/`.
2. Mettre à jour `build/data.json` (catégories/outils) à partir du tableau de la page
   Sélection sur le site.
3. Extraire les nouveaux logos si besoin (voir la méthode dans `logos-mapping.md` :
   les liens hypertexte du pptx pointent directement vers l'image associée).
4. `python3 build/generate.py` → régénère `selection-outils.html` et `-en.html`.
5. Copier ces deux fichiers dans `versions/vN-XXXX/` pour l'archive, garder la racine
   comme version en ligne.

## Licence

Contenu sous licence CC BY 4.0, comme le reste du site uneiaparjour.fr.
