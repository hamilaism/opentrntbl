/**
 * Card — surface container primitive.
 *
 * Minimal API: optional `role` + `ariaLabel` for accessibility. Zero
 * visual props — layout is driven by children (Row, Alert, Input, or
 * custom content).
 *
 * Spacing : Card does NOT own a margin. Parents stack Cards via
 * `display: flex; gap: var(--spacing-default)` — see guidelines in Card.md.
 *
 * Scope of this file : the **shell** only. Card+Row compositions live in
 * `Components/Row` (Default, Selected, Loading, Wifi, Reconnect, Gallery,
 * Multiple, Interactive, Many) since the variation comes from Row, not
 * from Card.
 */

import { spinner } from './primitives.js';

const cardAttrs = ({ role, ariaLabel }) => {
  const parts = [];
  if (role)       parts.push(`role="${role}"`);
  if (ariaLabel)  parts.push(`aria-label="${ariaLabel}"`);
  return parts.join(' ');
};

export default {
  title: 'Components/Card',
  tags: ['autodocs'],
  argTypes: {
    role: {
      control: { type: 'select' },
      options: [null, 'group', 'list', 'region'],
      description: 'Optional ARIA role. Set when the Card semantically groups related items (list of speakers = `list`, a form group = `group`, a page landmark = `region`). Leave `null` for purely presentational Cards.',
      table: { type: { summary: "'group' | 'list' | 'region' | null" }, defaultValue: { summary: 'null' }, category: 'Accessibility' },
    },
    ariaLabel: {
      control: 'text',
      description: 'Required when `role` is set — gives the role a meaningful name for screen readers. Example: `"Sonos speakers"` for a list of speaker rows.',
      table: { type: { summary: 'string' }, defaultValue: { summary: "''" }, category: 'Accessibility' },
    },
  },
  args: {
    role: null,
    ariaLabel: '',
  },
  parameters: {
    docs: {
      description: {
        component:
          'Surface container. Minimal API — children drive the layout. See `Card.md` for composition patterns, spacing guidelines, and accessibility details. Card+Row compositions are showcased in `Components/Row`.',
      },
    },
  },
};

// ===== Default — shell only, no children =====
export const Default = {
  parameters: {
    docs: { description: { story: 'Empty Card shell. Demonstrates the bare container — visible surface, radius, padding inheritance from children.' } },
  },
  render: ({ role, ariaLabel }) => `
    <div class="card" style="max-width:480px;min-height:80px" ${cardAttrs({ role, ariaLabel })}></div>
  `,
};

// ===== Empty state — spinner inside =====
export const Empty = {
  parameters: {
    controls: { disable: true },
    docs: { description: { story: 'Empty/loading state pattern — centered spinner inside a Card. Used while a list is fetching or unpopulated.' } },
  },
  render: () => `
    <div class="card" style="max-width:480px">
      <div class="row" style="cursor:default;justify-content:center">
        ${spinner()}
      </div>
    </div>
  `,
};

// ===== Card with custom (non-row) content =====
export const WithCustomContent = {
  name: 'With custom content',
  argTypes: {
    description: { control: 'text', description: 'Help text above the URL — example content, not a Card prop' },
    url:         { control: 'text', description: 'Example content, not a Card prop' },
    buttonLabel: { control: 'text', description: 'Example content, not a Card prop' },
  },
  args: {
    role: null,
    ariaLabel: '',
    description: 'Share this link to listen from any browser or media player.',
    url: 'http://example.com/stream',
    buttonLabel: 'Share',
  },
  render: ({ role, ariaLabel, description, url, buttonLabel }) => `
    <div class="card" style="max-width:480px" ${cardAttrs({ role, ariaLabel })}>
      <div style="padding:16px">
        <div style="font-size:13px;color:var(--text-color-secondary);margin-bottom:10px;font-weight:500;line-height:1.5">${description}</div>
        <div style="display:flex;align-items:center;gap:10px">
          <div style="flex:1;font-size:13px;color:var(--text-color-placeholder);background:var(--surface-sunken-background);padding:10px 14px;border-radius:var(--radius-round);overflow:hidden;text-overflow:ellipsis;white-space:nowrap;font-family:var(--text-code-family)">${url}</div>
          <button class="btn-tonal">${buttonLabel}</button>
        </div>
      </div>
    </div>
  `,
  parameters: {
    docs: { description: { story: 'Card with non-row content. `description` / `url` / `buttonLabel` are example-content knobs, not Card props.' } },
  },
};
