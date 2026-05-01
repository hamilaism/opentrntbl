#!/usr/bin/env python3
"""
openTRNTBL — Core tokens generator.

Produces Tier 0 raw material (DTCG 2025.10) under design/tokens/src/:
  - color.tokens.json       9 hues x 11 shades (OKLCH + hex fallback)
  - dimension.tokens.json   22 rem values (hairline 1px as sub-rem exception)
  - opacity.tokens.json     9 steps
  - font-size.tokens.json   aliases onto dimension
  - line-height.tokens.json unitless ratios
  - duration.tokens.json    5 motion durations
  - easing.tokens.json      5 cubic-bezier curves

Color convention (Fusilier-style):
  - Scale 0..200, higher = lighter.
  - Difference >= 100 between two shades => WCAG AA (>= 4.5:1) target.
  - Difference >= 75  => WCAG AA UI (>= 3:1) target.
  - Difference >= 150 => WCAG AAA (>= 7:1) target.

  Targets hold across most UI-relevant pairs. Extremes (e.g. shade 100 vs 200)
  can fail strict AA due to the non-linear WCAG contrast curve; exceptions
  are reported by the validator, not silently suppressed.

Run:
  python3 design/tokens/scripts/generate-core.py
"""

import json
import math
from pathlib import Path


# ---------------------------------------------------------------------------
# OKLCH / sRGB conversion (pure stdlib, from CSS Color 4 + Bottosson)
# ---------------------------------------------------------------------------

def oklch_to_oklab(L, C, H):
    h = math.radians(H)
    return (L, C * math.cos(h), C * math.sin(h))


def oklab_to_linear_srgb(L, a, b):
    l_ = L + 0.3963377774 * a + 0.2158037573 * b
    m_ = L - 0.1055613458 * a - 0.0638541728 * b
    s_ = L - 0.0894841775 * a - 1.2914855480 * b
    l, m, s = l_ ** 3, m_ ** 3, s_ ** 3
    r = +4.0767416621 * l - 3.3077115913 * m + 0.2309699292 * s
    g = -1.2684380046 * l + 2.6097574011 * m - 0.3413193965 * s
    b_ = -0.0041960863 * l - 0.7034186147 * m + 1.7076147010 * s
    return (r, g, b_)


def linear_to_srgb(c):
    if c <= 0.0031308:
        return 12.92 * c
    return 1.055 * (c ** (1 / 2.4)) - 0.055


def srgb_to_hex(r, g, b):
    def clamp(x):
        return max(0.0, min(1.0, x))
    return "#{:02x}{:02x}{:02x}".format(
        round(clamp(r) * 255),
        round(clamp(g) * 255),
        round(clamp(b) * 255),
    )


def in_gamut(r, g, b, eps=1e-4):
    return all(-eps <= c <= 1 + eps for c in (r, g, b))


def oklch_to_hex_in_gamut(L, C, H):
    """Convert OKLCH to sRGB hex, binary-search chroma if out of gamut."""
    lab = oklch_to_oklab(L, C, H)
    rgb = oklab_to_linear_srgb(*lab)
    if in_gamut(*rgb):
        srgb = tuple(linear_to_srgb(x) for x in rgb)
        return srgb_to_hex(*srgb), C
    lo, hi = 0.0, C
    for _ in range(30):
        mid = (lo + hi) / 2
        lab = oklch_to_oklab(L, mid, H)
        rgb = oklab_to_linear_srgb(*lab)
        if in_gamut(*rgb):
            lo = mid
        else:
            hi = mid
    lab = oklch_to_oklab(L, lo, H)
    rgb = oklab_to_linear_srgb(*lab)
    srgb = tuple(linear_to_srgb(max(0.0, min(1.0, x))) for x in rgb)
    return srgb_to_hex(*srgb), lo


# ---------------------------------------------------------------------------
# WCAG contrast
# ---------------------------------------------------------------------------

def relative_luminance(hex_color):
    r = int(hex_color[1:3], 16) / 255
    g = int(hex_color[3:5], 16) / 255
    b = int(hex_color[5:7], 16) / 255
    def lin(c):
        return c / 12.92 if c <= 0.03928 else ((c + 0.055) / 1.055) ** 2.4
    return 0.2126 * lin(r) + 0.7152 * lin(g) + 0.0722 * lin(b)


def contrast_ratio(hex1, hex2):
    l1, l2 = relative_luminance(hex1), relative_luminance(hex2)
    hi, lo = max(l1, l2), min(l1, l2)
    return (hi + 0.05) / (lo + 0.05)


# ---------------------------------------------------------------------------
# Color ramps (Fusilier-style)
# ---------------------------------------------------------------------------

SHADES = [0, 10, 25, 50, 75, 100, 125, 150, 175, 190, 200]

HUES = {
    "neutral": {"h": 0,   "chroma_peak": 0.0},
    "red":     {"h": 29,  "chroma_peak": 0.18},
    "orange":  {"h": 55,  "chroma_peak": 0.17},
    "gold":    {"h": 85,  "chroma_peak": 0.13},
    "yellow":  {"h": 100, "chroma_peak": 0.17},
    "green":   {"h": 145, "chroma_peak": 0.17},
    "cyan":    {"h": 195, "chroma_peak": 0.13},
    "blue":    {"h": 255, "chroma_peak": 0.19},
    "violet":  {"h": 300, "chroma_peak": 0.18},
}


# Luminance-Y targets per shade.  Calibrated so that WCAG invariants hold
# universally across hues: diff >= 100 gives ratio >= 4.5 (AA text),
# diff >= 75 gives >= 3.0 (AA UI), diff >= 150 gives >= 7.0 (AAA).
#
# Derivation: WCAG contrast is (Y_hi + 0.05) / (Y_lo + 0.05).  To chain
# diff-100 at ratio 4.5 from Y(0)=0 to Y(200)=1, the mid point must satisfy
# Y(100) ~= 0.178.  Symmetric chaining yields the other anchors.
SHADE_Y_TARGETS = {
    0:   0.000,
    10:  0.004,
    25:  0.020,
    50:  0.055,
    75:  0.105,
    100: 0.180,
    125: 0.290,
    150: 0.430,
    175: 0.680,
    190: 0.880,
    200: 1.000,
}


def hex_to_Y(hex_color):
    r = int(hex_color[1:3], 16) / 255
    g = int(hex_color[3:5], 16) / 255
    b = int(hex_color[5:7], 16) / 255
    def lin(c):
        return c / 12.92 if c <= 0.03928 else ((c + 0.055) / 1.055) ** 2.4
    return 0.2126 * lin(r) + 0.7152 * lin(g) + 0.0722 * lin(b)


def find_L_for_Y(target_Y, chroma_req, hue, iterations=40):
    """Binary-search OKLCH L so the rendered sRGB has linear luminance Y."""
    if target_Y <= 0:
        return 0.0
    if target_Y >= 1:
        return 1.0
    lo, hi = 0.0, 1.0
    for _ in range(iterations):
        L = (lo + hi) / 2
        hex_val, _ = oklch_to_hex_in_gamut(L, chroma_req, hue)
        Y = hex_to_Y(hex_val)
        if Y < target_Y:
            lo = L
        else:
            hi = L
    return (lo + hi) / 2


def chroma_envelope(shade, peak):
    """Bell curve peaking around shade 100, decaying toward extremes.

    Keeps colored hues visibly tinted at extremes without blowing gamut.
    Neutral passes peak=0 -> chroma always 0.
    """
    if peak == 0:
        return 0.0
    center = 100
    width = 85
    falloff = math.exp(-((shade - center) ** 2) / (2 * width * width))
    floor = 0.15  # keep at least 15% of peak chroma at extremes (for tinted extremes)
    return peak * (floor + (1 - floor) * falloff)


ROLE_DESCRIPTION = {
    0:   "Darkest extreme. Pure black for neutral; deepest tint for hues.",
    10:  "Near-dark. Avoids OLED banding from absolute #000.",
    25:  "Deep. Text high-emphasis on light surfaces.",
    50:  "Strong. Body text on light; solid idle on bright themes.",
    75:  "Mid-dark. Border strong on light; solid idle.",
    100: "Midpoint. Placeholder text, disabled controls, max-chroma color.",
    125: "Mid-light. Interactive hover on dark themes.",
    150: "Light. Raised surface on bright themes; solid idle on dark themes.",
    175: "Very light. Base surface on light themes; body text on dark themes.",
    190: "Near-light. Avoids banding from absolute #fff.",
    200: "Lightest extreme. Pure white for neutral; palest tint for hues.",
}


def build_color_group():
    palette = {}
    for name, cfg in HUES.items():
        ramp = {}
        for shade in SHADES:
            Y_target = SHADE_Y_TARGETS[shade]
            C_req = chroma_envelope(shade, cfg["chroma_peak"])
            L = find_L_for_Y(Y_target, C_req, cfg["h"])
            hex_val, C_fit = oklch_to_hex_in_gamut(L, C_req, cfg["h"])
            ramp[str(shade)] = {
                "$type": "color",
                "$value": {
                    "colorSpace": "oklch",
                    "components": [round(L, 4), round(C_fit, 4), cfg["h"]],
                    "alpha": 1,
                    "hex": hex_val,
                },
                "$description": ROLE_DESCRIPTION[shade],
            }
        palette[name] = ramp
    return palette


# ---------------------------------------------------------------------------
# WCAG validator — reports exceptions rather than throwing
# ---------------------------------------------------------------------------

INVARIANTS = [
    # (min_diff, min_ratio, label)
    (75,  3.0, "AA UI"),
    (100, 4.5, "AA text"),
    (150, 7.0, "AAA text"),
]


def validate(palette):
    failures = []
    for hue_name, ramp in palette.items():
        shades = sorted(int(k) for k in ramp.keys())
        for i, s1 in enumerate(shades):
            for s2 in shades[i + 1:]:
                diff = s2 - s1
                h1 = ramp[str(s1)]["$value"]["hex"]
                h2 = ramp[str(s2)]["$value"]["hex"]
                ratio = contrast_ratio(h1, h2)
                for min_diff, min_ratio, label in INVARIANTS:
                    if diff >= min_diff and ratio < min_ratio:
                        failures.append({
                            "hue": hue_name,
                            "pair": f"{s1} <-> {s2}",
                            "diff": diff,
                            "ratio": round(ratio, 2),
                            "expected": f">= {min_ratio}",
                            "level": label,
                        })
                        break  # report tightest-failing invariant only
    return failures


# ---------------------------------------------------------------------------
# Dimension tokens (in rem, base 16px)
# ---------------------------------------------------------------------------

DIMENSION_INDICES = [
    1, 5, 10, 15, 20, 25, 30, 35, 40, 45, 50, 55, 60,
    70, 80, 90, 100, 120, 160, 200, 240, 320,
]

DIMENSION_DESCRIPTIONS = {
    1:   "Hairline. Sub-rem exception for 1px borders/dividers.",
    5:   "2px. Fine border, micro-radius.",
    10:  "4px. Base unit. Border-radius small.",
    40:  "16px. One rem. Typography base; default body padding.",
    100: "40px. Minimum tap target (WCAG AA 2.2).",
    320: "128px. Hero dimensions.",
}


def build_dimension_group():
    tokens = {}
    for idx in DIMENSION_INDICES:
        rem_value = round(idx * 0.025, 4)
        entry = {
            "$type": "dimension",
            "$value": {"value": rem_value, "unit": "rem"},
        }
        if idx in DIMENSION_DESCRIPTIONS:
            entry["$description"] = DIMENSION_DESCRIPTIONS[idx]
        tokens[f"{idx:02d}" if idx < 100 else str(idx)] = entry
    return tokens


# ---------------------------------------------------------------------------
# Opacity tokens
# ---------------------------------------------------------------------------

OPACITY_STEPS = [0, 4, 8, 16, 24, 40, 60, 80, 100]


def build_opacity_group():
    tokens = {}
    for step in OPACITY_STEPS:
        tokens[f"{step:03d}"] = {
            "$type": "number",
            "$value": step / 100,
        }
    return tokens


# ---------------------------------------------------------------------------
# Font-size tokens (aliases onto dimensions)
# ---------------------------------------------------------------------------
# Typography uses a subset of the dimension scale. Aliases point at the canonical
# dimension tokens so every size derives from the rhythmic system.
#
# Index convention here: same 0..100+ as our dimension naming, subset for typo use.

# alias -> dimension token key it points at
FONT_SIZE_ALIASES = {
    "10":  "30",   # 12px  caption
    "20":  "35",   # 14px  small body
    "30":  "40",   # 16px  body
    "40":  "45",   # 18px  large body
    "50":  "50",   # 20px  subheading
    "60":  "60",   # 24px  heading sm
    "80":  "80",   # 32px  heading md
    "90":  "90",   # 36px  heading lg
    "100": "100",  # 40px  display sm
    "120": "120",  # 48px  display md
    "160": "160",  # 64px  display lg
}


def build_font_size_group():
    tokens = {}
    for alias, dim_key in FONT_SIZE_ALIASES.items():
        tokens[alias] = {
            "$type": "dimension",
            "$value": "{core.dimension." + dim_key + "}",
        }
    return tokens


# ---------------------------------------------------------------------------
# Line-height tokens (unitless ratios)
# ---------------------------------------------------------------------------

LINE_HEIGHT_STEPS = {
    "10": (1.0,  "Tight. Display typography, uppercase, monospace blocks."),
    "20": (1.2,  "Snug. Headings, condensed UI."),
    "30": (1.4,  "Default. Body text, controls."),
    "40": (1.6,  "Loose. Long-form reading, prose."),
    "50": (1.8,  "Airy. Captions on dense layouts."),
}


def build_line_height_group():
    tokens = {}
    for k, (v, desc) in LINE_HEIGHT_STEPS.items():
        tokens[k] = {
            "$type": "number",
            "$value": v,
            "$description": desc,
        }
    return tokens


# ---------------------------------------------------------------------------
# Duration tokens
# ---------------------------------------------------------------------------

DURATION_STEPS = {
    "instant":  (0,   "Immediate, no transition."),
    "fast":     (100, "Micro-interactions: hover, focus."),
    "moderate": (200, "Standard UI transitions."),
    "slow":     (400, "Enter/exit: modals, drawers."),
    "slower":   (800, "Expressive transitions, rare."),
}


def build_duration_group():
    tokens = {}
    for name, (ms, desc) in DURATION_STEPS.items():
        tokens[name] = {
            "$type": "duration",
            "$value": {"value": ms, "unit": "ms"},
            "$description": desc,
        }
    return tokens


# ---------------------------------------------------------------------------
# Easing tokens
# ---------------------------------------------------------------------------

EASING_STEPS = {
    "linear":     ([0, 0, 1, 1],             "Constant rate. Use sparingly."),
    "in":         ([0.4, 0, 1, 1],           "Accelerate. Exiting elements."),
    "out":        ([0, 0, 0.2, 1],           "Decelerate. Entering elements."),
    "in-out":     ([0.4, 0, 0.2, 1],         "Standard two-way transition."),
    "emphasized": ([0.2, 0, 0, 1],           "Punchy. Expressive entrances."),
}


def build_easing_group():
    tokens = {}
    for name, (bezier, desc) in EASING_STEPS.items():
        tokens[name] = {
            "$type": "cubicBezier",
            "$value": bezier,
            "$description": desc,
        }
    return tokens


# ---------------------------------------------------------------------------
# Driver
# ---------------------------------------------------------------------------

OUTPUT_FILE = Path(__file__).resolve().parent.parent / "src" / "core.tokens.json"


def build_core_set():
    """Return core groups as a single 'core' token set body.

    Groups live under the set: palette, dimension, opacity, font-size,
    line-height, duration, easing. Standard DTCG 2025.10 nesting within.
    """
    return {
        "palette":     build_color_group(),
        "dimension":   build_dimension_group(),
        "opacity":     build_opacity_group(),
        "font-size":   build_font_size_group(),
        "line-height": build_line_height_group(),
        "duration":    build_duration_group(),
        "easing":      build_easing_group(),
    }


def main():
    core = build_core_set()

    document = {
        "$schema": "https://www.designtokens.org/schemas/2025.10/format.json",
        "core": core,
    }

    OUTPUT_FILE.parent.mkdir(parents=True, exist_ok=True)
    OUTPUT_FILE.write_text(json.dumps(document, indent=2) + "\n")

    size = OUTPUT_FILE.stat().st_size
    print(f"Wrote {OUTPUT_FILE.relative_to(Path.cwd())}  ({size:,} bytes)")

    # Token counts
    counts = {k: count_tokens(v) for k, v in core.items()}
    print()
    print("Token counts by group:")
    for group, n in counts.items():
        print(f"  {group:12s}  {n:>3d}")
    print(f"  {'total':12s}  {sum(counts.values()):>3d}")

    # WCAG validation on color palette
    failures = validate(core["palette"])
    total_pairs = len(HUES) * (len(SHADES) * (len(SHADES) - 1) // 2)
    print()
    print(f"WCAG validation: {total_pairs - len(failures)}/{total_pairs} pairs pass invariants")
    if failures:
        print(f"  {len(failures)} pairs fail:")
        for f in failures[:15]:
            print(f"  - {f['hue']:8s} {f['pair']:12s} diff {f['diff']:3d}  "
                  f"ratio {f['ratio']:5.2f} (expected {f['expected']}, {f['level']})")
        if len(failures) > 15:
            print(f"  ... {len(failures) - 15} more")


def count_tokens(node):
    """Count leaf tokens (nodes with $type) under a group."""
    if isinstance(node, dict):
        if "$type" in node:
            return 1
        return sum(count_tokens(v) for v in node.values())
    return 0


if __name__ == "__main__":
    main()
