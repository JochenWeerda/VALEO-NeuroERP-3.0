/**
 * VALEO Skill Registry
 * Inspiriert von SAP Joule Studio
 * 
 * Skills = Kleine, fokussierte AI-Funktionen
 * Agents = Orchestrieren mehrere Skills
 * 
 * Architektur:
 * - Skills: Atomar, wiederverwendbar, testbar
 * - Agents: Workflows, Multi-Step, Decision-Making
 * - MCP-Integration: Skills = MCP-Tools, Agents = MCP-Prompts
 */

import { createMCPMetadata } from '@/design/mcp-schemas/component-metadata';

/**
 * Skill-Definition (angelehnt an SAP Joule Studio)
 */
export interface ValeoSkill {
  id: string;
  name: string;
  description: string;
  category: 'data-retrieval' | 'data-modification' | 'analysis' | 'workflow';
  
  // Eingabe-Schema
  input: {
    parameters: Record<string, {
      type: string;
      required: boolean;
      description: string;
    }>;
  };
  
  // Ausgabe-Schema
  output: {
    type: string;
    schema: any;
  };
  
  // Erforderliche Scopes
  requiredScopes: string[];
  
  // MCP-Metadaten
  mcp: {
    toolName: string;
    grounding: 'user-data' | 'system-data' | 'none';
    explainable: boolean;
  };
  
  // Ausführungs-Funktion (Phase 3)
  execute?: (params: any, context: any) => Promise<any>;
}

/**
 * Agent-Definition (Multi-Step-Workflows)
 */
export interface ValeoAgent {
  id: string;
  name: string;
  description: string;
  skills: string[];  // Referenz zu Skill-IDs
  
  workflow: {
    steps: Array<{
      skillId: string;
      condition?: (context: any) => boolean;
      onSuccess?: string;  // Nächster Step
      onError?: string;    // Fehler-Handling
    }>;
  };
  
  // MCP-Integration
  mcp: {
    promptTemplate: string;
    contextRequired: string[];
  };
}

/**
 * Skill-Registry (vorkonfigurierte Skills)
 */
export const valeoSkills: ValeoSkill[] = [
  // Skill 1: Kunden suchen
  {
    id: 'search-customer',
    name: 'Kunde suchen',
    description: 'Sucht Kunden nach Name, Nummer oder Ort',
    category: 'data-retrieval',
    input: {
      parameters: {
        query: {
          type: 'string',
          required: true,
          description: 'Suchbegriff (Name, Nummer, Ort)',
        },
      },
    },
    output: {
      type: 'array',
      schema: { /* CustomerSchema */ },
    },
    requiredScopes: ['sales:read', 'crm:read'],
    mcp: {
      toolName: 'searchCustomer',
      grounding: 'user-data',
      explainable: true,
    },
  },

  // Skill 2: Artikel-Preis abrufen
  {
    id: 'get-article-price',
    name: 'Artikel-Preis abrufen',
    description: 'Holt aktuellen Verkaufspreis für Artikel',
    category: 'data-retrieval',
    input: {
      parameters: {
        articleNumber: {
          type: 'string',
          required: true,
          description: 'Artikel-Nummer',
        },
        customer: {
          type: 'string',
          required: false,
          description: 'Kunde (für kundenspezifische Preise)',
        },
      },
    },
    output: {
      type: 'object',
      schema: { price: 'number', currency: 'string' },
    },
    requiredScopes: ['sales:read'],
    mcp: {
      toolName: 'getArticlePrice',
      grounding: 'system-data',
      explainable: true,
    },
  },

  // Skill 3: Verkaufsauftrag erstellen
  {
    id: 'create-sales-order',
    name: 'Verkaufsauftrag erstellen',
    description: 'Erstellt einen neuen Verkaufsauftrag',
    category: 'data-modification',
    input: {
      parameters: {
        customer: { type: 'string', required: true, description: 'Kunden-ID' },
        articles: { type: 'array', required: true, description: 'Artikel-Liste' },
        deliveryDate: { type: 'date', required: false, description: 'Lieferdatum' },
      },
    },
    output: {
      type: 'object',
      schema: { orderId: 'string', status: 'string' },
    },
    requiredScopes: ['sales:write'],
    mcp: {
      toolName: 'createSalesOrder',
      grounding: 'user-data',
      explainable: true,
    },
  },

  // Skill 4: Policy-Check ausführen
  {
    id: 'check-policy',
    name: 'Policy-Check',
    description: 'Prüft ob Aktion gegen Policies verstößt',
    category: 'analysis',
    input: {
      parameters: {
        action: { type: 'string', required: true, description: 'Aktion (z.B. "submit-order")' },
        data: { type: 'object', required: true, description: 'Zu prüfende Daten' },
      },
    },
    output: {
      type: 'object',
      schema: { violations: 'array', warnings: 'array', allowed: 'boolean' },
    },
    requiredScopes: ['policy:read'],
    mcp: {
      toolName: 'checkPolicy',
      grounding: 'system-data',
      explainable: true,
    },
  },

  // Skill 5: Bestandsprüfung
  {
    id: 'check-stock',
    name: 'Bestand prüfen',
    description: 'Prüft verfügbaren Bestand für Artikel',
    category: 'data-retrieval',
    input: {
      parameters: {
        articleNumber: { type: 'string', required: true, description: 'Artikel-Nummer' },
        warehouse: { type: 'string', required: false, description: 'Lager' },
      },
    },
    output: {
      type: 'object',
      schema: { available: 'number', reserved: 'number', incoming: 'number' },
    },
    requiredScopes: ['inventory:read'],
    mcp: {
      toolName: 'checkStock',
      grounding: 'system-data',
      explainable: true,
    },
  },
];

/**
 * Agent-Registry (Workflow-Orchestrierung)
 */
export const valeoAgents: ValeoAgent[] = [
  // Agent 1: Auftrags-Assistent
  {
    id: 'order-assistant',
    name: 'Auftrags-Assistent',
    description: 'Hilft beim Erstellen von Verkaufsaufträgen mit Preis- und Bestandsprüfung',
    skills: ['search-customer', 'get-article-price', 'check-stock', 'check-policy', 'create-sales-order'],
    workflow: {
      steps: [
        {
          skillId: 'search-customer',
          onSuccess: 'get-article-price',
        },
        {
          skillId: 'get-article-price',
          onSuccess: 'check-stock',
        },
        {
          skillId: 'check-stock',
          condition: (ctx) => ctx.stock.available > 0,
          onSuccess: 'check-policy',
          onError: 'notify-out-of-stock',
        },
        {
          skillId: 'check-policy',
          condition: (ctx) => ctx.policy.allowed,
          onSuccess: 'create-sales-order',
          onError: 'notify-policy-violation',
        },
        {
          skillId: 'create-sales-order',
        },
      ],
    },
    mcp: {
      promptTemplate: `Du bist ein Verkaufsauftrag-Assistent für VALEO-ERP.
        Hilf dem Benutzer beim Erstellen eines Auftrags:
        1. Finde den Kunden
        2. Prüfe Artikel-Preise
        3. Prüfe Bestand
        4. Prüfe Policies
        5. Erstelle Auftrag
        
        Sei präzise, freundlich und erkläre jeden Schritt.`,
      contextRequired: ['user-permissions', 'current-page'],
    },
  },

  // Agent 2: Nachbestell-Assistent
  {
    id: 'reorder-assistant',
    name: 'Nachbestell-Assistent',
    description: 'Identifiziert Artikel unter Mindestbestand und schlägt Nachbestellungen vor',
    skills: ['check-stock'],
    workflow: {
      steps: [
        {
          skillId: 'check-stock',
          condition: (ctx) => ctx.stock.available < ctx.stock.minLevel,
          onSuccess: 'suggest-reorder',
        },
      ],
    },
    mcp: {
      promptTemplate: `Analysiere Bestände und schlage Nachbestellungen vor.
        Berücksichtige: Mindestbestand, Lieferzeit, Lagerkosten.`,
      contextRequired: ['inventory-data', 'supplier-data'],
    },
  },
];

/**
 * Skill-Executor (Phase 3)
 */
export class SkillExecutor {
  constructor(private mcpClient?: any) {}

  async executeSkill(skillId: string, params: any, context: any): Promise<any> {
    const skill = valeoSkills.find((s) => s.id === skillId);
    if (!skill) {
      throw new Error(`Skill not found: ${skillId}`);
    }

    // Phase 3: Echte MCP-Tool-Ausführung
    // return await this.mcpClient.executeTool(skill.mcp.toolName, params);

    // Aktuell: Mock
    console.log(`[Skill] Executing: ${skill.name}`, { params, context });
    return { success: true, data: {} };
  }

  async executeAgent(agentId: string, initialContext: any): Promise<any> {
    const agent = valeoAgents.find((a) => a.id === agentId);
    if (!agent) {
      throw new Error(`Agent not found: ${agentId}`);
    }

    // Phase 3: Multi-Step-Workflow mit MCP
    console.log(`[Agent] Executing: ${agent.name}`);
    
    let context = { ...initialContext };
    for (const step of agent.workflow.steps) {
      const result = await this.executeSkill(step.skillId, {}, context);
      context = { ...context, ...result.data };
    }

    return context;
  }
}

