import { useState } from 'react'
import { useNavigate } from '@/app/routing/typed-router'
import { useTranslation } from 'react-i18next'
import { Button } from '@/components/ui/button'
import { Input } from '@/components/ui/input'
import { Badge } from '@/components/ui/badge'
import { DataTable } from '@/components/ui/data-table'
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card'
import { FileDown, FileText, Plus, Search } from 'lucide-react'
import { getEntityTypeLabel, getListTitle, getStatusLabel } from '@/features/crud/utils/i18n-helpers'
import { AdvancedFilters, FilterConfig } from '@/components/list/AdvancedFilters'
import { CSVImport } from '@/components/list/CSVImport'
import { useToast } from '@/hooks/use-toast'
import { useListActions } from '@/hooks/useListActions'
import { formatDateForExport, formatCurrencyForExport } from '@/lib/export-utils'
import { saveDocument } from '@/lib/document-api'
import { getAxiosErrorMessage } from '@/lib/api-client'
import { stringValue } from '@/lib/record-utils'
import { useAuftraege, type Auftrag, type AuftragStatus } from '@/lib/api/sales'
import {
  CrudCapabilityChecklist,
  ManagementDecisionPanel,
  NextActionPanel,
  OperationalTaskPlan,
  RoleFocusBar,
  type UxTaskItem,
} from '@/components/workflow'

const statusVariantMap: Record<AuftragStatus, 'default' | 'outline' | 'secondary' | 'destructive'> = {
  open: 'default',
  offen: 'default',
  teilgeliefert: 'secondary',
  geliefert: 'outline',
  fakturiert: 'outline',
  storniert: 'destructive',
}

type SalesRoleFocus = 'all' | 'sales' | 'order-desk' | 'logistics' | 'finance' | 'management'

const salesRoleProfiles: Array<{ id: SalesRoleFocus; label: string; description: string }> = [
  {
    id: 'all',
    label: 'Alle Rollen',
    description: 'Zeigt die Auftragslage fuer Vertrieb, Auftragsabwicklung, Logistik, Finance und Leitung.',
  },
  {
    id: 'sales',
    label: 'Vertrieb',
    description: 'Fokus auf Kunde, Auftragswert und naechstes Follow-up.',
  },
  {
    id: 'order-desk',
    label: 'Auftragsabwicklung',
    description: 'Fokus auf offene Auftraege, Liefertermin und Bearbeitungsstatus.',
  },
  {
    id: 'logistics',
    label: 'Logistik',
    description: 'Fokus auf Lieferdruck, Teillieferungen und offene Auslieferung.',
  },
  {
    id: 'finance',
    label: 'Finance',
    description: 'Fokus auf fakturierte Auftraege, offene Faktura und Export.',
  },
  {
    id: 'management',
    label: 'Leitung',
    description: 'Fokus auf Rueckstand, Wert und operative Entscheidung.',
  },
]

export default function AuftraegeListePage(): JSX.Element {
  const { t } = useTranslation()
  const navigate = useNavigate()
  const { toast } = useToast()
  const entityType = 'salesOrder'
  const entityTypeLabel = getEntityTypeLabel(t, entityType, 'Verkaufsauftrag')
  const pageTitle = getListTitle(t, entityTypeLabel)
  const [searchTerm, setSearchTerm] = useState('')
  const [statusFilter, setStatusFilter] = useState<AuftragStatus | 'alle'>('alle')
  const [showImport, setShowImport] = useState(false)
  const [filterValues, setFilterValues] = useState<Record<string, unknown>>({})
  const [roleFocus, setRoleFocus] = useState<SalesRoleFocus>('all')

  const { data: auftraege = [] } = useAuftraege()

  // Filter-Konfiguration für AdvancedFilters
  const filterConfig: FilterConfig[] = [
    {
      key: 'status',
      label: t('crud.fields.status'),
      type: 'select',
      options: [
        { value: 'offen', label: t('status.pending') },
        { value: 'teilgeliefert', label: t('status.partiallyDelivered') },
        { value: 'geliefert', label: t('status.delivered') },
        { value: 'fakturiert', label: t('status.invoiced') },
        { value: 'storniert', label: t('status.cancelled') },
      ],
    },
    {
      key: 'datum',
      label: t('crud.fields.date'),
      type: 'date',
    },
    {
      key: 'kunde',
      label: t('crud.entities.customer'),
      type: 'text',
    },
    {
      key: 'liefertermin',
      label: t('crud.fields.deliveryDate'),
      type: 'date',
    },
  ]

  const filteredAuftraege = auftraege.filter((auftrag) => {
    const matchesSearch =
      stringValue(auftrag.nummer).toLowerCase().includes(searchTerm.toLowerCase()) ||
      stringValue(auftrag.kunde).toLowerCase().includes(searchTerm.toLowerCase())
    const matchesStatus = statusFilter === 'alle' || auftrag.status === statusFilter
    
    // Erweiterte Filter
    if (filterValues.status && auftrag.status !== filterValues.status) return false
    if (filterValues.kunde && !stringValue(auftrag.kunde).toLowerCase().includes(stringValue(filterValues.kunde).toLowerCase())) return false
    if (filterValues.datum) {
      const auftragDate = new Date(auftrag.datum).toISOString().split('T')[0]
      if (auftragDate !== filterValues.datum) return false
    }
    if (filterValues.liefertermin) {
      const lieferDate = new Date(auftrag.liefertermin).toISOString().split('T')[0]
      if (lieferDate !== filterValues.liefertermin) return false
    }
    
    return matchesSearch && matchesStatus
  })

  const exportData = filteredAuftraege.map(a => ({
    Auftragsnummer: a.nummer,
    Datum: formatDateForExport(a.datum),
    Kunde: a.kunde,
    Betrag: formatCurrencyForExport(a.betrag),
    Liefertermin: formatDateForExport(a.liefertermin),
    Status: getStatusLabel(t, a.status, a.status),
  }))

  const { handleExport, handlePrint } = useListActions({
    data: exportData,
    entityName: 'auftraege',
  })

  const total = filteredAuftraege.length
  const openCount = filteredAuftraege.filter((auftrag) => ['open', 'offen'].includes(String(auftrag.status))).length
  const partialCount = filteredAuftraege.filter((auftrag) => auftrag.status === 'teilgeliefert').length
  const deliveredCount = filteredAuftraege.filter((auftrag) => auftrag.status === 'geliefert').length
  const invoicedCount = filteredAuftraege.filter((auftrag) => auftrag.status === 'fakturiert').length
  const cancelledCount = filteredAuftraege.filter((auftrag) => auftrag.status === 'storniert').length
  const totalAmount = filteredAuftraege.reduce((sum, auftrag) => sum + Number(auftrag.betrag || 0), 0)
  const today = new Date().toISOString().split('T')[0]
  const overdueDeliveryCount = filteredAuftraege.filter((auftrag) =>
    auftrag.liefertermin && new Date(auftrag.liefertermin).toISOString().split('T')[0] < today && !['geliefert', 'fakturiert', 'storniert'].includes(String(auftrag.status)),
  ).length
  const nextOrderAction = overdueDeliveryCount > 0
    ? 'Ueberfaellige Liefertermine klaeren und Logistikfolge setzen.'
    : openCount > 0
      ? 'Offene Auftraege bestaetigen und Liefertermin sichern.'
      : partialCount > 0
        ? 'Teillieferungen nachhalten und Restlieferung planen.'
        : deliveredCount > 0
          ? 'Gelieferte Auftraege fakturieren.'
          : 'Neuen Auftrag anlegen oder Filter anpassen.'
  const orderTaskItems: UxTaskItem[] = [
    {
      label: 'Auftrag erfassen',
      done: total > 0,
      hint: total > 0 ? `${total} Auftraege in der aktuellen Sicht.` : 'Neuen Verkaufsauftrag anlegen oder Import starten.',
    },
    {
      label: 'Liefertermin klaeren',
      done: overdueDeliveryCount === 0 && total > 0,
      hint: overdueDeliveryCount > 0 ? `${overdueDeliveryCount} Auftraege sind ueberfaellig.` : 'Keine ueberfaelligen Liefertermine in der Sicht.',
    },
    {
      label: 'Liefern',
      done: partialCount + deliveredCount + invoicedCount > 0,
      hint: partialCount > 0 ? `${partialCount} Teillieferungen brauchen Nachlauf.` : `${openCount} offene Auftraege brauchen Lieferfolge.`,
    },
    {
      label: 'Fakturieren',
      done: invoicedCount > 0 && deliveredCount === 0,
      hint: deliveredCount > 0 ? `${deliveredCount} gelieferte Auftraege koennen fakturiert werden.` : 'Keine gelieferte, unfakturierte Position in der Sicht.',
    },
  ]
  const orderCrudCapabilities = [
    {
      key: 'create',
      label: 'Anlegen',
      available: true,
      hint: 'Neue Verkaufsauftraege koennen direkt aus der Liste angelegt werden.',
    },
    {
      key: 'read',
      label: 'Lesen',
      available: true,
      hint: 'Auftragsnummer, Kunde, Betrag, Liefertermin und Status sind sichtbar.',
    },
    {
      key: 'update',
      label: 'Bearbeiten',
      available: total > 0,
      hint: 'Auftraege koennen aus der Liste im Editor geoeffnet werden.',
    },
    {
      key: 'delete',
      label: 'Storno',
      available: cancelledCount > 0 || total > 0,
      hint: 'Storniert wird fachlich ueber den Auftragsstatus; direkte Loeschung ist kein Standardpfad.',
    },
    {
      key: 'approve',
      label: 'Liefer-/Faktura-Folge',
      available: openCount + partialCount + deliveredCount > 0,
      hint: 'Offene, teilgelieferte und gelieferte Auftraege zeigen den naechsten operativen Schritt.',
    },
    {
      key: 'export',
      label: 'Export/Import',
      available: true,
      hint: 'CSV-Export, Druck und CSV-Import sind an der Liste angebunden.',
    },
    {
      key: 'audit',
      label: 'Nachverfolgung',
      available: true,
      hint: 'Status, Liefertermin, Kunde und Betrag bilden die operative Nachfassspur.',
    },
  ]

  const handleImport = async (importData: Record<string, unknown>[]) => {
    try {
      for (const row of importData) {
        const doc = {
          number: row.Auftragsnummer || row.number || `SO-${Date.now()}`,
          date: row.Datum || row.date || new Date().toISOString().split('T')[0],
          customerId: row.Kunde || row.customerId || '',
          status: 'ENTWURF',
          deliveryDate: row.Liefertermin || row.deliveryDate || '',
          lines: [],
          subtotalNet: 0,
          totalTax: 0,
          totalGross: parseFloat(stringValue(row.Betrag).replace(/[^\d,.-]/g, '').replace(',', '.')) || 0,
        }
        await saveDocument('sales_order', doc)
      }
      toast({
        title: t('crud.messages.importSuccess'),
        description: `${importData.length} Aufträge wurden importiert.`,
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
      label: t('crud.fields.number'),
      render: (auftrag: Auftrag) => (
        <button
          onClick={() => navigate(`/sales/order-editor?id=${auftrag.id}`)}
          className="font-medium text-blue-600 hover:underline"
        >
          {auftrag.nummer}
        </button>
      ),
    },
    {
      key: 'datum' as const,
      label: t('crud.fields.date'),
      render: (auftrag: Auftrag) => new Date(auftrag.datum).toLocaleDateString('de-DE'),
    },
    {
      key: 'kunde' as const,
      label: t('crud.entities.customer'),
    },
    {
      key: 'betrag' as const,
      label: t('crud.fields.total'),
      render: (auftrag: Auftrag) =>
        new Intl.NumberFormat('de-DE', { style: 'currency', currency: 'EUR' }).format(auftrag.betrag),
    },
    {
      key: 'liefertermin' as const,
      label: t('crud.fields.deliveryDate'),
      render: (auftrag: Auftrag) => new Date(auftrag.liefertermin).toLocaleDateString('de-DE'),
    },
    {
      key: 'status' as const,
      label: t('crud.fields.status'),
      render: (auftrag: Auftrag) => (
        <Badge variant={statusVariantMap[auftrag.status]}>{getStatusLabel(t, auftrag.status, auftrag.status)}</Badge>
      ),
    },
  ]

  return (
    <div className="space-y-4 p-6">
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-3xl font-bold">{pageTitle}</h1>
          <p className="text-muted-foreground">{t('crud.list.overview', { entityType: entityTypeLabel })}</p>
        </div>
        <Button onClick={() => navigate('/sales/order-editor')} className="gap-2">
          <Plus className="h-4 w-4" />
          {t('crud.actions.new')} {entityTypeLabel}
        </Button>
      </div>
      <RoleFocusBar
        roles={salesRoleProfiles}
        value={roleFocus}
        onChange={setRoleFocus}
        visibleCount={roleFocus === 'all' ? 5 : 1}
        totalCount={5}
      />
      <ManagementDecisionPanel
        decision={{
          allowed: total > 0,
          allowedLabel: 'Auftragsarbeit moeglich',
          blockedLabel: 'Keine Auftraege',
          summary: total > 0
            ? `Die aktuelle Sicht enthaelt ${total} Auftraege mit ${new Intl.NumberFormat('de-DE', { style: 'currency', currency: 'EUR' }).format(totalAmount)} Auftragswert. ${nextOrderAction}`
            : 'In der aktuellen Sicht gibt es keine Verkaufsauftraege. Legen Sie einen neuen Auftrag an, importieren Sie Daten oder passen Sie Filter an.',
          blockerCount: total === 0 ? 1 : overdueDeliveryCount,
          nextFocus: nextOrderAction,
          template: {
            label: 'Verkaufsauftrag anlegen',
            href: '/sales/order-editor',
          },
        }}
      />
      <div className="grid gap-4 lg:grid-cols-[1.35fr_1fr]">
        <OperationalTaskPlan title="Auftrag-Follow-up-Plan" items={orderTaskItems} />
        <NextActionPanel
          action={nextOrderAction}
          tone={overdueDeliveryCount > 0 ? 'red' : openCount + partialCount + deliveredCount > 0 ? 'amber' : total > 0 ? 'blue' : 'red'}
        />
      </div>
      <CrudCapabilityChecklist capabilities={orderCrudCapabilities} />

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
              onChange={(e) => setStatusFilter(e.target.value as Auftrag['status'] | 'alle')}
              className="rounded-md border border-input bg-background px-3 py-2"
            >
              <option value="alle">{t('crud.list.allStatus', { defaultValue: 'Alle Status' })}</option>
              <option value="offen">{t('status.pending')}</option>
              <option value="teilgeliefert">{t('status.partiallyDelivered')}</option>
              <option value="geliefert">{t('status.delivered')}</option>
              <option value="fakturiert">{t('status.invoiced')}</option>
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
              expectedColumns={['Auftragsnummer', 'Datum', 'Kunde', 'Betrag', 'Liefertermin', 'Status']}
              entityName="Aufträge"
            />
          </CardContent>
        </Card>
      )}

      <Card>
        <CardContent className="pt-6">
          <DataTable data={filteredAuftraege} columns={columns} />
          <div className="mt-4 text-sm text-muted-foreground">
            {t('crud.list.showing', { count: filteredAuftraege.length, total: auftraege.length, entityType: entityTypeLabel })}
          </div>
        </CardContent>
      </Card>
    </div>
  )
}
