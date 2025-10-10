/**
 * Command Palette - Herzstück der modernen Navigation
 * Ersetzt Ribbon-Overload durch beschreibbare Aktionen
 * 
 * Features:
 * - Ctrl/Cmd+K zum Öffnen
 * - Fuzzy-Search über alle Aktionen
 * - Kategorisiert nach Domäne
 * - Keyboard-Navigation
 * - MCP-Ready für AI-Integration
 */

import { useEffect, useState } from 'react';
import {
  Command,
  CommandDialog,
  CommandEmpty,
  CommandGroup,
  CommandInput,
  CommandItem,
  CommandList,
  CommandSeparator,
} from '@/components/ui/command';
import { useNavigate } from 'react-router-dom';
import {
  FileText,
  Package,
  ShoppingCart,
  Users,
  Calculator,
  Settings,
  Search,
  HelpCircle,
} from 'lucide-react';
import { createMCPMetadata } from '@/design/mcp-schemas/component-metadata';

interface CommandPaletteProps {
  open: boolean;
  onOpenChange: (open: boolean) => void;
}

// MCP-Metadaten für Command Palette
export const commandPaletteMCP = createMCPMetadata('CommandPalette', 'navigation', {
  accessibility: {
    role: 'dialog',
    ariaLabel: 'Command palette for quick navigation',
    keyboardShortcuts: ['Ctrl+K', 'Cmd+K', 'Escape'],
    focusable: true,
  },
  intent: {
    purpose: 'Quick access to all system functions via search',
    userActions: ['search', 'select', 'navigate'],
    businessDomain: 'core',
  },
  mcpHints: {
    autoFillable: true,       // AI kann Suchbegriff vorschlagen
    explainable: true,         // AI kann verfügbare Commands erklären
    testable: true,
    contextAware: true,        // Kontext-abhängige Vorschläge
  },
});

// Command-Registry (MCP-ready)
interface Command {
  id: string;
  label: string;
  keywords: string[];
  icon: React.ComponentType<{ className?: string }>;
  action: () => void;
  category: string;
  // MCP-Metadaten
  mcp?: {
    intent: string;
    businessDomain: string;
    requiredScopes?: string[];
  };
}

export function CommandPalette({ open, onOpenChange }: CommandPaletteProps) {
  const navigate = useNavigate();
  const [search, setSearch] = useState('');

  // Command-Registry mit MCP-Metadaten
  const commands: Command[] = [
    // Sales
    {
      id: 'sales-order-new',
      label: 'Neuer Verkaufsauftrag',
      keywords: ['sales', 'order', 'so', 'auftrag', 'neu'],
      icon: ShoppingCart,
      category: 'Sales',
      action: () => navigate('/sales/orders/new'),
      mcp: {
        intent: 'create-sales-order',
        businessDomain: 'sales',
        requiredScopes: ['sales:write'],
      },
    },
    {
      id: 'sales-delivery-new',
      label: 'Neue Lieferung',
      keywords: ['sales', 'delivery', 'lieferung', 'versand'],
      icon: Package,
      category: 'Sales',
      action: () => navigate('/sales/deliveries/new'),
      mcp: {
        intent: 'create-delivery',
        businessDomain: 'sales',
        requiredScopes: ['sales:write'],
      },
    },
    {
      id: 'sales-invoice-new',
      label: 'Neue Rechnung',
      keywords: ['sales', 'invoice', 'rechnung', 'faktura'],
      icon: FileText,
      category: 'Sales',
      action: () => navigate('/sales/invoices/new'),
      mcp: {
        intent: 'create-invoice',
        businessDomain: 'sales',
        requiredScopes: ['sales:write'],
      },
    },

    // Inventory
    {
      id: 'inventory-adjust',
      label: 'Bestandskorrektur',
      keywords: ['inventory', 'bestand', 'korrektur', 'adjust'],
      icon: Package,
      category: 'Lager',
      action: () => navigate('/inventory/adjust'),
      mcp: {
        intent: 'adjust-inventory',
        businessDomain: 'inventory',
      },
    },

    // Finance
    {
      id: 'finance-booking',
      label: 'Buchung erfassen',
      keywords: ['finance', 'buchung', 'fibu', 'booking'],
      icon: Calculator,
      category: 'Finanzen',
      action: () => navigate('/finance/bookings/new'),
      mcp: {
        intent: 'create-booking',
        businessDomain: 'finance',
      },
    },

    // Customers
    {
      id: 'customers-list',
      label: 'Kunden anzeigen',
      keywords: ['customers', 'kunden', 'debitor'],
      icon: Users,
      category: 'Stammdaten',
      action: () => navigate('/customers'),
      mcp: {
        intent: 'view-customers',
        businessDomain: 'master-data',
      },
    },

    // Settings
    {
      id: 'settings',
      label: 'Einstellungen',
      keywords: ['settings', 'einstellungen', 'config'],
      icon: Settings,
      category: 'System',
      action: () => navigate('/settings'),
      mcp: {
        intent: 'configure-system',
        businessDomain: 'admin',
        requiredScopes: ['admin:all'],
      },
    },

    // Help (MCP-Integration Beispiel)
    {
      id: 'help-ai',
      label: 'Ask VALEO (AI-Hilfe)',
      keywords: ['help', 'hilfe', 'ai', 'ask', 'frage'],
      icon: HelpCircle,
      category: 'Hilfe',
      action: () => {
        // Phase 3: Öffnet AI-Chat-Interface
        console.log('AI-Hilfe wird in Phase 3 aktiviert (MCP-Browser)');
      },
      mcp: {
        intent: 'ai-assistance',
        businessDomain: 'help',
      },
    },
  ];

  // Fuzzy-Search (einfache Implementation)
  const filteredCommands = commands.filter((cmd) => {
    const searchLower = search.toLowerCase();
    return (
      cmd.label.toLowerCase().includes(searchLower) ||
      cmd.keywords.some((kw) => kw.includes(searchLower))
    );
  });

  // Gruppiere nach Kategorie
  const groupedCommands = filteredCommands.reduce((acc, cmd) => {
    if (!acc[cmd.category]) {
      acc[cmd.category] = [];
    }
    acc[cmd.category].push(cmd);
    return acc;
  }, {} as Record<string, Command[]>);

  return (
    <CommandDialog 
      open={open} 
      onOpenChange={onOpenChange}
      // MCP-Metadaten
      aria-label="Command palette"
      data-mcp-component="command-palette"
    >
      <CommandInput 
        placeholder="Aktion suchen... (z.B. 'Auftrag', 'Buchung')" 
        value={search}
        onValueChange={setSearch}
      />
      <CommandList>
        <CommandEmpty>
          Keine Aktionen gefunden.
          <div className="mt-2 text-xs text-muted-foreground">
            Tipp: Versuche allgemeinere Begriffe wie "Auftrag" oder "Kunde"
          </div>
        </CommandEmpty>

        {Object.entries(groupedCommands).map(([category, cmds], idx) => (
          <div key={category}>
            {idx > 0 && <CommandSeparator />}
            <CommandGroup heading={category}>
              {cmds.map((cmd) => {
                const Icon = cmd.icon;
                return (
                  <CommandItem
                    key={cmd.id}
                    value={cmd.label}
                    keywords={cmd.keywords}
                    onSelect={() => {
                      cmd.action();
                      onOpenChange(false);
                    }}
                    // MCP-Metadaten für einzelne Actions
                    data-mcp-action={cmd.id}
                    data-mcp-intent={cmd.mcp?.intent}
                    data-mcp-domain={cmd.mcp?.businessDomain}
                  >
                    <Icon className="mr-2 h-4 w-4" />
                    <span>{cmd.label}</span>
                    {cmd.mcp?.requiredScopes && (
                      <span className="ml-auto text-xs text-muted-foreground">
                        {cmd.mcp.requiredScopes[0]}
                      </span>
                    )}
                  </CommandItem>
                );
              })}
            </CommandGroup>
          </div>
        ))}

        {/* MCP-Integration Hinweis (Phase 3) */}
        {search.includes('ai') || search.includes('help') && (
          <>
            <CommandSeparator />
            <CommandGroup heading="💡 Tipp">
              <CommandItem disabled>
                <HelpCircle className="mr-2 h-4 w-4" />
                <span className="text-xs">
                  AI-Assistenz kommt in Phase 3 (MCP-Browser)
                </span>
              </CommandItem>
            </CommandGroup>
          </>
        )}
      </CommandList>
    </CommandDialog>
  );
}

