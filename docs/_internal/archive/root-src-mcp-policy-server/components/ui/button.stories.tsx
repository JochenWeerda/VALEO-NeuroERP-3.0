import type { Meta, StoryObj } from '@storybook/react';
import { Button } from './button';
import { createMCPMetadata } from '../../design/mcp-schemas/component-metadata';

// MCP-Metadaten für Button-Component (Phase 3 Vorbereitung)
const buttonMCPMetadata = createMCPMetadata('Button', 'button', {
  accessibility: {
    role: 'button',
    ariaLabel: 'Action button',
    focusable: true,
    keyboardShortcuts: ['Enter', 'Space'],
  },
  intent: {
    purpose: 'Trigger user action or submit data',
    userActions: ['click', 'keyboard-activate'],
    businessDomain: 'ui-primitives',
  },
  mcpHints: {
    autoFillable: false,
    explainable: true,
    testable: true,
    contextAware: false,
  },
  designSystem: {
    tokens: ['primary-color', 'spacing-md', 'border-radius'],
    variants: ['default', 'destructive', 'outline', 'secondary', 'ghost', 'link'],
    theme: 'auto',
  },
});

const meta: Meta<typeof Button> = {
  title: 'UI/Button',
  component: Button,
  parameters: {
    layout: 'centered',
    // MCP-Metadata im Storybook (für Phase 3)
    mcp: {
      metadata: buttonMCPMetadata,
      contextSchema: {
        type: 'component',
        category: 'ui-primitives',
        aiExplainable: true,
      },
    },
  },
  tags: ['autodocs'],
  argTypes: {
    variant: {
      control: 'select',
      options: ['default', 'destructive', 'outline', 'secondary', 'ghost', 'link'],
      description: 'Visual variant of the button',
      table: {
        type: { summary: 'string' },
        defaultValue: { summary: 'default' },
      },
    },
    size: {
      control: 'select',
      options: ['default', 'sm', 'lg', 'icon'],
      description: 'Size of the button',
    },
    disabled: {
      control: 'boolean',
      description: 'Disable button interaction',
    },
  },
};

export default meta;
type Story = StoryObj<typeof Button>;

// Stories mit verschiedenen Variants
export const Default: Story = {
  args: {
    children: 'Button',
    variant: 'default',
  },
  parameters: {
    docs: {
      description: {
        story: 'Standard-Button für primäre Aktionen (z.B. "Submit", "Save")',
      },
    },
  },
};

export const Destructive: Story = {
  args: {
    children: 'Delete',
    variant: 'destructive',
  },
  parameters: {
    docs: {
      description: {
        story: 'Destruktive Aktionen (z.B. "Delete", "Remove"). Nutzer-Bestätigung empfohlen!',
      },
    },
    // MCP-Hint: Destruktive Aktion erfordert Confirmation
    mcp: {
      requiresConfirmation: true,
      confirmationPrompt: 'Are you sure you want to delete this item?',
    },
  },
};

export const Outline: Story = {
  args: {
    children: 'Outline',
    variant: 'outline',
  },
  parameters: {
    docs: {
      description: {
        story: 'Sekundäre Aktionen oder alternative Optionen',
      },
    },
  },
};

export const Secondary: Story = {
  args: {
    children: 'Secondary',
    variant: 'secondary',
  },
};

export const Ghost: Story = {
  args: {
    children: 'Ghost',
    variant: 'ghost',
  },
  parameters: {
    docs: {
      description: {
        story: 'Minimaler Button für subtile Aktionen',
      },
    },
  },
};

export const Link: Story = {
  args: {
    children: 'Link',
    variant: 'link',
  },
};

// Size Variations
export const Small: Story = {
  args: {
    children: 'Small Button',
    size: 'sm',
  },
};

export const Large: Story = {
  args: {
    children: 'Large Button',
    size: 'lg',
  },
};

export const Icon: Story = {
  args: {
    children: '🔍',
    size: 'icon',
  },
  parameters: {
    docs: {
      description: {
        story: 'Icon-only Button (gleiche Breite/Höhe)',
      },
    },
  },
};

// States
export const Disabled: Story = {
  args: {
    children: 'Disabled',
    disabled: true,
  },
  parameters: {
    docs: {
      description: {
        story: 'Deaktivierter Zustand - keine Interaktion möglich',
      },
    },
  },
};

// MCP-Integration Beispiel (Phase 3)
export const WithMCPContext: Story = {
  args: {
    children: 'Create Sales Order',
    variant: 'default',
  },
  parameters: {
    docs: {
      description: {
        story: '**MCP-Integrationsbeispiel (Phase 3):** Button mit Kontext-Metadaten für AI-Assistenz',
      },
    },
    // MCP-Context für AI-Assistenz
    mcp: {
      context: {
        userIntent: 'create-sales-order',
        requiredData: ['customer', 'articles', 'delivery-date'],
        nextSteps: ['fill-customer', 'add-articles', 'set-date', 'submit'],
        llmPrompt: 'This button creates a new sales order. It requires customer selection, article list, and delivery date.',
      },
    },
  },
};

