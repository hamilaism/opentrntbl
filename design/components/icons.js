/* openTRNTBL — Icons (SVG inline, stroke=currentColor)
 * Toutes les icônes utilisées dans le portail web.
 * Importé par les stories pour exposer un control "icon" dropdown.
 */

export const ICONS = {
  // Speakers / devices
  soundbar:   `<svg viewBox="0 0 24 24"><rect x="2" y="8" width="20" height="8" rx="3"/><circle cx="7" cy="12" r="1.5" fill="currentColor" stroke="none"/><circle cx="17" cy="12" r="1.5" fill="currentColor" stroke="none"/></svg>`,
  homecinema: `<svg viewBox="0 0 24 24"><rect x="2" y="9" width="20" height="6" rx="2"/><rect x="3" y="4" width="4" height="5" rx="1" stroke-dasharray="2 1"/><rect x="17" y="4" width="4" height="5" rx="1" stroke-dasharray="2 1"/></svg>`,
  compact:    `<svg viewBox="0 0 24 24"><rect x="6" y="3" width="12" height="18" rx="2"/><circle cx="12" cy="14" r="3"/></svg>`,
  portable:   `<svg viewBox="0 0 24 24"><rect x="8" y="2" width="8" height="20" rx="4"/><circle cx="12" cy="15" r="2"/></svg>`,
  large:      `<svg viewBox="0 0 24 24"><rect x="5" y="3" width="14" height="18" rx="2"/><circle cx="12" cy="14" r="3.5"/><line x1="9" y1="7" x2="15" y2="7"/></svg>`,
  headphone:  `<svg viewBox="0 0 24 24"><path d="M4 16V12a8 8 0 0 1 16 0v4"/><rect x="2" y="14" width="4" height="6" rx="1"/><rect x="18" y="14" width="4" height="6" rx="1"/></svg>`,
  infra:      `<svg viewBox="0 0 24 24"><rect x="3" y="7" width="18" height="10" rx="2"/><circle cx="8" cy="12" r="1" fill="currentColor" stroke="none"/><line x1="12" y1="10" x2="18" y2="10"/><line x1="12" y1="14" x2="18" y2="14"/></svg>`,
  unknown:    `<svg viewBox="0 0 24 24"><circle cx="12" cy="12" r="9"/><circle cx="12" cy="12" r="4"/></svg>`,
  rca:        `<svg viewBox="0 0 24 24"><circle cx="8" cy="12" r="4"/><circle cx="8" cy="12" r="1.5" fill="currentColor" stroke="none"/><circle cx="17" cy="12" r="4"/><circle cx="17" cy="12" r="1.5" fill="currentColor" stroke="none"/></svg>`,

  // Semantic status icons (used by Alert, extensible)
  info:    `<svg viewBox="0 0 24 24"><circle cx="12" cy="12" r="10"/><line x1="12" y1="16" x2="12" y2="12"/><line x1="12" y1="8" x2="12.01" y2="8"/></svg>`,
  warning: `<svg viewBox="0 0 24 24"><path d="M10.29 3.86 1.82 18a2 2 0 0 0 1.71 3h16.94a2 2 0 0 0 1.71-3L13.71 3.86a2 2 0 0 0-3.42 0z"/><line x1="12" y1="9" x2="12" y2="13"/><line x1="12" y1="17" x2="12.01" y2="17"/></svg>`,
  error:   `<svg viewBox="0 0 24 24"><circle cx="12" cy="12" r="10"/><line x1="15" y1="9" x2="9" y2="15"/><line x1="9" y1="9" x2="15" y2="15"/></svg>`,
  success: `<svg viewBox="0 0 24 24"><path d="M22 11.08V12a10 10 0 1 1-5.93-9.14"/><polyline points="22 4 12 14.01 9 11.01"/></svg>`,
};

export const ICON_NAMES = Object.keys(ICONS);

/** Device-style icons — leading icons for Row (speakers + RCA). */
export const DEVICE_ICON_NAMES = [
  'soundbar', 'homecinema', 'compact', 'portable', 'large', 'headphone', 'infra', 'unknown', 'rca',
];

/** Semantic status icons — for Alert variants (info / warning / error / success). */
export const SEMANTIC_ICON_NAMES = ['info', 'warning', 'error', 'success'];

/** Render un wrapper .dev-icon avec l'icône demandée */
export const devIcon = (name) =>
  ICONS[name] ? `<div class="dev-icon">${ICONS[name]}</div>` : '';

/** Signal bars 0-4 (WiFi strength) */
export const signalBars = (level = 4) => {
  let html = '<div class="signal">';
  for (let i = 1; i <= 4; i++) {
    html += `<b${level < i ? ' class="off"' : ''}></b>`;
  }
  return html + '</div>';
};
