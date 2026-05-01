/* openTRNTBL — Primitives (template fonctions vanilla)
 *
 * Petits éléments réutilisés partout. Pas de framework JS — chaque
 * primitive est juste une fonction qui renvoie du HTML string, donc
 * utilisable dans les stories ET dans firmware/index.html en concat.
 *
 * Convention : args sous forme d'objet { ...props } pour rester lisible.
 */

/** Spinner (.spin) — variant small pour inline boutons */
export const spinner = ({ small = false } = {}) =>
  `<div class="spin${small ? ' spin-sm' : ''}"></div>`;

/** Status dot (.status-dot) — currentColor, animé si parent a .status-play.
 *  Le dot est gardé pour son sémantique "live/breathing" (signal d'activité,
 *  pas de variant). L'accessibilité non-couleur (WCAG 1.4.1) est portée par
 *  le label de StatusBadge — pas besoin d'icône SVG redondante. */
export const statusDot = () => `<span class="status-dot"></span>`;

/** Checkbox (.check) — accent gold quand on=true */
export const check = ({ on = false } = {}) =>
  `<div class="check${on ? ' on' : ''}"></div>`;

/** Brand mark — "open<em>TRNTBL</em>" lettering */
export const brand = ({ prefix = 'open', accent = 'TRNTBL' } = {}) =>
  `<div class="brand-name">${prefix}<em>${accent}</em></div>`;

/** Brand block (avec wrapper .brand pour le centrage + padding) */
export const brandBlock = (opts = {}) =>
  `<div class="brand">${brand(opts)}</div>`;
