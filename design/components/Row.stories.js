/**
 * Row — list item primitive that goes inside a Card.
 *
 * One component, three trailing patterns (none / check / signal).
 * - `none`   — informational row, no interaction affordance
 * - `check`  — checkbox (selected prop), for pickers (Sonos speakers, RCA, etc.)
 * - `signal` — signal bars + optional lock + chevron (WiFi networks)
 *
 * Icon is optional — speaker rows have it, WiFi rows don't.
 */

import { DEVICE_ICON_NAMES, devIcon, signalBars } from './icons.js';
import { check, spinner } from './primitives.js';

const TRAILINGS = ['none', 'check', 'signal'];

// Dropdown options: device icons only (Row is for device/network rows —
// Alert's semantic icons are not relevant here). Empty string = "no icon" sentinel.
const ICON_OPTIONS = ['', ...DEVICE_ICON_NAMES];

const renderRow = ({ title, subtitle, icon, trailing, selected, loading, secured, signal }) => {
  let trailingHtml = '';
  if (trailing === 'check') {
    trailingHtml = check({ on: selected });
  } else if (trailing === 'signal') {
    trailingHtml = `
      <div style="display:flex;align-items:center;gap:8px">
        ${secured ? `<span style="font-size:12px;color:var(--text-color-placeholder)">🔒</span>` : ''}
        ${signalBars(signal)}
        <span style="font-size:14px;color:var(--text-color-placeholder)" aria-hidden="true">›</span>
      </div>`;
  }
  return `
    <div class="card" style="max-width:480px">
      <button class="row${loading ? ' loading' : ''}">
        ${icon ? devIcon(icon) : ''}
        <div class="row-content">
          <div class="row-title">${title}</div>
          ${subtitle ? `<div class="row-sub">${subtitle}</div>` : ''}
        </div>
        ${trailingHtml}
      </button>
    </div>
  `;
};

export default {
  title: 'Components/Row',
  tags: ['autodocs'],
  argTypes: {
    title: {
      control: 'text',
      description: 'Primary row text.',
      table: { type: { summary: 'string' }, category: 'Content' },
    },
    subtitle: {
      control: 'text',
      description: 'Optional secondary line (13px). Empty string = hidden.',
      table: { type: { summary: 'string' }, defaultValue: { summary: "''" }, category: 'Content' },
    },
    icon: {
      control: { type: 'select' },
      options: ICON_OPTIONS,
      labels: { '': '(no icon)' },
      description: 'Leading device icon (speakers + RCA). "(no icon)" renders a row without the `.dev-icon` slot.',
      table: { type: { summary: DEVICE_ICON_NAMES.map(n => `'${n}'`).join(' | ') + ' | undefined' }, category: 'Content' },
    },
    trailing: {
      control: { type: 'select' },
      options: TRAILINGS,
      description: 'Trailing element type. `signal` includes lock + bars + chevron in one composed affordance.',
      table: { type: { summary: "'none' | 'check' | 'signal'" }, defaultValue: { summary: "'none'" }, category: 'Trailing' },
    },
    selected: {
      control: 'boolean',
      description: 'Only meaningful when `trailing=check`. Renders the checkmark filled (accent gold).',
      table: { type: { summary: 'boolean' }, defaultValue: { summary: 'false' }, category: 'State (config)' },
    },
    loading: {
      control: 'boolean',
      description: 'Opacity 0.5 + pointer-events:none. Used during API calls.',
      table: { type: { summary: 'boolean' }, defaultValue: { summary: 'false' }, category: 'State (config)' },
    },
    secured: {
      control: 'boolean',
      description: 'Only meaningful when `trailing=signal`. Shows 🔒 before the signal bars (secured WiFi).',
      table: { type: { summary: 'boolean' }, defaultValue: { summary: 'false' }, category: 'Trailing' },
    },
    signal: {
      control: { type: 'range', min: 0, max: 4, step: 1 },
      description: 'Only meaningful when `trailing=signal`. Number of lit signal bars (0–4).',
      table: { type: { summary: '0 | 1 | 2 | 3 | 4' }, defaultValue: { summary: '3' }, category: 'Trailing' },
    },
  },
  args: {
    // Match the API defaults (documented in .md). Individual stories
    // override for visual showcases.
    title: 'Row title',
    subtitle: '',
    icon: '',
    trailing: 'none',
    selected: false,
    loading: false,
    secured: false,
    signal: 3,
  },
  render: renderRow,
  parameters: {
    docs: {
      description: {
        component:
          'List item primitive. Lives inside a `Card`. See `Row.md` for the full matrix and guidelines.',
      },
    },
  },
};

// ===== Overview — row states + trailing patterns =====
export const Overview = {
  name: 'Overview',
  parameters: {
    controls: { disable: true },
    // Loading row uses opacity:0.5 → WCAG 1.4.3 exempts inactive UI components from contrast.
    a11y: { config: { rules: [{ id: 'color-contrast', enabled: false }] } },
  },
  render: () => `
    <div style="background:var(--surface-canvas-background);padding:var(--spacing-loose)">
    <div style="display:flex;flex-direction:column;gap:var(--spacing-default);max-width:480px">
      <div>
        <div style="font-size:var(--text-caption-size);color:var(--text-color-secondary);font-weight:500;margin-bottom:var(--spacing-snug)">Check trailing — speaker list</div>
        <div class="card" role="group" aria-label="Sonos speakers">
          <button class="row">
            ${devIcon('soundbar')}
            <div class="row-content"><div class="row-title">Salon Beam</div><div class="row-sub">Sonos Beam · 192.168.1.53</div></div>
            ${check({ on: true })}
          </button>
          <button class="row">
            ${devIcon('compact')}
            <div class="row-content"><div class="row-title">Chambre</div><div class="row-sub">Sonos One · 192.168.1.55</div></div>
            ${check({ on: false })}
          </button>
          <button class="row loading">
            ${devIcon('portable')}
            <div class="row-content"><div class="row-title">Vinyl Port</div><div class="row-sub">Sonos Roam · connecting…</div></div>
            ${check({ on: false })}
          </button>
        </div>
      </div>
      <div>
        <div style="font-size:var(--text-caption-size);color:var(--text-color-secondary);font-weight:500;margin-bottom:var(--spacing-snug)">Signal trailing — WiFi list</div>
        <div class="card" role="group" aria-label="WiFi networks">
          <button class="row">
            <div class="row-content"><div class="row-title">MyHomeWiFi</div><div class="row-sub">Connected</div></div>
            <div style="display:flex;align-items:center;gap:8px"><span style="font-size:12px;color:var(--text-color-placeholder)">🔒</span>${signalBars(4)}<span style="font-size:14px;color:var(--text-color-placeholder)" aria-hidden="true">›</span></div>
          </button>
          <button class="row">
            <div class="row-content"><div class="row-title">FreeBox-ABC</div></div>
            <div style="display:flex;align-items:center;gap:8px">${signalBars(2)}<span style="font-size:14px;color:var(--text-color-placeholder)" aria-hidden="true">›</span></div>
          </button>
        </div>
      </div>
      <div>
        <div style="font-size:var(--text-caption-size);color:var(--text-color-secondary);font-weight:500;margin-bottom:var(--spacing-snug)">Status display — informational (sunken, not interactive)</div>
        <div class="card card--status" role="group" aria-label="Status display">
          <div class="row" style="cursor:default">
            <div class="row-content"><div class="row-title">MyHomeWiFi</div><div class="row-sub">Network · <YOUR-CHIP-IP></div></div>
          </div>
          <div class="row" style="cursor:default">
            ${devIcon('soundbar')}
            <div class="row-content"><div class="row-title">Playing on Salon Beam</div><div class="row-sub">Sonos Beam · 192.168.1.53</div></div>
          </div>
        </div>
      </div>
    </div>
    </div>
  `,
};

// ===== Canonical stories =====
export const Default = {
  args: { icon: 'soundbar', subtitle: 'Row subtitle', trailing: 'check' },
};
export const Selected = {
  args: { icon: 'soundbar', subtitle: 'Row subtitle', trailing: 'check', selected: true },
};
export const Loading = {
  args: { icon: 'soundbar', subtitle: 'Loading…', trailing: 'check', loading: true },
  // Loading state intentionally drops opacity to 0.5 → contrast halved.
  // This is the canonical loading affordance — the row is unclickable, not legible.
  parameters: { a11y: { config: { rules: [{ id: 'color-contrast', enabled: false }] } } },
};
export const WifiNetwork = {
  args: {
    title: 'Network SSID',
    trailing: 'signal',
    signal: 3,
    secured: true,
  },
};

// ===== Card + Row compositions =====
// Live here (not in Card.stories.js) because the variation comes from Row,
// not from the Card shell. Keeps Card focused on the shell.

export const MultipleRows = {
  name: 'Card + multiple rows',
  parameters: {
    controls: { disable: true },
    docs: { description: { story: 'Static composition — three rows in a Card with a `list` role. Most common pattern for Sonos/RCA pickers.' } },
  },
  render: () => `
    <div class="card" style="max-width:480px" role="group" aria-label="Speaker list sample">
      <button class="row">
        ${devIcon('soundbar')}
        <div class="row-content"><div class="row-title">Row title 1</div><div class="row-sub">Row subtitle 1</div></div>
        ${check({ on: true })}
      </button>
      <button class="row">
        ${devIcon('portable')}
        <div class="row-content"><div class="row-title">Row title 2</div><div class="row-sub">Row subtitle 2</div></div>
        ${check()}
      </button>
      <button class="row">
        ${devIcon('rca')}
        <div class="row-content"><div class="row-title">Row title 3</div></div>
        ${check()}
      </button>
    </div>
  `,
};

export const Interactive = {
  name: 'Card + rows (interactive)',
  parameters: {
    controls: { disable: true },
    docs: { description: { story: 'Click any row to toggle its check. Demonstrates the Card+Row interactive composition end-to-end.' } },
  },
  render: () => {
    const card = document.createElement('div');
    card.className = 'card';
    card.style.maxWidth = '480px';
    card.setAttribute('role', 'group');
    card.setAttribute('aria-label', 'Speaker picker');
    const rows = [
      { icon: 'soundbar', title: 'Row title 1', sub: 'Row subtitle 1', selected: true },
      { icon: 'portable', title: 'Row title 2', sub: 'Row subtitle 2', selected: false },
      { icon: 'rca',      title: 'Row title 3', sub: '',               selected: false },
    ];
    rows.forEach((r) => {
      const btn = document.createElement('button');
      btn.className = 'row';
      btn.innerHTML = `
        ${devIcon(r.icon)}
        <div class="row-content"><div class="row-title">${r.title}</div>${r.sub ? `<div class="row-sub">${r.sub}</div>` : ''}</div>
        ${check({ on: r.selected })}
      `;
      btn.addEventListener('click', () => {
        btn.querySelector('.check').classList.toggle('on');
      });
      card.appendChild(btn);
    });
    return card;
  },
};

export const ManyRows = {
  name: 'Card + many rows (overflow)',
  parameters: {
    controls: { disable: true },
    docs: { description: { story: '12 rows in one Card — exercises overflow / density / divider behavior.' } },
  },
  render: () => {
    const rows = Array.from({ length: 12 }, (_, i) => `
      <button class="row">
        ${devIcon(['soundbar', 'portable', 'compact', 'large', 'homecinema'][i % 5])}
        <div class="row-content"><div class="row-title">Row title ${i + 1}</div><div class="row-sub">Row subtitle ${i + 1}</div></div>
        ${check({ on: i % 3 === 0 })}
      </button>
    `).join('');
    return `
      <div class="card" style="max-width:480px" role="group" aria-label="Large speaker list">
        ${rows}
      </div>
    `;
  },
};

// ===== Reconnect — row with spinner leading + message =====
// Was a Layout primitive; it's really a row-like composition (spinner instead
// of icon + message as title). No interaction — informational.
export const Reconnect = {
  name: 'Reconnect (spinner + message)',
  argTypes: { message: { control: 'text' } },
  args: { message: 'Reconnecting…' },
  parameters: {
    docs: { description: { story: 'Composition pattern — Row-shaped container with a spinner in the leading slot and a message as title. Used for transient reconnection states. Not a standard Row API use (spinner is not an `icon`), so Controls are limited.' } },
  },
  render: ({ message }) => `
    <div class="card" style="max-width:480px">
      <div class="row" style="cursor:default">
        ${spinner()}
        <div class="row-content"><div class="row-title">${message}</div></div>
      </div>
    </div>
  `,
};

// ===== Gallery — all device icon types stacked =====
// Used to be `SpeakerCard` stories; merged back into Row since SpeakerCard
// was a thin wrapper with no added value over Row.
export const Gallery = {
  name: 'Gallery — device icon types',
  parameters: {
    controls: { disable: true },
    docs: { description: { story: 'Each device icon type (Sonos form-factors + RCA) rendered in a Row — visual reference for the `icon` prop.' } },
  },
  render: () => {
    const labels = {
      soundbar:   { title: 'Soundbar',     sub: 'e.g. Sonos Beam' },
      homecinema: { title: 'Home theater', sub: 'e.g. Sonos Arc + Sub' },
      compact:    { title: 'Compact',      sub: 'e.g. Sonos One' },
      portable:   { title: 'Portable',     sub: 'e.g. Sonos Roam' },
      large:      { title: 'Large',        sub: 'e.g. Sonos Five' },
      headphone:  { title: 'Headphone',    sub: 'e.g. Sonos Ace' },
      infra:      { title: 'Infra',        sub: 'Infrastructure' },
      unknown:    { title: 'Unknown',      sub: 'Unidentified model' },
      rca:        { title: 'RCA',          sub: 'Local analog output' },
    };
    const rows = DEVICE_ICON_NAMES.map((iconName) => {
      const { title, sub } = labels[iconName];
      return `
        <button class="row">
          ${devIcon(iconName)}
          <div class="row-content"><div class="row-title">${title}</div><div class="row-sub">${sub}</div></div>
          ${check()}
        </button>
      `;
    }).join('');
    return `<div class="card" style="max-width:480px" role="group" aria-label="All device icon types">${rows}</div>`;
  },
};
