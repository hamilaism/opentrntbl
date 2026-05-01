// openTRNTBL — Tokens / Core / Dimensions stories.

import { tokens, dimValue } from './_helpers.js';

export default {
  title: 'Tokens/Core/Dimensions',
  parameters: { layout: 'fullscreen' },
};

export const Scale = () => {
  const dim = tokens.core.dimension;
  const entries = Object.entries(dim).sort((a, b) => {
    // Sort by numeric value
    const va = a[1].$value;
    const vb = b[1].$value;
    return (va.value * (va.unit === 'rem' ? 16 : 1)) - (vb.value * (vb.unit === 'rem' ? 16 : 1));
  });

  const rows = entries.map(([key, token]) => {
    const v = token.$value;
    const px = Math.round(v.value * (v.unit === 'rem' ? 16 : 1) * 100) / 100;
    const rem = v.unit === 'rem' ? v.value : v.value / 16;
    const bar = `<div style="
      background:#c8a96e;
      height:16px;
      width:${Math.max(px, 2)}px;
      max-width:320px;
      border-radius:2px;
    "></div>`;
    return `
      <tr style="border-bottom:1px solid #eee">
        <td style="padding:8px 12px;font-family:monospace;font-size:12px;font-weight:700;color:#666">${key}</td>
        <td style="padding:8px 12px;font-family:monospace;font-size:12px">${rem}rem</td>
        <td style="padding:8px 12px;font-family:monospace;font-size:12px;color:#888">${px}px</td>
        <td style="padding:8px 12px;width:100%">${bar}</td>
        <td style="padding:8px 12px;font-size:12px;color:#888;font-style:italic">${token.$description || ''}</td>
      </tr>
    `;
  }).join('');

  return `
    <div style="padding:24px;background:#fafafa;min-height:100vh;font-family:system-ui">
      <h1 style="font-size:20px;margin:0 0 8px;font-weight:800">Dimension scale — core.dimension.*</h1>
      <p style="margin:0 0 24px;color:#666;font-size:13px;max-width:640px">
        22 tokens, all in rem (base 16px). Index × 0.025 = value in rem.
        Token <code>40</code> is <strong>1rem</strong> = the typographic baseline.
        Bars truncated at 320px for readability; actual values may be larger.
      </p>
      <table style="background:#fff;border-collapse:collapse;box-shadow:0 1px 3px rgba(0,0,0,0.1);width:100%">
        <thead>
          <tr style="background:#fafafa;text-align:left;border-bottom:2px solid #ddd">
            <th style="padding:10px 12px;font-size:11px;font-weight:700;text-transform:uppercase;letter-spacing:0.08em">Token</th>
            <th style="padding:10px 12px;font-size:11px;font-weight:700;text-transform:uppercase;letter-spacing:0.08em">rem</th>
            <th style="padding:10px 12px;font-size:11px;font-weight:700;text-transform:uppercase;letter-spacing:0.08em">px</th>
            <th style="padding:10px 12px;font-size:11px;font-weight:700;text-transform:uppercase;letter-spacing:0.08em">Visual</th>
            <th style="padding:10px 12px;font-size:11px;font-weight:700;text-transform:uppercase;letter-spacing:0.08em">Note</th>
          </tr>
        </thead>
        <tbody>${rows}</tbody>
      </table>
    </div>
  `;
};

export const Opacity = () => {
  const op = tokens.core.opacity;
  const entries = Object.entries(op).sort((a, b) => a[1].$value - b[1].$value);
  const cells = entries.map(([key, token]) => {
    const v = token.$value;
    return `
      <div style="
        background:linear-gradient(45deg,#eee 25%,transparent 25%,transparent 75%,#eee 75%,#eee), linear-gradient(45deg,#eee 25%,transparent 25%,transparent 75%,#eee 75%,#eee) #fff;
        background-size:16px 16px;background-position:0 0, 8px 8px;
        padding:4px;border-radius:6px;
      ">
        <div style="
          background:#111;opacity:${v};
          width:96px;height:96px;border-radius:4px;
          display:flex;align-items:center;justify-content:center;
          color:#fff;font-family:monospace;font-size:12px;font-weight:700;
        ">
          ${key}
        </div>
        <div style="padding:8px 4px;font-family:monospace;font-size:11px;color:#666;text-align:center">${Math.round(v * 100)}%</div>
      </div>
    `;
  }).join('');
  return `
    <div style="padding:24px;background:#fafafa;min-height:100vh;font-family:system-ui">
      <h1 style="font-size:20px;margin:0 0 8px;font-weight:800">Opacity scale — core.opacity.*</h1>
      <p style="margin:0 0 24px;color:#666;font-size:13px;max-width:640px">
        9 steps. Usage: overlays, scrims, disabled states. Names kept numeric (percentage).
      </p>
      <div style="display:flex;gap:16px;flex-wrap:wrap">${cells}</div>
    </div>
  `;
};
