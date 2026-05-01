// openTRNTBL — Semantic / Text stories.

import { tokens, resolveToken, resolveTypography, activeModes } from './_helpers.js';

export default {
  title: 'Tokens/Semantic/Text',
  parameters: { layout: 'fullscreen' },
};

const TYPE_ROLES = [
  'display-large', 'display-small',
  'heading-1', 'heading-2', 'heading-3',
  'subheading',
  'body', 'body.emphasis',
  'small', 'caption',
  'code',
];

export const TypographyScale = () => {
  const modes = activeModes();
  const canvas = resolveToken(tokens.semantic.surface.canvas, modes);
  const base = resolveToken(tokens.semantic.surface.base, modes);
  const textPrimary = resolveToken(tokens.semantic.text.color.primary, modes);
  const textSecondary = resolveToken(tokens.semantic.text.color.secondary, modes);

  const rows = TYPE_ROLES.map(role => {
    // Keys like "body.emphasis" are stored as flat literal keys — look up directly.
    const node = tokens.semantic.text[role];
    if (!node || !node.$value) return '';
    const style = resolveTypography(node);
    const styleStr = Object.entries(style).map(([k, v]) => `${k.replace(/([A-Z])/g, '-$1').toLowerCase()}:${v}`).join(';');
    return `
      <div style="background:${base};padding:20px 24px;border-radius:10px;margin-bottom:12px">
        <div style="font-family:monospace;font-size:11px;color:${textSecondary};margin-bottom:8px;text-transform:uppercase;letter-spacing:0.08em">
          text.${role}
        </div>
        <div style="${styleStr};color:${textPrimary}">
          The quick brown fox jumps over the lazy dog
        </div>
        <div style="font-family:monospace;font-size:11px;color:${textSecondary};margin-top:8px">
          ${style.fontSize} · lh ${style.lineHeight} · weight ${style.fontWeight}
        </div>
      </div>
    `;
  }).join('');

  return `
    <div style="background:${canvas};min-height:100vh;padding:24px;font-family:system-ui;color:${textPrimary}">
      <h1 style="font-size:20px;margin:0 0 8px;font-weight:800">Typography — semantic.text.*</h1>
      <p style="margin:0 0 24px;color:${textSecondary};font-size:13px;max-width:640px">
        Composite tokens (<code>$type: "typography"</code>) pairing font-size + line-height + weight + family. Sizes come from the dimension scale.
      </p>
      ${rows}
    </div>
  `;
};

export const ColorVariants = () => {
  const modes = activeModes();
  const canvas = resolveToken(tokens.semantic.surface.canvas, modes);
  const base = resolveToken(tokens.semantic.surface.base, modes);
  const textSecondary = resolveToken(tokens.semantic.text.color.secondary, modes);

  const variants = [
    { key: 'primary',     label: 'Primary — body copy, headings' },
    { key: 'secondary',   label: 'Secondary — labels, metadata' },
    { key: 'placeholder', label: 'Placeholder — input hints' },
    { key: 'disabled',    label: 'Disabled — muted, non-interactive' },
    { key: 'accent',      label: 'Accent — inline links, emphasis' },
  ];

  const rows = variants.map(v => {
    const color = resolveToken(tokens.semantic.text.color[v.key], modes);
    return `
      <div style="background:${base};padding:16px 20px;border-radius:8px;margin-bottom:10px">
        <div style="font-family:monospace;font-size:11px;color:${textSecondary};margin-bottom:6px">text.color.${v.key} — ${color}</div>
        <div style="font-size:18px;color:${color};font-weight:500">${v.label}</div>
      </div>
    `;
  }).join('');

  // Inverse shown on a brand accent surface
  const primaryFill = resolveToken(tokens.semantic.accent.default, modes);
  const inverse = resolveToken(tokens.semantic.text.color.inverse, modes);

  return `
    <div style="background:${canvas};min-height:100vh;padding:24px;font-family:system-ui">
      <h1 style="font-size:20px;margin:0 0 8px;font-weight:800;color:${resolveToken(tokens.semantic.text.color.primary, modes)}">Text color variants</h1>
      <p style="margin:0 0 24px;color:${textSecondary};font-size:13px;max-width:640px">
        Six color roles. <code>inverse</code> shown below on a solid primary fill.
      </p>
      ${rows}
      <div style="background:${primaryFill};padding:16px 20px;border-radius:8px;margin-top:10px">
        <div style="font-family:monospace;font-size:11px;color:${inverse};opacity:0.8;margin-bottom:6px">text.color.inverse on accent.default — ${inverse}</div>
        <div style="font-size:18px;color:${inverse};font-weight:600">Inverse — text on solid colored surfaces</div>
      </div>
    </div>
  `;
};
