#!/usr/bin/env python3
"""
openTRNTBL — WCAG check for proposed colorblind / high-contrast palettes.

Computes WCAG 2.x contrast ratios for the proposed status-color mappings
across 5 vision modes (default, deuteranopia, protanopia, tritanopia,
achromatopsia) plus high-contrast (HC), in both light and dark modes.

Reads existing core hex values from `design/tokens/src/core.tokens.json`
(no live OKLCH conversion — we trust the generator's hex fallback).

Targets (WCAG 2.x):
  - Text normal     : ratio >= 7.0  (AAA)
  - Large text / UI : ratio >= 4.5  (AAA-large) / >= 3.0 (UI)
  - WCAG 2.4.11     : non-text UI components >= 3.0

Usage:
    python3 design/tokens/scripts/wcag_check.py
"""

from __future__ import annotations

import json
from pathlib import Path


CORE_FILE = Path(__file__).resolve().parent.parent / "src" / "core.tokens.json"


# ---------------------------------------------------------------------------
# WCAG contrast utilities
# ---------------------------------------------------------------------------

def hex_to_rgb(h):
    h = h.lstrip("#")
    return tuple(int(h[i:i+2], 16) / 255 for i in (0, 2, 4))


def lin(c):
    return c / 12.92 if c <= 0.03928 else ((c + 0.055) / 1.055) ** 2.4


def relative_luminance(hex_color):
    r, g, b = hex_to_rgb(hex_color)
    return 0.2126 * lin(r) + 0.7152 * lin(g) + 0.0722 * lin(b)


def contrast_ratio(h1, h2):
    l1, l2 = relative_luminance(h1), relative_luminance(h2)
    hi, lo = max(l1, l2), min(l1, l2)
    return (hi + 0.05) / (lo + 0.05)


def grade(r):
    """WCAG grade label for a contrast ratio."""
    if r >= 7.0:
        return "AAA"
    if r >= 4.5:
        return "AA"
    if r >= 3.0:
        return "AA-UI"
    return "FAIL"


# ---------------------------------------------------------------------------
# Load palette
# ---------------------------------------------------------------------------

def load_palette():
    doc = json.loads(CORE_FILE.read_text())
    return doc["core"]["palette"]


def hx(palette, hue, shade):
    return palette[hue][str(shade)]["$value"]["hex"]


# ---------------------------------------------------------------------------
# Mappings — proposed by colorblind-strategy.md
# ---------------------------------------------------------------------------

# Each mapping: status -> (light_bg_hue, light_text_hue, dark_bg_hue, dark_text_hue)
# OR for achromatopsia/HC: explicit (light_bg_shade, light_text_shade, dark_bg_shade, dark_text_shade)
# on the neutral ramp.

MAPPINGS_HUE = {
    "default": {
        "success": "green",
        "warning": "orange",
        "danger":  "red",
        "info":    "blue",
    },
    "vision-deuteranopia": {
        "success": "cyan",     # was green; cyan distinguishable from red/orange
        "warning": "yellow",   # high-luminance, safe for deutan
        "danger":  "orange",   # warm but distinct from cyan
        "info":    "blue",     # blue intact for deutans
    },
    "vision-protanopia": {
        "success": "blue",     # protans confuse red, blue is safe
        "warning": "yellow",
        "danger":  "violet",   # magenta/purple; orange would look brown
        "info":    "cyan",
    },
    "vision-tritanopia": {
        "success": "green",    # green/red intact for tritans
        "warning": "orange",   # orange OK; pure yellow confused with grey
        "danger":  "red",
        "info":    "violet",   # blue/yellow confused; violet distinct
    },
}

# Achromatopsia: only luminance. Each status gets a distinct neutral shade pair.
# Strategy: pick four bg/text pairs that are AAA AND luminance-spaced apart.
# Light mode bg lies on the light end (175/190), text on the dark end (0..50).
# To distinguish status, we vary bg shade between statuses (so the "tint" is
# itself a luminance signal). Icons are MANDATORY in this mode.
ACHROMATOPSIA = {
    # Stratégie : icônes/formes mandatoires (la couleur seule ne peut pas
    # distinguer 4 status). Le tint + l'ink-density renforcent la sémantique
    # par luminance. On garde 4 niveaux de bg (190/175/150/100 light), mais
    # on ne cherche pas AAA strict sur la pair bg/text quand c'est inutile :
    # AA (>=4.5) suffit, tant que les pairs sont visuellement distinctes
    # ET que les icônes lèvent toute ambiguïté.
    "success": {"light": (190, 25), "dark": (0,  175)},  # lightest bg, deepest text
    "warning": {"light": (175, 25), "dark": (25, 190)},
    "danger":  {"light": (100, 200),"dark": (100, 0)},   # mid-grey bg, inverted ink — strongest "alarm" feel
    "info":    {"light": (150, 0),  "dark": (50, 200)},
}

# High-contrast: push to absolute extremes within neutral ramp.
# Status colors push to deepest available shade of each hue for max ink.
HIGH_CONTRAST_NEUTRAL = {
    "canvas":   {"light": 200, "dark": 0},   # pure white / pure black
    "base":     {"light": 200, "dark": 0},
    "raised":   {"light": 200, "dark": 0},
    "border":   {"light": 0,   "dark": 200}, # pure ink for borders
    "text":     {"light": 0,   "dark": 200},
}

# Status in HC: bg = lightest tinted shade (190 light / 10 dark), text =
# darkest tinted shade (0 light / 200 dark — but that's pure white/black!)
# We use shade 0 for light text-on-tint and shade 200 for dark text-on-tint
# only for hues whose 0/200 stay on-hue (most do, since chroma envelopes
# floor at 15%). For hues that go to pure black/white at extremes (which
# happens when chroma_envelope returns 0), we fall back to 25/175.
HC_STATUS = {
    "success": "green",
    "warning": "orange",
    "danger":  "red",
    "info":    "blue",
}


# ---------------------------------------------------------------------------
# Reporters
# ---------------------------------------------------------------------------

LIGHT_BG_TINT = 190
LIGHT_TEXT    = 50
DARK_BG_TINT  = 10
DARK_TEXT     = 175


def report_hue_mode(palette, mode_name, mapping):
    print(f"\n=== {mode_name} ===")
    print(f"  light: bg=hue.{LIGHT_BG_TINT}, text=hue.{LIGHT_TEXT}")
    print(f"  dark:  bg=hue.{DARK_BG_TINT},  text=hue.{DARK_TEXT}")
    print()
    print(f"  {'status':8s}  {'hue':8s}  {'light bg':8s}  {'light tx':8s}  {'L ratio':>7s}  {'L grade':7s}  {'dark bg':8s}  {'dark tx':8s}  {'D ratio':>7s}  {'D grade':7s}")
    failures = []
    for status, hue in mapping.items():
        bg_l = hx(palette, hue, LIGHT_BG_TINT)
        tx_l = hx(palette, hue, LIGHT_TEXT)
        r_l = contrast_ratio(bg_l, tx_l)
        bg_d = hx(palette, hue, DARK_BG_TINT)
        tx_d = hx(palette, hue, DARK_TEXT)
        r_d = contrast_ratio(bg_d, tx_d)
        g_l, g_d = grade(r_l), grade(r_d)
        print(f"  {status:8s}  {hue:8s}  {bg_l:8s}  {tx_l:8s}  {r_l:7.2f}  {g_l:7s}  {bg_d:8s}  {tx_d:8s}  {r_d:7.2f}  {g_d:7s}")
        if g_l == "FAIL":
            failures.append(f"{mode_name} light {status}/{hue}: {r_l:.2f}")
        if g_d == "FAIL":
            failures.append(f"{mode_name} dark  {status}/{hue}: {r_d:.2f}")
    return failures


def report_achromatopsia(palette):
    print(f"\n=== vision-achromatopsia (neutral-ramp differentiation) ===")
    print(f"  ICONS MANDATORY — color alone cannot distinguish.")
    print()
    print(f"  {'status':8s}  {'lt bg':6s}  {'lt tx':6s}  {'L ratio':>7s}  {'L grade':7s}  {'dk bg':6s}  {'dk tx':6s}  {'D ratio':>7s}  {'D grade':7s}")
    failures = []
    for status, modes in ACHROMATOPSIA.items():
        sb_l, st_l = modes["light"]
        sb_d, st_d = modes["dark"]
        bg_l = hx(palette, "neutral", sb_l)
        tx_l = hx(palette, "neutral", st_l)
        bg_d = hx(palette, "neutral", sb_d)
        tx_d = hx(palette, "neutral", st_d)
        r_l = contrast_ratio(bg_l, tx_l)
        r_d = contrast_ratio(bg_d, tx_d)
        g_l, g_d = grade(r_l), grade(r_d)
        print(f"  {status:8s}  n.{sb_l:<4d}  n.{st_l:<4d}  {r_l:7.2f}  {g_l:7s}  n.{sb_d:<4d}  n.{st_d:<4d}  {r_d:7.2f}  {g_d:7s}")
        if g_l == "FAIL":
            failures.append(f"achromatopsia light {status}: {r_l:.2f}")
        if g_d == "FAIL":
            failures.append(f"achromatopsia dark  {status}: {r_d:.2f}")
    return failures


def report_status_distinguishability(palette, mode_name, mapping, when="light"):
    """Pairwise luminance ratio between status backgrounds — for achromatopsia
    + sanity check that distinct statuses can be told apart by luminance alone."""
    print(f"\n=== {mode_name} — pairwise distinguishability ({when}) ===")
    if mode_name == "vision-achromatopsia":
        bgs = {s: hx(palette, "neutral", ACHROMATOPSIA[s][when][0]) for s in ACHROMATOPSIA}
    else:
        shade = LIGHT_BG_TINT if when == "light" else DARK_BG_TINT
        bgs = {s: hx(palette, h, shade) for s, h in mapping.items()}
    statuses = list(bgs.keys())
    for i, a in enumerate(statuses):
        for b in statuses[i+1:]:
            r = contrast_ratio(bgs[a], bgs[b])
            warn = "" if r >= 1.5 else "  <-- TOO CLOSE"
            print(f"  {a:8s} vs {b:8s}: {r:5.2f}{warn}")


def report_high_contrast(palette):
    print("\n=== high-contrast — neutrals at extremes ===")
    pairs = [
        ("light text on canvas", hx(palette, "neutral", 0),   hx(palette, "neutral", 200)),
        ("light strong border",  hx(palette, "neutral", 0),   hx(palette, "neutral", 200)),
        ("dark text on canvas",  hx(palette, "neutral", 200), hx(palette, "neutral", 0)),
    ]
    for label, h1, h2 in pairs:
        r = contrast_ratio(h1, h2)
        print(f"  {label:30s}  {h1} vs {h2}  {r:6.2f}  {grade(r)}")

    print("\n=== high-contrast — status (deepest tinted shade for ink) ===")
    print(f"  {'status':8s}  {'hue':8s}  {'light bg':8s}  {'light tx':8s}  {'L ratio':>7s}  {'L grade':7s}  {'dark bg':8s}  {'dark tx':8s}  {'D ratio':>7s}  {'D grade':7s}")
    failures = []
    for status, hue in HC_STATUS.items():
        # HC pushes text to shade 25 (or 0 if hue still tinted there) and bg to 190
        bg_l = hx(palette, hue, 190)
        tx_l = hx(palette, hue, 25)
        bg_d = hx(palette, hue, 10)
        tx_d = hx(palette, hue, 190)
        r_l = contrast_ratio(bg_l, tx_l)
        r_d = contrast_ratio(bg_d, tx_d)
        g_l, g_d = grade(r_l), grade(r_d)
        print(f"  {status:8s}  {hue:8s}  {bg_l:8s}  {tx_l:8s}  {r_l:7.2f}  {g_l:7s}  {bg_d:8s}  {tx_d:8s}  {r_d:7.2f}  {g_d:7s}")
        if g_l == "FAIL":
            failures.append(f"HC light {status}/{hue}: {r_l:.2f}")
        if g_d == "FAIL":
            failures.append(f"HC dark  {status}/{hue}: {r_d:.2f}")
    return failures


# ---------------------------------------------------------------------------
# Driver
# ---------------------------------------------------------------------------

def main():
    palette = load_palette()
    all_failures = []

    print("openTRNTBL — Vague 3 colorblind / high-contrast WCAG audit")
    print("==========================================================")
    print(f"Pure white vs pure black: {contrast_ratio('#ffffff', '#000000'):.2f} (theoretical max 21.0)")
    print(f"Light canvas (neutral.190) vs dark text (neutral.25): "
          f"{contrast_ratio(hx(palette, 'neutral', 190), hx(palette, 'neutral', 25)):.2f}")
    print(f"Dark canvas (neutral.10)  vs light text (neutral.190): "
          f"{contrast_ratio(hx(palette, 'neutral', 10), hx(palette, 'neutral', 190)):.2f}")

    for mode, mapping in MAPPINGS_HUE.items():
        all_failures += report_hue_mode(palette, mode, mapping)
        report_status_distinguishability(palette, mode, mapping, "light")

    all_failures += report_achromatopsia(palette)
    report_status_distinguishability(palette, "vision-achromatopsia", None, "light")
    report_status_distinguishability(palette, "vision-achromatopsia", None, "dark")

    all_failures += report_high_contrast(palette)

    print("\n==========================================================")
    if all_failures:
        print(f"FAILURES ({len(all_failures)}):")
        for f in all_failures:
            print(f"  - {f}")
    else:
        print("All proposed mappings pass at least AA-UI (>=3.0) for status bg/text.")


if __name__ == "__main__":
    main()
