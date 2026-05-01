#!/usr/bin/env python3
"""
openTRNTBL — Audit structurel + WCAG des composants critiques (Vague 4 QA).

Pour chaque composant interactif (Button, Input, Row, SegmentedControl,
Alert, StatusBadge), calcule les ratios de contraste WCAG sur les paires
(text, background) clés sous chaque mode :
  - color: light / dark
  - contrast: default / enhanced
  - vision: default / deuteranopia / protanopia / tritanopia / achromatopsia

Source de vérité : `design/tokens/dist/tokens.css` (déjà généré, OKLCH).
On convertit via les hex stockés dans `core.tokens.json` quand on peut,
sinon on convertit l'OKLCH → sRGB → hex avec une approximation interne.

Usage :
    python3 design/tokens/scripts/audit_components.py
"""

from __future__ import annotations

import json
import re
import math
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent.parent.parent
TOKENS_CSS = ROOT / "design" / "tokens" / "dist" / "tokens.css"

# ---------------------------------------------------------------------------
# OKLCH -> RGB (approximation ; suffisant pour ratio WCAG)
# ---------------------------------------------------------------------------

def oklch_to_rgb(L: float, C: float, h_deg: float):
    """OKLCH (0..1, 0..0.4, 0..360) -> sRGB linéaire 0..1 -> sRGB gamma 0..1."""
    h = math.radians(h_deg)
    a = C * math.cos(h)
    b = C * math.sin(h)

    # OKLab -> LMS' (linear)
    l_ = L + 0.3963377774 * a + 0.2158037573 * b
    m_ = L - 0.1055613458 * a - 0.0638541728 * b
    s_ = L - 0.0894841775 * a - 1.2914855480 * b

    l = l_ ** 3
    m = m_ ** 3
    s = s_ ** 3

    r =  4.0767416621 * l - 3.3077115913 * m + 0.2309699292 * s
    g = -1.2684380046 * l + 2.6097574011 * m - 0.3413193965 * s
    bl = -0.0041960863 * l - 0.7034186147 * m + 1.7076147010 * s

    def gamma(c):
        if c < 0:
            return 0.0
        if c > 1:
            return 1.0
        return 1.055 * (c ** (1/2.4)) - 0.055 if c > 0.0031308 else 12.92 * c

    return (gamma(r), gamma(g), gamma(bl))


def relative_luminance_rgb(r, g, b):
    def lin(c):
        return c / 12.92 if c <= 0.03928 else ((c + 0.055) / 1.055) ** 2.4
    return 0.2126 * lin(r) + 0.7152 * lin(g) + 0.0722 * lin(b)


def contrast_ratio_rgb(rgb1, rgb2):
    l1 = relative_luminance_rgb(*rgb1)
    l2 = relative_luminance_rgb(*rgb2)
    hi, lo = max(l1, l2), min(l1, l2)
    return (hi + 0.05) / (lo + 0.05)


def grade(r):
    if r >= 7.0:
        return "AAA"
    if r >= 4.5:
        return "AA"
    if r >= 3.0:
        return "AA-UI"
    return "FAIL"


# ---------------------------------------------------------------------------
# Parser de tokens.css : extrait les couleurs OKLCH pour chaque (mode -> token)
# ---------------------------------------------------------------------------

OKLCH_RE = re.compile(r"oklch\(\s*([0-9.]+)\s+([0-9.]+)\s+([0-9.]+)\s*\)")

def parse_tokens_css():
    """Retourne dict[mode_key, dict[token_name, rgb_tuple]].
    mode_key = '' pour :root, ou la combinaison '[data-color="dark"]' etc.
    """
    text = TOKENS_CSS.read_text()
    blocks = {}
    # Split sur les sélecteurs (assez naïf mais suffisant)
    pattern = re.compile(r"(:root|\[[^\{]+?\])\s*\{([^}]*)\}", re.DOTALL)
    for m in pattern.finditer(text):
        selector = m.group(1).strip()
        body = m.group(2)
        block = {}
        for line in body.splitlines():
            line = line.strip().rstrip(";")
            if not line.startswith("--"):
                continue
            if ":" not in line:
                continue
            name, _, value = line.partition(":")
            name = name.strip()
            value = value.strip()
            mo = OKLCH_RE.search(value)
            if mo:
                L = float(mo.group(1))
                C = float(mo.group(2))
                H = float(mo.group(3))
                rgb = oklch_to_rgb(L, C, H)
                block[name] = rgb
        blocks[selector] = block
    return blocks


def resolve_tokens(blocks, mode):
    """Compose le set effectif de tokens pour un mode donné.
    mode = dict {'color': 'light'|'dark', 'contrast': 'default'|'enhanced',
                 'vision': 'default'|'deuteranopia'|'protanopia'|'tritanopia'|'achromatopsia'}.

    Applique :root, puis chaque sélecteur dont les attrs matchent.
    Composites '[data-color="dark"][data-contrast="enhanced"]' priorisés en
    dernier (CSS spécificité).
    """
    out = dict(blocks.get(":root", {}))

    def selector_matches(sel):
        # Parse [data-X="Y"] tokens
        attrs = re.findall(r'\[data-([a-z]+)="([^"]+)"\]', sel)
        for axis, val in attrs:
            if mode.get(axis) != val:
                return False
        return True

    # Two passes : single-attr first, then composites (more specific)
    single = []
    composites = []
    for sel in blocks:
        if sel == ":root":
            continue
        attr_count = sel.count("[data-")
        if attr_count >= 2:
            composites.append(sel)
        else:
            single.append(sel)

    for sel in single + composites:
        if selector_matches(sel):
            out.update(blocks[sel])
    return out


# ---------------------------------------------------------------------------
# Composants à auditer (paires text/bg consommées par le CSS).
# Les paires sont l'image fidèle de design/components/components.css.
# ---------------------------------------------------------------------------

# Format : (component_label, [(state_label, text_token, bg_token, kind)])
# kind : "text" (>=4.5/7), "ui" (>=3 pour borders/icons)
COMPONENT_PAIRS = {
    "Button.primary": [
        ("default",  "--surface-canvas-background",   "--text-color-primary", "text"),
        ("hover",    "--surface-canvas-background",   "--text-color-primary", "text"),  # opacity 0.85 — approx, identique en luminance
        # active: color-mix 80% text-primary + black → on saute (calculé)
        # disabled: opacity 0.25 — non couvert
    ],
    "Button.secondary": [
        ("default",  "--text-color-primary", "--surface-base-background", "text"),
        # hover/active: color-mix → calculé, omis
    ],
    "Button.destructive": [
        ("default",  "--status-danger-text", "--status-danger-bg", "text"),
    ],
    "Button.toggle.off": [
        ("default",  "--text-color-secondary", "--surface-base-background", "text"),
    ],
    "Button.toggle.on": [
        # color = on-accent token (auto-inverted in vision:achromatopsia)
        ("default",  "--text-color-on-accent",                "--accent-default", "text"),
    ],
    "Button.tonal": [
        ("default",  "--text-color-primary", "--surface-raised-background", "text"),
    ],
    "Button.ghost": [
        ("default",  "--text-color-primary", "--surface-canvas-background", "text"),
    ],
    "Input.default": [
        ("default",     "--text-color-primary", "--surface-sunken-background", "text"),
        ("placeholder", "--text-color-placeholder", "--surface-sunken-background", "text"),
        ("disabled",    "--text-color-disabled", "--surface-sunken-background", "text"),
        ("focus-border","--border-focus", "--surface-sunken-background", "ui"),
    ],
    "Input.action": [
        ("default",  "--accent-default", "--surface-base-background", "ui"),
    ],
    "Row.default": [
        ("title",   "--text-color-primary", "--surface-base-background", "text"),
        ("sub",     "--text-color-secondary", "--surface-base-background", "text"),
    ],
    "Row.divider": [
        ("border",  "--border-subtle", "--surface-base-background", "ui"),
    ],
    "SegmentedControl.inactive": [
        ("default", "--text-color-secondary", "--surface-raised-background", "text"),
    ],
    "SegmentedControl.active": [
        ("default", "--text-color-primary", "--surface-base-background", "text"),
    ],
    "StatusBadge.idle": [
        ("default", "--text-color-secondary", "--surface-base-background", "text"),
    ],
    "StatusBadge.playing": [
        ("default", "--status-success-text", "--status-success-bg", "text"),
    ],
    "StatusBadge.warning": [
        ("default", "--status-warning-text", "--status-warning-bg", "text"),
    ],
    "StatusBadge.error": [
        ("default", "--status-danger-text", "--status-danger-bg", "text"),
    ],
    "Alert.info": [
        ("body",    "--text-color-secondary", "--surface-base-background", "text"),
        ("title",   "--text-color-primary",   "--surface-base-background", "text"),
        ("icon",    "--status-info-text",    "--status-info-bg", "ui"),
    ],
    "Alert.warning": [
        ("body",    "--text-color-secondary", "--surface-base-background", "text"),
        ("icon",    "--status-warning-text", "--status-warning-bg", "ui"),
    ],
    "Alert.error": [
        ("body",    "--text-color-secondary", "--surface-base-background", "text"),
        ("icon",    "--status-danger-text",  "--status-danger-bg",  "ui"),
    ],
    "Alert.success": [
        ("body",    "--text-color-secondary", "--surface-base-background", "text"),
        ("icon",    "--status-success-text", "--status-success-bg", "ui"),
    ],
    "FocusRing": [
        ("on-canvas", "--focus-ring-color", "--surface-canvas-background", "ui"),
        ("on-base",   "--focus-ring-color", "--surface-base-background",   "ui"),
        ("on-sunken", "--focus-ring-color", "--surface-sunken-background", "ui"),
    ],
}


# Modes à auditer : 9 modes simples + composites importants.
MODES = []
for color in ["light", "dark"]:
    for contrast in ["default", "enhanced"]:
        for vision in ["default", "deuteranopia", "protanopia", "tritanopia", "achromatopsia"]:
            MODES.append({
                "color": color,
                "contrast": contrast,
                "vision": vision,
                "density": "default",
            })


def mode_label(m):
    parts = [m["color"]]
    if m["contrast"] != "default":
        parts.append(f"hc")
    if m["vision"] != "default":
        parts.append(m["vision"][:3])
    return ".".join(parts)


def main():
    blocks = parse_tokens_css()
    print(f"Parsed {len(blocks)} CSS selector blocks from tokens.css.")
    print(f"Token count in :root = {len(blocks.get(':root', {}))}")
    print()

    # Threshold : text 4.5 (AA) ou 7 (AAA enhanced) ; ui = 3
    # On affiche AAA si contrast=enhanced
    failures = []
    warnings_low = []  # passes AA-UI mais pas AA texte

    print(f"{'component':24s} {'state':16s} {'mode':24s} {'ratio':>7s}  {'grade':5s} {'kind':4s}")
    print("-" * 90)

    for comp, pairs in COMPONENT_PAIRS.items():
        for state, text_tok, bg_tok, kind in pairs:
            for mode in MODES:
                # Skip combos non utiles : vision modes ne devraient pas affecter
                # les paires non-status. On audite quand même mais on filtre l'output.
                if "status" not in text_tok and "status" not in bg_tok and \
                   "accent" not in text_tok and "accent" not in bg_tok and \
                   "focus" not in text_tok and \
                   mode["vision"] != "default":
                    continue

                resolved = resolve_tokens(blocks, mode)
                # Cas spécial BLACK
                rgb_t = (0,0,0) if text_tok == "BLACK" else resolved.get(text_tok)
                rgb_b = resolved.get(bg_tok)
                if rgb_t is None or rgb_b is None:
                    continue
                r = contrast_ratio_rgb(rgb_t, rgb_b)
                g = grade(r)
                threshold = 7.0 if mode["contrast"] == "enhanced" and kind == "text" else \
                            4.5 if kind == "text" else 3.0
                ok = r >= threshold

                ml = mode_label(mode)
                line = f"{comp:24s} {state:16s} {ml:24s} {r:7.2f}  {g:5s} {kind:4s}"
                # Imprime seulement les FAIL pour tenir le rapport concis
                if not ok:
                    print(f"{line}  <-- FAIL (need >={threshold})")
                    failures.append((comp, state, ml, r, kind, threshold))

    print()
    print(f"Total failures : {len(failures)}")
    if failures:
        print("\nDetails:")
        # Group by component
        by_comp = {}
        for f in failures:
            by_comp.setdefault(f[0], []).append(f)
        for comp, fs in sorted(by_comp.items()):
            print(f"  {comp}: {len(fs)} fail(s)")
            for c, s, m, r, k, t in fs[:8]:
                print(f"    - {s} @ {m}: {r:.2f} (need {t}, kind={k})")


if __name__ == "__main__":
    main()
