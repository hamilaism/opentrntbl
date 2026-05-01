# StatusBadge

Pill-shaped status indicator. Four semantic levels. Only `playing` animates.

The live API table is in the **Docs** tab of the `Components/StatusBadge`
story. This page focuses on the matrix and guidelines.

## Matrix — variant × dot

| Variant | Color | Default visual |
|---------|-------|----------------|
| idle    | neutral grey | ● + label |
| playing | green | ● *pulsing* + label |
| warning | orange | ● + label |
| error   | red | ● + label |

**Non-color accessibility (WCAG 1.4.1)**: the **label** is the primary
signal — it carries the semantics in plain text ("Playing", "Error",
"Warning", "Idle"). No need for a per-variant SVG icon: the label +
color redundancy is enough. The **dot** is kept for its own role —
"live/breathing" signal when `playing` (pulse animation), not for
accessibility.

**Known caveat**: the pairwise success/warning contrast under
achromatopsia drops to 1.27 (below the 1.5 threshold typically cited
to distinguish two colors without a label). That's OK here since the
label does the work. The cell remains flagged in `audit_components.py`
— this is by design.

## Matrix — interaction states

StatusBadge is **read-only** — no hover / focus / pressed states defined.
If you ever make it clickable, it becomes a Button, not a StatusBadge.

## Guidelines

- **Semantic mapping is fixed.** `playing` = green, `warning` = orange,
  `error` = red, `idle` = grey. Don't reuse variants for other semantics.
- **Label is user-facing microcopy** — keep short (≤ 40 chars). Truncation
  with ellipsis is not handled, long labels will wrap.
- **Dot is almost always on.** The dot carries the "live" signal (and
  pulses when `playing`). Use `dot: false` only when the badge is repeated
  in a dense list and the color + label are enough.
- **Don't combine multiple badges** on the same object. If a speaker is
  both "playing" and "partial", prefer the highest-priority one (`warning`
  over `playing`).
