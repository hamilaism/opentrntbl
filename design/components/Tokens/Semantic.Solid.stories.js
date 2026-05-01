// openTRNTBL — Semantic / Accent states stories.
//
// Renamed from Semantic/Solid (2026-04-26) — solid.primary/neutral were
// misnamed: solid.primary served as accent decorative fill, solid.neutral
// was dead code. Cf. design/TONE-SHARING-ANALYSIS.md.

import { tokens, resolveToken, activeModes } from './_helpers.js';

export default {
  title: 'Tokens/Semantic/Accent',
  parameters: { layout: 'fullscreen' },
};

export const States = () => {
  const modes = activeModes();
  const canvas = resolveToken(tokens.semantic.surface.canvas, modes);
  const base = resolveToken(tokens.semantic.surface.base, modes);
  const textPrimary = resolveToken(tokens.semantic.text.color.primary, modes);
  const textSecondary = resolveToken(tokens.semantic.text.color.secondary, modes);

  const idle = resolveToken(tokens.semantic.accent.default, modes);
  const hover = resolveToken(tokens.semantic.accent.hover, modes);
  // Accent fill (gold) — text reads as #000 since gold is light enough.
  const textOnFill = '#000';

  return `
    <div style="background:${canvas};min-height:100vh;padding:24px;font-family:system-ui;color:${textPrimary}">
      <h1 style="font-size:20px;margin:0 0 8px;font-weight:800">Brand accent — semantic.accent.*</h1>
      <p style="margin:0 0 24px;color:${textSecondary};font-size:13px;max-width:640px">
        Hover is computed via <code>color-mix()</code> from the base color (12 % white).
        Fallback alias sits in <code>$extensions.com.opentrntbl.fallback</code> for tools that can't compute color-mix.
        Pressed not defined — calculated via <code>color-mix()</code> at point of use if needed (Donnie pattern).
      </p>
      <div style="background:${base};padding:20px;border-radius:10px;margin-bottom:16px">
        <div style="font-family:monospace;font-size:11px;color:${textSecondary};margin-bottom:8px;text-transform:uppercase;letter-spacing:0.08em">brand accent (gold) — decorative fill</div>
        <div style="display:flex;gap:12px;align-items:center;flex-wrap:wrap">
          <button style="background:${idle};color:${textOnFill};border:none;padding:12px 20px;border-radius:8px;font-size:14px;font-weight:600;cursor:pointer">
            Default
          </button>
          <button style="background:${hover};color:${textOnFill};border:none;padding:12px 20px;border-radius:8px;font-size:14px;font-weight:600;cursor:pointer">
            Hover
          </button>
        </div>
        <div style="font-family:monospace;font-size:11px;color:${textSecondary};margin-top:12px">
          default <code>${idle}</code><br/>
          hover <code>${hover}</code>
        </div>
      </div>
    </div>
  `;
};
