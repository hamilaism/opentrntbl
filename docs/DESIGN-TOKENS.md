# Design Tokens — Architecture

This document explains the design tokens system that powers the openTRNTBL portal UI. It's intended for contributors who want to extend the design system, rebrand the firmware, or fork the project for a different hardware platform.

If you're new to design tokens, the [W3C Design Tokens Community Group spec (DTCG)](https://www.designtokens.org/) is the reference. The pattern below is a concrete implementation of those ideas, opinionated for openTRNTBL but transferable.

---

## TL;DR

- **4 strict layers** : `primitive → brand → semantic → component` — each layer carries a specific kind of decision
- **4 mode axes** : `color` (light/dark) × `contrast` (default/high) × `vision` (default + 4 colorblindness adaptations) × `density` (default/compact/spacious)
- **Source format** : DTCG 2025.10 JSON, OKLCH colors at the primitive layer
- **Pipeline** : `design/tokens/src/*.tokens.json` → `design/tokens/scripts/generate-css.py` → `firmware/tokens.css` (113 CSS variables consumed by `firmware/index.html`)
- **Bundles** : matrix bundle (multi-mode), Tokens-Studio-compatible bundle, Figma payload bundle (per-mode resolved values for variable injection)

---

## The 4 layers

The design system is structured in **4 strict layers**. Each alias should justify its existence by **carrying a decision** — not just renaming the same value across layers.

| Layer | Role | Example |
|---|---|---|
| **Primitive** | The catalog of available options. No semantic meaning. | `core.palette.gold.125`, `core.dimension.30`, `core.opacity.50` |
| **Brand** | The brand's expression — what's "openTRNTBL" specifically (vs another brand using the same primitives). | `brand.color.accent.125 → core.palette.gold.125` |
| **Semantic** | A decision : "in this product, the `accent.default` is `accent.125` because…". Carries intent. | `semantic.accent.default → brand.color.accent.125` |
| **Component** | Bound at the component instance level. | `Button.background = semantic.accent.default` |

**Why this discipline matters** : without it, you get tokens like `color.button.primary.background = #e8a932`. Now you can't rebrand without touching every component. By going `Component → Semantic → Brand → Primitive`, a multi-brand swap requires only changing the Brand layer (1 file), not every component.

**Practical rules** :
- Don't create a Brand alias if it's identical to its Primitive (no decision carried) — use the Primitive directly
- Don't create a Semantic alias if it doesn't represent a decision specific to the product context
- The Component layer should ONLY reference Semantic (or in rare exceptions, Brand). Never reference Primitives directly from Components — that breaks the rebrand contract.

---

## The 4 mode axes

Modes are applied via CSS attributes on the document root or a parent element :

```html
<html data-color="light" data-contrast="default" data-vision="default" data-density="default">
```

Switching a mode rebinds the cascade automatically — no JS required for the visual change (just for setting the attribute).

### 1. Color : `light` / `dark`

Standard light/dark theme. The primitive palette has both light and dark resolved values, the semantic layer picks the right one per mode.

### 2. Contrast : `default` / `enhanced` (HC)

High Contrast (HC) is **not just stronger borders**. It's a [radical pattern](.claude/memory-templates/) where surfaces shift to a pure dim/bright contrast :

- HC track / input background → `surface.dim` (fixed dark) + text `text.color.on-dim` (white)
- HC active tile → `surface.bright` (fixed light) + text `text.color.on-bright` (black)
- **No bandage borders** added — colors carry their own contrast

This works because HC is for users who need maximum luminance contrast, not "more decoration". The pattern matches WCAG AAA contrast targets without UI noise.

### 3. Vision : `default` / `deutan` / `protan` / `tritan` / `achroma`

Colorblind adaptations, **not simulations**. The four daltonism modes use **alternative palettes that preserve the semantic distinction**, not what a colorblind user would see :

- `accent` in `deutan` mode → shifts to `cyan` / `info` (blue) because deuteranopes confuse red/green ; we give them a blue that stays distinguishable
- `accent` in `achroma` mode → shifts to `neutral` luminance steps ; no hue works for full achromatopsia, so we play on lightness
- `warning` in `protan` mode → shifts to `violet` (avoids red/green confusion)

The mappings are in `design/tokens/src/semantic.tokens.json` under each token's `vision:*` overrides.

### 4. Density : `default` / `compact` / `spacious`

Spacing scale that adjusts to the user's preference for information density :

- `compact` : tighter padding, smaller gaps — useful for dashboards / data tables
- `default` : balanced
- `spacious` : more breathing room — useful for accessibility or touch-first contexts

Spacing is consumed as `gap` (for flex/grid containers) and as `padding` at the point of use. **No margins** in the system — see [project_ds_spacing_gap_only memory](.claude/memory-templates/project_ds_spacing_gap_only.md) for the rationale.

---

## Source files

```
design/tokens/src/
  core.tokens.json              # Primitive layer : palette, dimension, opacity, fontSize, etc.
  primitives-openTRNTBL.tokens.json  # Brand layer : aliases to core
  semantic.tokens.json          # Semantic layer : surface, text, accent, status, border, etc.
  icons.tokens.json             # Icon SVG references
```

Each file is DTCG 2025.10 compliant. Tokens carry typed values (`{ "$type": "color", "$value": "oklch(...)" }`) and optional `$extensions.com.opntrntbl.*` metadata for governance (deprecated, varies, scope).

---

## The generator

`design/tokens/scripts/generate-css.py` is a Python 3 script that :

1. Loads the 4 source JSON files
2. Resolves the alias chain (Component → Semantic → Brand → Primitive)
3. Computes the resolved value for each `(token, mode-combination)` pair using **longest-match cascade** :
   - For mode `dark-hc-deutan`, the resolver looks for an exact override `color:dark|contrast:enhanced|vision:deuteranopia` first
   - If not found, falls back to longest-prefix : `color:dark|contrast:enhanced` → `color:dark` → base
4. Outputs `firmware/tokens.css` : a single CSS file with `:root` defaults + `[data-*]` selector blocks for each mode override

The CSS file is what the firmware actually loads. It's regenerable at any time via :

```bash
python3 design/tokens/scripts/generate-css.py
```

Other generators in the same folder :
- `resolve-modes-matrix.py` : produces `dist/tokens.modes-matrix.json` with all (token × mode) resolved values, used by Figma payload generation
- `_build_figma_payloads.py` : splits the matrix into Figma-importable payload files (`dist/figma/{core,brand,mode-vars,density-vars,excluded}.json` + batched lots)

---

## The bundles (`design/tokens/dist/`)

```
tokens.json                  # Matrix bundle : all tokens with all mode overrides resolved
tokens.studio.json           # Tokens Studio compatible (legacy hex format)
tokens.modes-matrix.json     # 54 semantic tokens × 20 modes resolved
tokens.density-matrix.json   # 5 density tokens × 3 modes
tokens.penpot.json           # Penpot-compatible bundle
figma/core.json              # Figma payload : Core variables
figma/brand.json             # Figma payload : Brand variables (alias targets)
figma/mode-vars.json         # Figma payload : Semantic variables × modes
figma/density-vars.json      # Figma payload : Density variables × density modes
figma/excluded.json          # Composite tokens (typography 11, transition 4, shadow 2) — to convert to Figma Text/Effect Styles
figma/batches/               # Pre-split batches of 25 for safe re-injection
figma/batches-mini/          # Pre-split batches of 10 for very safe re-injection
```

These bundles are **regenerable artifacts** — they're committed to the repo because downstream consumers (Figma, Penpot, future tools) shouldn't have to run the Python pipeline themselves.

---

## Storybook gallery

`design/components/` contains Storybook stories (`@storybook/html-vite`, version 10.3) that visualize :

- **Primitives** : color palettes, dimension scale, icons
- **Semantic tokens** : surfaces, text colors, status, modes/vision, radius/motion, spacing, solid (button states), text styles
- **Components** : Button (6 variants), Card (3 variants), Input (5 states), Row (3 trailings × 3 states), Alert (4 variants), StatusBadge (4 variants), SegmentedControl (default + HC), Layout (TitleBlock, SectionHeader, WifiBar)

Run Storybook locally :

```bash
npm install
npm run storybook
```

Opens on `http://localhost:6006`. The mode toggle (top-right toolbar) lets you switch any mode axis live.

---

## Inspirations & credits

This system did not appear in a vacuum. It builds on (and synthesizes ideas from) the public work of several design-systems practitioners. Their writing was extremely useful when designing this system :

- **[Donnie d'Amato](https://donnie.dev/)** — Color systems, the `color-mix()` hover pattern, runtime color computation. The `accent.hover = color-mix(in oklch, accent.default, text-color-primary 16%)` pattern in this codebase is a direct application of his approach. See also `.claude/memory-templates/project_donnie_hover_pattern.md`.
- **[Bill Collins](https://github.com/billycollins)** — Token architecture, the discipline of "alias only carries a decision", the longest-match cascade resolver. The 4-layer taxonomy here is a more opinionated version of his framework.
- **[Ness Grixti](https://nessgrixti.com/)** — Design system methodology, governance, the relationship between primitive scale design and semantic intent. Several of the meta-principles in `design/research/META-thinking-design-systems.md` are inspired by her writing.
- **[David Fusilier](https://github.com/davidfusilier)** — Design system structure, the discipline around mode composition (color × contrast × vision orthogonal axes). The mode axis architecture in this project owes a lot to his work.

If you're publishing your own design system, I strongly recommend reading their original work. The synthesized notes in `design/research/KNOWLEDGE-*.md` are my personal takeaways — they shouldn't replace the source material.

---

## Extending or rebranding

If you fork openTRNTBL for a different turntable, a different SBC, or a different brand, here's the typical extension path :

1. **Rebrand only** (same firmware, different look) :
   - Edit `design/tokens/src/primitives-openTRNTBL.tokens.json` — change the brand aliases (e.g. `accent.125` points to a different primitive scale)
   - Re-run `python3 design/tokens/scripts/generate-css.py`
   - Replace `firmware/tokens.css` and redeploy

2. **Add a new component** :
   - Add the CSS in `design/components/components.css` (ship-side)
   - Add a Storybook story in `design/components/<Name>.stories.js`
   - Document in `design/components/<Name>.md`
   - Reference only **semantic tokens** in the component CSS (never primitives)

3. **Add a new mode axis** (e.g., a `contrast=ultra` mode) :
   - Add the override under `semantic.tokens.json` for tokens that need adapting
   - Update `generate-css.py` to handle the new axis in cascade resolution
   - Document the new mode in the [4 mode axes](#the-4-mode-axes) section above

4. **Multi-brand** (one firmware, swap brand at deploy time) :
   - The Brand layer is already isolated — duplicate `primitives-openTRNTBL.tokens.json` to `primitives-<your-brand>.tokens.json`
   - Build pipeline picks one brand file at deploy time
   - Currently not implemented end-to-end ; see V2 roadmap

---

## Known limitations (V1.0.0-alpha)

- **lineHeight** : Figma plugin API doesn't support binding lineHeight to variables — kept as literal in the Figma file. Browser CSS unaffected.
- **`color-mix(in oklch, ...)`** : Used widely for runtime hover/pressed colors. Not natively supported by Figma or Penpot — represented as resolved literals in design tools (with a documented mode token like `text-color-primary-pressed` for cases where the literal would lie in dark mode).
- **Penpot SDK 2.15** : `applyToken` bulk operations are unreliable. Penpot file uses hex literals (light mode only) instead of token bindings — accepted limitation, will revisit when Penpot SDK fixes the issue.
- **Figma Pro plan cap** : 10 modes max per collection. The 20-mode matrix in `tokens.modes-matrix.json` is collapsed to 10 priority modes (no `light/dark-achroma` and no `light/dark-hc-{deutan,protan,tritan,achroma}` combos). Figma Enterprise lifts the cap.

---

## Further reading inside this repo

- [`README.md`](../README.md) — Project overview, getting started
- [`design/research/`](../design/research/) — Synthesized notes on the DS ecosystem (Donnie, Bill, Ness, David)
- [`docs/VIBECODING-WITH-CLAUDE.md`](VIBECODING-WITH-CLAUDE.md) — How this project was built with Claude Code
- [`.claude/memory-templates/`](../.claude/memory-templates/) — Anonymized memory examples that capture design system decisions

If you ship something interesting using or extending this system, please open a GitHub issue or PR — happy to learn from your variants.
