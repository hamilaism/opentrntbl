// openTRNTBL — Semantic / Status stories.

import { tokens, resolveToken, activeModes } from './_helpers.js';

export default {
  title: 'Tokens/Semantic/Status',
  parameters: { layout: 'fullscreen' },
};

const ROLES = ['success', 'warning', 'danger', 'info'];
const ICON = {
  success: `<svg viewBox="0 0 24 24" width="20" height="20" fill="none" stroke="currentColor" stroke-width="2.5" stroke-linecap="round" stroke-linejoin="round"><path d="M5 12l4 4 10-10"/></svg>`,
  warning: `<svg viewBox="0 0 24 24" width="20" height="20" fill="none" stroke="currentColor" stroke-width="2.5" stroke-linecap="round" stroke-linejoin="round"><path d="M12 4v10M12 18v2M3 20h18"/></svg>`,
  danger:  `<svg viewBox="0 0 24 24" width="20" height="20" fill="none" stroke="currentColor" stroke-width="2.5" stroke-linecap="round" stroke-linejoin="round"><circle cx="12" cy="12" r="9"/><path d="M8 8l8 8M16 8l-8 8"/></svg>`,
  info:    `<svg viewBox="0 0 24 24" width="20" height="20" fill="none" stroke="currentColor" stroke-width="2.5" stroke-linecap="round" stroke-linejoin="round"><circle cx="12" cy="12" r="9"/><path d="M12 8v1M12 12v4"/></svg>`,
};
const LABEL = {
  success: 'Connection established',
  warning: 'Audio buffer running low',
  danger:  'Failed to reach Sonos speaker',
  info:    'Streaming paused — no input signal',
};

export const Banners = () => {
  const modes = activeModes();
  const canvas = resolveToken(tokens.semantic.surface.canvas, modes);
  const textPrimary = resolveToken(tokens.semantic.text.color.primary, modes);
  const textSecondary = resolveToken(tokens.semantic.text.color.secondary, modes);

  const rows = ROLES.map(role => {
    const bg = resolveToken(tokens.semantic.status[role].bg, modes);
    const text = resolveToken(tokens.semantic.status[role].text, modes);
    // Pas de token semantic.status.*.border — décision DS (Vague Méta-1) :
    // les borders status n'existent pas, le tint bg + l'icône portent la
    // sémantique. Cohérent avec Alert qui ne consomme pas de border non plus.
    return `
      <div style="
        background:${bg};color:${text};
        border-left:4px solid ${text};
        padding:14px 16px;border-radius:8px;margin-bottom:12px;
        display:flex;gap:12px;align-items:center;
      ">
        <span style="flex-shrink:0">${ICON[role]}</span>
        <div style="flex:1">
          <div style="font-weight:600;font-size:14px;margin-bottom:2px;text-transform:capitalize">${role}</div>
          <div style="font-size:13px">${LABEL[role]}</div>
        </div>
      </div>
    `;
  }).join('');

  return `
    <div style="background:${canvas};min-height:100vh;padding:24px;font-family:system-ui;color:${textPrimary}">
      <h1 style="font-size:20px;margin:0 0 8px;font-weight:800">Status banners — semantic.status.*</h1>
      <p style="margin:0 0 24px;color:${textSecondary};font-size:13px;max-width:640px">
        4 roles × 3 slots (bg, text, border). Hierarchical naming <code>status.success.bg</code> etc.
        Accessibility: icon + color + text together — never color alone.
      </p>
      ${rows}
    </div>
  `;
};
