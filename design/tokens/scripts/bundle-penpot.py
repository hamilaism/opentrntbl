#!/usr/bin/env python3
"""
openTRNTBL — Penpot/Tokens Studio bundle generator.

Reads design/tokens/src/*.tokens.json (the same source files as bundle.py)
and produces design/tokens/dist/tokens.penpot.json with the multi-set /
multi-theme architecture that Tokens Studio in Penpot can switch through
visually.

The source uses $extensions.com.opntrntbl.modes for mode overrides.
Tokens Studio doesn't read this extension. This script transforms the
modes-via-extensions encoding into separate "sets" and "themes" — Tokens
Studio's native mechanism for switching values.

Architecture target (cf. design/PENPOT-ARCHITECTURE.md):
- 11 sets: core, primitives/openTRNTBL, semantic-base, mode/dark, hc/enabled,
  vision/{deuteranopia,protanopia,tritanopia,achromatopsia},
  density/{compact,spacious}.
- 13 themes in 5 groups: Brand / Color / Contrast / Vision / Density.

mode/light has no set (Light = default state, "Dark off"). The Color/Light
theme has empty selectedTokenSets, like Contrast/Default and Vision/Default.

icons are kept in the source (`design/tokens/src/icons.tokens.json`) but
filtered at the Penpot edge (token type `icon` is not supported by Tokens
Studio). They live as runtime SVG assets, not as design tokens here.

Color-aliases indirection: tokens that are color-dependent AND have HC or
vision overrides get split into color-aliases.<path>.light and .dark in
semantic-base. mode/dark redirects the semantic token to the .dark slot.
HC/Vision sets override the .light and .dark aliases directly. Single
set per HC and per vision mode regardless of Color base.

Run:
    python3 design/tokens/scripts/bundle-penpot.py
"""

import json
import sys
from pathlib import Path

SCRIPTS_DIR = Path(__file__).resolve().parent
sys.path.insert(0, str(SCRIPTS_DIR))
from bundle import to_hex_color, load_set_body  # reuse hex conversion + body loader

SRC_DIR = SCRIPTS_DIR.parent / "src"
DIST_DIR = SCRIPTS_DIR.parent / "dist"


def _fmt_number(n):
    if isinstance(n, float) and n.is_integer():
        return str(int(n))
    return str(n)


def drop_unsupported_types(node, types_to_drop):
    """Mutate node in-place: remove any token whose $type is in types_to_drop.

    Walks the tree, deletes leaf tokens of unsupported types, and prunes
    intermediate dicts that become empty as a result.
    """
    if not isinstance(node, dict):
        return
    keys_to_delete = []
    for k, v in node.items():
        if k.startswith("$"):
            continue
        if isinstance(v, dict):
            if v.get("$type") in types_to_drop:
                keys_to_delete.append(k)
            else:
                drop_unsupported_types(v, types_to_drop)
                # Prune empty containers (no $type means it's a group, not a token).
                if "$type" not in v and not any(kk for kk in v.keys() if not kk.startswith("$")):
                    keys_to_delete.append(k)
    for k in keys_to_delete:
        del node[k]


def to_ts_legacy(node):
    """Mutate node in-place: convert DTCG 2025.10 object/array values to TS legacy strings.

    - dimension {value, unit}  -> "<value><unit>"  (e.g. "1rem")
    - duration  {value, unit}  -> "<value><unit>"  (e.g. "100ms")
    - fontFamily [a, b, ...]   -> "a, b, ..."
    String refs like "{core.dimension.40}" are left untouched.
    cubicBezier arrays are left as-is (TS supports them).
    """
    if isinstance(node, dict):
        ttype = node.get("$type")
        val = node.get("$value")
        if ttype == "dimension" and isinstance(val, dict) and "value" in val:
            v = val["value"]
            unit = val.get("unit", "")
            # Penpot stores dimensions in px; convert rem at 16px base.
            if unit == "rem":
                v = v * 16
                unit = "px"
            node["$value"] = f"{_fmt_number(v)}{unit}"
        elif ttype == "duration" and isinstance(val, dict) and "value" in val:
            node["$value"] = f"{_fmt_number(val['value'])}{val.get('unit', '')}"
        elif ttype == "fontFamily" and isinstance(val, list):
            node["$value"] = ", ".join(val)
        for k, v in node.items():
            if k.startswith("$"):
                continue
            to_ts_legacy(v)
    elif isinstance(node, list):
        for item in node:
            to_ts_legacy(item)

# ---------- Set names (consumed by $themes too) ----------
SET_CORE = "core"
SET_PRIMITIVES = "primitives/openTRNTBL"  # slash form matches existing refs in source
SET_SEMANTIC_BASE = "semantic-base"
SET_MODE_DARK = "mode/dark"
SET_HC = "hc/enabled"

VISION_MODES = ['deuteranopia', 'protanopia', 'tritanopia', 'achromatopsia']
DENSITY_MODES = ['compact', 'spacious']


def set_vision(mode):
    return f"vision/{mode}"


def set_density(mode):
    return f"density/{mode}"


# ---------- Helpers ----------

def parse_mode_key(key):
    """Parse 'color:dark|contrast:enhanced' into {'color': 'dark', 'contrast': 'enhanced'}."""
    axes = {}
    for part in key.split('|'):
        if ':' in part:
            axis, value = part.split(':', 1)
            axes[axis] = value
    return axes


def walk_tokens(node, path=''):
    """Yield (dotted_path, token_dict) for every leaf token (a dict with $type)."""
    if not isinstance(node, dict):
        return
    if '$type' in node:
        yield path, node
        return
    for k, v in node.items():
        if k.startswith('$'):
            continue
        sub = f"{path}.{k}" if path else k
        yield from walk_tokens(v, sub)


def set_at_path(tree, path_parts, value):
    """Insert `value` into `tree` at the given dotted-path-parts location, creating groups as needed."""
    cursor = tree
    for p in path_parts[:-1]:
        if p not in cursor:
            cursor[p] = {}
        cursor = cursor[p]
    cursor[path_parts[-1]] = value


def make_token(token_type, value, description=None):
    out = {'$type': token_type, '$value': value}
    if description:
        out['$description'] = description
    return out


# ---------- Core transformation ----------

def transform_semantic_token(path, token, sets):
    """
    Transform one semantic source token into entries spread across sets.
    `sets` is the dict of mutable sub-set dicts; we mutate them in place.
    """
    ext = token.get('$extensions', {})
    modes = ext.get('com.opntrntbl.modes', {})
    parts = path.split('.')

    description = token.get('$description')
    token_type = token['$type']
    base_value = token['$value']

    if not modes:
        # No mode overrides — token goes straight into semantic-base.
        set_at_path(sets[SET_SEMANTIC_BASE], parts, make_token(token_type, base_value, description))
        return

    # Categorize the available modes.
    color_dark_value = modes.get('color:dark')
    hc_light_value = modes.get('contrast:enhanced')
    hc_dark_value = modes.get('color:dark|contrast:enhanced')

    vision_overrides = {}  # vmode -> {'light': v_or_none, 'dark': v_or_none}
    for vmode in VISION_MODES:
        light_v = modes.get(f'vision:{vmode}')
        dark_v = modes.get(f'color:dark|vision:{vmode}')
        if light_v or dark_v:
            vision_overrides[vmode] = {'light': light_v, 'dark': dark_v}

    density_overrides = {}  # dmode -> value
    for dmode in DENSITY_MODES:
        v = modes.get(f'density:{dmode}')
        if v:
            density_overrides[dmode] = v

    needs_color_aliases = bool(hc_light_value or hc_dark_value or vision_overrides)

    if needs_color_aliases:
        # Introduce color-aliases.<path>.{light,dark} as the indirection layer.
        # The semantic token itself becomes an alias to the .light slot (the default).
        alias_root = ['color-aliases'] + parts

        # Light slot = original $value (default = light context).
        set_at_path(
            sets[SET_SEMANTIC_BASE],
            alias_root + ['light'],
            make_token(token_type, base_value),
        )
        # Dark slot = color:dark override or fallback to default.
        set_at_path(
            sets[SET_SEMANTIC_BASE],
            alias_root + ['dark'],
            make_token(token_type, color_dark_value or base_value),
        )

        # Semantic token: alias to .light (default).
        light_alias_ref = '{' + SET_SEMANTIC_BASE + '.' + '.'.join(alias_root + ['light']) + '}'
        set_at_path(
            sets[SET_SEMANTIC_BASE],
            parts,
            make_token(token_type, light_alias_ref, description),
        )

        # mode/dark redirects the semantic token to the .dark slot.
        dark_alias_ref = '{' + SET_SEMANTIC_BASE + '.' + '.'.join(alias_root + ['dark']) + '}'
        set_at_path(
            sets[SET_MODE_DARK],
            parts,
            make_token(token_type, dark_alias_ref),
        )

        # HC overrides the color-aliases (not the semantic token).
        if hc_light_value:
            set_at_path(sets[SET_HC], alias_root + ['light'], make_token(token_type, hc_light_value))
        if hc_dark_value:
            set_at_path(sets[SET_HC], alias_root + ['dark'], make_token(token_type, hc_dark_value))

        # Vision overrides target the same color-aliases.
        for vmode, vvals in vision_overrides.items():
            vset = sets[set_vision(vmode)]
            if vvals['light']:
                set_at_path(vset, alias_root + ['light'], make_token(token_type, vvals['light']))
            if vvals['dark']:
                set_at_path(vset, alias_root + ['dark'], make_token(token_type, vvals['dark']))
    else:
        # Token is only Color-dependent (or Density-only) — simple direct overrides.
        set_at_path(sets[SET_SEMANTIC_BASE], parts, make_token(token_type, base_value, description))
        if color_dark_value:
            set_at_path(sets[SET_MODE_DARK], parts, make_token(token_type, color_dark_value))

    # Density overrides are independent of Color base — direct value override.
    for dmode, value in density_overrides.items():
        set_at_path(sets[set_density(dmode)], parts, make_token(token_type, value))


# ---------- Themes ----------

def build_themes():
    """Return $themes — 13 themes across 5 groups."""
    themes = []

    themes.append({
        "id": "brand-sonos-like",
        "name": "Sonos-like",
        "group": "Brand",
        "selectedTokenSets": {
            SET_CORE: "enabled",
            SET_PRIMITIVES: "enabled",
            SET_SEMANTIC_BASE: "enabled",
        },
    })

    themes.append({
        "id": "color-light",
        "name": "Light",
        "group": "Color",
        "selectedTokenSets": {},  # Light = default state, no override needed
    })
    themes.append({
        "id": "color-dark",
        "name": "Dark",
        "group": "Color",
        "selectedTokenSets": {SET_MODE_DARK: "enabled"},
    })

    themes.append({
        "id": "contrast-default",
        "name": "Default",
        "group": "Contrast",
        "selectedTokenSets": {},
    })
    themes.append({
        "id": "contrast-enhanced",
        "name": "Enhanced",
        "group": "Contrast",
        "selectedTokenSets": {SET_HC: "enabled"},
    })

    themes.append({
        "id": "vision-default",
        "name": "Default",
        "group": "Vision",
        "selectedTokenSets": {},
    })
    for vmode in VISION_MODES:
        themes.append({
            "id": f"vision-{vmode}",
            "name": vmode.capitalize(),
            "group": "Vision",
            "selectedTokenSets": {set_vision(vmode): "enabled"},
        })

    themes.append({
        "id": "density-default",
        "name": "Default",
        "group": "Density",
        "selectedTokenSets": {},
    })
    for dmode in DENSITY_MODES:
        themes.append({
            "id": f"density-{dmode}",
            "name": dmode.capitalize(),
            "group": "Density",
            "selectedTokenSets": {set_density(dmode): "enabled"},
        })

    return themes


# ---------- Main ----------

def main():
    # Load source files (filename stem -> body of the single top-level group).
    sources = {}
    for path in sorted(SRC_DIR.glob("*.tokens.json")):
        stem = path.name[: -len(".tokens.json")]
        sources[stem] = load_set_body(path)

    # Initialize the 10 sets. Sources `icons` are intentionally not loaded:
    # the type `icon` isn't supported by Tokens Studio, and Penpot doesn't
    # materialise empty sets — referencing them would create theme-side ghosts.
    sets = {
        SET_CORE: sources.get('core', {}),
        SET_PRIMITIVES: sources.get('primitives-openTRNTBL', {}),
        SET_SEMANTIC_BASE: {},
        SET_MODE_DARK: {},
        SET_HC: {},
    }
    for vmode in VISION_MODES:
        sets[set_vision(vmode)] = {}
    for dmode in DENSITY_MODES:
        sets[set_density(dmode)] = {}

    # Walk the semantic source and dispatch each token across the sets.
    semantic_source = sources.get('semantic', {})
    transformed = 0
    for token_path, token in walk_tokens(semantic_source):
        transform_semantic_token(token_path, token, sets)
        transformed += 1

    # Assemble the output document.
    output = {
        "$schema": "https://www.designtokens.org/schemas/2025.10/format.json",
    }

    token_set_order = [
        SET_CORE,
        SET_PRIMITIVES,
        SET_SEMANTIC_BASE,
        SET_MODE_DARK,
        SET_HC,
    ] + [set_vision(v) for v in VISION_MODES] \
      + [set_density(d) for d in DENSITY_MODES]

    for s in token_set_order:
        output[s] = sets[s]

    output["$metadata"] = {"tokenSetOrder": token_set_order}
    output["$themes"] = build_themes()

    # Convert matrix color values to hex strings (Tokens Studio format).
    output_hex = to_hex_color(output)

    # Convert DTCG 2025.10 object/array values to TS-legacy string forms.
    # TS in Penpot doesn't grok {value, unit} or fontFamily arrays.
    to_ts_legacy(output_hex)

    # Drop token types Penpot doesn't support (motion + icons are runtime concerns,
    # not design-tool concerns). Keeps source intact; only the Penpot edge filters.
    drop_unsupported_types(output_hex, {"duration", "cubicBezier", "transition", "icon"})

    # Drop $schema — TS rejects unknown top-level keys.
    output_hex.pop("$schema", None)

    DIST_DIR.mkdir(parents=True, exist_ok=True)
    output_path = DIST_DIR / "tokens.penpot.json"
    output_path.write_text(json.dumps(output_hex, indent=2) + "\n")

    # Report.
    def count_leaves(node):
        return sum(1 for _ in walk_tokens(node))

    print(f"Wrote {output_path.relative_to(Path.cwd()) if output_path.is_relative_to(Path.cwd()) else output_path}")
    print(f"  Source semantic tokens transformed: {transformed}")
    print(f"  Sets: {len(token_set_order)}")
    print(f"  Themes: {len(output['$themes'])}")
    print()
    print("Token counts per set:")
    for s in token_set_order:
        print(f"  {s:30s}  {count_leaves(output_hex.get(s, {})):>5}")


if __name__ == "__main__":
    main()
