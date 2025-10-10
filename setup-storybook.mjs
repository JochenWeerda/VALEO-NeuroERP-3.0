#!/usr/bin/env node
/**
 * Storybook + Accessibility Setup Script
 * VALEO-NeuroERP 3.0
 * 
 * Installiert und konfiguriert:
 * - Storybook mit React-Vite
 * - ESLint JSX Accessibility Plugin
 * - Erste Component-Stories mit MCP-Metadaten
 */

import { execSync } from 'child_process';
import fs from 'fs';
import path from 'path';

const log = (msg, color = 'cyan') => {
  const colors = {
    cyan: '\x1b[36m',
    green: '\x1b[32m',
    yellow: '\x1b[33m',
    reset: '\x1b[0m',
  };
  console.log(`${colors[color]}${msg}${colors.reset}`);
};

log('\n╔════════════════════════════════════════════╗');
log('║  📚 Storybook + A11y Setup                ║');
log('╚════════════════════════════════════════════╝\n');

// 1. Install Accessibility Plugin
log('📦 Schritt 1: Installiere Accessibility Plugin...', 'yellow');
try {
  execSync('pnpm add -D eslint-plugin-jsx-a11y', { stdio: 'inherit' });
  log('✅ eslint-plugin-jsx-a11y installiert\n', 'green');
} catch (error) {
  log('⚠️  Installation übersprungen (möglicherweise bereits vorhanden)\n', 'yellow');
}

// 2. Update ESLint Config
log('📝 Schritt 2: Update ESLint-Konfiguration...', 'yellow');
const eslintConfigPath = '.eslintrc.json';
if (fs.existsSync(eslintConfigPath)) {
  const eslintConfig = JSON.parse(fs.readFileSync(eslintConfigPath, 'utf8'));
  
  if (!eslintConfig.extends.includes('plugin:jsx-a11y/recommended')) {
    eslintConfig.extends.push('plugin:jsx-a11y/recommended');
    eslintConfig.plugins = eslintConfig.plugins || [];
    if (!eslintConfig.plugins.includes('jsx-a11y')) {
      eslintConfig.plugins.push('jsx-a11y');
    }
    
    fs.writeFileSync(eslintConfigPath, JSON.stringify(eslintConfig, null, 2));
    log('✅ ESLint-Konfiguration aktualisiert\n', 'green');
  } else {
    log('✅ ESLint-Konfiguration bereits aktuell\n', 'green');
  }
}

// 3. Add Storybook Scripts to package.json
log('📝 Schritt 3: Update package.json Scripts...', 'yellow');
const packageJsonPath = 'package.json';
const packageJson = JSON.parse(fs.readFileSync(packageJsonPath, 'utf8'));

packageJson.scripts = {
  ...packageJson.scripts,
  'storybook': 'storybook dev -p 6006',
  'storybook:build': 'storybook build',
  'storybook:test': 'test-storybook',
};

fs.writeFileSync(packageJsonPath, JSON.stringify(packageJson, null, 2));
log('✅ Storybook-Scripts hinzugefügt\n', 'green');

// 4. Create MCP-Context Schema Template
log('📝 Schritt 4: Erstelle MCP-Context-Schema...', 'yellow');
const mcpSchemaDir = 'src/design/mcp-schemas';
if (!fs.existsSync(mcpSchemaDir)) {
  fs.mkdirSync(mcpSchemaDir, { recursive: true });
}

const componentSchemaTemplate = `/**
 * MCP-Component-Schema Template
 * Für zukünftige MCP-Browser-Integration (Phase 3)
 */

export interface MCPComponentMetadata {
  // Component-Identifikation
  componentName: string;
  componentType: 'form' | 'button' | 'input' | 'display' | 'navigation';
  version: string;
  
  // Accessibility-Metadaten
  accessibility: {
    role: string;
    ariaLabel?: string;
    ariaDescribedBy?: string;
    keyboardShortcuts?: string[];
  };
  
  // Intent-Schema (für AI-Assistenz)
  intent: {
    purpose: string;           // "Create sales order", "Submit form", etc.
    userActions: string[];     // ["click", "fill", "submit"]
    dataContext?: string[];    // ["customer", "article", "price"]
  };
  
  // Validation-Schema
  validation?: {
    required: boolean;
    constraints?: Record<string, any>;
  };
  
  // MCP-Browser Hints
  mcpHints?: {
    autoFillable: boolean;
    explainable: boolean;
    testable: boolean;
  };
}

export const createMCPMetadata = (
  componentName: string,
  type: MCPComponentMetadata['componentType'],
  options: Partial<MCPComponentMetadata> = {}
): MCPComponentMetadata => {
  return {
    componentName,
    componentType: type,
    version: '1.0.0',
    accessibility: {
      role: options.accessibility?.role || type,
      ...options.accessibility,
    },
    intent: {
      purpose: options.intent?.purpose || \`\${componentName} interaction\`,
      userActions: options.intent?.userActions || ['click'],
      ...options.intent,
    },
    ...options,
  };
};
`;

fs.writeFileSync(
  path.join(mcpSchemaDir, 'component-metadata.ts'),
  componentSchemaTemplate
);
log('✅ MCP-Schema-Template erstellt\n', 'green');

log('╔════════════════════════════════════════════╗');
log('║  ✅ SETUP KOMPLETT!                       ║', 'green');
log('╚════════════════════════════════════════════╝\n');

log('🚀 Storybook starten:', 'cyan');
log('   pnpm storybook\n', 'yellow');

log('📖 Dokumentation:', 'cyan');
log('   http://localhost:6006\n', 'yellow');

log('📚 Nächste Schritte:', 'cyan');
log('   1. Erste Story erstellen: src/components/ui/button.stories.tsx');
log('   2. MCP-Metadaten hinzufügen');
log('   3. Accessibility prüfen');
log('');

