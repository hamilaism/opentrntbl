/** Preview-level config — 4-axis modes toolbar + token-system switcher + a11y + components CSS.
 *
 * Merges:
 * - The mode-toolbar system (color / contrast / vision / density via body data-attrs)
 * - Token-system switcher: v1 (production) | algorithmic | nested-modes | neumorphic
 * - The a11y addon test config (mode: 'todo' until violations are triaged)
 * - Component CSS + generated tokens CSS imports
 */

// V1 tokens (production) — declares public CSS custom properties on :root
import '../design/tokens/dist/tokens.css';

// Experimental token systems — scoped to [data-token-system="<name>"]
// Higher selector specificity than :root so experiments always override V1.
import '../design/tokens/experiments/algorithmic/tokens.css';
import '../design/tokens/experiments/nested-modes/tokens.css';
import '../design/tokens/experiments/neumorphic/tokens.css';
import '../design/tokens/experiments/flat-ui/tokens.css';
import '../design/tokens/experiments/neumorphic-nested/tokens.css';
import '../design/tokens/experiments/neumorphic-algo/tokens.css';
import '../design/tokens/experiments/modern-nested/tokens.css';
import '../design/tokens/experiments/modern-algo/tokens.css';

// Component styles — consume the token vars above (whichever are active)
import '../design/components/components.css';

// Firmware-specific page styles (used by Screens stories to match trntbl.local)
import '../design/components/firmware-ui.css';

/** @type { import('@storybook/html-vite').Preview } */
const preview = {
  parameters: {
    layout: 'padded',
    backgrounds: { disable: true }, // canvas bg comes from `--surface-canvas` driven by the active token system + color mode
    controls: {
      matchers: { color: /(background|color)$/i, date: /Date$/i },
    },

    options: {
      storySort: {
        order: [
          'Tokens', ['Core', 'Primitives', 'Semantic'],
          'Components',
          'Patterns',
        ],
      },
    },

    a11y: {
      test: 'error',
      config: {
        rules: [
          // Component gallery — stories render in isolation, not in a full page.
          // The `region` rule (all content inside landmarks) is not applicable here.
          { id: 'region', enabled: false },
        ],
      },
    },
  },

  globalTypes: {
    // ── Token system switcher ──────────────────────────────────────────────
    tokenSystem: {
      name: 'Token system',
      description: 'Switch between production V1 and experimental token architectures',
      defaultValue: 'v1',
      toolbar: {
        icon: 'database',
        items: [
          { value: 'v1',                title: 'Sonos' },
          { value: 'nested-modes',      title: 'Sonos — Nested' },
          { value: 'algorithmic',       title: 'Sonos — Algo' },
          { value: 'neumorphic',        title: 'Soft' },
          { value: 'neumorphic-nested', title: 'Soft — Nested' },
          { value: 'neumorphic-algo',   title: 'Soft — Algo' },
          { value: 'flat-ui',           title: 'Simple' },
          { value: 'modern-nested',     title: 'Simple — Nested' },
          { value: 'modern-algo',       title: 'Simple — Algo' },
        ],
        dynamicTitle: true,
      },
    },

    // ── Four orthogonal mode axes ──────────────────────────────────────────
    color: {
      name: 'Color mode',
      description: 'Light / dark mode',
      defaultValue: 'light',
      toolbar: {
        icon: 'mirror',
        items: [
          { value: 'light', title: 'Light' },
          { value: 'dark',  title: 'Dark' },
        ],
        dynamicTitle: true,
      },
    },
    contrast: {
      name: 'Contrast',
      description: 'Default / enhanced contrast',
      defaultValue: 'default',
      toolbar: {
        icon: 'contrast',
        items: [
          { value: 'default',  title: 'Default contrast' },
          { value: 'enhanced', title: 'Enhanced contrast' },
        ],
        dynamicTitle: true,
      },
    },
    vision: {
      name: 'Vision',
      description: 'Color vision simulation',
      defaultValue: 'default',
      toolbar: {
        icon: 'eye',
        items: [
          { value: 'default',       title: 'Trichromat' },
          { value: 'deuteranopia',  title: 'Deuteranopia (no green)' },
          { value: 'protanopia',    title: 'Protanopia (no red)' },
          { value: 'tritanopia',    title: 'Tritanopia (no blue)' },
          { value: 'achromatopsia', title: 'Achromatopsia (monochrome)' },
        ],
        dynamicTitle: true,
      },
    },
    density: {
      name: 'Density',
      description: 'Layout density',
      defaultValue: 'default',
      toolbar: {
        icon: 'ruler',
        items: [
          { value: 'compact',  title: 'Compact' },
          { value: 'default',  title: 'Comfortable' },
          { value: 'spacious', title: 'Spacious' },
        ],
        dynamicTitle: true,
      },
    },
  },

  decorators: [
    (storyFn, context) => {
      const body = document.body;

      // Token system — sets data-token-system on body.
      // 'v1' means no attribute (cascade falls through to :root).
      // Experiments scope their vars to [data-token-system="<name>"].
      const sys = context.globals.tokenSystem ?? 'v1';
      if (sys === 'v1') {
        delete body.dataset.tokenSystem;
      } else {
        body.dataset.tokenSystem = sys;
      }

      // Mode axes — always applied regardless of token system.
      body.dataset.color    = context.globals.color    ?? 'light';
      body.dataset.contrast = context.globals.contrast ?? 'default';
      body.dataset.vision   = context.globals.vision   ?? 'default';
      body.dataset.density  = context.globals.density  ?? 'default';
      body.style.colorScheme = body.dataset.color;

      return storyFn();
    },
  ],
};

export default preview;
