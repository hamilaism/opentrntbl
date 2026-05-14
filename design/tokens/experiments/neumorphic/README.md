# Experiment : Neumorphic theme

**Branche : `experiment/neumorphic`**

## Concept

Esthétique physique : les éléments semblent extrudés de la surface plutôt que posés dessus. Une seule couleur de surface, l'élévation communiquée exclusivement par les ombres (double shadow : lumière haut-gauche, ombre bas-droite).

Pas de ramps de couleurs. Pas de borders visibles pour l'élévation. Pas de flat design.

## Architecture

### Une seule couleur de base

```json
"base.surface": "oklch(0.92 0.008 262)"
```

Toutes les surfaces partagent cette couleur. La hiérarchie d'élévation est portée par les ombres, pas par les valeurs de surface.

### Système d'élévation dual-shadow

```
raised:  -4px -4px 8px  [light]  +  4px 4px 8px  [dark]   → extrusion
sunken:  inset shadow en sens inverse                        → creux
pressed: inset réduit                                        → enfoncement physique
overlay: ombres plus larges                                  → lévitation
```

Les couleurs d'ombre dérivent de la surface :
- `shadow-light` : légèrement plus clair que la surface (`oklch(0.98 0.003 262)`)
- `shadow-dark` : légèrement plus foncé (`oklch(0.78 0.012 262)`)

### Tokens d'élévation

```json
"semantic.elevation.raised":  "-4px -4px 8px [light], 4px 4px 8px [dark]"
"semantic.elevation.sunken":  "inset -4px -4px 8px [light], inset 4px 4px 8px [dark]"
"semantic.elevation.pressed": "inset -2px -2px 5px [light], inset 2px 2px 5px [dark]"
"semantic.elevation.overlay": "-8px -8px 20px [light], 8px 8px 20px [dark]"
```

Ce sont des tokens de type `shadow` qui viennent s'ajouter aux tokens `surface.*`. Les composants utilisent `elevation.*` à la place de `surface.raised.elevation`.

## Accessibilité

Voir `ACCESSIBILITY.md` pour l'audit complet. Résumé :

- **Textes** : WCAG AA ✓ (contrast maintenu)
- **Borders** : ≤ 3:1 ✗ (inhérent à l'esthétique)
- **Status bg** : faible contrast ✗ (status communiqué par texte + icône)
- **Focus ring** : accent hue, WCAG AA ✓

**Ce thème ne peut pas être le thème par défaut.** Il est adapté comme option opt-in pour les utilisateurs qui acceptent le trade-off esthétique / accessibilité.

## Fichiers

```
experiments/neumorphic/
  src/
    theme.tokens.json   ← tokens surface, élévation, border, text, status
  ACCESSIBILITY.md      ← audit contrast ligne par ligne
  README.md             ← ce fichier
```

## Intégration Storybook (à faire)

Pour comparer ce thème dans Storybook, il faudra :
1. Écrire un `resolver.py` qui génère `tokens.css` scoped `[data-token-system="neumorphic"]`
2. Ajouter `neumorphic` dans la liste du switcher dans `preview.js`
3. Adapter `components.css` pour utiliser `elevation.*` au lieu de `box-shadow` statiques

Non prioritaire tant que le thème est en exploration.

## Pour aller plus loin

- Tester différentes valeurs de `base.surface` pour trouver le bon gris (trop blanc → l'effet disparaît, trop gris → sombre et lourd)
- Tester la version dark : neumorphic dark fonctionne mieux avec une surface intermédiaire (`oklch(0.25 0.010 262)`) pour avoir de l'espace en haut et en bas
- Évaluer si les composants interactifs sont lisibles sans borders : boutons et inputs sont particulièrement critiques
