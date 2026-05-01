/**
 * Alert — standalone panel with semantic variant + icon + optional title + body.
 *
 * Four variants (info / warning / error / success) — each with its own icon
 * background color and default icon from the ICONS map.
 *
 * Distinct from Card — uses its own `.alert` CSS class, with integrated
 * padding and icon slot.
 */

import { ICONS, SEMANTIC_ICON_NAMES } from './icons.js';

const VARIANTS = ['info', 'warning', 'error', 'success'];

// Default icon per variant (overridable via `icon` prop)
const DEFAULT_ICONS = {
  info:    'info',
  warning: 'warning',
  error:   'error',
  success: 'success',
};

const renderAlert = ({ variant, title, body, icon }) => {
  const iconKey = icon || DEFAULT_ICONS[variant];
  const iconSvg = ICONS[iconKey] || '';
  return `
    <div class="alert ${variant}" style="max-width:480px">
      <div class="alert-icon">${iconSvg}</div>
      <div class="alert-content">
        ${title ? `<div class="alert-title">${title}</div>` : ''}
        <div class="alert-body">${body}</div>
      </div>
    </div>
  `;
};

export default {
  title: 'Components/Alert',
  tags: ['autodocs'],
  argTypes: {
    variant: {
      control: { type: 'select' },
      options: VARIANTS,
      description: 'Semantic level. Each variant has its own icon background color and default SVG.',
      table: { type: { summary: VARIANTS.map(v => `'${v}'`).join(' | ') }, defaultValue: { summary: "'warning'" }, category: 'Variant' },
    },
    title: {
      control: 'text',
      description: 'Optional bold title above the body. Skip for single-line body-only alerts.',
      table: { type: { summary: 'string' }, defaultValue: { summary: "''" }, category: 'Content' },
    },
    body: {
      control: 'text',
      description: 'Main message. Supports inline HTML (`<strong>`, `<em>`).',
      table: { type: { summary: 'string' }, category: 'Content' },
    },
    icon: {
      control: { type: 'select' },
      options: ['', ...SEMANTIC_ICON_NAMES],
      labels: { '': '(variant default)' },
      description: 'Override the default semantic icon. Leave empty to use the variant default (info/warning/error/success).',
      table: { type: { summary: "'info' | 'warning' | 'error' | 'success' | undefined" }, category: 'Content' },
    },
  },
  args: {
    variant: 'warning',
    title: '',
    body: 'Alert body — supports inline <strong>bold</strong>.',
    icon: '',
  },
  render: renderAlert,
  parameters: {
    docs: {
      description: {
        component:
          'Standalone panel for contextual messages. Distinct from Card — uses `.alert` CSS class with integrated icon slot. See `Alert.md` for the variant × icon matrix and guidelines.',
      },
    },
  },
};

// ===== One story per variant =====
export const Warning = {
  args: {
    variant: 'warning',
    title: 'Network unreachable',
    body: 'The network <strong>MyHomeWiFi</strong> is not responding. Check that your router is on.',
  },
};

export const Info = {
  args: {
    variant: 'info',
    title: 'Firmware update available',
    body: 'Version 1.2.0 is ready. Apply now or later from Settings.',
  },
};

export const Error = {
  args: {
    variant: 'error',
    title: 'Stream failed to start',
    body: 'Audio capture could not initialize. Try unplugging and reconnecting the USB audio device.',
  },
};

export const Success = {
  args: {
    variant: 'success',
    title: 'Settings saved',
    body: 'Your bitrate preference has been applied to all sessions.',
  },
};
