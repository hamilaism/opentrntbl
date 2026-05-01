// openTRNTBL — Vision modes preview (HC + 4 daltonisms).
//
// Renders the 4 status banners (success / warning / danger / info) under
// each accessibility mode side-by-side, so the impact of vision:* and
// contrast:enhanced is visible at a glance. The toolbar Vision dropdown
// still works for individual story-level previews — this gallery shows
// all modes simultaneously.

import { tokens, resolve, getByPath, contrast, wcagBadge } from './_helpers.js';

export default {
  title: 'Tokens/Semantic/Modes/Vision',
  parameters: { layout: 'fullscreen' },
};

const ROLES = ['success', 'warning', 'danger', 'info'];
const ICON = {
  success: '<svg viewBox="0 0 24 24" width="18" height="18" fill="none" stroke="currentColor" stroke-width="2.5" stroke-linecap="round" stroke-linejoin="round"><path d="M5 12l4 4 10-10"/></svg>',
  warning: '<svg viewBox="0 0 24 24" width="18" height="18" fill="none" stroke="currentColor" stroke-width="2.5" stroke-linecap="round" stroke-linejoin="round"><path d="M12 4v10M12 18v2M3 20h18"/></svg>',
  danger:  '<svg viewBox="0 0 24 24" width="18" height="18" fill="none" stroke="currentColor" stroke-width="2.5" stroke-linecap="round" stroke-linejoin="round"><circle cx="12" cy="12" r="9"/><path d="M8 8l8 8M16 8l-8 8"/></svg>',
  info:    '<svg viewBox="0 0 24 24" width="18" height="18" fill="none" stroke="currentColor" stroke-width="2.5" stroke-linecap="round" stroke-linejoin="round"><circle cx="12" cy="12" r="9"/><path d="M12 8v1M12 12v4"/></svg>',
};
const LABEL = {
  success: 'Connection established',
  warning: 'Audio buffer running low',
  danger:  'Failed to reach Sonos speaker',
  info:    'Streaming paused — no input signal',
};

// Mode catalog — keyed by `data-vision` / `data-contrast` value as it
// appears on <body>. The default trichromat baseline is rendered first
// so the viewer always has a reference.
const VISION_MODES = [
  { key: 'default',       label: 'Default (trichromat)',  desc: 'Baseline. Full hue spectrum.' },
  { key: 'deuteranopia',  label: 'Deuteranopia',          desc: 'No green. Most common (~6% of men). success→cyan, warning→yellow, danger→orange.' },
  { key: 'protanopia',    label: 'Protanopia',            desc: 'No red. ~2% of men. success→blue, warning→yellow, danger→violet, info→cyan.' },
  { key: 'tritanopia',    label: 'Tritanopia',            desc: 'No blue. Very rare (~0.01%). info→violet (only override).' },
  { key: 'achromatopsia', label: 'Achromatopsia',         desc: 'Monochrome (~0.003%). Pure luminance + mandatory icons.' },
];

const CONTRAST_MODES = [
  { key: 'default',  label: 'Default contrast',   desc: 'Baseline AAA on neutrals + status.' },
  { key: 'enhanced', label: 'Enhanced (HC)',      desc: 'Pushed to 13–21:1 ratios. text→shade 25 (light) / 190 (dark), borders to extremes.' },
];

// Resolve a status pair (bg, text) under a given (color, vision, contrast)
// override snapshot. Reads tokens from JSON directly + applies modes
// matching with the same logic as resolveToken (composite '|' keys).
function resolveStatusPair(role, modesOverride) {
  const bgToken = tokens.semantic.status[role].bg;
  const txToken = tokens.semantic.status[role].text;

  const pickValue = (token) => {
    let v = token.$value;
    const overrides = token.$extensions?.['com.opntrntbl.modes'];
    if (overrides) {
      // Best match: longest matching composite key wins.
      let best = null;
      let bestLen = 0;
      for (const [key, override] of Object.entries(overrides)) {
        const terms = key.split('|');
        const allMatch = terms.every(term => {
          const [axis, variant] = term.split(':');
          return modesOverride[axis] === variant;
        });
        if (allMatch && terms.length >= bestLen) {
          best = override;
          bestLen = terms.length;
        }
      }
      if (best != null) v = best;
    }
    return resolve(v, modesOverride);
  };

  return { bg: pickValue(bgToken), text: pickValue(txToken) };
}

// Resolve a semantic token under a modes snapshot (used for the canvas
// context around each mode preview).
function resolveSemantic(path, modesOverride) {
  const token = getByPath(path);
  if (!token) return null;
  let v = token.$value;
  const overrides = token.$extensions?.['com.opntrntbl.modes'];
  if (overrides) {
    let best = null;
    let bestLen = 0;
    for (const [key, override] of Object.entries(overrides)) {
      const terms = key.split('|');
      const allMatch = terms.every(term => {
        const [axis, variant] = term.split(':');
        return modesOverride[axis] === variant;
      });
      if (allMatch && terms.length >= bestLen) {
        best = override;
        bestLen = terms.length;
      }
    }
    if (best != null) v = best;
  }
  return resolve(v, modesOverride);
}

function renderStatusRow(role, bg, text) {
  const ratio = contrast(bg, text);
  const badge = wcagBadge(ratio);
  return `
    <div style="
      background:${bg};color:${text};
      padding:10px 12px;border-radius:6px;margin-bottom:8px;
      display:flex;gap:10px;align-items:center;font-size:12px;
    ">
      <span style="flex-shrink:0;display:inline-flex">${ICON[role]}</span>
      <div style="flex:1;min-width:0">
        <div style="font-weight:600;text-transform:capitalize">${role}</div>
        <div style="font-size:11px;opacity:0.85">${LABEL[role]}</div>
      </div>
      <span title="WCAG contrast ratio ${ratio.toFixed(2)}:1" style="
        background:${badge.color};color:#fff;font-size:10px;
        padding:1px 6px;border-radius:3px;font-weight:700;letter-spacing:0.3px;
      ">${badge.label}</span>
    </div>
  `;
}

function renderModeColumn(title, desc, modes) {
  const canvas = resolveSemantic('semantic.surface.canvas', modes);
  const textPrimary = resolveSemantic('semantic.text.color.primary', modes);
  const textSecondary = resolveSemantic('semantic.text.color.secondary', modes);
  const border = resolveSemantic('semantic.border.subtle', modes);

  const rows = ROLES.map(role => {
    const { bg, text } = resolveStatusPair(role, modes);
    return renderStatusRow(role, bg, text);
  }).join('');

  return `
    <div style="
      background:${canvas};color:${textPrimary};
      border:1px solid ${border};border-radius:8px;
      padding:16px;font-family:system-ui;
    ">
      <div style="font-weight:700;font-size:13px;margin-bottom:4px">${title}</div>
      <div style="font-size:11px;color:${textSecondary};margin-bottom:14px;line-height:1.4">${desc}</div>
      ${rows}
    </div>
  `;
}

function activeBaseModes() {
  // Read the current toolbar state — vision/contrast forced per column,
  // but color (light/dark) and density follow the toolbar globally.
  const b = document.body.dataset;
  return {
    color: b.color || 'light',
    density: b.density || 'default',
  };
}

export const VisionModes = () => {
  const base = activeBaseModes();
  const cols = VISION_MODES.map(m => renderModeColumn(
    m.label,
    m.desc,
    { ...base, vision: m.key, contrast: 'default' }
  )).join('');

  return `
    <div style="padding:24px;font-family:system-ui;background:var(--surface-canvas-background, #f5f5f5);min-height:100vh">
      <h1 style="font-size:18px;margin:0 0 6px;font-weight:800">Vision modes — status palettes side-by-side</h1>
      <p style="margin:0 0 24px;font-size:12px;max-width:820px;color:var(--text-color-secondary, #555)">
        4 daltonism modes + trichromat baseline. Each column applies a different
        <code>data-vision</code> override on the same status.* tokens. Toolbar
        Color (light/dark) is honored — switch it to see dark variants.
        Achromatopsia uses pure luminance + mandatory icons (no color signal).
      </p>
      <div style="display:grid;grid-template-columns:repeat(auto-fit,minmax(240px,1fr));gap:16px">
        ${cols}
      </div>
    </div>
  `;
};

export const ContrastModes = () => {
  const base = activeBaseModes();
  const cols = CONTRAST_MODES.map(m => renderModeColumn(
    m.label,
    m.desc,
    { ...base, vision: 'default', contrast: m.key }
  )).join('');

  return `
    <div style="padding:24px;font-family:system-ui;background:var(--surface-canvas-background, #f5f5f5);min-height:100vh">
      <h1 style="font-size:18px;margin:0 0 6px;font-weight:800">Contrast modes — default vs enhanced (HC)</h1>
      <p style="margin:0 0 24px;font-size:12px;max-width:820px;color:var(--text-color-secondary, #555)">
        Enhanced contrast pushes neutrals to pure extremes (n.0/n.200) and
        status text to shade 25 (light) / 190 (dark) for ratios 13–21:1.
        Cumulable with color:dark via composite mode key.
      </p>
      <div style="display:grid;grid-template-columns:repeat(auto-fit,minmax(280px,1fr));gap:16px">
        ${cols}
      </div>
    </div>
  `;
};
