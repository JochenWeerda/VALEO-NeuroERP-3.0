import { useMemo, useState } from 'react'
import { useTranslation } from 'react-i18next'
import { useNavigate } from 'react-router-dom'
import { Archive, Download, Filter, Plus, Search, Sparkles, Upload } from 'lucide-react'
import { PageToolbar, type ToolbarAction } from '@/components/navigation/PageToolbar'
import { PageSection, PageSurface } from '@/components/patterns/PageSurface'
import { Badge } from '@/components/ui/badge'
import { Button } from '@/components/ui/button'
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card'
import { Input } from '@/components/ui/input'
import { DataTable } from '@/components/ui/data-table'
import { getEntityTypeLabel, getListTitle, getStatusLabel } from '@/features/crud/utils/i18n-helpers'
import { useAuftraege, type Auftrag, type AuftragStatus } from '@/lib/api/sales'

const STATUS_OPTIONS: Array<{ value: AuftragStatus | 'alle'; label: string }> = [
  { value: 'alle', label: 'Alle Status' },
  { value: 'offen', label: 'Offen' },
  { value: 'teilgeliefert', label: 'Teilgeliefert' },
  { value: 'geliefert', label: 'Geliefert' },
  { value: 'fakturiert', label: 'Fakturiert' },
  { value: 'storniert', label: 'Storniert' },
]

const statusVariantMap: Record<AuftragStatus, 'default' | 'outline' | 'secondary' | 'destructive'> = {
  open: 'default',
  offen: 'default',
  teilgeliefert: 'secondary',
  geliefert: 'outline',
  fakturiert: 'outline',
  storniert: 'destructive',
}

function downloadCsv(rows: Auftrag[]): void {
  const header = ['Auftragsnummer', 'Datum', 'Kunde', 'Betrag', 'Liefertermin', 'Status']
  const lines = rows.map((auftrag) =>
    [
      auftrag.nummer,
      auftrag.datum,
      auftrag.kunde,
      auftrag.betrag.toFixed(2).replace('.', ','),
      auftrag.liefertermin,
      auftrag.status,
    ]
      .map((value) => `"${String(value).replaceAll('"', '""')}"`)
      .join(';'),
  )
  const csv = [header.join(';'), ...lines].join('\n')
  const blob = new Blob([csv], { type: 'text/csv;charset=utf-8' })
  const url = URL.createObjectURL(blob)
  const link = document.createElement('a')
  link.href = url
  link.download = `sales-orders-${new Date().toISOString().slice(0, 10)}.csv`
  link.click()
  URL.revokeObjectURL(url)
}

export default function SalesOrdersModernPage(): JSX.Element {
  const { t } = useTranslation()
  const navigate = useNavigate()
  const entityType = 'salesOrder'
  const entityTypeLabel = getEntityTypeLabel(t, entityType, 'Verkaufsauftrag')
  const pageTitle = getListTitle(t, entityTypeLabel)
  const [searchTerm, setSearchTerm] = useState('')
  const [statusFilter, setStatusFilter] = useState<AuftragStatus | 'alle'>('alle')
  const [showFilters, setShowFilters] = useState(false)

  const { data: orders = [] } = useAuftraege()

  const filteredOrders = useMemo(() => {
    return orders.filter((order) => {
      const matchesSearch =
        !searchTerm ||
        order.nummer.toLowerCase().includes(searchTerm.toLowerCase()) ||
        order.kunde.toLowerCase().includes(searchTerm.toLowerCase())
      const matchesStatus = statusFilter === 'alle' || order.status === statusFilter
      return matchesSearch && matchesStatus
    })
  }, [orders, searchTerm, statusFilter])

  const quickStats = useMemo(() => {
    const open = filteredOrders.filter((order) => order.status === 'offen' || order.status === 'open').length
    const partial = filteredOrders.filter((order) => order.status === 'teilgeliefert').length
    const invoiceReady = filteredOrders.filter((order) => order.status === 'geliefert').length
    const archiveReady = filteredOrders.filter(
      (order) => order.status === 'fakturiert' || order.status === 'storniert',
    ).length
    return { open, partial, invoiceReady, archiveReady }
  }, [filteredOrders])

  const focusOrder = filteredOrders[0]

  const primaryActions: ToolbarAction[] = [
    {
      id: 'new-order',
      label: `${t('crud.actions.new')} ${entityTypeLabel}`,
      icon: <Plus className="h-4 w-4" />,
      onClick: () => navigate('/sales/orders/new'),
      variant: 'default',
      shortcut: 'Ctrl+N',
      mcp: {
        intent: 'create-sales-order',
        requiredData: ['customer', 'articles'],
      },
    },
    {
      id: 'export',
      label: t('crud.actions.export'),
      icon: <Download className="h-4 w-4" />,
      onClick: () => downloadCsv(filteredOrders),
      variant: 'outline',
      mcp: {
        intent: 'export-data',
        requiredData: ['selection'],
      },
    },
  ]

  const overflowActions: ToolbarAction[] = [
    {
      id: 'import',
      label: t('crud.actions.import'),
      icon: <Upload className="h-4 w-4" />,
      onClick: () => navigate('/sales/auftraege-liste'),
      mcp: {
        intent: 'import-data',
      },
    },
    {
      id: 'filter',
      label: t('crud.actions.filter'),
      icon: <Filter className="h-4 w-4" />,
      onClick: () => setShowFilters((current) => !current),
      mcp: {
        intent: 'filter-data',
      },
    },
    {
      id: 'archive',
      label: t('crud.actions.archive'),
      icon: <Archive className="h-4 w-4" />,
      onClick: () => navigate('/sales/auftraege-liste?status=fakturiert'),
      variant: 'destructive',
      mcp: {
        intent: 'archive-data',
        requiresConfirmation: true,
        requiredData: ['selection'],
      },
    },
  ]

  const columns = [
    {
      key: 'nummer' as const,
      label: t('crud.fields.number'),
      render: (order: Auftrag) => (
        <button
          onClick={() => navigate(`/sales/order-editor?id=${order.id}`)}
          className="font-medium text-blue-600 hover:underline"
        >
          {order.nummer}
        </button>
      ),
    },
    {
      key: 'kunde' as const,
      label: t('crud.entities.customer'),
    },
    {
      key: 'betrag' as const,
      label: t('crud.fields.total'),
      render: (order: Auftrag) =>
        new Intl.NumberFormat('de-DE', { style: 'currency', currency: 'EUR' }).format(order.betrag),
    },
    {
      key: 'liefertermin' as const,
      label: t('crud.fields.deliveryDate'),
    },
    {
      key: 'status' as const,
      label: t('crud.fields.status'),
      render: (order: Auftrag) => (
        <Badge variant={statusVariantMap[order.status]}>
          {getStatusLabel(t, order.status, order.status)}
        </Badge>
      ),
    },
  ]

  return (
    <>
      <PageToolbar
        title={pageTitle}
        subtitle="Vertriebslage, Folgeaktionen und operative Arbeitsplaetze fuer offene Auftraege."
        primaryActions={primaryActions}
        overflowActions={overflowActions}
        mcpContext={{
          pageDomain: 'sales',
          currentDocument: focusOrder?.id,
          availableActions: ['create', 'export', 'import', 'filter', 'archive'],
        }}
      />

      <PageSurface data-page-surface="sales-orders-modern">
        <PageSection
          title={pageTitle}
          description="Die Seite ist jetzt an die reale Auftragslage angebunden und fuehrt in die produktiven Arbeitsplaetze fuer Export, Import, Bearbeitung und Archivvorbereitung."
        >
          <div className="grid gap-4 md:grid-cols-4">
            <Card>
              <CardHeader className="pb-2">
                <CardTitle className="text-sm font-medium">Offene Auftraege</CardTitle>
              </CardHeader>
              <CardContent>
                <div className="text-2xl font-bold">{quickStats.open}</div>
              </CardContent>
            </Card>
            <Card>
              <CardHeader className="pb-2">
                <CardTitle className="text-sm font-medium">Teilgeliefert</CardTitle>
              </CardHeader>
              <CardContent>
                <div className="text-2xl font-bold">{quickStats.partial}</div>
              </CardContent>
            </Card>
            <Card>
              <CardHeader className="pb-2">
                <CardTitle className="text-sm font-medium">Rechnungsfaehig</CardTitle>
              </CardHeader>
              <CardContent>
                <div className="text-2xl font-bold">{quickStats.invoiceReady}</div>
              </CardContent>
            </Card>
            <Card>
              <CardHeader className="pb-2">
                <CardTitle className="text-sm font-medium">Archivkandidaten</CardTitle>
              </CardHeader>
              <CardContent>
                <div className="text-2xl font-bold">{quickStats.archiveReady}</div>
              </CardContent>
            </Card>
          </div>

          <div className="grid gap-4 lg:grid-cols-[2fr_1fr]">
            <Card>
              <CardHeader>
                <CardTitle>Operative Sicht</CardTitle>
              </CardHeader>
              <CardContent className="space-y-4">
                <div className="flex flex-col gap-3 lg:flex-row">
                  <div className="relative flex-1">
                    <Search className="absolute left-3 top-1/2 h-4 w-4 -translate-y-1/2 text-muted-foreground" />
                    <Input
                      value={searchTerm}
                      onChange={(event) => setSearchTerm(event.target.value)}
                      placeholder="Auftragsnummer oder Kunde suchen"
                      className="pl-10"
                    />
                  </div>
                  <Button variant="outline" onClick={() => setShowFilters((current) => !current)} className="gap-2">
                    <Filter className="h-4 w-4" />
                    Filter
                  </Button>
                  <Button variant="outline" onClick={() => navigate('/sales/auftraege-liste')} className="gap-2">
                    <Upload className="h-4 w-4" />
                    Importarbeitsplatz
                  </Button>
                </div>

                {showFilters ? (
                  <div className="rounded-2xl border bg-muted/40 p-4">
                    <label className="mb-2 block text-sm font-medium">Statusfilter</label>
                    <select
                      value={statusFilter}
                      onChange={(event) => setStatusFilter(event.target.value as AuftragStatus | 'alle')}
                      className="flex h-10 w-full rounded-md border border-input bg-background px-3 py-2 text-sm"
                    >
                      {STATUS_OPTIONS.map((option) => (
                        <option key={option.value} value={option.value}>
                          {option.label}
                        </option>
                      ))}
                    </select>
                  </div>
                ) : null}

                <DataTable data={filteredOrders} columns={columns} />
                <p className="text-sm text-muted-foreground">
                  {filteredOrders.length} von {orders.length} Auftraegen sichtbar.
                </p>
              </CardContent>
            </Card>

            <Card>
              <CardHeader>
                <CardTitle className="flex items-center gap-2">
                  <Sparkles className="h-4 w-4" />
                  Naechste empfohlene Aktion
                </CardTitle>
              </CardHeader>
              <CardContent className="space-y-4">
                {focusOrder ? (
                  <>
                    <div className="rounded-2xl border bg-muted/40 p-4">
                      <div className="text-sm text-muted-foreground">Fokusauftrag</div>
                      <div className="font-semibold">{focusOrder.nummer}</div>
                      <div className="text-sm">{focusOrder.kunde}</div>
                      <div className="mt-2">
                        <Badge variant={statusVariantMap[focusOrder.status]}>
                          {getStatusLabel(t, focusOrder.status, focusOrder.status)}
                        </Badge>
                      </div>
                    </div>
                    <div className="space-y-2 text-sm text-muted-foreground">
                      <p>
                        Offene und teilgelieferte Auftraege gehoeren in die operative Bearbeitung, fakturierte oder stornierte Faelle in die Archivvorbereitung.
                      </p>
                      <p>
                        Export und Import laufen nicht mehr als Platzhalter, sondern ueber CSV-Download und den produktiven Auftragsarbeitsplatz.
                      </p>
                    </div>
                    <div className="grid gap-2">
                      <Button onClick={() => navigate(`/sales/order-editor?id=${focusOrder.id}`)}>
                        Auftrag bearbeiten
                      </Button>
                      <Button variant="outline" onClick={() => navigate('/sales/auftraege-liste')}>
                        Auftragsliste mit Import oeffnen
                      </Button>
                      <Button variant="outline" onClick={() => navigate('/sales/auftraege-liste?status=fakturiert')}>
                        Archivvorbereitung anzeigen
                      </Button>
                    </div>
                  </>
                ) : (
                  <div className="rounded-2xl border border-dashed p-4 text-sm text-muted-foreground">
                    Keine Auftraege fuer die aktuelle Filterlage gefunden.
                  </div>
                )}
              </CardContent>
            </Card>
          </div>
        </PageSection>
      </PageSurface>
    </>
  )
}
