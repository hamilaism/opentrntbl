// openTRNTBL — Tokens / Core / Colors stories.

import { tokens, contrast as wcagContrast, wcagBadge } from './_helpers.js';

export default {
  title: 'Tokens/Core/Colors',
  parameters: { layout: 'fullscreen', a11y: { config: { rules: [{ id: 'color-contrast', enabled: false }, { id: 'empty-table-header', enabled: false }] } } },
};

const SHADES = [0, 10, 25, 50, 75, 100, 125, 150, 175, 190, 200];

// ---------------------------------------------------------------------------
// Palette — all 9 hues x 11 shades
// ---------------------------------------------------------------------------

// Shared swatch geometry — same height/padding for Core + Primitives stories.
// Width is driven by the parent grid (1fr per column).
const SWATCH_HEIGHT = 112;
const SWATCH_PADDING = '14px 12px';
const SWATCH_RADIUS = 6;
const SWATCH_GAP = 4;

function swatch(hue, shade, hex, L, C, H, description) {
  // Text color choice: dark shades (<=100) -> white, light (>=100) -> black-ish
  const textOnSwatch = shade >= 100 ? '#111' : '#f5f5f5';
  const ratio = wcagContrast(hex, textOnSwatch);
  const badge = wcagBadge(ratio);
  return `
    <div style="
      background:${hex};
      color:${textOnSwatch};
      padding:${SWATCH_PADDING};
      border-radius:${SWATCH_RADIUS}px;
      display:flex;flex-direction:column;gap:4px;
      font-family:'SF Mono', Menlo, monospace;font-size:11px;line-height:1.3;
      height:${SWATCH_HEIGHT}px;justify-content:space-between;
      box-sizing:border-box;overflow:hidden;
    ">
      <div style="display:flex;justify-content:space-between;align-items:start;gap:8px">
        <span style="font-weight:700;font-size:13px">${hue}·${shade}</span>
        <span style="background:${badge.color};color:#fff;padding:1px 6px;border-radius:3px;font-weight:600;font-size:10px;flex-shrink:0">
          ${badge.label} ${ratio.toFixed(1)}
        </span>
      </div>
      <div style="opacity:0.85">
        <div>${hex}</div>
        <div style="font-size:10px">L ${L.toFixed(2)} · C ${C.toFixed(3)} · H ${H}</div>
      </div>
    </div>
  `;
}

function hueRow(hue, ramp) {
  const cells = SHADES.map(s => {
    const k = String(s);
    const token = ramp[k];
    const v = token.$value;
    return swatch(hue, s, v.hex, v.components[0], v.components[1], v.components[2], token.$description);
  }).join('');

  return `
    <div style="margin-bottom:20px">
      <h2 style="font-family:system-ui;font-size:14px;font-weight:700;margin:0 0 8px;text-transform:uppercase;letter-spacing:0.08em">${hue}</h2>
      <div style="display:grid;grid-template-columns:repeat(${SHADES.length}, minmax(0, 1fr));gap:${SWATCH_GAP}px">
        ${cells}
      </div>
    </div>
  `;
}

export const Palette = () => {
  const palette = tokens.core.palette;
  const hues = Object.keys(palette);
  return `
    <div style="padding:24px;background:#fafafa;min-height:100vh;font-family:system-ui">
      <h1 style="font-size:20px;margin:0 0 8px;font-weight:800">Palette — core.palette.*</h1>
      <p style="margin:0 0 24px;color:#666;font-size:13px;max-width:640px">
        9 hues × 11 shades. Scale 0 → 200, <strong>higher = lighter</strong>. Numerical difference between shades encodes WCAG contrast:
        diff ≥ 75 = AA UI (≥3:1), diff ≥ 100 = AA text (≥4.5:1), diff ≥ 150 = AAA (≥7:1). Badges show contrast vs the text color picked here.
      </p>
      ${hues.map(h => hueRow(h, palette[h])).join('')}
    </div>
  `;
};

// ---------------------------------------------------------------------------
// Contrast matrix — demonstrates the Fusilier invariant visually
// ---------------------------------------------------------------------------

export const ContrastMatrix = () => {
  const palette = tokens.core.palette;
  const hue = 'neutral'; // showcase with neutral
  const ramp = palette[hue];
  const headers = SHADES.map(s => `<th scope="col" style="padding:6px;font-size:11px;font-weight:700;text-align:center;font-family:monospace">${s}</th>`).join('');
  const rows = SHADES.map(s1 => {
    const k1 = String(s1);
    const hex1 = ramp[k1].$value.hex;
    const cells = SHADES.map(s2 => {
      const k2 = String(s2);
      const hex2 = ramp[k2].$value.hex;
      const ratio = wcagContrast(hex1, hex2);
      const badge = wcagBadge(ratio);
      return `
        <td style="
          padding:6px;text-align:center;font-family:monospace;font-size:10px;
          background:${badge.color};color:#fff;font-weight:600;
        ">
          ${ratio.toFixed(1)}
        </td>
      `;
    }).join('');
    return `
      <tr>
        <th scope="row" style="padding:6px;text-align:right;font-size:11px;font-weight:700;font-family:monospace">${s1}</th>
        ${cells}
      </tr>
    `;
  }).join('');

  return `
    <div style="padding:24px;background:#fafafa;min-height:100vh;font-family:system-ui">
      <h1 style="font-size:20px;margin:0 0 8px;font-weight:800">Contrast matrix — neutral</h1>
      <p style="margin:0 0 16px;color:#666;font-size:13px;max-width:640px">
        WCAG contrast ratio of every pair in the neutral ramp. Green = AAA (≥7), teal = AA (≥4.5), orange = AA UI only (≥3), red = fails.
        <br/><strong>All pairs separated by ≥100 should be at least AA.</strong>
      </p>
      <table style="border-collapse:collapse;background:#fff;box-shadow:0 1px 3px rgba(0,0,0,0.1)">
        <thead>
          <tr>
            <th scope="col" aria-label="Shade"></th>
            ${headers}
          </tr>
        </thead>
        <tbody>${rows}</tbody>
      </table>
    </div>
  `;
};
