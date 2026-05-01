/**
 * Layout — structural primitives for screen scaffolding.
 *
 * Brand moved to `Primitives/Overview` (it's a lettering primitive, not
 * screen-specific). Reconnect moved to `Row` (composition pattern).
 * Screens moved to `Patterns/Screens` (illustrative compositions, not
 * reusable components).
 *
 * What remains here: the three title/header/bar primitives.
 */

import { signalBars } from './icons.js';

export default {
  title: 'Components/Layout',
  parameters: { layout: 'fullscreen' },
};

// ===== Title + subtitle =====
export const TitleBlock = {
  argTypes: {
    title:    { control: 'text' },
    subtitle: { control: 'text' },
  },
  args: {
    title: 'Screen title',
    subtitle: 'Screen subtitle — one-sentence context about the screen.',
  },
  render: ({ title, subtitle }) => `
    <div class="page">
      <h1 class="title">${title}</h1>
      <p class="subtitle">${subtitle}</p>
    </div>
  `,
};

// ===== Section header =====
export const SectionHeader = {
  argTypes: { label: { control: 'text' } },
  args: { label: 'Section label' },
  render: ({ label }) => `<div class="page"><h2 class="section">${label}</h2></div>`,
};

// ===== WiFi bar =====
export const WifiBar = {
  argTypes: {
    ssid:   { control: 'text' },
    signal: { control: { type: 'range', min: 0, max: 4, step: 1 } },
  },
  args: { ssid: 'Network SSID', signal: 3 },
  render: ({ ssid, signal }) => `
    <div class="page">
      <div class="wifi-bar">
        ${signalBars(signal)}
        <span>${ssid}</span>
      </div>
    </div>
  `,
};
