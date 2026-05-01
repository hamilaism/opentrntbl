#!/usr/bin/env python3
"""
openTRNTBL — Semantic Tier 2 generator.

Produces `design/tokens/src/semantic.tokens.json`. Semantic tokens:
  - Name the *intent* (surface.canvas, accent.default, text.primary...)
  - Alias to Tier 1 primitives decisions (not directly to core)
  - Carry mode-specific resolutions via the `$extensions` block

## Mode encoding (first pass: color + density)

A token's `$value` is its canonical resolution (light mode, default
contrast, default vision, default density). Alternative modes sit under:

    "$extensions": {
      "com.opntrntbl.modes": {
        "color:dark":       "<override-value>",
        "density:compact":  "<override-value>"
      }
    }

Mode keys use `axis:variant` (e.g. `color:dark`). Combinations are encoded
with `|` separator (e.g. `color:dark|contrast:enhanced`). Non-listed
combinations fall back on the default.

Tools that don't read the extension get the canonical value — still
usable, just single-mode.

## Color-mix fallback (hover/pressed)

Interactive states (`solid.*.hover`, `solid.*.pressed`) use `color-mix()`
in the primary `$value` so the tint derives from the base color. For
tools that can't compute color-mix at build time, a fallback alias
sits under:

    "$extensions": {
      "com.opntrntbl.fallback": {
        "$value": "<alias-to-a-precomputed-shade>"
      }
    }

## Contrast/vision modes

Deferred to iteration 2 (after visual review in Storybook). Adding them
later means extending the `modes` extension of existing tokens, no
structural change.

Run:
  python3 design/tokens/scripts/generate-semantic.py
"""

import json
from pathlib import Path


THEME = "openTRNTBL"

OUTPUT_FILE = Path(__file__).resolve().parent.parent / "src" / "semantic.tokens.json"


# ---------------------------------------------------------------------------
# Alias helpers
# ---------------------------------------------------------------------------

def primitive(path):
    """Reference a Tier 1 primitives token."""
    return "{primitives/" + THEME + "." + path + "}"


def core(path):
    """Reference a Tier 0 core token."""
    return "{core." + path + "}"


def self_ref(path):
    """Reference another semantic token (same tier)."""
    return "{semantic." + path + "}"


# ---------------------------------------------------------------------------
# Token builders
# ---------------------------------------------------------------------------

def color_token(default, modes=None, fallback=None, description=None):
    """Build a color semantic token.

    Args:
        default: default (canonical) $value — an alias string or literal.
        modes: dict of mode-key → override value. Keys like 'color:dark'.
        fallback: alias string for tools that can't compute color-mix.
        description: optional $description.
    """
    token = {
        "$type": "color",
        "$value": default,
    }
    extensions = {}
    if modes:
        extensions["com.opntrntbl.modes"] = modes
    if fallback is not None:
        extensions["com.opntrntbl.fallback"] = {"$value": fallback}
    if extensions:
        token["$extensions"] = extensions
    if description:
        token["$description"] = description
    return token


def dimension_token(default, modes=None, description=None):
    token = {
        "$type": "dimension",
        "$value": default,
    }
    if modes:
        token["$extensions"] = {"com.opntrntbl.modes": modes}
    if description:
        token["$description"] = description
    return token


def number_token(default, modes=None, description=None):
    token = {
        "$type": "number",
        "$value": default,
    }
    if modes:
        token["$extensions"] = {"com.opntrntbl.modes": modes}
    if description:
        token["$description"] = description
    return token


def typography_token(font_size, line_height, font_weight, font_family=None, letter_spacing=None, description=None):
    """Composite $type: 'typography' token."""
    value = {
        "fontSize":   font_size,
        "lineHeight": line_height,
        "fontWeight": font_weight,
    }
    if font_family:
        value["fontFamily"] = font_family
    if letter_spacing:
        value["letterSpacing"] = letter_spacing
    token = {"$type": "typography", "$value": value}
    if description:
        token["$description"] = description
    return token


def transition_token(duration, easing, description=None):
    token = {
        "$type": "transition",
        "$value": {
            "duration":       duration,
            "timingFunction": easing,
        },
    }
    if description:
        token["$description"] = description
    return token


# ---------------------------------------------------------------------------
# Surface — hierarchical backgrounds
# ---------------------------------------------------------------------------
# Light mode follows the iOS/Apple pattern the firmware already uses:
#   canvas (page bg)  < base (card)      — canvas slightly dimmer so cards pop
#   base  < raised    — same value, differentiated by shadow/elevation
#   sunken = canvas-like (inputs feel inset into the page)
# Dark mode inverts with punchier contrast between canvas and base.

SURFACE = {
    "canvas": {
        "default": primitive("color.neutral.190"),
        "modes":   {"color:dark": primitive("color.neutral.0")},
        "desc":    "Page background. Bottom-most surface.",
    },
    "base": {
        "default": primitive("color.neutral.200"),
        "modes":   {"color:dark": primitive("color.neutral.10")},
        "desc":    "Default card / panel surface.",
    },
    "raised": {
        "default": primitive("color.neutral.200"),
        "modes":   {"color:dark": primitive("color.neutral.25")},
        "desc":    "Elevated surface (modal, popover). Usually paired with a shadow.",
    },
    "sunken": {
        "default": primitive("color.neutral.190"),
        "modes":   {"color:dark": primitive("color.neutral.0")},
        "desc":    "Recessed surface (input background, well, code block).",
    },
    "overlay": {
        "default": primitive("color.neutral.0"),
        "modes":   {"color:dark": primitive("color.neutral.0")},
        "desc":    "Scrim / backdrop for modals. Apply via CSS with 0.6 alpha.",
    },
}


# ---------------------------------------------------------------------------
# Border
# ---------------------------------------------------------------------------

BORDER = {
    "subtle": {
        "default": primitive("color.neutral.175"),
        "modes":   {"color:dark": primitive("color.neutral.25")},
        "desc":    "Low-emphasis divider (row separators, group dividers).",
    },
    "default": {
        "default": primitive("color.neutral.150"),
        "modes":   {"color:dark": primitive("color.neutral.50")},
        "desc":    "Standard border (inputs, outlined buttons).",
    },
    "strong": {
        "default": primitive("color.neutral.100"),
        "modes":   {"color:dark": primitive("color.neutral.100")},
        "desc":    "Emphasis border (hover, selected, active).",
    },
    "focus": {
        "default": primitive("color.accent.100"),
        "modes":   {"color:dark": primitive("color.accent.125")},
        "desc":    "Focus ring color. Always visible (accessibility baseline).",
    },
}


# ---------------------------------------------------------------------------
# Accent — brand decorative fill (gold)
# ---------------------------------------------------------------------------
# Used as link color, brand emphasis, binary on-state. Pas un "tone primary"
# partagé entre composants — c'est de l'accent décoratif (cf.
# design/TONE-SHARING-ANALYSIS.md). hover = color-mix(base, white 12%) ;
# pressed pas défini (Donnie pattern : on calcule au point d'usage si besoin).
# Fallback alias pour les outils qui ne savent pas color-mix.

ACCENT = {
    "default": {
        "default": primitive("color.accent.125"),
        "modes":   None,
        "desc":    "Brand accent (gold) — decorative fill (idle). Used as link color, brand emphasis, binary on-state.",
    },
    "hover": {
        "default":  f"color-mix(in oklch, {primitive('color.accent.125')} 88%, #ffffff)",
        "modes":    {"color:dark": f"color-mix(in oklch, {primitive('color.accent.125')} 88%, #ffffff)"},
        "fallback": primitive("color.accent.150"),
        "desc":     "Brand accent (gold) — hover (lightened).",
    },
}


# ---------------------------------------------------------------------------
# Text
# ---------------------------------------------------------------------------

TEXT_COLOR = {
    "primary": {
        "default": primitive("color.neutral.25"),
        "modes":   {"color:dark": primitive("color.neutral.190")},
        "desc":    "Primary text. Body copy, headings.",
    },
    "secondary": {
        "default": primitive("color.neutral.75"),
        "modes":   {"color:dark": primitive("color.neutral.150")},
        "desc":    "Secondary text. Labels, metadata, captions.",
    },
    "placeholder": {
        "default": primitive("color.neutral.125"),
        "modes":   {"color:dark": primitive("color.neutral.100")},
        "desc":    "Placeholder text. Empty-state hints in inputs.",
    },
    "disabled": {
        "default": primitive("color.neutral.150"),
        "modes":   {"color:dark": primitive("color.neutral.75")},
        "desc":    "Disabled text. Controls that can't be interacted with.",
    },
    "inverse": {
        "default": primitive("color.neutral.200"),
        "modes":   {"color:dark": primitive("color.neutral.0")},
        "desc":    "Text on solid/colored surfaces (e.g. white on primary).",
    },
    "accent": {
        "default": primitive("color.accent.75"),
        "modes":   {"color:dark": primitive("color.accent.150")},
        "desc":    "Accent text. Inline links, brand emphasis.",
    },
}


# ---------------------------------------------------------------------------
# Status — hierarchical: status.<role>.<slot>
# ---------------------------------------------------------------------------
# Each status role has two slots: bg, text.
# bg = low-emphasis surface tint; text = readable on bg.
# Pas de slot border : si on veut une border tintée, on la calcule via
# color-mix() sur le bg au point d'usage (Donnie pattern, YAGNI).

def status_triad(role, shade_bg_light, shade_text_light,
                  shade_bg_dark, shade_text_dark, desc_role):
    return {
        "bg": {
            "default": primitive(f"color.{role}.{shade_bg_light}"),
            "modes":   {"color:dark": primitive(f"color.{role}.{shade_bg_dark}")},
            "desc":    f"{desc_role} — background tint.",
        },
        "text": {
            "default": primitive(f"color.{role}.{shade_text_light}"),
            "modes":   {"color:dark": primitive(f"color.{role}.{shade_text_dark}")},
            "desc":    f"{desc_role} — text on the tint.",
        },
    }


STATUS = {
    "success": status_triad("success", "190", "50",
                             "10", "175",
                             "Success state (completed action, OK)"),
    "warning": status_triad("warning", "190", "50",
                             "10", "175",
                             "Warning state (caution, non-blocking issue)"),
    "danger": status_triad("danger",   "190", "50",
                             "10", "175",
                             "Danger state (error, destructive action)"),
    "info":    status_triad("info",    "190", "50",
                             "10", "175",
                             "Info state (neutral notice, informational)"),
}


# ---------------------------------------------------------------------------
# Spacing — density-aware
# ---------------------------------------------------------------------------
# tight / snug / default / loose / airy
# density:compact shrinks by one step; density:spacious expands by one step.

SPACING = {
    "tight": {
        "default": core("dimension.10"),   # 4px
        "modes": {
            "density:compact":  core("dimension.05"),   # 2px
            "density:spacious": core("dimension.15"),   # 6px
        },
        "desc": "Tight gap. Between adjacent visual elements sharing a conceptual unit.",
    },
    "snug": {
        "default": core("dimension.20"),   # 8px
        "modes": {
            "density:compact":  core("dimension.15"),   # 6px
            "density:spacious": core("dimension.25"),   # 10px
        },
        "desc": "Snug gap. Inner padding of controls (buttons, inputs).",
    },
    "default": {
        "default": core("dimension.40"),   # 16px
        "modes": {
            "density:compact":  core("dimension.30"),   # 12px
            "density:spacious": core("dimension.50"),   # 20px
        },
        "desc": "Default gap. Between distinct elements on a surface.",
    },
    "loose": {
        "default": core("dimension.60"),   # 24px
        "modes": {
            "density:compact":  core("dimension.50"),   # 20px
            "density:spacious": core("dimension.80"),   # 32px
        },
        "desc": "Loose gap. Between grouped sections.",
    },
    "airy": {
        "default": core("dimension.100"),  # 40px
        "modes": {
            "density:compact":  core("dimension.80"),   # 32px
            "density:spacious": core("dimension.120"),  # 48px
        },
        "desc": "Airy gap. Major section breaks.",
    },
}


# ---------------------------------------------------------------------------
# Radius
# ---------------------------------------------------------------------------

RADIUS = {
    "sharp":  (core("dimension.01"), "Hairline rounding. Almost-square."),
    "soft":   (core("dimension.10"), "Soft rounding. Inputs, small cards."),
    "round":  (core("dimension.25"), "Rounded. Main surfaces (cards, panels, modals)."),
    "pill":   (core("dimension.240"), "Pill. Full-pill controls, segmented toggles."),
    "circle": ("50%", "Circle. Avatars, round buttons. Applied as raw percentage."),
}


# ---------------------------------------------------------------------------
# Typography — composite tokens
# ---------------------------------------------------------------------------
# Each role pairs font-size + line-height + weight + family.

SANS = primitive("font-family.sans")
MONO = primitive("font-family.mono")


TEXT_TYPOGRAPHY = {
    "caption": typography_token(
        font_size=core("font-size.10"),    # 12px
        line_height=core("line-height.20"),  # 1.2
        font_weight=400,
        font_family=SANS,
        description="Caption. Metadata, legal text.",
    ),
    "small": typography_token(
        font_size=core("font-size.20"),    # 14px
        line_height=core("line-height.30"),  # 1.4
        font_weight=400,
        font_family=SANS,
        description="Small body. Secondary copy, dense UI.",
    ),
    "body": typography_token(
        font_size=core("font-size.30"),    # 16px
        line_height=core("line-height.30"),  # 1.4
        font_weight=400,
        font_family=SANS,
        description="Body. Default reading size.",
    ),
    "body.emphasis": typography_token(
        font_size=core("font-size.30"),
        line_height=core("line-height.30"),
        font_weight=600,
        font_family=SANS,
        description="Body emphasis. Same size as body, heavier weight for emphasis.",
    ),
    "subheading": typography_token(
        font_size=core("font-size.50"),    # 20px
        line_height=core("line-height.20"),  # 1.2
        font_weight=600,
        font_family=SANS,
        description="Subheading. Section labels inside a page.",
    ),
    "heading-3": typography_token(
        font_size=core("font-size.60"),    # 24px
        line_height=core("line-height.20"),
        font_weight=700,
        font_family=SANS,
        description="Tertiary heading. Within-section titles.",
    ),
    "heading-2": typography_token(
        font_size=core("font-size.80"),    # 32px
        line_height=core("line-height.10"),  # 1.0
        font_weight=700,
        font_family=SANS,
        description="Secondary heading. Major-section titles.",
    ),
    "heading-1": typography_token(
        font_size=core("font-size.100"),   # 40px
        line_height=core("line-height.10"),
        font_weight=800,
        font_family=SANS,
        description="Primary heading. Page titles.",
    ),
    "display-small": typography_token(
        font_size=core("font-size.120"),   # 48px
        line_height=core("line-height.10"),
        font_weight=800,
        font_family=SANS,
        description="Small display. Marketing or hero subtitles.",
    ),
    "display-large": typography_token(
        font_size=core("font-size.160"),   # 64px
        line_height=core("line-height.10"),
        font_weight=800,
        font_family=SANS,
        description="Large display. Hero titles.",
    ),
    "code": typography_token(
        font_size=core("font-size.20"),    # 14px
        line_height=core("line-height.30"),
        font_weight=400,
        font_family=MONO,
        description="Monospace code / stream URLs / log output.",
    ),
}


# ---------------------------------------------------------------------------
# Motion — intent-based transitions (composite of duration + easing)
# ---------------------------------------------------------------------------

MOTION = {
    "feedback": transition_token(
        duration=core("duration.fast"),     # 100ms
        easing=core("easing.out"),
        description="Hover, focus ring, micro-feedback.",
    ),
    "state-change": transition_token(
        duration=core("duration.moderate"), # 200ms
        easing=core("easing.in-out"),
        description="Toggle, switch, tab change.",
    ),
    "enter": transition_token(
        duration=core("duration.slow"),     # 400ms
        easing=core("easing.out"),
        description="Element entering (modal, drawer, toast).",
    ),
    "exit": transition_token(
        duration=core("duration.moderate"),
        easing=core("easing.in"),
        description="Element leaving (close modal, dismiss toast).",
    ),
}


# ---------------------------------------------------------------------------
# Icon — size only (stroke-width deliberately not tokenized — see CLAUDE.md)
# ---------------------------------------------------------------------------
# Pas de icon.color : les composants héritent de text.color.* directement
# (currentColor pattern). Les color tokens icon-* étaient des alias morts
# (0 consommateur, tous court-circuités).

ICON = {
    "size.sm":  dimension_token(core("dimension.40"),  description="Small icon. Inline with body text."),   # 16px
    "size.md":  dimension_token(core("dimension.60"),  description="Medium icon. Default control icon."),   # 24px
    "size.lg":  dimension_token(core("dimension.80"),  description="Large icon. Feature blocks, empty states."),  # 32px
}


# ---------------------------------------------------------------------------
# Focus ring — accessibility baseline (always visible)
# ---------------------------------------------------------------------------

FOCUS = {
    "ring.width":  dimension_token(core("dimension.05"), description="Focus ring stroke width."),   # 2px
    "ring.offset": dimension_token(core("dimension.05"), description="Focus ring offset from the element edge."),
    "ring.color":  color_token(self_ref("border.focus"), description="Focus ring color."),
}


# ---------------------------------------------------------------------------
# Assembly
# ---------------------------------------------------------------------------

def _is_leaf_spec(s):
    """True when a dict is a token spec (has a string 'default' = the value itself),
    not a sub-group (where 'default' would be another sub-dict = a role named 'default').
    """
    return isinstance(s, dict) and isinstance(s.get("default"), str)


def build_color_group(spec):
    """Expand a dict of color specs into DTCG tokens."""
    out = {}
    for name, s in spec.items():
        if _is_leaf_spec(s):
            out[name] = color_token(
                default=s["default"],
                modes=s.get("modes"),
                fallback=s.get("fallback"),
                description=s.get("desc"),
            )
        elif isinstance(s, dict):
            out[name] = build_color_group(s)
        else:
            raise ValueError(f"Unexpected shape for {name}: {s!r}")
    return out


def build_dimension_group_from_spec(spec):
    out = {}
    for name, s in spec.items():
        if _is_leaf_spec(s):
            out[name] = dimension_token(
                default=s["default"],
                modes=s.get("modes"),
                description=s.get("desc"),
            )
        elif isinstance(s, dict):
            out[name] = build_dimension_group_from_spec(s)
    return out


def build_radius_group():
    out = {}
    for name, (value, desc) in RADIUS.items():
        out[name] = dimension_token(value, description=desc)
    return out


def set_nested(target, dotted_path, value):
    """Set a value at a dotted path inside a nested dict."""
    parts = dotted_path.split(".")
    node = target
    for p in parts[:-1]:
        node = node.setdefault(p, {})
    node[parts[-1]] = value


def build_flat_group(flat_spec):
    """Build a nested group from a dotted-key spec."""
    out = {}
    for path, token in flat_spec.items():
        set_nested(out, path, token)
    return out


def main():
    semantic = {
        "surface":  build_color_group(SURFACE),
        "border":   build_color_group(BORDER),
        "accent":   build_color_group(ACCENT),
        "text":     {
            "color":      build_color_group(TEXT_COLOR),
            **TEXT_TYPOGRAPHY,
        },
        "status":   build_color_group(STATUS),
        "spacing":  build_dimension_group_from_spec(SPACING),
        "radius":   build_radius_group(),
        "motion":   MOTION,
        "icon":     build_flat_group(ICON),
        "focus":    build_flat_group(FOCUS),
    }

    document = {
        "$schema": "https://www.designtokens.org/schemas/2025.10/format.json",
        "semantic": semantic,
    }

    OUTPUT_FILE.parent.mkdir(parents=True, exist_ok=True)
    OUTPUT_FILE.write_text(json.dumps(document, indent=2) + "\n")

    size = OUTPUT_FILE.stat().st_size
    print(f"Wrote {OUTPUT_FILE.relative_to(Path.cwd())}  ({size:,} bytes)")

    # Token count
    def count(node):
        if isinstance(node, dict):
            if "$type" in node:
                return 1
            return sum(count(v) for v in node.values())
        return 0

    total = count(semantic)
    print(f"Semantic tokens: {total}")
    for group, body in semantic.items():
        print(f"  {group:12s}  {count(body):>3d}")


if __name__ == "__main__":
    main()
