#!/usr/bin/env python3
"""Resolve semantic tokens into a 20-mode matrix for Figma export.

Re-uses cascade logic from generate-css.py (`_value_for_mode`, `resolve_alias`,
formatters) to compute, for each semantic token, the resolved hex value across
the 20 consolidated modes:

  light, dark,
  light-hc, dark-hc,
  light-deutan, dark-deutan, ..., dark-achroma,
  light-hc-deutan, dark-hc-deutan, ..., dark-hc-achroma

Density is exported separately into 3 modes (default, compact, spacious).

Outputs:
  dist/tokens.modes-matrix.json   — semantic non-spacing × 20 modes (hex)
  dist/tokens.density-matrix.json — semantic spacing × 3 modes (rem)

Run:
  python3 design/tokens/scripts/resolve-modes-matrix.py
"""

from __future__ import annotations

import importlib.util
import json
import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
DIST = ROOT / "dist"
TOKENS_JSON = DIST / "tokens.json"
GEN_CSS = ROOT / "scripts" / "generate-css.py"

# Hot-load generate-css.py (filename has a hyphen → can't `import generate-css`)
spec = importlib.util.spec_from_file_location("gen_css", GEN_CSS)
gen = importlib.util.module_from_spec(spec)
spec.loader.exec_module(gen)


# ---------------------------------------------------------------------------
# Mode definitions
# ---------------------------------------------------------------------------

VISION_MAP = {
    "deutan":  "deuteranopia",
    "protan":  "protanopia",
    "tritan":  "tritanopia",
    "achroma": "achromatopsia",
}

# Build the 20 modes as ordered list of (mode_label, mode_terms)
# mode_terms is a tuple of (axis, value) consumed by _value_for_mode/resolve_alias.
def build_modes():
    modes = []
    for color in ("light", "dark"):
        for hc in (False, True):
            for vision_short in (None, "deutan", "protan", "tritan", "achroma"):
                label_parts = [color]
                if hc:
                    label_parts.append("hc")
                if vision_short:
                    label_parts.append(vision_short)
                label = "-".join(label_parts)

                terms = []
                if color == "dark":
                    terms.append(("color", "dark"))
                if hc:
                    terms.append(("contrast", "enhanced"))
                if vision_short:
                    terms.append(("vision", VISION_MAP[vision_short]))
                modes.append((label, tuple(terms)))
    return modes


MODES_20 = build_modes()
DENSITY_MODES = [
    ("default",  ()),
    ("compact",  (("density", "compact"),)),
    ("spacious", (("density", "spacious"),)),
]


# ---------------------------------------------------------------------------
# Color → hex normalization
# ---------------------------------------------------------------------------

# CSS oklch() → hex via colorsys/manual.
def oklch_to_hex(L: float, C: float, H: float) -> str:
    """Convert OKLCH to sRGB hex (gamut-clipped, gamma corrected)."""
    import math
    h_rad = math.radians(H)
    a = C * math.cos(h_rad)
    b = C * math.sin(h_rad)

    # OKLab → linear sRGB (Björn Ottosson)
    l_ = L + 0.3963377774 * a + 0.2158037573 * b
    m_ = L - 0.1055613458 * a - 0.0638541728 * b
    s_ = L - 0.0894841775 * a - 1.2914855480 * b

    l = l_ ** 3
    m = m_ ** 3
    s = s_ ** 3

    r =  4.0767416621 * l - 3.3077115913 * m + 0.2309699292 * s
    g = -1.2684380046 * l + 2.6097574011 * m - 0.3413193965 * s
    bl =  -0.0041960863 * l - 0.7034186147 * m + 1.7076147010 * s

    def to_srgb(c):
        c = max(0.0, min(1.0, c))
        if c <= 0.0031308:
            v = 12.92 * c
        else:
            v = 1.055 * (c ** (1 / 2.4)) - 0.055
        return max(0, min(255, round(v * 255)))

    return f"#{to_srgb(r):02x}{to_srgb(g):02x}{to_srgb(bl):02x}"


_OKLCH_RE = re.compile(
    r"oklch\(\s*([0-9.+-eE]+)\s+([0-9.+-eE]+)\s+([0-9.+-eE]+)(?:\s*/\s*([0-9.+-eE]+))?\s*\)"
)
_HEX_RE = re.compile(r"^#[0-9a-fA-F]{6,8}$")
_COLOR_MIX_RE = re.compile(r"color-mix\(.+\)", re.DOTALL)


def normalize_color(value, tokens, mode_terms):
    """Best-effort: return a hex string for whatever color expression we got.

    - If the input is already a hex (#rrggbb / #rrggbbaa) → keep it.
    - If oklch(L C H[/A]) → convert via oklch_to_hex (alpha → #rrggbbaa).
    - color-mix() expressions → resolve operands and crude midpoint mix.
    - Anything else → pass-through (Figma will fail-soft if invalid).
    """
    if isinstance(value, dict):
        # DTCG matrix color object straight from the bundle.
        if value.get("colorSpace") == "oklch":
            comps = value.get("components", [])
            alpha = value.get("alpha", 1)
            if len(comps) >= 3:
                hex_ = oklch_to_hex(comps[0], comps[1], comps[2])
                if alpha < 1:
                    a = max(0, min(255, round(alpha * 255)))
                    return f"{hex_}{a:02x}"
                return hex_
        if "hex" in value:
            return value["hex"]

    if not isinstance(value, str):
        return str(value)

    s = value.strip()

    if _HEX_RE.match(s):
        return s.lower()

    m = _OKLCH_RE.search(s)
    if m and not _COLOR_MIX_RE.search(s):
        L = float(m.group(1))
        C = float(m.group(2))
        H = float(m.group(3))
        hex_ = oklch_to_hex(L, C, H)
        if m.group(4):
            try:
                alpha = float(m.group(4))
                a = max(0, min(255, round(alpha * 255)))
                return f"{hex_}{a:02x}"
            except ValueError:
                pass
        return hex_

    # color-mix(in oklch, COLOR_A PCT%, COLOR_B) — crude mid-mix.
    if s.startswith("color-mix"):
        return resolve_color_mix(s, tokens, mode_terms)

    return s


_MIX_PARSE_RE = re.compile(
    r"color-mix\(\s*in\s+\w+\s*,\s*(.+?)\s*\)$", re.DOTALL
)


def _split_mix_args(inner: str):
    """Split color-mix inner args by top-level commas (ignore nested parens)."""
    out, depth, buf = [], 0, []
    for ch in inner:
        if ch == "(":
            depth += 1
            buf.append(ch)
        elif ch == ")":
            depth -= 1
            buf.append(ch)
        elif ch == "," and depth == 0:
            out.append("".join(buf).strip())
            buf = []
        else:
            buf.append(ch)
    if buf:
        out.append("".join(buf).strip())
    return out


def _hex_to_rgb(hex_: str):
    h = hex_.lstrip("#")
    if len(h) >= 6:
        return (int(h[0:2], 16), int(h[2:4], 16), int(h[4:6], 16))
    return (0, 0, 0)


def resolve_color_mix(expr: str, tokens, mode_terms) -> str:
    """Approximate color-mix(in oklch, A pct%, B) → hex via linear RGB mix.

    Good enough for Figma static export (hex). Real color-mix happens at
    runtime in the browser — this is a best-effort doc/preview value.
    """
    m = _MIX_PARSE_RE.match(expr.strip())
    if not m:
        return expr
    args = _split_mix_args(m.group(1))
    if len(args) < 2:
        return expr

    def parse_part(part):
        tokens_ = part.rsplit(" ", 1)
        if len(tokens_) == 2 and tokens_[1].endswith("%"):
            try:
                return tokens_[0], float(tokens_[1].rstrip("%"))
            except ValueError:
                return part, None
        return part, None

    a_color, a_pct = parse_part(args[0])
    b_color, b_pct = parse_part(args[1])

    if a_pct is None and b_pct is None:
        a_pct = 50.0
        b_pct = 50.0
    elif a_pct is None:
        a_pct = 100.0 - b_pct
    elif b_pct is None:
        b_pct = 100.0 - a_pct

    a_hex = normalize_color(gen.resolve_alias(tokens, a_color, mode_terms=mode_terms), tokens, mode_terms)
    b_hex = normalize_color(gen.resolve_alias(tokens, b_color, mode_terms=mode_terms), tokens, mode_terms)
    if not (_HEX_RE.match(a_hex) and _HEX_RE.match(b_hex)):
        return expr

    ar, ag, ab = _hex_to_rgb(a_hex)
    br, bg, bb = _hex_to_rgb(b_hex)
    wa = a_pct / 100.0
    wb = b_pct / 100.0
    total = wa + wb or 1.0
    r = round((ar * wa + br * wb) / total)
    g = round((ag * wa + bg * wb) / total)
    bch = round((ab * wa + bb * wb) / total)
    return f"#{r:02x}{g:02x}{bch:02x}"


# ---------------------------------------------------------------------------
# Walk semantic tree and resolve per-mode values
# ---------------------------------------------------------------------------

SKIP_TYPES = {"typography", "transition", "shadow"}  # composites: not exported as native Figma vars


def collect_color_tokens(tokens):
    """Return list of (dot.path, type, leaf_node) for color tokens."""
    out = []
    semantic = tokens.get("semantic", {})
    _walk(semantic, ["semantic"], out)
    return out


def _walk(node, path, out):
    if not isinstance(node, dict):
        return
    if "$type" in node and "$value" in node:
        type_ = node["$type"]
        if type_ in SKIP_TYPES:
            return
        out.append((".".join(path), type_, node))
        return
    for k, v in node.items():
        if k.startswith("$"):
            continue
        _walk(v, path + [k], out)


def resolve_for_modes(tokens, leaf, type_, modes):
    """Return {mode_label: resolved_value_string} for every mode."""
    result = {}
    for label, terms in modes:
        # Cascade: pick override matching active mode (longest match) or default.
        value = gen._value_for_mode(leaf, terms)
        # Recursive alias resolution carrying the active mode.
        resolved = gen.resolve_alias(tokens, value, mode_terms=terms)
        if type_ == "color":
            result[label] = normalize_color(resolved, tokens, terms)
        elif type_ == "dimension":
            result[label] = gen.format_dimension(resolved)
        elif type_ in ("number", "opacity"):
            result[label] = gen.format_number(resolved)
        elif type_ == "duration":
            result[label] = gen.format_duration(resolved)
        elif type_ == "cubicBezier":
            result[label] = gen.format_easing(resolved)
        else:
            result[label] = resolved if isinstance(resolved, (str, int, float, bool)) else json.dumps(resolved)
    return result


def split_by_axis(tokens):
    """Density-axis tokens go to a separate matrix; everything else → 20 modes."""
    color_or_static, density = [], []
    for path, type_, leaf in collect_color_tokens(tokens):
        ext = leaf.get("$extensions", {}) or {}
        modes_ext = ext.get("com.opntrntbl.modes", {}) or {}
        axes_used = set()
        for k in modes_ext:
            for term in k.split("|"):
                if ":" in term:
                    axes_used.add(term.split(":", 1)[0])
        if axes_used == {"density"}:
            density.append((path, type_, leaf))
        else:
            color_or_static.append((path, type_, leaf))
    return color_or_static, density


# ---------------------------------------------------------------------------
# Main
# ---------------------------------------------------------------------------

def main():
    if not TOKENS_JSON.exists():
        print(f"ERROR: {TOKENS_JSON} not found. Run bundle.py first.", file=sys.stderr)
        sys.exit(1)

    tokens = json.loads(TOKENS_JSON.read_text())
    color_static, density = split_by_axis(tokens)

    print(f"Found {len(color_static)} non-density semantic tokens (→ 20 modes).")
    print(f"Found {len(density)} density-axis semantic tokens (→ 3 modes).")

    # 20-mode matrix
    matrix = {}
    for path, type_, leaf in color_static:
        matrix[path] = {
            "type": type_,
            "values": resolve_for_modes(tokens, leaf, type_, MODES_20),
            "description": leaf.get("$description", ""),
        }
    out_path = DIST / "tokens.modes-matrix.json"
    out_path.write_text(json.dumps(matrix, indent=2) + "\n")
    print(f"Wrote {out_path}  ({out_path.stat().st_size:,} bytes)")

    # 3-mode density matrix
    density_matrix = {}
    for path, type_, leaf in density:
        density_matrix[path] = {
            "type": type_,
            "values": resolve_for_modes(tokens, leaf, type_, DENSITY_MODES),
            "description": leaf.get("$description", ""),
        }
    dout = DIST / "tokens.density-matrix.json"
    dout.write_text(json.dumps(density_matrix, indent=2) + "\n")
    print(f"Wrote {dout}  ({dout.stat().st_size:,} bytes)")

    # Sanity check: print 5 known tokens
    print("\nSanity check (5 tokens, all 20 modes):")
    sample_paths = [
        "semantic.surface.canvas.background",
        "semantic.surface.base.background",
        "semantic.accent.default",
        "semantic.text.color.primary",
        "semantic.border.focus",
    ]
    for p in sample_paths:
        if p not in matrix:
            print(f"  [missing] {p}")
            continue
        vals = matrix[p]["values"]
        print(f"  {p}")
        for label, _ in MODES_20:
            print(f"    {label:30s} {vals.get(label)}")


if __name__ == "__main__":
    main()
