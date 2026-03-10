import {
  BarChart3,
  FileText,
  Package,
  Plus,
  Settings,
  ShoppingCart,
  Truck,
  Users,
  type LucideIcon,
} from 'lucide-react'
import type { CommandItem } from '@/components/innendienst/CommandPalette'

type CommandCategory = CommandItem['category']

type CommandDescriptor = {
  id: string
  label: string
  description?: string
  icon: LucideIcon
  shortcut?: string
  category: CommandCategory
  path: string
  keywords?: string[]
}

const DEFAULT_COMMAND_DESCRIPTORS: CommandDescriptor[] = [
  {
    id: 'nav-dashboard',
    label: 'Dashboard',
    description: 'Zur Startseite',
    icon: BarChart3,
    category: 'navigation',
    path: '/',
    keywords: ['home', 'start', 'uebersicht'],
  },
  {
    id: 'nav-customers',
    label: 'Kunden',
    description: 'Kundenstamm oeffnen',
    icon: Users,
    shortcut: 'G K',
    category: 'navigation',
    path: '/crm/kunden-stamm',
    keywords: ['crm', 'kontakte', 'adressen'],
  },
  {
    id: 'nav-orders',
    label: 'Auftraege',
    description: 'Auftragsliste oeffnen',
    icon: ShoppingCart,
    shortcut: 'G A',
    category: 'navigation',
    path: '/sales/auftraege-liste',
    keywords: ['verkauf', 'bestellungen', 'orders'],
  },
  {
    id: 'nav-invoices',
    label: 'Rechnungen',
    description: 'Rechnungsliste oeffnen',
    icon: FileText,
    shortcut: 'G R',
    category: 'navigation',
    path: '/sales/rechnungen-liste',
    keywords: ['finanzen', 'buchhaltung', 'belege'],
  },
  {
    id: 'nav-inventory',
    label: 'Lagerbestand',
    description: 'Bestandsuebersicht oeffnen',
    icon: Package,
    shortcut: 'G L',
    category: 'navigation',
    path: '/lager/bestandsuebersicht',
    keywords: ['warehouse', 'artikel', 'stock'],
  },
  {
    id: 'nav-deliveries',
    label: 'Lieferungen',
    description: 'Lieferungsliste oeffnen',
    icon: Truck,
    category: 'navigation',
    path: '/sales/lieferungen-liste',
    keywords: ['versand', 'transport', 'logistik'],
  },
  {
    id: 'nav-settings',
    label: 'Einstellungen',
    description: 'Systemeinstellungen',
    icon: Settings,
    category: 'navigation',
    path: '/einstellungen',
    keywords: ['config', 'optionen', 'profil'],
  },
  {
    id: 'action-new-customer',
    label: 'Neuer Kunde',
    description: 'Kunde anlegen',
    icon: Plus,
    shortcut: 'N K',
    category: 'action',
    path: '/verkauf/kunde-neu',
    keywords: ['erstellen', 'anlegen', 'create'],
  },
  {
    id: 'action-new-order',
    label: 'Neuer Auftrag',
    description: 'Auftrag erstellen',
    icon: Plus,
    shortcut: 'N A',
    category: 'action',
    path: '/sales/order-editor',
    keywords: ['erstellen', 'anlegen', 'create'],
  },
  {
    id: 'action-new-offer',
    label: 'Neues Angebot',
    description: 'Angebot erstellen',
    icon: Plus,
    shortcut: 'N O',
    category: 'action',
    path: '/sales/angebot-erstellen',
    keywords: ['erstellen', 'anlegen', 'quote'],
  },
  {
    id: 'action-new-invoice',
    label: 'Neue Rechnung',
    description: 'Rechnung erstellen',
    icon: Plus,
    shortcut: 'N R',
    category: 'action',
    path: '/finance/invoice-form',
    keywords: ['erstellen', 'anlegen', 'billing'],
  },
]

export function getDefaultCommands(navigate: (path: string) => void): CommandItem[] {
  return DEFAULT_COMMAND_DESCRIPTORS.map((descriptor) => {
    const Icon = descriptor.icon
    return {
      id: descriptor.id,
      label: descriptor.label,
      description: descriptor.description,
      icon: <Icon className="h-4 w-4" />,
      shortcut: descriptor.shortcut,
      category: descriptor.category,
      action: () => navigate(descriptor.path),
      keywords: descriptor.keywords,
    }
  })
}
