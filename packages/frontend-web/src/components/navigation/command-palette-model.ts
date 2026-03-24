import type { ComponentType } from 'react'
import {
  AlertCircle,
  BarChart3,
  BookOpen,
  Calculator,
  Calendar,
  CheckSquare,
  ClipboardList,
  CreditCard,
  Database,
  Euro,
  FileText,
  HelpCircle,
  LayoutDashboard,
  Leaf,
  Monitor,
  Package,
  QrCode,
  ReceiptText,
  RefreshCw,
  Scale,
  Settings,
  ShieldCheck,
  ShoppingCart,
  Sprout,
  Target,
  Tractor,
  Truck,
  Upload,
  Users,
  Warehouse,
  Zap,
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
  // ── Verkauf ────────────────────────────────────────────────────────────────
  {
    id: 'nav-verkaufsauftraege',
    label: 'Verkaufsaufträge',
    keywords: ['auftrag', 'aufträge', 'sales', 'order', 'so'],
    icon: ShoppingCart,
    category: 'Verkauf',
    actionId: 'nav-verkaufsauftraege',
    actionParams: { path: '/verkauf/auftraege' },
    mcp: { intent: 'navigate', businessDomain: 'sales' },
  },
  {
    id: 'nav-angebote',
    label: 'Angebote',
    keywords: ['angebot', 'angebote', 'quote', 'offert'],
    icon: FileText,
    category: 'Verkauf',
    actionId: 'nav-angebote',
    actionParams: { path: '/verkauf/angebote' },
    mcp: { intent: 'navigate', businessDomain: 'sales' },
  },
  {
    id: 'nav-lieferscheine',
    label: 'Lieferscheine',
    keywords: ['lieferschein', 'lieferung', 'delivery'],
    icon: Truck,
    category: 'Verkauf',
    actionId: 'nav-lieferscheine',
    actionParams: { path: '/verkauf/lieferschein-erfassung' },
    mcp: { intent: 'navigate', businessDomain: 'sales' },
  },
  {
    id: 'nav-rechnungen',
    label: 'Rechnungen',
    keywords: ['rechnung', 'rechnungen', 'invoice', 'faktura'],
    icon: FileText,
    category: 'Verkauf',
    actionId: 'nav-rechnungen',
    actionParams: { path: '/sales/invoice' },
    mcp: { intent: 'navigate', businessDomain: 'sales' },
  },
  {
    id: 'nav-kunden-verkauf',
    label: 'Kunden',
    keywords: ['kunden', 'kunde', 'customer', 'crm'],
    icon: Users,
    category: 'Verkauf',
    actionId: 'nav-kunden-verkauf',
    actionParams: { path: '/verkauf/kunden-liste' },
    mcp: { intent: 'navigate', businessDomain: 'sales' },
  },

  // ── Einkauf ────────────────────────────────────────────────────────────────
  {
    id: 'nav-rechnungseingang',
    label: 'Rechnungseingang',
    keywords: ['rechnungseingang', 'eingangsrechnung', 'kreditor', 'eingang'],
    icon: ReceiptText,
    category: 'Einkauf',
    actionId: 'nav-rechnungseingang',
    actionParams: { path: '/einkauf/rechnungseingang' },
    mcp: { intent: 'navigate', businessDomain: 'procurement' },
  },
  {
    id: 'nav-bestellvorschlag-lager',
    label: 'Bestellvorschlag Lager',
    keywords: ['bestellvorschlag', 'lager', 'mindestbestand', 'beschaffung'],
    icon: Package,
    category: 'Einkauf',
    actionId: 'nav-bestellvorschlag-lager',
    actionParams: { path: '/einkauf/bestellvorschlag-lager' },
    mcp: { intent: 'navigate', businessDomain: 'procurement' },
  },
  {
    id: 'nav-bestellungen',
    label: 'Bestellungen',
    keywords: ['bestellung', 'bestellungen', 'order', 'purchase'],
    icon: ClipboardList,
    category: 'Einkauf',
    actionId: 'nav-bestellungen',
    actionParams: { path: '/einkauf/bestellungen' },
    mcp: { intent: 'navigate', businessDomain: 'procurement' },
  },
  {
    id: 'nav-lieferanten',
    label: 'Lieferanten',
    keywords: ['lieferant', 'lieferanten', 'supplier', 'vendor'],
    icon: Users,
    category: 'Einkauf',
    actionId: 'nav-lieferanten',
    actionParams: { path: '/einkauf/lieferanten' },
    mcp: { intent: 'navigate', businessDomain: 'procurement' },
  },
  {
    id: 'nav-wareneingang',
    label: 'Wareneingang',
    keywords: ['wareneingang', 'eingang', 'annahme', 'receipt'],
    icon: Package,
    category: 'Einkauf',
    actionId: 'nav-wareneingang',
    actionParams: { path: '/einkauf/wareneingang' },
    mcp: { intent: 'navigate', businessDomain: 'procurement' },
  },

  // ── Lager ──────────────────────────────────────────────────────────────────
  {
    id: 'nav-lagerbestand',
    label: 'Lagerbestand',
    keywords: ['lagerbestand', 'bestand', 'bestandsübersicht', 'inventory'],
    icon: Warehouse,
    category: 'Lager',
    actionId: 'nav-lagerbestand',
    actionParams: { path: '/lager/bestand' },
    mcp: { intent: 'navigate', businessDomain: 'inventory' },
  },
  {
    id: 'nav-einlagerung',
    label: 'Einlagerung',
    keywords: ['einlagerung', 'einlagern', 'put-away'],
    icon: Truck,
    category: 'Lager',
    actionId: 'nav-einlagerung',
    actionParams: { path: '/lager/einlagerung' },
    mcp: { intent: 'navigate', businessDomain: 'inventory' },
  },
  {
    id: 'nav-auslagerung',
    label: 'Auslagerung',
    keywords: ['auslagerung', 'auslagern', 'pick'],
    icon: Truck,
    category: 'Lager',
    actionId: 'nav-auslagerung',
    actionParams: { path: '/lager/auslagerung' },
    mcp: { intent: 'navigate', businessDomain: 'inventory' },
  },
  {
    id: 'nav-inventur',
    label: 'Inventur',
    keywords: ['inventur', 'zählung', 'stocktaking'],
    icon: Scale,
    category: 'Lager',
    actionId: 'nav-inventur',
    actionParams: { path: '/lager/inventur' },
    mcp: { intent: 'navigate', businessDomain: 'inventory' },
  },
  {
    id: 'nav-bestandskorrektur',
    label: 'Bestandskorrektur',
    keywords: ['bestandskorrektur', 'korrektur', 'adjust', 'inventory'],
    icon: Package,
    category: 'Lager',
    actionId: 'nav-bestandskorrektur',
    actionParams: { path: '/inventory/adjust' },
    mcp: { intent: 'adjust-inventory', businessDomain: 'inventory' },
  },

  // ── Finanzen ───────────────────────────────────────────────────────────────
  {
    id: 'nav-op-kreditoren',
    label: 'Offene Posten Kreditoren',
    keywords: ['offene posten', 'op', 'kreditoren', 'verbindlichkeiten'],
    icon: Euro,
    category: 'Finanzen',
    actionId: 'nav-op-kreditoren',
    actionParams: { path: '/finance/op-kreditoren' },
    mcp: { intent: 'navigate', businessDomain: 'finance' },
  },
  {
    id: 'nav-op-debitoren',
    label: 'Offene Posten Debitoren',
    keywords: ['offene posten', 'op', 'debitoren', 'forderungen'],
    icon: Euro,
    category: 'Finanzen',
    actionId: 'nav-op-debitoren',
    actionParams: { path: '/finance/op-debitoren' },
    mcp: { intent: 'navigate', businessDomain: 'finance' },
  },
  {
    id: 'nav-mahnwesen',
    label: 'Mahnwesen',
    keywords: ['mahnung', 'mahnwesen', 'dunning', 'forderung'],
    icon: AlertCircle,
    category: 'Finanzen',
    actionId: 'nav-mahnwesen',
    actionParams: { path: '/finance/mahnwesen' },
    mcp: { intent: 'navigate', businessDomain: 'finance' },
  },
  {
    id: 'nav-buchungsimport',
    label: 'Buchhaltungsimport',
    keywords: ['buchungsimport', 'import', 'csv', 'massenbuchung', 'datev'],
    icon: Upload,
    category: 'Finanzen',
    actionId: 'nav-buchungsimport',
    actionParams: { path: '/fibu/buchungsimport' },
    mcp: { intent: 'navigate', businessDomain: 'finance' },
  },
  {
    id: 'nav-zahlungslaeufe',
    label: 'Zahlungsläufe',
    keywords: ['zahlung', 'zahlungsläufe', 'payment', 'run'],
    icon: CreditCard,
    category: 'Finanzen',
    actionId: 'nav-zahlungslaeufe',
    actionParams: { path: '/fibu/zahlungslaeufe' },
    mcp: { intent: 'navigate', businessDomain: 'finance' },
  },
  {
    id: 'nav-skonto-optimizer',
    label: 'Skonto-Optimierung',
    keywords: ['skonto', 'optimizer', 'ki', 'agent', 'zahlung', 'fälligkeit'],
    icon: Zap,
    category: 'Finanzen',
    actionId: 'nav-skonto-optimizer',
    actionParams: { path: '/finance/skonto-optimizer' },
    mcp: { intent: 'navigate', businessDomain: 'finance' },
  },
  {
    id: 'nav-ustva',
    label: 'USt.-Voranmeldung',
    keywords: ['ustva', 'umsatzsteuer', 'voranmeldung', 'finanzamt'],
    icon: FileText,
    category: 'Finanzen',
    actionId: 'nav-ustva',
    actionParams: { path: '/export/ustva' },
    mcp: { intent: 'navigate', businessDomain: 'finance' },
  },
  {
    id: 'nav-wechselkurse',
    label: 'Wechselkurse',
    keywords: ['wechselkurs', 'devisen', 'fremdwährung', 'kurs', 'ezb'],
    icon: RefreshCw,
    category: 'Finanzen',
    actionId: 'nav-wechselkurse',
    actionParams: { path: '/finance/wechselkurse' },
    mcp: { intent: 'navigate', businessDomain: 'finance' },
  },
  {
    id: 'nav-bilanz',
    label: 'Bilanz',
    keywords: ['bilanz', 'balance sheet', 'jahresabschluss'],
    icon: BarChart3,
    category: 'Finanzen',
    actionId: 'nav-bilanz',
    actionParams: { path: '/fibu/bilanz' },
    mcp: { intent: 'navigate', businessDomain: 'finance' },
  },
  {
    id: 'finance-booking',
    label: 'Buchung erfassen',
    keywords: ['buchung', 'fibu', 'erfassen', 'buchen'],
    icon: Calculator,
    category: 'Finanzen',
    actionId: 'finance-booking',
    actionParams: { path: '/finance/bookings/new' },
    mcp: { intent: 'create-booking', businessDomain: 'finance' },
  },

  // ── Agrar ──────────────────────────────────────────────────────────────────
  {
    id: 'nav-ernte-annahme',
    label: 'Ernte-Annahme',
    keywords: ['ernte', 'annahme', 'ernteannahme', 'harvest', 'warenannahme'],
    icon: Tractor,
    category: 'Agrar',
    actionId: 'nav-ernte-annahme',
    actionParams: { path: '/agrar/annahme' },
    mcp: { intent: 'navigate', businessDomain: 'agrar' },
  },
  {
    id: 'nav-agrar-vertraege',
    label: 'Agrar-Verträge',
    keywords: ['vertrag', 'verträge', 'agrar', 'kontrakt', 'liefervertrag'],
    icon: FileText,
    category: 'Agrar',
    actionId: 'nav-agrar-vertraege',
    actionParams: { path: '/agrar/vertraege' },
    mcp: { intent: 'navigate', businessDomain: 'agrar' },
  },
  {
    id: 'nav-silos',
    label: 'Silo-Status',
    keywords: ['silo', 'silos', 'lager', 'getreide', 'status'],
    icon: Database,
    category: 'Agrar',
    actionId: 'nav-silos',
    actionParams: { path: '/lager/silos' },
    mcp: { intent: 'navigate', businessDomain: 'agrar' },
  },
  {
    id: 'nav-schlaege',
    label: 'Schläge / Feldbuch',
    keywords: ['schlag', 'schläge', 'feldbuch', 'flurstück', 'fläche'],
    icon: Leaf,
    category: 'Agrar',
    actionId: 'nav-schlaege',
    actionParams: { path: '/agrar/schlaege' },
    mcp: { intent: 'navigate', businessDomain: 'agrar' },
  },
  {
    id: 'nav-rohware-annahme',
    label: 'Rohware-Annahme',
    keywords: ['rohware', 'annahme', 'wiegeschein', 'rohstoff'],
    icon: QrCode,
    category: 'Agrar',
    actionId: 'nav-rohware-annahme',
    actionParams: { path: '/agrar/annahme/rohware' },
    mcp: { intent: 'navigate', businessDomain: 'agrar' },
  },

  // ── POS ────────────────────────────────────────────────────────────────────
  {
    id: 'nav-pos-terminal',
    label: 'POS Terminal',
    keywords: ['pos', 'terminal', 'kasse', 'verkauf', 'kassensystem'],
    icon: Monitor,
    category: 'POS',
    actionId: 'nav-pos-terminal',
    actionParams: { path: '/pos/terminal' },
    mcp: { intent: 'navigate', businessDomain: 'pos' },
  },
  {
    id: 'nav-tagesabschluss',
    label: 'Tagesabschluss POS',
    keywords: ['tagesabschluss', 'abschluss', 'pos', 'kasse', 'abrechnung'],
    icon: CheckSquare,
    category: 'POS',
    actionId: 'nav-tagesabschluss',
    actionParams: { path: '/pos/tagesabschluss-enhanced' },
    mcp: { intent: 'navigate', businessDomain: 'pos' },
  },
  {
    id: 'nav-pos-retoure',
    label: 'Retoure',
    keywords: ['retoure', 'rückgabe', 'return', 'gutschrift', 'pos'],
    icon: RefreshCw,
    category: 'POS',
    actionId: 'nav-pos-retoure',
    actionParams: { path: '/pos/retoure' },
    mcp: { intent: 'navigate', businessDomain: 'pos' },
  },
  {
    id: 'nav-suspended-sales',
    label: 'Pausierte Verkäufe',
    keywords: ['pausiert', 'verkäufe', 'park', 'suspended', 'pos'],
    icon: ShoppingCart,
    category: 'POS',
    actionId: 'nav-suspended-sales',
    actionParams: { path: '/pos/suspended-sales' },
    mcp: { intent: 'navigate', businessDomain: 'pos' },
  },

  // ── CRM ────────────────────────────────────────────────────────────────────
  {
    id: 'nav-crm-kunden',
    label: 'Kunden (CRM)',
    keywords: ['kunden', 'crm', 'kontakte', 'customer', 'betrieb'],
    icon: Users,
    category: 'CRM',
    actionId: 'nav-crm-kunden',
    actionParams: { path: '/crm/kunden' },
    mcp: { intent: 'navigate', businessDomain: 'crm', requiredScopes: ['crm:read'] },
  },
  {
    id: 'nav-crm-leads',
    label: 'Leads',
    keywords: ['leads', 'verkaufschancen', 'opportunities', 'crm'],
    icon: Target,
    category: 'CRM',
    actionId: 'nav-crm-leads',
    actionParams: { path: '/crm/leads' },
    mcp: { intent: 'view-leads', businessDomain: 'crm', requiredScopes: ['crm:read'] },
  },
  {
    id: 'nav-crm-aktivitaeten',
    label: 'Aktivitäten',
    keywords: ['aktivitäten', 'termine', 'aufgaben', 'crm', 'activities'],
    icon: Calendar,
    category: 'CRM',
    actionId: 'nav-crm-aktivitaeten',
    actionParams: { path: '/crm/aktivitaeten' },
    mcp: { intent: 'view-activities', businessDomain: 'crm', requiredScopes: ['crm:read'] },
  },
  {
    id: 'nav-crm-betriebsprofile',
    label: 'Betriebsprofile',
    keywords: ['betriebsprofil', 'betriebe', 'landwirt', 'farm', 'crm'],
    icon: Tractor,
    category: 'CRM',
    actionId: 'nav-crm-betriebsprofile',
    actionParams: { path: '/crm/betriebsprofile' },
    mcp: { intent: 'view-farm-profiles', businessDomain: 'crm', requiredScopes: ['crm:read'] },
  },
  {
    id: 'nav-crm-kampagnen',
    label: 'Kampagnen',
    keywords: ['kampagne', 'marketing', 'newsletter', 'crm'],
    icon: Zap,
    category: 'CRM',
    actionId: 'nav-crm-kampagnen',
    actionParams: { path: '/crm/campaigns' },
    mcp: { intent: 'navigate', businessDomain: 'crm', requiredScopes: ['crm:read'] },
  },

  // ── Admin ──────────────────────────────────────────────────────────────────
  {
    id: 'nav-compliance-dashboard',
    label: 'Compliance Dashboard',
    keywords: ['compliance', 'dashboard', 'admin', 'aufsicht'],
    icon: ShieldCheck,
    category: 'Admin',
    actionId: 'nav-compliance-dashboard',
    actionParams: { path: '/admin/compliance' },
    mcp: { intent: 'navigate', businessDomain: 'admin', requiredScopes: ['admin:all'] },
  },
  {
    id: 'nav-data-quality',
    label: 'Datenqualität',
    keywords: ['datenqualität', 'qualität', 'data quality', 'admin'],
    icon: CheckSquare,
    category: 'Admin',
    actionId: 'nav-data-quality',
    actionParams: { path: '/admin/data-quality' },
    mcp: { intent: 'navigate', businessDomain: 'admin', requiredScopes: ['admin:all'] },
  },
  {
    id: 'settings',
    label: 'Systemeinstellungen',
    keywords: ['system', 'settings', 'einstellungen', 'konfiguration'],
    icon: Settings,
    category: 'Admin',
    actionId: 'settings',
    actionParams: { path: '/settings' },
    mcp: { intent: 'configure-system', businessDomain: 'admin', requiredScopes: ['admin:all'] },
  },
  {
    id: 'nav-benutzerverwaltung',
    label: 'Benutzerverwaltung',
    keywords: ['benutzer', 'user', 'rollen', 'rechte', 'admin'],
    icon: Users,
    category: 'Admin',
    actionId: 'nav-benutzerverwaltung',
    actionParams: { path: '/admin/users' },
    mcp: { intent: 'navigate', businessDomain: 'admin', requiredScopes: ['admin:all'] },
  },

  // ── Wissen ─────────────────────────────────────────────────────────────────
  {
    id: 'nav-wissensbasis',
    label: 'Wissensbasis',
    keywords: ['wissen', 'wissensbasis', 'knowledge', 'handbuch', 'hilfe'],
    icon: BookOpen,
    category: 'Wissen',
    actionId: 'nav-wissensbasis',
    actionParams: { path: '/wissen/wissensbasis' },
    mcp: { intent: 'navigate', businessDomain: 'help' },
  },

  // ── Hilfe / KI ─────────────────────────────────────────────────────────────
  {
    id: 'help-ai',
    label: 'Ask VALEO (AI-Hilfe)',
    keywords: ['help', 'hilfe', 'ai', 'ask', 'frage', 'assistent'],
    icon: HelpCircle,
    category: 'Hilfe',
    actionId: 'ai-ask-valeo',
    actionParams: { eventName: 'open-ask-valeo' },
    mcp: { intent: 'ai-assistance', businessDomain: 'help' },
  },
  {
    id: 'nav-dashboard',
    label: 'Dashboard',
    keywords: ['dashboard', 'startseite', 'home', 'übersicht'],
    icon: LayoutDashboard,
    category: 'Navigation',
    actionId: 'nav-dashboard',
    actionParams: { path: '/' },
    mcp: { intent: 'navigate', businessDomain: 'core' },
  },
]

// ── Schnellaktionen ──────────────────────────────────────────────────────────
const QUICK_ACTION_COMMANDS: PaletteCommand[] = [
  {
    id: 'action-new-sales-order',
    label: 'Neuer Verkaufsauftrag',
    keywords: ['neu', 'auftrag', 'anlegen', 'erstellen', 'sales', 'order'],
    icon: ShoppingCart,
    category: 'Aktionen',
    actionId: 'action-new-sales-order',
    actionParams: { path: '/verkauf/auftraege/neu' },
    mcp: { intent: 'create-sales-order', businessDomain: 'sales', requiredScopes: ['sales:write'] },
  },
  {
    id: 'action-new-eingangsrechnung',
    label: 'Neue Eingangsrechnung',
    keywords: ['neu', 'eingangsrechnung', 'rechnungseingang', 'kreditor'],
    icon: ReceiptText,
    category: 'Aktionen',
    actionId: 'action-new-eingangsrechnung',
    actionParams: { path: '/einkauf/rechnungseingang' },
    mcp: { intent: 'create-invoice', businessDomain: 'procurement', requiredScopes: ['procurement:write'] },
  },
  {
    id: 'action-pos-terminal-open',
    label: 'POS Terminal öffnen',
    keywords: ['pos', 'terminal', 'kasse', 'öffnen'],
    icon: Monitor,
    category: 'Aktionen',
    actionId: 'action-pos-terminal-open',
    actionParams: { path: '/pos/terminal' },
    mcp: { intent: 'quick-action', businessDomain: 'pos' },
  },
  {
    id: 'action-tagesabschluss-starten',
    label: 'Tagesabschluss starten',
    keywords: ['tagesabschluss', 'starten', 'abschluss', 'pos', 'kasse'],
    icon: CheckSquare,
    category: 'Aktionen',
    actionId: 'action-tagesabschluss-starten',
    actionParams: { path: '/pos/tagesabschluss-enhanced' },
    mcp: { intent: 'quick-action', businessDomain: 'pos' },
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

  // Schnellaktionen immer einfügen (agrar-Aktionen nur wenn agrar aktiv)
  appendUniqueCommands(
    commands,
    agrarEnabled
      ? QUICK_ACTION_COMMANDS
      : QUICK_ACTION_COMMANDS.filter((cmd) => {
          const path = cmd.actionParams?.path
          return typeof path === 'string' ? !path.startsWith('/agrar') : true
        }),
  )

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
