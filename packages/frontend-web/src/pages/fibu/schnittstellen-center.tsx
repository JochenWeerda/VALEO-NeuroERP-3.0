/**
 * Schnittstellen-Center – Übersicht aller FIBU-Connectoren (VALEO, DATEV, SEPA, UStVA, Import, …).
 * Mapping/Profil je Mandant und Verweise auf Exporte/Importe.
 */

import { Link } from 'react-router-dom'
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card'
import { Badge } from '@/components/ui/badge'
import {
  FileDown,
  FileUp,
  Database,
  CreditCard,
  FileText,
  Building2,
  LayoutGrid,
  ArrowRight,
  CheckCircle2,
  Clock,
} from 'lucide-react'

type Connector = {
  id: string
  name: string
  description: string
  path: string
  icon: typeof FileDown
  status: 'active' | 'planned' | 'readonly'
  category: 'export' | 'import' | 'both'
}

const CONNECTORS: Connector[] = [
  {
    id: 'valeo-neuro-erp',
    name: 'VALEO NeuroERP',
    description: 'Buchungen aus Verkauf, Einkauf, Kasse → GL + OP',
    path: '/fibu/buchungsjournal',
    icon: Database,
    status: 'active',
    category: 'both',
  },
  {
    id: 'buchungsuebergabe',
    name: 'Buchungsübergabe (ASC)',
    description: 'Export von Buchungssätzen für externe FIBU',
    path: '/fibu/schnittstelle-fibu',
    icon: FileDown,
    status: 'active',
    category: 'export',
  },
  {
    id: 'datev',
    name: 'DATEV',
    description: 'Kontenplan- und Buchungs-Export im DATEV-Format',
    path: '/finance/chart-of-accounts',
    icon: FileDown,
    status: 'active',
    category: 'export',
  },
  {
    id: 'sepa',
    name: 'SEPA / Zahlungsläufe',
    description: 'Zahlungsexport und -status für E-Banking',
    path: '/fibu/zahlungslaeufe',
    icon: CreditCard,
    status: 'active',
    category: 'export',
  },
  {
    id: 'ustva',
    name: 'USt-Voranmeldung',
    description: 'Export und ELSTER-Übermittlung',
    path: '/export/umsatzsteuervoranmeldung',
    icon: FileText,
    status: 'active',
    category: 'export',
  },
  {
    id: 'buchungsimport',
    name: 'Massen-Import',
    description: 'CSV/DATEV-Import von Buchungen',
    path: '/finance/buchungsimport',
    icon: FileUp,
    status: 'active',
    category: 'import',
  },
  {
    id: 'lohn',
    name: 'Lohn (LEXWARE / Connector)',
    description: 'Lohnbuchungen aus Lohnbuchhaltung',
    path: '/fibu/lohn-connector',
    icon: Building2,
    status: 'active',
    category: 'import',
  },
  {
    id: 'anlagen-suite',
    name: 'VALEO Suite Anlagen (Asset Ledger)',
    description: 'Anlagenbuchhaltung: Stammdaten, AfA, Abschreibungen, Umbuchungen, Abgänge – Anlagenverwaltung & Import',
    path: '/fibu/anlagen-suite',
    icon: LayoutGrid,
    status: 'active',
    category: 'both',
  },
  {
    id: 'atlas',
    name: 'ATLAS (Zoll)',
    description: 'Zollanmeldungen, Ausfuhr, EU-Übermittlung',
    path: '/fibu/atlas',
    icon: FileDown,
    status: 'planned',
    category: 'export',
  },
  {
    id: 'elster-online',
    name: 'ELSTER (Online)',
    description: 'Direkte Übermittlung UStVA, Lohnsteuer, Einkommensteuer',
    path: '/fibu/elster-online',
    icon: FileText,
    status: 'planned',
    category: 'export',
  },
  {
    id: 'asset-import',
    name: 'Anlagen-Import (CSV/DATEV)',
    description: 'Massenimport Anlagendaten aus DATEV oder CSV',
    path: '/fibu/anlagen-suite',
    icon: FileUp,
    status: 'planned',
    category: 'import',
  },
]

function statusLabel(s: Connector['status']): string {
  switch (s) {
    case 'active':
      return 'Aktiv'
    case 'planned':
      return 'Geplant'
    case 'readonly':
      return 'Nur Lesen'
    default:
      return ''
  }
}

export default function SchnittstellenCenterPage(): JSX.Element {
  return (
    <div className="p-6 max-w-6xl mx-auto">
      <div className="mb-8">
        <h1 className="text-2xl font-bold">Schnittstellen-Center</h1>
        <p className="text-muted-foreground mt-1">
          Connectoren, Exporte und Importe für die Finanzbuchhaltung. Mapping und Profile je Mandant.
        </p>
      </div>
      <div className="grid gap-4 sm:grid-cols-2 lg:grid-cols-3">
        {CONNECTORS.map((conn) => {
          const Icon = conn.icon
          const isPlaceholder = conn.status === 'planned' && conn.path === '/fibu/schnittstellen-center'
          return (
            <Card key={conn.id} className="flex flex-col">
              <CardHeader className="pb-2">
                <div className="flex items-center justify-between gap-2">
                  <div className="flex items-center gap-2">
                    <span className="rounded-lg border bg-muted/40 p-2">
                      <Icon className="h-5 w-5" />
                    </span>
                    <CardTitle className="text-base">{conn.name}</CardTitle>
                  </div>
                  <Badge variant={conn.status === 'active' ? 'default' : 'secondary'}>
                    {conn.status === 'active' ? <CheckCircle2 className="h-3 w-3 mr-1 inline" /> : <Clock className="h-3 w-3 mr-1 inline" />}
                    {statusLabel(conn.status)}
                  </Badge>
                </div>
                <CardDescription className="text-xs">{conn.description}</CardDescription>
              </CardHeader>
              <CardContent className="pt-0 mt-auto">
                {isPlaceholder ? (
                  <span className="text-sm text-muted-foreground">In Vorbereitung</span>
                ) : (
                  <Link to={conn.path}>
                    <span className="text-sm font-medium text-primary inline-flex items-center gap-1 hover:underline">
                      Öffnen <ArrowRight className="h-4 w-4" />
                    </span>
                  </Link>
                )}
              </CardContent>
            </Card>
          )
        })}
      </div>
      <p className="mt-6 text-xs text-muted-foreground">
        Import-Warteschlange und Fehlerbehandlung sowie versionierte Exporte werden in einer späteren Version ergänzt.
      </p>
    </div>
  )
}
