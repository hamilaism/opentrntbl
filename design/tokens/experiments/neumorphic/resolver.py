#!/usr/bin/env python3
"""
Neumorphic theme resolver.

Reads src/theme.tokens.json and emits tokens.css with:
  1. Token vars scoped to [data-token-system="neumorphic"]
  2. Dark overrides: [data-token-system="neumorphic"][data-color="dark"]
  3. Density overrides: compact / spacious
  4. Component overrides: shadows applied to actual components to make the
     neumorphic effect visible (box-shadow, border resets, hover/active states)

CSS var naming mirrors V1 so components work without renaming:
  semantic.surface.canvas.background → --surface-canvas-background
  semantic.surface.raised.elevation  → --surface-raised-elevation
  semantic.elevation.raised          → --elevation-raised
  semantic.text.color.primary        → --text-color-primary
  semantic.status.success.bg         → --status-success-bg
  base.surface                       → --base-surface
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
 * Applies neumorphic shadow effect to existing component classes.
 * Raised elements get dual-shadow + thin border (the border sharpens the 3D
 * edge without being a strong visual cue). Sunken elements get inset shadow,
 * no border. Colored badges keep their bg — shadow is additive.
 * ── ─────────────────────────────────────────────────────────────────────── */

/* Body */
[data-token-system="neumorphic"] body {
  background: var(--surface-canvas-background);
}

/* Transitions — base components.css only animates background/opacity; neumorphic
 * effects live in box-shadow so we override transition to cover both. */
[data-token-system="neumorphic"] .btn-1,
[data-token-system="neumorphic"] .btn-2,
[data-token-system="neumorphic"] .btn-ghost,
[data-token-system="neumorphic"] .btn-toggle,
[data-token-system="neumorphic"] .btn-disconnect,
[data-token-system="neumorphic"] .btn-tonal,
[data-token-system="neumorphic"] .row {
  transition:
    box-shadow var(--motion-state-change-duration) var(--motion-state-change-easing),
    background var(--motion-feedback-duration) var(--motion-feedback-easing);
}

/* Card — raised + thin edge */
[data-token-system="neumorphic"] .card {
  background: var(--surface-canvas-background);
  box-shadow: var(--elevation-raised);
  border: 1px solid var(--border-subtle);
}

/* Row — no hover bg change (physical metaphor), active = micro inset */
[data-token-system="neumorphic"] .row:hover  {
  background: transparent;
}
[data-token-system="neumorphic"] .row:active {
  background: var(--surface-canvas-background);
  box-shadow: inset 1px 1px 2px var(--shadow-dark), inset -1px -1px 2px var(--shadow-light);
}

/* btn-1 (primary) — dark charcoal key. Hover = slight bg lightening (no shadow
 * change — physical buttons don't lift on proximity). Pressed = custom inset
 * with dark-adapted shadow colors (canvas-tone inset doesn't read on dark surface). */
[data-token-system="neumorphic"] .btn-1 {
  background: oklch(0.45 0.008 262);
  color: oklch(0.97 0 0);
  box-shadow: var(--elevation-raised);
  border: none;
}
[data-token-system="neumorphic"] .btn-1:hover {
  background: oklch(0.45 0.008 262);
  box-shadow: var(--elevation-raised);
  opacity: 1;
}
[data-token-system="neumorphic"] .btn-1:active {
  background: oklch(0.45 0.008 262);
  box-shadow: inset 4px 4px 5px oklch(0.32 0.010 262), inset -2px -2px 4px oklch(0.60 0.008 262);
  opacity: 1;
}
[data-token-system="neumorphic"] .btn-1:disabled {
  background: oklch(0.45 0.008 262);
  color: oklch(0.60 0 0);
  box-shadow: var(--elevation-raised);
  border: none;
  opacity: 0.5;
}

/* btn-2 — raised + thin border */
[data-token-system="neumorphic"] .btn-2 {
  box-shadow: var(--elevation-raised);
  border: 1px solid var(--border-subtle);
  background: var(--surface-canvas-background);
}
[data-token-system="neumorphic"] .btn-2:hover  {
  box-shadow: var(--elevation-raised);
  border-color: var(--border-subtle);
  background: var(--surface-canvas-background);
}
[data-token-system="neumorphic"] .btn-2:active {
  box-shadow: var(--elevation-pressed);
  border-color: var(--border-subtle);
  background: var(--surface-canvas-background);
}

/* btn-toggle — raised + thin border; active = pressed + accent border + tinted bg */
[data-token-system="neumorphic"] .btn-toggle {
  box-shadow: var(--elevation-raised);
  border: 1px solid var(--border-subtle);
  background: var(--surface-canvas-background);
  color: var(--text-color-secondary);
}
[data-token-system="neumorphic"] .btn-toggle:hover {
  box-shadow: var(--elevation-raised);
  border-color: var(--border-subtle);
  background: var(--surface-canvas-background);
}
[data-token-system="neumorphic"] .btn-toggle:active {
  box-shadow: var(--elevation-pressed);
  border-color: var(--border-subtle);
  background: var(--surface-canvas-background);
}
/* Active: pressed inset + accent border + accent text — no tint (avoids OKLCH hue shift) */
[data-token-system="neumorphic"] .btn-toggle.active {
  box-shadow: var(--elevation-pressed);
  border: 1px solid var(--accent-default);
  background: var(--surface-canvas-background);
  color: var(--accent-default);
}
[data-token-system="neumorphic"] .btn-toggle.active:hover {
  box-shadow: var(--elevation-pressed);
  border-color: var(--accent-default);
  background: var(--surface-canvas-background);
}
[data-token-system="neumorphic"] .btn-toggle.active:active {
  box-shadow: var(--elevation-pressed);
  background: var(--surface-canvas-background);
}

/* btn-disconnect — raised + thin border; hover gradient stays in danger hue */
[data-token-system="neumorphic"] .btn-disconnect {
  box-shadow: var(--elevation-raised);
  border: 1px solid var(--border-subtle);
}
[data-token-system="neumorphic"] .btn-disconnect:hover  {
  box-shadow: var(--elevation-raised);
  background: var(--status-danger-bg);
}
[data-token-system="neumorphic"] .btn-disconnect:active {
  box-shadow: var(--elevation-pressed);
  background: var(--status-danger-bg);
}

/* btn-tonal — gentle raised shadow + thin border */
[data-token-system="neumorphic"] .btn-tonal {
  box-shadow: var(--elevation-raised);
  border: 1px solid var(--border-subtle);
}
[data-token-system="neumorphic"] .btn-tonal:hover  {
  box-shadow: var(--elevation-raised);
  background: var(--surface-canvas-background);
}
[data-token-system="neumorphic"] .btn-tonal:active { box-shadow: var(--elevation-pressed); }

/* btn-ghost — very subtle raised shadow. Uses color-mix for alpha on CSS vars
 * so shadow colors adapt to dark mode (shadow-dark/light change in dark). */
[data-token-system="neumorphic"] .btn-ghost {
  background: var(--surface-canvas-background);
  box-shadow: 2px 2px 5px color-mix(in oklch, var(--shadow-dark) 60%, transparent),
              -1px -1px 4px color-mix(in oklch, var(--shadow-light) 80%, transparent);
  border: none;
}
[data-token-system="neumorphic"] .btn-ghost:hover {
  background: var(--surface-canvas-background);
  box-shadow: 2px 2px 5px color-mix(in oklch, var(--shadow-dark) 60%, transparent),
              -1px -1px 4px color-mix(in oklch, var(--shadow-light) 80%, transparent);
}
[data-token-system="neumorphic"] .btn-ghost:active {
  background: var(--surface-canvas-background);
  box-shadow: inset 2px 2px 4px color-mix(in oklch, var(--shadow-dark) 70%, transparent),
              inset -1px -1px 3px color-mix(in oklch, var(--shadow-light) 90%, transparent);
}

/* Input — sunken into surface */
[data-token-system="neumorphic"] .inp {
  box-shadow: var(--elevation-sunken);
  border-color: transparent;
  background: var(--surface-canvas-background);
}
[data-token-system="neumorphic"] .inp:hover:not(:focus):not(:disabled) {
  box-shadow: var(--elevation-sunken);
  border-color: transparent;
  background: var(--surface-canvas-background);
}
[data-token-system="neumorphic"] .inp:focus {
  box-shadow: var(--elevation-sunken), 0 0 0 3px color-mix(in oklch, var(--accent-default) 25%, transparent);
  border-color: transparent;
  background: var(--surface-canvas-background);
}

/* SegmentedControl — track sunken; active segment raised + thin border.
 * Asymmetric animation via CSS destination-state trick:
 * - transition on .seg-segment (no .active) = slow spring-return when losing active (320ms)
 * - transition on .seg-segment.active       = fast pop when gaining active (140ms)
 * Browser uses the destination-state transition, so: gain = 140ms, lose = 320ms. */
[data-token-system="neumorphic"] .seg-track {
  box-shadow: var(--elevation-sunken);
  border-color: transparent;
  background: var(--surface-canvas-background);
}
[data-token-system="neumorphic"] .seg-segment {
  transition:
    box-shadow var(--motion-component-exit-duration) var(--motion-component-exit-easing),
    background var(--motion-component-exit-duration) var(--motion-component-exit-easing);
}
[data-token-system="neumorphic"] .seg-segment.active {
  box-shadow: var(--elevation-raised);
  border: 1px solid var(--border-subtle);
  background: var(--surface-canvas-background);
  color: var(--text-color-primary);
  transition:
    box-shadow var(--motion-component-enter-duration) var(--motion-component-enter-easing),
    background var(--motion-component-enter-duration) var(--motion-component-enter-easing);
}
[data-token-system="neumorphic"] .seg-segment:hover:not(.active)  { background: transparent; }
[data-token-system="neumorphic"] .seg-segment:active:not(.active) { background: var(--surface-canvas-background); }

/* Alert — raised + thin border */
[data-token-system="neumorphic"] .alert {
  box-shadow: var(--elevation-raised);
  border: 1px solid var(--border-subtle);
  background: var(--surface-canvas-background);
}

/* card--status (informational) — sunken: relief = interactivity principle */
[data-token-system="neumorphic"] .card--status {
  box-shadow: var(--elevation-sunken);
  border: none;
  background: var(--surface-canvas-background);
}

/* Wifi bar — informational status pill, sunken (not interactive) */
[data-token-system="neumorphic"] .wifi-bar {
  box-shadow: var(--elevation-sunken);
  border: none;
  background: var(--surface-canvas-background);
}

/* dev-icon — raised circle + thin border */
[data-token-system="neumorphic"] .dev-icon {
  box-shadow: var(--elevation-raised);
  border: 1px solid var(--border-subtle);
  background: var(--surface-canvas-background);
}

/* Check (checkbox) — raised when unchecked (resting on surface), sunken + accent when checked.
 * Same physical metaphor as SegmentedControl: selection = physically pressed in.
 * Asymmetric animation: gaining .on = fast press (component-enter), losing = slow return (component-exit). */
[data-token-system="neumorphic"] .check {
  background: var(--surface-canvas-background);
  border: none;
  box-shadow: var(--elevation-raised);
  transition:
    box-shadow var(--motion-component-exit-duration) var(--motion-component-exit-easing),
    background var(--motion-component-exit-duration) var(--motion-component-exit-easing);
}
[data-token-system="neumorphic"] .check.on {
  background: var(--accent-default);
  border: none;
  box-shadow: inset 2px 2px 3px oklch(0.55 0.16 85), inset -1px -1px 2px oklch(0.88 0.10 85);
  transition:
    box-shadow var(--motion-component-enter-duration) var(--motion-component-enter-easing),
    background var(--motion-component-enter-duration) var(--motion-component-enter-easing);
}
[data-token-system="neumorphic"] .check.on::after {
  color: oklch(0.97 0 0);
  font-size: 13px;
}

/* Input action (Show/Hide) — mini raised pill inside the sunken field */
[data-token-system="neumorphic"] .inp-action {
  background: var(--surface-canvas-background);
  border: none;
  border-radius: 4px;
  padding: 3px 8px;
  color: var(--text-color-secondary);
  box-shadow: 1px 1px 3px color-mix(in oklch, var(--shadow-dark) 70%, transparent),
              -1px -1px 2px color-mix(in oklch, var(--shadow-light) 70%, transparent);
  transition:
    box-shadow var(--motion-state-change-duration) var(--motion-state-change-easing);
}
[data-token-system="neumorphic"] .inp-action:hover { color: var(--text-color-secondary); }
[data-token-system="neumorphic"] .inp-action:active {
  box-shadow: inset 1px 1px 2px color-mix(in oklch, var(--shadow-dark) 70%, transparent),
              inset -1px -1px 2px color-mix(in oklch, var(--shadow-light) 70%, transparent);
  color: var(--text-color-primary);
}

/* Status badge — sunken (embedded feel); keeps colored bg */
[data-token-system="neumorphic"] .status { box-shadow: var(--elevation-sunken); }

/* ── Dark mode adaptations ──────────────────────────────────────────────────
 * btn-1 dark: near-white on dark canvas — mirrors light-mode hierarchy.
 * Raised shadows calibrated on the CANVAS (0.25), not the button surface:
 * shadow-light=0.35 / shadow-dark=0.15 — same as the dark token pair.
 * Using button-surface values (0.97) would glow white against the 0.25 canvas.
 * Active inset shadows calibrated on the BUTTON surface (0.88) for depth.
 * btn-disconnect dark: danger-bg token is too dark (0.24/low chroma) —
 * override with a readable saturated red. */
[data-token-system="neumorphic"][data-color="dark"] .btn-1 {
  background: oklch(0.88 0 0);
  color: oklch(0.12 0 0);
  box-shadow: -4px -4px 8px oklch(0.35 0 0), 4px 4px 8px oklch(0.15 0 0);
  border: none;
}
[data-token-system="neumorphic"][data-color="dark"] .btn-1:hover {
  background: oklch(0.88 0 0);
  box-shadow: -4px -4px 8px oklch(0.35 0 0), 4px 4px 8px oklch(0.15 0 0);
  opacity: 1;
}
[data-token-system="neumorphic"][data-color="dark"] .btn-1:active {
  background: oklch(0.88 0 0);
  box-shadow: inset 4px 4px 5px oklch(0.70 0 0), inset -4px -4px 5px oklch(0.96 0 0);
  opacity: 1;
}
[data-token-system="neumorphic"][data-color="dark"] .btn-1:disabled {
  background: oklch(0.88 0 0);
  color: oklch(0.42 0 0);
  box-shadow: -4px -4px 8px oklch(0.35 0 0), 4px 4px 8px oklch(0.15 0 0);
  opacity: 0.5;
}

/* btn-disconnect dark — saturated red visible on dark canvas */
[data-token-system="neumorphic"][data-color="dark"] .btn-disconnect {
  background: oklch(0.42 0.20 25);
  color: oklch(0.97 0 0);
  box-shadow: var(--elevation-raised);
  border: none;
}
[data-token-system="neumorphic"][data-color="dark"] .btn-disconnect:hover {
  background: oklch(0.48 0.22 25);
  box-shadow: var(--elevation-raised);
}
[data-token-system="neumorphic"][data-color="dark"] .btn-disconnect:active {
  background: oklch(0.42 0.20 25);
  box-shadow: var(--elevation-pressed);
}

/* ── High contrast — light ───────────────────────────────────────────────────
 * Shadows calibrated to max-contrast pair (white light / dark-50 dark).
 * Elevation vars overridden so all components pick up HC shadows via var().
 * Borders become visible: neumorphic normally hides them (decorative-only). */
[data-token-system="neumorphic"][data-contrast="enhanced"] {
  --text-color-primary: oklch(0 0 0);
  --text-color-secondary: oklch(0.10 0.008 262);
  --text-color-placeholder: oklch(0.15 0.008 262);
  --text-color-disabled: oklch(0.22 0.008 262);
  --border-subtle: oklch(0.55 0.010 262);
  --border-default: oklch(0.40 0.010 262);
  --border-strong: oklch(0.15 0.010 262);
  --shadow-light: oklch(1 0 0);
  --shadow-dark: oklch(0.50 0.012 262);
  --elevation-flat: 0px 0px 0px 0px transparent;
  --elevation-raised: -4px -4px 10px oklch(1 0 0), 4px 4px 10px oklch(0.50 0.012 262);
  --elevation-raised-hover: -5px -5px 12px oklch(1 0 0), 5px 5px 12px oklch(0.50 0.012 262);
  --elevation-pressed: inset -3px -3px 5px oklch(1 0 0), inset 3px 3px 5px oklch(0.50 0.012 262);
  --elevation-sunken: inset -4px -4px 10px oklch(1 0 0), inset 4px 4px 10px oklch(0.50 0.012 262);
  --elevation-overlay: -8px -8px 22px oklch(1 0 0), 8px 8px 22px oklch(0.50 0.012 262);
  --surface-raised-elevation: -4px -4px 10px oklch(1 0 0), 4px 4px 10px oklch(0.50 0.012 262);
  --status-success-bg: oklch(0.37 0.1166 145);
  --status-success-text: oklch(0.9485 0.0916 145);
  --status-warning-bg: oklch(0.3881 0.0963 55);
  --status-warning-text: oklch(0.9602 0.0232 55);
  --status-danger-bg: oklch(0.3983 0.1557 29);
  --status-danger-text: oklch(0.9607 0.0195 29);
  --status-info-bg: oklch(0.3832 0.1265 255);
  --status-info-text: oklch(0.9584 0.0201 255);
}
/* HC: enforce visible boundaries on normally-borderless elements */
[data-token-system="neumorphic"][data-contrast="enhanced"] .card,
[data-token-system="neumorphic"][data-contrast="enhanced"] .card--status,
[data-token-system="neumorphic"][data-contrast="enhanced"] .wifi-bar { border: 1px solid var(--border-default); }
[data-token-system="neumorphic"][data-contrast="enhanced"] .btn,
[data-token-system="neumorphic"][data-contrast="enhanced"] .btn-2,
[data-token-system="neumorphic"][data-contrast="enhanced"] .btn-ghost,
[data-token-system="neumorphic"][data-contrast="enhanced"] .btn-toggle { border: 1px solid var(--border-default); }
[data-token-system="neumorphic"][data-contrast="enhanced"] .inp { border-color: var(--border-strong); }

/* ── High contrast — dark ────────────────────────────────────────────────────
 * Same approach as HC light: keep dark surfaces/shadows as-is, just make
 * borders visible and boost text to max. No shadow amplification. */
[data-token-system="neumorphic"][data-color="dark"][data-contrast="enhanced"] {
  --text-color-primary: oklch(1 0 0);
  --text-color-secondary: oklch(0.95 0 0);
  --text-color-placeholder: oklch(0.90 0 0);
  --text-color-disabled: oklch(0.78 0 0);
  --border-subtle: oklch(0.48 0.008 262);
  --border-default: oklch(0.65 0.008 262);
  --border-strong: oklch(0.85 0 0);
  --status-success-bg: oklch(0.7392 0.147 145);
  --status-success-text: oklch(0 0.0582 145);
  --status-warning-bg: oklch(0.7662 0.147 55);
  --status-warning-text: oklch(0 0.035 55);
  --status-danger-bg: oklch(0.7697 0.1363 29);
  --status-danger-text: oklch(0 0.0552 29);
  --status-info-bg: oklch(0.7555 0.1275 255);
  --status-info-text: oklch(0 0.0533 255);
}
/* Dark HC: btn-1 override gets a border too */
[data-token-system="neumorphic"][data-color="dark"][data-contrast="enhanced"] .btn-1 { border: 1px solid var(--border-default); }
[data-token-system="neumorphic"][data-color="dark"][data-contrast="enhanced"] .card,
[data-token-system="neumorphic"][data-color="dark"][data-contrast="enhanced"] .card--status,
[data-token-system="neumorphic"][data-color="dark"][data-contrast="enhanced"] .wifi-bar { border: 1px solid var(--border-default); }

/* ── Vision — achromatopsia (no color) ──────────────────────────────────────*/
[data-token-system="neumorphic"][data-vision="achromatopsia"] {
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
[data-token-system="neumorphic"][data-color="dark"][data-vision="achromatopsia"] {
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
[data-token-system="neumorphic"][data-vision="deuteranopia"] {
  --status-success-bg: oklch(0.9492 0.0766 195);
  --status-success-text: oklch(0.3721 0.0636 195);
  --status-warning-bg: oklch(0.9554 0.0962 100);
  --status-warning-text: oklch(0.3792 0.079 100);
  --status-danger-bg: oklch(0.9602 0.0232 55);
  --status-danger-text: oklch(0.3881 0.0963 55);
}
[data-token-system="neumorphic"][data-color="dark"][data-vision="deuteranopia"] {
  --status-success-bg: oklch(0.1542 0.0271 195);
  --status-success-text: oklch(0.8684 0.0944 195);
  --status-warning-bg: oklch(0.1589 0.0342 100);
  --status-warning-text: oklch(0.8769 0.1234 100);
  --status-danger-bg: oklch(0.1613 0.0413 55);
  --status-danger-text: oklch(0.885 0.0711 55);
}

/* ── Vision — protanopia (no red) ────────────────────────────────────────────*/
[data-token-system="neumorphic"][data-vision="protanopia"] {
  --status-success-bg: oklch(0.9584 0.0201 255);
  --status-success-text: oklch(0.3832 0.1265 255);
  --status-warning-bg: oklch(0.9554 0.0962 100);
  --status-warning-text: oklch(0.3792 0.079 100);
  --status-danger-bg: oklch(0.9594 0.0226 300);
  --status-danger-text: oklch(0.3989 0.1557 300);
  --status-info-bg: oklch(0.9492 0.0766 195);
  --status-info-text: oklch(0.3721 0.0636 195);
}
[data-token-system="neumorphic"][data-color="dark"][data-vision="protanopia"] {
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
[data-token-system="neumorphic"][data-vision="tritanopia"] {
  --accent-default: oklch(0.6768 0.1639 55);
  --status-info-bg: oklch(0.9594 0.0226 300);
  --status-info-text: oklch(0.3989 0.1557 300);
}
[data-token-system="neumorphic"][data-color="dark"][data-vision="tritanopia"] {
  --accent-default: oklch(0.7662 0.147 55);
  --status-info-bg: oklch(0.1709 0.0925 300);
  --status-info-text: oklch(0.8839 0.0666 300);
}

/* ── Toggle switch — neumorphic treatment ────────────────────────────────*/
[data-token-system="neumorphic"] .toggle-slider {
  background-color: var(--surface-canvas-background);
  box-shadow: inset 1px 1px 3px var(--shadow-dark), inset -1px -1px 3px var(--shadow-light);
}
[data-token-system="neumorphic"] .toggle-slider::before {
  width: 20px; height: 20px; left: 4px; bottom: 4px;
  box-shadow: 1px 1px 3px var(--shadow-dark), -1px -1px 3px var(--shadow-light);
}
[data-token-system="neumorphic"] input:checked + .toggle-slider {
  background-color: var(--accent-default);
  box-shadow: inset 1px 1px 3px oklch(0 0 0 / 0.2), inset -1px -1px 2px oklch(1 0 0 / 0.06);
}
[data-token-system="neumorphic"] input:checked + .toggle-slider::before {
  transform: translateX(22px);
}
"""


def main():
    data = load()

    defaults: dict = {}
    walk(data.get("base",     {}), ["base"],     defaults)
    walk(data.get("semantic", {}), ["semantic"], defaults)

    dark: dict = {}
    walk(data.get("base",     {}), ["base"],     dark, mode_key="dark")
    walk(data.get("semantic", {}), ["semantic"], dark, mode_key="dark")

    compact: dict = {}
    walk(data.get("semantic", {}), ["semantic"], compact, mode_key="compact")

    spacious: dict = {}
    walk(data.get("semantic", {}), ["semantic"], spacious, mode_key="spacious")

    lines = [
        "/* ================================================================",
        " * Neumorphic theme — generated by experiments/neumorphic/resolver.py",
        " * DO NOT EDIT. Edit src/theme.tokens.json and re-run resolver.py.",
        " *",
        " * Scope: [data-token-system=\"neumorphic\"] on <body>.",
        " * All surfaces are the same mono-surface color.",
        " * Depth = dual shadow only (light top-left, dark bottom-right).",
        " * ================================================================ */",
        "",
    ]

    lines += emit_block('[data-token-system="neumorphic"]', defaults)
    lines.append("")

    if dark:
        lines += emit_block('[data-token-system="neumorphic"][data-color="dark"]', dark)
        lines.append("")

    if compact:
        lines += emit_block('[data-token-system="neumorphic"][data-density="compact"]', compact)
        lines.append("")

    if spacious:
        lines += emit_block('[data-token-system="neumorphic"][data-density="spacious"]', spacious)
        lines.append("")

    lines.append(COMPONENT_OVERRIDES)

    OUT.write_text("\n".join(lines), encoding="utf-8")
    print(f"✓  {OUT}")
    print(f"   {len(defaults)} default vars, {len(dark)} dark, {len(compact)} compact, {len(spacious)} spacious")
    print(f"   + component overrides block")


if __name__ == "__main__":
    main()
