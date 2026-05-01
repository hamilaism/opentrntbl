# Design Tokens — synthesis of accumulated knowledge

> Source: openTRNTBL sessions April 2026 (Ismail × Claude)
> Usable for: *The Design Tokens Book*, FranceTV DS, cross projects.
> Date: 2026-04-28.

This document is **not** the openTRNTBL doc. It's the synthesis of **all the reflections, decisions, abstractions, tooling, methodologies** we have laid down or made explicit during the construction of openTRNTBL's DS V1 — in a form transposable to other projects.

---

## 1. The two layers of the doc of a Design System

Distinction made explicit by Ismail:

| Layer | Role | Reader | Form |
|---|---|---|---|
| **Tactical** | Catalog of values, inspector, "what is the color of `button.primary` in dark?" | Implementer (designer/dev who does the job) | Storybook + MDX inspector pages |
| **Meta** | Explanation of the system as a system — *aliases, taxonomy+architecture, mise en modes, variance zones* | Decision-maker, contributor, future-self | Separate doc site (Diátaxis "Explanation"), eventually outside Storybook |

The meta documents **the 4 strata of abstraction**:
- **Aliases**: the translation of an intent into a token (why `button.primary` points here and not there)
- **Taxonomy + architecture**: the naming grammar + the hierarchy (why N layers and not N±1)
- **Mise en modes**: which variation axes exist and how they operate
- **Variance zones**: which decisions vary in which context, and why others don't vary

→ The tactical doc today is **a catalog**. The meta — **system as system** — is what is missing in 95% of DS.

---

## 2. Layer architecture (4-layers)

```
┌────────────────────────┐
│ Component (CSS)        │  ← consumes. NOT a set of tokens.
└─────────────┬──────────┘
              │
┌─────────────▼──────────┐
│ Semantic decision      │  ← "in THIS context with THESE constraints,
│ (semantic.tokens.json) │     we use THIS token".
└─────────────┬──────────┘
              │
┌─────────────▼──────────┐
│ Brand / Primitive      │  ← brand selects from the matter.
│ (primitives-X.json)    │     "Our success green is here in the ramp."
└─────────────┬──────────┘
              │
┌─────────────▼──────────┐
│ Core                   │  ← raw matter (OKLCH ramps,
│ (core.tokens.json)     │     numeric scales, font primitives).
└────────────────────────┘
```

**Decision Ismail (before 2026-04-26)**: `core` = raw matter, `primitives` = brand selection. Before we said `foundations` / `theme` but it was misleading. The word "primitive" must mean "what we take first as a concretely usable base" → that's what the brand has selected, not the raw ramp (which is just matter).

**Aliasing rule**:
> An alias is legitimate if and only if **it carries a decision** (option, brand, or semantic).
> An alias that just renames without carrying a decision = gratuitous, to be removed.

Application:
- An alias in `primitives` must carry a **brand decision**
- An alias in `semantic` must carry a **semantic decision** (usage context)
- If a semantic token points directly to a core primitive without going through a brand primitive → red flag, broken layer contract

---

## 3. The component layer does NOT exist on the tokens side

Structural decision by Ismail: **components are NOT a set of tokens**. They consume tokens in CSS at the point of use.

Implication: a DS that defines `button.primary.bg`, `button.primary.text`, etc. as tokens **invents a layer** that has no reason to exist (= true semantic inversion: it's the component that consumes the semantic, not the reverse).

Unless we adopt Bill Collins' **higher-order tokens** pattern (cf. §11) which makes explicit token **bundles** (container = `{fg, bg, border}`). Decision: not for openTRNTBL V1, it's an aggregation level above.

---

## 4. DTCG metadata schema

```json
"$extensions": {
  "com.<org>.deprecated": false,
  "com.<org>.varies": "stable" | "varies" | "undecided",
  "com.<org>.scope": ["mode", "density", "brand", ...]
}
```

### Tri-state `varies` (≠ boolean)

- **`stable`**: "I thought about it, this token is intentionally immutable" — explicit statement
- **`varies`**: this token varies on ≥1 axis (to complete in `scope`)
- **`undecided`**: not yet thought through, placeholder to audit

→ `undecided` allows **filtering what hasn't been audited**. Transforms metadata into a governance tool.

### `scope` field (not `varies-on`)

Initially named `varies-on`. Renamed to `scope` because **interactive states are not a variance of tokens** (cf. §6) — it's the usage that changes, not the value.

A token like `--text-color-disabled` doesn't *vary* — it's always `gray.500`. What varies is *which token is consumed depending on the component's state*. `scope` is more accurate: "this token is destined to be consumed in such a usage scope".

### Source-of-truth pattern

The **JSON is the only source of truth**. Everything else (CSS, meta doc, Penpot, Tokens Studio, Figma) is **generated** from the JSON. Never manually maintain two representations.

---

## 5. Modes — variance axes of tokens

The real variance axes of tokens are:
- `mode`: `light` / `dark` (colors)
- `density`: `compact` / `default` / `spacious` (spacings, font sizes)
- `contrast`: `default` / `enhanced` (HC mode)
- `vision`: `default` / `deuteranopia` / `protanopia` / `tritanopia` / `achromatopsia` (color blindness)
- `brand`: if multi-brand

**Composites**: light × HC, dark × vision, etc. → combined CSS selectors (`[data-color="dark"][data-contrast="enhanced"]`).

### Radical HC pattern (openTRNTBL)

In HC, **increase ALL contrasts between ALL elements** — not as a band-aid via forced borders.

Validated strategies:
1. **Real surface hierarchy**: canvas / base / raised / sunken must all be visually distinct in HC, not crushed toward pure white or pure black
2. **Fixed tokens for HC scoped**:
   - `surface.dim` (fixed dark regardless of light/dark)
   - `surface.bright` (fixed light)
   - `text-color.on-dim` (fixed white)
   - `text-color.on-bright` (fixed black)
3. **Segment control HC pattern**: track switches to `surface.dim` (fixed dark), active tile `surface.bright` (fixed light), inactive transparent + `text-color.on-dim`. Radical distinction by luminance, not by border.

### 4 color blindness modes (vs 1 generic)

Each type has its own confusions — therefore a distinct palette:
- **Deuteranopia** (green, ~6%): red↔green confusion, refuges = blue/yellow/orange/magenta
- **Protanopia** (red, ~2%): similar to deutero but different luminance
- **Tritanopia** (blue, rare): blue↔yellow confusion, refuges = red/green/magenta/cyan
- **Achromatopsia** (mono): differentiate by luminance + mandatorily by icons/labels

Refs: **Wong palette** (Nature 2011), **IBM Color Blind Safe**, **Tableau Color Blind 10**, **Coblis** simulator.

---

## 6. Interactive states — the key debate

Distinction from the **Mise en mode** book (Damato):

| Type of state | Example | Modeling |
|---|---|---|
| **Ephemeral pseudo-classes** | `:hover`, `:focus`, `:active` (pressed) | Vanilla CSS, **no token** dedicated a priori |
| **Durable scoped modes** | `selected`, `critical`, `disabled` | Scoped mode via `[data-state="..."]` that reassigns CSS vars |

Bill Collins corroborates: *"hover is a mode that resolves `$root`"* — interactive state = structural mode, not a variance of tokens.

### Donnie pattern simplification (computed states)

The Donnie D'Amato pattern (Salesforce → PatternFly, taken up by Wise under Ness Grixti, Radix `subtle` variants):

```css
.element:hover {
  background: color-mix(in oklch, var(--base-color), currentColor 8-15%);
}
```

→ Hovers/derived states **computed** from the base, not dedicated tokens. Eliminates the proliferation of state tokens (no need for a hover per surface), automatically adapts to light/dark.

**But beware**, Damato himself considers this a **simplification** of his deeper point. Article *Hovercraft*: *"perhaps we don't need to put so much design into hover effects from a token maintenance perspective"* — before `color-mix()`, ask yourself if this hover should exist at all.

### openTRNTBL compromise

1. **Hovers kept systematically** (Ismail's decision, vs Damato strict) — for iOS/macOS feel.
2. **Explicit derived tokens** for recurring patterns (e.g., `surface.base-hover/-pressed`, `accent.pressed`) with `$value: color-mix(...)` + `$extensions.com.<org>.fallback.$value: <static>` for tools that don't compute (Penpot SDK 2.14.1, Figma, etc.).
3. **CSS at the point of use** for specific variations (row 80%/70% more marked than btn-2 92%/84%, etc.).

---

## 7. Tone layer — generally parkable

Empirical audit on openTRNTBL (cf. `TONE-SHARING-ANALYSIS.md`): **a single really shared tone** = `status.*` (success/warning/danger/info) consumed by Alert + StatusBadge + Button.destructive.

All other "tone-looking" tokens (`solid.primary.*`, `solid.neutral.*`) were actually **dead** — no component consumed them. The naming made it look like a shared tone, but it was illusion.

→ Empirical rule: **a tone is legitimate iff it is consumed by ≥2 distinct component families**.

Damato corroborates: 0 occurrences of "tone" in his book. What we call "tone" is either (a) a flat **purpose-category** (surface/action/control/text/figure/status), or (b) a **scoped mode**.

→ For openTRNTBL: no general tone layer, status alone documented tone. Damato would say "permanently parkable". Wise (Ness Grixti) extends: formal `sentiment` as axis (alert/neutral/warning/success/proposition) + `emphasis` layer (critical/high-contrast) — but it's banking-specific and a 2D matrix.

---

## 8. Anti-combinatorial-explosion discipline

Learned from Wise and Damato. A matrix of 4 modes × 5 sentiments × 3 emphasis × 6 states = explodes quickly.

Disciplines:
1. **Reference the base, only split the diffs** (Wise): a token override only contains the value that changes, not the entire value. 400 → 4000 tokens avoided.
2. **Invariance pattern** (Wise): if a token has no interaction behavior, **same value replicated** on the 3 modes default/hover/active (no conditional fork).
3. **No numeric scale in semantic** (Damato — *Truly Semantic*): any semantic token with a numeric suffix (`--text-12`, `--neutral-50`) is suspect.
4. **Strict intent grammar** (Damato Mise en mode): `purpose_priority_property`, max 3 priority levels, max ~33 semantic tokens.

---

## 9. Systemic a11y standards

What you do going from "good DS" to "pro DS":

- **Outside HC**: every text/bg pair ≥ **AA** (4.5:1 normal text, 3:1 large/UI)
- **In HC**: every text/bg pair ≥ **AAA** (7:1 normal text, 4.5:1 large/UI)
- **WCAG 1.4.1 Use of Color**: a non-color cue must always exist (label is enough, icon is bonus but not mandatory if label is present)
- **WCAG 2.4.7 Focus Visible**: focus indicator visible on keyboard focus
- **WCAG 2.4.11 Focus Appearance** (AAA, 2.2): minimum 2px solid, 3:1 contrast against adjacent colors
- **`:focus` vs `:focus-visible`**: WCAG doesn't decide. Practice:
  - Inputs → `:focus` (consistent with iOS/macOS, ring even on mouse click)
  - Buttons and other clickable elements → `:focus-visible` (ring only on keyboard focus)

### Decorative vs structural

WCAG 1.4.11 exempts the **decorative** (a 0.5px iOS hairline divider doesn't need 3:1 if the info also passes through layout/typo/hover/etc.).

Trick: **2 border tokens** for the same type — a decorative one (`border.subtle`, low ratio) and a structural one (`border.default`, ≥3:1). The component chooses depending on usage.

---

## 10. Tooling

### Minimal pipeline

```
src/
  core.tokens.json           DTCG sources
  primitives-X.tokens.json
  semantic.tokens.json
scripts/
  bundle.py                  → dist/tokens.json (matrix bundle)
  generate-css.py            → dist/tokens.css (CSS custom props)
  add_metadata.py            → adds $extensions.com.<org>.* idempotent
  validate_metadata.py       → check varies/scope coherence, list undecided
  audit_components.py        → computes WCAG ratios on actual text/bg pairs
  audit_status_hc.py         → targeted HC status audit
  wcag_check.py              → utility OKLCH → contrast ratio
```

### Storybook 10.3 + axe-core + Vitest

```
.storybook/
  main.js                    addons: addon-docs, addon-a11y, addon-vitest, storybook-addon-pseudo-states
  preview.js                 4-axes toolbar (color/contrast/density/vision)
```

`npm test` (Vitest + Playwright + axe-core via @storybook/addon-vitest) → run a11y check on all stories. `'todo'` mode by default, bumpable to `'error'` to fail the build.

### DTCG bundles

- `tokens.json` (matrix bundle, source of truth)
- `tokens.studio.json` (Tokens Studio Figma compat)

---

## 11. References and authors studied

### Donnie D'Amato (Design Systems House, W3C Design Tokens CG)
- **GitHub repos**: `mise-en-mode`, `token-operations`
- **Book**: *Mise en mode* — distinction between ephemeral pseudo-classes vs scoped modes, intent grammar `purpose_priority_property`, 🔒 pattern for private CSS vars
- **complementary.space**: spacing manifesto — 2 tokens (`space-near` + `space-away`), density shift = direct ancestor of mise-en-mode, no `size` prop on components
- **Articles**:
  - *Truly Semantic* — no numeric scale in semantic
  - *People's Primitives* — primitives never consumed directly in experience
  - *Ondark virus* — radical critique of contextual suffixes (`*.dark`, `*.inverse`)
  - *Hovercraft* — questioning the necessity of hover before designing it
- **Formal DTCG proposal**: `$operations` (general mechanism for transformations on tokens)

### Bill Collins (mrginglymus, DTCG CG)
- **Torquens** (torquens.bill.works): higher-order tokens — `{fg, bg, border} × {forced/standard} × {enabled/disabled}` "container" bundle swapped via mixin. Aggregation level above intents.
- **dtcg-playground / dt-demo**: concrete DTCG 2025.10 demo
- **Formal DTCG proposal**: `resolver.json` + `$extends` — formal modifier × context matrix
- **Distinction**: *source-of-truth (designer) vs record-of-truth (DTCG)*

### Ness Grixti (Wise — *Making Wise Design Multi-brand*)
- Multi-brand: 4 consumer themes + 3 Platform themes in **a single axis** (brand × light/dark merged)
- **Sentiment** as a formal axis (5 values: alert/neutral/warning/success/**proposition**) + **emphasis** layer (critical / high-contrast)
- Anti-explosion discipline: reference base + diffs, invariance pattern
- Workaround for Figma 4-modes limit: nesting libraries

### Color blindness palette references
- **Wong palette** (Nature, 2011) — 8 colors distinguishable by all types
- **IBM Color Blind Safe Palette**
- **Tableau Color Blind 10**
- **Coblis** (Color Blindness Simulator) — for visual validation

---

## 12. Conventions and patterns retained

### Naming
- **English** (open-source ready)
- 4 layers: `core` / `primitives-<brand>` / `semantic` / CSS component
- Reverse-DNS for metadata extensions: `com.<org>.<key>`

### Spacing
- **Gap only** (no margin) — modern flex/grid with `gap` replaces margins
- A single scale consumed as `gap` or `padding` at the point of use
- Storybook: padding on the wrapper decorator (not in the component)

### Components
- No `size` prop on components — size falls from the container via `data-density`
- `selected/checked/active` = scoped mode (data-attribute)
- `disabled` = scoped mode (can also be native HTML `:disabled`)
- `:hover/:active/:focus-visible` = pseudo-classes (vanilla CSS)

### Pseudo-states
- Donnie pattern (`color-mix()`) for hovers/pressed derived from bases
- Explicit derived tokens for recurring patterns (with static fallback)
- CSS at the point of use for specific variations

### Modes
- `[data-color="dark"]`, `[data-contrast="enhanced"]`, `[data-density="compact"|"spacious"]`, `[data-vision="<type>"]` on `<body>`
- Composites by concatenation of CSS selectors

---

## 13. Process / methodology

### Design tokens workflow
1. **Source of truth** in the JSON (DTCG)
2. **Automatic generation** of everything else (CSS, docs, Penpot, Figma)
3. **Auto-extracted metadata** for governance (undecided, deprecated, scope)
4. **Scripted audits** with WCAG ratio computed in OKLCH

### Modification cycle
1. Modify the source `*.tokens.json`
2. `npm run tokens:build` (bundle + generate-css + add_metadata)
3. `validate_metadata.py` — assertions
4. `audit_components.py` — detect a11y regressions
5. Smoke test Storybook (`npm test`)
6. Commit with a message that says the "why" (not the "what")

### Structural decisions to make early
- **Axis vocabulary**: light/dark, density, contrast, vision, brand
- **Pseudo-state strategy**: explicit derived tokens vs CSS at the point of use
- **HC pattern**: increase inter-surface contrasts vs forced borders as band-aid
- **Tone layer**: general or status alone?
- **Components in JSON** or not?

---

## 14. Anti-patterns identified (openTRNTBL sessions)

- **Dead tokens**: created in anticipation of usage, never consumed. At the moment we push them to Penpot/Figma, we discover them. → Regular audit.
- **Forced HC borders**: "band-aid" approach that doesn't address the root (which is: poorly differentiated surfaces in HC). To avoid.
- **Stale bundler**: JSON bundle not regenerated after source cleanup → push outdated. Always `npm run tokens:build` before deploy.
- **dist/ not regenerated after rebrand**: rebranding the source file breaks references in the bundle if not re-bundled.
- **Em-dash `—`** in DTCG descriptions: can silently break some parsers. Plain hyphens safer for portability.
- **`color-mix()` not supported on the tools side** (Penpot 2.14.1, Figma): provide static fallback in `$extensions.<org>.fallback`.

---

## 15. Penpot tooling (2.14.1)

### Observed API limitations
- DTCG types not supported: `duration`, `cubicBezier`, `transition`, `icon` → skip with doc
- `color-mix()` value not supported — static fallback required
- `addToken()` object-only signature (positional broken)
- Em-dash in description → silent failure
- `typography` with `fontFamily: '{ref}'` fails if ref was just created → array literal

### Recommended Penpot pattern
- Penpot catalog = 1:1 mirror of the JSON (with non-pushable types documented separately)
- 1 Penpot theme per logical mode
- Derived tokens with static fallback for the rendering (DTCG calculation preserved for tools that support)

---

## 16. Open meta questions (for your book)

- **When is an alias justified?** Semantic / variance / reuse / other criterion?
- **General presentational layer or not?** (Ismail openTRNTBL answer: not before Tag/Chip/Switch/Tabs critical mass)
- **Visual hierarchy vs functional role**: is `button.primary` really semantic, or just visual hierarchy?
- **Token bundles (Bill)** vs intents (Damato) vs CSS component — which level of abstraction?
- **How to formalize Donnie calculations in DTCG** when tools don't support them?
- **Source-of-truth designer vs record-of-truth DTCG** — how to reconcile (Bill)?
- **Tokens "expected to vary"** (anticipated brand) — how to mark them without making them real `varies`?
- **Auto-generated meta-doc** — what minimal viable format (Diátaxis "Explanation")?

---

## Internal sources (to port)

- `design/research/damato-ds.md` — synthesis of Damato repos
- `design/research/mise-en-mode/SYNTHESIS.md` — book synthesis
- `design/research/complementary-space/notes.md` — spacing manifesto
- `design/research/wise-multi-brand.md` — Wise multi-brand
- `design/research/wise/{refresh,icons,typography,spacing}/notes.md` — refresh case studies
- `design/research/bill-collins/{torquens,dt-demo}/notes.md` — Bill Collins
- `design/QA-REPORT.md` — state of WCAG component audit
- `design/research/colorblind-strategy.md` — color blindness palette strategy

All portable (1 folder = 1 ref set, copy-paste into another project).
