# Neumorphic — Accessibility audit (pre-build)

Neumorphic aesthetics and WCAG 2.1 are in structural tension.

## What passes

| Token | Against surface | Ratio | WCAG |
|---|---|---|---|
| `text.primary` | canvas | ~14:1 | ✓ AAA |
| `text.secondary` | canvas | ~5:1 | ✓ AA |
| `border.focus` | canvas | ~4.5:1 | ✓ AA |
| `accent.default` | canvas | ~4.5:1 | ✓ AA |
| `status.*.text` | status bg | ≥4.5:1 | ✓ AA (text on status bg) |

## What fails

| Token | Ratio | WCAG | Why |
|---|---|---|---|
| `border.subtle` | ~1.3:1 | ✗ | Hairline border is the aesthetic |
| `border.default` | ~1.8:1 | ✗ | Same |
| `border.strong` | ~3:1 | ✗ (borderline) | UI chrome threshold is 3:1 |
| `text.placeholder` | ~3:1 | ✗ | Below 4.5:1 |
| `status.*.bg` | ~1.5:1 vs canvas | ✗ | Status conveyed by color area alone |

## Mitigation strategies (if shipping this theme)

1. **Supplement borders with shadows** — the elevation system (`elevation.raised`, `elevation.sunken`) communicates affordance without relying on border contrast. Where a border exists, it's decorative.

2. **Status via icon + text, not background** — rely on text color (which passes) and iconography to communicate status. The tinted bg is a hint, not the signal.

3. **Focus ring stays high-contrast** — `border.focus` is the only UI-chrome token that must pass, and it does (accent hue, L=0.55 on L=0.92 surface).

4. **Provide an HC override** — if used in production, pair with a `[data-contrast="enhanced"]` override that restores full contrast at the cost of the neumorphic aesthetic.

## Verdict

Neumorphic is viable as a **non-default theme for users who explicitly opt in**, never as the system default. It should ship with a visible warning in settings: "This theme has reduced contrast and may not meet accessibility standards for some users."
