/**
 * SegmentedControl — Apple HIG / iOS style exclusive toggle group.
 *
 * Track with border, inactive segments transparent, active "tile" with
 * distinct background. No individual segment borders.
 *
 * Exactly one option selected at a time. Selection is controlled — the
 * parent owns `value` and reacts to clicks.
 */

const renderSegmented = ({ options, value, disabled, loading }) => {
  const attrs = [];
  if (disabled) attrs.push('aria-disabled="true"');
  if (loading)  attrs.push('data-loading="true"');
  const buttons = options
    .map((opt) => `<button class="seg-segment${opt.value === value ? ' active' : ''}" data-value="${opt.value}">${opt.label}</button>`)
    .join('');
  return `<div class="seg-track" ${attrs.join(' ')}>${buttons}</div>`;
};

const renderSegmentedInteractive = ({ options, value, disabled, loading }) => {
  const root = document.createElement('div');
  root.className = 'seg-track';
  if (disabled) root.setAttribute('aria-disabled', 'true');
  if (loading)  root.setAttribute('data-loading', 'true');
  options.forEach((opt) => {
    const btn = document.createElement('button');
    btn.className = `seg-segment${opt.value === value ? ' active' : ''}`;
    btn.textContent = opt.label;
    btn.addEventListener('click', () => {
      if (root.getAttribute('aria-disabled') === 'true' || root.getAttribute('data-loading') === 'true') return;
      root.querySelectorAll('.seg-segment').forEach((x) => x.classList.remove('active'));
      btn.classList.add('active');
    });
    root.appendChild(btn);
  });
  return root;
};

const BITRATE_OPTIONS = [
  { value: 128, label: '128k' },
  { value: 192, label: '192k' },
  { value: 256, label: '256k' },
  { value: 320, label: '320k' },
];

const GENERIC_OPTIONS = [
  { value: 'a', label: 'Option A' },
  { value: 'b', label: 'Option B' },
  { value: 'c', label: 'Option C' },
];

export default {
  title: 'Components/SegmentedControl',
  tags: ['autodocs'],
  argTypes: {
    options: {
      control: 'object',
      description: 'Array of `{ value, label }`. Exactly one value is selected at a time.',
      table: { type: { summary: 'Array<{ value: string | number; label: string }>' }, category: 'Content' },
    },
    value: {
      control: 'text',
      description: 'Currently selected `option.value`.',
      table: { type: { summary: 'string | number' }, category: 'State (config)' },
    },
    disabled: {
      control: 'boolean',
      description: 'Permanent lock — intentional, feature not available. Opacity 0.4, pointer-events blocked.',
      table: { type: { summary: 'boolean' }, defaultValue: { summary: 'false' }, category: 'State (config)' },
    },
    loading: {
      control: 'boolean',
      description: 'Transient lock during async operation (e.g., bitrate change API call). Opacity 0.6, pointer-events blocked, cursor `wait`.',
      table: { type: { summary: 'boolean' }, defaultValue: { summary: 'false' }, category: 'State (config)' },
    },
  },
  args: {
    options: GENERIC_OPTIONS,
    value: 'a',
    disabled: false,
    loading: false,
  },
  render: renderSegmented,
  parameters: {
    docs: {
      description: {
        component:
          'Exclusive toggle group — iOS-style track with floating active tile. See `SegmentedControl.md` for guidelines.',
      },
    },
  },
};

// ===== Canonical stories =====
export const Default = { args: {} };

export const Bitrate = {
  args: { options: BITRATE_OPTIONS, value: 320 },
  parameters: {
    docs: { description: { story: 'Concrete portal use case — audio bitrate selector (128 / 192 / 256 / 320k).' } },
  },
};

export const Interactive = {
  name: 'Bitrate (interactive)',
  args: { options: BITRATE_OPTIONS, value: 320 },
  render: renderSegmentedInteractive,
  parameters: {
    docs: { description: { story: 'Click a segment to switch. Replicates `setBitrate()` behavior in the firmware. Add `loading: true` in controls to test the async lock state.' } },
  },
};
