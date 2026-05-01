---
name: Donnie hover pattern — hovers via color-mix(), not static tokens
description: Hover and pressed colors are calculated from the base color via color-mix(in oklch, ...) at runtime — they're NOT separate tokens to be aliased
type: project
---

Hover and pressed states for buttons / interactive surfaces are **calculated at runtime** via CSS `color-mix(in oklch, ...)` from the base color. They are **NOT separate tokens** to be aliased (no `accent.hover`, `accent.pressed` as primitives).

Pattern (named after Donnie d'Amato's blog) :

```css
.btn-tonal {
  background: var(--surface-tonal-bg);
  color: var(--text-color-primary);
}

.btn-tonal:hover {
  /* Calculated : 16 % overlay of text-primary on base */
  background: color-mix(in oklch, var(--surface-tonal-bg), var(--text-color-primary) 16%);
}

.btn-tonal:active {
  background: color-mix(in oklch, var(--surface-tonal-bg), var(--text-color-primary) 24%);
}
```

The mix ratios are typically 8 % / 16 % / 24 % depending on the desired pressure of the interaction.

**Why:**
- Hover/pressed for *every* surface type would otherwise require N × 2 extra tokens (every variant of every surface state). The combinatorial explosion is unmanageable.
- The mix is mathematically consistent across modes (light, dark, HC) — you don't need to redefine each hover token per mode.
- It's how iOS / macOS / native UIs work — the platform calculates the pressed state.

**How to apply:**
- Don't create tokens like `accent.default.hover`, `accent.default.pressed`. Use `color-mix(in oklch, var(--accent-default), var(--text-color-primary) 16%)` directly in the component CSS.
- In Figma : `color-mix` is not natively supported by variables. The hover/pressed values must be computed manually for each cell and stored as **literal hex** (not as variable aliases). Document them clearly as "calculated, not aliasable".
- In Penpot : same situation — no native `color-mix`. Calculate the resulting OKLCH mid-point, convert to hex, store as literal in the variant.
- Exception : `.btn-1` (primary) uses `opacity: 0.85` for hover instead of color-mix (because the bg is already the strongest text color, mixing further wouldn't be visible). This is documented.

This pattern keeps the token surface area small and the math consistent. Don't fight it by inventing intermediate tokens.
