# Token Architecture — openTRNTBL Design System

Describes the structure, zones of variation, and decisions behind the token pipeline.
For how to *use* tokens in CSS, see `../README.md`.

---

## Three-tier system

```
core.tokens.json
    └─ raw material: OKLCH ramps, dimension scales, easing curves
       These are stable constants. No semantic meaning. Consumed only by primitives.

primitives-openTRNTBL.tokens.json
    └─ brand aliases: accent → gold, success → green, warning → orange, danger → red, info → blue
       One level of indirection. Lets brand reassignment happen in one file.
       Private: components should never reference a primitive directly — only semantics.

semantic.tokens.json
    └─ public API consumed by components
       Mode-aware via $extensions.com.opntrntbl.modes
       CSS custom properties emitted by generate-css.py
```

Each tier has a rule:

| Tier | Rule |
|---|---|
| Core | Declares values. References nothing. |
| Primitive | References only core. One alias per brand decision. |
| Semantic | References only primitives. Declares mode overrides. Never references core directly. |

---

## Four variation axes

The system has 4 orthogonal mode axes. Two are active, two are reserved.

| Axis | `data-*` attribute | Values | Status |
|---|---|---|---|
| Color | `data-color` | `light` (default), `dark` | **Active** |
| Density | `data-density` | `default` (comfortable), `compact`, `spacious` | **Active** |
| Contrast | `data-contrast` | `default`, `enhanced` | Active (color axis only) |
| Vision | `data-vision` | `default`, `protan`, `deutan`, `tritan` | Reserved — no values yet |

Axes are orthogonal. Any combination is valid: `data-color="dark" data-density="compact"`.
Combined modes are declared explicitly in `$extensions.com.opntrntbl.modes` using the `axis:value|axis:value` key format.

---

## Zones of variation — which tokens vary on which axis

### Color axis (light ↔ dark ↔ HC)

Everything that carries a color value varies on the color axis.

| Category | Varies | Notes |
|---|---|---|
| `surface.*` | Yes | All 5 elevation levels + dim/bright + hover/pressed states |
| `border.*` | Yes | subtle/default/strong/focus |
| `accent.*` | Yes | default/hover/pressed |
| `text.color.*` | Yes | All 10 text color roles |
| `status.*` | Yes | All 4 statuses × bg/text/hover/pressed |
| `focus.ring.color` | Yes | |
| `radius.*` | No | Geometry is mode-invariant |
| `spacing.*` | No | Spacing is mode-invariant on the color axis |
| `text.*` (size, weight, lh) | No | Typography scale is mode-invariant |
| `motion.*` | No | |
| `icon.size.*` | No | |

### Density axis (compact ↔ default ↔ spacious)

Only spacing tokens vary on the density axis. No color variation.

| Token | compact | default | spacious |
|---|---|---|---|
| `spacing.tight` | 0.125rem | 0.25rem | 0.375rem |
| `spacing.snug` | 0.375rem | 0.5rem | 0.625rem |
| `spacing.default` | 0.75rem | 1rem | 1.25rem |
| `spacing.loose` | 1.25rem | 1.5rem | 2rem |
| `spacing.airy` | 2rem | 2.5rem | 3rem |

Typography scale and icon sizes are intentionally excluded from density variation — only gaps change, not the type or icon size.

### Contrast axis (default ↔ enhanced)

The contrast axis is a sub-axis of the color axis. It selects higher-contrast primitives within the same hue.
Combined modes (`color:dark|contrast:enhanced`) are declared explicitly.

### Vision axis

Reserved. No tokens have vision-axis overrides yet. When implemented, it will remap hue assignments at the primitive tier (swap the accent hue to be distinguishable under each deficiency type), not at the semantic tier.

---

## Mode implementation — how it works technically

### In the JSON source

Mode overrides are declared inline in `$extensions.com.opntrntbl.modes` on each semantic token:

```json
"semantic.surface.base.background": {
  "$value": "{primitives/openTRNTBL.color.neutral.200}",
  "$extensions": {
    "com.opntrntbl.modes": {
      "color:dark": "{primitives/openTRNTBL.color.neutral.10}",
      "contrast:enhanced": "{primitives/openTRNTBL.color.neutral.200}",
      "color:dark|contrast:enhanced": "{primitives/openTRNTBL.color.neutral.25}"
    },
    "com.opntrntbl.varies": "varies",
    "com.opntrntbl.scope": ["mode"]
  }
}
```

The `bundle.py` script reads these and emits `dist/tokens.modes-matrix.json` (all color-axis values) and `dist/tokens.density-matrix.json` (all density-axis values).

### In CSS

`generate-css.py` emits `dist/tokens.css`:

```css
:root {
  --surface-base: oklch(97.4% 0.003 262);   /* default light values */
  --spacing-default: 1rem;
}
[data-color="dark"] {
  --surface-base: oklch(12% 0.01 262);
}
[data-density="compact"] {
  --spacing-default: 0.75rem;
}
[data-density="spacious"] {
  --spacing-default: 1.25rem;
}
```

At runtime, `data-color` and `data-density` are set as attributes on `<body>`. The CSS cascade does the rest — no JS token resolution at read time.

### Tradeoffs vs alternatives

| Approach | What it does | Why we didn't use it |
|---|---|---|
| **Tokens Studio convention** (ours) | Mode matrix embedded in `$extensions` per token | What we use. Pragmatic. Not spec-compliant. |
| **Bill Collins `resolver.json`** | External resolver file, tokens stay clean | Requires resolver tooling at build time, not yet in ecosystem |
| **Damato scoping** | No mode values in JSON, CSS redeclares via `[data-mode]` | Loses the JSON-as-source-of-truth property. Clean but harder to audit. |

The embedded approach was chosen because it keeps the full matrix inspectable from the JSON without running the CSS generator, and is compatible with Tokens Studio / Figma import.

---

## Token metadata schema

Each semantic token carries a `$extensions.com.opntrntbl.*` block:

| Key | Type | Meaning |
|---|---|---|
| `deprecated` | `boolean` | If `true`, do not use in new component work. |
| `varies` | `"varies"` \| `"stable"` \| `"reserved"` | Whether the token changes value across modes. |
| `scope` | `string[]` | Which axes it varies on: `"mode"`, `"density"`, `"vision"`. |
| `modes` | `object` | Map of `"axis:value"` → overriding primitive reference. |

`varies` is a governance signal, not a runtime value. It is used by auditing scripts (`validate_metadata.py`, `audit_components.py`) to catch components consuming `stable` tokens as if they were mode-aware, or vice versa.

---

## Aliasing taxonomy — 4 layers and what justifies each

```
core.gold.500         ← raw value (OKLCH number). No meaning.
  ↓
primitives.accent     ← brand decision: "our accent is gold". Justification: rebrand in one place.
  ↓
semantic.accent.default  ← semantic decision: "interactive accent". Justification: carries purpose.
  ↓
(components consume semantic.accent.default — no component-level tokens yet)
```

**A token is justified if it carries a decision.** Tests:
1. Could you rename it without changing what it represents? If yes, it's probably not carrying a distinct decision.
2. Does removing it require touching more than one component? If yes, the abstraction is earning its keep.
3. Does it vary across at least one mode axis? If not, and it's not a named constant, it may be a premature alias.

Component tokens (e.g. `button.primary.bg`) are intentionally absent. They create maintenance overhead without benefit as long as the semantic tier covers the intent. They become justified when a component genuinely needs a value that no semantic token describes.

---

## What is stable and why

Some tokens are deliberately mode-invariant:

**Typography scale** — font size, weight, line-height are invariant across color and density axes. Density affects gaps, not letterforms. The reading experience (type size) is not a density concern.

**Radius** — geometric constants. No optical reason for radii to change per mode.

**Motion** — duration and easing are invariant. Motion preference (reduced-motion) is handled via `@media (prefers-reduced-motion)` in CSS, not via tokens.

**Icon sizes** — 3 named sizes (sm/md/lg), mode-invariant. Icon scale follows text scale implicitly (icons sized to match adjacent type).

---

## Experimental architectures

Three alternative architectures coexist in `experiments/` for comparison in Storybook (toolbar → database icon).

| Experiment | Fichiers source | Resolver | CSS output |
|---|---|---|---|
| `algorithmic` | `src/base.tokens.json` + `src/semantic.tokens.json` | `resolver.py` | `tokens.css` |
| `nested-modes` | `src/defaults.tokens.json` + `src/modes/*.tokens.json` | `resolver.py` | `tokens.css` |
| `neumorphic` | `src/theme.tokens.json` (branche `experiment/neumorphic`) | — (à écrire) | — |

### Algorithmic

Toute la couche sémantique est exprimée en formules référençant `{base.*}`. Le resolver substitue les références et émet des `var(--base-*)` dans le CSS — ce qui rend le système live en DevTools. Changer `--base-hue` repeint tout. Changer `--base-font-size` rescale toute la typographie. La densité est un unique multiplicateur (`--base-density-factor`) appliqué à tous les espaces.

**Différence fondamentale avec V1** : V1 cureate des valeurs. Algorithmic encode des relations entre valeurs.

### Nested modes

Implémente le principe de *Mise en mode* (Damato) + la proposition `resolver.json` (Bill Collins). Chaque axe de mode vit dans un fichier séparé. Le CSS est généré avec un bloc par mode (`[data-token-system="nested-modes"][data-color="dark"]`), jamais de combinaison déclarée. La cascade CSS résout les intersections :

```
dark + compact = [data-color="dark"] ∩ [data-density="compact"] → résolu par cascade, O(n+m) pas O(n×m)
```

**Différence fondamentale avec V1** : V1 déclare explicitement `"color:dark|density:compact"` dans `$extensions.modes`. Nested-modes ne déclare jamais de combinaison.

Voir `experiments/nested-modes/README.md` et `experiments/algorithmic/README.md` pour les détails.

---

## Known gaps (V2 direction)

**Density axis doesn't cover icon sizes or typography** — if a future use case needs truly compact information density (e.g. a table view or admin panel), icon size and type size would also need to respond. Currently only gaps change.

**HC vision axis is unimplemented** — contrast:enhanced exists but vision-axis (protan/deutan/tritan) has no values. When implemented, the hue reassignment should happen at the primitive tier, not by adding new semantic overrides.

**No component tokens exist** — appropriate for now but will become necessary once components diverge meaningfully (e.g. a Chart component needing categorical colors outside the semantic palette).

**Modes embedded in $extensions, not in a resolver** — the JSON structure is Tokens Studio convention, not DTCG-spec. If the DTCG formalizes `resolver.json` (Bill Collins proposal), migrating would mean extracting all `$extensions.modes` blocks into an external matrix file. The semantic source would become cleaner; the tooling would need updating.

**status.* as tokens vs as mode scopes** — the current `status.warning.bg` / `status.danger.bg` etc. are declared tokens. The Damato approach would model these as CSS mode scopes (`[data-mode~="critical"]` redeclaring `--surface-base`, `--border-default`) rather than as a new token namespace. This would eliminate the `status.*` tier entirely. Deferred to V2 once we have more components that consume status colors.
