// openTRNTBL — Tokens / Core / Motion stories.
//
// Exposes the motion primitives (`core.duration.*` + `core.easing.*`) that
// are composed into `semantic.motion.*` intents. The semantic story
// (Tokens/Semantic/Radius & Motion → Motion) shows the composed intents;
// this story shows the primitives they are built from.
//
// Play trigger: a ▶ Play button per card (not hover). The .motion-track
// wrapper is full-width so translateX(calc(100% - 32px)) correctly slides
// the ball to the right edge of the container. On transitionend the ball
// snaps back instantly (no reverse animation) so you can replay cleanly.

import { tokens, resolveToken, activeModes } from './_helpers.js';

function playMotion(btn) {
  const ms = parseInt(btn.dataset.ms || '300');
  const card = btn.closest('.motion-card');
  const track = card.querySelector('.motion-track');
  if (track._busy) return;
  track._busy = true;
  btn.disabled = true;
  btn.textContent = '◼';

  const reset = () => {
    track.style.transition = 'none';
    track.classList.remove('is-playing');
    track.offsetHeight; // force reflow — ensures snap back before re-enabling transition
    track.style.transition = '';
    track._busy = false;
    btn.disabled = false;
    btn.textContent = '▶ Play';
  };

  track.classList.add('is-playing');

  if (ms === 0) {
    setTimeout(reset, 60);
    return;
  }

  const onEnd = (e) => {
    if (e.propertyName !== 'transform') return;
    track.removeEventListener('transitionend', onEnd);
    clearTimeout(fallback);
    reset();
  };
  const fallback = setTimeout(() => {
    track.removeEventListener('transitionend', onEnd);
    reset();
  }, ms + 300);

  track.addEventListener('transitionend', onEnd);
}

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

  const easingCss = 'cubic-bezier(0, 0, 0.2, 1)';

  const cells = Object.entries(tokens.core.duration).map(([key, token]) => {
    const ms = token.$value.value;
    return `
      <div class="motion-card" style="background:${base};border-radius:10px;padding:24px;flex:1;min-width:200px;">
        <div style="font-family:monospace;font-size:11px;color:${textSecondary};margin-bottom:4px;text-transform:uppercase;letter-spacing:0.08em">core.duration.${key}</div>
        <div style="font-size:16px;font-weight:700;margin-bottom:12px;color:${textPrimary}">${key}</div>
        <div style="background:${canvas};border-radius:6px;padding:8px;margin-bottom:12px;overflow:hidden">
          <div
            class="motion-track"
            style="width:100%;height:48px;display:flex;align-items:center;transition:transform ${ms}ms ${easingCss};"
          >
            <div style="width:32px;height:32px;background:${accent};border-radius:6px;flex-shrink:0;"></div>
          </div>
        </div>
        <div style="font-family:monospace;font-size:12px;font-weight:700;color:${textPrimary}">${ms}ms</div>
        <div style="font-size:11px;color:${textSecondary};margin-top:4px;margin-bottom:14px">${token.$description || ''}</div>
        <button class="play-btn" data-ms="${ms}" style="padding:6px 14px;background:${accent};color:#fff;border:none;border-radius:6px;font-size:12px;font-weight:600;cursor:pointer;letter-spacing:0.03em;">▶ Play</button>
      </div>
    `;
  }).join('');

  const container = document.createElement('div');
  container.innerHTML = `
    <div style="background:${canvas};min-height:100vh;padding:24px;font-family:system-ui;color:${textPrimary}">
      <h1 style="font-size:20px;margin:0 0 8px;font-weight:800">Duration primitives — core.duration.*</h1>
      <p style="margin:0 0 24px;color:${textSecondary};font-size:13px;max-width:640px">
        5 duration steps. Click <strong>▶ Play</strong> to preview — the ball slides across, then snaps back.
        <code>semantic.motion.*</code> intents compose these with easings.
      </p>
      <div style="display:flex;gap:16px;flex-wrap:wrap">${cells}</div>
      <style>
        .motion-track.is-playing { transform: translateX(calc(100% - 32px)); }
        .motion-card .play-btn:disabled { opacity: 0.45; cursor: default; }
      </style>
    </div>
  `;

  container.querySelectorAll('.play-btn').forEach(btn =>
    btn.addEventListener('click', () => playMotion(btn))
  );

  return container;
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

  const ms = 600;

  const cells = Object.entries(tokens.core.easing).map(([key, token]) => {
    const cb = token.$value;
    const cssCb = `cubic-bezier(${cb.join(', ')})`;
    return `
      <div class="motion-card" style="background:${base};border-radius:10px;padding:24px;flex:1;min-width:200px;">
        <div style="font-family:monospace;font-size:11px;color:${textSecondary};margin-bottom:4px;text-transform:uppercase;letter-spacing:0.08em">core.easing.${key}</div>
        <div style="font-size:16px;font-weight:700;margin-bottom:12px;color:${textPrimary}">${key}</div>
        <div style="background:${canvas};border-radius:6px;padding:8px;margin-bottom:12px;overflow:hidden">
          <div
            class="motion-track"
            style="width:100%;height:48px;display:flex;align-items:center;transition:transform ${ms}ms ${cssCb};"
          >
            <div style="width:32px;height:32px;background:${accent};border-radius:6px;flex-shrink:0;"></div>
          </div>
        </div>
        <div style="font-family:monospace;font-size:11px;font-weight:700;color:${textPrimary};margin-bottom:4px">${cssCb}</div>
        <div style="font-size:11px;color:${textSecondary};margin-bottom:14px">${token.$description || ''}</div>
        <button class="play-btn" data-ms="${ms}" style="padding:6px 14px;background:${accent};color:#fff;border:none;border-radius:6px;font-size:12px;font-weight:600;cursor:pointer;letter-spacing:0.03em;">▶ Play</button>
      </div>
    `;
  }).join('');

  const container = document.createElement('div');
  container.innerHTML = `
    <div style="background:${canvas};min-height:100vh;padding:24px;font-family:system-ui;color:${textPrimary}">
      <h1 style="font-size:20px;margin:0 0 8px;font-weight:800">Easing primitives — core.easing.*</h1>
      <p style="margin:0 0 24px;color:${textSecondary};font-size:13px;max-width:640px">
        5 cubic-bezier curves, all at <strong>${ms}ms</strong> — only the curve varies.
        Click <strong>▶ Play</strong> to feel the difference.
      </p>
      <div style="display:flex;gap:16px;flex-wrap:wrap">${cells}</div>
      <style>
        .motion-track.is-playing { transform: translateX(calc(100% - 32px)); }
        .motion-card .play-btn:disabled { opacity: 0.45; cursor: default; }
      </style>
    </div>
  `;

  container.querySelectorAll('.play-btn').forEach(btn =>
    btn.addEventListener('click', () => playMotion(btn))
  );

  return container;
};
