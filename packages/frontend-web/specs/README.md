# VALEO NeuroERP Frontend Specifications

This directory contains automatically generated component specifications using Spec Kit.

## Directory Structure

```
specs/
├── components/          # UI component specifications
│   ├── ui/             # Base UI components (Button, Card, etc.)
│   ├── forms/          # Form components
│   └── layout/         # Layout components
├── features/           # Feature-specific component specs
│   ├── inventory/      # Inventory management components
│   ├── sales/          # Sales components
│   ├── finance/        # Finance components
│   └── hr/             # HR components
├── pages/              # Page-level specifications
└── shared/             # Shared component specs
```

## Specification Format

Each `.spec.json` file contains:

- **Component metadata**: Name, description, version
- **Props interface**: TypeScript prop definitions
- **Style tokens**: Tailwind classes and design tokens
- **Variants**: Different component states/variants
- **Events**: Component event handlers
- **Accessibility**: A11y compliance information
- **Dependencies**: Required imports and dependencies

## Usage in Development

### For Planners
```json
{
  "feature": "Inventory Slotting",
  "spec": "./specs/features/inventory/slotting.spec.json",
  "owner": "UI-Team",
  "status": "planned"
}
```

### For Developers
```typescript
// Component implementation follows spec
import { Button } from './specs/components/ui/button.spec.json';

// Implementation must match spec requirements
```

### For GENXAIS Agents
- **VAN Phase**: Specs define vision and requirements
- **PLAN Phase**: Tasks derived from spec analysis
- **CREATE Phase**: Code generation using specs as context
- **REFLECT Phase**: Automatic spec validation and updates

## Generation

Specs are automatically generated using:

```bash
# Generate all specs
pnpm spec-kit generate

# Generate specific component specs
pnpm spec-kit generate --component Button

# Validate specs against design system
pnpm spec-kit validate
```

## Integration with Design System

Specs are synchronized with:
- **Tailwind Config**: Color and spacing tokens
- **Component Library**: shadcn/ui components
- **Design Tokens**: Consistent styling variables

## Quality Assurance

- **Accessibility**: WCAG 2.1 AA compliance
- **Responsive**: Mobile-first design validation
- **Performance**: Bundle size and rendering metrics
- **Consistency**: Design system adherence

## Maintenance

- Specs are auto-updated when components change
- Manual review required for breaking changes
- Version control ensures spec evolution tracking
- CI/CD validates spec compliance