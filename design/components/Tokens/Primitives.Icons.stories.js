// openTRNTBL — Tokens / Primitives / Icons stories (brand-selected device icons).

import { tokens } from './_helpers.js';

export default {
  title: 'Tokens/Primitives/Icons',
  parameters: { layout: 'fullscreen' },
};

export const Gallery = () => {
  const iconSet = tokens.icons;
  const cells = Object.entries(iconSet).map(([name, token]) => {
    const svg = token.$value.svg;
    return `
      <div style="
        background:#fff;border:1px solid #eee;border-radius:8px;
        padding:20px;display:flex;flex-direction:column;align-items:center;gap:12px;
      ">
        <div style="color:#111;width:48px;height:48px">
          ${svg.replace(/width="24"\s+height="24"/, 'width="48" height="48"')}
        </div>
        <div style="font-family:monospace;font-size:12px;font-weight:700">${name}</div>
        <div style="font-size:11px;color:#888;text-align:center;line-height:1.4">${token.$description || ''}</div>
      </div>
    `;
  }).join('');
  return `
    <div style="padding:24px;background:#fafafa;min-height:100vh;font-family:system-ui">
      <h1 style="font-size:20px;margin:0 0 8px;font-weight:800">Icons — icons.*</h1>
      <p style="margin:0 0 24px;color:#666;font-size:13px;max-width:640px">
        9 speaker-type icons. Token format is hybrid: SVG inline for theming via <code>currentColor</code> + fallback <code>src</code> path.
        Stroke-width intrinsic to the source (not tokenized — see decision log).
      </p>
      <div style="display:grid;grid-template-columns:repeat(auto-fill,minmax(180px,1fr));gap:16px">${cells}</div>
    </div>
  `;
};

export const Colored = () => {
  const iconSet = tokens.icons;
  const palette = [
    { bg: '#fff',    fg: '#111',     label: 'neutral.25 on neutral.200' },
    { bg: '#fff',    fg: '#957000',  label: 'gold.100 on neutral.200' },
    { bg: '#1c1c1e', fg: '#d8d8d8',  label: 'neutral.175 on neutral.10' },
    { bg: '#957000', fg: '#fff',     label: 'neutral.200 on gold.100' },
  ];
  const rows = palette.map(p => {
    const cells = Object.entries(iconSet).slice(0, 9).map(([name, token]) => `
      <div style="
        background:${p.bg};color:${p.fg};
        width:64px;height:64px;border-radius:8px;
        display:flex;align-items:center;justify-content:center;
        border:1px solid rgba(0,0,0,0.05);
      ">
        ${token.$value.svg.replace(/width="24"\s+height="24"/, 'width="32" height="32"')}
      </div>
    `).join('');
    return `
      <div style="margin-bottom:20px">
        <h3 style="font-family:monospace;font-size:12px;font-weight:700;margin:0 0 8px;color:#666">${p.label}</h3>
        <div style="display:flex;gap:12px;flex-wrap:wrap">${cells}</div>
      </div>
    `;
  }).join('');
  return `
    <div style="padding:24px;background:#fafafa;min-height:100vh;font-family:system-ui">
      <h1 style="font-size:20px;margin:0 0 8px;font-weight:800">Icons in context</h1>
      <p style="margin:0 0 24px;color:#666;font-size:13px;max-width:640px">
        Icons inherit <code>currentColor</code> — any color token works.
      </p>
      ${rows}
    </div>
  `;
};
