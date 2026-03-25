import {
  BookOpen,
  Boxes,
  BriefcaseBusiness,
  ClipboardCheck,
  Compass,
  Factory,
  Landmark,
  LayoutDashboard,
  Leaf,
  Package,
  ReceiptText,
  ScanLine,
  ShieldCheck,
  ShoppingCart,
  Store,
  Truck,
  Users,
  Warehouse,
  Wrench,
  Zap,
  type LucideIcon,
} from 'lucide-react'
import type { NavItem } from '@/app/navigation/types'

type DashboardLanguage = 'de' | 'en'

type DashboardText = {
  de: string
  en: string
}

type SectionPreset = {
  landingItemId?: string
  landingPath?: string
  description: DashboardText
}

type DomainPreset = {
  label: DashboardText
  icon: LucideIcon
}

export type DashboardDomainPresentation = {
  label: string
  icon: LucideIcon
}

export type DashboardSectionPresentation = {
  description: string
  landingPath?: string
  landingLabel: string
  domain: DashboardDomainPresentation
}

const DOMAIN_PRESETS: Record<string, DomainPreset> = {
  admin: { label: { de: 'Administration', en: 'Administration' }, icon: ShieldCheck },
  agrar: { label: { de: 'Agrar', en: 'Agribusiness' }, icon: Leaf },
  compliance: { label: { de: 'Compliance', en: 'Compliance' }, icon: ShieldCheck },
  core: { label: { de: 'Start', en: 'Home' }, icon: LayoutDashboard },
  crm: { label: { de: 'CRM', en: 'CRM' }, icon: Users },
  finance: { label: { de: 'Finanzen', en: 'Finance' }, icon: Landmark },
  hr: { label: { de: 'Personal', en: 'HR' }, icon: Users },
  inventory: { label: { de: 'Lager', en: 'Inventory' }, icon: Warehouse },
  knowledge: { label: { de: 'Wissen', en: 'Knowledge' }, icon: BookOpen },
  logistics: { label: { de: 'Logistik', en: 'Logistics' }, icon: Truck },
  marketing: { label: { de: 'Marketing', en: 'Marketing' }, icon: Compass },
  pos: { label: { de: 'Kasse', en: 'POS' }, icon: Store },
  procurement: { label: { de: 'Einkauf', en: 'Procurement' }, icon: ShoppingCart },
  quality: { label: { de: 'Qualität', en: 'Quality' }, icon: ClipboardCheck },
  sales: { label: { de: 'Vertrieb', en: 'Sales' }, icon: ReceiptText },
  service: { label: { de: 'Service', en: 'Service' }, icon: Wrench },
  wissen: { label: { de: 'Wissen', en: 'Knowledge' }, icon: BookOpen },
  workflow: { label: { de: 'Prozesse', en: 'Processes' }, icon: Zap },
}

const DOMAIN_ALIASES: Record<string, string> = {
  vertrieb: 'sales',
  einkauf: 'procurement',
  lager: 'inventory',
  agrar: 'agrar',
  qualitaet: 'quality',
  'qualität': 'quality',
  service: 'service',
  finanzen: 'finance',
  compliance: 'compliance',
  prozesse: 'workflow',
  wissen: 'knowledge',
}

const SECTION_PRESETS: Record<string, SectionPreset> = {
  dashboard: {
    landingPath: '/',
    description: {
      de: 'Persönliche Startseite mit Kennzahlen, Schnellaktionen und Prozessräumen.',
      en: 'Personal home with KPIs, shortcuts, and process rooms.',
    },
  },
  workflow: {
    landingItemId: 'workflow-flow-spine',
    description: {
      de: 'End-to-End-Prozesse, Freigaben und KI-Steuerung in einem Arbeitsraum.',
      en: 'End-to-end workflows, approvals, and AI control in one workspace.',
    },
  },
  admin: {
    landingItemId: 'monitoring',
    description: {
      de: 'Systemsteuerung, Monitoring, Datenqualität und Agenten-Governance.',
      en: 'System control, monitoring, data quality, and agent governance.',
    },
  },
  wissen: {
    landingPath: '/wissen/wissensbasis',
    description: {
      de: 'Zentraler Wissensspeicher für Richtlinien, Standards und Prozesswissen.',
      en: 'Central knowledge store for policies, standards, and process know-how.',
    },
  },
  kundenportal: {
    landingPath: '/portal',
    description: {
      de: 'Externer Kundenbereich für Bestellungen, Dokumente und Servicezugriffe.',
      en: 'External customer area for orders, documents, and service access.',
    },
  },
  verkauf: {
    landingItemId: 'sales-dashboard',
    description: {
      de: 'Vertrieb, Aufträge, Lieferungen und Faktura mit Tagessteuerung.',
      en: 'Sales, orders, deliveries, and invoicing with daily steering.',
    },
  },
  crm: {
    landingItemId: 'kontakte',
    description: {
      de: 'Kundenbeziehungen, Kampagnen und Marktpotenziale auf einen Blick.',
      en: 'Customer relations, campaigns, and market potential in one place.',
    },
  },
  einkauf: {
    landingItemId: 'einkauf-dashboard',
    description: {
      de: 'Bedarf, Bestellungen, Wareneingang und Rechnungsabgleich steuern.',
      en: 'Control demand, purchase orders, goods receipt, and invoice matching.',
    },
  },
  fibu: {
    landingPath: '/fibu-suite',
    description: {
      de: 'Buchhaltung, Zahlungsflüsse und Abschlussarbeiten in der FIBU-Suite.',
      en: 'Accounting, payments, and close activities in the finance suite.',
    },
  },
  controlling: {
    landingItemId: 'plan-ist',
    description: {
      de: 'KPI-Steuerung, Benchmarking und Maßnahmen für Management und Teams.',
      en: 'KPI steering, benchmarking, and actions for management and teams.',
    },
  },
  lager: {
    landingItemId: 'bestandsuebersicht',
    description: {
      de: 'Bestände, Lagerbewegungen und Inventur im operativen Überblick.',
      en: 'Inventory, stock movements, and counting in one operational view.',
    },
  },
  agrar: {
    landingItemId: 'ernte',
    description: {
      de: 'Agrarhandel, Ernte, Feldbuch und Betriebsmittel fachlich gebündelt.',
      en: 'Agribusiness, harvest, field records, and inputs in one domain.',
    },
  },
  annahme: {
    landingItemId: 'warteschlange',
    description: {
      de: 'Annahme, Waage und Hoflogistik mit klarem Einstieg in die Tagessteuerung.',
      en: 'Receiving, weighbridge, and yard logistics with a clear daily start point.',
    },
  },
  quality: {
    landingItemId: 'qm-dokumente',
    description: {
      de: 'Qualitätsdokumente, Audit-Trails und Prüfprozesse zentral verwalten.',
      en: 'Manage quality documents, audit trails, and inspections centrally.',
    },
  },
  compliance: {
    landingItemId: 'policies',
    description: {
      de: 'Richtlinien, ESG, EUDR und Meldungen revisionssicher steuern.',
      en: 'Control policies, ESG, EUDR, and reporting with auditability.',
    },
  },
  logistik: {
    landingItemId: 'tourenplanung',
    description: {
      de: 'Touren, Fuhrpark und Streckengeschäft für Disposition und Versand.',
      en: 'Tours, fleet, and direct-route logistics for dispatch and shipping.',
    },
  },
  versand: {
    landingItemId: 'versand-avis',
    description: {
      de: 'Versandavis, Frachtdokumente und Etiketten für den Versandstart.',
      en: 'Shipping notices, freight documents, and labels for outbound processes.',
    },
  },
  produktion: {
    landingItemId: 'produktions-dokumente-drucken',
    description: {
      de: 'Produktionsnahe Dokumente und Ablaufunterlagen für Fertigung und Mischungen.',
      en: 'Production documents and work papers for manufacturing and blends.',
    },
  },
  pos: {
    landingItemId: 'pos-terminal',
    description: {
      de: 'Kasse, TSE und Filialabschluss für den stationären Verkauf.',
      en: 'Checkout, fiscal logs, and branch close for retail operations.',
    },
  },
  personal: {
    landingItemId: 'mitarbeiter-liste',
    description: {
      de: 'Mitarbeiter, Qualifikationen, Schulungen und Zeitdaten verwalten.',
      en: 'Manage employees, qualifications, trainings, and time records.',
    },
  },
}

function normalizeLanguage(lang?: string): DashboardLanguage {
  const normalized = (lang ?? 'de').split('-')[0].toLowerCase()
  return normalized === 'en' ? 'en' : 'de'
}

function translate(text: DashboardText, lang?: string): string {
  return text[normalizeLanguage(lang)]
}

function findNavItemById(item: NavItem, itemId: string): NavItem | null {
  if (item.id === itemId) {
    return item
  }
  for (const child of item.children ?? []) {
    const match = findNavItemById(child, itemId)
    if (match) {
      return match
    }
  }
  return null
}

export function findFirstRoutableChild(item: NavItem): NavItem | null {
  if (item.path && !item.path.includes(':')) {
    return item
  }
  for (const child of item.children ?? []) {
    const found = findFirstRoutableChild(child)
    if (found) {
      return found
    }
  }
  return null
}

export function getDomainPresentation(domain: string, lang?: string): DashboardDomainPresentation {
  const normalizedDomain = domain.trim().toLowerCase()
  const domainKey = DOMAIN_ALIASES[normalizedDomain] ?? normalizedDomain
  const preset = DOMAIN_PRESETS[domainKey] ?? { label: { de: domain, en: domain }, icon: Boxes }
  return {
    label: translate(preset.label, lang),
    icon: preset.icon,
  }
}

export function getSectionPresentation(section: NavItem, lang?: string): DashboardSectionPresentation {
  const preset = SECTION_PRESETS[section.id]
  const landingItem =
    (preset?.landingItemId ? findNavItemById(section, preset.landingItemId) : null) ??
    findFirstRoutableChild(section)
  const domain = getDomainPresentation(section.mcp.businessDomain, lang)

  return {
    description:
      preset?.description
        ? translate(preset.description, lang)
        : `${domain.label} ${normalizeLanguage(lang) === 'de' ? 'starten und steuern' : 'workspace and operations'}`,
    landingPath: preset?.landingPath ?? landingItem?.path,
    landingLabel: landingItem?.label ?? section.label,
    domain,
  }
}
