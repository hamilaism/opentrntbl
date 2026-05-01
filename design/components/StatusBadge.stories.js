/**
 * StatusBadge — colored pill signaling playback status.
 *
 * Variants: idle / playing / warning / error.
 * CSS classes: status-idle / status-play / status-warn / status-err.
 */

import { statusDot } from './primitives.js';

const CSS = {
  idle:    'status-idle',
  playing: 'status-play',
  warning: 'status-warn',
  error:   'status-err',
};

const VARIANTS = Object.keys(CSS);

const renderBadge = ({ variant, label, dot }) => `
  <span class="status ${CSS[variant]}">
    ${dot ? statusDot() : ''}
    <span>${label}</span>
  </span>
`;

export default {
  title: 'Components/StatusBadge',
  tags: ['autodocs'],
  argTypes: {
    variant: {
      control: { type: 'select' },
      options: VARIANTS,
      description: 'Semantic level. `playing` animates the dot via `@keyframes pulse`.',
      table: { type: { summary: VARIANTS.map(v => `'${v}'`).join(' | ') }, defaultValue: { summary: "'idle'" }, category: 'Variant' },
    },
    label: {
      control: 'text',
      description: 'Badge text.',
      table: { type: { summary: 'string' }, category: 'Content' },
    },
    dot: {
      control: 'boolean',
      description: '8px leading dot. Animated only when variant is `playing` (signal "live/breathing").',
      table: { type: { summary: 'boolean' }, defaultValue: { summary: 'true' }, category: 'Content' },
    },
  },
  args: {
    variant: 'playing',
    label: 'Status label',
    dot: true,
  },
  render: renderBadge,
  parameters: {
    layout: 'centered',
    docs: {
      description: {
        component: 'See `StatusBadge.md` for the full variant × dot matrix.',
      },
    },
  },
};

export const Idle    = { args: { variant: 'idle',    label: 'Idle' } };
export const Playing = { args: { variant: 'playing', label: 'Playing' } };
export const Warning = { args: { variant: 'warning', label: 'Warning' } };
export const Error   = { args: { variant: 'error',   label: 'Error' } };
