/**
 * Toggle — iOS-style boolean switch.
 *
 * A pill-shaped track with a sliding knob. Off = muted track, On = accent fill.
 * Used in the firmware portal for binary settings (e.g. "Afficher sortie RCA").
 *
 * Not a segmented control (no exclusive selection). Represents a single
 * true/false preference — use SegmentedControl for multi-value choices.
 */

const renderToggle = ({ checked, disabled, label }) => {
  const checkedAttr = checked ? 'checked' : '';
  const disabledAttr = disabled ? 'disabled' : '';
  const opacity = disabled ? 'opacity:0.4;pointer-events:none;' : '';
  const ariaLabel = label ? ` aria-label="${label}"` : '';
  return `
    <div class="toggle-row" style="${opacity}">
      ${label ? `<span class="toggle-label" aria-hidden="true">${label}</span>` : ''}
      <label class="toggle-switch">
        <input type="checkbox" ${checkedAttr} ${disabledAttr}${ariaLabel}>
        <span class="toggle-slider" aria-hidden="true"></span>
      </label>
    </div>
  `.trim();
};

export default {
  title: 'Components/Toggle',
  tags: ['autodocs'],
  argTypes: {
    checked: {
      control: 'boolean',
      description: 'On/off state.',
      table: { type: { summary: 'boolean' }, defaultValue: { summary: 'false' }, category: 'State (config)' },
    },
    disabled: {
      control: 'boolean',
      description: 'Locked state — setting not available. Opacity 0.4, pointer-events off.',
      table: { type: { summary: 'boolean' }, defaultValue: { summary: 'false' }, category: 'State (config)' },
    },
    label: {
      control: 'text',
      description: 'Optional label displayed to the left of the toggle.',
      table: { type: { summary: 'string' }, category: 'Content' },
    },
  },
  args: {
    checked: false,
    disabled: false,
    label: 'Enable feature',
  },
  render: ({ checked, disabled, label }) => renderToggle({ checked, disabled, label }),
  parameters: {
    docs: {
      description: {
        component:
          'iOS-style boolean toggle. Renders a pill track with sliding knob. Use for binary preferences only — multi-value choices use `SegmentedControl`.',
      },
    },
  },
};

export const Overview = {
  name: 'Overview',
  parameters: {
    controls: { disable: true },
    // Disabled rows use opacity:0.4 which axe flags, but WCAG 1.4.3 explicitly exempts
    // "inactive user interface components" from contrast requirements.
    a11y: { config: { rules: [{ id: 'color-contrast', enabled: false }] } },
  },
  render: () => `
    <div style="background:var(--surface-canvas-background);padding:var(--spacing-loose);max-width:280px">
    <div style="display:flex;flex-direction:column;gap:0">
      ${renderToggle({ checked: false, label: 'Off state' })}
      ${renderToggle({ checked: true,  label: 'On state' })}
      ${renderToggle({ checked: false, disabled: true, label: 'Disabled' })}
      ${renderToggle({ checked: true,  disabled: true, label: 'Disabled (on)' })}
    </div>
    </div>
  `,
};

export const Default = { args: { checked: false } };

export const Checked = {
  args: { checked: true, label: 'Show RCA output' },
  parameters: { docs: { description: { story: 'Active state — accent-colored track.' } } },
};

export const Interactive = {
  name: 'Interactive',
  args: { label: 'Show RCA output', checked: false },
  render: ({ label }) => {
    const wrap = document.createElement('div');
    wrap.style.cssText = 'background:var(--surface-canvas-background);padding:var(--spacing-loose);max-width:280px';
    wrap.innerHTML = renderToggle({ checked: false, label });
    const inp = wrap.querySelector('input');
    inp.addEventListener('change', () => {
      const newLabel = inp.checked ? 'Feature enabled' : 'Feature disabled';
      const lbl = wrap.querySelector('.toggle-label');
      if (lbl) lbl.textContent = newLabel;
      inp.setAttribute('aria-label', newLabel);
    });
    return wrap;
  },
  parameters: { docs: { description: { story: 'Click to toggle. Mirrors `rca-show-ui` firmware setting behavior.' } } },
};
