/**
 * Icons — all SVG icons exposed by the design system.
 */

import { ICONS, ICON_NAMES, devIcon, signalBars } from './icons.js';

export default {
  title: 'Components/Icons',
  parameters: { layout: 'centered' },
};

// ===== Single icon (dropdown control) =====
export const SingleIcon = {
  argTypes: {
    name:    { control: { type: 'select' }, options: ICON_NAMES, description: 'Icon key in the ICONS map' },
    wrapped: { control: 'boolean', description: 'Wrap in `.dev-icon` (40px square) like in Card rows' },
  },
  args: { name: 'soundbar', wrapped: true },
  render: ({ name, wrapped }) =>
    wrapped ? devIcon(name) : `<div style="width:32px;height:32px;color:var(--text-color-secondary)">${ICONS[name]}</div>`,
};

// ===== Gallery =====
export const Gallery = {
  parameters: { controls: { disable: true } },
  render: () => `
    <div style="display:grid;grid-template-columns:repeat(4, 1fr);gap:16px;max-width:520px">
      ${ICON_NAMES.map((name) => `
        <div style="display:flex;flex-direction:column;align-items:center;gap:8px;padding:16px;background:var(--surface-base-background);border-radius:var(--radius-round)">
          ${devIcon(name)}
          <div style="font-family:var(--text-code-family);font-size:11px;color:var(--text-color-secondary)">${name}</div>
        </div>
      `).join('')}
    </div>
  `,
};

// ===== Signal bars =====
export const SignalBars = {
  argTypes: { level: { control: { type: 'range', min: 0, max: 4, step: 1 } } },
  args: { level: 3 },
  render: ({ level }) => `<div style="color:var(--text-color-primary)">${signalBars(level)}</div>`,
};

export const SignalAllLevels = {
  parameters: { controls: { disable: true } },
  render: () => `
    <div style="display:flex;gap:24px;align-items:center;color:var(--text-color-primary)">
      ${[0, 1, 2, 3, 4].map((l) => `
        <div style="display:flex;flex-direction:column;align-items:center;gap:8px">
          ${signalBars(l)}
          <div style="font-family:var(--text-code-family);font-size:11px;color:var(--text-color-secondary)">${l}/4</div>
        </div>
      `).join('')}
    </div>
  `,
};
