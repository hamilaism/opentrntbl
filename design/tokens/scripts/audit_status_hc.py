#!/usr/bin/env python3
"""
openTRNTBL — Vague 8.5 — Audit ciblé des status.*.bg en mode HC.

Mesure :
  1. ratio status.*.bg vs surface.canvas (UI distinguabilité, target >= 3.0)
  2. ratio status.*.text vs status.*.bg (texte AAA, target >= 7.0)

en HC light (contrast:enhanced) et HC dark (color:dark|contrast:enhanced),
en lisant directement le hex depuis core.tokens.json (pas d'OKLCH approx).

Usage :
    python3 design/tokens/scripts/audit_status_hc.py [--shade-light SHADE] [--shade-dark SHADE]

Avec un shade explicite, simule "et si on prenait shade=N pour status.*.bg
en HC ?" Permet d'itérer sur les overrides.
"""

from __future__ import annotations

import argparse
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent.parent.parent
CORE_FILE = ROOT / "design" / "tokens" / "src" / "core.tokens.json"
SEMANTIC_FILE = ROOT / "design" / "tokens" / "src" / "semantic.tokens.json"


# WCAG utilities ------------------------------------------------------------

def hex_to_rgb(h):
    h = h.lstrip("#")
    return tuple(int(h[i:i+2], 16) / 255 for i in (0, 2, 4))


def lin(c):
    return c / 12.92 if c <= 0.03928 else ((c + 0.055) / 1.055) ** 2.4


def rel_lum(hex_color):
    r, g, b = hex_to_rgb(hex_color)
    return 0.2126 * lin(r) + 0.7152 * lin(g) + 0.0722 * lin(b)


def contrast(h1, h2):
    l1, l2 = rel_lum(h1), rel_lum(h2)
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


# Palette loader ------------------------------------------------------------

def load_palette():
    return json.loads(CORE_FILE.read_text())["core"]["palette"]


def hx(palette, hue, shade):
    return palette[hue][str(shade)]["$value"]["hex"]


# Mapping status -> primitive hue (success/warning/danger/info utilisent leur
# hue dédiée comme primitive dans semantic.tokens.json) -------------------

STATUS_HUES = {
    "success": "green",
    "warning": "orange",
    "danger":  "red",
    "info":    "blue",
}

# Surface canvas en HC : light n.175, dark n.0
CANVAS_HC = {
    "light": ("neutral", 175),
    "dark":  ("neutral", 0),
}


# Audit core ----------------------------------------------------------------

def audit(palette, override_bg_shade_light=None, override_bg_shade_dark=None,
          override_text_shade_light=None, override_text_shade_dark=None):
    """Affiche les ratios HC pour chaque status.

    Sans override, les valeurs par défaut sont les actuelles "héritées" :
      light bg = hue.190 (héritée de mode color:light)
      light text = hue.25 (override existant contrast:enhanced)
      dark bg = hue.10 (héritée de mode color:dark)
      dark text = hue.190 (override existant color:dark|contrast:enhanced)
    """
    # Defaults reflètent l'état ACTUEL semantic.tokens.json
    bg_l = override_bg_shade_light if override_bg_shade_light is not None else 190
    bg_d = override_bg_shade_dark if override_bg_shade_dark is not None else 10
    tx_l = override_text_shade_light if override_text_shade_light is not None else 25
    tx_d = override_text_shade_dark if override_text_shade_dark is not None else 190

    canvas_l = hx(palette, *CANVAS_HC["light"])
    canvas_d = hx(palette, *CANVAS_HC["dark"])

    print(f"\n=== HC light : status.bg=hue.{bg_l} / status.text=hue.{tx_l} / canvas=neutral.175 ({canvas_l}) ===")
    print(f"  {'status':8s}  {'bg hex':9s}  {'tx hex':9s}  {'bg/canvas':>10s} {'g':5s}  {'text/bg':>8s} {'g':5s}")
    fail_count = 0
    for status, hue in STATUS_HUES.items():
        bg = hx(palette, hue, bg_l)
        tx = hx(palette, hue, tx_l)
        r_bg_canvas = contrast(bg, canvas_l)
        r_tx_bg = contrast(tx, bg)
        g1 = grade(r_bg_canvas)
        g2 = grade(r_tx_bg)
        flag = ""
        if r_bg_canvas < 3.0:
            flag += " BG<3"
            fail_count += 1
        if r_tx_bg < 7.0:
            flag += " TX<7"
            fail_count += 1
        print(f"  {status:8s}  {bg:9s}  {tx:9s}  {r_bg_canvas:10.2f} {g1:5s}  {r_tx_bg:8.2f} {g2:5s}{flag}")

    print(f"\n=== HC dark : status.bg=hue.{bg_d} / status.text=hue.{tx_d} / canvas=neutral.0 ({canvas_d}) ===")
    print(f"  {'status':8s}  {'bg hex':9s}  {'tx hex':9s}  {'bg/canvas':>10s} {'g':5s}  {'text/bg':>8s} {'g':5s}")
    for status, hue in STATUS_HUES.items():
        bg = hx(palette, hue, bg_d)
        tx = hx(palette, hue, tx_d)
        r_bg_canvas = contrast(bg, canvas_d)
        r_tx_bg = contrast(tx, bg)
        g1 = grade(r_bg_canvas)
        g2 = grade(r_tx_bg)
        flag = ""
        if r_bg_canvas < 3.0:
            flag += " BG<3"
            fail_count += 1
        if r_tx_bg < 7.0:
            flag += " TX<7"
            fail_count += 1
        print(f"  {status:8s}  {bg:9s}  {tx:9s}  {r_bg_canvas:10.2f} {g1:5s}  {r_tx_bg:8.2f} {g2:5s}{flag}")

    print(f"\n  → fail count : {fail_count}")
    return fail_count


def explore_shades(palette):
    """Pour chaque status, balaie les shades candidats pour bg et text et affiche
    le ratio bg/canvas et text/bg, pour aider à choisir.
    """
    canvas_l = hx(palette, *CANVAS_HC["light"])
    canvas_d = hx(palette, *CANVAS_HC["dark"])

    candidate_bg_light = [125, 150, 175, 190]   # plus saturé/foncé que 190
    candidate_bg_dark  = [10, 25, 50, 75]       # plus marqué que 10
    candidate_tx_light = [0, 25, 50]
    candidate_tx_dark  = [150, 175, 190, 200]

    for status, hue in STATUS_HUES.items():
        print(f"\n--- {status} ({hue}) ---")
        print(f"  HC light (canvas n.175 = {canvas_l})")
        print(f"  {'bg shade':>9s} {'bg hex':>9s} {'bg/canv':>8s}  | text shades vs bg :")
        for sb in candidate_bg_light:
            bg = hx(palette, hue, sb)
            r_bgc = contrast(bg, canvas_l)
            cells = []
            for st in candidate_tx_light:
                tx = hx(palette, hue, st)
                r = contrast(tx, bg)
                cells.append(f"  t.{st}={r:5.2f}{grade(r)[:2]}")
            print(f"  n.{sb:<7d} {bg:>9s} {r_bgc:8.2f}{grade(r_bgc)[:2]}  |{' '.join(cells)}")

        print(f"  HC dark (canvas n.0 = {canvas_d})")
        print(f"  {'bg shade':>9s} {'bg hex':>9s} {'bg/canv':>8s}  | text shades vs bg :")
        for sb in candidate_bg_dark:
            bg = hx(palette, hue, sb)
            r_bgc = contrast(bg, canvas_d)
            cells = []
            for st in candidate_tx_dark:
                tx = hx(palette, hue, st)
                r = contrast(tx, bg)
                cells.append(f"  t.{st}={r:5.2f}{grade(r)[:2]}")
            print(f"  n.{sb:<7d} {bg:>9s} {r_bgc:8.2f}{grade(r_bgc)[:2]}  |{' '.join(cells)}")


# CLI -----------------------------------------------------------------------

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--bg-light", type=int, default=None,
                        help="Override status.*.bg HC light shade (default actuel = 190)")
    parser.add_argument("--bg-dark", type=int, default=None,
                        help="Override status.*.bg HC dark shade (default actuel = 10)")
    parser.add_argument("--text-light", type=int, default=None,
                        help="Override status.*.text HC light shade (default actuel = 25)")
    parser.add_argument("--text-dark", type=int, default=None,
                        help="Override status.*.text HC dark shade (default actuel = 190)")
    parser.add_argument("--explore", action="store_true",
                        help="Affiche tous les couples bg/text candidats par status")
    parser.add_argument("--live", action="store_true",
                        help="Mesure les ratios sur tokens.css généré (cascade réelle)")
    args = parser.parse_args()

    palette = load_palette()

    if args.explore:
        explore_shades(palette)
        return

    if args.live:
        audit_live()
        return

    print("openTRNTBL — Vague 8.5 — Audit status.*.{bg,text} en HC")
    print("=" * 70)
    audit(palette,
          override_bg_shade_light=args.bg_light,
          override_bg_shade_dark=args.bg_dark,
          override_text_shade_light=args.text_light,
          override_text_shade_dark=args.text_dark)


def audit_live():
    """Lit le tokens.css réel généré et calcule les ratios effectifs après
    cascade des overrides — simule ce que les modes data-* produisent dans le
    Storybook réel.
    """
    import sys
    here = Path(__file__).resolve().parent
    sys.path.insert(0, str(here))
    from audit_components import parse_tokens_css, resolve_tokens, contrast_ratio_rgb, grade as grade_rgb

    blocks = parse_tokens_css()
    print("openTRNTBL — Vague 8.5 — Audit live (parsed from tokens.css)")
    print("=" * 70)

    def report(mode_label, mode):
        resolved = resolve_tokens(blocks, mode)
        canvas = resolved.get("--surface-canvas")
        if canvas is None:
            print(f"  [skip {mode_label}: canvas not found]")
            return 0
        print(f"\n=== {mode_label} ===")
        print(f"  {'token':22s} {'bg/canvas':>10s} {'g':5s} {'text/bg':>10s} {'g':5s}")
        fails = 0
        for s in ["success", "warning", "danger", "info"]:
            bg = resolved.get(f"--status-{s}-bg")
            tx = resolved.get(f"--status-{s}-text")
            if bg is None or tx is None:
                continue
            r1 = contrast_ratio_rgb(bg, canvas)
            r2 = contrast_ratio_rgb(tx, bg)
            g1, g2 = grade_rgb(r1), grade_rgb(r2)
            flag = ""
            if r1 < 3.0:
                flag += " BG<3"
                fails += 1
            if r2 < 7.0:
                flag += " TX<7"
                fails += 1
            print(f"  status.{s:14s}   {r1:10.2f} {g1:5s} {r2:10.2f} {g2:5s}{flag}")
        return fails

    total = 0
    total += report("HC light (default vision)",
                    {"color": "light", "contrast": "enhanced", "vision": "default", "density": "default"})
    total += report("HC dark (default vision)",
                    {"color": "dark", "contrast": "enhanced", "vision": "default", "density": "default"})
    total += report("Standard light (no contrast)",
                    {"color": "light", "contrast": "default", "vision": "default", "density": "default"})
    total += report("Standard dark (no contrast)",
                    {"color": "dark", "contrast": "default", "vision": "default", "density": "default"})

    print(f"\n  → live fail count : {total}")


if __name__ == "__main__":
    main()
