# design/tokens/scripts

Generator and bundler for openTRNTBL design tokens.

## Layout

```
design/tokens/
├── src/                                       editable sources, one file per tier
│   ├── core.tokens.json                       Tier 0 — generated, don't edit by hand
│   ├── primitives-openTRNTBL.tokens.json      Tier 1
│   └── semantic.tokens.json                   Tier 2
├── dist/                                      build artifacts, injectable in tools
│   ├── tokens.json                            DTCG 2025.10 matrix (Figma native, PenPot)
│   └── tokens.studio.json                     hex-string legacy (Tokens Studio plugin)
└── scripts/
    ├── generate-core.py                       produces src/core.tokens.json
    ├── generate-primitives-openTRNTBL.py      produces src/primitives-openTRNTBL.tokens.json
    ├── generate-semantic.py                   produces src/semantic.tokens.json
    ├── bundle.py                              assembles src/* into dist/*
    ├── generate-css.py                        emits dist/tokens.css from semantic
    └── README.md
```

## Typical workflow

```sh
# 1. (Re)generate Tier 0 raw material from scratch
python3 design/tokens/scripts/generate-core.py

# 2. Rebuild both distribution bundles
python3 design/tokens/scripts/bundle.py
```

`generate-core.py` is idempotent. Re-run it whenever you tune the
OKLCH curves, add a hue, or change the shade scale. `bundle.py` reads every
`src/*.tokens.json` and produces the two flavors in `dist/`.

## Distribution flavors — why two

DTCG 2025.10 introduces a new color value shape (`colorSpace`/`components`
matrix), and support landed unevenly:

| Tool | `dist/tokens.json` (matrix) | `dist/tokens.studio.json` (hex) |
|------|-----------------------------|---------------------------------|
| Figma native variables       | OK | OK |
| PenPot (recent)              | OK | OK |
| Tokens Studio (Figma plugin) | **fails** | OK |

Import `dist/tokens.studio.json` into Tokens Studio. Everything else reads
`dist/tokens.json`. When Tokens Studio catches up to DTCG 2025.10, drop the
studio output.

The matrix bundle is the source of truth — the studio bundle is derived by
flattening each color's `$value` to its `hex` fallback. Aliases (e.g.
`{core.dimension.40}`) pass through unchanged.

## Color convention — Fusilier-style

Scale `0 → 200`, **higher = lighter**. Numerical difference between shades
encodes WCAG contrast:

| Difference | Guaranteed ratio |
|-----------|------------------|
| ≥ 75      | ≥ 3:1 — AA UI |
| ≥ 100     | ≥ 4.5:1 — AA text |
| ≥ 150     | ≥ 7:1 — AAA |

The generator validates every pair in every ramp. Regressions fail loudly.

## Add a new hue

1. Edit `generate-core.py`, add to `HUES`:
   ```python
   "teal": {"h": 180, "chroma_peak": 0.14},
   ```
2. Re-run the generator. Validator confirms contrast holds.
3. Run `bundle.py` to refresh `dist/`.

## Calibration notes

- `SHADE_Y_TARGETS` maps each shade to a target WCAG linear luminance (Y),
  calibrated so contrast invariants hold universally across hues.
- For each (hue, shade), the script binary-searches the OKLCH `L` that
  renders to exactly `Y_target` in sRGB. Same WCAG luminance across hues
  ⇒ same contrast ⇒ invariants hold regardless of hue.
- `chroma_envelope` peaks at shade 100 with a 15 % floor at extremes —
  keeps tinted extremes without blowing sRGB gamut. Neutral uses peak 0.
- Out-of-gamut OKLCH colors get chroma reduced by binary search.
