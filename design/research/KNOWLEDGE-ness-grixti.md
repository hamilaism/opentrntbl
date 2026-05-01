# Ness Grixti — synthesis of thought

> Lead Design Systems at **Wise** (cross-border bank). Author of the multi-brand process documented publicly as one of the most mature case studies in the industry.
>
> The most structuring author on **multi-brand operational discipline** and on **governance of a DS that scales**.

---

## Position

Ness Grixti approaches the DS **from the field**, not from theory. Her central concern: *how does a DS stay coherent when it serves several brands, several products, several teams, over time?*

Her distinctive angle: a multi-brand DS is not the DS of one brand repeated N times. It's a **system of explicit variances** where each brand contributes its differences without duplicating everything. And the difficulty is not technical — it's **organizational and operational**.

---

## Major works

### *Making Wise Design (Multi-brand)* (public case study)
Detailed documentation of the Wise process to move from a mono-brand DS to a multi-brand DS that serves:
- 4 consumer themes
- 3 Platform themes (B2B)
- All in **a single variance axis** (brand × light/dark merged)

**Notable innovations**:
- **Sentiment** as a formal axis (not as a tone layer):
  - 5 values: `alert`, `neutral`, `warning`, `success`, `proposition`
  - `proposition` = banking-specific (measured commercial push)
- **Emphasis** as a layer above sentiments:
  - 2D matrix `sentiment × emphasis` (critical / high-contrast)
- **Brand × light/dark merged**: not two dropdowns, a single axis with all combinations

### *Wise Refresh* (typography, spacing, icons, brand)
Case studies of the **tokens-driven identity refresh** process. How to change the typography of the entire ecosystem without breaking components. How to revise spacing without touching layout.

### Bonus articles (medium)
- *How to Get Buy-in and Build a Successful Design System that Scales*
- *The Hidden Work Behind Design System Adoption*
- *Beyond Buy-In: Sustaining Momentum in Design Systems*
(Out of scope for pure tokens — they fall under organizational governance)

---

## Central theses

### 1. Anti-combinatorial-explosion discipline
*"Going from 400 to 4000 tokens avoided"* — the Wise approach does:
- **Reference + diff**: a mode override (brand B in dark) only contains the tokens that change, not a complete copy.
- Allows scaling to 7+ themes without multiplying tokens.

### 2. Invariance pattern
If a token has no interaction behavior, its value is **replicated identically** across all default/hover/active modes. No conditional fork.

→ Example: a `button.surface` that doesn't change with hover will be defined with the same value on the `interaction:hover` mode as on `interaction:default`. Intentionally redundant to remain explicit.

### 3. Formal sentiment ≠ visual tone
Where most DS mix "primary tone" (visual) and "warning sentiment" (intention), Wise separates:
- **Sentiment** = nature of the information (alert/neutral/warning/success/proposition)
- **Emphasis** = intensity of attention (critical/high-contrast)

It's a 2D matrix, not a flat list. And it's very banking-specific: the `proposition` value (measured commercial push) doesn't apply to just any domain.

### 4. Working around tool limits
Figma has a 4-modes-per-file limit. Wise gets around it by **nesting libraries** rather than stacking modes. A pattern to know for anyone hitting the same limit.

### 5. The DS as a product with its own customers
The internal DS has its customers (the product teams). Persona research was done to understand their needs. The DS must be **designed for adoption**, not just for technical coherence.

---

## Key quotes / observations

> "All branded systems have system components linked from the Nebula library, with their brand overrides living within their own brand file they could share out as a branded system."
> — *Making Wise Design*

> "We filter the audit list down to the most used cases — we only build what is essential for immediate delivery."
> — Wise process

> "Before we created the docs site we wanted to understand the customers of the design system. I ran a workshop with our delivery manager within the design system to put together following personas."
> — *Making Wise Design*

---

## Cross-context implications

For any DS that scales:

1. **Reference + diff** systematically for overrides — don't duplicate, don't overload.
2. **Invariance pattern** to apply even when it seems redundant — system readability takes precedence over conciseness.
3. **Sentiment vs emphasis** as a 2D matrix if the domain lends itself (banking, medical, e-commerce). For simpler domains (CMS, internal portal), a single sentiment is enough.
4. **Explicit limits of tools** — know Figma 4 modes max, Penpot SDK 2.x limitations, Tokens Studio caveats. Work around by structure (nested libraries) rather than by hack.
5. **Personas of the DS itself** — who consumes, who contributes, what are their needs. The DS that doesn't know who it exists for won't be adopted.

---

## For which project?

Ness Grixti is particularly relevant for:
- **Multi-brand** DS (at least 2 distinct brands)
- **Multi-product** DS where multiple teams consume
- **Mature DS that scales** (beyond 5 components and 50 tokens)
- DS where teams' **buy-in** is a topic (not a top-down imposed DS)

Less relevant for:
- Single-product mono-brand DS (the multi-brand lessons bring nothing)
- Embryonic DS (still in the foundation phase, no scale)

---

## Links

- **Portfolio**: nessgrixti.com/portfolio
- **Wise case studies**: portfolio/wise-multi-brand, /wise-refresh, /wise-typography, /wise-spacing, /wise-icons
- **Broader articles** (governance, adoption): redesigningdesign.systems
- **Position complementary to Damato**: Wise applies in practice patterns whose foundations Damato theorizes (scoped modes, invariance pattern), with multi-brand operational rigor that goes beyond the theoretical framework.
