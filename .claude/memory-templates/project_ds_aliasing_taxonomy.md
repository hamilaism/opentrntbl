---
name: DS aliasing 4-layer taxonomy (primitive → brand → semantic → component)
description: The strict 4-layer architecture used in the openTRNTBL design tokens — every alias must justify itself by carrying a decision
type: project
---

The design tokens system is structured in **4 strict layers**. Every alias should justify its existence by **carrying a decision** — not just renaming the same value across layers.

| Layer | Role | Example |
|---|---|---|
| **Primitive** | The catalog of available options. No semantic meaning. | `core.palette.gold.125`, `core.dimension.30`, `core.opacity.50` |
| **Brand** | The brand's expression — what's "openTRNTBL" specifically (vs another brand using the same primitives). | `brand.color.accent.125 → core.palette.gold.125` |
| **Semantic** | A decision : "in this product, the `accent.default` is `accent.125` because..." Carries intent. | `semantic.accent.default → brand.color.accent.125` |
| **Component** | Bound at the component instance level. | Button.background = `semantic.accent.default` |

**Why:** without this discipline, you get tokens like `color.button.primary.background = #e8a932`. Now you can't rebrand without touching every component. By going `Component → Semantic → Brand → Primitive`, a multi-brand swap requires only changing the Brand layer (1 file), not every component.

**How to apply:**
- Don't create a Brand alias if it's identical to its Primitive (no decision carried) — just use the Primitive directly
- Don't create a Semantic alias if it doesn't represent a decision specific to the product context — same rule
- The Component layer should ONLY reference Semantic (or in rare exceptions, Brand). Never reference Primitives directly from Components — that breaks the rebrand contract.

In Figma terms : Mode collection = Semantic. Brand-openTRNTBL collection = Brand. Core collection = Primitive. Components use variables from the Mode collection (with rare exceptions for non-semantic concerns like radius/spacing which come from Brand or Density).
