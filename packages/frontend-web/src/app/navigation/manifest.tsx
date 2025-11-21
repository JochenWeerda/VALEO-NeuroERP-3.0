import {
  AlertCircle,
  BarChart3,
  Building2,
  Calendar,
  Calculator,
  Euro,
  FileText,
  LayoutDashboard,
  Leaf,
  Package,
  Scale,
  Settings,
  ShieldCheck,
  ShoppingCart,
  Sprout,
  Target,
  Tractor,
  Truck,
  UserCog,
  Users,
  Zap,
  Plus,
  Search,
} from 'lucide-react'
import { resolveRoutePathFromModule } from '@/app/navigation/route-paths'
import { ENABLE_PROSPECTING_UI } from '@/features/prospecting/feature-flags'

type MCPInfo = {
  businessDomain: string
  scope: string
}

export type RawNavItem = {
  id: string
  label: string
  icon: typeof LayoutDashboard
  module?: string
  /**
   * When the preferred URL differs from the auto-derived path (e.g. landing page).
   */
  preferredPath?: string
  path?: string
  keywords?: string[]
  mcp: MCPInfo
  featureKey?: 'agrar'
  children?: RawNavItem[]
}

export type NavItem = Omit<RawNavItem, 'children'> & {
  path?: string
  children?: NavItem[]
}

export type NavigationShortcut = {
  id: string
  label: string
  icon: typeof LayoutDashboard
  path: string
  keywords?: string[]
}

export type ActionShortcut = {
  id: string
  label: string
  icon: typeof LayoutDashboard
  path: string
  keywords?: string[]
}

export type AiShortcut =
  | {
      id: string
      label: string
      icon: typeof LayoutDashboard
      type: 'event'
      eventName: string
      keywords?: string[]
    }
  | {
      id: string
      label: string
      icon: typeof LayoutDashboard
      type: 'navigate'
      path: string
      keywords?: string[]
    }

const CRM_CHILDREN: RawNavItem[] = [
  {
    id: 'kontakte',
    label: 'Kontakte',
    icon: Users,
    module: '@/pages/crm/kontakte-liste',
    keywords: ['kontakte'],
    mcp: { businessDomain: 'crm', scope: 'crm:read' },
  },
  {
    id: 'leads',
    label: 'Leads',
    icon: Target,
    module: '@/pages/crm/leads',
    keywords: ['leads'],
    mcp: { businessDomain: 'crm', scope: 'crm:read' },
  },
  {
    id: 'aktivitaeten',
    label: 'Aktivit��ten',
    icon: Calendar,
    module: '@/pages/crm/aktivitaeten',
    keywords: ['aktivit��ten'],
    mcp: { businessDomain: 'crm', scope: 'crm:read' },
  },
  {
    id: 'betriebsprofile',
    label: 'Betriebsprofile',
    icon: Tractor,
    module: '@/pages/crm/betriebsprofile-liste',
    keywords: ['betriebsprofile'],
    mcp: { businessDomain: 'crm', scope: 'crm:read' },
  },
]

if (ENABLE_PROSPECTING_UI) {
  CRM_CHILDREN.splice(2, 0, {
    id: 'prospecting',
    label: 'Prospecting',
    icon: Search,
    module: '@/pages/prospecting/LeadExplorer',
    preferredPath: 'prospecting/leads',
    keywords: ['prospecting', 'gap', 'potenzial'],
    mcp: { businessDomain: 'crm', scope: 'crm:read' },
  })
}

const NAV_SECTIONS_CONFIG: RawNavItem[] = [
  {
    id: 'dashboard',
    label: 'Dashboard',
    icon: LayoutDashboard,
    module: '@/pages/analytics',
    preferredPath: '/',
    mcp: { businessDomain: 'core', scope: 'core:read' },
  },
  {
    id: 'verkauf',
    label: 'Verkauf',
    icon: ShoppingCart,
    mcp: { businessDomain: 'sales', scope: 'sales:read' },
    children: [
      {
        id: 'sales-dashboard',
        label: 'Dashboard',
        icon: BarChart3,
        module: '@/pages/dashboard/sales-dashboard',
        preferredPath: 'dashboard/sales',
        keywords: ['dashboard', 'kpi', 'analytics'],
        mcp: { businessDomain: 'sales', scope: 'sales:read' },
      },
      {
        id: 'angebot',
        label: 'Angebote',
        icon: FileText,
        module: '@/pages/sales/angebote-liste',
        preferredPath: 'sales',
        keywords: ['angebot', 'angebot-liste'],
        mcp: { businessDomain: 'sales', scope: 'sales:read' },
      },
      {
        id: 'auftrag',
        label: 'Aufträge',
        icon: FileText,
        module: '@/pages/sales/order-editor',
        preferredPath: 'sales/order',
        keywords: ['aufträge'],
        mcp: { businessDomain: 'sales', scope: 'sales:read' },
      },
      {
        id: 'lieferung',
        label: 'Lieferungen',
        icon: Truck,
        module: '@/pages/sales/delivery-editor',
        preferredPath: 'sales/delivery',
        keywords: ['lieferungen'],
        mcp: { businessDomain: 'sales', scope: 'sales:read' },
      },
      {
        id: 'rechnung',
        label: 'Rechnungen',
        icon: FileText,
        module: '@/pages/sales/invoice-editor',
        preferredPath: 'sales/invoice',
        keywords: ['rechnungen'],
        mcp: { businessDomain: 'sales', scope: 'sales:read' },
      },
      {
        id: 'kunden',
        label: 'Kunden',
        icon: Users,
        module: '@/pages/verkauf/kunden-liste',
        keywords: ['kunden', 'crm', 'customer'],
        mcp: { businessDomain: 'sales', scope: 'sales:read' },
      },
      {
        id: 'artikel',
        label: 'Artikel',
        icon: Package,
        module: '@/pages/artikel/liste',
        keywords: ['artikel', 'products', 'lager'],
        mcp: { businessDomain: 'sales', scope: 'sales:read' },
      },
      {
        id: 'analytics',
        label: 'Analytics',
        icon: BarChart3,
        module: '@/pages/analytics',
        keywords: ['analytics'],
        mcp: { businessDomain: 'sales', scope: 'sales:read' },
      },
      {
        id: 'reports',
        label: 'Berichte',
        icon: FileText,
        module: '@/pages/reports',
        keywords: ['berichte', 'reports'],
        mcp: { businessDomain: 'sales', scope: 'sales:read' },
      },
    ],
  },
  {
    id: 'crm',
    label: 'CRM & Marketing',
    icon: UserCog,
    mcp: { businessDomain: 'crm', scope: 'crm:read' },
    children: CRM_CHILDREN,
  },
  {
    id: 'einkauf',
    label: 'Einkauf',
    icon: ShoppingCart,
    mcp: { businessDomain: 'procurement', scope: 'procurement:read' },
    children: [
      {
        id: 'einkauf-dashboard',
        label: 'Dashboard',
        icon: BarChart3,
        module: '@/pages/dashboard/einkauf-dashboard',
        preferredPath: 'dashboard/einkauf',
        keywords: ['dashboard', 'einkauf'],
        mcp: { businessDomain: 'procurement', scope: 'procurement:read' },
      },
      {
        id: 'bestellvorschlaege',
        label: 'Bestellvorschläge',
        icon: AlertCircle,
        module: '@/pages/einkauf/bestellvorschlaege',
        keywords: ['bestellvorschläge'],
        mcp: { businessDomain: 'procurement', scope: 'procurement:read' },
      },
      {
        id: 'bestellungen',
        label: 'Bestellungen',
        icon: FileText,
        module: '@/pages/contracts',
        keywords: ['bestellungen'],
        mcp: { businessDomain: 'procurement', scope: 'procurement:read' },
      },
      {
        id: 'wareneingang',
        label: 'Wareneingang',
        icon: Package,
        module: '@/pages/charge/wareneingang',
        keywords: ['wareneingang'],
        mcp: { businessDomain: 'procurement', scope: 'procurement:read' },
      },
      {
        id: 'lieferanten',
        label: 'Lieferanten',
        icon: Users,
        module: '@/pages/einkauf/lieferanten-liste',
        keywords: ['lieferanten'],
        mcp: { businessDomain: 'procurement', scope: 'procurement:read' },
      },
      {
        id: 'warengruppen',
        label: 'Warengruppen',
        icon: Package,
        module: '@/pages/einkauf/warengruppen',
        keywords: ['warengruppen'],
        mcp: { businessDomain: 'procurement', scope: 'procurement:read' },
      },
      {
        id: 'disposition',
        label: 'Disposition',
        icon: Calculator,
        module: '@/pages/disposition/liste',
        keywords: ['disposition'],
        mcp: { businessDomain: 'procurement', scope: 'procurement:read' },
      },
    ],
  },
  {
    id: 'fibu',
    label: 'Finanzbuchhaltung',
    icon: Euro,
    mcp: { businessDomain: 'finance', scope: 'finance:read' },
    children: [
      {
        id: 'hauptbuch',
        label: 'Hauptbuch',
        icon: FileText,
        module: '@/pages/fibu/hauptbuch',
        keywords: ['hauptbuch'],
        mcp: { businessDomain: 'finance', scope: 'finance:read' },
      },
      {
        id: 'debitoren',
        label: 'Debitoren',
        icon: Users,
        module: '@/pages/fibu/debitoren',
        keywords: ['debitoren'],
        mcp: { businessDomain: 'finance', scope: 'finance:read' },
      },
      {
        id: 'kreditoren',
        label: 'Kreditoren',
        icon: Users,
        module: '@/pages/fibu/kreditoren',
        keywords: ['kreditoren'],
        mcp: { businessDomain: 'finance', scope: 'finance:read' },
      },
      {
        id: 'buchungsjournal',
        label: 'Buchungsjournal',
        icon: FileText,
        module: '@/pages/fibu/buchungsjournal',
        keywords: ['buchungsjournal'],
        mcp: { businessDomain: 'finance', scope: 'finance:read' },
      },
      {
        id: 'kontenplan',
        label: 'Kontenplan',
        icon: FileText,
        module: '@/pages/fibu/kontenplan',
        keywords: ['kontenplan'],
        mcp: { businessDomain: 'finance', scope: 'finance:read' },
      },
      {
        id: 'bilanz',
        label: 'Bilanz',
        icon: BarChart3,
        module: '@/pages/fibu/bilanz',
        keywords: ['bilanz'],
        mcp: { businessDomain: 'finance', scope: 'finance:read' },
      },
      {
        id: 'guv',
        label: 'GuV',
        icon: BarChart3,
        module: '@/pages/fibu/guv',
        keywords: ['guv'],
        mcp: { businessDomain: 'finance', scope: 'finance:read' },
      },
      {
        id: 'bwa',
        label: 'BWA',
        icon: BarChart3,
        module: '@/pages/fibu/bwa',
        keywords: ['bwa'],
        mcp: { businessDomain: 'finance', scope: 'finance:read' },
      },
      {
        id: 'anlagen',
        label: 'Anlagenbuchhaltung',
        icon: Building2,
        module: '@/pages/fibu/anlagen',
        keywords: ['anlagen'],
        mcp: { businessDomain: 'finance', scope: 'finance:read' },
      },
      {
        id: 'op-verwaltung',
        label: 'OP-Verwaltung',
        icon: Euro,
        module: '@/pages/fibu/op-verwaltung',
        keywords: ['op', 'verwaltung'],
        mcp: { businessDomain: 'finance', scope: 'finance:read' },
      },
      {
        id: 'ustva',
        label: 'USt.-Voranmeldung',
        icon: FileText,
        module: '@/pages/export/umsatzsteuervoranmeldung',
        preferredPath: 'export/ustva',
        keywords: ['ustva'],
        mcp: { businessDomain: 'finance', scope: 'finance:read' },
      },
    ],
  },
  {
    id: 'lager',
    label: 'Lager & Bestände',
    icon: Package,
    mcp: { businessDomain: 'inventory', scope: 'inventory:read' },
    children: [
      {
        id: 'bestandsuebersicht',
        label: 'Bestandsübersicht',
        icon: Package,
        module: '@/pages/lager/bestandsuebersicht',
        keywords: ['bestandsübersicht'],
        mcp: { businessDomain: 'inventory', scope: 'inventory:read' },
      },
      {
        id: 'einlagerung',
        label: 'Einlagerung',
        icon: Truck,
        module: '@/pages/lager/einlagerung',
        keywords: ['einlagerung'],
        mcp: { businessDomain: 'inventory', scope: 'inventory:read' },
      },
      {
        id: 'auslagerung',
        label: 'Auslagerung',
        icon: Truck,
        module: '@/pages/lager/auslagerung',
        keywords: ['auslagerung'],
        mcp: { businessDomain: 'inventory', scope: 'inventory:read' },
      },
      {
        id: 'inventur',
        label: 'Inventur',
        icon: Scale,
        module: '@/pages/lager/inventur',
        keywords: ['inventur'],
        mcp: { businessDomain: 'inventory', scope: 'inventory:read' },
      },
    ],
  },
  {
    id: 'agrar',
    label: 'Agrar & Warenwirtschaft',
    icon: Sprout,
    featureKey: 'agrar',
    mcp: { businessDomain: 'agrar', scope: 'agrar:read' },
    children: [
      {
        id: 'psm',
        label: 'Pflanzenschutz',
        icon: Leaf,
        module: '@/pages/agrar/psm/liste',
        preferredPath: 'agrar/psm',
        mcp: { businessDomain: 'agrar', scope: 'agrar:read' },
      },
      {
        id: 'duenger',
        label: 'Dünger',
        icon: Sprout,
        module: '@/pages/agrar/duenger-liste',
        preferredPath: 'agrar/duenger-liste',
        mcp: { businessDomain: 'agrar', scope: 'agrar:read' },
      },
      {
        id: 'saatgut',
        label: 'Saatgut',
        icon: Leaf,
        module: '@/pages/agrar/saatgut-liste',
        preferredPath: 'agrar/saatgut-liste',
        mcp: { businessDomain: 'agrar', scope: 'agrar:read' },
      },
      {
        id: 'bodenproben',
        label: 'Bodenproben',
        icon: Scale,
        module: '@/pages/agrar/bodenproben/liste',
        preferredPath: 'agrar/bodenproben',
        mcp: { businessDomain: 'agrar', scope: 'agrar:read' },
      },
      {
        id: 'ernte',
        label: 'Ernteplanung',
        icon: Tractor,
        module: '@/pages/agrar/ernte/liste',
        preferredPath: 'agrar/ernte',
        mcp: { businessDomain: 'agrar', scope: 'agrar:read' },
      },
      {
        id: 'feldbuch',
        label: 'Feldbuch',
        icon: FileText,
        module: '@/pages/agrar/feldbuch/schlagkartei',
        preferredPath: 'agrar/feldbuch/schlagkartei',
        mcp: { businessDomain: 'agrar', scope: 'agrar:read' },
      },
      {
        id: 'futter',
        label: 'Futtermittel',
        icon: Package,
        module: '@/pages/futter/einzel/liste',
        preferredPath: 'futter/einzel/liste',
        mcp: { businessDomain: 'agrar', scope: 'agrar:read' },
      },
    ],
  },
  {
    id: 'annahme',
    label: 'Annahme & Waage',
    icon: Truck,
    mcp: { businessDomain: 'logistics', scope: 'logistics:read' },
    children: [
      {
        id: 'warteschlange',
        label: 'Warteschlange',
        icon: Truck,
        module: '@/pages/annahme/warteschlange',
        path: '/annahme/warteschlange',
        mcp: { businessDomain: 'logistics', scope: 'logistics:read' },
      },
      {
        id: 'waage-liste',
        label: 'Waagen',
        icon: Scale,
        module: '@/pages/waage/liste',
        path: '/waage/liste',
        mcp: { businessDomain: 'logistics', scope: 'logistics:read' },
      },
      {
        id: 'wiegungen',
        label: 'Wiegungen',
        icon: FileText,
        module: '@/pages/waage/wiegungen',
        path: '/waage/wiegungen',
        mcp: { businessDomain: 'logistics', scope: 'logistics:read' },
      },
    ],
  },
  {
    id: 'quality',
    label: 'Qualität & Compliance',
    icon: ShieldCheck,
    mcp: { businessDomain: 'quality', scope: 'quality:read' },
    children: [
      {
        id: 'qm-dokumente',
        label: 'QM-Dokumente',
        icon: FileText,
        module: '@/pages/document',
        mcp: { businessDomain: 'quality', scope: 'quality:read' },
      },
      {
        id: 'audit-trails',
        label: 'Audit Trails',
        icon: ShieldCheck,
        module: '@/pages/admin/audit-log',
        mcp: { businessDomain: 'quality', scope: 'quality:read' },
      },
      {
        id: 'compliance',
        label: 'Compliance Cockpit',
        icon: ShieldCheck,
        module: '@/pages/admin/compliance-dashboard',
        preferredPath: 'admin/compliance',
        keywords: ['compliance'],
        mcp: { businessDomain: 'quality', scope: 'quality:read' },
      },
    ],
  },
  {
    id: 'compliance',
    label: 'Compliance',
    icon: ShieldCheck,
    mcp: { businessDomain: 'compliance', scope: 'compliance:read' },
    children: [
      {
        id: 'policies',
        label: 'Policies',
        icon: ShieldCheck,
        module: '@/pages/policy-manager',
        preferredPath: 'policies',
        mcp: { businessDomain: 'compliance', scope: 'compliance:read' },
      },
      {
        id: 'zulassungen',
        label: 'Zulassungen',
        icon: FileText,
        module: '@/pages/compliance/zulassungen-register',
        path: '/compliance/zulassungen-register',
        mcp: { businessDomain: 'compliance', scope: 'compliance:read' },
      },
      {
        id: 'eudr',
        label: 'EUDR-Compliance',
        icon: Leaf,
        module: '@/pages/nachhaltigkeit/eudr-compliance',
        path: '/nachhaltigkeit/eudr-compliance',
        mcp: { businessDomain: 'compliance', scope: 'compliance:read' },
      },
      {
        id: 'labor',
        label: 'Labor',
        icon: FileText,
        module: '@/pages/qualitaet/labor-liste',
        path: '/qualitaet/labor-liste',
        mcp: { businessDomain: 'quality', scope: 'quality:read' },
      },
      {
        id: 'zertifikate',
        label: 'Zertifikate',
        icon: ShieldCheck,
        module: '@/pages/zertifikate/liste',
        path: '/zertifikate/liste',
        mcp: { businessDomain: 'compliance', scope: 'compliance:read' },
      },
    ],
  },
  {
    id: 'logistik',
    label: 'Logistik',
    icon: Truck,
    mcp: { businessDomain: 'logistics', scope: 'logistics:read' },
    children: [
      {
        id: 'tourenplanung',
        label: 'Tourenplanung',
        icon: Truck,
        module: '@/pages/logistik/tourenplanung',
        preferredPath: 'logistik/tourenplanung',
        mcp: { businessDomain: 'logistics', scope: 'logistics:read' },
      },
      {
        id: 'frachtbriefe',
        label: 'Frachtbriefe',
        icon: Target,
        module: '@/pages/logistik/frachtbriefe',
        preferredPath: 'logistik/frachtbriefe',
        mcp: { businessDomain: 'logistics', scope: 'logistics:read' },
      },
    ],
  },
  {
    id: 'pos',
    label: 'POS & Filialen',
    icon: Euro,
    mcp: { businessDomain: 'pos', scope: 'pos:read' },
    children: [
      {
        id: 'pos-terminal',
        label: 'POS Terminal',
        icon: Euro,
        module: '@/pages/pos/terminal',
        mcp: { businessDomain: 'pos', scope: 'pos:read' },
      },
      {
        id: 'tse-journal',
        label: 'TSE Journal',
        icon: FileText,
        module: '@/pages/pos/tse-journal',
        mcp: { businessDomain: 'pos', scope: 'pos:read' },
      },
      {
        id: 'tagesabschluss',
        label: 'Tagesabschluss',
        icon: Calculator,
        module: '@/pages/pos/tagesabschluss-enhanced',
        mcp: { businessDomain: 'pos', scope: 'pos:read' },
      },
      {
        id: 'gift-cards',
        label: 'Geschenkkarten',
        icon: Euro,
        module: '@/pages/pos/gift-cards',
        mcp: { businessDomain: 'pos', scope: 'pos:read' },
      },
      {
        id: 'rabatte',
        label: 'Rabatte',
        icon: Euro,
        module: '@/pages/pos/rabatte',
        mcp: { businessDomain: 'pos', scope: 'pos:read' },
      },
    ],
  },
  {
    id: 'personal',
    label: 'Personal',
    icon: Users,
    mcp: { businessDomain: 'hr', scope: 'hr:read' },
    children: [
      {
        id: 'mitarbeiter-liste',
        label: 'Mitarbeiter',
        icon: Users,
        module: '@/pages/personal/mitarbeiter-liste',
        mcp: { businessDomain: 'hr', scope: 'hr:read' },
      },
      {
        id: 'zeiterfassung',
        label: 'Zeiterfassung',
        icon: Calendar,
        module: '@/pages/personal/zeiterfassung',
        mcp: { businessDomain: 'hr', scope: 'hr:read' },
      },
      {
        id: 'stundenzettel',
        label: 'Stundenzettel',
        icon: FileText,
        module: '@/pages/personal/stundenzettel',
        mcp: { businessDomain: 'hr', scope: 'hr:read' },
      },
      {
        id: 'schulungen',
        label: 'Schulungen',
        icon: UserCog,
        module: '@/pages/personal/schulungen',
        mcp: { businessDomain: 'hr', scope: 'hr:read' },
      },
      {
        id: 'schichtplan',
        label: 'Schichtplan',
        icon: Calendar,
        module: '@/pages/schichtplan/liste',
        mcp: { businessDomain: 'hr', scope: 'hr:read' },
      },
    ],
  },
  {
    id: 'admin',
    label: 'Administration',
    icon: Settings,
    mcp: { businessDomain: 'admin', scope: 'admin:read' },
    children: [
      {
        id: 'benutzer',
        label: 'Benutzer',
        icon: Users,
        module: '@/pages/admin/benutzer-liste',
        mcp: { businessDomain: 'admin', scope: 'admin:read' },
      },
      {
        id: 'rollen-verwaltung',
        label: 'Rollen',
        icon: UserCog,
        module: '@/pages/admin/rollen-verwaltung',
        mcp: { businessDomain: 'admin', scope: 'admin:read' },
      },
      {
        id: 'audit-log',
        label: 'Audit-Log',
        icon: FileText,
        module: '@/pages/admin/audit-log',
        mcp: { businessDomain: 'admin', scope: 'admin:read' },
      },
      {
        id: 'monitoring',
        label: 'Monitoring',
        icon: AlertCircle,
        module: '@/pages/admin/monitoring/alerts',
        preferredPath: 'monitoring/alerts',
        mcp: { businessDomain: 'admin', scope: 'admin:read' },
      },
      {
        id: 'compliance-dashboard',
        label: 'Compliance',
        icon: ShieldCheck,
        module: '@/pages/admin/compliance-dashboard',
        preferredPath: 'admin/compliance',
        mcp: { businessDomain: 'admin', scope: 'admin:read' },
      },
      ...(ENABLE_PROSPECTING_UI
        ? [
            {
              id: 'gap-pipeline',
              label: 'GAP-Pipeline',
              icon: BarChart3,
              module: '@/pages/admin/GapPipelineConsole',
              preferredPath: 'admin/gap-pipeline',
              keywords: ['gap', 'pipeline', 'prospecting', 'import'],
              mcp: { businessDomain: 'admin', scope: 'admin:write' },
            },
          ]
        : []),
      {
        id: 'system-einstellungen',
        label: 'System',
        icon: Settings,
        module: '@/pages/einstellungen/system',
        preferredPath: 'einstellungen/system',
        mcp: { businessDomain: 'admin', scope: 'admin:read' },
      },
    ],
  },
]

const ACTION_SHORTCUTS_CONFIG: Array<
  {
    id: string
    label: string
    icon: typeof LayoutDashboard
    module: string
    preferredPath?: string
    keywords?: string[]
  }
> = [
  {
    id: 'action-new-customer',
    label: 'Neuer Kunde anlegen',
    icon: Plus,
    module: '@/pages/verkauf/kunde-neu',
    keywords: ['neu', 'kunde'],
  },
  {
    id: 'action-new-invoice',
    label: 'Neue Rechnung erstellen',
    icon: Plus,
    module: '@/pages/sales/invoice-editor',
    preferredPath: 'sales/invoice',
    keywords: ['rechnung'],
  },
  {
    id: 'action-bestellvorschlag',
    label: 'Bestellvorschlag generieren',
    icon: Calculator,
    module: '@/pages/einkauf/bestellvorschlaege',
    keywords: ['bestellvorschlag'],
  },
]

export const NAV_SECTIONS: NavItem[] = NAV_SECTIONS_CONFIG.map(resolveNavItem)

export const NAV_LINKS: NavItem[] = flattenNavItems(NAV_SECTIONS)

export const NAVIGATION_SHORTCUTS: NavigationShortcut[] = NAV_LINKS.filter(
  (item): item is NavItem & { path: string } => Boolean(item.path),
).map((item) => ({
  id: item.id,
  label: item.label,
  icon: item.icon,
  path: item.path,
  keywords: item.keywords,
}))

export const ACTION_SHORTCUTS: ActionShortcut[] = ACTION_SHORTCUTS_CONFIG.map((shortcut) => ({
  id: shortcut.id,
  label: shortcut.label,
  icon: shortcut.icon,
  path: resolveRoutePathFromModule(shortcut.module, shortcut.preferredPath),
  keywords: shortcut.keywords,
}))

export const AI_SHORTCUTS: AiShortcut[] = [
  {
    id: 'ai-ask-valeo',
    label: 'Ask VALEO (AI-Copilot)',
    icon: Zap,
    type: 'event',
    eventName: 'open-ask-valeo',
    keywords: ['ai', 'copilot', 'assistant'],
  },
  {
    id: 'ai-search',
    label: 'Semantische Suche',
    icon: Search,
    type: 'event',
    eventName: 'open-semantic-search',
    keywords: ['search', 'semantic'],
  },
  {
    id: 'ai-compliance',
    label: 'Compliance-Check durchführen',
    icon: ShieldCheck,
    type: 'navigate',
    path: resolveRoutePathFromModule('@/pages/admin/compliance-dashboard', 'admin/compliance'),
    keywords: ['compliance', 'audit'],
  },
]

function resolveNavItem(item: RawNavItem): NavItem {
  const moduleSpecifier = item.module ?? inferModuleFromPath(item.path)
  const resolvedPath =
    item.path ??
    (moduleSpecifier ? resolveRoutePathFromModule(moduleSpecifier, item.preferredPath) : undefined)

  return {
    ...item,
    module: moduleSpecifier,
    path: resolvedPath,
    children: item.children?.map(resolveNavItem),
  }
}

function inferModuleFromPath(path?: string): string | undefined {
  if (!path) {
    return undefined
  }
  const normalized = path.startsWith('/') ? path.slice(1) : path
  if (!normalized) {
    return '@/pages/index'
  }
  return `@/pages/${normalized}`
}

function flattenNavItems(items: NavItem[]): NavItem[] {
  return items.flatMap((item) => {
    const result: NavItem[] = []
    if (item.path) {
      result.push(item)
    }
    if (item.children) {
      result.push(...flattenNavItems(item.children))
    }
    return result
  })
}
