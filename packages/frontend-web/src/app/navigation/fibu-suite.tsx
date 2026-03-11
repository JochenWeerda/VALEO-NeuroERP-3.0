import {
  BarChart3,
  Building2,
  Calendar,
  Calculator,
  Database,
  Euro,
  FileDown,
  FileText,
  LayoutDashboard,
  LayoutGrid,
  RefreshCw,
  ShieldCheck,
  ShoppingCart,
  Upload,
  Users,
  Zap,
} from 'lucide-react'
import { resolveRoutePathFromModule } from '@/app/navigation/route-paths'

export type FibuSuiteItem = {
  id: string
  label: string
  icon: typeof LayoutDashboard
  module: string
  path: string
}

const FIBU_SUITE_CONFIG: Array<{
  id: string
  label: string
  icon: typeof LayoutDashboard
  module: string
  preferredPath?: string
}> = [
  { id: 'hauptbuch', label: 'Hauptbuch', icon: FileText, module: '@/pages/fibu/hauptbuch' },
  { id: 'debitoren', label: 'Debitoren', icon: Users, module: '@/pages/fibu/debitoren' },
  { id: 'kreditoren', label: 'Kreditoren', icon: Users, module: '@/pages/fibu/kreditoren' },
  { id: 'buchungsjournal', label: 'Buchungsjournal', icon: FileText, module: '@/pages/fibu/buchungsjournal' },
  { id: 'kontenplan', label: 'Kontenplan', icon: FileText, module: '@/pages/fibu/kontenplan' },
  { id: 'bilanz', label: 'Bilanz', icon: BarChart3, module: '@/pages/fibu/bilanz' },
  { id: 'guv', label: 'GuV', icon: BarChart3, module: '@/pages/fibu/guv' },
  { id: 'bwa', label: 'BWA', icon: BarChart3, module: '@/pages/fibu/bwa' },
  { id: 'anlagen', label: 'Anlagenbuchhaltung', icon: Building2, module: '@/pages/fibu/anlagen' },
  { id: 'op-verwaltung', label: 'OP-Verwaltung', icon: Euro, module: '@/pages/fibu/op-verwaltung' },
  { id: 'offene-posten', label: 'Offene Posten', icon: Euro, module: '@/pages/fibu/offene-posten' },
  { id: 'abschluss-cockpit', label: 'Abschluss-Cockpit', icon: ShieldCheck, module: '@/pages/fibu/abschluss-cockpit', preferredPath: 'fibu/abschluss-cockpit' },
  { id: 'zahlungslaeufe', label: 'Zahlungslaeufe', icon: Euro, module: '@/pages/fibu/zahlungslaeufe' },
  { id: 'zahlungseingaenge', label: 'Zahlungseingaenge & Matching', icon: Euro, module: '@/pages/finance/payment-matching', preferredPath: 'finance/payments' },
  { id: 'bank-stamm', label: 'Bankkonten (Bankstamm)', icon: Building2, module: '@/pages/finance/bank-stamm', preferredPath: 'finance/bank-stamm' },
  { id: 'op-debitoren-finance', label: 'OP Debitoren', icon: Euro, module: '@/pages/finance/op-debitoren', preferredPath: 'finance/op-debitoren' },
  { id: 'op-kreditoren-finance', label: 'OP Kreditoren', icon: Euro, module: '@/pages/finance/op-kreditoren', preferredPath: 'finance/op-kreditoren' },
  { id: 'nebenbuch-abstimmung', label: 'Nebenbuch-Abstimmung', icon: BarChart3, module: '@/pages/finance/nebenbuch-abstimmung', preferredPath: 'finance/nebenbuch-abstimmung' },
  { id: 'kostenstellenrechnung', label: 'Kostenstellen', icon: Calculator, module: '@/pages/fibu/kostenstellenrechnung' },
  { id: 'ustva', label: 'USt.-Voranmeldung', icon: FileText, module: '@/pages/export/umsatzsteuervoranmeldung', preferredPath: 'export/ustva' },
  { id: 'audit-trail-finance', label: 'Audit-Trail (GoBD)', icon: ShieldCheck, module: '@/pages/finance/audit-trail' },
  { id: 'periodensteuerung', label: 'Periodensteuerung', icon: Calendar, module: '@/pages/finance/periods', preferredPath: 'finance/periods' },
  { id: 'wechselkurse', label: 'Wechselkurse', icon: RefreshCw, module: '@/pages/finance/wechselkurse' },
  { id: 'buchungsvorlagen', label: 'Buchungsvorlagen', icon: FileText, module: '@/pages/finance/buchungsvorlagen' },
  { id: 'buchungsimport', label: 'Massen-Import', icon: Upload, module: '@/pages/finance/buchungsimport' },
  { id: 'uebernahme-tagesabschluss-pos', label: 'Uebernahme Buchungen Tagesabschluss POS', icon: ShoppingCart, module: '@/pages/pos/tagesabschluss-enhanced', preferredPath: 'pos/tagesabschluss' },
  { id: 'buchungsuebernahme-connectors', label: 'Buchungsuebernahme Connectors', icon: Zap, module: '@/pages/fibu/buchungsuebernahme-connectors', preferredPath: 'fibu/buchungsuebernahme-connectors' },
  { id: 'buchhaltungsuebersicht', label: 'Buchhaltungsuebersicht', icon: BarChart3, module: '@/pages/fibu/buchhaltungsuebersicht' },
  { id: 'monatswerte', label: 'Monatswerte fuer mehrere Monate', icon: BarChart3, module: '@/pages/fibu/monatswerte' },
  { id: 'uebernahme-kasse', label: 'Uebernahme Kasse', icon: Database, module: '@/pages/pos/uebernahme-kasse' },
  { id: 'ubergabe-fibu', label: 'Uebergabe an FIBU', icon: FileDown, module: '@/pages/fibu/schnittstelle-fibu' },
  { id: 'schnittstelle-fibu', label: 'Schnittstelle FIBU', icon: FileDown, module: '@/pages/fibu/schnittstelle-fibu' },
  { id: 'schnittstellen-center', label: 'Schnittstellen-Center', icon: LayoutDashboard, module: '@/pages/fibu/schnittstellen-center' },
  { id: 'lohn-connector', label: 'Lohn-Connector', icon: Building2, module: '@/pages/fibu/lohn-connector' },
  { id: 'anlagen-suite', label: 'VALEO Suite Anlagen (Asset Ledger)', icon: LayoutGrid, module: '@/pages/fibu/anlagen-suite' },
  { id: 'atlas', label: 'ATLAS (Zoll)', icon: FileDown, module: '@/pages/fibu/atlas' },
  { id: 'elster-online', label: 'ELSTER (Online)', icon: FileText, module: '@/pages/fibu/elster-online' },
]

export const FIBU_SUITE_ITEMS: FibuSuiteItem[] = FIBU_SUITE_CONFIG.map((item) => ({
  id: item.id,
  label: item.label,
  icon: item.icon,
  module: item.module,
  path: resolveRoutePathFromModule(item.module, item.preferredPath),
}))
