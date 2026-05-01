#!/usr/bin/env python3
"""
openTRNTBL — Primitives (Tier 1) generator.

Emits `design/tokens/src/primitives-openTRNTBL.tokens.json`, the
brand-level token set that selects raw material from `core` into
openTRNTBL's primitives:

  color.accent   -> core.palette.gold
  color.neutral  -> core.palette.neutral
  color.success  -> core.palette.green
  color.warning  -> core.palette.orange
  color.danger   -> core.palette.red
  color.info     -> core.palette.blue

Plus 3 brand-extension hues, exposées en primitive pour les modes
daltonisme (consommées par les overrides `vision:*` du semantic) :
  color.cyan     -> core.palette.cyan
  color.yellow   -> core.palette.yellow
  color.violet   -> core.palette.violet

Aliases are shade-by-shade passthrough (0..200). Role-specific shade picks
(`bg`, `solid`, `text`) belong to Tier 2 semantic, not here.

Plus font families:
  font-family.sans (Inter stack)
  font-family.mono (SF Mono stack)

To fork into a new brand, copy this file, rename, and edit
THEME_NAME / COLOR_ROLE_TO_HUE / FONT_FAMILIES.
"""

import json
from pathlib import Path


THEME_NAME = "openTRNTBL"

COLOR_ROLE_TO_HUE = {
    "accent":  "gold",
    "neutral": "neutral",
    "success": "green",
    "warning": "orange",
    "danger":  "red",
    "info":    "blue",
    # Brand-extension hues — exposed for vision-mode overrides (daltonism
    # safe palettes). Not bound to a semantic role at default; consumed
    # only via [data-vision="..."] overrides in semantic.tokens.json.
    "cyan":    "cyan",
    "yellow":  "yellow",
    "violet":  "violet",
}

# Roles that don't carry a semantic meaning at default (used only as raw
# palette in vision-mode overrides). Marked with scope=["brand"] + a
# different description vs the role-bound hues.
BRAND_EXTENSION_ROLES = {"cyan", "yellow", "violet"}

FONT_FAMILIES = {
    "sans": ["Inter", "-apple-system", "BlinkMacSystemFont", "Segoe UI", "sans-serif"],
    "mono": ["SF Mono", "Menlo", "monospace"],
}


SRC_DIR = Path(__file__).resolve().parent.parent / "src"
CORE_FILE = SRC_DIR / "core.tokens.json"
OUTPUT_FILE = SRC_DIR / f"primitives-{THEME_NAME}.tokens.json"


def load_shade_keys():
    """Read the shade keys from core palette — single source of truth."""
    doc = json.loads(CORE_FILE.read_text())
    neutral = doc["core"]["palette"]["neutral"]
    return sorted(neutral.keys(), key=lambda k: int(k))


def build_color_aliases(shade_keys):
    color = {}
    for role, hue in COLOR_ROLE_TO_HUE.items():
        color[role] = {
            shade: {
                "$type": "color",
                "$value": f"{{core.palette.{hue}.{shade}}}",
            }
            for shade in shade_keys
        }
    return color


def build_font_family():
    return {
        name: {"$type": "fontFamily", "$value": stack}
        for name, stack in FONT_FAMILIES.items()
    }


def main():
    if not CORE_FILE.exists():
        raise SystemExit(
            f"{CORE_FILE.relative_to(Path.cwd())} not found. "
            "Run generate-core.py first."
        )

    shade_keys = load_shade_keys()

    primitives = {
        "color":       build_color_aliases(shade_keys),
        "font-family": build_font_family(),
    }

    document = {
        "$schema": "https://www.designtokens.org/schemas/2025.10/format.json",
        f"primitives/{THEME_NAME}": primitives,
    }

    OUTPUT_FILE.write_text(json.dumps(document, indent=2) + "\n")

    size = OUTPUT_FILE.stat().st_size
    n_color = sum(len(role) for role in primitives["color"].values())
    n_font = len(primitives["font-family"])
    print(f"Wrote {OUTPUT_FILE.relative_to(Path.cwd())}  ({size:,} bytes)")
    print()
    print(f"Color aliases: {len(primitives['color'])} roles x {len(shade_keys)} shades = {n_color}")
    for role, hue in COLOR_ROLE_TO_HUE.items():
        print(f"  {role:8s} -> core.palette.{hue}")
    print(f"Font-family: {n_font} ({', '.join(FONT_FAMILIES.keys())})")


if __name__ == "__main__":
    main()
