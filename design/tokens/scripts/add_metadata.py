#!/usr/bin/env python3
"""
openTRNTBL — One-shot patch : ajoute le bloc $extensions.com.opntrntbl.* à
tous les leaf tokens des 3 sources (core, primitives, semantic).

Schéma DTCG `$extensions.com.opntrntbl` :
  {
    "com.opntrntbl.deprecated": false,
    "com.opntrntbl.varies":     "stable" | "varies" | "undecided",
    "com.opntrntbl.scope":      []   # axes : ["mode", "state", "density", "brand", ...]
  }

Règles d'initialisation (cf. project_ds_token_metadata.md) :

- **core** : tous "stable, []" — la matière première brute est par
  définition immuable, c'est son rôle.
- **primitives/openTRNTBL.color.*** : aliases 1:1 sur core.palette.* —
  pas de mode override propre, donc "stable, []". La variance est portée
  au niveau semantic.
- **primitives/openTRNTBL.font-family.*** : "stable, []".
- **semantic.*** : auto-détection. Si le token contient
  `$extensions.com.opntrntbl.modes` → on extrait les axes présents
  (`color`, `density`, ...) et on marque "varies" + `scope: [<axes>]`.
  Sinon → "undecided, []" pour audit ultérieur (state, brand, etc.).

Idempotent : ré-exécuté, ne réécrit pas les blocs déjà présents (sauf
tokens explicitement opt-out).

Usage :
    python3 design/tokens/scripts/add_metadata.py
"""

from __future__ import annotations

import json
from pathlib import Path


SRC_DIR = Path(__file__).resolve().parent.parent / "src"

FILES = {
    "core":                  SRC_DIR / "core.tokens.json",
    "primitives/openTRNTBL": SRC_DIR / "primitives-openTRNTBL.tokens.json",
    "semantic":              SRC_DIR / "semantic.tokens.json",
}


def is_leaf(node):
    """A leaf token has both $type and $value."""
    return isinstance(node, dict) and "$type" in node and "$value" in node


# Mapping interne (clés des modes dans le JSON) -> vocabulaire canonique
# de la metadata (cf. project_ds_token_metadata.md).
#   color   -> mode    (axe light/dark)
#   density -> density
# (state, brand : pas encore présents dans les modes du JSON.)
AXIS_RENAME = {
    "color": "mode",
}


def detect_axes(node):
    """Extract the axes list from $extensions.com.opntrntbl.modes keys.

    A mode key looks like 'color:dark' or 'density:compact|color:dark'. We
    split on '|' and ':' to collect axis names, then map them to the
    canonical metadata vocabulary (mode, state, density, brand).
    """
    ext = node.get("$extensions", {}) or {}
    modes = ext.get("com.opntrntbl.modes", {}) or {}
    axes = set()
    for key in modes.keys():
        for term in key.split("|"):
            if ":" in term:
                raw_axis = term.split(":", 1)[0]
                axes.add(AXIS_RENAME.get(raw_axis, raw_axis))
    return sorted(axes)


def make_metadata(varies, scope, deprecated=False):
    return {
        "com.opntrntbl.deprecated": deprecated,
        "com.opntrntbl.varies":     varies,
        "com.opntrntbl.scope":      scope,
    }


def attach_metadata(node, varies, scope, deprecated=False):
    """Insert $extensions.com.opntrntbl.* into a leaf token. Preserve
    existing $extensions entries (modes, fallback, etc.)."""
    ext = node.setdefault("$extensions", {})
    # Skip if already present — idempotent.
    if "com.opntrntbl.deprecated" in ext and "com.opntrntbl.varies" in ext:
        return False
    meta = make_metadata(varies, scope, deprecated)
    ext.update(meta)
    return True


def walk_core(node):
    """All leaves are 'stable, []'."""
    count = 0
    if is_leaf(node):
        if attach_metadata(node, "stable", []):
            count += 1
        return count
    if isinstance(node, dict):
        for k, v in node.items():
            if k.startswith("$"):
                continue
            count += walk_core(v)
    return count


def walk_primitives(node):
    """All leaves are 'stable, []' (color aliases + font-family)."""
    count = 0
    if is_leaf(node):
        if attach_metadata(node, "stable", []):
            count += 1
        return count
    if isinstance(node, dict):
        for k, v in node.items():
            if k.startswith("$"):
                continue
            count += walk_primitives(v)
    return count


def walk_semantic(node):
    """Auto-detect axes from existing modes block. If none → undecided."""
    count_varies = 0
    count_undecided = 0
    if is_leaf(node):
        axes = detect_axes(node)
        if axes:
            if attach_metadata(node, "varies", axes):
                count_varies += 1
        else:
            if attach_metadata(node, "undecided", []):
                count_undecided += 1
        return count_varies, count_undecided
    if isinstance(node, dict):
        for k, v in node.items():
            if k.startswith("$"):
                continue
            cv, cu = walk_semantic(v)
            count_varies += cv
            count_undecided += cu
    return count_varies, count_undecided


def patch_file(path, walker):
    doc = json.loads(path.read_text())
    result = walker(doc)
    path.write_text(json.dumps(doc, indent=2) + "\n")
    return result


def main():
    print(f"Patching {FILES['core'].name} ...")
    n = patch_file(FILES["core"], walk_core)
    print(f"  {n:>4d} leaves marked stable.")

    print(f"Patching {FILES['primitives/openTRNTBL'].name} ...")
    n = patch_file(FILES["primitives/openTRNTBL"], walk_primitives)
    print(f"  {n:>4d} leaves marked stable.")

    print(f"Patching {FILES['semantic'].name} ...")
    cv, cu = patch_file(FILES["semantic"], walk_semantic)
    print(f"  {cv:>4d} leaves marked varies (axes auto-detected).")
    print(f"  {cu:>4d} leaves marked undecided (à auditer).")


if __name__ == "__main__":
    main()
