// openTRNTBL — Semantic / Spacing stories (density-aware).

import { tokens, resolveToken, dimValue, activeModes } from './_helpers.js';

export default {
  title: 'Tokens/Semantic/Spacing',
  parameters: { layout: 'fullscreen' },
};

const ROLES = ['tight', 'snug', 'default', 'loose', 'airy'];

export const Scale = () => {
  const modes = activeModes();
  const canvas = resolveToken(tokens.semantic.surface.canvas, modes);
  const base = resolveToken(tokens.semantic.surface.base, modes);
  const textPrimary = resolveToken(tokens.semantic.text.color.primary, modes);
  const textSecondary = resolveToken(tokens.semantic.text.color.secondary, modes);
  const accentFill = resolveToken(tokens.semantic.accent.default, modes);

  const rows = ROLES.map(role => {
    const token = tokens.semantic.spacing[role];
    const resolved = resolveToken(token, modes);
    const dim = typeof resolved === 'object' ? `${resolved.value}${resolved.unit}` : resolved;
    // Compute the pixel width of the bar (assume rem * 16)
    const barWidth = typeof resolved === 'object' ? resolved.value * 16 : 16;
    return `
      <div style="background:${base};padding:16px 20px;border-radius:8px;margin-bottom:10px">
        <div style="display:flex;justify-content:space-between;align-items:baseline;margin-bottom:8px">
          <div style="font-family:monospace;font-size:12px;font-weight:700">spacing.${role}</div>
          <div style="font-family:monospace;font-size:11px;color:${textSecondary}">${dim}</div>
        </div>
        <div style="background:${accentFill};height:12px;width:${barWidth}px;border-radius:2px"></div>
        <div style="font-size:11px;color:${textSecondary};margin-top:8px">${token.$description || ''}</div>
      </div>
    `;
  }).join('');

  return `
    <div style="background:${canvas};min-height:100vh;padding:24px;font-family:system-ui;color:${textPrimary}">
      <h1 style="font-size:20px;margin:0 0 8px;font-weight:800">Spacing — semantic.spacing.*</h1>
      <p style="margin:0 0 24px;color:${textSecondary};font-size:13px;max-width:640px">
        Density-aware. Toggle <strong>Density</strong> in the toolbar to see compact / comfortable / spacious — all spacings shift one step. Mode <code>default</code> here is "comfortable".
      </p>
      ${rows}
    </div>
  `;
};

export const DensityComparison = () => {
  const modes = activeModes();
  const canvas = resolveToken(tokens.semantic.surface.canvas, modes);
  const base = resolveToken(tokens.semantic.surface.base, modes);
  const textPrimary = resolveToken(tokens.semantic.text.color.primary, modes);
  const textSecondary = resolveToken(tokens.semantic.text.color.secondary, modes);
  const accent = resolveToken(tokens.semantic.accent.default, modes);

  const renderCard = (density) => {
    const spacing = {};
    ROLES.forEach(role => {
      const v = resolveToken(tokens.semantic.spacing[role], { ...modes, density });
      spacing[role] = typeof v === 'object' ? `${v.value}${v.unit}` : v;
    });
    return `
      <div style="background:${base};border-radius:10px;padding:${spacing.default};flex:1">
        <div style="font-family:monospace;font-size:11px;color:${textSecondary};margin-bottom:${spacing.tight};text-transform:uppercase;letter-spacing:0.08em">density: ${density}</div>
        <div style="font-size:18px;font-weight:700;margin-bottom:${spacing.snug}">Heading</div>
        <div style="font-size:14px;color:${textSecondary};margin-bottom:${spacing.loose}">
          A short paragraph to show how reading density feels as the scale shifts. Notice the gap to the action below.
        </div>
        <button style="background:${accent};color:#fff;border:none;padding:${spacing.snug} ${spacing.default};border-radius:6px;font-weight:600;font-size:13px">
          Action
        </button>
      </div>
    `;
  };

  return `
    <div style="background:${canvas};min-height:100vh;padding:24px;font-family:system-ui;color:${textPrimary}">
      <h1 style="font-size:20px;margin:0 0 8px;font-weight:800">Density side-by-side</h1>
      <p style="margin:0 0 24px;color:${textSecondary};font-size:13px;max-width:640px">
        Same content, three densities. Cards adapt to their content height —
        the size delta makes the density choice tangible.
      </p>
      <div style="display:flex;gap:16px;align-items:flex-start">
        ${renderCard('compact')}
        ${renderCard('default')}
        ${renderCard('spacious')}
      </div>
    </div>
  `;
};
