# Token system experiments

Three token architectures coexist in this directory, each exploring a different design philosophy. V1 (the production system in `dist/`) remains the reference.

## How to switch in Storybook

```bash
npm run storybook
```

Toolbar → icône **database** → choisir parmi :

| Option | Architecture | Source |
|---|---|---|
| `V1 — current` | Ramps curées, overrides inline dans `$extensions` | `dist/tokens.css` (`:root {}`) |
| `Algorithmic` | 4 inputs, tout calculé, formules dans `$value` | `experiments/algorithmic/tokens.css` |
| `Nested modes` | Fichiers par mode, cascade CSS, zéro combinaison | `experiments/nested-modes/tokens.css` |

Les axes **color / density / contrast / vision** de la toolbar restent actifs sur les 3 systèmes.

## Mécanique CSS

Les CSS expérimentaux sont scopés sous `[data-token-system="X"]` (posé sur `<body>` par le décorateur Storybook). Ils overrident les vars V1 définies dans `:root` grâce à la spécificité cascade :

```
:root { --surface-canvas: #f2f2f2; }                         ← V1, specificity 0-0-1
body[data-token-system="algorithmic"] { --surface-canvas: oklch(…); }  ← gagne
```

Les overrides de mode expérimental ont une spécificité plus haute que les overrides V1 (2 attributs vs 1 attribut) :

```
[data-color="dark"] { … }                                    ← V1 dark, spec 0-1-0
[data-token-system="algorithmic"][data-color="dark"] { … }   ← Algo dark, spec 0-2-0 → gagne
```

## Regénérer les CSS

```bash
python3 design/tokens/experiments/algorithmic/resolver.py
python3 design/tokens/experiments/nested-modes/resolver.py
```

## Répertoire

```
experiments/
  algorithmic/        → formules dans le JSON, CSS live en DevTools
  nested-modes/       → un fichier par mode, cascade sans combinaison
  neumorphic/         → branche experiment/neumorphic, dual-shadow, mono-surface
  README.md           ← ce fichier
```

## Comparaison rapide

| Critère | V1 | Algorithmic | Nested modes |
|---|---|---|---|
| Source of truth | JSON + ramps | JSON + formules | JSON par couche |
| Changer de thème | Recalibrer les ramps | Changer 4 valeurs dans `base.tokens.json` | Écrire un fichier `modes/mybrand.json` |
| Combinaisons light+compact | Déclarées explicitement | Héritées (density-factor live) | Héritées (cascade) |
| CSS live en DevTools | Non | Oui (`--base-hue`, `--base-font-size`, …) | Non |
| Compatibilité Tokens Studio | Partielle | Non (formules custom) | Oui (valeurs résolues) |
| DTCG-compliance | Partielle (`$extensions` custom) | Partielle (formules dans `$value`) | Strict |
