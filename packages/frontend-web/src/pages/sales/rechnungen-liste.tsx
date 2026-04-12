import { useState } from 'react'
import { useNavigate } from 'react-router-dom'
import { useTranslation } from 'react-i18next'
import { Button } from '@/components/ui/button'
import { Input } from '@/components/ui/input'
import { Badge } from '@/components/ui/badge'
import { DataTable } from '@/components/ui/data-table'
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card'
import { FileDown, FileText, Receipt, Search } from 'lucide-react'
import { getEntityTypeLabel, getListTitle, getStatusLabel } from '@/features/crud/utils/i18n-helpers'
import { AdvancedFilters, FilterConfig } from '@/components/list/AdvancedFilters'
import { CSVImport } from '@/components/list/CSVImport'
import { OperationalCaseHeader } from '@/components/workflow/OperationalCaseHeader'
import { OperationalContextPanel } from '@/components/workflow/OperationalContextPanel'
import { OperationalTimeline } from '@/components/workflow/OperationalTimeline'
import { useToast } from '@/hooks/use-toast'
import { useListActions } from '@/hooks/useListActions'
import { formatDateForExport, formatCurrencyForExport } from '@/lib/export-utils'
import { saveDocument } from '@/lib/document-api'
import { getAxiosErrorMessage } from '@/lib/api-client'
import { useRechnungen, type Rechnung, type RechnungStatus } from '@/lib/api/sales'
import { normalizeOperationalStatus } from '@/lib/operational-status'

const statusVariantMap: Record<RechnungStatus, 'default' | 'outline' | 'secondary' | 'destructive'> = {
  offen: 'default',
  teilbezahlt: 'secondary',
  bezahlt: 'outline',
  ueberfaellig: 'destructive',
  storniert: 'destructive',
}

export default function RechnungenListePage(): JSX.Element {
  const { t } = useTranslation()
  const navigate = useNavigate()
  const { toast } = useToast()
  const entityType = 'invoice'
  const entityTypeLabel = getEntityTypeLabel(t, entityType, 'Rechnung')
  const pageTitle = getListTitle(t, entityTypeLabel)
  const [searchTerm, setSearchTerm] = useState('')
  const [statusFilter, setStatusFilter] = useState<RechnungStatus | 'alle'>('alle')
  const [showImport, setShowImport] = useState(false)
  const [filterValues, setFilterValues] = useState<Record<string, any>>({})

  const { data: rechnungen = [] } = useRechnungen()

  // Filter-Konfiguration für AdvancedFilters
  const filterConfig: FilterConfig[] = [
    {
      key: 'status',
      label: t('crud.fields.status'),
      type: 'select',
      options: [
        { value: 'offen', label: t('status.pending') },
        { value: 'teilbezahlt', label: t('status.partial') },
        { value: 'bezahlt', label: t('status.paid') },
        { value: 'ueberfaellig', label: t('status.overdue') },
        { value: 'storniert', label: t('status.cancelled') },
      ],
    },
    {
      key: 'datum',
      label: t('crud.fields.invoiceDate'),
      type: 'date',
    },
    {
      key: 'kunde',
      label: t('crud.entities.customer'),
      type: 'text',
    },
    {
      key: 'faelligAm',
      label: t('crud.fields.dueDate'),
      type: 'date',
    },
  ]

  const filteredRechnungen = rechnungen.filter((rechnung) => {
    const matchesSearch =
      rechnung.nummer.toLowerCase().includes(searchTerm.toLowerCase()) ||
      rechnung.kunde.toLowerCase().includes(searchTerm.toLowerCase()) ||
      rechnung.auftragsNr.toLowerCase().includes(searchTerm.toLowerCase())
    const matchesStatus = statusFilter === 'alle' || rechnung.status === statusFilter
    
    // Erweiterte Filter
    if (filterValues.status && rechnung.status !== filterValues.status) return false
    if (filterValues.kunde && !rechnung.kunde.toLowerCase().includes(filterValues.kunde.toLowerCase())) return false
    if (filterValues.datum) {
      const rechnungDate = new Date(rechnung.datum).toISOString().split('T')[0]
      if (rechnungDate !== filterValues.datum) return false
    }
    if (filterValues.faelligAm) {
      const faelligDate = new Date(rechnung.faelligAm).toISOString().split('T')[0]
      if (faelligDate !== filterValues.faelligAm) return false
    }
    
    return matchesSearch && matchesStatus
  })

  const exportData = filteredRechnungen.map(r => ({
    Rechnungsnummer: r.nummer,
    Datum: formatDateForExport(r.datum),
    Kunde: r.kunde,
    Auftragsnummer: r.auftragsNr,
    Betrag: formatCurrencyForExport(r.betrag),
    'Fällig am': formatDateForExport(r.faelligAm),
    Status: getStatusLabel(t, r.status, r.status),
  }))

  const { handleExport, handlePrint } = useListActions({
    data: exportData,
    entityName: 'rechnungen',
  })
  const overdueCount = filteredRechnungen.filter((rechnung) => rechnung.status === 'ueberfaellig').length
  const openCount = filteredRechnungen.filter((rechnung) => rechnung.status === 'offen' || rechnung.status === 'teilbezahlt').length
  const totalVolume = filteredRechnungen.reduce((sum, rechnung) => sum + rechnung.betrag, 0)
  const operationalStatus = normalizeOperationalStatus(
    overdueCount > 0 ? 'eskaliert' : openCount > 0 ? 'wartet_auf_mensch' : filteredRechnungen.length > 0 ? 'abgeschlossen' : 'offen'
  )
  const contextSections = [
    {
      title: 'Vorgang',
      items: [
        { label: 'Gefilterte Rechnungen', value: String(filteredRechnungen.length) },
        { label: 'Offen/Teilbezahlt', value: String(openCount) },
        { label: 'Ueberfaellig', value: String(overdueCount) },
      ],
    },
    {
      title: 'Wirtschaftslage',
      items: [
        { label: 'Volumen', value: new Intl.NumberFormat('de-DE', { style: 'currency', currency: 'EUR' }).format(totalVolume) },
        { label: 'Statusfilter', value: statusFilter === 'alle' ? 'Alle' : statusFilter },
        { label: 'Suchbegriff', value: searchTerm || 'Keine Einschraenkung' },
      ],
    },
    {
      title: 'Governance',
      items: [
        { label: 'Naechste Aktion', value: overdueCount > 0 ? 'Ueberfaellige Rechnungen klaeren' : openCount > 0 ? 'Offene Rechnungen drucken oder versenden' : 'Neue Rechnung anlegen oder Liste exportieren' },
        { label: 'Blocker', value: overdueCount > 0 ? 'Mindestens eine Rechnung ist ueberfaellig.' : 'Kein akuter Blocker' },
      ],
    },
  ]
  const timelineItems = [
    { label: 'Rechnungsliste geladen', detail: `${rechnungen.length} Rechnungen gesamt` },
    overdueCount > 0 ? { label: 'Ueberfaellige Forderungen erkannt', detail: `${overdueCount} Rechnung(en)` } : null,
    showImport ? { label: 'Importmodus aktiv', detail: 'CSV-Import fuer Faktura geoeffnet' } : null,
  ].filter((item): item is { label: string; detail: string } => item !== null)

  const handleImport = async (importData: any[]) => {
    try {
      for (const row of importData) {
        const doc = {
          number: row.Rechnungsnummer || row.number || `INV-${Date.now()}`,
          date: row.Datum || row.date || new Date().toISOString().split('T')[0],
          customerId: row.Kunde || row.customerId || '',
          sourceOrder: row.Auftragsnummer || row.sourceOrder || '',
          status: 'ENTWURF',
          dueDate: row['Fällig am'] || row.dueDate || '',
          lines: [],
          subtotalNet: 0,
          totalTax: 0,
          totalGross: parseFloat(row.Betrag?.replace(/[^\d,.-]/g, '').replace(',', '.')) || 0,
        }
        await saveDocument('sales_invoice', doc)
      }
      toast({
        title: t('crud.messages.importSuccess'),
        description: `${importData.length} Rechnungen wurden importiert.`,
      })
      window.location.reload()
    } catch (error) {
      toast({
        variant: 'destructive',
        title: t('crud.messages.importError'),
        description: getAxiosErrorMessage(error),
      })
    }
  }

  const columns = [
    {
      key: 'nummer' as const,
      label: t('crud.fields.invoiceNumber'),
      render: (rechnung: Rechnung) => (
        <button
          onClick={() => navigate(`/sales/invoice-editor?id=${rechnung.id}`)}
          className="font-medium text-blue-600 hover:underline"
        >
          {rechnung.nummer}
        </button>
      ),
    },
    {
      key: 'datum' as const,
      label: t('crud.fields.invoiceDate'),
      render: (rechnung: Rechnung) => new Date(rechnung.datum).toLocaleDateString('de-DE'),
    },
    {
      key: 'kunde' as const,
      label: t('crud.entities.customer'),
    },
    {
      key: 'auftragsNr' as const,
      label: t('crud.entities.salesOrder'),
      render: (rechnung: Rechnung) => (
        <button
          onClick={() => navigate(`/sales/order-editor?id=${rechnung.auftragsNr}`)}
          className="text-sm text-blue-600 hover:underline"
        >
          {rechnung.auftragsNr}
        </button>
      ),
    },
    {
      key: 'betrag' as const,
      label: t('crud.fields.total'),
      render: (rechnung: Rechnung) =>
        new Intl.NumberFormat('de-DE', { style: 'currency', currency: 'EUR' }).format(
          rechnung.betrag
        ),
    },
    {
      key: 'faelligAm' as const,
      label: t('crud.fields.paymentDue'),
      render: (rechnung: Rechnung) => new Date(rechnung.faelligAm).toLocaleDateString('de-DE'),
    },
    {
      key: 'status' as const,
      label: t('crud.fields.status'),
      render: (rechnung: Rechnung) => (
        <Badge variant={statusVariantMap[rechnung.status]}>{getStatusLabel(t, rechnung.status, rechnung.status)}</Badge>
      ),
    },
  ]

  return (
    <div className="space-y-4 p-6">
      <OperationalCaseHeader
        title={pageTitle}
        description="Faktura- und Forderungsraum fuer offene, ueberfaellige und bereits versandte Rechnungen."
        status={operationalStatus}
        owner="Vertriebsinnendienst"
        blocker={overdueCount > 0 ? 'Ueberfaellige Rechnungen muessen geklaert oder angemahnt werden.' : null}
        nextAction={overdueCount > 0 ? 'Ueberfaellige Rechnungen priorisieren' : openCount > 0 ? 'Offene Rechnungen drucken oder versenden' : 'Neue Rechnung anlegen'}
        caseLabel="Ausgangsrechnungen"
        tags={['Sales', 'FIBU']}
      />
      <div className="grid gap-4 xl:grid-cols-[1.3fr_0.7fr]">
        <OperationalTimeline title="Rechnungsverlauf" items={timelineItems} />
        <OperationalContextPanel sections={contextSections} />
      </div>
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-3xl font-bold">{pageTitle}</h1>
          <p className="text-muted-foreground">{t('crud.list.overview', { entityType: entityTypeLabel })}</p>
        </div>
        <Button onClick={() => navigate('/sales/invoice-editor')} className="gap-2">
          <Receipt className="h-4 w-4" />
          {t('crud.actions.new')} {entityTypeLabel}
        </Button>
      </div>

      <Card>
        <CardHeader>
          <CardTitle>{t('crud.actions.filter')} & {t('crud.actions.search')}</CardTitle>
        </CardHeader>
        <CardContent className="space-y-4">
          <div className="flex gap-4">
            <div className="relative flex-1">
              <Search className="absolute left-3 top-1/2 h-4 w-4 -translate-y-1/2 text-muted-foreground" />
              <Input
                placeholder={`${t('crud.actions.search')  }...`}
                value={searchTerm}
                onChange={(e) => setSearchTerm(e.target.value)}
                className="pl-10"
              />
            </div>
            <select
              value={statusFilter}
              onChange={(e) => setStatusFilter(e.target.value as Rechnung['status'] | 'alle')}
              className="rounded-md border border-input bg-background px-3 py-2"
            >
              <option value="alle">{t('crud.list.allStatus', { defaultValue: 'Alle Status' })}</option>
              <option value="offen">{t('status.pending')}</option>
              <option value="teilbezahlt">{t('status.partial')}</option>
              <option value="bezahlt">{t('status.paid')}</option>
              <option value="ueberfaellig">{t('status.overdue')}</option>
              <option value="storniert">{t('status.cancelled')}</option>
            </select>
            <AdvancedFilters
              filters={filterConfig}
              values={filterValues}
              onChange={setFilterValues}
              onReset={() => setFilterValues({})}
            />
            <Button variant="outline" className="gap-2" onClick={handleExport}>
              <FileDown className="h-4 w-4" />
              {t('crud.print.export')}
            </Button>
            <Button variant="outline" className="gap-2" onClick={handlePrint}>
              <FileText className="h-4 w-4" />
              {t('crud.actions.print')}
            </Button>
            <Button variant="outline" className="gap-2" onClick={() => setShowImport(!showImport)}>
              <FileText className="h-4 w-4" />
              {t('crud.actions.import')}
            </Button>
          </div>
        </CardContent>
      </Card>

      {showImport && (
        <Card>
          <CardContent className="pt-6">
            <CSVImport
              onImport={handleImport}
              expectedColumns={['Rechnungsnummer', 'Datum', 'Kunde', 'Auftragsnummer', 'Betrag', 'Fällig am', 'Status']}
              entityName="Rechnungen"
            />
          </CardContent>
        </Card>
      )}

      <Card>
        <CardContent className="pt-6">
          <DataTable data={filteredRechnungen} columns={columns} />
          <div className="mt-4 text-sm text-muted-foreground">
            {t('crud.list.showing', { count: filteredRechnungen.length, total: rechnungen.length, entityType: entityTypeLabel })}
          </div>
        </CardContent>
      </Card>
    </div>
  )
}
