# David Fusilier — synthesis of thought

> Product Designer at **Spotify**, Brooklyn. Author of a color naming system that encodes WCAG contrast **directly in the token name**.
>
> The most structuring author on **a11y as a naming convention** — not as a post-hoc audit nor as a runtime calculation, but as a grammar that makes WCAG conformance **readable at a glance** from the names.

---

## Position

Where Damato thinks about modes, Bill Collins thinks about cross-tooling, and Ness Grixti thinks about operational discipline, **David Fusilier thinks about naming convention**.

His central thesis: WCAG conformance is neither an after-the-fact audit nor a runtime calculation — it's a **systemic rule** integrated into the grammar of token names. If I look at `green105` and `gray025` side by side, the shade difference (105 - 025 = 80) immediately tells me whether the pair satisfies AA, AAA, or neither — without tools, without calculation, without guessing.

It's more modest than an automatic generation algorithm. But it's **more systemic** as a method: it changes the day-to-day conversation in the team.

---

## Major works (GitHub repos `dfusilier`)

### `color-shades` ⭐ (the most structuring)

> "Determine color contrast at a glance from the names of colors."

**Naming convention**:
- **Shades go from 0 to 200** indexed on perceived luminance
- Names integrate the shade: `green105`, `gray025`, `blue140`, etc.
- The **shade difference** between two tokens predicts their contrast ratio

**Derived rules**:

| Shade difference | WCAG ratio | Use case |
|---|---|---|
| ≥ 100 | ≥ 4.5:1 | Normal text (WCAG AA) |
| ≥ 75 | ≥ 3.0:1 | UI components, large text (WCAG 2.4.11) |

→ Conformance **readable at a glance** from the names. No more need for Coblis, Stark, or an audit script to validate.

### `type-director` + `type-director-compass`

Generative typography system through interpolation between **constraint pairs**:
- For each breakpoint (phone, tablet, desktop): base + max font-size, base + max line-height
- The system computes intermediate values proportionally → modular scale

**Per-typeface adjustments**:
- `fontSizeAdjustment` (Verdana looks 11% larger than Georgia at the same size)
- `lineHeightAdjustment`
- `uppercaseAdjustment`

→ Allows **swapping typefaces** without breaking the typographic hierarchy.

Export to **JSON + Theo tokens** (cross-platform). No direct a11y angle on this project.

### `space`

Sass toolkit inspired by **Nathan Curtis** "Space in Design Systems".

5 explicit space patterns:
1. **Insets** — padding parent → children
2. **Stack** — vertical margins between siblings
3. **Inline** — horizontal margins between siblings
4. **Gutter** — column spacing in grids
5. **Bustout** — negative margins for overflow

Scale: `(0, 0.5, 1, 2, 3, 4, 6, 8, 12, 16)` × 4px base.

→ The naming of the **5 categories** is what structures — not the values themselves.

---

## Central theses

### 1. The naming convention carries a11y semantics
Instead of separating names (`primary`, `secondary`) from a11y (post-hoc audit), encode contrast **in the grammar itself**. When a11y is in the name, it doesn't get lost.

### 2. A systemic grammar > one-off rules
Rather than "careful, this blue must be dark enough to pass AA", say "any pair of shades ≥100 is AA". It **scales**: adding a new color doesn't require re-checking the 50 existing pairs — the rule is intrinsic.

### 3. Explicit naming > implicit naming
Prefer `gray025` over `gray-light` or `text-tertiary`. The numeric shade is **precise** and **predictable**, where "light" is subjective and "tertiary" obscure.

### 4. Typography as a constrained system
Type Director: 4-5 variables → entire scale derived. No one-off decisions size by size.

### 5. Space as a named system
Don't call padding "spacing-md" but inscribe it in a **semantic category** (Inset, Stack, Inline, Gutter, Bustout). The function of the space is explicit, not just its size.

---

## Key quotes / observations

> "Determine color contrast at a glance from the names of colors."
> — color-shades, README

> Numerical shades range from 0 to 200 based on luminance. Colors with shade differences ≥100 achieve ≥4.5:1 contrast.
> — color-shades

---

## Cross-context implications

For any DS that wants to industrialize a11y **without** heavy tooling infrastructure:

1. **Index shades on perceived luminance** (OKLCH `L`) — not on arbitrary Material/Tailwind/etc. conventions. When shade = luminance, contrast calculations become **predictable**.
2. **Adopt a naming grammar that encodes a11y** — `accent125` rather than `accent-light`. The numeric suffix allows mental reasoning.
3. **Define explicit thresholds** in the doc: "token pairs with difference ≥X pass WCAG level Y". This replaces manual audit.
4. **Complement with a script** (cf. `audit_components.py`) for the pairs actually consumed — the convention is necessary but not sufficient.
5. **Name the space categories** (Inset/Stack/Inline/Gutter/Bustout) — the value is not the function.

---

## For which project?

David Fusilier is particularly relevant for:
- DS where a11y is **non-negotiable** but the team doesn't have the infrastructure to automate the calculation on the fly
- **Distributed** teams (designers, devs, content writers) who must be able to reason about a11y without tools
- DS where **name readability** is a quality attribute (open-source, multi-team)
- DS refactor that wants to **rationalize** its a11y-first naming convention

Less relevant for:
- Very visually-centered DS where names are marketed (`twilight-mauve`, `desert-sand`) — the numeric shade breaks the expression
- Projects that really want runtime calculation (Spotify dynamic cover art for example) — color-shades is static

---

## Connections with other authors

- **Damato**: convergence on naming rigor. Damato says *"semantic tokens do not include a scale"*; David would index at the primitives/core level, not semantic. Coherent: the numeric shade lives on the primitive side (where the scalar position makes sense), the semantic stays intent-only.
- **Bill Collins**: David doesn't formalize cross-tooling thinking, but his naming convention **travels very well** between Figma, code, Penpot, doc. That's its natural portability.
- **Ness Grixti**: Wise probably also uses a shade convention. Compatible with Wise's reference + diff discipline.

---

## Our adoption (openTRNTBL)

We use **exactly** the David Fusilier pattern without having stated it as such:
- neutral / accent / success / warning / danger / info ramps indexed **0-200 by luminance**
- Differences between shades = predictable ratios (`n.0` vs `n.200` = 21:1, that's the maximum possible)
- In light HC, `text-color.primary` (`n.0`) on `surface.base` (`n.200`) = difference 200 = max contrast

His convention is **already integrated** into openTRNTBL via the OKLCH generator (`design/tokens/scripts/generate-core.py`). It's probably also **the right default convention** for most modern DS.

---

## Sources

- **GitHub**: [github.com/dfusilier](https://github.com/dfusilier)
- **color-shades**: [github.com/dfusilier/color-shades](https://github.com/dfusilier/color-shades) — the most structuring repo
- **type-director**: [github.com/dfusilier/type-director](https://github.com/dfusilier/type-director)
- **space**: [github.com/dfusilier/space](https://github.com/dfusilier/space)
- **Inspiration**: Nathan Curtis, *"Space in Design Systems"* (Medium, EightShapes) for `space`
