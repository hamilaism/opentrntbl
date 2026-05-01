#!/usr/bin/env python3
"""Generate dist/tokens.css from dist/tokens.json.

Emits **semantic-tier** tokens as CSS custom properties, with mode overrides
under [data-{mode}="{value}"] selectors. Foundations and theme tiers stay
internal to the bundler — not exposed as CSS vars (per Option 2 naming
convention: no tier prefix in CSS var names).

Output: design/tokens/dist/tokens.css

Usage:
    python3 design/tokens/scripts/generate-css.py
"""

from __future__ import annotations

import json
import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent  # design/tokens/
TOKENS_JSON = ROOT / 'dist' / 'tokens.json'
OUTPUT = ROOT / 'dist' / 'tokens.css'

ALIAS_RE = re.compile(r'\{([^{}]+)\}')


# ============================================================================
# Token tree navigation + alias resolution
# ============================================================================

def get_by_path(tokens, path):
    """Walk a dotted path inside the tokens tree.
    Top-level keys may contain slashes (e.g. 'primitives/openTRNTBL'); we
    still split on '.' only — slashes stay intact in the segment name."""
    # Try exact top-level match first (e.g. 'primitives/openTRNTBL')
    for top in tokens:
        if path == top:
            return tokens[top]
        if path.startswith(top + '.'):
            rest = path[len(top) + 1:]
            return _walk(tokens[top], rest.split('.'))
    # Otherwise plain dotted path
    return _walk(tokens, path.split('.'))


def _walk(node, parts):
    for p in parts:
        if isinstance(node, dict):
            node = node.get(p)
            if node is None:
                return None
        else:
            return None
    return node


def _value_for_mode(target, mode_terms):
    """Return the $value to use for a target token given the active mode.
    If the target has a com.opntrntbl.modes override matching mode_terms
    (e.g. (('color','dark'),)), return that override. Otherwise the default $value.
    The override key in the source is a string like 'color:dark' or
    'color:dark|contrast:enhanced' — we match against mode_terms tuples.
    """
    default = target.get('$value')
    if not mode_terms:
        return default
    ext = target.get('$extensions') or {}
    modes = ext.get('com.opntrntbl.modes') or {}
    # Build set of axes present in the active mode for partial-match support:
    # if the active mode is (color=dark, contrast=enhanced) and the target
    # only has 'color:dark', use that. Prefer the longest match.
    best_key = None
    best_len = -1
    active_set = set(mode_terms)
    for key in modes.keys():
        try:
            terms = tuple(tuple(t.split(':', 1)) for t in key.split('|'))
        except Exception:
            continue
        if all(t in active_set for t in terms) and len(terms) > best_len:
            best_key = key
            best_len = len(terms)
    if best_key is not None:
        return modes[best_key]
    return default


def resolve_alias(tokens, value, _seen=None, mode_terms=None):
    """Recursively resolve aliases in a value, propagating the active mode.
    - String "{path}" → resolves to the target's $value (or its mode override
      if mode_terms matches one of its com.opntrntbl.modes entries)
    - String containing {path} fragments (color-mix expressions etc.)
    - mode_terms = tuple of (axis, value) pairs of the currently active mode
      so that semantic→semantic aliases get resolved with the correct override.
    """
    if _seen is None:
        _seen = set()

    if isinstance(value, str):
        # Pure alias reference?
        m = re.fullmatch(r'\{([^{}]+)\}', value.strip())
        if m:
            ref = m.group(1)
            if ref in _seen:
                return value  # cycle guard
            _seen.add(ref)
            target = get_by_path(tokens, ref)
            if target and isinstance(target, dict) and '$value' in target:
                target_value = _value_for_mode(target, mode_terms)
                return resolve_alias(tokens, target_value, _seen, mode_terms)
            return value

        # Embedded references (e.g. color-mix expressions)
        def _replace(m):
            ref = m.group(1)
            if ref in _seen:
                return m.group(0)
            _seen_copy = set(_seen)
            _seen_copy.add(ref)
            target = get_by_path(tokens, ref)
            if not target or not isinstance(target, dict) or '$value' not in target:
                return m.group(0)
            target_value = _value_for_mode(target, mode_terms)
            resolved = resolve_alias(tokens, target_value, _seen_copy, mode_terms)
            return format_value(resolved, target.get('$type', 'color'))
        return ALIAS_RE.sub(_replace, value)

    return value


# ============================================================================
# Type-specific formatters (primitive → CSS value)
# ============================================================================

def format_color(value):
    if isinstance(value, str):
        return value  # already a string (color-mix expression, hex, or oklch literal)
    if isinstance(value, dict):
        cs = value.get('colorSpace', 'oklch')
        comps = value.get('components', [])
        alpha = value.get('alpha', 1)
        if cs == 'oklch' and len(comps) >= 3:
            L, C, H = comps[0], comps[1], comps[2]
            base = f'oklch({_fmt_num(L)} {_fmt_num(C)} {_fmt_num(H)})'
            if alpha < 1:
                return f'oklch({_fmt_num(L)} {_fmt_num(C)} {_fmt_num(H)} / {_fmt_num(alpha)})'
            return base
        return value.get('hex', '#000000')
    return str(value)


def format_dimension(value):
    if isinstance(value, dict):
        return f"{_fmt_num(value.get('value', 0))}{value.get('unit', 'rem')}"
    if isinstance(value, str):
        return value
    return str(value)


def format_duration(value):
    if isinstance(value, dict):
        unit = value.get('unit', 'ms')
        return f"{_fmt_num(value.get('value', 0))}{unit}"
    if isinstance(value, str):
        return value
    return f"{_fmt_num(value)}ms"


def format_easing(value):
    if isinstance(value, list) and len(value) == 4:
        return f"cubic-bezier({', '.join(_fmt_num(v) for v in value)})"
    if isinstance(value, str):
        return value
    return str(value)


def format_number(value):
    if isinstance(value, (int, float)):
        return _fmt_num(value)
    if isinstance(value, str):
        return value
    return str(value)


def format_shadow(value, tokens=None):
    """Convert a DTCG shadow $value into a CSS box-shadow string.

    DTCG 2025.10 allows shadow $value to be either:
      - a single object {color, offsetX, offsetY, blur, spread, inset?}
      - an array of such objects (multi-layer stack)

    Each layer becomes "inset? offsetX offsetY blur spread color", layers
    joined with ", ". Empty array → "none" (flat / no-op).
    """
    layers = value if isinstance(value, list) else [value]
    if not layers:
        return 'none'

    parts = []
    for layer in layers:
        if not isinstance(layer, dict):
            continue
        color = layer.get('color', '#000000')
        if isinstance(color, str) and tokens is not None:
            color = format_color(resolve_alias(tokens, color))
        elif isinstance(color, dict):
            color = format_color(color)
        ox = format_dimension(layer.get('offsetX', '0'))
        oy = format_dimension(layer.get('offsetY', '0'))
        bl = format_dimension(layer.get('blur', '0'))
        sp = format_dimension(layer.get('spread', '0'))
        prefix = 'inset ' if layer.get('inset') else ''
        parts.append(f'{prefix}{ox} {oy} {bl} {sp} {color}')
    return ', '.join(parts) if parts else 'none'


def _fmt_num(n):
    if isinstance(n, (int, float)):
        if float(n).is_integer():
            return str(int(n))
        return f"{n:g}"
    return str(n)


def format_value(value, type_, tokens=None):
    if type_ == 'color':
        return format_color(value)
    if type_ == 'dimension':
        return format_dimension(value)
    if type_ == 'duration':
        return format_duration(value)
    if type_ == 'cubicBezier':
        return format_easing(value)
    if type_ == 'number' or type_ == 'opacity':
        return format_number(value)
    if type_ == 'shadow':
        return format_shadow(value, tokens)
    if isinstance(value, str):
        return value
    return str(value)


# ============================================================================
# Walk semantic tier and emit CSS vars
# ============================================================================

# Semantic paths to skip from CSS export (composite types we explode separately)
COMPOSITE_TYPES = {'typography', 'transition'}


def collect_semantic_vars(tokens):
    """Return list of (var_name, default_value, modes_dict).
    modes_dict: {('color','dark'): override_value, ('density','compact'): ...}
    """
    semantic = tokens.get('semantic', {})
    out = []
    _collect(semantic, [], tokens, out)
    return out


def _collect(node, path, tokens, out):
    if not isinstance(node, dict):
        return

    # Is this a leaf token? ($type + $value present)
    if '$type' in node and '$value' in node:
        type_ = node['$type']
        # Skip composites — handled separately
        if type_ == 'typography':
            _emit_typography(path, node, tokens, out)
            return
        if type_ == 'transition':
            _emit_transition(path, node, tokens, out)
            return

        var_name = '--' + '-'.join(path).replace('.', '-')
        default = format_value(resolve_alias(tokens, node['$value']), type_, tokens)

        modes = {}
        ext = node.get('$extensions', {})
        modes_ext = ext.get('com.opntrntbl.modes', {}) or {}
        for mode_key, override in modes_ext.items():
            # mode_key looks like 'color:dark', 'density:compact', or a
            # composite 'color:dark|contrast:enhanced' (cumulative axes).
            # Split on '|' to support cross-axis combinations.
            terms = []
            valid = True
            for term in mode_key.split('|'):
                if ':' not in term:
                    valid = False
                    break
                axis, val = term.split(':', 1)
                terms.append((axis, val))
            if not valid or not terms:
                continue
            # Use a tuple-of-tuples as dict key to preserve ordered axes.
            modes[tuple(terms)] = format_value(resolve_alias(tokens, override, mode_terms=tuple(terms)), type_, tokens)

        out.append((var_name, default, modes))
        return

    # Recurse into children (skip $-prefixed keys)
    for key, child in node.items():
        if key.startswith('$'):
            continue
        _collect(child, path + [key], tokens, out)


def _emit_transition(path, node, tokens, out):
    """Explode a $type:transition composite into duration + easing vars."""
    val = node['$value']
    if not isinstance(val, dict):
        return
    base = '--' + '-'.join(path).replace('.', '-')
    if 'duration' in val:
        d = resolve_alias(tokens, val['duration'])
        out.append((f'{base}-duration', format_duration(d), {}))
    if 'timingFunction' in val:
        e = resolve_alias(tokens, val['timingFunction'])
        out.append((f'{base}-easing', format_easing(e), {}))


def _emit_typography(path, node, tokens, out):
    """Explode a $type:typography composite into individual axis vars."""
    val = node['$value']
    if not isinstance(val, dict):
        return
    base = '--' + '-'.join(path).replace('.', '-')
    axis_map = {
        'fontFamily': 'family',
        'fontSize': 'size',
        'fontWeight': 'weight',
        'lineHeight': 'line-height',
        'letterSpacing': 'letter-spacing',
    }
    for src_key, suffix in axis_map.items():
        if src_key not in val:
            continue
        v = val[src_key]
        resolved = resolve_alias(tokens, v)
        # Determine type for formatter
        if src_key == 'fontFamily':
            formatted = resolved if isinstance(resolved, str) else ', '.join(resolved) if isinstance(resolved, list) else str(resolved)
        elif src_key in ('fontSize', 'lineHeight', 'letterSpacing'):
            formatted = format_dimension(resolved) if isinstance(resolved, (dict, str)) else _fmt_num(resolved)
        else:
            formatted = _fmt_num(resolved) if isinstance(resolved, (int, float)) else str(resolved)
        out.append((f'{base}-{suffix}', formatted, {}))


# ============================================================================
# CSS output
# ============================================================================

def emit_css(vars_):
    """Build a CSS string from the (var, default, modes) tuples."""
    # Group modes by their tuple-of-(axis,value) key. Single-axis keys are
    # 1-tuples, composite keys are N-tuples → emit a multi-attribute selector.
    modes_by_key = {}  # ((axis,val), ...) -> [(var, override), ...]
    root_vars = []

    for var_name, default, modes in vars_:
        root_vars.append((var_name, default))
        for terms, override in modes.items():
            # Skip overrides that match the root value — they'd be a no-op,
            # just bloat. Common case: brand colors (accent) are identical
            # across light/dark, so the dark hover/pressed expressions
            # mixing with #ffffff/#000000 produce the same result both modes.
            if override == default:
                continue
            modes_by_key.setdefault(terms, []).append((var_name, override))

    lines = []
    lines.append('/* openTRNTBL — Generated CSS custom properties from semantic tokens.')
    lines.append(' *')
    lines.append(' * Generated by design/tokens/scripts/generate-css.py from dist/tokens.json.')
    lines.append(' * Do not edit by hand. Run `npm run tokens:build` to regenerate.')
    lines.append(' *')
    lines.append(' * Semantic-tier tokens only (core + primitives stay internal).')
    lines.append(' * Mode overrides via [data-color="dark"], [data-density="compact"|"spacious"], etc.')
    lines.append(' * Composite overrides combine attributes — e.g. dark + enhanced contrast →')
    lines.append(' * [data-color="dark"][data-contrast="enhanced"].')
    lines.append(' */')
    lines.append('')
    lines.append(':root {')
    for var, val in root_vars:
        lines.append(f'  {var}: {val};')
    lines.append('}')
    lines.append('')

    # Mode overrides — sorted for deterministic output. Single-axis keys
    # come first (1-tuple), then composite keys (longer tuples) — guarantees
    # composite selectors win via specificity AND source order.
    def _sort_key(terms):
        return (len(terms), terms)
    for terms in sorted(modes_by_key.keys(), key=_sort_key):
        overrides = modes_by_key[terms]
        selector = ''.join(f'[data-{axis}="{val}"]' for axis, val in terms)
        lines.append(f'{selector} {{')
        for var, ov in overrides:
            lines.append(f'  {var}: {ov};')
        lines.append('}')
        lines.append('')

    return '\n'.join(lines)


def check_unresolved(vars_):
    """Fail loudly if any output value still contains {alias} placeholders.
    Catches cases where a token references a non-leaf node (group with no
    $value) — generator silently passes the input through, producing
    invalid CSS like `--icon-color-default: {semantic.text.primary};`."""
    bad = []
    for var_name, default, modes in vars_:
        if isinstance(default, str) and ALIAS_RE.search(default):
            bad.append((var_name, 'default', default))
        for terms, override in modes.items():
            if isinstance(override, str) and ALIAS_RE.search(override):
                label = '|'.join(f'{a}={v}' for a, v in terms)
                bad.append((var_name, label, override))
    if bad:
        print('ERROR: unresolved aliases (likely pointing to non-leaf nodes):', file=sys.stderr)
        for var_name, mode, val in bad:
            print(f'  {var_name} [{mode}] = {val}', file=sys.stderr)
        sys.exit(1)


def main():
    if not TOKENS_JSON.exists():
        print(f'ERROR: {TOKENS_JSON} not found. Run bundle.py first.', file=sys.stderr)
        sys.exit(1)

    with TOKENS_JSON.open() as f:
        tokens = json.load(f)

    vars_ = collect_semantic_vars(tokens)
    check_unresolved(vars_)
    css = emit_css(vars_)

    OUTPUT.write_text(css)

    print(f'Wrote {OUTPUT}  ({len(css):,} bytes, {len(vars_)} vars)')


if __name__ == '__main__':
    main()
