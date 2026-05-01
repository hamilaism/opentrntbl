---
name: status.* is the only transverse tone layer (no general "tone" layer)
description: Don't add a generic "tone" abstraction over the DS — only status.* (success/warning/danger/info) qualifies as a transverse tone, and even that is parked until used by Tag/Chip/Switch/Tabs
type: project
---

The DS does not have a generic "tone" layer. The only transverse tone is **`status.*`** (success / warning / danger / info), and even that should not be over-architected until it's actually consumed by enough components (Tag, Chip, Switch, Tabs).

**Why:** Tone abstractions like `tone = neutral | accent | brand | inverse | success | warning | danger | info` look elegant on paper but become a mess in practice :
- `accent` is brand-specific, not transverse
- `inverse` is contextual (depends on parent surface), not a tone
- `neutral` is the absence of tone, not a tone
- Mixing brand-specific (accent) with status (success/warning) in the same axis confuses consumers — should I use `tone=success` for "yes button" or `variant=primary` ?

By keeping `status.*` as the only transverse tone (and treating accent/brand/neutral as separate layers), each component's variant axis stays semantically clean : Button has `variant = primary | secondary | tonal | ghost | danger`, not `variant = primary | tone=success`.

**How to apply:**
- When tempted to extract a "tone" abstraction over multiple components, ask : do they all consume the same set of values ? If not (they rarely do), don't extract it.
- For status semantics specifically : `status.success.*`, `status.warning.*`, `status.danger.*`, `status.info.*` form a clean cluster. Use them where status is the meaning (Alert, StatusBadge).
- Don't proactively migrate Button.variant=danger to "use the status tone" — keep them as variant axes per component until 4+ components actually share the tone semantics.
- Park the abstraction. When the third or fourth component (Tag, Chip, Switch, Tabs) needs status semantics, *then* extract.
