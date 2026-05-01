"""Build Figma payloads from DTCG bundle for batch import via figma-console MCP.

Outputs (under design/tokens/dist/figma/):
  - core.json         : 156 vars (Default mode), grouped by namespace
  - brand.json        : 99 color aliases + 2 string font-family
                       (alias targets resolved to hex; references rewritten in a 2nd pass after Core seeded)
  - mode-vars.json    : 54 semantic vars × 20 modes (resolved hex / dimension / number)
  - density-vars.json : 5 spacing vars × 3 modes (dimension)
  - excluded.json     : 17 singletons (typography / shadow / transition) - composite, become styles
"""
import json
import os
from pathlib import Path
from collections import defaultdict

REPO = Path(__file__).resolve().parents[3]
SRC = REPO / 'design' / 'tokens' / 'src'
DIST = REPO / 'design' / 'tokens' / 'dist'
OUT = DIST / 'figma'
OUT.mkdir(parents=True, exist_ok=True)

with open(DIST / 'tokens.json') as f:
    bundle = json.load(f)
with open(DIST / 'tokens.modes-matrix.json') as f:
    modes_matrix = json.load(f)
with open(DIST / 'tokens.density-matrix.json') as f:
    density_matrix = json.load(f)
with open(SRC / 'primitives-openTRNTBL.tokens.json') as f:
    raw_brand = json.load(f)
with open(SRC / 'core.tokens.json') as f:
    raw_core = json.load(f)


def walk(obj, prefix=''):
    out = []
    if isinstance(obj, dict):
        if '$value' in obj or '$type' in obj:
            out.append({
                'name': prefix,
                'type': obj.get('$type'),
                'value': obj.get('$value'),
                'desc': obj.get('$description'),
            })
        else:
            for k, v in obj.items():
                if k.startswith('$'):
                    continue
                p = f'{prefix}.{k}' if prefix else k
                out.extend(walk(v, p))
    return out


def color_value_to_hex(v):
    """OKLCH source has $value.hex pre-computed. Strings are passthrough."""
    if isinstance(v, dict) and 'hex' in v:
        return v['hex']
    if isinstance(v, str) and v.startswith('#'):
        return v
    raise ValueError(f'Cannot resolve color: {v!r}')


def dim_to_float_px(v):
    """Convert dimension to px float for Figma FLOAT variables.

    Accepts either DTCG 2025.10 object form ``{"value": 0.25, "unit": "rem"}``
    or a CSS string like ``"0.25rem"`` / ``"8px"``. 1 rem = 16 px (firmware default).
    """
    if isinstance(v, dict) and 'value' in v and 'unit' in v:
        n = float(v['value'])
        u = v['unit']
        if u == 'rem':
            return n * 16.0
        if u == 'px':
            return n
        if u == '%':
            return n
        raise ValueError(f'Unknown dim unit: {u}')
    if isinstance(v, str):
        s = v.strip()
        if s.endswith('rem'):
            return float(s[:-3]) * 16.0
        if s.endswith('px'):
            return float(s[:-2])
        if s.endswith('%'):
            return float(s[:-1])
    if isinstance(v, (int, float)):
        return float(v)
    raise ValueError(f'Cannot resolve dimension: {v!r}')


# -------- CORE --------
core_leaves = [a for a in walk(bundle) if a['name'].startswith('core.')]
# Build alias resolver: ref name → typed leaf
_all_leaves_by_name = {a['name']: a for a in walk(bundle)}


def resolve_alias(value, allow_recurse=True):
    """If value is a "{core.x.y.z}" string, return the resolved $value of the target."""
    if isinstance(value, str) and value.startswith('{') and value.endswith('}'):
        ref = value[1:-1]
        target = _all_leaves_by_name.get(ref)
        if target is None:
            raise KeyError(f'Alias target missing: {ref}')
        # Recurse once if target itself is an alias
        if allow_recurse:
            return resolve_alias(target['value'], allow_recurse=True)
        return target['value']
    return value

core_vars = []
for a in core_leaves:
    name = a['name'][len('core.'):]  # strip "core." prefix → "palette/neutral/0"
    name = name.replace('.', '/')    # Figma uses "/" for hierarchy
    desc = a['desc'] or ''
    if a['type'] == 'color':
        core_vars.append({
            'name': name,
            'resolvedType': 'COLOR',
            'value': color_value_to_hex(a['value']),
            'description': desc,
        })
    elif a['type'] == 'dimension':
        core_vars.append({
            'name': name,
            'resolvedType': 'FLOAT',
            'value': dim_to_float_px(resolve_alias(a['value'])),
            'description': desc + ' (px)',
        })
    elif a['type'] == 'number':
        # opacity 0..1, line-height multiplier
        core_vars.append({
            'name': name,
            'resolvedType': 'FLOAT',
            'value': float(a['value']),
            'description': desc,
        })
    elif a['type'] == 'duration':
        # DTCG 2025.10: {value: 150, unit: 'ms'}, or string "150ms"
        ms = a['value']
        if isinstance(ms, dict) and 'value' in ms:
            v = float(ms['value'])
            u = ms.get('unit', 'ms')
            if u == 's':
                v = v * 1000.0
            ms = v
        elif isinstance(ms, str) and ms.endswith('ms'):
            ms = float(ms[:-2])
        elif isinstance(ms, str) and ms.endswith('s'):
            ms = float(ms[:-1]) * 1000.0
        core_vars.append({
            'name': name,
            'resolvedType': 'FLOAT',
            'value': float(ms),
            'description': desc + ' (ms)',
        })
    elif a['type'] == 'cubicBezier':
        # store as STRING "0.4,0,0.2,1"
        bez = a['value']
        if isinstance(bez, list):
            bez_str = ','.join(str(x) for x in bez)
        else:
            bez_str = str(bez)
        core_vars.append({
            'name': name,
            'resolvedType': 'STRING',
            'value': bez_str,
            'description': desc,
        })
    else:
        print('SKIP core:', a['name'], a['type'])

with open(OUT / 'core.json', 'w') as f:
    json.dump(core_vars, f, indent=2)
print(f'core.json: {len(core_vars)} vars')


# -------- BRAND PRIMITIVES --------
# Source uses {core.palette.gold.0} aliases. We need to keep alias info to rewrite later
# once Core variables exist in Figma (we'll convert string ref → VariableAlias).
raw_brand_leaves = walk(raw_brand)
brand_vars = []
for a in raw_brand_leaves:
    # name: primitives/openTRNTBL.color.accent.0 -> color/accent/0
    name = a['name'][len('primitives/openTRNTBL.'):]
    name = name.replace('.', '/')
    val = a['value']
    desc = a['desc'] or ''

    if a['type'] == 'color':
        # value is "{core.palette.gold.0}"
        if isinstance(val, str) and val.startswith('{') and val.endswith('}'):
            ref = val[1:-1]                              # "core.palette.gold.0"
            ref_figma = ref[len('core.'):].replace('.', '/')  # "palette/gold/0"
            # resolved hex for the FALLBACK literal value (in case binding fails)
            # Look it up in core_vars by name
            fallback = next((c['value'] for c in core_vars if c['name'] == ref_figma), None)
            brand_vars.append({
                'name': name,
                'resolvedType': 'COLOR',
                'value': fallback,                # hex fallback
                'aliasOf': ref_figma,             # we'll bind in pass 2
                'description': desc,
            })
        else:
            print('SKIP brand color (literal):', a['name'], val)
    elif a['type'] == 'fontFamily':
        v = val if isinstance(val, str) else (val[0] if isinstance(val, list) else str(val))
        brand_vars.append({
            'name': name,
            'resolvedType': 'STRING',
            'value': v,
            'description': desc,
        })
    elif a['type'] == 'shadow':
        # composite — Figma effect style, not a variable. Skip here, keep info for excluded list
        pass
    else:
        print('SKIP brand:', a['name'], a['type'])

with open(OUT / 'brand.json', 'w') as f:
    json.dump(brand_vars, f, indent=2)
print(f'brand.json: {len(brand_vars)} vars '
      f'({sum(1 for v in brand_vars if "aliasOf" in v)} aliases, '
      f'{sum(1 for v in brand_vars if "aliasOf" not in v)} literals)')


# -------- MODE (semantic non-density) --------
MODES_ORDER = [
    # 10 prioritized modes (Figma Pro hard cap = 10 modes per collection).
    # Pre-alpha trade-off: drop achromatopsia + HC×vision combos (rare or covered
    # by HC alone). Full 20-mode resolution remains in tokens.css (runtime) and
    # in the Documentation page on Figma.
    'light', 'dark',
    'light-hc', 'dark-hc',
    'light-deutan', 'dark-deutan',
    'light-protan', 'dark-protan',
    'light-tritan', 'dark-tritan',
]

mode_vars = []
semantic_leaves = [a for a in walk(bundle) if a['name'].startswith('semantic.')]
sem_index = {a['name']: a for a in semantic_leaves}

for token_name, info in modes_matrix.items():
    short = token_name[len('semantic.'):].replace('.', '/')
    sem = sem_index.get(token_name, {})
    desc = sem.get('desc') or ''
    if info['type'] == 'color':
        valuesByMode = {}
        for m in MODES_ORDER:
            v = info['values'].get(m)
            if v is None:
                v = info['values'].get('light')  # fallback
            valuesByMode[m] = v
        mode_vars.append({
            'name': short,
            'resolvedType': 'COLOR',
            'valuesByMode': valuesByMode,
            'description': desc,
        })
    elif info['type'] == 'dimension':
        valuesByMode = {}
        for m in MODES_ORDER:
            raw = info['values'].get(m)
            if raw is None:
                raw = info['values'].get('light')
            valuesByMode[m] = dim_to_float_px(raw)
        mode_vars.append({
            'name': short,
            'resolvedType': 'FLOAT',
            'valuesByMode': valuesByMode,
            'description': desc + ' (px)',
        })
    else:
        print('SKIP mode:', token_name, info['type'])

with open(OUT / 'mode-vars.json', 'w') as f:
    json.dump({'modesOrder': MODES_ORDER, 'variables': mode_vars}, f, indent=2)
print(f'mode-vars.json: {len(mode_vars)} vars × {len(MODES_ORDER)} modes')


# -------- DENSITY (semantic spacing) --------
DENSITY_MODES = ['default', 'compact', 'spacious']
density_vars = []
for token_name, info in density_matrix.items():
    short = token_name[len('semantic.'):].replace('.', '/')
    sem = sem_index.get(token_name, {})
    desc = sem.get('desc') or ''
    valuesByMode = {}
    for m in DENSITY_MODES:
        valuesByMode[m] = dim_to_float_px(info['values'][m])
    density_vars.append({
        'name': short,
        'resolvedType': 'FLOAT',
        'valuesByMode': valuesByMode,
        'description': desc + ' (px)',
    })
with open(OUT / 'density-vars.json', 'w') as f:
    json.dump({'modesOrder': DENSITY_MODES, 'variables': density_vars}, f, indent=2)
print(f'density-vars.json: {len(density_vars)} vars × {len(DENSITY_MODES)} modes')


# -------- EXCLUDED (composite types — Figma styles only) --------
excluded = []
for a in semantic_leaves:
    if a['type'] in ('typography', 'shadow', 'transition'):
        excluded.append({
            'name': a['name'],
            'type': a['type'],
            'value': a['value'],
            'description': a['desc'] or '',
        })
with open(OUT / 'excluded.json', 'w') as f:
    json.dump(excluded, f, indent=2)
print(f'excluded.json: {len(excluded)} composite tokens (typography/shadow/transition)')


# -------- BATCH SLICING --------
# Output ready-to-feed batches for figma_batch_create_variables.
# Each batch: list of {name, resolvedType, valuesByMode, description}
# valuesByMode here uses the LOGICAL mode key (string like 'default', 'light').
# The MCP-side caller must rewrite these keys to actual Figma modeIds before calling.

BATCH_DIR = OUT / 'batches'
BATCH_DIR.mkdir(exist_ok=True)


def emit_batches(prefix, items, size, mode_key=None):
    """If mode_key is set (single-mode collection), wrap value into valuesByMode."""
    n = 0
    for i in range(0, len(items), size):
        chunk = items[i:i + size]
        out = []
        for v in chunk:
            base = {
                'name': v['name'],
                'resolvedType': v['resolvedType'],
                'description': v.get('description', ''),
            }
            if 'valuesByMode' in v:
                base['valuesByMode'] = v['valuesByMode']
            elif 'value' in v:
                base['valuesByMode'] = {mode_key or 'default': v['value']}
            if 'aliasOf' in v:
                base['aliasOf'] = v['aliasOf']
            out.append(base)
        path = BATCH_DIR / f'{prefix}-{n:02d}.json'
        with open(path, 'w') as f:
            json.dump(out, f, indent=2)
        n += 1
    return n


n_core = emit_batches('core', core_vars, 25, mode_key='default')
n_brand = emit_batches('brand', brand_vars, 25, mode_key='default')
n_mode = emit_batches('mode', mode_vars, 10)  # 10 vars × 20 modes = 200 values per batch
n_density = emit_batches('density', density_vars, 5)
print(f'\nBatches written: core={n_core}, brand={n_brand}, mode={n_mode}, density={n_density}')

# Also emit one-line minified JSON for each batch (handier to copy-paste into MCP args).
MINI_DIR = OUT / 'batches-mini'
MINI_DIR.mkdir(exist_ok=True)
for path in BATCH_DIR.iterdir():
    if path.suffix != '.json':
        continue
    with open(path) as f:
        data = json.load(f)
    with open(MINI_DIR / path.name, 'w') as f:
        json.dump(data, f, separators=(',', ':'))

print('\nDone.')
