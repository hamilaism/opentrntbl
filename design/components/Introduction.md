# openTRNTBL Design System

The design system powering the **openTRNTBL** web portal — the firmware
interface that turns a dead VNYL TRNTBL into a WiFi-streaming vinyl deck
for Sonos speakers.

This Storybook is the authoritative reference for every UI primitive,
component, and pattern in the portal. It is **not** a rendered product
— it's the spec + playground design and engineering work from.

## What you'll find

### `Primitives/`
The atomic layer — indivisible visual pieces.

- **Overview** — `spinner`, `statusDot`, `check`, `brand` helpers
- **Icons** — 13 SVG icons (9 device types for Row + 4 semantic status icons for Alert) + signal bars helper
- **Tokens/** — Core / Primitives / Semantic galleries (DTCG token visualization)

### `Semantic/`
Auto-generated galleries for the semantic-tier tokens (the public API consumed by components).

- **Surfaces** — `--surface-canvas-background/base/raised/sunken/overlay`
- **Solid** — `--solid-{primary,neutral}-{default,hover,pressed}`
- **Status** — `--status-{success,warning,danger,info}-{bg,text,border}`
- **Text** — typography composites + text colors
- **Spacing** — `--spacing-{tight,snug,default,loose,airy}` (density-aware)
- **Radius.Motion** — radius scale + transition tokens

### `Components/`
Composable building blocks. Each has:
- A `.stories.js` with individual state stories + interactive demos
- A `.md` with matrices (config × state, interaction states) and guidelines

Current roster:
- `Button` — 6 variants (primary / secondary / destructive / toggle / ghost / tonal)
- `Card` — surface primitive
- `Row` — list item (3 trailing types: none / check / signal)
- `Alert` — standalone panel (4 variants: info / warning / error / success)
- `Input` — text / password + inline action
- `SegmentedControl` — exclusive toggle group
- `StatusBadge` — 4 semantic levels (idle / playing / warning / error)
- `Layout` — TitleBlock, SectionHeader, WifiBar (screen scaffolding primitives)

### `Patterns/`
Illustrative full-screen compositions — not reusable components, just
canonical examples showing how primitives combine into real screens.

- **Screens** — `WifiSetup`, `Dashboard`

## Design principles

### 1. Taxonomy before code

Every prop has a single, defended name. **Config states** (prop-driven,
e.g. `selected`, `disabled`, `loading`) are separate from **interaction
states** (CSS pseudo-classes `:hover`, `:active`, `:focus`). Focus is an
independent toggle that combines with hover and active.

### 2. Tokens over hard values

Three-tier DTCG 2025.10 system:
- **Core** (`design/tokens/src/core.tokens.json`) — raw material : OKLCH
  color ramps, dimensions, opacity, font sizes, durations, easings.
- **Primitives** (`design/tokens/src/primitives-openTRNTBL.tokens.json`) —
  brand aliases (accent → gold ramp, success → green ramp, etc.).
- **Semantic** (`design/tokens/src/semantic.tokens.json`) — public API
  (`surface.canvas`, `accent.default`, `status.success.bg`, ...).
  Mode-aware via `$extensions.com.opntrntbl.modes` for `color:dark`,
  `density:compact|spacious`.

The bundler (`scripts/bundle.py`) emits `dist/tokens.json` (matrix DTCG)
and `dist/tokens.studio.json` (hex legacy for Tokens Studio).
The CSS generator (`scripts/generate-css.py`) emits `dist/tokens.css`
with semantic-tier CSS custom properties (no tier prefix in var names —
`--surface-canvas-background`, not `--semantic-surface-canvas`).

### 3. Legacy-compatible

CSS class names (`btn-1`, `btn-2`, `status-play`, `dev-icon`) are preserved
exactly as they appear in `firmware/index.html`. The design system wraps
them with semantic names (`primary`, `playing`) at the API level, but the
generated HTML is identical. This means the firmware can adopt the design
system progressively without a full rewrite.

### 4. Vanilla-compatible

Every component renders from plain HTML string templates. No framework
runtime, no JSX, no build step for consumers. The browser loads
`dist/tokens.css` + `components.css` + copy-pasted HTML.

Storybook is a **dev-only** tool — it never ships to the CHIP (512MB
Debian Jessie, no npm).

## Where things live

```
design/
├── tokens/
│   ├── src/                # Editable DTCG sources (core, primitives, semantic, icons)
│   ├── dist/               # Generated bundles — tokens.json (matrix), tokens.studio.json, tokens.css
│   └── scripts/            # Python 3 generators (bundle.py, generate-core/primitives/semantic/css.py)
├── icons/                  # SVG sources for device icons
├── components/
│   ├── components.css      # Component styles, semantic-token-referenced
│   ├── icons.js            # ICONS map + devIcon / signalBars helpers
│   ├── primitives.js       # spinner / statusDot / check / brand string helpers
│   ├── Tokens/             # Storybook stories that render the token galleries
│   ├── *.stories.js        # Storybook stories per component
│   └── *.md                # Docs + matrices per component
└── README.md               # Repo-level doc
```

## How to use this Storybook

- **Toolbar — Color mode** : light / dark. Sets `data-color` on `<body>`.
  Tokens CSS reacts via `[data-color="dark"]` rules.
- **Toolbar — Density** : compact / comfortable / spacious. Sets
  `data-density`. Spacing tokens scale per mode.
- **Toolbar — Contrast / Vision** : enhanced contrast + colorblind
  simulations (protan/deutan/tritan). Reserved for a future a11y pass.
- **Default mode** : light + comfortable + default contrast.
- **Controls panel** (right sidebar) — live-edit args, see the result.
- **A11y panel** — axe-core violations per story, currently in `todo`
  mode (reports without failing).
- **Docs tab** — auto-generated API table; matrices and guidelines live
  in the sibling `.md` files for human reading on GitHub.

## Testing

`npm test` runs all stories as smoke tests in headless Chromium via
Vitest + Playwright. A story that crashes on render fails the test.
Axe-core checks run but don't block (mode: `todo`). Plan is to promote
to `error` once the existing violations are triaged.

`npm run tokens:build` regenerates `dist/tokens.json`, `dist/tokens.studio.json`
and `dist/tokens.css` from the editable `src/` files.
