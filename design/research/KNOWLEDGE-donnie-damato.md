# Donnie D'Amato — synthesis of thought

> Founder & Chief Architect of Design Systems House (ds.house). Member of the W3C Design Tokens Community Group. Former Salesforce / Red Hat PatternFly.
>
> The most structuring author on the **meta layer** of a DS and on **modes modeling**.

---

## Position

Damato is probably the contemporary DS thinker who pushes **modeling rigor** the furthest. He refuses inherited conventions (contextual suffixes, numeric scales in semantics, hover as an acquired necessity) and proposes an argued alternative each time.

His distinctive angle: a DS must **document itself** by exposing its architectural choices. The meta layer is not a bonus, it's what makes the system maintainable over time.

---

## Major works

### *Mise en mode* (book, 2024-2025)
- **Central thesis**: the **mode** is the architectural primitive of the DS. Everything we call "variant", "state", "theme" can be reduced to a scoped mode (data-attribute that reassigns CSS vars in a sub-tree).
- **Key distinction**: ephemeral pseudo-classes (`:hover`, `:focus`, `:active`) ≠ durable scoped modes (`selected`, `critical`, `disabled`). The first are vanilla CSS, the second are modes.
- **Strict intent grammar**: `purpose_priority_property`, max 3 priority levels, max ~33 semantic tokens.
- **🔒 pattern**: emoji prefix to make intent CSS variables "private" (non-typable on the editor side).

### *Truly Semantic* (article)
- *"Semantic tokens do not include a scale"*
- Any semantic token with a numeric suffix (`text-12`, `neutral-500`) is suspect. Semantics speaks of **intention** (`text.body`, `text.heading-1`), not measurement.

### *People's Primitives* (article)
- *"Primitives should never be found there [in the experience]. Primitives should only exist in the exercise of assigning values, if at all!"*
- Primitives must never be consumed directly by components. Only the semantic layer is.

### *Hovercraft* (article)
- *"Perhaps we don't need to put so much design into hover effects from a token maintenance perspective."*
- Before computing a hover (`color-mix()` etc.), ask whether the hover should exist at all.
- The Donnie color-mix pattern that circulates as "his" method is, according to him, a **simplification** of his point.

### *Ondark virus* (article)
- Radical critique of contextual suffixes (`*.dark`, `*.inverse`, `*.contrast`). Mechanically the same argument demolishes `*.hover`, `*.pressed`, `*.disabled` as individual tokens.
- A contextual suffix on the name is a lie about the nature of the token. If the value changes according to context, it's a **mode**, not a new token.

### complementary.space (single-thesis site)
- Manifesto on spacing: **2 tokens** (`--space-near`, `--space-away`), period.
- Density shift via `data-attribute` that reassigns CSS Custom Properties = direct ancestor of the *Mise en mode* book (published later).
- **No `size` prop on components**: size falls from the container.

### DTCG `$operations` proposal (July 2023, community group)
- General mechanism for transformations on tokens, broader than `color-mix()`.
- Not adopted in the official spec but structures the thinking on transformations.

### GitHub repos
- `mise-en-mode` — reference implementation of the modes pattern
- `token-operations` — DTCG transformation demos

---

## Central theses (summary)

1. **The mode is the architectural primitive**, not the token. Anything that changes according to context = scoped mode, never a suffix on the name.
2. **Semantics has no numeric scale**. If a semantic token has a scalar suffix, it's disguised theme.
3. **Primitives are not consumed by components** — strictly an internal assignment layer.
4. **The DS must question its conventions** — "should this hover exist?" before "how do I design it?".
5. **Durable states (`selected`, `disabled`) are modes**, not component variants.

---

## Key quotes

> "Such as delivering the concept of 'critical' as a mode instead of a component variant."
> — *Mise en mode*, ch.5

> "Semantic tokens do not include a scale."
> — *Truly Semantic*

> "Primitives should never be found there. Primitives should only exist in the exercise of assigning values, if at all!"
> — *People's Primitives*

> "Perhaps we don't need to put so much design into hover effects from a token maintenance perspective. Using the cursor alone avoids the need to curate specific colors for every type of button."
> — *Hovercraft*

---

## Cross-context implications

For any DS being built today:

1. **Audit your contextual suffixes** — if a token ends in `.dark`, `.inverse`, `.hover`, it's a warning signal. Probably a disguised mode.
2. **Audit your numeric scales in semantic** — `text-12`, `text-14`, `text-16` at the intent level = anti-pattern.
3. **Distinguish your ephemeral pseudo-classes from your durable modes** — refactor the modeling if everything is mixed.
4. **Limit your semantic tokens** — the `purpose_priority_property` grammar with max ~33 tokens is a useful cap.
5. **Reintroduce meta questions** in the design process — every hover/focus/border is a decision, not an obvious given.

---

## For which project?

Damato is particularly relevant for:
- **Mature** DS that wants to consolidate its architecture (not a beginner DS still wading in variants)
- Complex **multi-modes** DS (light/dark + density + a11y + i18n + brand) where modes become unmanageable without strict grammar
- **Multi-product** DS where the cross-cutting semantic layer must remain rigorous
- DS that wants to publish its **meta layer** in open-source (*"a DS that knows why it exists"*)

Less relevant for:
- Simple single-product DS where meta complexity is over-engineering
- Very visually-centered DS where the conversation revolves around values (colors, types) rather than architecture

---

## Links

- **Main site**: ds.house
- **complementary.space**: spacing manifesto
- **GitHub**: github.com/ddamato (mise-en-mode, token-operations, etc.)
- **Articles**: blog.damato.design
- **Book**: *Mise en mode* (epub available)
- **W3C DTCG**: community group contributions
