#!/usr/bin/env python3
"""
openTRNTBL — Validate $extensions.com.opntrntbl.* metadata across the 3
source files. Outils de gouvernance du DS.

Vérifie :
  - Cohérence varies/scope :
      * varies = "varies"  -> scope doit être non vide
      * varies = "stable"  -> scope doit être vide
      * varies = "undecided" -> tolérant (scope libre)
  - Présence du bloc com.opntrntbl.* sur tous les leaves (manquant = warning).

Liste :
  - tous les tokens marqués "undecided" (pour priorisation audit)
  - tous les tokens marqués "deprecated: true" (à grep dans
    design/components/ pour vérifier qu'ils ne sont plus consommés)

Usage :
    python3 design/tokens/scripts/validate_metadata.py

Exit code : 0 si OK (warnings tolérés), 1 si incohérences bloquantes.
"""

from __future__ import annotations

import json
import sys
from pathlib import Path


SRC_DIR = Path(__file__).resolve().parent.parent / "src"

FILES = {
    "core":                  SRC_DIR / "core.tokens.json",
    "primitives/openTRNTBL": SRC_DIR / "primitives-openTRNTBL.tokens.json",
    "semantic":              SRC_DIR / "semantic.tokens.json",
}


def is_leaf(node):
    return isinstance(node, dict) and "$type" in node and "$value" in node


def walk_leaves(node, path=""):
    """Yield (path, leaf_dict) for every leaf token."""
    if is_leaf(node):
        yield path, node
        return
    if isinstance(node, dict):
        for k, v in node.items():
            if k.startswith("$"):
                continue
            sub = f"{path}.{k}" if path else k
            yield from walk_leaves(v, sub)


def get_metadata(node):
    """Return (deprecated, varies, scope) or None if missing."""
    ext = node.get("$extensions") or {}
    if "com.opntrntbl.varies" not in ext:
        return None
    return (
        ext.get("com.opntrntbl.deprecated", False),
        ext.get("com.opntrntbl.varies"),
        ext.get("com.opntrntbl.scope", []),
    )


def collect():
    """Aggregate per-file leaves with their metadata."""
    out = {}  # file_label -> list of (path, deprecated, varies, scope)
    for label, path in FILES.items():
        doc = json.loads(path.read_text())
        # The top-level key inside the doc holds the body.
        body = {k: v for k, v in doc.items() if not k.startswith("$")}
        if len(body) != 1:
            print(f"WARN {path.name}: expected 1 top-level key, got {list(body.keys())}",
                  file=sys.stderr)
        rows = []
        for body_key, body_val in body.items():
            for token_path, leaf in walk_leaves(body_val):
                meta = get_metadata(leaf)
                rows.append((token_path, leaf, meta))
        out[label] = rows
    return out


def validate(rows_by_file):
    errors = []
    warnings = []

    for file_label, rows in rows_by_file.items():
        for path, leaf, meta in rows:
            full_path = f"{file_label}.{path}"
            if meta is None:
                warnings.append(f"missing com.opntrntbl.* metadata on {full_path}")
                continue
            deprecated, varies, scope = meta

            if varies not in ("stable", "varies", "undecided"):
                errors.append(f"invalid varies value '{varies}' on {full_path}")
                continue

            if varies == "varies" and not scope:
                errors.append(f"varies='varies' but scope=[] on {full_path}")
            elif varies == "stable" and scope:
                errors.append(f"varies='stable' but scope={scope} on {full_path}")

    return errors, warnings


def list_undecided(rows_by_file):
    out = []
    for file_label, rows in rows_by_file.items():
        for path, leaf, meta in rows:
            if meta is None:
                continue
            _, varies, _ = meta
            if varies == "undecided":
                out.append(f"{file_label}.{path}")
    return out


def list_deprecated(rows_by_file):
    out = []
    for file_label, rows in rows_by_file.items():
        for path, leaf, meta in rows:
            if meta is None:
                continue
            deprecated, _, _ = meta
            if deprecated:
                out.append(f"{file_label}.{path}")
    return out


def find_consumers(token_path):
    """Heuristic grep for consumers of a deprecated token in
    design/components/ (CSS var name = '--' + dotted path with dots/slashes
    replaced by '-')."""
    components_dir = Path(__file__).resolve().parent.parent.parent / "components"
    if not components_dir.exists():
        return []
    # Strip 'semantic.' prefix and the '/<theme>' segment for CSS var lookup.
    short = token_path
    for prefix in ("semantic.", "primitives/openTRNTBL.", "core."):
        if short.startswith(prefix):
            short = short[len(prefix):]
            break
    css_var = "--" + short.replace(".", "-").replace("/", "-")
    hits = []
    for f in components_dir.rglob("*"):
        if f.is_file() and f.suffix in (".css", ".js", ".html", ".md"):
            try:
                content = f.read_text()
            except Exception:
                continue
            if css_var in content or token_path in content:
                hits.append(str(f.relative_to(components_dir.parent.parent)))
    return hits


def section(title):
    print()
    print(title)
    print("-" * len(title))


def main():
    rows_by_file = collect()

    total = sum(len(rows) for rows in rows_by_file.values())
    with_meta = sum(1 for rows in rows_by_file.values() for _, _, m in rows if m is not None)

    section("Coverage")
    print(f"  total leaf tokens : {total}")
    print(f"  with com.opntrntbl.* : {with_meta}")
    print(f"  missing           : {total - with_meta}")
    for label, rows in rows_by_file.items():
        with_m = sum(1 for _, _, m in rows if m is not None)
        print(f"    {label:24s}  {with_m:>3d} / {len(rows):>3d}")

    section("Validation")
    errors, warnings = validate(rows_by_file)
    if not errors and not warnings:
        print("  OK — no inconsistencies.")
    else:
        if errors:
            print(f"  ERRORS ({len(errors)}):")
            for e in errors:
                print(f"    - {e}")
        if warnings:
            print(f"  WARNINGS ({len(warnings)}):")
            for w in warnings:
                print(f"    - {w}")

    undecided = list_undecided(rows_by_file)
    section(f"Undecided ({len(undecided)}) — to audit")
    if not undecided:
        print("  none.")
    else:
        for p in undecided:
            print(f"  {p}")

    deprecated = list_deprecated(rows_by_file)
    section(f"Deprecated ({len(deprecated)}) — should not be consumed")
    if not deprecated:
        print("  none.")
    else:
        for p in deprecated:
            consumers = find_consumers(p)
            print(f"  {p}")
            if consumers:
                print(f"    !! still consumed by:")
                for c in consumers:
                    print(f"       {c}")
            else:
                print(f"    OK — no consumer found.")

    sys.exit(1 if errors else 0)


if __name__ == "__main__":
    main()
