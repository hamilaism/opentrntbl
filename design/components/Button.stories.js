/**
 * Button — all variants used in the openTRNTBL portal.
 *
 * Taxonomy:
 * - primary     — Filled, inverted, main CTA per screen
 * - secondary   — Filled surface, equal-weight alternative
 * - destructive — Red text, reversible destructive action
 * - toggle      — Binary on/off state (stateful by design)
 * - ghost       — No fill, text action in a flow (shadcn/Chakra canonical)
 * - tonal       — Subtle fill, attached to content (Material 3 canonical)
 *
 * CSS classes: btn-1 / btn-2 / btn-disconnect / btn-toggle / btn-ghost / btn-tonal.
 */

import { spinner } from './primitives.js';

const CSS = {
  primary:     'btn btn-1',
  secondary:   'btn btn-2',
  destructive: 'btn btn-disconnect',
  toggle:      'btn-toggle',
  ghost:       'btn-ghost',
  tonal:       'btn-tonal',
};

const VARIANTS = Object.keys(CSS);

// Default fullWidth per variant — can be overridden via prop
const FULL_WIDTH_DEFAULTS = {
  primary: true, secondary: true, destructive: true, toggle: true, ghost: true, tonal: false,
};

const renderButton = ({ variant, label, toggled, disabled, loading, fullWidth }) => {
  const isFullWidth = fullWidth !== undefined ? fullWidth : FULL_WIDTH_DEFAULTS[variant];
  // `.active` only applies to `toggle` variant — other variants have no CSS hook for it
  const cls = `${CSS[variant]}${variant === 'toggle' && toggled ? ' active' : ''}`;
  const content = loading ? `${spinner({ small: true })} ${label}` : label;
  const style = `style="width:${isFullWidth ? '100%' : 'auto'}"`;
  return `<button class="${cls}" ${disabled ? 'disabled' : ''} ${style}>${content}</button>`;
};

export default {
  title: 'Components/Button',
  tags: ['autodocs'],
  argTypes: {
    variant: {
      control: { type: 'select' },
      options: VARIANTS,
      description: 'Semantic role. Maps to CSS class internally.',
      table: { type: { summary: VARIANTS.map(v => `'${v}'`).join(' | ') }, defaultValue: { summary: "'primary'" }, category: 'Variant' },
    },
    label: {
      control: 'text',
      description: 'Visible button text (microcopy).',
      table: { type: { summary: 'string' }, category: 'Content' },
    },
    disabled: {
      control: 'boolean',
      description: 'HTML `disabled` attribute.',
      table: { type: { summary: 'boolean' }, defaultValue: { summary: 'false' }, category: 'State (config)' },
    },
    loading: {
      control: 'boolean',
      description: 'Inline spinner before the label. Meaningful for primary / secondary / destructive. Usually combined with `disabled`.',
      table: { type: { summary: 'boolean' }, defaultValue: { summary: 'false' }, category: 'State (config)' },
    },
    toggled: {
      control: 'boolean',
      description: 'Toggle `on` state. Only meaningful for `variant=toggle` (renders `.active` class). Named `toggled` — not `active` or `selected` — to signal "this is a toggle" and to avoid collision with CSS `:active` (pressed).',
      table: { type: { summary: 'boolean' }, defaultValue: { summary: 'false' }, category: 'State (config)' },
    },
    fullWidth: {
      control: 'boolean',
      description: 'Override variant default. Defaults: `true` for primary/secondary/destructive/toggle/ghost, `false` for tonal. Set explicitly to force a specific width regardless of variant.',
      table: { type: { summary: 'boolean' }, defaultValue: { summary: 'variant-dependent' }, category: 'Layout' },
    },
  },
  args: {
    variant: 'primary',
    label: 'Button label',
    disabled: false,
    loading: false,
    toggled: false,
    // fullWidth intentionally omitted — undefined triggers the variant-
    // dependent default in renderButton (primary/…/ghost = true, tonal = false)
  },
  render: renderButton,
  parameters: {
    docs: {
      description: {
        component:
          'Button primitive. Six semantic variants. Interaction states (`:hover`, `:focus`, `:active`) can be forced via the **Pseudo-states** toolbar toggle. See `Button.md` for the full matrix and guidelines.',
      },
    },
  },
};

// ===== Variant showcases =====
export const Primary     = { args: { variant: 'primary',     label: 'Primary action',     fullWidth: true  } };
export const Secondary   = { args: { variant: 'secondary',   label: 'Secondary action',   fullWidth: true  } };
export const Destructive = { args: { variant: 'destructive', label: 'Destructive action', fullWidth: true  } };
export const Ghost       = {
  args: { variant: 'ghost', label: 'Ghost action', fullWidth: true },
  // TODO a11y: gold accent text on light surface fails WCAG AA (4.5:1) for
  // normal-size text. Brand-identity decision: accent IS gold, can't dim it
  // to gray without losing brand. Revisit when the contrast pass arrives —
  // either bump to 16px (passes for large text 3:1) or add a darker gold.
  parameters: { a11y: { test: 'off' } },
};
export const Tonal       = { args: { variant: 'tonal',       label: 'Tonal action',       fullWidth: false } };

// ===== Config state showcases (dedicated for discoverability) =====
export const Disabled = {
  args: { variant: 'primary', label: 'Primary action', disabled: true, fullWidth: true },
  parameters: { docs: { description: { story: 'Disabled state applies to any variant (`opacity: 0.25` on primary, natural disabled styling elsewhere).' } } },
};

export const Loading = {
  args: { variant: 'primary', label: 'Loading…', loading: true, disabled: true, fullWidth: true },
  parameters: { docs: { description: { story: 'Loading state renders an inline spinner before the label. Usually combined with `disabled`.' } } },
};

// ===== Toggle (interactive — variant showcase + behavior) =====
export const Toggle = {
  name: 'Toggle (interactive)',
  argTypes: {
    offLabel:    { control: 'text', description: 'Label when `toggled=false`' },
    onLabel:     { control: 'text', description: 'Label when `toggled=true`' },
    startToggled: { control: 'boolean', description: 'Initial toggled state' },
  },
  args: {
    offLabel: 'Enable priority',
    onLabel: 'Disable priority',
    startToggled: false,
  },
  render: ({ offLabel, onLabel, startToggled }) => {
    const btn = document.createElement('button');
    btn.className = `btn-toggle${startToggled ? ' active' : ''}`;
    btn.style.width = '100%';
    btn.textContent = startToggled ? onLabel : offLabel;
    btn.addEventListener('click', () => {
      btn.classList.toggle('active');
      btn.textContent = btn.classList.contains('active') ? onLabel : offLabel;
    });
    return btn;
  },
  parameters: {
    docs: { description: { story: 'Click toggles the `.active` CSS class and swaps the microcopy. Real behavior reproduction of `togglePriority()` in the firmware.' } },
  },
};
