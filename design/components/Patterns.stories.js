/**
 * Patterns — full-screen compositions for reference and design review.
 *
 * These are NOT reusable components — they're illustrative examples
 * showing how the design system's primitives combine into real screens.
 * Keep them up-to-date with the firmware's actual UX flow.
 */

import { devIcon, signalBars } from './icons.js';
import { brandBlock, statusDot, check } from './primitives.js';

export default {
  title: 'Patterns/Screens',
  parameters: {
    layout: 'fullscreen',
    // Patterns are illustrative compositions — they reuse component-level
    // styles and inherit any contrast trade-offs documented per-component
    // (Brand gold accent, Row .loading opacity, etc.). Audit those at the
    // component level, not in the screen composition.
    a11y: { config: { rules: [{ id: 'color-contrast', enabled: false }] } },
  },
};

// ===== Full WiFi setup screen =====
export const WifiSetup = {
  name: 'WiFi setup',
  parameters: {
    controls: { disable: true },
    docs: { description: { story: 'Full-screen composition combining Brand, TitleBlock, Card+Rows (signal trailing), and a Button/primary.' } },
  },
  render: () => `
    <div class="page">
      ${brandBlock()}
      <h1 class="title">Screen title</h1>
      <p class="subtitle">Screen subtitle — one-sentence context about the screen.</p>
      <div style="display:flex;justify-content:space-between;align-items:center;margin:24px 0 12px">
        <h2 class="section" style="margin:0;padding:0">Section label</h2>
        <button class="btn-ghost" style="margin:0;font-size:14px;width:auto">Action link</button>
      </div>
      <div class="card">
        <button class="row">
          <div class="row-content"><div class="row-title">Row title 1</div></div>
          <div style="display:flex;align-items:center;gap:8px">
            <span style="font-size:12px;color:var(--text-color-placeholder)">🔒</span>
            ${signalBars(4)}
            <span style="font-size:14px;color:var(--text-color-placeholder)">›</span>
          </div>
        </button>
        <button class="row">
          <div class="row-content"><div class="row-title">Row title 2</div></div>
          <div style="display:flex;align-items:center;gap:8px">
            <span style="font-size:12px;color:var(--text-color-placeholder)">🔒</span>
            ${signalBars(2)}
            <span style="font-size:14px;color:var(--text-color-placeholder)">›</span>
          </div>
        </button>
      </div>
      <button class="btn btn-1">Primary action</button>
    </div>
  `,
};

// ===== Full Dashboard screen =====
export const Dashboard = {
  parameters: {
    controls: { disable: true },
    docs: { description: { story: 'Main playback screen — Brand, Title, StatusBadge (playing), WifiBar, SectionHeader, Card+Row (speaker), Button/toggle.' } },
  },
  render: () => `
    <div class="page">
      ${brandBlock()}
      <h1 class="title">Screen title</h1>
      <div style="padding:8px 0 20px;text-align:center">
        <span class="status status-play">${statusDot()}<span>Playing on Speaker name</span></span>
      </div>
      <div class="wifi-bar">${signalBars(3)}<span>Network SSID</span></div>
      <h2 class="section">Section label</h2>
      <div class="card">
        <button class="row">
          ${devIcon('soundbar')}
          <div class="row-content"><div class="row-title">Speaker name</div><div class="row-sub">Speaker model</div></div>
          ${check({ on: true })}
        </button>
      </div>
      <div style="margin-top:16px">
        <button class="btn-toggle active">Toggle on</button>
      </div>
    </div>
  `,
};
