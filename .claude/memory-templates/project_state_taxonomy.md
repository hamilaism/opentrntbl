---
name: State taxonomy — config (variant) vs interaction (state) vs focus (orthogonal)
description: Three independent axes that govern how a component changes appearance — keep them separate, don't conflate
type: project
---

A component's appearance is governed by **three independent axes**. Don't conflate them.

1. **Config** (variant) — set by the consumer of the component (a prop, a class, a CSS attribute). Stable through the interaction.
   - Examples : `Button.variant = primary | secondary | tonal | ghost | danger | toggle`, `Alert.variant = info | warning | danger | success`, `Input.type = text | password`.
   - In Figma : modeled as **Variants of a Component Set**.
   - In CSS : modeled as classes or `data-*` attributes.

2. **Interaction** (state) — set by the user's interaction with the component. Transient.
   - Examples : `default`, `hover`, `pressed`, `disabled`, `loading`, `selected`.
   - In Figma : modeled as additional Variant axis (e.g., `state=hover`) OR as separate frames showing each state.
   - In CSS : modeled as pseudo-classes (`:hover`, `:active`, `:disabled`) — never as classes.

3. **Focus** (orthogonal) — set by keyboard navigation. **Independent of state**, can combine with any state.
   - In Figma : either a separate Variant axis (`focus=true|false`), or shown as an additional ring overlay.
   - In CSS : `:focus-visible` (modern, only on keyboard navigation, not mouse).

**Why:** if you conflate state and config, you end up with `Button.variant = primary-hover` which scales badly (you'd need `primary-hover-focus`, etc., for every combination). If you conflate focus and state, the component breaks in keyboard accessibility (focused-but-not-hovered shows wrong style).

**How to apply:**
- For each component : decide upfront what's config (variant) vs interaction (state) vs focus
- Document explicitly in the component's `.md` spec
- In Figma : create separate Variant axes for each, never collapse them
- In CSS : use classes for config, pseudo-classes for interaction, `:focus-visible` for focus

Edge case : `selected` is config when it persists (e.g., a tab that's the active one) but state when it's transient (e.g., a row picked momentarily). Decide per-component, don't generalize.
