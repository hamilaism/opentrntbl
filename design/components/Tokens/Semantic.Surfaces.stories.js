// openTRNTBL — Semantic / Surfaces stories.

import { tokens, resolveToken, activeModes } from './_helpers.js';

export default {
  title: 'Tokens/Semantic/Surfaces',
  parameters: { layout: 'fullscreen' },
};

export const Hierarchy = () => {
  const modes = activeModes();
  const surf = tokens.semantic.surface;
  const canvas = resolveToken(surf.canvas, modes);
  const base = resolveToken(surf.base, modes);
  const raised = resolveToken(surf.raised, modes);
  const sunken = resolveToken(surf.sunken, modes);
  const textPrimary = resolveToken(tokens.semantic.text.color.primary, modes);
  const textSecondary = resolveToken(tokens.semantic.text.color.secondary, modes);

  return `
    <div style="background:${canvas};min-height:100vh;padding:24px;font-family:system-ui;color:${textPrimary}">
      <h1 style="font-size:20px;margin:0 0 8px;font-weight:800">Surface hierarchy — semantic.surface.*</h1>
      <p style="margin:0 0 24px;color:${textSecondary};font-size:13px;max-width:640px">
        Toggle <strong>Color mode</strong> in the toolbar (top right) to see light ↔ dark. Each surface sits conceptually above the one below it.
      </p>

      <div style="background:${base};padding:24px;border-radius:12px;max-width:720px;margin-bottom:16px">
        <div style="font-family:monospace;font-size:11px;color:${textSecondary};margin-bottom:4px">semantic.surface.base</div>
        <div style="font-size:16px;margin-bottom:16px">Default card / panel surface</div>

        <div style="background:${raised};padding:20px;border-radius:10px;box-shadow:0 2px 8px rgba(0,0,0,0.08)">
          <div style="font-family:monospace;font-size:11px;color:${textSecondary};margin-bottom:4px">semantic.surface.raised</div>
          <div style="font-size:16px;margin-bottom:16px">Elevated (modal, popover, floating)</div>

          <div style="background:${sunken};padding:14px;border-radius:6px">
            <div style="font-family:monospace;font-size:11px;color:${textSecondary};margin-bottom:4px">semantic.surface.sunken</div>
            <div style="font-size:14px">Input background, well, code block</div>
          </div>
        </div>
      </div>

      <div style="max-width:720px;font-size:12px;color:${textSecondary};font-family:monospace">
        canvas ${canvas} · base ${base} · raised ${raised} · sunken ${sunken}
      </div>
    </div>
  `;
};

export const OverlayScrim = () => {
  const modes = activeModes();
  const canvas = resolveToken(tokens.semantic.surface.canvas, modes);
  const base = resolveToken(tokens.semantic.surface.base, modes);
  const raised = resolveToken(tokens.semantic.surface.raised, modes);
  const overlay = resolveToken(tokens.semantic.surface.overlay, modes);
  const textPrimary = resolveToken(tokens.semantic.text.color.primary, modes);
  const textSecondary = resolveToken(tokens.semantic.text.color.secondary, modes);

  return `
    <div style="background:${canvas};min-height:100vh;padding:24px;font-family:system-ui;color:${textPrimary};position:relative">
      <h1 style="font-size:20px;margin:0 0 8px;font-weight:800">Overlay scrim</h1>
      <p style="margin:0 0 16px;color:${textSecondary};font-size:13px">
        Backdrop color <code>${overlay}</code> at 60% alpha with a raised surface on top.
      </p>

      <div style="background:${base};padding:24px;border-radius:12px;max-width:720px;position:relative;overflow:hidden;min-height:280px">
        <div style="font-family:monospace;font-size:11px;color:${textSecondary};margin-bottom:4px">canvas (page bg)</div>
        <div style="font-size:14px;color:${textSecondary}">Content blurred / dimmed by the overlay scrim.</div>

        <div style="
          position:absolute;inset:0;
          background:${overlay};opacity:0.6;
        "></div>

        <div style="
          position:absolute;inset:50% auto auto 50%;transform:translate(-50%, -50%);
          background:${raised};border-radius:12px;padding:24px;min-width:280px;
          box-shadow:0 8px 32px rgba(0,0,0,0.2);
        ">
          <div style="font-family:monospace;font-size:11px;color:${textSecondary};margin-bottom:6px">surface.raised</div>
          <div style="font-size:15px;font-weight:600">Modal content here</div>
        </div>
      </div>
    </div>
  `;
};
