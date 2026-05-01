#!/usr/bin/env python3
"""
openTRNTBL — One-shot patch : ajoute des `$description` DTCG manquants aux
leaf tokens des 3 sources (core, primitives, semantic).

Priorité : les dimensions (criantes selon QA Vague 2). Étendu à toutes les
catégories où un token n'a pas encore de description :
  - core.dimension.*  (16 manquants)
  - core.opacity.*    (9 manquants)
  - core.font-size.*  (11 manquants)
  - primitives/openTRNTBL.color.*.* (66 manquants — alias 1:1 sur core.palette)
  - primitives/openTRNTBL.font-family.{sans,mono} (2 manquants)

Le contenu des descriptions explique l'**intuition d'usage** (quand utiliser
ce token plutôt qu'un autre proche), pas la valeur (déjà visible).

Idempotent : ré-exécuté, ne réécrit pas une description déjà présente.

Usage :
    python3 design/tokens/scripts/add_descriptions.py
"""

from __future__ import annotations

import json
from pathlib import Path


SRC_DIR = Path(__file__).resolve().parent.parent / "src"

CORE = SRC_DIR / "core.tokens.json"
PRIMITIVES = SRC_DIR / "primitives-openTRNTBL.tokens.json"


# ---------------------------------------------------------------------------
# core.dimension.* — usage intuition for every step
# ---------------------------------------------------------------------------
DIMENSION_DESC = {
    "01":  "Hairline. Sub-rem exception for 1px borders/dividers.",
    "05":  "2px. Fine border, micro-radius, focus-ring stroke.",
    "10":  "4px. Tightest gap (label↔input). Border-radius soft.",
    "15":  "6px. Compact density variant of `default`.",
    "20":  "8px. Snug gap. Inner padding of small controls.",
    "25":  "10px. Border-radius round (cards, panels). Compact-spacious knob.",
    "30":  "12px. Caption font-size. Compact `default` step.",
    "35":  "14px. Small body font-size. Compact-spacious knob.",
    "40":  "16px. One rem. Typography base; default body padding & gap.",
    "45":  "18px. Large body font-size.",
    "50":  "20px. Subheading font-size. Spacious `snug` variant.",
    "55":  "22px. Reserved for fine-grained tuning between 50 and 60.",
    "60":  "24px. Heading-3 font-size. Loose gap (compact).",
    "70":  "28px. Reserved tuning step between 60 and 80.",
    "80":  "32px. Heading-2 font-size. Loose gap (default).",
    "90":  "36px. Reserved tuning step between 80 and 100.",
    "100": "40px. Minimum tap target (WCAG AA 2.2). Heading-1 font-size.",
    "120": "48px. Spacious `loose` step. Display-small font-size.",
    "160": "64px. Display-large font-size.",
    "200": "80px. Major hero spacing.",
    "240": "96px. Pill radius (always larger than tallest pill control).",
    "320": "128px. Hero dimensions.",
}


# ---------------------------------------------------------------------------
# core.opacity.* — usage intuition
# ---------------------------------------------------------------------------
OPACITY_DESC = {
    "000": "0%. Fully transparent.",
    "004": "4%. Faintest tint — cell hover on dense surfaces.",
    "008": "8%. Subtle tint — `:hover` mix amount on filled buttons.",
    "016": "16%. Soft overlay — disabled-on-light reduction.",
    "024": "24%. Light scrim.",
    "040": "40%. Medium scrim — disabled control body.",
    "060": "60%. Standard backdrop scrim (modals, drawers).",
    "080": "80%. Strong dimming.",
    "100": "100%. Fully opaque (ergonomic shortcut).",
}


# ---------------------------------------------------------------------------
# core.font-size.* — usage intuition (aliases onto dimension)
# ---------------------------------------------------------------------------
FONT_SIZE_DESC = {
    "10":  "12px. Caption: metadata, legal text, table headers.",
    "20":  "14px. Small body: secondary copy, dense UI, inputs.",
    "30":  "16px. Default body: reading size.",
    "40":  "18px. Large body: emphasized paragraphs.",
    "50":  "20px. Subheading: in-page section labels.",
    "60":  "24px. Heading-3: within-section titles.",
    "80":  "32px. Heading-2: major-section titles.",
    "90":  "36px. Reserved tuning step.",
    "100": "40px. Heading-1: page titles.",
    "120": "48px. Display-small: hero subtitles.",
    "160": "64px. Display-large: hero titles.",
}


# ---------------------------------------------------------------------------
# primitives/openTRNTBL — color role meaning at brand level
# ---------------------------------------------------------------------------
ROLE_INTENT = {
    "accent":  "Brand accent (gold). Decorative emphasis, link color, binary on-state.",
    "neutral": "Neutral grayscale. Surfaces, borders, body text.",
    "success": "Positive feedback (green). Connection OK, action complete.",
    "warning": "Caution (orange). Non-blocking issues, recoverable problems.",
    "danger":  "Error / destructive (red). Blocking failures, irreversible actions.",
    "info":    "Informational notice (blue). Neutral context, hints.",
    # Brand-extension hues — exposed as primitives but not bound to a
    # default semantic role. Consumed via vision-mode overrides
    # (deuteranopia / protanopia / tritanopia) in semantic.tokens.json
    # to remap success / warning / danger / info to safe palettes.
    "cyan":    "Brand-extension hue (cyan). Used in vision-mode overrides for daltonism-safe success/info.",
    "yellow":  "Brand-extension hue (yellow). Used in vision-mode overrides for daltonism-safe warning.",
    "violet":  "Brand-extension hue (violet). Used in vision-mode overrides for daltonism-safe danger/info.",
}

# Per-shade purpose in the role ramp. Matches the contrast invariants
# enforced in core.palette (diff ≥ 100 ⇒ AA, ≥ 150 ⇒ AAA).
SHADE_PURPOSE = {
    "0":   "darkest extreme",
    "10":  "near-dark / OLED-safe deep",
    "25":  "deep — high-emphasis text on light",
    "50":  "strong — body text on light, solid idle on bright surfaces",
    "75":  "secondary text on light",
    "100": "mid-tone — borders, disabled fills",
    "125": "primary fill on dark surfaces",
    "150": "soft border, disabled text",
    "175": "near-light tint",
    "190": "tint — subtle background hue",
    "200": "lightest extreme",
}


# ---------------------------------------------------------------------------
# primitives/openTRNTBL.font-family.*
# ---------------------------------------------------------------------------
FONT_FAMILY_DESC = {
    "sans": "UI sans-serif stack (Inter first). Body, headings, controls.",
    "mono": "Monospace stack (SF Mono first). Code, stream URLs, technical output.",
}


# ---------------------------------------------------------------------------
# Patch helpers
# ---------------------------------------------------------------------------
def patch_leaf(node, desc):
    """Set $description if missing/empty. Returns True if patched."""
    if not isinstance(node, dict):
        return False
    if node.get("$description", "").strip():
        return False
    node["$description"] = desc
    return True


def patch_core(doc):
    n = 0
    core = doc["core"]
    for key, desc in DIMENSION_DESC.items():
        if key in core["dimension"] and patch_leaf(core["dimension"][key], desc):
            n += 1
    for key, desc in OPACITY_DESC.items():
        if key in core["opacity"] and patch_leaf(core["opacity"][key], desc):
            n += 1
    for key, desc in FONT_SIZE_DESC.items():
        if key in core["font-size"] and patch_leaf(core["font-size"][key], desc):
            n += 1
    return n


def patch_primitives(doc):
    n = 0
    body_key = next(k for k in doc if not k.startswith("$"))
    body = doc[body_key]
    color = body.get("color", {})
    for role, ramp in color.items():
        intent = ROLE_INTENT.get(role, "Brand color role.")
        for shade, leaf in ramp.items():
            purpose = SHADE_PURPOSE.get(shade, "")
            desc = f"{intent} Shade {shade} — {purpose}." if purpose else intent
            if patch_leaf(leaf, desc):
                n += 1
    fam = body.get("font-family", {})
    for name, leaf in fam.items():
        if name in FONT_FAMILY_DESC and patch_leaf(leaf, FONT_FAMILY_DESC[name]):
            n += 1
    return n


def main():
    core_doc = json.loads(CORE.read_text())
    n_core = patch_core(core_doc)
    if n_core:
        CORE.write_text(json.dumps(core_doc, indent=2) + "\n")
    print(f"core.tokens.json         : patched {n_core} descriptions")

    prim_doc = json.loads(PRIMITIVES.read_text())
    n_prim = patch_primitives(prim_doc)
    if n_prim:
        PRIMITIVES.write_text(json.dumps(prim_doc, indent=2) + "\n")
    print(f"primitives-openTRNTBL.tokens.json : patched {n_prim} descriptions")

    print()
    print(f"Total : {n_core + n_prim} descriptions added.")


if __name__ == "__main__":
    main()
