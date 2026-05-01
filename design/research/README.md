# Design system — research library

> Library of actionable references for **openTRNTBL** and **cross-project** work.
>
> Strict focus: **pure tokens** (architecture, modeling, vocabulary, modes, states). **Out of scope**: governance, adoption, contribution model, organizational process.

## Structure convention

One folder per author / source. Each folder contains:
- `notes.md` (or `SYNTHESIS.md` for book digests) — direct quotes + pure-tokens-focused analysis
- `images/` (if relevant) — downloaded visuals referenced in notes.md
- Sub-folders if multiple sources from the same author

Everything is cross-project portable — copying the sub-folder is enough.

---

## Navigation

### 🟦 Damato

Donnie D'Amato — DS architect, founder of Design Systems House, member of the W3C Design Tokens CG. The most structuring voice in our library on tokens architecture.

| Source | Focus | Path |
|---|---|---|
| **GitHub repos** (synthesis) | Mise en mode, token-operations, semantic layering, no scale in semantics, JSON-only primitives | [`damato/notes.md`](damato/notes.md) |
| **Mise en mode** (book) | Distinction between ephemeral pseudo-classes vs durable scoped modes. `purpose_priority_property` grammar. 🔒 pattern for private CSS vars | [`mise-en-mode/SYNTHESIS.md`](mise-en-mode/SYNTHESIS.md) (+ `full.md` + `chapters/`) |
| **complementary.space** | Spacing in 2 tokens (`--space-near`, `--space-away`). Density shift = ancestor of mise-en-mode. No `size` prop on components — size falls from the container | [`complementary-space/notes.md`](complementary-space/notes.md) |

### 🟩 Wise (Ness Grixti)

Ness Grixti — Lead Design Systems at Wise. The most operational / multi-brand voice in our library.

| Source | Focus | Path |
|---|---|---|
| **Multi-brand** | Sentiment as a formal axis (5 values) + emphasis layer. Brand theme + light/dark merged. Invariance pattern for states. Anti-explosion discipline (base reference + diffs) | [`wise/multi-brand/notes.md`](wise/multi-brand/notes.md) |
| **Brand refresh** | Tokens-driven identity refresh | [`wise/refresh/notes.md`](wise/refresh/notes.md) |
| **Typography** | Systemic typography refresh | [`wise/typography/notes.md`](wise/typography/notes.md) |
| **Spacing** | Systemic spacing refresh | [`wise/spacing/notes.md`](wise/spacing/notes.md) |
| **Icons** | Systemic icons refresh | [`wise/icons/notes.md`](wise/icons/notes.md) |

### 🟧 Bill Collins

Bill Collins (alias `mrginglymus`) — author of the **`resolver.json` (DTCG 2025.10)** proposal to the Community Group. Complementary angle: higher-order tokens (aggregated bundle) + states as structural mode.

| Source | Focus | Path |
|---|---|---|
| **Torquens** | Higher-order tokens. `{fg, bg, border}` "container" bundle swapped via a mixin. Distinction source-of-truth designer / record-of-truth DTCG. One Rectangle (unifying keystone) | [`bill-collins/torquens/notes.md`](bill-collins/torquens/notes.md) |
| **dtcg-playground** (pivot from dt-demo dead-end) | Concrete DTCG 2025.10 demo — `resolver.json` + `$extends` + modifier × context matrix. Complementary to Damato's `$operations` | [`bill-collins/dt-demo/notes.md`](bill-collins/dt-demo/notes.md) |

---

## Use cases

### For openTRNTBL

This library is used to inform the modeling decisions of the openTRNTBL DS in progress:
- DTCG metadata schema `$extensions.ismo.*` (cf. `MEMORY.md` → `project_ds_token_metadata.md`)
- Distinction modes / states / sentiments / brand
- Tone layer (status only, parking the general tone layer)
- Hover/pressed strategy (Donnie color-mix() pattern in V1)
- Layering primitive → brand → semantic decision → component

### For cross-project (Ismail's book + other DS)

Everything is portable. The convention by author allows extracting a sub-folder and using it elsewhere as a reference set. The `notes.md` files do the pure-tokens curation; the raw content (books `full.md`, full articles) stays nearby for verification.

---

## Out of scope (intentional)

- DS team governance, contribution model, adoption, process
- Tools unrelated to tokens (Figma plugins, Storybook addons, etc.)
- DS case studies that don't touch tokens architecture (e.g., wise-calculator, wise-platform-demo, orion-nebula, scaling-many-systems, practical-guide — all explicitly excluded on 2026-04-26)

If a new ref comes in and overflows the pure-tokens scope, create another folder (`design/governance/`, `design/process/`, etc.) — don't put it here.
