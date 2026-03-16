import type { ComponentType } from 'react'
import {
  Calculator,
  Calendar,
  FileText,
  HelpCircle,
  Package,
  Settings,
  ShoppingCart,
  Sprout,
  Target,
  Tractor,
  Users,
  Warehouse,
} from 'lucide-react'
import { ACTION_SHORTCUTS } from '@/app/navigation/action-shortcuts'
import { AI_SHORTCUTS } from '@/app/navigation/ai-shortcuts'
import type { NavigationShortcut } from '@/app/navigation/types'
import type { MaskRegistryEntry } from '@/lib/api/mask-registry'

export interface PaletteCommand {
  id: string
  label: string
  keywords: string[]
  icon: ComponentType<{ className?: string }>
  actionId: string
  actionParams?: Record<string, unknown>
  category: string
  shortcut?: string
  hint?: string
  mcp?: {
    intent: string
    businessDomain: string
    requiredScopes?: string[]
  }
}

interface BuildPaletteCommandsOptions {
  agrarEnabled: boolean
  navigationShortcuts: NavigationShortcut[]
  maskRegistry?: MaskRegistryEntry[]
}

const BASE_COMMANDS: PaletteCommand[] = [
  {
    id: 'sales-order-new',
    label: 'Neuer Verkaufsauftrag',
    keywords: ['sales', 'order', 'so', 'auftrag', 'neu'],
    icon: ShoppingCart,
    category: 'Sales',
    actionId: 'sales-order-new',
    actionParams: { path: '/sales/orders/new' },
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
    actionId: 'sales-delivery-new',
    actionParams: { path: '/sales/deliveries/new' },
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
    actionId: 'sales-invoice-new',
    actionParams: { path: '/sales/invoices/new' },
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
    actionId: 'crm-contacts-list',
    actionParams: { path: '/crm/kontakte-liste' },
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
    actionId: 'crm-leads-list',
    actionParams: { path: '/crm/leads' },
    mcp: {
      intent: 'view-leads',
      businessDomain: 'crm',
      requiredScopes: ['crm:read'],
    },
  },
  {
    id: 'crm-activities-list',
    label: 'Aktivitaeten anzeigen',
    keywords: ['crm', 'aktivitaeten', 'activities', 'termine'],
    icon: Calendar,
    category: 'CRM',
    actionId: 'crm-activities-list',
    actionParams: { path: '/crm/aktivitaeten' },
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
    actionId: 'crm-farmprofiles-list',
    actionParams: { path: '/crm/betriebsprofile' },
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
    actionId: 'inventory-adjust',
    actionParams: { path: '/inventory/adjust' },
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
    actionId: 'finance-booking',
    actionParams: { path: '/finance/bookings/new' },
    mcp: {
      intent: 'create-booking',
      businessDomain: 'finance',
    },
  },
  {
    id: 'settings',
    label: 'Systemeinstellungen',
    keywords: ['system', 'settings', 'einstellungen'],
    icon: Settings,
    category: 'System',
    actionId: 'settings',
    actionParams: { path: '/settings' },
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
    actionId: 'ai-ask-valeo',
    actionParams: { eventName: 'open-ask-valeo' },
    mcp: {
      intent: 'ai-assistance',
      businessDomain: 'help',
    },
  },
]

const AGRAR_COMMANDS: PaletteCommand[] = [
  {
    id: 'agrar-seed-list',
    label: 'Saatgut-Liste oeffnen',
    keywords: ['agrar', 'saatgut', 'liste', 'seed'],
    icon: Sprout,
    category: 'Agrar',
    actionId: 'agrar-seed-list',
    actionParams: { path: '/agrar/saatgut' },
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
    actionId: 'agrar-seed-master',
    actionParams: { path: '/agrar/saatgut/stamm?id=SEED-00123' },
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
    actionId: 'agrar-seed-order',
    actionParams: { path: '/agrar/saatgut/bestellung' },
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
    actionId: 'agrar-fertilizer-list',
    actionParams: { path: '/agrar/duenger' },
    mcp: {
      intent: 'open-fertilizer-list',
      businessDomain: 'agrar',
    },
  },
]

function appendUniqueCommands(target: PaletteCommand[], incoming: PaletteCommand[]): void {
  const existingIds = new Set(target.map((item) => item.id))
  for (const item of incoming) {
    if (!existingIds.has(item.id)) {
      target.push(item)
      existingIds.add(item.id)
    }
  }
}

function supportsAgrarCommand(command: { actionParams?: Record<string, unknown> }): boolean {
  const path = command.actionParams?.path
  return typeof path === 'string' ? !path.startsWith('/agrar') : true
}

function buildMaskCommands(maskRegistry: MaskRegistryEntry[] | undefined, agrarEnabled: boolean): PaletteCommand[] {
  if (!maskRegistry || maskRegistry.length === 0) {
    return []
  }

  return maskRegistry
    .filter((mask) => mask.mask_class === 'A' || mask.mask_class === 'B')
    .filter((mask) => agrarEnabled || (mask.domain !== 'agrar' && !mask.route.startsWith('/agrar')))
    .sort((left, right) => {
      if (left.mask_class !== right.mask_class) {
        return left.mask_class.localeCompare(right.mask_class)
      }
      return left.label.localeCompare(right.label, 'de')
    })
    .map((mask) => ({
      id: `mask:${mask.mask_id}`,
      label: mask.label,
      keywords: [
        mask.mask_id,
        mask.route,
        mask.domain,
        mask.mask_class,
        mask.process_key ?? '',
        mask.explainability,
        mask.requires_approval_ui ? 'approval' : '',
        mask.wave1_contract ? 'wave1' : '',
      ].filter((keyword): keyword is string => keyword.length > 0),
      icon: mask.domain === 'agrar' ? Sprout : mask.domain === 'finance' ? Calculator : FileText,
      category: mask.mask_class === 'A' ? 'Kernprozesse' : 'Prozessmasken',
      actionId: `mask:${mask.mask_id}`,
      actionParams: {
        path: mask.route,
        maskId: mask.mask_id,
        maskClass: mask.mask_class,
        processKey: mask.process_key ?? null,
      },
      hint: `${mask.mask_class} | ${mask.domain}${mask.process_key ? ` | ${mask.process_key}` : ''}`,
      mcp: {
        intent: 'open-process-mask',
        businessDomain: mask.domain,
      },
    }))
}

export function buildPaletteCommands({
  agrarEnabled,
  navigationShortcuts,
  maskRegistry,
}: BuildPaletteCommandsOptions): PaletteCommand[] {
  const commands: PaletteCommand[] = [...BASE_COMMANDS]

  if (agrarEnabled) {
    appendUniqueCommands(commands, AGRAR_COMMANDS)
  }

  const navigationCommands: PaletteCommand[] = navigationShortcuts
    .filter((shortcut) => (agrarEnabled ? true : !shortcut.path.startsWith('/agrar')))
    .map((shortcut) => ({
      id: `nav-${shortcut.id}`,
      label: shortcut.label,
      keywords: shortcut.keywords ?? [],
      icon: shortcut.icon,
      category: 'Navigation',
      actionId: `nav-${shortcut.id}`,
      actionParams: { path: shortcut.path },
      mcp: {
        intent: 'navigate',
        businessDomain: 'core',
      },
    }))

  const actionCommands: PaletteCommand[] = ACTION_SHORTCUTS
    .filter((shortcut) => (agrarEnabled ? true : !shortcut.path.startsWith('/agrar')))
    .map((shortcut) => ({
      id: shortcut.id,
      label: shortcut.label,
      keywords: shortcut.keywords ?? [],
      icon: shortcut.icon,
      category: 'Aktionen',
      shortcut: shortcut.shortcut,
      actionId: shortcut.id,
      actionParams: { path: shortcut.path },
      mcp: {
        intent: 'quick-action',
        businessDomain: 'core',
      },
    }))

  const aiCommands: PaletteCommand[] = AI_SHORTCUTS.map((shortcut) => ({
    id: shortcut.id,
    label: shortcut.label,
    keywords: shortcut.keywords ?? [],
    icon: shortcut.icon,
    category: 'KI',
    actionId: shortcut.id,
    actionParams: shortcut.type === 'navigate' ? { path: shortcut.path } : { eventName: shortcut.eventName },
    mcp: {
      intent: 'ai-action',
      businessDomain: 'ai',
    },
  }))

  appendUniqueCommands(commands, navigationCommands)
  appendUniqueCommands(commands, actionCommands)
  appendUniqueCommands(commands, aiCommands)
  appendUniqueCommands(commands, buildMaskCommands(maskRegistry, agrarEnabled))

  return agrarEnabled ? commands : commands.filter(supportsAgrarCommand)
}
