// openTRNTBL — Tokens / Core / Motion stories.
//
// Exposes the motion primitives (`core.duration.*` + `core.easing.*`) that
// are composed into `semantic.motion.*` intents. The semantic story
// (Tokens/Semantic/Radius & Motion → Motion) shows the composed intents;
// this story shows the primitives they are built from.
//
// Anti-judder note : the live preview boxes animate on hover of the
// **wrapper card** (the cursor stays on a stable parent), so the moving
// box never escapes from under the cursor.

import { tokens, resolveToken, activeModes } from './_helpers.js';

export default {
  title: 'Tokens/Core/Motion',
  parameters: { layout: 'fullscreen' },
};

// ---------------------------------------------------------------------------
// Durations — `core.duration.*`
// ---------------------------------------------------------------------------
export const Durations = () => {
  const modes = activeModes();
  const canvas = resolveToken(tokens.semantic.surface.canvas, modes);
  const base = resolveToken(tokens.semantic.surface.base, modes);
  const textPrimary = resolveToken(tokens.semantic.text.color.primary, modes);
  const textSecondary = resolveToken(tokens.semantic.text.color.secondary, modes);
  const accent = resolveToken(tokens.semantic.accent.default, modes);

  // Stable easing for these previews (we vary duration only).
  const easingCss = 'cubic-bezier(0, 0, 0.2, 1)';

  const cells = Object.entries(tokens.core.duration).map(([key, token]) => {
    const ms = token.$value.value;
    return `
      <div
        class="motion-card"
        style="
          background:${base};border-radius:10px;padding:24px;flex:1;min-width:240px;
          cursor:pointer;
        "
      >
        <div style="font-family:monospace;font-size:11px;color:${textSecondary};margin-bottom:4px;text-transform:uppercase;letter-spacing:0.08em">core.duration.${key}</div>
        <div style="font-size:16px;font-weight:700;margin-bottom:12px">${key}</div>
        <div style="background:${canvas};border-radius:6px;padding:8px;margin-bottom:12px;overflow:hidden">
          <div
            class="motion-track"
            style="
              width:32px;height:32px;background:${accent};border-radius:6px;
              transition:transform ${ms}ms ${easingCss};
            "
          ></div>
        </div>
        <div style="font-family:monospace;font-size:12px;font-weight:700">${ms}ms</div>
        <div style="font-size:11px;color:${textSecondary};margin-top:4px">${token.$description || ''}</div>
      </div>
    `;
  }).join('');

  return `
    <div style="background:${canvas};min-height:100vh;padding:24px;font-family:system-ui;color:${textPrimary}">
      <h1 style="font-size:20px;margin:0 0 8px;font-weight:800">Duration primitives — core.duration.*</h1>
      <p style="margin:0 0 24px;color:${textSecondary};font-size:13px;max-width:640px">
        5 duration steps. Hover any card (anywhere on it, not just the box) to play the animation —
        the box translates inside its track. <code>semantic.motion.*</code> intents compose these primitives with easings.
      </p>
      <div style="display:flex;gap:16px;flex-wrap:wrap">${cells}</div>
      <style>
        .motion-card:hover .motion-track { transform: translateX(calc(100% - 32px)); }
      </style>
    </div>
  `;
};

// ---------------------------------------------------------------------------
// Easings — `core.easing.*`
// ---------------------------------------------------------------------------
export const Easings = () => {
  const modes = activeModes();
  const canvas = resolveToken(tokens.semantic.surface.canvas, modes);
  const base = resolveToken(tokens.semantic.surface.base, modes);
  const textPrimary = resolveToken(tokens.semantic.text.color.primary, modes);
  const textSecondary = resolveToken(tokens.semantic.text.color.secondary, modes);
  const accent = resolveToken(tokens.semantic.accent.default, modes);

  // Stable duration for these previews (we vary easing only) — slow enough
  // to feel the curve.
  const ms = 600;

  const cells = Object.entries(tokens.core.easing).map(([key, token]) => {
    const cb = token.$value;
    const cssCb = `cubic-bezier(${cb.join(', ')})`;
    return `
      <div
        class="motion-card"
        style="
          background:${base};border-radius:10px;padding:24px;flex:1;min-width:240px;
          cursor:pointer;
        "
      >
        <div style="font-family:monospace;font-size:11px;color:${textSecondary};margin-bottom:4px;text-transform:uppercase;letter-spacing:0.08em">core.easing.${key}</div>
        <div style="font-size:16px;font-weight:700;margin-bottom:12px">${key}</div>
        <div style="background:${canvas};border-radius:6px;padding:8px;margin-bottom:12px;overflow:hidden">
          <div
            class="motion-track"
            style="
              width:32px;height:32px;background:${accent};border-radius:6px;
              transition:transform ${ms}ms ${cssCb};
            "
          ></div>
        </div>
        <div style="font-family:monospace;font-size:11px;font-weight:700">${cssCb}</div>
        <div style="font-size:11px;color:${textSecondary};margin-top:4px">${token.$description || ''}</div>
      </div>
    `;
  }).join('');

  return `
    <div style="background:${canvas};min-height:100vh;padding:24px;font-family:system-ui;color:${textPrimary}">
      <h1 style="font-size:20px;margin:0 0 8px;font-weight:800">Easing primitives — core.easing.*</h1>
      <p style="margin:0 0 24px;color:${textSecondary};font-size:13px;max-width:640px">
        5 cubic-bezier curves. All animate at <strong>${ms}ms</strong> so only the curve differs.
        Hover anywhere on a card to play.
      </p>
      <div style="display:flex;gap:16px;flex-wrap:wrap">${cells}</div>
      <style>
        .motion-card:hover .motion-track { transform: translateX(calc(100% - 32px)); }
      </style>
    </div>
  `;
};
