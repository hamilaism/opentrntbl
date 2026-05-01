// openTRNTBL — Semantic / Radius + Motion stories.

import { tokens, resolveToken, activeModes } from './_helpers.js';

export default {
  title: 'Tokens/Semantic/Radius & Motion',
  parameters: { layout: 'fullscreen' },
};

export const Radius = () => {
  const modes = activeModes();
  const canvas = resolveToken(tokens.semantic.surface.canvas, modes);
  const textPrimary = resolveToken(tokens.semantic.text.color.primary, modes);
  const textSecondary = resolveToken(tokens.semantic.text.color.secondary, modes);
  const accent = resolveToken(tokens.semantic.accent.default, modes);

  const roles = Object.keys(tokens.semantic.radius);
  const cells = roles.map(role => {
    const token = tokens.semantic.radius[role];
    const v = resolveToken(token, modes);
    const radius = typeof v === 'object' ? `${v.value}${v.unit}` : v;
    return `
      <div style="display:flex;flex-direction:column;align-items:center;gap:8px">
        <div style="width:128px;height:128px;background:${accent};border-radius:${radius}"></div>
        <div style="font-family:monospace;font-size:12px;font-weight:700">${role}</div>
        <div style="font-family:monospace;font-size:11px;color:${textSecondary}">${radius}</div>
        <div style="font-size:11px;color:${textSecondary};text-align:center;max-width:128px">${token.$description || ''}</div>
      </div>
    `;
  }).join('');

  return `
    <div style="background:${canvas};min-height:100vh;padding:24px;font-family:system-ui;color:${textPrimary}">
      <h1 style="font-size:20px;margin:0 0 8px;font-weight:800">Radius — semantic.radius.*</h1>
      <p style="margin:0 0 24px;color:${textSecondary};font-size:13px;max-width:640px">
        5 levels from near-square to full circle. Values alias onto core.dimension.
      </p>
      <div style="display:flex;gap:32px;flex-wrap:wrap;align-items:flex-start">${cells}</div>
    </div>
  `;
};

// Semantic motion intents — composed from `core.duration.*` + `core.easing.*`.
// Read alias chain dynamically so this stays in sync with the JSON sources.
function resolveMotion(intentKey) {
  const intent = tokens.semantic.motion[intentKey];
  const v = intent.$value;

  // duration alias -> ms
  let ms = v.duration;
  if (typeof ms === 'string' && ms.startsWith('{')) {
    const path = ms.slice(1, -1).split('.');
    let node = tokens;
    for (const p of path) node = node[p];
    ms = node.$value.value;
  }

  // easing alias -> cubic-bezier array
  let easing = v.timingFunction;
  let easingKey = null;
  if (typeof easing === 'string' && easing.startsWith('{')) {
    const aliasPath = easing.slice(1, -1);
    easingKey = aliasPath.split('.').pop();
    const path = aliasPath.split('.');
    let node = tokens;
    for (const p of path) node = node[p];
    easing = node.$value;
  }
  const cssEasing = `cubic-bezier(${easing.join(', ')})`;

  // Find duration alias key for display
  let durationKey = null;
  if (typeof v.duration === 'string' && v.duration.startsWith('{')) {
    durationKey = v.duration.slice(1, -1).split('.').pop();
  }

  return { ms, cssEasing, durationKey, easingKey, description: intent.$description };
}

export const Motion = () => {
  const modes = activeModes();
  const canvas = resolveToken(tokens.semantic.surface.canvas, modes);
  const base = resolveToken(tokens.semantic.surface.base, modes);
  const textPrimary = resolveToken(tokens.semantic.text.color.primary, modes);
  const textSecondary = resolveToken(tokens.semantic.text.color.secondary, modes);
  const accent = resolveToken(tokens.semantic.accent.default, modes);

  const INTENT_KEYS = ['feedback', 'state-change', 'enter', 'exit'];

  const cells = INTENT_KEYS.map(key => {
    const m = resolveMotion(key);
    return `
      <div
        class="motion-card"
        style="
          background:${base};border-radius:10px;padding:24px;flex:1;min-width:260px;
          cursor:pointer;
        "
      >
        <div style="font-family:monospace;font-size:11px;color:${textSecondary};margin-bottom:4px;text-transform:uppercase;letter-spacing:0.08em">semantic.motion.${key}</div>
        <div style="font-size:16px;font-weight:700;margin-bottom:12px">${key}</div>
        <div style="background:${canvas};border-radius:6px;padding:8px;margin-bottom:12px;overflow:hidden">
          <div
            class="motion-track"
            style="
              width:40px;height:40px;background:${accent};border-radius:8px;
              transition:transform ${m.ms}ms ${m.cssEasing};
            "
          ></div>
        </div>
        <div style="font-family:monospace;font-size:11px;color:${textSecondary};margin-bottom:4px">
          ${m.durationKey ? `core.duration.${m.durationKey}` : `${m.ms}ms`} · ${m.easingKey ? `core.easing.${m.easingKey}` : m.cssEasing}
        </div>
        <div style="font-family:monospace;font-size:11px;color:${textSecondary};margin-bottom:8px">${m.ms}ms · ${m.cssEasing}</div>
        <div style="font-size:11px;color:${textSecondary}">${m.description || ''}</div>
      </div>
    `;
  }).join('');

  return `
    <div style="background:${canvas};min-height:100vh;padding:24px;font-family:system-ui;color:${textPrimary}">
      <h1 style="font-size:20px;margin:0 0 8px;font-weight:800">Motion intents — semantic.motion.*</h1>
      <p style="margin:0 0 24px;color:${textSecondary};font-size:13px;max-width:680px">
        Intent-based compositions of <code>core.duration.*</code> + <code>core.easing.*</code> primitives —
        see <strong>Tokens / Core / Motion</strong> for the building blocks. Hover anywhere on a card
        (not just the box) to play. The cursor stays on a stable parent so the moving box never escapes
        from under it (no judder).
      </p>
      <div style="display:flex;gap:16px;flex-wrap:wrap">${cells}</div>
      <style>
        .motion-card:hover .motion-track { transform: translateX(calc(100% - 40px)); }
      </style>
    </div>
  `;
};
