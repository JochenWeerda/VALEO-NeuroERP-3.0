import type { Preview } from '@storybook/react';
import '../src/index.css';

const preview: Preview = {
  parameters: {
    actions: { argTypesRegex: '^on[A-Z].*' },
    controls: {
      matchers: {
        color: /(background|color)$/i,
        date: /Date$/i,
      },
    },
    // MCP-Metadata für zukünftige Integration
    mcp: {
      enabled: true,
      version: '1.0.0',
      contextSchemas: true, // Component-Schemas für MCP-Browser
    },
  },
};

export default preview;

