#!/usr/bin/env python3
"""
openTRNTBL — Bundle tier sources into distributable token files.

Reads every *.tokens.json under design/tokens/src/ and produces two outputs
under design/tokens/dist/:

  - tokens.json           DTCG 2025.10 with matrix color values (colorSpace
                          + components). For Figma native variables, PenPot,
                          and any tool supporting the 2025.10 draft.

  - tokens.studio.json    DTCG legacy with color values as hex strings.
                          For Tokens Studio (Figma plugin) which does not
                          yet read the matrix format.

Source files map to token sets by filename:
  core.tokens.json                  -> set "core"
  primitives-openTRNTBL.tokens.json -> set "primitives/openTRNTBL"
  semantic.tokens.json              -> set "semantic"

Set order in $metadata.tokenSetOrder follows TIER_ORDER (core first,
primitives next, semantic last). Unknown sets append after.

Run:
  python3 design/tokens/scripts/bundle.py
"""

import json
from pathlib import Path


SRC_DIR = Path(__file__).resolve().parent.parent / "src"
DIST_DIR = Path(__file__).resolve().parent.parent / "dist"

# Canonical order for $metadata.tokenSetOrder. Unknown files append after.
TIER_ORDER = [
    "core",
    "primitives/openTRNTBL",
    "semantic",
    "icons",
]

# filename stem (without .tokens) -> set name in the bundled document.
FILENAME_TO_SET = {
    "core":                  "core",
    "primitives-openTRNTBL": "primitives/openTRNTBL",
    "semantic":              "semantic",
    "icons":                 "icons",
}


def discover_sources():
    """Return a list of (set_name, path) sorted by TIER_ORDER."""
    pairs = []
    for path in sorted(SRC_DIR.glob("*.tokens.json")):
        stem = path.name[: -len(".tokens.json")]
        set_name = FILENAME_TO_SET.get(stem, stem)
        pairs.append((set_name, path))

    def rank(pair):
        name = pair[0]
        return TIER_ORDER.index(name) if name in TIER_ORDER else len(TIER_ORDER)

    pairs.sort(key=rank)
    return pairs


def load_set_body(path):
    """Read a source file and return its set body.

    Sources are written with a single top-level key matching the set name,
    holding the groups. We return just the body (groups), discarding $schema
    so the bundler owns the envelope.
    """
    doc = json.loads(path.read_text())
    body = {k: v for k, v in doc.items() if not k.startswith("$")}
    if len(body) != 1:
        raise ValueError(
            f"{path.name}: expected exactly one non-meta top-level key, got {list(body.keys())}"
        )
    return next(iter(body.values()))


def build_matrix_bundle(sources):
    """Assemble the DTCG 2025.10 matrix bundle."""
    doc = {
        "$schema": "https://www.designtokens.org/schemas/2025.10/format.json",
    }
    for set_name, path in sources:
        doc[set_name] = load_set_body(path)
    doc["$metadata"] = {"tokenSetOrder": [n for n, _ in sources]}
    doc["$themes"] = []
    return doc


def to_hex_color(node):
    """Recursively convert matrix color values into hex string values.

    A color token in matrix form has:
      {"$type": "color", "$value": {"colorSpace": ..., "components": ...,
                                    "alpha": ..., "hex": "#rrggbb"}, ...}

    We rewrite $value to just the hex string, preserving $description and
    other meta. Non-color nodes are recursed into. Aliases (string $value
    referencing another token) are left untouched.
    """
    if isinstance(node, dict):
        if node.get("$type") == "color" and isinstance(node.get("$value"), dict):
            v = node["$value"]
            hex_val = v.get("hex")
            if hex_val is None:
                raise ValueError("Color token missing hex fallback")
            alpha = v.get("alpha", 1)
            new_value = hex_val if alpha == 1 else _apply_alpha(hex_val, alpha)
            return {**node, "$value": new_value}
        return {k: to_hex_color(v) for k, v in node.items()}
    if isinstance(node, list):
        return [to_hex_color(x) for x in node]
    return node


def _apply_alpha(hex_val, alpha):
    """Return hex with 8-digit alpha channel when alpha < 1."""
    a = max(0, min(255, round(alpha * 255)))
    return f"{hex_val}{a:02x}"


def build_studio_bundle(matrix_bundle):
    """Derive the Tokens Studio-compatible bundle from the matrix bundle."""
    return to_hex_color(matrix_bundle)


def main():
    SRC_DIR.mkdir(parents=True, exist_ok=True)
    DIST_DIR.mkdir(parents=True, exist_ok=True)

    sources = discover_sources()
    if not sources:
        print(f"No source files found under {SRC_DIR.relative_to(Path.cwd())}.")
        print("Run generate-core.py first.")
        return

    matrix = build_matrix_bundle(sources)
    studio = build_studio_bundle(matrix)

    matrix_path = DIST_DIR / "tokens.json"
    studio_path = DIST_DIR / "tokens.studio.json"

    matrix_path.write_text(json.dumps(matrix, indent=2) + "\n")
    studio_path.write_text(json.dumps(studio, indent=2) + "\n")

    print("Sources:")
    for name, path in sources:
        print(f"  {name:24s}  <- {path.relative_to(Path.cwd())}")

    print()
    print("Bundles:")
    for p in (matrix_path, studio_path):
        size = p.stat().st_size
        print(f"  {p.relative_to(Path.cwd())}  ({size:,} bytes)")


if __name__ == "__main__":
    main()
