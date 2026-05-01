# Thinking a Design System

> Meta reflection framework for anyone who designs, maintains, or critiques a design system.
>
> Source: Ismail × Claude sessions (April 2026), nourished by the work of **Donnie D'Amato**, **Bill Collins**, **Ness Grixti**, and our own construction (openTRNTBL). Not a prescriptive method nor a recap of a project — a grid for deciding, in another context, without dogma.

---

## Preamble — the nature of the subject

A design system is neither a list of colors nor a bank of components. It's a **structure of shared abstractions** that makes explicit *why* a visual or behavioral decision is made — and that allows several people, at several moments, to make coherent decisions without consulting each other.

This structure is never neutral. Every layer of abstraction we add to it is a decision that simplifies certain future manipulations and complicates others. Doing a DS well essentially means **becoming aware of these tensions** rather than dodging them behind inherited conventions.

The chapters that follow are not a manual. These are the real questions to ask, and a recent state of the art (Damato, Bill Collins, Wise) on the possible answers.

---

## I. The DS as a system of abstractions, not as a catalog

The majority of public DS present themselves as **catalogs**: one page per token, one page per component, usage matrices. It's useful to implement, but it doesn't **explain** anything.

The critical distinction:

| Layer | Object | Reader | Typical question |
|---|---|---|---|
| **Tactical** | Catalog: values, variants, code, CSS classes | Implementer (designer/dev who produces) | "What is the value of `button.primary` in dark?" |
| **Meta** | System: intentions, axes, rules, exceptions | Decision-maker, contributor, future-self | "Why this pattern here and not there?" |

The tactical is generated from the source. The meta is **written** — it's writing, not listing. And that's where the real value of a DS is found when it lives over time: the meta layer survives refactors, technological migrations, team changes.

**Test**: if we delete all doc files *other* than the token list and the Storybook rendering, can a new member understand **why** the system is what it is? If not, the DS only has a tactical layer.

Damato poses the same distinction with other words in *Mise en mode*: the DS must tell its own choices. Ness Grixti embodies it at Wise via case studies that expose the **design process** of the DS itself, not just its result.

---

## II. Abstraction layers and the aliasing grammar

Most DS adopt 2 or 3 layers: *primitives* / *semantic* (sometimes *brand* between the two). It's rarely justified beyond convention. **Why do these layers exist?** Because they each encapsulate **a distinct decision**.

Proposed framework (4 layers):

| Layer | Encapsulated decision | Question answered |
|---|---|---|
| **Core** | What raw values do we have at our disposal? | "What is the amplitude of our raw material (ramps, scales)?" |
| **Brand / primitives** | Which values do we choose to embody our identity? | "What is *our* success green? *Our* gold?" |
| **Semantic decision** | Which intent does each token serve? | "When do we use this alias rather than another?" |
| **Component (CSS)** | How do we compose the visual expression? | "How does this button consume the semantic?" |

Each layer has its **rule of justification**:
- An alias in `primitives` must carry a **brand decision** (not just a renaming).
- An alias in `semantic` must carry a **contextualized decision** (not just an indirection).
- If an alias just relabels without carrying a decision, it's **gratuitous indirection** — to be removed.

It's more demanding than it looks. The empirical test rule: **an alias is legitimate iff its removal would lose information not recoverable otherwise**.

**Critical question**: does the component layer have to exist on the tokens side?

Damato and openTRNTBL answer **no**: the component consumes the semantic, it's not a layer of tokens. Inverting that (creating `button.primary.bg` as a token) amounts to externalizing the component into the DS, which dilutes the component's autonomy and weighs down the combinatorial matrix.

Bill Collins proposes the opposite position with his **higher-order tokens** (Torquens): a bundle `container = {fg, bg, border} × {forced/standard} × {enabled/disabled}` is an aggregation level that allows swapping a whole "expression" through a mixin. It's powerful but it reintroduces the component layer in tokens.

The choice depends on the context. For a product DS (1 product, 1 vocabulary), no bundles: the CSS component layer is enough. For a multi-product / cross-tooling DS (designer Figma ↔ dev React ↔ dev iOS), bundles serve to transport the unit of expression without depending on the target tooling.

---

## III. Variances and invariances — the mapping of a system

**Variance** in a DS is the list of dimensions according to which a value changes. Light/dark is the most well-known axis, but there are others:

- `mode` — light, dark, and other color schemes
- `density` — compact, default, spacious (touch vs mouse)
- `contrast` — default, enhanced (high-contrast for a11y)
- `vision` — color blindness types (palette adapted to type)
- `brand` — multi-brand / multi-product
- `state` — ephemeral pseudo-classes or scoped modes

A good practice: **make the variance matrix explicit** (axis × token). For each token, say:
- what **varies** (and on which axes)
- what is **stable** (intentionally immutable)
- what is **anticipated** (doesn't vary yet, but structured to do so one day)
- what is **undecided** (to be audited)

This 4th status (`undecided`) is underused. It transforms metadata into a governance tool — we filter what hasn't been audited, and we put it through a review.

**Distinction** *that changes everything*:
- "The token **varies**" = its resolved value differs according to the axis (`text.color.primary` is black in light, white in dark).
- "The token is **destined for a scope**" = it's used in a particular case but its value doesn't change (`text.color.disabled` is always gray.500; what changes is *which token is consumed* depending on the component's state).

Confusing the two leads to monstrous matrices. Damato attacks this in *Truly Semantic*: a token has only one resolved value, it's the usage that changes. If we mix the two in a single `varies-on` metadata, we lie to ourselves about the system's nature.

→ **Rename the fields** when the word lies. For example, `varies-on` → `scope` (= "this token is destined for such usage scope", not "the token has N values").

---

## IV. Modes — much more than light/dark

Mode is the most powerful mechanism of the DS: a single HTML/CSS attribute (`[data-mode="dark"]`) reassigns dozens (hundreds) of values simultaneously. It's the basis of:
- `[data-color="dark"]` — color scheme
- `[data-density="compact"]` — touch density
- `[data-contrast="enhanced"]` — HC accessibility
- `[data-vision="deuteranopia"]` — color blindness adaptation
- `[data-locale="ja"]` — typographic internationalization
- `[data-brand="X"]` — multi-brand on the same DOM

Damato pushes the mechanism to the paroxysm in *Mise en mode*: "**critical** is a mode, not a variant** of button. **Selected** is a mode**. **Disabled** is a mode**." What we traditionally call **states** (not hover/focus but durable states) are actually scoped modes on a sub-tree of the DOM.

It's an architectural distinction that changes components: a Button no longer has a `disabled="true"` variant, it lives in a scoped mode `[data-state="disabled"]` that reassigns the values around it.

**Mode composition**: they stack. `[data-color="dark"][data-contrast="enhanced"]` is a composite selector. Penpot and Tokens Studio support it. A token can have overrides per specific combination (e.g., HC in dark mode has a different override than HC alone).

Bill Collins formalizes this logic at the DTCG spec level via his `resolver.json` + `$extends` proposal: explicitly declaring the mode × token combinatorics.

**When is a mode a mode?**

Test: if we can imagine the mode being applied to *a sub-tree of the DOM*, it's a mode. If it necessarily applies to the whole document, it's more of a theme, and the distinction loses interest.

Example: `density:compact` is typically a mode (an admin panel can be compact while the page is default). `lang:ja` is a mode (a bilingual page mixes two locales). `vision:deuteranopia` is more debatable — generally applied globally.

---

## V. Interactive states — the distinction that changes everything

It's the trickiest topic. Hover, focus, active, disabled, selected, checked, error: all of this is called "state" in mainstream documentation. But they are not of the same nature.

**Damato (Mise en mode) proposes a partition**:

| Type | Examples | Modeling |
|---|---|---|
| **Ephemeral pseudo-classes** | `:hover`, `:focus`, `:focus-visible`, `:active` (= pressed) | Vanilla CSS at the point of use. No dedicated token *a priori*. |
| **Durable scoped modes** | `[data-state="selected"]`, `[data-state="critical"]`, `:disabled` | Scoped mode that reassigns CSS vars in a sub-tree. |

Why this distinction is important:
- The `:hover` is **transient and binary** (the cursor is there or not). It lasts a few seconds and doesn't survive the reload. The DS doesn't need to make a token of it, the component computes it at the moment of consumption.
- The `selected`, on the other hand, is **durable** (the state persists in the app, can be serialized). Putting it in mode allows reassigning a whole visual expression (background, text, border, icons, ...) in one go, like a localized theme.

Bill Collins corroborates: *"hover is a mode that resolves `$root`"*. Wise (Ness Grixti) implements compatible logic: a same token (`button.surface`) takes different values via the `interaction` mode (default/hover/active) — when interaction is variant; otherwise the value is replicated.

**The debate on hover as a token**:

The Donnie pattern (color-mix at the point of use) resolves the hover without a token. But the pattern itself is, according to Damato, a *simplification* of his point: before computing a hover, we must ask **whether the hover should exist** (article *Hovercraft*).

It's unusual. Most designers consider hover as a given. Yet many mobile platforms have no hover, and many desktop hovers don't serve much purpose. The DS must open the question, not close it.

**Honest compromise**: if we keep hovers (openTRNTBL case for a mobile-dominant UI), formalize the **recurring patterns** as derived tokens (`surface.base.hover`, `accent.pressed`, etc.) with calculation (`color-mix`) + static fallback. Specific variations remain at the CSS point of use.

---

## VI. Calculation as first-class

Absolute tokens (`#0066FF`) vs computed tokens (`color-mix(...)`): it's a structuring distinction.

**Calculation for whom?**

- The **design tool** (Figma, Penpot 2.14.x) — not (yet) all calculations. Hover tokens derived via `color-mix()` are sometimes displayed as a frozen resolved value, sometimes silently fail.
- The **runtime browser** — `color-mix()` has been native since 2023 (Chrome 111+, Firefox 113+, Safari 16.2+). All calculations resolve in real time.
- The **DTCG spec** — supports calculations via `$value: "calc(...)"` or `color-mix(...)` but not all implementers resolve.

→ Recommended pattern: `$value: "color-mix(...)"` (the calculation **is** the canonical DTCG value) + `$extensions.<org>.fallback.$value: "<static>"` (adjacent static shade for tools that don't compute).

**Donnie pattern and its meta-critique**:

The Donnie D'Amato pattern (Salesforce → PatternFly, taken up by Wise and Radix) is elegant: `color-mix(in oklch, var(--base) 92%, currentColor)` computes the hover from the base and `currentColor` (which is the text). It automatically adapts to the parent mode (light/dark) and doesn't introduce a new token.

But as noted in V, Damato himself considers this a **simplification** of his point. The real debate is not "what percentage for the hover" but "is this hover necessary". The Donnie pattern mechanically answers a question that may not be the right one.

→ **Pragmatic position**: use the Donnie pattern when we have accepted the necessity of the hover. Formalize it as a visible derived token rather than computing it inline (more DRY, more inspectable, more cross-tool portable).

---

## VII. The tone layer — illusion and empirical test

DS often adopt **tones**: `tone.primary`, `tone.secondary`, `tone.ghost`, `tone.warning`, etc. Supposedly shared between components — a Button.primary, a Tag.primary, an Alert.primary would consume the same tone.

**Empirical test on any existing DS**:
- Open the code and grep the `tone.primary` token (or equivalent).
- Count the number of **component families** that consume it.
- If 1 → it's not a tone, it's just the variants of that component disguised as a cross-cutting abstraction.
- If 2-3 → fragile tone, to monitor.
- If 4+ → legitimate tone.

On openTRNTBL, the audit showed that **0 general tones** were shared between ≥2 component families. The only real cross-cutting tone was `status.*` (success/warning/danger/info) consumed by Alert + StatusBadge + Button.destructive — system sentiment, not a visual tone.

Damato, in all of *Mise en mode*, doesn't use the word "tone" **a single time**. For him, a **purpose** (intent grouping by prefix: `feedback-warning-*`, `surface-base-*`) is enough. No need for an additional tone layer.

Wise (Ness Grixti) extends the reflection with a **2D matrix `sentiment × emphasis`**: `sentiment ∈ {alert, neutral, warning, success, proposition}` + `emphasis ∈ {critical, high-contrast}`. But it's very banking-specific (the `proposition` value is the measured commercial push).

→ **Pragmatic position**: don't create a tone layer until it's empirically justified by ≥2 sharing component families. If that happens, make it explicit; otherwise, it's premature abstraction.

---

## VIII. Higher-order tokens — Bill Collins' ambition

Bill Collins (Torquens, dtcg-playground) proposes a step above Damato intents: **higher-order tokens**.

The idea: instead of having 5 individual tokens (`button.primary.bg`, `button.primary.text`, `button.primary.border`, etc.), we have **a single bundle token**:

```json
"button-container.primary.standard.enabled": {
  "$value": {
    "fg": "{accent.text}",
    "bg": "{accent.surface}",
    "border": "transparent"
  }
}
```

And the component does `apply(this, --button-container-primary-standard-enabled)` via a CSS mixin.

**Source-of-truth designer vs record-of-truth DTCG** (Bill Collins):

An important philosophical distinction. The designer thinks in terms of **complete expressions** (this button is *as it is*, its individual tokens have no autonomous meaning). DTCG thinks in terms of **composable elementary values** (each value has its own resolution).

Bill proposes that the **bundle** be the source-of-truth for the designer (the unit of thought), and that individual values be the record-of-truth for DTCG (the unit of storage). Both representations derive from each other.

→ **When to use**: multi-product or cross-tooling DS where the unit of expression has to travel between Figma, Tokens Studio, React code, iOS code, static doc. The bundle preserves the coherent expression.

→ **When NOT to use**: single-product DS with a single toolchain. Bundles add complexity without cross-tooling benefit.

---

## IX. Anti-combinatorial-explosion discipline

A matrix of 4 modes × 5 sentiments × 3 emphasis × 6 states × 2 brands = **720 distinct values** for a single concept. Without discipline, a DS explodes within months.

**Disciplines that mature DS apply**:

1. **Reference + diff** (Wise, Material 3) — a mode override only contains the tokens that change, not a complete copy. It reduces 4000 tokens to 400.

2. **Invariance pattern** (Wise) — if a token has no interaction behavior, its value is **replicated identically** across all default/hover/active modes. No conditional fork.

3. **No numeric scale in semantic** (Damato — *Truly Semantic*) — any semantic token with a numeric suffix (`text-12`, `neutral-500`) is suspect. Semantics speaks of intent (`text.body`, `text.heading-1`), not measurement.

4. **Strict intent grammar** (Damato, *Mise en mode*) — `purpose_priority_property`, max 3 priority levels, max ~33 semantic tokens. Explicit cap, regular audit.

5. **Aggressive removal of dead tokens** — a created token that has no consumer in the code is debt. Audit quarterly, remove what isn't consumed.

→ **Simple test**: if we add a new variance axis (e.g., new brand), how many tokens do we have to define to cover it? If the answer is "all", the discipline isn't in place. If the answer is "only those that differ", it is.

---

## X. The DS and a11y — non-negotiable

A11y is not an optional layer. It's a constraint that structures the values of tokens.

**Recommended global standard**:

| Mode | Criterion |
|---|---|
| Standard (light/dark without HC) | WCAG **AA**: 4.5:1 normal text, 3:1 large/UI |
| HC enhanced | WCAG **AAA**: 7:1 normal text, 4.5:1 large/UI |

**WCAG 1.4.1 Use of Color**: a non-color cue must always exist. The **label** is enough (a StatusBadge "Error" in red with text "Error" is conformant — no need for an additional icon for conformance). The icon is a **redundant bonus**, not an obligation.

**WCAG 2.4.7 Focus Visible**: focus indicator visible on keyboard focus. WCAG 2.4.11 Focus Appearance (AAA, 2.2) specifies minimum 2px solid, 3:1 contrast.

**`:focus` vs `:focus-visible`**: WCAG doesn't decide. Recommended practice:
- Inputs → `:focus` (the ring also displays on mouse click, expected behavior on iOS/macOS text fields)
- Buttons and other clickable elements → `:focus-visible` (ring only on keyboard focus — no ring polluting the mouse click)

**Decorative vs structural**: WCAG 1.4.11 exempts the decorative. A 0.5px iOS-hairline divider doesn't need 3:1 if the info also passes through layout/typo/hover/etc. Trick: 2 border tokens (`border.subtle` decorative low-ratio, `border.default` structural ≥3:1), the component chooses.

**HC doesn't boil down to "more contrast"**: it's increasing ALL contrasts between ALL elements, not just text vs background. The hierarchy of surfaces (canvas, base, raised, sunken) must remain perceptible — otherwise components blend together despite their AAA text.

→ **Anti-pattern to avoid**: putting forced borders in HC to distinguish components that blend together. It's treating the symptom, not the cause. The cause is: surfaces crushed toward pure white or pure black in HC. Clean solution: maintain a real hierarchy of surface values in HC.

**Color blindness**: 4 main types (deuteranopia, protanopia, tritanopia, achromatopsia). Each has its own confusions, so requires **a distinct palette**. A single "color-blind safe" mode (Wong palette) is sub-optimal for each case. Serious references: Wong (Nature 2011), IBM Color Blind Safe, Tableau Color Blind 10. Visual validation: Coblis simulator.

---

## XI. Tooling and process

A DS is not a deliverable, it's a **flow**. The tooling must reflect this flow.

**Single source-of-truth pattern**:

```
JSON DTCG (source of truth)
    ↓ scripts
  ├──> CSS custom properties (consumed by browsers)
  ├──> Tokens Studio JSON (consumed by Figma)
  ├──> Penpot tokens catalog (consumed by Penpot)
  ├──> iOS Swift constants
  ├──> Android XML
  └──> Auto-generated doc
```

Everything is generated from the JSON. **Never manually maintain two representations**: it diverges within weeks.

**Scripted audits**:

- Validation of metadata coherence (`varies` vs `scope` consistent)
- List of `undecided` to audit
- WCAG ratios calculated in OKLCH on the actual text/bg pairs consumed by the CSS
- Orphan tokens (defined but not consumed)
- Phantom tokens (consumed but not defined)

**Integrated test runner**:

Storybook 10+ supports axe-core via addon-a11y and Vitest via addon-vitest with @vitest/browser-playwright. `npm test` automatically runs all a11y tests on all stories. To set up from the start, not in V2.

**Designer ↔ developer** (Bill Collins):

The designer thinks in expressions, the developer thinks in values. The DS must **reconcile** the two without imposing one over the other. Bill proposes an explicit distinction: designer thinking (bundle) generates developer thinking (individual tokens), not the reverse. The `resolver.json` (DTCG 2025.10) formalizes what to resolve to what.

---

## XII. Universal anti-patterns

Identified through Damato, Bill, Wise, and our sessions. To recognize before they take hold.

| Anti-pattern | Symptom | Cause | Antidote |
|---|---|---|---|
| **Dead tokens** | `--solid-primary-pressed` defined but 0 consumers | Creation by anticipation without usage | Quarterly audit, aggressive removal |
| **Illusory tone** | `tone.primary` consumed by 1 single component disguised as cross-cutting abstraction | Confusion between visual hierarchy and functional role | ≥2 consumers test, merge with the component if sole consumer |
| **Scale in semantic** | `text-12`, `neutral-500` at the semantic level | Mix between "intent" and "measurement" | Rename to intent (`text.body`, `text.subtle`) |
| **Contextual suffix** | `*.dark`, `*.inverse`, `*.contrast` (Damato — *Ondark virus*) | Token that lies about its nature (should be a mode override, not a new token) | Scoped mode via `[data-mode="..."]`, no suffix on the name |
| **Band-aid border (HC)** | Forced borders in HC to distinguish components | Surfaces crushed toward pure white/black in HC | Maintain a hierarchy of values between surfaces in HC |
| **Stale dist/** | Generated bundle isn't regenerated after a source cleanup | No auto-build hook, no manual discipline | `npm run tokens:build` pre-commit hook or CI check |
| **Em-dash in description** | Silent parsing failure in DTCG (Penpot 2.14.1, others) | Non-ASCII unicode character | Plain hyphens `-` for portability, em-dash in human doc only |
| **fontFamily with leading hyphens** | `'-apple-system'` interpreted as math/math reference | Tokens Studio / Penpot mis-parses | `system-ui` instead (universal modern CSS equivalent) |

---

## XIII. The questions to ask at the start (and at regular intervals)

No prescriptive checklist. A **list of questions** to structure thinking. Each DS gives its own answers.

**On layer architecture**:
- How many layers do I really need? Why not one more or one less?
- What decision does each layer encapsulate? If I remove this layer, what do I lose?
- Does the component layer live on the tokens side or the CSS side?
- Do my aliases all carry a decision, or are some gratuitous?

**On modes and variance**:
- What variance axes does my system really need to support?
- For each axis, which tokens vary and which remain stable?
- Does the metadata trace the nature of each variance, or is everything mixed?
- How to compose multiple modes (dark + HC, dark + vision-deutero)?

**On states**:
- Are my "states" ephemeral pseudo-classes or scoped modes?
- Should hover exist on this component? Why?
- Do interactive states live in CSS at the point of use, in computed derived tokens, or in scoped modes?

**On sharing between components**:
- Which tokens are **really** shared between ≥2 component families? (Empirical test with grep)
- Are the other "tones" illusions?

**On calculation**:
- Are my derived tokens computed (`color-mix`) or statically frozen?
- Do the target tools (Figma, Penpot, etc.) resolve my calculations? If not, what fallback?

**On a11y**:
- Does my DS impose a global a11y standard (AA outside HC, AAA in HC)?
- Do my audit scripts compute WCAG ratios on the actual text/bg pairs consumed?
- Is my HC "band-aid" (forced borders) or systemic (surface hierarchy preserved)?
- Is color blindness a formal axis with palettes per type, or a single mode?

**On tooling**:
- Is there a single source of truth (the JSON)?
- Does everything else generate from this source, without human intervention?
- Are audits scripted and run automatically (CI or pre-commit)?
- Is the anti-explosion discipline codified (token cap, invariance pattern, etc.)?

**On the meta**:
- Does my DS have a documented meta layer, distinct from the tactical catalog?
- Can a new member understand the *decisions* of the system, not just its values?
- Are the `undecided` tracked and audited?

---

## XIV. Annotated bibliography

### Donnie D'Amato (Design Systems House, W3C Design Tokens CG)

The most structuring author on the **meta layer** of a DS.

- **Mise en mode** (book, 2024-2025) — distinction between ephemeral pseudo-classes vs durable scoped modes. Strict intent grammar `purpose_priority_property`. The mode as architectural primitive.
- **Truly Semantic** (article) — *"Semantic tokens do not include a scale"*. Any semantic token with a numeric suffix is suspect.
- **People's Primitives** (article) — *"Primitives should never be found there [in the experience]. Primitives should only exist in the exercise of assigning values, if at all!"*
- **Hovercraft** (article) — questioning the necessity of hover before designing it. The Donnie color-mix pattern is, according to Damato, a simplification of his point.
- **Ondark virus** (article) — radical critique of contextual suffixes (`*.dark`, `*.inverse`, `*.contrast`). Mechanically the same argument demolishes `*.hover`, `*.pressed`.
- **complementary.space** (single-thesis site) — manifesto on spacing: 2 tokens (`--space-near`, `--space-away`), no `size` prop on components. Density shift = direct ancestor of mise-en-mode.
- **DTCG `$operations` proposal** (July 2023) — general mechanism for transformations on tokens.

### Bill Collins (mrginglymus, DTCG Community Group)

The most structuring author on **cross-tooling**.

- **Torquens** (torquens.bill.works) — higher-order tokens methodology. `{fg, bg, border}` "container" bundle swapped via mixin. Aggregation level above Damato intents. Distinction *source-of-truth designer / record-of-truth DTCG*.
- **dtcg-playground** (GitHub) — concrete DTCG 2025.10 demo with `resolver.json` + `$extends`. Formal modifier × context mechanism.
- **DTCG `resolver.json` proposal** — formalization of mode × token combinatorics at the spec level.

### Ness Grixti (Wise — *Making Wise Design Multi-brand*)

The most structuring author on **multi-brand operational discipline**.

- **Making Wise Design (Multi-brand)** (case study) — formal sentiment as axis (5 values) + emphasis layer (2D matrix). Brand × light/dark merged into a single axis. Anti-explosion discipline: reference base + only split the diffs (400 → 4000 avoided). Invariance pattern for states without interaction. Workaround for Figma 4-modes limit via nested libraries.
- **Wise refresh** (typography, spacing, icons, brand) — case studies of the tokens-driven identity refresh process.

### Color blindness palette references

- **Wong palette** (Nature, 2011) — 8 colors distinguishable by all types of color blindness. The academic reference.
- **IBM Color Blind Safe Palette** — variant optimized for data-viz.
- **Tableau Color Blind 10** — 10 safe colors for data-viz.
- **Coblis** (Color Blindness Simulator) — visual validation tool.

### Spec standards

- **DTCG 2025.10** — Design Tokens Community Group spec, latest version.
- **WCAG 2.2** — accessibility criteria.

---

## XV. End notes

This document is a reflection framework, not a method. Any application on a real project requires **re-opening** each of these questions in light of the specific context. A DS for a medical app doesn't have the same constraints as a DS for a vinyl portal or for a bank.

But the questions themselves remain. And it's by answering them explicitly, even when the answer seems obvious, that a DS becomes a system — not a checklist, not a catalog.

The works of Donnie, Bill and Ness are reference points. Not gospels. The DS that would copy them without questioning would paradoxically be the opposite of their approach, which consists in **questioning inherited conventions**.

> "A well-made DS is a DS that knows why it exists and what it refuses to do."
