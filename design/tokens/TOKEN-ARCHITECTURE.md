# Token Architecture — openTRNTBL Design System

Describes the structure, variation zones, algorithmic decisions, and pipeline behind the token system.
For how to *use* tokens in CSS, see `../README.md`.

---

## System overview

The system has three production tiers, three experimental architectures running in parallel, and five variation axes. The key question this document answers: **for any given variation (brand, dark mode, high contrast, density, vision deficiency) — which tier do you touch, and why.**

```text
Core  →  Primitives  →  Semantic  →  CSS custom properties
  ↑           ↑              ↑
generated   brand         modes
by script   decision      & states
```

---

## The three tiers

### Tier 0 — Core (`src/core.tokens.json`)

Raw material. Generated entirely by `scripts/generate-core.py` — **never edited by hand.**

Contains:
- 9 color hues × 11 shades (0, 10, 25, 50, 75, 100, 125, 150, 175, 190, 200) in OKLCH
- 22 dimension tokens (rem scale, 1px hairline exception)
- 9 opacity steps
- Font-size aliases to dimension scale (12px–64px)
- 5 line-height ratios (unitless)
- 5 motion durations + 5 easing curves

**Core carries no semantic meaning and references nothing.**

The OKLCH shade scale is WCAG-calibrated: shade-diff ≥ 100 guarantees 4.5:1 AA text contrast; ≥ 75 gives 3:1 AA UI; ≥ 150 gives 7:1 AAA. The generator binary-searches L-values to hit exact luminance targets, then validates all pairs before writing the file. Out-of-gamut colors are auto-reduced via chroma binary search.

Hues: `neutral`, `red`, `orange`, `gold` (brand accent), `yellow`, `green`, `cyan`, `blue`, `violet`.

### Tier 1 — Primitives (`src/primitives-openTRNTBL.tokens.json`)

Brand decisions. References only `core.*`. One alias per brand decision.

```text
core.palette.gold.100  →  primitives.accent.100
core.palette.green.100 →  primitives.success.100
core.palette.orange.75 →  primitives.warning.75
core.palette.red.100   →  primitives.danger.100
core.palette.blue.75   →  primitives.info.75
```

Also contains shadow primitives (4 elevation levels) derived from core neutrals.

**Primitives are private.** No component should reference a primitive directly — only the semantic tier consumes them.

### Tier 2 — Semantic (`src/semantic.tokens.json`)

The public API consumed by components. References only `primitives.*`. Declares all mode overrides inline via `$extensions.com.opntrntbl.modes`.

Categories:

| Namespace | Tokens | Varies on |
|---|---|---|
| `surface.*` | canvas, base, raised, sunken, overlay + hover/pressed states | color, contrast |
| `border.*` | subtle, default, strong, focus | color, contrast |
| `accent.*` | default, hover, pressed | color, contrast |
| `text.color.*` | primary, secondary, placeholder, disabled, inverse, accent + 4 more | color, contrast |
| `status.*` | success/warning/danger/info × bg/text | color, contrast |
| `spacing.*` | tight, snug, default, loose, airy | density |
| `radius.*` | sharp, soft, round, pill, circle | — (invariant) |
| `text.*` | family, size, weight, line-height × semantic roles | — (invariant) |
| `motion.*` | duration + easing × feedback/state/enter/exit | — (invariant) |
| `icon.size.*` | sm, md, lg | — (invariant) |
| `focus.ring.*` | width, offset, color | color |

---

## Where variation lives — the full map

This is the central question. For each variation axis, **one and only one tier is the point of change.**

```
                  Core    Primitives    Semantic    CSS (@media)
                  ────    ──────────    ────────    ────────────
Brand / theme      —         ✓             —              —
Color (light/dark) —         —             ✓              —
High contrast      —         —             ✓              —
Density            —         —             ✓              —
Vision deficiency  —         ✓ (future)    —              —
Reduced motion     —         —             —              ✓
```

### Brand — varies at the Primitives tier

To create a new brand (openTRNTBL, Neuphoisme, a Notion-like theme), you write a new primitives file that maps the same role names (`accent`, `success`, `warning`, `danger`, `info`) to different core hues.

```text
primitives-openTRNTBL.tokens.json   →  accent = gold
primitives-neuphoisme.tokens.json   →  accent = violet   (hypothetical)
primitives-notion.tokens.json       →  accent = blue     (hypothetical)
```

The semantic tier and all components stay **identical**. Swapping primitives is the entire brand change. The neumorphic experiment goes one step further — it replaces the surface model entirely (no color ramps, pure dual-shadow elevation) while keeping the same semantic token names.

### Color mode (light ↔ dark) — varies at the Semantic tier

Mode overrides are declared inline in `$extensions.com.opntrntbl.modes` on each semantic token:

```json
"semantic.surface.base.background": {
  "$value": "{primitives/openTRNTBL.color.neutral.200}",
  "$extensions": {
    "com.opntrntbl.modes": {
      "color:dark": "{primitives/openTRNTBL.color.neutral.10}"
    }
  }
}
```

`bundle.py` reads these and emits `dist/tokens.modes-matrix.json`. `generate-css.py` emits the selectors:

```css
:root                  { --surface-base: oklch(97.4% 0.003 262); }
[data-color="dark"]    { --surface-base: oklch(12% 0.01 262); }
```

Only tokens with `"com.opntrntbl.varies": "varies"` get overrides. Invariant tokens (radius, typography, motion) have no mode block.

### High contrast — sub-axis of color, still at the Semantic tier

Contrast is not a separate pass — it's additional entries in the same `$extensions.modes` block:

```json
"com.opntrntbl.modes": {
  "color:dark":                    "{primitives.neutral.10}",
  "contrast:enhanced":             "{primitives.neutral.200}",
  "color:dark|contrast:enhanced":  "{primitives.neutral.25}"
}
```

The `color:dark|contrast:enhanced` key handles the combined case explicitly. CSS:

```css
[data-contrast="enhanced"]               { --surface-base: oklch(…HC light…); }
[data-color="dark"][data-contrast="enhanced"] { --surface-base: oklch(…HC dark…); }
```

Axes are orthogonal — any combination is valid without extra code.

### Density — varies at the Semantic tier, spacing only

Only `spacing.*` tokens carry density overrides. Typography, icons, and radii are intentionally excluded — density changes gaps, not letterforms or geometry.

```css
:root                     { --spacing-default: 1rem; }
[data-density="compact"]  { --spacing-default: 0.75rem; }
[data-density="spacious"] { --spacing-default: 1.25rem; }
```

Full spacing table:

| Token | compact | default | spacious |
|---|---|---|---|
| `spacing.tight` | 0.125rem | 0.25rem | 0.375rem |
| `spacing.snug` | 0.375rem | 0.5rem | 0.625rem |
| `spacing.default` | 0.75rem | 1rem | 1.25rem |
| `spacing.loose` | 1.25rem | 1.5rem | 2rem |
| `spacing.airy` | 2rem | 2.5rem | 3rem |

### Vision deficiency (daltonisme) — will vary at the Primitives tier

Not yet implemented. When added, it will remap **hue assignments** at the primitives tier — not add new semantic overrides.

Example: under `protan` (red-blind), `primitives.danger` would point to `core.palette.blue` instead of `core.palette.red`, ensuring the semantic meaning survives without relying on hue alone. The semantic tier (`semantic.status.danger.*`) and all components are untouched.

The `data-vision` attribute is reserved. The nested-modes experiment has placeholder files (`vision.protan.tokens.json`, `vision.achromatopsia.tokens.json`, etc.) that sketch the structure.

### Reduced motion — CSS @media, not tokens

`motion.*` tokens (duration, easing) are invariant. Motion preference is handled via standard CSS:

```css
@media (prefers-reduced-motion: reduce) {
  *, *::before, *::after { transition-duration: 0.01ms !important; }
}
```

This is not a token concern — the OS-level preference is more reliable and covers all animations (including JS-driven ones) without token system involvement.

---

## Mode implementation — technical details

### V1 (current production): embedded matrix

Mode overrides live inline in each token's `$extensions` block. Chosen because:
- Full matrix is inspectable from JSON without running the CSS generator
- Compatible with Tokens Studio / Figma plugin import
- `validate_metadata.py` can lint every token's `varies`/`scope` consistency

Trade-off: the JSON grows with every new mode combination. At 4 active axes with partial overlap, it stays manageable. If modes multiply, the nested-modes approach (see below) scales better.

### Token metadata schema

Each semantic token carries `$extensions.com.opntrntbl.*`:

| Key | Type | Meaning |
|---|---|---|
| `deprecated` | `boolean` | Do not use in new component work |
| `varies` | `"varies"` \| `"stable"` \| `"reserved"` | Whether the token changes across modes |
| `scope` | `string[]` | Which axes: `"mode"`, `"density"`, `"vision"` |
| `modes` | `object` | Map of `"axis:value"` → overriding primitive reference |

`varies` is a governance signal used by audit scripts to catch components consuming stable tokens as mode-aware, or vice versa.

---

## Aliasing rules

A token is justified if it carries a distinct decision. Tests:

1. Could you rename it without changing what it represents? If yes → probably not a distinct decision.
2. Does removing it require touching more than one component? If yes → the abstraction earns its keep.
3. Does it vary across at least one mode axis? If not, and it's not a named constant → likely a premature alias.

```text
core.gold.500               ← raw OKLCH value. No meaning.
  ↓
primitives.accent.100       ← brand decision: "our accent is gold". Justification: rebrand in one place.
  ↓
semantic.accent.default     ← semantic decision: "interactive accent". Justification: carries purpose.
  ↓
(components consume semantic.accent.default)
```

Component tokens (e.g. `button.primary.bg`) are intentionally absent. They add maintenance overhead without benefit as long as the semantic tier covers the intent. They become justified when a component needs a value no semantic token describes.

---

## What is invariant and why

| What | Why invariant |
|---|---|
| Typography scale (size, weight, line-height) | Density changes gaps, not letterforms. Type size is not a density concern. |
| Radius | Geometric constants. No optical reason to change per mode. |
| Motion duration + easing | Handled at CSS `@media` level, not token level. OS preference is more reliable. |
| Icon sizes (sm/md/lg) | Follow text scale implicitly. Mode-invariant by design. |
| Core palette | Only the primitives tier makes brand decisions. Core is untouched by modes. |

---

## Token categories × variation axes

Which token categories are actually touched by each variation. `✓` = values change. `—` = unchanged. `(indirect)` = values change only because primitives changed upstream.

| Token category | Brand swap | dark | HC | density | vision (future) | neumorphic |
|---|---|---|---|---|---|---|
| `surface.*` (5 levels + states) | (indirect) | ✓ | ✓ partial | — | — | replaced by shadows |
| `border.*` | (indirect) | ✓ | ✓ | — | — | removed |
| `accent.*` | ✓ hue | ✓ | ✓ | — | — | ✓ |
| `text.color.*` (10 roles) | (indirect) | ✓ | ✓ | — | — | ✓ |
| `status.*` (4 × bg/text) | (indirect) | ✓ | ✓ | — | (hue remap) | weak |
| `focus.ring.color` | (indirect) | ✓ | ✓ | — | — | ✓ |
| `spacing.*` (5 steps) | — | — | — | ✓ | — | — |
| `shadow.*` | — | — | — | — | — | ✓ NEW |
| `radius.*` | — | — | — | — | — | — |
| `text.*` (size/weight/lh) | — | — | — | — | — | — |
| `motion.*` | — | — | — | — | — | — |
| `icon.size.*` | — | — | — | — | — | — |

**Reading the table:**

- **Brand swap** changes nothing in the semantic tier directly — it replaces the primitives file. All `(indirect)` tokens get new resolved values because their primitive references now point to different hues.
- **HC** is a sub-axis of color: it only touches a subset of `surface.*` and `border.*` — the tokens where a higher-contrast variant exists in the primitives. Text, accent, and status are already high-contrast by construction.
- **Density** has zero intersection with color tokens. No token belongs to both sets. This is why the CSS cascade can resolve `dark + compact` without explicit combination declarations.
- **Neumorphic** replaces the surface model (dual shadows instead of color ramps), removes borders as an elevation signal, and adds `shadow.*` tokens that don't exist in V1.

---

## Experimental architectures

Three alternative architectures run in parallel under `experiments/`, scoped under `[data-token-system="X"]` so they coexist with V1 without collision (2-attribute specificity beats V1's 1-attribute selectors). Switch between them in Storybook via the toolbar → database icon.

### Algorithmic (`experiments/algorithmic/`)

**Concept:** Encode relations between values, not values themselves. The entire semantic layer is expressed as formulas referencing 4 base scalars.

```
--base-hue: 262
--base-chroma: 0.012
--base-font-size: 1rem
--base-density-factor: 1
```

`resolver.py` converts formulas to `calc()` chains. Everything derives at runtime:

```css
--surface-base: oklch(calc(var(--base-lightness) * 0.97) var(--base-chroma) var(--base-hue));
--spacing-default: calc(1rem * var(--base-density-factor));
```

**Consequence:** Changing `--base-hue` in DevTools repaints the entire UI. Changing `--base-density-factor` rescales all spacing. Dark mode is a `--base-lightness` flip. No mode matrix needed — modes become scalar mutations.

**Trade-off:** Live DevTools editing, single source of truth, O(1) new modes. But: no Tokens Studio compat (can't import `calc()` chains as Figma variables), L-values still need calibration per hue, no per-token override possible.

**Where variation lives in Algorithmic:** everything varies at the scalar level — there is no tier boundary for modes.

### Nested modes (`experiments/nested-modes/`)

**Concept:** Implement D'Amato's *mise en mode* principle + Bill Collins' `resolver.json` pattern. Each mode axis lives in a separate file containing **only what changes**. The CSS cascade resolves intersections.

```text
src/defaults.tokens.json          ← full semantic layer, default values
src/modes/color.dark.tokens.json  ← only tokens that differ in dark
src/modes/density.compact.tokens.json
src/modes/density.spacious.tokens.json
src/modes/vision.protan.tokens.json
src/modes/vision.achromatopsia.tokens.json
...
```

If a token isn't in `color.dark.tokens.json`, it inherits the default. No need to declare "this token is the same in dark mode" — absence is the declaration.

CSS output has one block per mode, never a combined block:

```css
[data-token-system="nested-modes"]                            { --surface-base: oklch(97%…); }
[data-token-system="nested-modes"][data-color="dark"]         { --surface-base: oklch(12%…); }
[data-token-system="nested-modes"][data-density="compact"]    { --spacing-default: 0.75rem; }
```

`dark + compact` resolves via cascade: both `[data-color="dark"]` and `[data-density="compact"]` apply simultaneously, CSS handles the intersection. No `[data-color="dark"][data-density="compact"]` declaration needed.

**Complexity:** V1 is O(n × m) — every token × every mode combination must be declared. Nested-modes is O(n + m) — tokens and modes are independent, intersections are free.

**Where variation lives in Nested modes:** same tier split as V1 (primitives for brand, semantic defaults file for base values, per-axis mode files for overrides), but mode files are separate from token definitions rather than embedded.

**Trade-off:** Dramatically simpler mode management, scales to many axes. But: requires `resolver.py` at build time (not Tokens Studio-compatible as-is), harder to inspect the full matrix for a single token without running the resolver.

#### Imbrication schema — what nests inside what

```text
PRIMITIVES LAYER  (swapped as a whole — not nested in CSS)
┌──────────────────────────────────────────────────────┐
│  brand : primitives-openTRNTBL.json                  │
│  accent=gold  success=green  warning=orange          │
│                                                      │
│  ┌──────────────────────────────────────────────┐   │
│  │  vision (future) : vision.protan.json …      │   │
│  │  danger=blue  accent=?                       │   │
│  │  → remap hues, same role names               │   │
│  └──────────────────────────────────────────────┘   │
└──────────────────────────────────────────────────────┘

  ↓ primitives resolve into ↓

SEMANTIC LAYER  (CSS cascade — axes overlap by specificity)
┌──────────────────────────────────────────────────────────────────────┐
│  defaults  (all tokens, :root)                                       │
│  surface.*  border.*  text.*  accent.*  status.*  spacing.*  …      │
│                                                                      │
│  ┌──────────────────────────────────────────────────────────────┐   │
│  │  color axis  [data-color="dark"]                             │   │
│  │  surface.*  border.*  text.color.*  accent.*  status.*       │   │
│  │  focus.ring.color                                            │   │
│  │                                                              │   │
│  │  ┌──────────────────────────────────────────────────────┐   │   │
│  │  │  contrast sub-axis  [data-contrast="enhanced"]       │   │   │
│  │  │  surface.base  surface.raised  border.*              │   │   │
│  │  │  → nested INSIDE color: enhanced picks from the      │   │   │
│  │  │    same hue as current color mode (light HC ≠ dark HC)│   │   │
│  │  └──────────────────────────────────────────────────────┘   │   │
│  └──────────────────────────────────────────────────────────────┘   │
│                                                                      │
│  ┌──────────────────────────────┐                                   │
│  │  density axis                │  ← no overlap with color axis     │
│  │  [data-density="compact"]    │    (different token categories)   │
│  │  [data-density="spacious"]   │                                   │
│  │  spacing.* only              │                                   │
│  └──────────────────────────────┘                                   │
│                                                                      │
│  radius.*  typography  motion.*  icon.*  ← never vary (any axis)   │
└──────────────────────────────────────────────────────────────────────┘
```

**What nests (contrast inside color):** `[data-contrast="enhanced"]` is a sub-axis of color because "enhanced light" and "enhanced dark" are distinct sets of values — you need to know which color mode is active to know which HC primitives to pick. The file `color.hc.tokens.json` is empty; HC is expressed as `color.dark.hc.tokens.json` and `color.light.hc.tokens.json` — they nest under their parent color mode.

**What doesn't nest (density ⊥ color):** `[data-density="compact"]` touches only `spacing.*`. `[data-color="dark"]` touches only color tokens. Zero overlap → zero conflict → CSS applies both blocks simultaneously without either one needing to know about the other.

**What doesn't nest at all (vision ⊥ semantic):** Vision lives at the primitives tier, not in semantic mode files. `dark + protan` means: load `primitives-protan.json` (remaps hue assignments) then apply `[data-color="dark"]` CSS block. The two operations are on different layers and don't interact.

**What can never coexist:** Two values of the same axis (`data-color="dark"` and `data-color="light"` on the same element). DOM attributes are single-valued; this is enforced by HTML, not the token system.

### Neumorphic (`experiments/neumorphic/`, branch `experiment/neumorphic`)

**Concept:** A full theme built on physical extrusion aesthetics. No color ramps — all elevation is communicated via dual shadows (light source top-left).

```css
--surface-base: oklch(0.92 0.008 262);   /* single shared surface, all elevations */
--shadow-light: oklch(0.98 0.004 262);   /* highlight shadow (top-left) */
--shadow-dark:  oklch(0.78 0.012 262);   /* depth shadow (bottom-right) */
```

Raised components cast outward shadows. Pressed/sunken components invert to inset shadows. Overlay uses deeper shadow pairs. No border tokens needed for elevation — shadows carry all spatial meaning.

**Where variation lives in Neumorphic:** brand variation swaps the single surface color and shadow derivations — all at the primitives tier. Semantic token names (`surface.raised`, `surface.sunken`) stay identical; their resolved values change.

**Accessibility trade-off:** WCAG AA for text (contrast ratios hold). Borders below 3:1 (no color ramp → no contrast-based borders). Status colors (warning, danger) weak in the flat color space. Documented in `experiments/neumorphic/ACCESSIBILITY.md`.

**Status:** Resolver not yet written; CSS hand-authored for Storybook preview. Not integrated into the production pipeline.

---

## Pipeline

```text
generate-core.py          →  src/core.tokens.json
generate-primitives-*.py  →  src/primitives-openTRNTBL.tokens.json
generate-semantic.py      →  src/semantic.tokens.json
bundle.py                 →  dist/tokens.json (DTCG) + dist/tokens.studio.json (Tokens Studio compat)
generate-css.py           →  dist/tokens.css (105 CSS custom properties)
resolve-modes-matrix.py   →  dist/tokens.modes-matrix.json + dist/tokens.density-matrix.json
bundle-penpot.py          →  dist/tokens.penpot.json
_build_figma_payloads.py  →  dist/figma/batches/
```

```bash
# Normal build (after editing semantic or primitives):
python3 design/tokens/scripts/bundle.py
python3 design/tokens/scripts/generate-css.py

# Full regeneration (after changing core calibration):
python3 design/tokens/scripts/generate-core.py
python3 design/tokens/scripts/bundle.py
python3 design/tokens/scripts/generate-css.py

# Audit:
python3 design/tokens/scripts/audit_components.py
python3 design/tokens/scripts/validate_metadata.py
```

### Dist outputs

| File | Size | Purpose |
|---|---|---|
| `tokens.json` | 174 KB | DTCG 2025.10 canonical — colors as `{colorSpace, components, hex}` objects |
| `tokens.studio.json` | 155 KB | Tokens Studio fallback — colors as hex strings |
| `tokens.css` | 14 KB | 105 semantic CSS custom properties + mode selectors |
| `tokens.modes-matrix.json` | 46 KB | Flattened: every semantic token × every mode |
| `tokens.density-matrix.json` | 1.2 KB | Spacing tokens only, density axis |
| `tokens.penpot.json` | 149 KB | PenPot variable format |
| `figma/` | — | Batched Figma API payloads (brand, core, mode, density) |

---

## Tradeoffs vs. alternatives (mode implementation)

| Approach | What it does | Why we didn't adopt |
|---|---|---|
| **V1 embedded matrix** (current) | Mode overrides in `$extensions` per token | What we use. Inspectable, Tokens Studio compat. Grows with modes. |
| **Algorithmic (experiment)** | 4 scalars + `calc()` formulas | Live DevTools, O(1) modes. Not Tokens Studio compat. No per-token override. |
| **Nested modes (experiment)** | Per-axis files, cascade resolves intersections | O(n+m) complexity. Requires resolver tooling. Not Tokens Studio compat as-is. |
| **Bill Collins `resolver.json`** | External resolver, tokens stay clean | Not yet tooling-supported in ecosystem. |
| **D'Amato `[data-mode]` scoping** | CSS redeclares via attribute selectors, no mode values in JSON | Loses JSON-as-source-of-truth. Clean but harder to audit. |

---

## Known gaps (V2 direction)

**Vision axis unimplemented** — `data-vision` is reserved. Nested-modes experiment has placeholder files. When implemented: hue reassignment at primitives tier, not new semantic overrides.

**Density doesn't cover icon sizes or typography** — intentional for now. A truly compact information-dense view (admin panel, data table) would need type and icon scale to respond too.

**No component tokens** — appropriate until a component needs a value the semantic tier can't express (e.g. Chart needing categorical colors outside the palette).

**Mode matrix embedded in `$extensions`** — Tokens Studio convention, not DTCG-spec. If DTCG formalizes `resolver.json`, migration means extracting all `$extensions.modes` blocks into an external matrix file.

**`status.*` as tokens vs. mode scopes** — D'Amato's approach would model status as CSS mode scopes (`[data-mode~="critical"]` redeclaring `--surface-base`) eliminating the `status.*` tier. Deferred to V2 once more components consume status colors.

**Neumorphic resolver not written** — the experiment is hand-authored CSS. Integrating it into the pipeline requires writing `resolver.py` for neumorphic and hooking it into `bundle.py`.
