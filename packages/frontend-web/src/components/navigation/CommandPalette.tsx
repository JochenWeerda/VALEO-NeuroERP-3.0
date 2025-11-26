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

import { type ComponentType, useMemo, useState } from 'react'
import {
  CommandDialog,
  CommandEmpty,
  CommandGroup,
  CommandInput,
  CommandItem,
  CommandList,
  CommandSeparator,
} from '@/components/ui/command'
import { useNavigate } from 'react-router-dom'
import { Calculator, FileText, HelpCircle, Package, Settings, ShoppingCart, Sprout, Warehouse, Users, Target, Calendar, Tractor } from 'lucide-react'
import { createMCPMetadata } from '@/design/mcp-schemas/component-metadata'
import { useFeature } from '@/hooks/useFeature'

interface CommandPaletteProps {
  open: boolean
  onOpenChange: (_open: boolean) => void
}

interface PaletteCommand {
  id: string
  label: string
  keywords: string[]
  icon: ComponentType<{ className?: string }>
  action: () => void
  category: string
  mcp?: {
    intent: string
    businessDomain: string
    requiredScopes?: string[]
  }
}

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
    autoFillable: true,
    explainable: true,
    testable: true,
    contextAware: true,
  },
})

const createCommands = (navigate: ReturnType<typeof useNavigate>, agrarEnabled: boolean): PaletteCommand[] => {
  const commands: PaletteCommand[] = [
    {
      id: 'sales-order-new',
      label: 'Neuer Verkaufsauftrag',
      keywords: ['sales', 'order', 'so', 'auftrag', 'neu'],
      icon: ShoppingCart,
      category: 'Sales',
      action: (): void => navigate('/sales/orders/new'),
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
      action: (): void => navigate('/sales/deliveries/new'),
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
      action: (): void => navigate('/sales/invoices/new'),
      mcp: {
        intent: 'create-invoice',
        businessDomain: 'sales',
        requiredScopes: ['sales:write'],
      },
    },
    {
      id: 'crm-contacts-list',
      label: 'Kontakte anzeigen',
      keywords: ['crm', 'kontakte', 'contacts', 'liste'],
      icon: Users,
      category: 'CRM',
      action: (): void => navigate('/crm/kontakte-liste'),
      mcp: {
        intent: 'view-contacts',
        businessDomain: 'crm',
        requiredScopes: ['crm:read'],
      },
    },
    {
      id: 'crm-leads-list',
      label: 'Leads anzeigen',
      keywords: ['crm', 'leads', 'verkaufschancen', 'opportunities'],
      icon: Target,
      category: 'CRM',
      action: (): void => navigate('/crm/leads'),
      mcp: {
        intent: 'view-leads',
        businessDomain: 'crm',
        requiredScopes: ['crm:read'],
      },
    },
    {
      id: 'crm-activities-list',
      label: 'Aktivitäten anzeigen',
      keywords: ['crm', 'aktivitäten', 'activities', 'termine'],
      icon: Calendar,
      category: 'CRM',
      action: (): void => navigate('/crm/aktivitaeten'),
      mcp: {
        intent: 'view-activities',
        businessDomain: 'crm',
        requiredScopes: ['crm:read'],
      },
    },
    {
      id: 'crm-farmprofiles-list',
      label: 'Betriebsprofile anzeigen',
      keywords: ['crm', 'betriebsprofile', 'farm', 'landwirt'],
      icon: Tractor,
      category: 'CRM',
      action: (): void => navigate('/crm/betriebsprofile'),
      mcp: {
        intent: 'view-farm-profiles',
        businessDomain: 'crm',
        requiredScopes: ['crm:read'],
      },
    },
    {
      id: 'inventory-adjust',
      label: 'Bestandskorrektur',
      keywords: ['inventory', 'bestand', 'korrektur', 'adjust'],
      icon: Package,
      category: 'Lager',
      action: (): void => navigate('/inventory/adjust'),
      mcp: {
        intent: 'adjust-inventory',
        businessDomain: 'inventory',
      },
    },
    {
      id: 'finance-booking',
      label: 'Buchung erfassen',
      keywords: ['finance', 'buchung', 'fibu', 'booking'],
      icon: Calculator,
      category: 'Finanzen',
      action: (): void => navigate('/finance/bookings/new'),
      mcp: {
        intent: 'create-booking',
        businessDomain: 'finance',
      },
    },
  ];

  if (agrarEnabled) {
    commands.push(
      {
        id: 'agrar-seed-list',
        label: 'Saatgut-Liste oeffnen',
        keywords: ['agrar', 'saatgut', 'liste', 'seed'],
        icon: Sprout,
        category: 'Agrar',
        action: (): void => navigate('/agrar/saatgut'),
        mcp: {
          intent: 'open-seed-list',
          businessDomain: 'agrar',
        },
      },
      {
        id: 'agrar-seed-master',
        label: 'Saatgut Stammdaten',
        keywords: ['agrar', 'saatgut', 'stamm', 'detail'],
        icon: Sprout,
        category: 'Agrar',
        action: (): void => navigate('/agrar/saatgut/stamm?id=SEED-00123'),
        mcp: {
          intent: 'open-seed-master',
          businessDomain: 'agrar',
        },
      },
      {
        id: 'agrar-seed-order',
        label: 'Saatgut-Bestellung anlegen',
        keywords: ['agrar', 'saatgut', 'bestellung', 'wizard'],
        icon: ShoppingCart,
        category: 'Agrar',
        action: (): void => navigate('/agrar/saatgut/bestellung'),
        mcp: {
          intent: 'create-seed-order',
          businessDomain: 'agrar',
        },
      },
      {
        id: 'agrar-fertilizer-list',
        label: 'Duenger-Liste oeffnen',
        keywords: ['agrar', 'duenger', 'fertilizer', 'liste'],
        icon: Warehouse,
        category: 'Agrar',
        action: (): void => navigate('/agrar/duenger'),
        mcp: {
          intent: 'open-fertilizer-list',
          businessDomain: 'agrar',
        },
      },
    );
  }

  commands.push(
    {
      id: 'settings',
      label: 'Systemeinstellungen',
      keywords: ['system', 'settings', 'einstellungen'],
      icon: Settings,
      category: 'System',
      action: (): void => navigate('/settings'),
      mcp: {
        intent: 'configure-system',
        businessDomain: 'admin',
        requiredScopes: ['admin:all'],
      },
    },
    {
      id: 'help-ai',
      label: 'Ask VALEO (AI-Hilfe)',
      keywords: ['help', 'hilfe', 'ai', 'ask', 'frage'],
      icon: HelpCircle,
      category: 'Hilfe',
      action: (): void => {
        if (import.meta.env.DEV) {
          console.info('AI-Hilfe wird in Phase 3 aktiviert (MCP-Browser)');
        }
      },
      mcp: {
        intent: 'ai-assistance',
        businessDomain: 'help',
      },
    },
  );

  return commands;
};

export function CommandPalette({ open, onOpenChange }: CommandPaletteProps): JSX.Element {
  const navigate = useNavigate()
  const agrarEnabled = useFeature('agrar')
  const [search, setSearch] = useState<string>('')

  const commands = useMemo<PaletteCommand[]>(() => {
    const baseCommands = createCommands(navigate, agrarEnabled)
    return agrarEnabled ? baseCommands : baseCommands.filter((cmd) => cmd.category !== 'Agrar')
  }, [agrarEnabled, navigate])

  const filteredCommands = useMemo(() => {
    const searchLower = search.trim().toLowerCase()
    if (searchLower.length === 0) {
      return commands
    }
    return commands.filter((cmd) => {
      return (
        cmd.label.toLowerCase().includes(searchLower) ||
        cmd.keywords.some((keyword) => keyword.toLowerCase().includes(searchLower))
      )
    })
  }, [commands, search])

  const groupedCommands = useMemo(() => {
    return filteredCommands.reduce<Record<string, PaletteCommand[]>>((accumulator, cmd) => {
      if (accumulator[cmd.category] === undefined) {
        accumulator[cmd.category] = []
      }
      accumulator[cmd.category].push(cmd)
      return accumulator
    }, {})
  }, [filteredCommands])

  return (
    <CommandDialog
      open={open}
      onOpenChange={onOpenChange}
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
            Tipp: Versuche allgemeinere Begriffe wie &quot;Auftrag&quot; oder &quot;Kunde&quot;
          </div>
        </CommandEmpty>

        {Object.entries(groupedCommands).map(([category, cmds], idx) => (
          <div key={category}>
            {idx > 0 && <CommandSeparator />}
            <CommandGroup heading={category}>
              {cmds.map((cmd) => {
                const Icon = cmd.icon
                return (
                  <CommandItem
                    key={cmd.id}
                    value={cmd.label}
                    keywords={cmd.keywords}
                    onSelect={() => {
                      cmd.action()
                      onOpenChange(false)
                    }}
                    data-mcp-action={cmd.id}
                    data-mcp-intent={cmd.mcp?.intent}
                    data-mcp-domain={cmd.mcp?.businessDomain}
                  >
                    <Icon className="mr-2 h-4 w-4" />
                    <span>{cmd.label}</span>
                    {cmd.mcp?.requiredScopes && (
                      <span className="ml-auto text-xs text-muted-foreground">{cmd.mcp.requiredScopes[0]}</span>
                    )}
                  </CommandItem>
                )
              })}
            </CommandGroup>
          </div>
        ))}

        {(search.toLowerCase().includes('ai') || search.toLowerCase().includes('help')) && (
          <>
            <CommandSeparator />
            <CommandGroup heading="Ask VALEO">
              <CommandItem
                value="Ask VALEO"
                onSelect={() => {
                  navigate('/copilot')
                  onOpenChange(false)
                }}
              >
                <HelpCircle className="mr-2 h-4 w-4" />
                Ask VALEO öffnen
              </CommandItem>
            </CommandGroup>
          </>
        )}
      </CommandList>
    </CommandDialog>
  )
}

