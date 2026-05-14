#!/usr/bin/env python3
"""
Modern theme resolver (ShadCN/Aceternity-inspired).

Reads src/theme.tokens.json and emits tokens.css with:
  1. Token vars scoped to [data-token-system="flat-ui"]
  2. Dark overrides
  3. Density overrides (compact / spacious)
  4. Component overrides — border + shadow-sm on cards, 1px borders on inputs
     and buttons, overrides seg-segment hardcoded shadow

Visual identity: white cards on zinc-50 canvas, 1px zinc-200 border + shadow-sm
as depth cue, 6px radius, cool-tinted neutral palette, fast motion.
"""

import json
import pathlib

ROOT = pathlib.Path(__file__).parent
SRC  = ROOT / "src" / "theme.tokens.json"
OUT  = ROOT / "tokens.css"

SKIP_KEYS = {"$description", "$type", "$value", "$extensions"}


def load():
    with open(SRC, encoding="utf-8") as f:
        return json.load(f)


def token_path_to_css_var(parts: list) -> str:
    if parts[0] in ("semantic", "base"):
        parts = parts[1:]
    return "--" + "-".join(parts)


def format_value(value) -> str:
    if isinstance(value, list):
        items = []
        for v in value:
            items.append(f'"{v}"' if " " in str(v) else str(v))
        return ", ".join(items)
    if isinstance(value, bool):
        return str(value).lower()
    return str(value)


def format_cubic_bezier(value) -> str:
    if isinstance(value, list) and len(value) == 4:
        return f"cubic-bezier({', '.join(str(v) for v in value)})"
    return str(value)


def walk(node: dict, path: list, collector: dict, mode_key=None):
    if "$value" in node:
        css_var  = token_path_to_css_var(list(path))
        raw_type = node.get("$type", "")

        if mode_key:
            ext = node.get("$extensions", {})
            if mode_key not in ext:
                return
            raw = ext[mode_key]
        else:
            raw = node["$value"]

        if raw_type == "cubicBezier":
            value = format_cubic_bezier(raw)
        elif isinstance(raw, list):
            value = format_value(raw)
        elif isinstance(raw, (int, float)):
            value = str(raw)
        else:
            value = raw

        collector[css_var] = value
        return

    for key, child in node.items():
        if key in SKIP_KEYS:
            continue
        if isinstance(child, dict):
            walk(child, path + [key], collector, mode_key)


def emit_block(selector: str, tokens: dict, indent: int = 2) -> list:
    lines = [f"{selector} {{"]
    pad = " " * indent
    for var, val in tokens.items():
        lines.append(f"{pad}{var}: {val};")
    lines.append("}")
    return lines


COMPONENT_OVERRIDES = """\
/* ── Component overrides ───────────────────────────────────────────────────
 * Modern (ShadCN/Aceternity): white cards on zinc-50 canvas. Depth cue =
 * 1px zinc-200 border + shadow-sm. 6px radius. Focus ring = near-black ring.
 * ── ─────────────────────────────────────────────────────────────────────── */

/* Body */
[data-token-system="flat-ui"] body {
  background: var(--surface-canvas-background);
}

/* Card — white + 1px border + shadow-sm */
[data-token-system="flat-ui"] .card {
  background: var(--surface-base-background);
  border: 1px solid var(--border-default);
  box-shadow: var(--surface-raised-elevation);
}

/* Row — subtle hover tint */
[data-token-system="flat-ui"] .row:hover  { background: var(--surface-base-hover); }
[data-token-system="flat-ui"] .row:active { background: var(--surface-base-pressed); }

/* Row separator — slightly more visible in flat style */
[data-token-system="flat-ui"] .row + .row { border-top-color: var(--border-default); }

/* Buttons — 3-step density scale (shift down vs V1).
   default=0.75rem  compact=0.5rem(ShadCN py-2)  spacious=1rem */
[data-token-system="flat-ui"] .btn,
[data-token-system="flat-ui"] .btn-2,
[data-token-system="flat-ui"] .btn-ghost,
[data-token-system="flat-ui"] .btn-disconnect,
[data-token-system="flat-ui"] .btn-toggle {
  padding: 0.75rem var(--spacing-default);
  font-size: var(--text-small-size);
}
[data-token-system="flat-ui"][data-density="compact"] .btn,
[data-token-system="flat-ui"][data-density="compact"] .btn-2,
[data-token-system="flat-ui"][data-density="compact"] .btn-ghost,
[data-token-system="flat-ui"][data-density="compact"] .btn-disconnect,
[data-token-system="flat-ui"][data-density="compact"] .btn-toggle {
  padding: 0.5rem var(--spacing-default);
}
[data-token-system="flat-ui"][data-density="spacious"] .btn,
[data-token-system="flat-ui"][data-density="spacious"] .btn-2,
[data-token-system="flat-ui"][data-density="spacious"] .btn-ghost,
[data-token-system="flat-ui"][data-density="spacious"] .btn-disconnect,
[data-token-system="flat-ui"][data-density="spacious"] .btn-toggle {
  padding: 1rem var(--spacing-default);
}

/* btn-2 — border + sunken bg */
[data-token-system="flat-ui"] .btn-2 {
  background: var(--surface-base-background);
  border: 1px solid var(--border-default);
  box-shadow: none;
}
[data-token-system="flat-ui"] .btn-2:hover  { background: var(--surface-base-hover);   border-color: var(--border-strong); }
[data-token-system="flat-ui"] .btn-2:active { background: var(--surface-base-pressed); border-color: var(--border-strong); }

/* btn-toggle — keep border */
[data-token-system="flat-ui"] .btn-toggle { box-shadow: none; }
[data-token-system="flat-ui"] .btn-toggle:hover  { border-color: var(--border-strong); }

/* btn-disconnect — no shadow */
[data-token-system="flat-ui"] .btn-disconnect { box-shadow: none; }

/* Input — already has border in components.css */
[data-token-system="flat-ui"] .inp {
  background: var(--surface-sunken-background);
  border-color: var(--border-default);
}
[data-token-system="flat-ui"] .inp:hover:not(:focus):not(:disabled) {
  background: var(--surface-sunken-hover);
  border-color: var(--border-strong);
}

/* SegmentedControl — remove the hardcoded iOS box-shadow on active tile */
[data-token-system="flat-ui"] .seg-track {
  background: var(--surface-canvas-background);
  border-color: var(--border-default);
}
[data-token-system="flat-ui"] .seg-segment.active {
  background: var(--surface-base-background);
  box-shadow: none;
  border: 1px solid var(--border-default);
}

/* Alert — explicit border */
[data-token-system="flat-ui"] .alert {
  background: var(--surface-base-background);
  border: 1px solid var(--border-default);
  box-shadow: none;
}

/* Wifi bar — explicit border */
[data-token-system="flat-ui"] .wifi-bar {
  background: var(--surface-base-background);
  border: 1px solid var(--border-default);
}

/* dev-icon — subtle bg, no border needed (borderless icon container) */
[data-token-system="flat-ui"] .dev-icon {
  background: var(--surface-sunken-background);
}
/* Dark: all dark surfaces cluster near 0.10 → hardcode a clearly lighter fill */
[data-token-system="flat-ui"][data-color="dark"] .dev-icon {
  background: oklch(0.24 0.012 264);
  border: 1px solid var(--border-default);
}

/* btn-ghost--sm — (0,3,0): beats both the base ghost override (0,2,0)
   and the density compact override (0,3,0, earlier in file). */
[data-token-system="flat-ui"] .btn-ghost.btn-ghost--sm {
  padding: var(--spacing-snug) var(--spacing-default);
  font-size: var(--text-small-size);
  width: auto;
}

/* ── High contrast — light ───────────────────────────────────────────────────
 * Borders max-contrast. Text pure black. Status: WCAG AAA dark-on-vivid. */
[data-token-system="flat-ui"][data-contrast="enhanced"] {
  --text-color-primary: oklch(0 0 0);
  --text-color-secondary: oklch(0.08 0 0);
  --text-color-placeholder: oklch(0.14 0 0);
  --text-color-disabled: oklch(0.20 0 0);
  --border-subtle: oklch(0.45 0 0);
  --border-default: oklch(0.30 0 0);
  --border-strong: oklch(0 0 0);
  --border-focus: oklch(0 0 0);
  --status-success-bg: oklch(0.37 0.1166 145);
  --status-success-text: oklch(0.9485 0.0916 145);
  --status-warning-bg: oklch(0.3881 0.0963 55);
  --status-warning-text: oklch(0.9602 0.0232 55);
  --status-danger-bg: oklch(0.3983 0.1557 29);
  --status-danger-text: oklch(0.9607 0.0195 29);
  --status-info-bg: oklch(0.3832 0.1265 255);
  --status-info-text: oklch(0.9584 0.0201 255);
}

/* ── High contrast — dark ────────────────────────────────────────────────────
 * Canvas pure black. Borders near-white. Text pure white. */
[data-token-system="flat-ui"][data-color="dark"][data-contrast="enhanced"] {
  --surface-canvas-background: oklch(0 0 0);
  --surface-base-background: oklch(0.10 0 0);
  --text-color-primary: oklch(1 0 0);
  --text-color-secondary: oklch(0.96 0 0);
  --text-color-placeholder: oklch(0.90 0 0);
  --text-color-disabled: oklch(0.78 0 0);
  --border-subtle: oklch(0.50 0 0);
  --border-default: oklch(0.80 0 0);
  --border-strong: oklch(1 0 0);
  --border-focus: oklch(1 0 0);
  --status-success-bg: oklch(0.7392 0.147 145);
  --status-success-text: oklch(0 0.0582 145);
  --status-warning-bg: oklch(0.7662 0.147 55);
  --status-warning-text: oklch(0 0.035 55);
  --status-danger-bg: oklch(0.7697 0.1363 29);
  --status-danger-text: oklch(0 0.0552 29);
  --status-info-bg: oklch(0.7555 0.1275 255);
  --status-info-text: oklch(0 0.0533 255);
}

/* ── Vision — achromatopsia (no color) ──────────────────────────────────────*/
[data-token-system="flat-ui"][data-vision="achromatopsia"] {
  --accent-default: oklch(0.2707 0 0);
  --text-color-on-accent: oklch(1 0 0);
  --status-success-bg: oklch(0.9596 0 0);
  --status-success-text: oklch(0.2707 0 0);
  --status-warning-bg: oklch(0.8807 0 0);
  --status-warning-text: oklch(0.2707 0 0);
  --status-danger-bg: oklch(0.5641 0 0);
  --status-danger-text: oklch(1 0 0);
  --status-info-bg: oklch(0.7556 0 0);
  --status-info-text: oklch(0 0 0);
}
[data-token-system="flat-ui"][data-color="dark"][data-vision="achromatopsia"] {
  --accent-default: oklch(0.9596 0 0);
  --text-color-on-accent: oklch(0.2707 0 0);
  --status-success-bg: oklch(0 0 0);
  --status-success-text: oklch(0.8807 0 0);
  --status-warning-bg: oklch(0.2707 0 0);
  --status-warning-text: oklch(0.9596 0 0);
  --status-danger-bg: oklch(0.5641 0 0);
  --status-danger-text: oklch(0 0 0);
  --status-info-bg: oklch(0.381 0 0);
  --status-info-text: oklch(1 0 0);
}

/* ── Vision — deuteranopia (no green) ───────────────────────────────────────*/
[data-token-system="flat-ui"][data-vision="deuteranopia"] {
  --status-success-bg: oklch(0.9492 0.0766 195);
  --status-success-text: oklch(0.3721 0.0636 195);
  --status-warning-bg: oklch(0.9554 0.0962 100);
  --status-warning-text: oklch(0.3792 0.079 100);
  --status-danger-bg: oklch(0.9602 0.0232 55);
  --status-danger-text: oklch(0.3881 0.0963 55);
}
[data-token-system="flat-ui"][data-color="dark"][data-vision="deuteranopia"] {
  --status-success-bg: oklch(0.1542 0.0271 195);
  --status-success-text: oklch(0.8684 0.0944 195);
  --status-warning-bg: oklch(0.1589 0.0342 100);
  --status-warning-text: oklch(0.8769 0.1234 100);
  --status-danger-bg: oklch(0.1613 0.0413 55);
  --status-danger-text: oklch(0.885 0.0711 55);
}

/* ── Vision — protanopia (no red) ────────────────────────────────────────────*/
[data-token-system="flat-ui"][data-vision="protanopia"] {
  --status-success-bg: oklch(0.9584 0.0201 255);
  --status-success-text: oklch(0.3832 0.1265 255);
  --status-warning-bg: oklch(0.9554 0.0962 100);
  --status-warning-text: oklch(0.3792 0.079 100);
  --status-danger-bg: oklch(0.9594 0.0226 300);
  --status-danger-text: oklch(0.3989 0.1557 300);
  --status-info-bg: oklch(0.9492 0.0766 195);
  --status-info-text: oklch(0.3721 0.0636 195);
}
[data-token-system="flat-ui"][data-color="dark"][data-vision="protanopia"] {
  --status-success-bg: oklch(0.1597 0.0544 255);
  --status-success-text: oklch(0.878 0.0607 255);
  --status-warning-bg: oklch(0.1589 0.0342 100);
  --status-warning-text: oklch(0.8769 0.1234 100);
  --status-danger-bg: oklch(0.1709 0.0925 300);
  --status-danger-text: oklch(0.8839 0.0666 300);
  --status-info-bg: oklch(0.1542 0.0271 195);
  --status-info-text: oklch(0.8684 0.0944 195);
}

/* ── Vision — tritanopia (no blue) ──────────────────────────────────────────*/
[data-token-system="flat-ui"][data-vision="tritanopia"] {
  --accent-default: oklch(0.6768 0.1639 55);
  --status-info-bg: oklch(0.9594 0.0226 300);
  --status-info-text: oklch(0.3989 0.1557 300);
}
[data-token-system="flat-ui"][data-color="dark"][data-vision="tritanopia"] {
  --accent-default: oklch(0.7662 0.147 55);
  --status-info-bg: oklch(0.1709 0.0925 300);
  --status-info-text: oklch(0.8839 0.0666 300);
}

/* ── Toggle switch — flat/Simple treatment ───────────────────────────────*/
[data-token-system="flat-ui"] .toggle-slider {
  border-radius: var(--radius-soft);
  background-color: var(--surface-raised-background);
  outline: 1.5px solid var(--border-default);
  outline-offset: -1.5px;
}
[data-token-system="flat-ui"] .toggle-slider::before {
  border-radius: calc(var(--radius-soft) - 1px);
  background-color: var(--text-color-secondary);
  box-shadow: none;
}
[data-token-system="flat-ui"] input:checked + .toggle-slider {
  background-color: var(--accent-default);
  outline-color: var(--accent-default);
}
[data-token-system="flat-ui"] input:checked + .toggle-slider::before {
  background-color: oklch(1 0 0);
}
"""


def main():
    data = load()

    defaults: dict = {}
    walk(data.get("semantic", {}), ["semantic"], defaults)

    dark: dict = {}
    walk(data.get("semantic", {}), ["semantic"], dark, mode_key="dark")

    compact: dict = {}
    walk(data.get("semantic", {}), ["semantic"], compact, mode_key="compact")

    spacious: dict = {}
    walk(data.get("semantic", {}), ["semantic"], spacious, mode_key="spacious")

    lines = [
        "/* ================================================================",
        " * Flat UI theme — generated by experiments/flat-ui/resolver.py",
        " * DO NOT EDIT. Edit src/theme.tokens.json and re-run resolver.py.",
        " *",
        " * Scope: [data-token-system=\"flat-ui\"] on <body>.",
        " * White cards on off-white canvas. 1px borders = sole depth cue.",
        " * Radius: 4-6px (--radius-round = 0.375rem).",
        " * ================================================================ */",
        "",
    ]

    lines += emit_block('[data-token-system="flat-ui"]', defaults)
    lines.append("")

    if dark:
        lines += emit_block('[data-token-system="flat-ui"][data-color="dark"]', dark)
        lines.append("")

    if compact:
        lines += emit_block('[data-token-system="flat-ui"][data-density="compact"]', compact)
        lines.append("")

    if spacious:
        lines += emit_block('[data-token-system="flat-ui"][data-density="spacious"]', spacious)
        lines.append("")

    lines.append(COMPONENT_OVERRIDES)

    OUT.write_text("\n".join(lines), encoding="utf-8")
    print(f"✓  {OUT}")
    print(f"   {len(defaults)} default vars, {len(dark)} dark, {len(compact)} compact, {len(spacious)} spacious")
    print(f"   + component overrides block")


if __name__ == "__main__":
    main()
