# Experiment : Algorithmic token system

## Concept

Toute l'interface dérive de **4 inputs**. Changer `--base-hue` en DevTools repeint toutes les surfaces, les bordures, les status colors — instantanément, sans recompiler.

```
base.hue          → hue de toutes les surfaces, bordures, textes tintés
base.chroma       → saturation des surfaces neutres
base.hue-accent   → hue de l'accent (CTA, focus, liens)
base.chroma-accent→ saturation de l'accent
base.font-size    → base du système typographique
base.scale-ratio  → ratio de l'échelle modulaire (1.25 = tierce majeure)
base.space-unit   → atome d'espacement en px (grid de 4px)
```

Les autres valeurs (hues de status, chroma-status, font-families, motion-base) sont des paramètres secondaires dans `base.tokens.json`.

## Architecture JSON

### `src/base.tokens.json`

Contient uniquement des scalaires (`number`, `fontFamily`). Ce sont les seules valeurs qu'un designer édite pour rethemer.

```json
{
  "base": {
    "hue":          { "$type": "number", "$value": 262 },
    "space-unit":   { "$type": "number", "$value": 4 },
    "density-factor": {
      "$value": 1,
      "$extensions": {
        "com.opntrntbl.compact":  0.5,
        "com.opntrntbl.spacious": 1.5
      }
    }
  }
}
```

### `src/semantic.tokens.json`

Toutes les valeurs sont des **formules** référençant `{base.*}`. Le JSON n'est pas résolu — c'est le resolver qui fait le travail.

```json
{
  "surface": {
    "canvas": {
      "$type": "color",
      "$value": "oklch(0.96 {base.chroma} {base.hue})",
      "$extensions": {
        "com.opntrntbl.dark": "oklch(0.08 {base.chroma} {base.hue})",
        "com.opntrntbl.hc":   "oklch(0.98 {base.chroma} {base.hue})"
      }
    }
  },
  "spacing": {
    "default": {
      "$type": "dimension",
      "$value": "calc({base.space-unit}px * 4 * {base.density-factor})"
    }
  },
  "text": {
    "body": {
      "$type": "typography",
      "$value": {
        "fontSize": "clamp(calc({base.font-size}px * 0.9), calc({base.font-size}px * 1), calc({base.font-size}px * 1.1))",
        "lineHeight": 1.5
      }
    }
  }
}
```

**Décisions de design dans les formules :**
- Les valeurs de luminosité `L` (ex. `0.96` pour canvas en light, `0.08` en dark) sont hardcodées dans les formules — ce sont des décisions sémantiques, pas des paramètres.
- Le hue et le chroma (la "personnalité de marque") passent par les refs `{base.*}`.

## Résolution : syntaxe des références

Le resolver applique ces règles de substitution :

| Pattern dans `$value` | Résultat CSS |
|---|---|
| `{base.hue}` | `var(--base-hue)` |
| `{base.space-unit}px` | `(var(--base-space-unit) * 1px)` |
| `{base.motion-base}ms` | `(var(--base-motion-base) * 1ms)` |
| `{base.density-factor}` | `var(--base-density-factor)` |

Les références unitaires (suffixe `px`, `ms`) sont isolées pour rester valides dans `calc()`.

## CSS généré

```css
[data-token-system="algorithmic"] {
  /* Base vars — live en DevTools */
  --base-hue: 262;
  --base-chroma: 0.012;
  --base-font-size: 16;
  --base-space-unit: 4;
  --base-density-factor: 1;

  /* Semantic — référencent les base vars */
  --surface-canvas: oklch(0.96 var(--base-chroma) var(--base-hue));
  --spacing-default: calc((var(--base-space-unit) * 1px) * 4 * var(--base-density-factor));
  --text-body-size: clamp(calc((var(--base-font-size) * 1px) * 0.9), …);
}

[data-token-system="algorithmic"][data-color="dark"] {
  --surface-canvas: oklch(0.08 var(--base-chroma) var(--base-hue));
  /* … 30 overrides dark */
}

[data-token-system="algorithmic"][data-density="compact"] {
  --base-density-factor: 0.5;  /* seule ligne nécessaire pour tout le système d'espacement */
}
```

**Pourquoi le density est différent :** il suffit de changer `--base-density-factor` — tous les `spacing.*` et `radius.*` et `icon.size.*` se recalculent via leurs `calc()`.

## Typographie fluide

Échelle modulaire ratio 1.25, chaque step est :
```
font-size-step-n = base.font-size × 1.25^n
```

Les valeurs sont pré-calculées (coefficients) mais le `base.font-size` reste une CSS var live :
```css
--text-body-size: clamp(
  calc((var(--base-font-size) * 1px) * 0.9),   /* min */
  calc((var(--base-font-size) * 1px) * 1),      /* preferred */
  calc((var(--base-font-size) * 1px) * 1.1)     /* max */
);
```

Line-height calculé optiquement : `lh = 1 + 8 / font-size-px` (plus élevé pour les petits corps, plus serré pour les grands). Valeurs pré-calculées et hardcodées.

## Grid 4px

Tous les espaces sont des multiples entiers de `base.space-unit` (4px) × `density-factor`. Les facteurs de densité (0.5 / 1 / 1.5) sont choisis pour que toutes les valeurs restent sur la grille 4px :
```
tight   = 4 × 1 = 4px   → ×0.5 = 2px  ×1.5 = 6px   (tous ÷ 4)
snug    = 4 × 2 = 8px   → ×0.5 = 4px  ×1.5 = 12px
default = 4 × 4 = 16px  → ×0.5 = 8px  ×1.5 = 24px
loose   = 4 × 6 = 24px  → ×0.5 = 12px ×1.5 = 36px
airy    = 4 × 10 = 40px → ×0.5 = 20px ×1.5 = 60px
```

## Regénérer

```bash
python3 design/tokens/experiments/algorithmic/resolver.py
```

## Modifier le thème

Pour tester un thème différent sans recompiler, ouvrir les DevTools Storybook et modifier les CSS vars live :

```css
/* Dans DevTools, sur l'élément <body> : */
--base-hue: 195;          /* turquoise */
--base-hue-accent: 15;    /* corail */
--base-font-size: 18;     /* corps plus grand */
```

Pour figer un nouveau thème, éditer `src/base.tokens.json` et relancer le resolver.

## Trade-offs

| ✓ Pour | ✗ Contre |
|---|---|
| Retheming en 4 valeurs | Les L-values (luminosité sémantique) restent hardcodées |
| CSS live en DevTools | `calc()` imbriqués parfois verbeux |
| Density en 1 var CSS | Pas compatible Tokens Studio |
| Grid 4px garantie | Line-heights pré-calculés, pas adaptatifs |
| Moins de tokens à maintenir | Perd la granularité de curation V1 |
