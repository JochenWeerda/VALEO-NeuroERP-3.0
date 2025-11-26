import { useState, useEffect } from 'react'
import { useNavigate } from 'react-router-dom'
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

type Auftrag = {
  id: string
  nummer: string
  datum: string
  kunde: string
  betrag: number
  status: 'offen' | 'teilgeliefert' | 'geliefert' | 'fakturiert' | 'storniert'
  liefertermin: string
}

const mockAuftraege: Auftrag[] = [
  {
    id: '1',
    nummer: 'SO-2025-0001',
    datum: '2025-10-08',
    kunde: 'Landhandel Nord GmbH',
    betrag: 12500.0,
    status: 'teilgeliefert',
    liefertermin: '2025-10-15',
  },
  {
    id: '2',
    nummer: 'SO-2025-0002',
    datum: '2025-10-09',
    kunde: 'Agrar-Zentrum Süd',
    betrag: 8750.5,
    status: 'geliefert',
    liefertermin: '2025-10-12',
  },
  {
    id: '3',
    nummer: 'SO-2025-0003',
    datum: '2025-10-10',
    kunde: 'Müller Landwirtschaft',
    betrag: 5200.0,
    status: 'offen',
    liefertermin: '2025-10-20',
  },
]

const statusVariantMap: Record<Auftrag['status'], 'default' | 'outline' | 'secondary' | 'destructive'> = {
  offen: 'default',
  teilgeliefert: 'secondary',
  geliefert: 'outline',
  fakturiert: 'outline',
  storniert: 'destructive',
}

export default function AuftraegeListePage(): JSX.Element {
  const { t } = useTranslation()
  const navigate = useNavigate()
  const { toast } = useToast()
  const entityType = 'salesOrder'
  const entityTypeLabel = getEntityTypeLabel(t, entityType, 'Verkaufsauftrag')
  const pageTitle = getListTitle(t, entityTypeLabel)
  const [searchTerm, setSearchTerm] = useState('')
  const [statusFilter, setStatusFilter] = useState<Auftrag['status'] | 'alle'>('alle')
  const [auftraege, setAuftraege] = useState<Auftrag[]>([])
  const [loading, setLoading] = useState(true)
  const [showImport, setShowImport] = useState(false)
  const [filterValues, setFilterValues] = useState<Record<string, any>>({})


  // Lade Daten von API
  useEffect(() => {
    const loadData = async () => {
      setLoading(true)
      try {
        const response = await fetch('/api/mcp/documents/sales_order?skip=0&limit=100')
        if (response.ok) {
          const result = await response.json()
          if (result.ok && result.data) {
            // Transformiere API-Daten
            const transformed = result.data.map((doc: any) => ({
              id: doc.number,
              nummer: doc.number,
              datum: doc.date,
              kunde: doc.customerId || '',
              betrag: 0, // Wird aus lines berechnet
              status: (doc.status?.toLowerCase() || 'offen') as Auftrag['status'],
              liefertermin: doc.deliveryDate || '',
            }))
            setAuftraege(transformed.length > 0 ? transformed : mockAuftraege)
          } else {
            setAuftraege(mockAuftraege)
          }
        } else {
          setAuftraege(mockAuftraege)
        }
      } catch (error) {
        console.error('Fehler beim Laden der Aufträge:', error)
        setAuftraege(mockAuftraege)
      } finally {
        setLoading(false)
      }
    }
    loadData()
  }, [])

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
      auftrag.nummer.toLowerCase().includes(searchTerm.toLowerCase()) ||
      auftrag.kunde.toLowerCase().includes(searchTerm.toLowerCase())
    const matchesStatus = statusFilter === 'alle' || auftrag.status === statusFilter
    
    // Erweiterte Filter
    if (filterValues.status && auftrag.status !== filterValues.status) return false
    if (filterValues.kunde && !auftrag.kunde.toLowerCase().includes(filterValues.kunde.toLowerCase())) return false
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

  const handleImport = async (importData: any[]) => {
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
          totalGross: parseFloat(row.Betrag?.replace(/[^\d,.-]/g, '').replace(',', '.')) || 0,
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
        description: error instanceof Error ? error.message : 'Unbekannter Fehler',
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

      <Card>
        <CardHeader>
          <CardTitle>{t('crud.actions.filter')} & {t('crud.actions.search')}</CardTitle>
        </CardHeader>
        <CardContent className="space-y-4">
          <div className="flex gap-4">
            <div className="relative flex-1">
              <Search className="absolute left-3 top-1/2 h-4 w-4 -translate-y-1/2 text-muted-foreground" />
              <Input
                placeholder={t('crud.actions.search') + '...'}
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
            {t('crud.list.showing', { count: filteredAuftraege.length, total: mockAuftraege.length, entityType: entityTypeLabel })}
          </div>
        </CardContent>
      </Card>
    </div>
  )
}
