# Bill Collins — synthesis of thought

> Alias **mrginglymus** on GitHub. Active member of the W3C Design Tokens Community Group. Contributor of formal proposals to the DTCG 2025.10 spec.
>
> The most structuring author on the **cross-tooling toolchain** of a DS and on **designer ↔ developer portability**.

---

## Position

Bill Collins treats the DS as a **system for transforming representations**. His central concern is not the architecture of semantic layers (Damato) nor the multi-brand operational discipline (Wise) — it's the **portability of design expression** across a heterogeneous toolchain: Figma, Tokens Studio, React code, iOS code, Storybook, static documentation.

For him, a DS's fragility emerges at the **inter-tool transition** moments. The designer thinks in coherent bundles (a button, an input, a complete expression). The developer thinks in composable elementary values. Each tool speaks its own dialect. The DS must reconcile without imposing.

---

## Major works

### Torquens (torquens.bill.works)
- **Public methodology** on *higher-order tokens*. Manifesto-style educational site.
- **Central idea**: instead of N individual tokens (`button.primary.bg`, `button.primary.text`, `button.primary.border`...), a single **bundle** that components consume from a single mixin:

```json
"button-container.primary.standard.enabled": {
  "$value": {
    "fg": "{accent.text}",
    "bg": "{accent.surface}",
    "border": "transparent"
  }
}
```

- **Designer/dev friction** explicitly stated:
  > "Designers and developers use radically different techniques to apply design tokens to their outputs — which are reflective of, and optimised for, the tooling in use by each discipline."

### dtcg-playground (GitHub `mrginglymus/dtcg-playground`)
- Concrete DTCG 2025.10 demo with `resolver.json` + `$extends` + `terrazzo.config.ts`.
- Reference implementation of the formal modes model.

### DTCG `resolver.json` proposal
- Formal mechanism for a **modifier × context matrix** at the spec level.
- Allows declaring: "this token has this value in mode A, that other value in mode B + condition C, etc.", on top of the resolution engine.
- Complementary to Damato's `$operations` proposal — one declares the matrix (Bill), the other transforms value→value (Damato).

### One Rectangle (architectural concept)
- Unifying keystone that combines **color + shape + size + typography** in a single CSS class.
- Concept absent from other references. Allows thinking of the graphic element as a complete and coherent expression.

---

## Central theses

### 1. Source-of-truth designer vs record-of-truth DTCG
Fundamental philosophical distinction in Bill's thinking:
- The **designer** thinks in *complete expressions* — this button is *as it is*, its individual tokens have no autonomous meaning for them.
- **DTCG** stores in *composable elementary values* — each value has its own resolution, each transformation is explicit.
- The **bundle** is the designer's *source-of-truth* (the unit of thought). Individual values are DTCG's *record-of-truth* (the unit of storage). Both representations derive from each other via resolution.

### 2. Cross-tooling pragmatism
When a tool can't resolve a calculation, **pre-compute** the value. When a format doesn't support a syntax, **emit a compatible variant** at the pipeline edge. DTCG rigor at the source, flexibility at the edges.

### 3. Higher-order tokens > simple intents
A simple intent (`accent.bg`) doesn't capture the complete expression. A bundle (`button-container.primary.standard.enabled`) lets you swap a coherent expression without touching individual values.

### 4. The DTCG spec as contract
Bill explicitly invests in the **community group spec** because a DS without a formal inter-tool contract is doomed to diverge. `resolver.json` is his proposed contract for modes.

---

## Key quotes

> "Designers and developers use radically different techniques to apply design tokens to their outputs—which are reflective of, and optimised for, the tooling in use by each discipline."
> — Torquens, intro

> "Hover is a mode that resolves `$root`."
> — Bill Collins (DTCG community)

(Strong implicit position, in agreement with Damato on the status of hover as a mode rather than as a variant)

---

## Cross-context implications

For any DS that has to travel between tools:

1. **Formally define the modes × tokens matrix** — not just light/dark, but all possible combinations. Penpot, Figma, code, doc must all speak about the same graph.
2. **Distinguish what is source-of-truth designer vs record-of-truth DTCG** — don't impose one vision over the other. Both derive from each other.
3. **Consider bundles** when the unit of expression has to travel — especially for multi-product DS or with a complex toolchain.
4. **Document what each tool CAN'T do** — static fallback, unsupported type, etc. It's a reality, not a failure.
5. **Invest in the DTCG community group spec** rather than in proprietary conventions — for long-term interoperability.

---

## For which project?

Bill Collins is particularly relevant for:
- **Multi-tooling** DS (Figma, Tokens Studio, React code, iOS code, Storybook, etc.) where designer/dev friction is recurring
- **Multi-product** DS where the unit of expression has to travel
- DS published as a **shared spec / library** (not an internal mono-product DS)
- Team that invests in the **long-term DTCG spec** and wants to influence or follow its evolution

Less relevant for:
- Single-product DS with minimal toolchain (no real inter-tool friction)
- DS where bundle thinking is over-engineering (a Button with 3 CSS props doesn't need a higher-order token)

---

## Links

- **Torquens**: torquens.bill.works (methodology, manifesto)
- **GitHub**: github.com/mrginglymus (dtcg-playground, dt-demo)
- **W3C DTCG**: community group — `resolver.json` + `$extends` proposal
- **Position complementary to Damato**: `$operations` (Damato, value→value) + `resolver.json` (Bill, modifier×context) are the two DTCG proposals that complement each other
