import { Link } from 'react-router-dom'
import { Badge } from '@/components/ui/badge'
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card'
import { useAccountingPeriods, useFibuCockpit, useFibuConnectorProfiles } from '@/lib/api/fibu'
import {
  ArrowRight,
  Building2,
  CheckCircle2,
  Clock,
  CreditCard,
  Database,
  FileDown,
  FileText,
  FileUp,
  LayoutGrid,
} from 'lucide-react'

type Connector = {
  id: string
  name: string
  description: string
  path: string
  icon: typeof FileDown
  status: 'active' | 'attention' | 'readonly'
  category: 'export' | 'import' | 'both'
}

const CONNECTORS: Connector[] = [
  {
    id: 'valeo-neuro-erp',
    name: 'VALEO NeuroERP',
    description: 'Buchungen aus Verkauf, Einkauf, Kasse und Agrar in GL und OP',
    path: '/fibu/buchungsjournal',
    icon: Database,
    status: 'active',
    category: 'both',
  },
  {
    id: 'buchungsuebergabe',
    name: 'Buchungsübergabe (ASC)',
    description: 'Export von Buchungssätzen in externe FIBU-Stacks',
    path: '/fibu/schnittstelle-fibu',
    icon: FileDown,
    status: 'active',
    category: 'export',
  },
  {
    id: 'datev',
    name: 'DATEV',
    description: 'Kontenplan-, Buchungs- und Abstimmexporte',
    path: '/finance/chart-of-accounts',
    icon: FileDown,
    status: 'active',
    category: 'export',
  },
  {
    id: 'sepa',
    name: 'SEPA / Zahlungsläufe',
    description: 'Zahlungsexport und Rückmeldung für E-Banking',
    path: '/fibu/zahlungslaeufe',
    icon: CreditCard,
    status: 'active',
    category: 'export',
  },
  {
    id: 'ustva',
    name: 'UStVA / ELSTER',
    description: 'Meldeweg, XML-Export und Einreichung',
    path: '/fibu/elster-online',
    icon: FileText,
    status: 'active',
    category: 'export',
  },
  {
    id: 'buchungsimport',
    name: 'Massen-Import',
    description: 'CSV-, DATEV- und Belegimporte mit Validierung',
    path: '/finance/buchungsimport',
    icon: FileUp,
    status: 'active',
    category: 'import',
  },
  {
    id: 'lohn',
    name: 'Lohn / Payroll',
    description: 'Lohnbuchungen mit Profilen, Mapping und Revisionspfad',
    path: '/fibu/lohn-connector',
    icon: Building2,
    status: 'active',
    category: 'import',
  },
  {
    id: 'anlagen-suite',
    name: 'Anlagen / Asset Ledger',
    description: 'Anlagenstamm, Import, AfA und Umbuchungen',
    path: '/fibu/anlagen-suite',
    icon: LayoutGrid,
    status: 'active',
    category: 'both',
  },
  {
    id: 'atlas',
    name: 'ATLAS / Zoll',
    description: 'Meldebetrieb mit Artefakt- und Bescheidspur',
    path: '/fibu/atlas',
    icon: FileDown,
    status: 'attention',
    category: 'export',
  },
]

function statusLabel(status: Connector['status']): string {
  switch (status) {
    case 'active':
      return 'Aktiv'
    case 'attention':
      return 'Prüfen'
    case 'readonly':
      return 'Nur Lesen'
    default:
      return status
  }
}

export default function SchnittstellenCenterPage(): JSX.Element {
  const { data: fibuCockpit } = useFibuCockpit()
  const { data: periods } = useAccountingPeriods()
  const { data: payrollProfiles } = useFibuConnectorProfiles('PAYROLL')
  const { data: assetProfiles } = useFibuConnectorProfiles('ASSET_LEDGER')

  const openPeriods = periods.filter((period) => period.status === 'OPEN').length
  const adjustingPeriods = periods.filter((period) => period.status === 'ADJUSTING').length

  return (
    <div className="mx-auto max-w-7xl space-y-6 p-6">
      <div>
        <h1 className="text-2xl font-bold">Schnittstellen-Center</h1>
        <p className="mt-1 text-muted-foreground">
          Profile, Exportpfade, Revisionslage und Periodenstatus für den FIBU-Kern.
        </p>
      </div>

      <div className="grid gap-4 md:grid-cols-4">
        <Card>
          <CardHeader className="pb-2"><CardTitle className="text-sm">Connector-Profile</CardTitle></CardHeader>
          <CardContent><div className="text-2xl font-semibold">{fibuCockpit.master_data.connector_profile_count}</div></CardContent>
        </Card>
        <Card>
          <CardHeader className="pb-2"><CardTitle className="text-sm">Exportläufe</CardTitle></CardHeader>
          <CardContent><div className="text-2xl font-semibold">{fibuCockpit.revision.export_runs}</div></CardContent>
        </Card>
        <Card>
          <CardHeader className="pb-2"><CardTitle className="text-sm">Perioden offen</CardTitle></CardHeader>
          <CardContent><div className="text-2xl font-semibold">{openPeriods}</div></CardContent>
        </Card>
        <Card>
          <CardHeader className="pb-2"><CardTitle className="text-sm">Reorganisator</CardTitle></CardHeader>
          <CardContent><div className="text-sm font-semibold">{adjustingPeriods > 0 ? `${adjustingPeriods} in Nachbearbeitung` : 'stabil'}</div></CardContent>
        </Card>
      </div>

      <Card>
        <CardHeader>
          <CardTitle>Masterdaten- und Revisionslage</CardTitle>
          <CardDescription>Exklusive FIBU-Parameter, Profilversionen und technische Reife pro Connector.</CardDescription>
        </CardHeader>
        <CardContent className="grid gap-4 lg:grid-cols-3">
          <div className="rounded-lg border p-4">
            <div className="text-sm font-semibold">Mahn- und Zinsparameter</div>
            <div className="mt-3 flex flex-wrap gap-2">
              <Badge variant={fibuCockpit.master_data.dunning_parameters_ready ? 'outline' : 'secondary'}>
                Mahnparameter {fibuCockpit.master_data.dunning_parameters_ready ? 'bereit' : 'offen'}
              </Badge>
              <Badge variant={fibuCockpit.master_data.interest_groups_ready ? 'outline' : 'secondary'}>
                Zinsgruppen {fibuCockpit.master_data.interest_groups_ready ? 'bereit' : 'ergänzen'}
              </Badge>
            </div>
          </div>
          <div className="rounded-lg border p-4">
            <div className="text-sm font-semibold">Payroll-Profile</div>
            <div className="mt-2 text-2xl font-semibold">{payrollProfiles.length}</div>
            <div className="mt-2 text-xs text-muted-foreground">
              {payrollProfiles[0] ? `${payrollProfiles[0].name} · Version ${payrollProfiles[0].version}` : 'Noch kein Profil angelegt'}
            </div>
          </div>
          <div className="rounded-lg border p-4">
            <div className="text-sm font-semibold">Asset-Ledger-Profile</div>
            <div className="mt-2 text-2xl font-semibold">{assetProfiles.length}</div>
            <div className="mt-2 text-xs text-muted-foreground">
              {assetProfiles[0] ? `${assetProfiles[0].name} · Version ${assetProfiles[0].version}` : 'Noch kein Profil angelegt'}
            </div>
          </div>
        </CardContent>
      </Card>

      <div className="grid gap-4 sm:grid-cols-2 xl:grid-cols-3">
        {CONNECTORS.map((connector) => {
          const Icon = connector.icon
          const exportInfo =
            connector.id === 'ustva'
              ? fibuCockpit.exports.find((item) => item.kind === 'vat_return')
              : undefined

          return (
            <Card key={connector.id} className="flex flex-col">
              <CardHeader className="pb-2">
                <div className="flex items-center justify-between gap-2">
                  <div className="flex items-center gap-2">
                    <span className="rounded-lg border bg-muted/40 p-2">
                      <Icon className="h-5 w-5" />
                    </span>
                    <CardTitle className="text-base">{connector.name}</CardTitle>
                  </div>
                  <Badge variant={connector.status === 'active' ? 'default' : 'secondary'}>
                    {connector.status === 'active' ? <CheckCircle2 className="mr-1 inline h-3 w-3" /> : <Clock className="mr-1 inline h-3 w-3" />}
                    {statusLabel(connector.status)}
                  </Badge>
                </div>
                <CardDescription className="text-xs">{connector.description}</CardDescription>
              </CardHeader>
              <CardContent className="mt-auto space-y-3 pt-0">
                {connector.id === 'ustva' ? (
                  <div className="rounded-lg border bg-muted/20 p-3 text-xs text-muted-foreground">
                    eBilanz {fibuCockpit.tax.e_bilanz_ready ? 'bereit' : 'vorbereiten'} ·
                    E-Clearing {fibuCockpit.tax.e_clearing_ready ? 'bereit' : 'offen'} ·
                    letzte Periode {fibuCockpit.tax.latest_period ?? 'n/a'}
                    {exportInfo?.latest_created_at ? ` · letzter Export ${new Date(exportInfo.latest_created_at).toLocaleDateString('de-DE')}` : ''}
                  </div>
                ) : null}
                <Link to={connector.path}>
                  <span className="inline-flex items-center gap-1 text-sm font-medium text-primary hover:underline">
                    Öffnen <ArrowRight className="h-4 w-4" />
                  </span>
                </Link>
              </CardContent>
            </Card>
          )
        })}
      </div>
    </div>
  )
}
