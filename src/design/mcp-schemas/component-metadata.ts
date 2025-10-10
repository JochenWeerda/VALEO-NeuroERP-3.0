/**
 * MCP-Component-Schema
 * Vorbereitung für MCP-Browser-Integration (Phase 3)
 * 
 * Diese Metadaten ermöglichen:
 * - AI-gestützte Formular-Assistenz
 * - Kontext-bewusste UI-Erklärungen
 * - Automatisches Testing via MCP-Browser
 * - LLM-Integration für "Explain this component"
 */

export interface MCPComponentMetadata {
  // Component-Identifikation
  componentName: string;
  componentType: 'form' | 'button' | 'input' | 'display' | 'navigation' | 'dialog' | 'table';
  version: string;
  
  // Accessibility-Metadaten (WCAG 2.1)
  accessibility: {
    role: string;
    ariaLabel?: string;
    ariaDescribedBy?: string;
    ariaLive?: 'polite' | 'assertive' | 'off';
    keyboardShortcuts?: string[];
    focusable: boolean;
  };
  
  // Intent-Schema (für AI-Assistenz)
  intent: {
    purpose: string;           // "Create sales order", "Submit form", etc.
    userActions: string[];     // ["click", "fill", "submit"]
    dataContext?: string[];    // ["customer", "article", "price"]
    businessDomain?: string;   // "sales", "inventory", "finance"
  };
  
  // Validation-Schema
  validation?: {
    required: boolean;
    constraints?: Record<string, any>;
    errorMessages?: Record<string, string>;
  };
  
  // MCP-Browser Hints (Phase 3)
  mcpHints?: {
    autoFillable: boolean;      // Kann von AI ausgefüllt werden?
    explainable: boolean;       // Kann von AI erklärt werden?
    testable: boolean;          // Automatisch testbar?
    contextAware: boolean;      // Nutzt Kontext-Daten?
  };
  
  // Design-System-Referenz
  designSystem?: {
    tokens: string[];          // ["primary-color", "spacing-md"]
    variants: string[];        // ["default", "destructive", "outline"]
    theme: 'light' | 'dark' | 'auto';
  };
}

/**
 * Factory-Funktion für MCP-Metadaten
 */
export const createMCPMetadata = (
  componentName: string,
  type: MCPComponentMetadata['componentType'],
  options: Partial<MCPComponentMetadata> = {}
): MCPComponentMetadata => {
  return {
    componentName,
    componentType: type,
    version: options.version || '1.0.0',
    accessibility: {
      role: options.accessibility?.role || type,
      focusable: options.accessibility?.focusable ?? true,
      ...options.accessibility,
    },
    intent: {
      purpose: options.intent?.purpose || `${componentName} interaction`,
      userActions: options.intent?.userActions || ['click'],
      dataContext: options.intent?.dataContext || [],
      businessDomain: options.intent?.businessDomain,
    },
    validation: options.validation,
    mcpHints: {
      autoFillable: false,
      explainable: true,
      testable: true,
      contextAware: false,
      ...options.mcpHints,
    },
    designSystem: options.designSystem,
  };
};

/**
 * Exportiere MCP-Metadata als JSON (für MCP-Browser)
 */
export const serializeMCPMetadata = (metadata: MCPComponentMetadata): string => {
  return JSON.stringify(metadata, null, 2);
};

/**
 * MCP-Context-Provider (für Phase 3)
 * Später: Integration mit @modelcontext/browser-adapter
 */
export interface MCPContext {
  component: MCPComponentMetadata;
  userIntent?: string;
  dataContext?: Record<string, any>;
  llmHints?: string[];
}

export const createMCPContext = (
  metadata: MCPComponentMetadata,
  additionalContext: Partial<MCPContext> = {}
): MCPContext => {
  return {
    component: metadata,
    ...additionalContext,
  };
};

