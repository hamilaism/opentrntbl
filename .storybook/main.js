/** @type { import('@storybook/html-vite').StorybookConfig } */
const config = {
  stories: ['../design/components/**/*.stories.@(js|jsx|ts|tsx)'],
  addons: [
    '@storybook/addon-docs',
    '@storybook/addon-a11y',
    '@storybook/addon-vitest',
    'storybook-addon-pseudo-states',
  ],
  framework: {
    name: '@storybook/html-vite',
    options: {},
  },
  core: {
    disableTelemetry: true,
  },
};

export default config;
