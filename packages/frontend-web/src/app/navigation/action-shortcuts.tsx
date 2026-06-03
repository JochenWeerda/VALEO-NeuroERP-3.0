import { Calculator, Euro, LayoutDashboard, MapPin, Plus, Search, Tractor } from 'lucide-react'
import { resolveRoutePathFromModule } from '@/app/navigation/route-paths'

export type ActionShortcut = {
  id: string
  label: string
  icon: typeof LayoutDashboard
  path: string
  keywords?: string[]
  shortcut?: string
}

const ACTION_SHORTCUTS_CONFIG: Array<{
  id: string
  label: string
  icon: typeof LayoutDashboard
  module: string
  preferredPath?: string
  keywords?: string[]
  shortcut?: string
}> = [
  {
    id: 'action-new-customer',
    label: 'Neuer Kunde anlegen',
    icon: Plus,
    module: '@/pages/verkauf/kunden-stamm',
    keywords: ['neu', 'kunde'],
    shortcut: 'Ctrl+Alt+N',
  },
  {
    id: 'action-new-invoice',
    label: 'Neue Rechnung erstellen',
    icon: Plus,
    module: '@/pages/sales/invoice-editor',
    preferredPath: 'sales/invoice',
    keywords: ['rechnung'],
    shortcut: 'Ctrl+Alt+R',
  },
  {
    id: 'action-bestellvorschlag',
    label: 'Bestellvorschlag generieren',
    icon: Calculator,
    module: '@/pages/einkauf/bestellvorschlaege',
    keywords: ['bestellvorschlag'],
    shortcut: 'Ctrl+Alt+B',
  },
  {
    id: 'action-ernte-annahme',
    label: 'Ernte-Annahme erfassen',
    icon: Tractor,
    module: '@/pages/agrar/ernte-annahme-erfassung',
    preferredPath: 'agrar/ernte-annahme-erfassung',
    keywords: ['ernte', 'annahme'],
    shortcut: 'Ctrl+Alt+E',
  },
  {
    id: 'action-kunden-schnellauswahl',
    label: 'Kunden-Schnellauswahl',
    icon: Search,
    module: '@/pages/crm/kunden-schnellauswahl',
    preferredPath: 'crm/kunden-schnellauswahl',
    keywords: ['kunde', 'suche', 'schnellauswahl', 'lookup'],
  },
  {
    id: 'action-milchvieh-crosssell',
    label: 'Milchvieh Cross-Sell',
    icon: Euro,
    module: '@/pages/agrar/milchvieh-crosssell',
    preferredPath: 'agrar/milchvieh-crosssell',
    keywords: ['milchvieh', 'cross-sell', 'potenzial', 'kraftfutter'],
  },
  {
    id: 'action-milchvieh-karte',
    label: 'Milchvieh-Karte',
    icon: MapPin,
    module: '@/pages/agrar/milchvieh-karte',
    preferredPath: 'agrar/milchvieh-karte',
    keywords: ['milchvieh', 'karte', 'map', 'betriebe', 'crm'],
  },
]

export const ACTION_SHORTCUTS: ActionShortcut[] = ACTION_SHORTCUTS_CONFIG.map((shortcut) => ({
  id: shortcut.id,
  label: shortcut.label,
  icon: shortcut.icon,
  path: resolveRoutePathFromModule(shortcut.module, shortcut.preferredPath),
  keywords: shortcut.keywords,
  shortcut: shortcut.shortcut,
}))
