#!/usr/bin/env python3
"""
Nested-modes token resolver.

Architecture: separate source files per mode layer, no inlining.
  src/defaults.tokens.json          → :root {}  (all semantic defaults)
  src/modes/color.dark.tokens.json  → [data-color="dark"] {}
  src/modes/color.hc.tokens.json    → [data-contrast="enhanced"] {}
  src/modes/density.compact.tokens.json  → [data-density="compact"] {}
  src/modes/density.spacious.tokens.json → [data-density="spacious"] {}

Mode combinations (e.g. dark + compact) are NOT declared.
CSS cascade resolves them: [data-color="dark"] + [data-density="compact"]
on the same element applies BOTH overrides simultaneously. This is the
"nesting without flattening" property that makes this architecture scale.

Reference resolution chain: core → primitives → semantic.
"""

import json, re
from pathlib import Path

ROOT  = Path(__file__).parent
SRC   = ROOT / "src"
MODES = SRC / "modes"
DESIGN_TOKENS = ROOT.parent.parent / "src"

def load(path):
    with open(path) as f:
        return json.load(f)

def flatten(obj: dict, prefix: str = "") -> dict:
    result = {}
    for k, v in obj.items():
        if k.startswith("$"):
            continue
        path = f"{prefix}.{k}" if prefix else k
        if isinstance(v, dict) and "$value" not in v:
            result.update(flatten(v, path))
        else:
            result[path] = v
    return result

def build_resolution_map() -> dict:
    """Build flat map path → resolved CSS value by walking core → primitives."""
    core  = load(DESIGN_TOKENS / "core.tokens.json")
    prims = load(DESIGN_TOKENS / "primitives-openTRNTBL.tokens.json")

    raw = {}
    raw.update(flatten(core))
    raw.update(flatten(prims))

    resolved = {}

    def resolve_value(val):
        if isinstance(val, str) and val.startswith("{") and val.endswith("}"):
            ref = val[1:-1]
            if ref in resolved:
                return resolved[ref]
            if ref in raw:
                tok = raw[ref]
                inner = tok.get("$value") if isinstance(tok, dict) else tok
                return resolve_value(inner)
            return val
        if isinstance(val, dict):
            comp = val.get("components", [])
            if comp and "colorSpace" in val:
                L, C, H = comp
                return f"oklch({L} {C} {H})"
            if "hex" in val:
                return val["hex"]
            if "value" in val and "unit" in val:
                return f"{val['value']}{val['unit']}"
            return str(val)
        return val

    for path, tok in raw.items():
        val = tok.get("$value") if isinstance(tok, dict) else tok
        resolved[path] = resolve_value(val)

    return resolved

def _ref_to_css_var(ref: str) -> str:
    """Convert a token ref path to a CSS var name, stripping semantic/base prefix."""
    for prefix in ("semantic.", "base."):
        if ref.startswith(prefix):
            ref = ref[len(prefix):]
            break
    return f"var(--{ref.replace('.', '-')})"

def resolve_ref(val, res_map: dict):
    """Resolve a token value against core/primitives map; unknown refs → CSS var()."""
    if not isinstance(val, str):
        return format_value(val)
    if val.startswith("{") and val.endswith("}"):
        ref = val[1:-1]
        if ref in res_map:
            return res_map[ref]
        return _ref_to_css_var(ref)
    def sub(m):
        ref = m.group(1)
        if ref in res_map:
            return res_map[ref]
        return _ref_to_css_var(ref)
    return re.sub(r"\{([^}]+)\}", sub, val)

def format_value(val) -> str:
    if isinstance(val, list):
        return ", ".join(f'"{f}"' if " " in f else f for f in val)
    if isinstance(val, dict):
        if "value" in val and "unit" in val:
            return f"{val['value']}{val['unit']}"
        if "duration" in val:
            return val["duration"]
        if "offsetX" in val:
            ox = val["offsetX"]["value"]
            oy = val["offsetY"]["value"]
            blur = val["blur"]["value"]
            spread = val["spread"]["value"]
            color = val.get("color", "rgba(0,0,0,0.1)")
            return f"{ox}px {oy}px {blur}px {spread}px {color}"
    return str(val)

def token_path_to_css_var(path: str) -> str:
    for prefix in ("semantic.", "base."):
        if path.startswith(prefix):
            path = path[len(prefix):]
            break
    return "--" + path.replace(".", "-")

def emit_block(tokens_flat: dict, res_map: dict, indent: str = "  ") -> list[str]:
    lines = []
    for path, tok in sorted(tokens_flat.items()):
        val = tok.get("$value") if isinstance(tok, dict) else tok
        typ = tok.get("$type", "") if isinstance(tok, dict) else ""
        css_var = token_path_to_css_var(path)

        if typ == "typography" and isinstance(val, dict):
            suffixes = {"fontSize": "size", "lineHeight": "line-height",
                        "fontWeight": "weight", "fontFamily": "family"}
            for k, s in suffixes.items():
                if k in val:
                    v = format_value(val[k]) if not isinstance(val[k], str) else val[k]
                    resolved = resolve_ref(v, res_map)
                    if isinstance(resolved, list):
                        resolved = ", ".join(f'"{f}"' if " " in f else f for f in resolved)
                    lines.append(f"{indent}{css_var}-{s}: {resolved};")
        elif typ == "transition" and isinstance(val, dict):
            if "duration" in val:
                lines.append(f"{indent}{css_var}-duration: {resolve_ref(val['duration'], res_map)};")
            if "timingFunction" in val:
                lines.append(f"{indent}{css_var}-easing: {resolve_ref(val['timingFunction'], res_map)};")
        elif typ == "shadow" and isinstance(val, list):
            parts = [format_value(s) for s in val]
            lines.append(f"{indent}{css_var}: {', '.join(parts) if parts else 'none'};")
        else:
            resolved = resolve_ref(val, res_map)
            if isinstance(resolved, list):
                parts = []
                for item in resolved:
                    if isinstance(item, str):
                        parts.append(f'"{item}"' if " " in item else item)
                    else:
                        parts.append(format_value(item))
                resolved = ", ".join(parts)
            lines.append(f"{indent}{css_var}: {resolved};")
    return lines

def generate():
    res_map = build_resolution_map()

    defaults  = flatten(load(SRC / "defaults.tokens.json"))
    mode_files = {
        '[data-color="dark"]':                         "color.dark.tokens.json",
        '[data-contrast="enhanced"]':                  "color.hc.tokens.json",
        '[data-density="compact"]':                    "density.compact.tokens.json",
        '[data-density="spacious"]':                   "density.spacious.tokens.json",
        '[data-vision="achromatopsia"]':               "vision.achromatopsia.tokens.json",
        '[data-vision="deuteranopia"]':                "vision.deuteranopia.tokens.json",
        '[data-vision="protanopia"]':                  "vision.protanopia.tokens.json",
        '[data-vision="tritanopia"]':                  "vision.tritanopia.tokens.json",
    }

    scope = '[data-token-system="nested-modes"]'
    out = [
        "/*",
        " * Nested-modes token system — generated by resolver.py",
        " * Do not edit directly. Edit src/defaults.tokens.json or src/modes/*.tokens.json.",
        " *",
        " * Architecture: each mode layer is a separate file with only its overrides.",
        " * Combinations (dark + compact, dark + hc, etc.) are NOT declared —",
        " * the CSS cascade resolves them by stacking the active [data-*] selectors.",
        " * This is O(n + m) declarations, not O(n × m).",
        " */",
        "",
        f"{scope} {{",
    ]
    out.extend(emit_block(defaults, res_map))
    out.append("}")
    out.append("")

    for selector, fname in mode_files.items():
        fpath = MODES / fname
        if not fpath.exists():
            continue
        mode_tokens = flatten(load(fpath))
        out.append(f"{scope}{selector} {{")
        out.extend(emit_block(mode_tokens, res_map))
        out.append("}")
        out.append("")

    css = "\n".join(out)
    (ROOT / "tokens.css").write_text(css)
    print(f"  Wrote {ROOT / 'tokens.css'} ({len(out)} lines)")

if __name__ == "__main__":
    generate()
