/**
 * Primitives — small reusable visual pieces.
 * Import from `design/components/primitives.js`.
 */

import { spinner, statusDot, check, brand, brandBlock } from './primitives.js';

export default {
  title: 'Components/Primitives',
  parameters: { layout: 'centered' },
};

// ===== Spinner =====
export const Spinner = {
  argTypes: { small: { control: 'boolean', description: 'Smaller variant for inline usage in buttons' } },
  args: { small: false },
  render: (args) => spinner(args),
};

export const SpinnerInButton = {
  parameters: { controls: { disable: true } },
  render: () => `
    <button class="btn btn-1" disabled style="width:240px">
      ${spinner({ small: true })} Loading…
    </button>
  `,
};

// ===== Status dot =====
export const StatusDotStatic = {
  name: 'StatusDot — static',
  parameters: { controls: { disable: true } },
  render: () => `<span class="status status-idle">${statusDot()}<span>idle</span></span>`,
};

export const StatusDotPulsing = {
  name: 'StatusDot — pulsing',
  parameters: {
    controls: { disable: true },
    docs: { description: { story: 'Animation is triggered by the parent `.status-play` class.' } },
  },
  render: () => `<span class="status status-play">${statusDot()}<span>playing</span></span>`,
};

// ===== Check =====
export const Check = {
  argTypes: { on: { control: 'boolean' } },
  args: { on: false },
  render: (args) => check(args),
};

export const CheckBoth = {
  name: 'Check — off + on',
  parameters: { controls: { disable: true } },
  render: () => `
    <div style="display:flex;gap:24px;align-items:center">
      ${check({ on: false })}
      ${check({ on: true })}
    </div>
  `,
};

// ===== Brand =====
// Note: a11y color-contrast disabled — gold accent on light bg is intentional
// brand identity, not a WCAG-target text element.
const BRAND_A11Y = { a11y: { config: { rules: [{ id: 'color-contrast', enabled: false }] } } };

export const Brand = {
  argTypes: {
    prefix: { control: 'text' },
    accent: { control: 'text' },
  },
  args: { prefix: 'open', accent: 'TRNTBL' },
  render: (args) => brand(args),
  parameters: BRAND_A11Y,
};

export const BrandBlock = {
  name: 'Brand — full block',
  argTypes: {
    prefix: { control: 'text' },
    accent: { control: 'text' },
  },
  args: { prefix: 'open', accent: 'TRNTBL' },
  render: (args) => brandBlock(args),
  parameters: { layout: 'fullscreen', ...BRAND_A11Y },
};
