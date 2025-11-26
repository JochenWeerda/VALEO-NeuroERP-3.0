import { useState, useEffect } from 'react'
import { useTranslation } from 'react-i18next'
import { useNavigate } from 'react-router-dom'
import { Button } from '@/components/ui/button'
import { Input } from '@/components/ui/input'
import { Badge } from '@/components/ui/badge'
import { DataTable } from '@/components/ui/data-table'
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card'
import { FileDown, FileText, Plus, Search } from 'lucide-react'
import { useListActions } from '@/hooks/useListActions'
import { formatDateForExport, formatCurrencyForExport } from '@/lib/export-utils'
import { getEntityTypeLabel, getListTitle, getStatusLabel } from '@/features/crud/utils/i18n-helpers'
import { AdvancedFilters, FilterConfig } from '@/components/list/AdvancedFilters'
import { CSVImport } from '@/components/list/CSVImport'
import { useToast } from '@/hooks/use-toast'
import { saveDocument } from '@/lib/document-api'

type Angebot = {
  id: string
  nummer: string
  datum: string
  kunde: string
  betrag: number
  status: 'offen' | 'angenommen' | 'abgelehnt' | 'abgelaufen'
  gueltigBis: string
}

const mockAngebote: Angebot[] = [
  {
    id: '1',
    nummer: 'ANG-2025-001',
    datum: '2025-10-08',
    kunde: 'Landhandel Nord GmbH',
    betrag: 12500.0,
    status: 'offen',
    gueltigBis: '2025-11-07',
  },
  {
    id: '2',
    nummer: 'ANG-2025-002',
    datum: '2025-10-09',
    kunde: 'Agrar-Zentrum Süd',
    betrag: 8750.5,
    status: 'angenommen',
    gueltigBis: '2025-11-08',
  },
  {
    id: '3',
    nummer: 'ANG-2025-003',
    datum: '2025-10-10',
    kunde: 'Müller Landwirtschaft',
    betrag: 5200.0,
    status: 'offen',
    gueltigBis: '2025-11-09',
  },
]

const statusVariantMap: Record<Angebot['status'], 'default' | 'outline' | 'secondary' | 'destructive'> = {
  offen: 'default',
  angenommen: 'outline',
  abgelehnt: 'destructive',
  abgelaufen: 'secondary',
}

export default function AngeboteListePage(): JSX.Element {
  const { t } = useTranslation()
  const navigate = useNavigate()
  const { toast } = useToast()
  const [searchTerm, setSearchTerm] = useState('')
  const [statusFilter, setStatusFilter] = useState<Angebot['status'] | 'alle'>('alle')
  const [angebote, setAngebote] = useState<Angebot[]>([])
  const [loading, setLoading] = useState(true)
  const [showImport, setShowImport] = useState(false)
  const [filterValues, setFilterValues] = useState<Record<string, any>>({})

  const entityType = 'offer'
  const entityTypeLabel = getEntityTypeLabel(t, entityType, 'Angebot')


  // Lade Daten von API
  useEffect(() => {
    const loadData = async () => {
      setLoading(true)
      try {
        const response = await fetch('/api/mcp/documents/sales_offer?skip=0&limit=100')
        if (response.ok) {
          const result = await response.json()
          if (result.ok && result.data) {
            // Transformiere API-Daten in lokales Format
            const transformed = result.data.map((doc: any) => ({
              id: doc.number,
              nummer: doc.number,
              datum: doc.date,
              kunde: doc.customerId || '',
              betrag: doc.totalGross || 0,
              status: (doc.status?.toLowerCase() || 'offen') as Angebot['status'],
              gueltigBis: doc.validUntil || '',
            }))
            setAngebote(transformed.length > 0 ? transformed : mockAngebote)
          } else {
            setAngebote(mockAngebote)
          }
        } else {
          setAngebote(mockAngebote)
        }
      } catch (error) {
        console.error('Fehler beim Laden der Angebote:', error)
        setAngebote(mockAngebote)
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
        { value: 'offen', label: getStatusLabel(t, 'offen', 'Offen') },
        { value: 'angenommen', label: getStatusLabel(t, 'angenommen', 'Angenommen') },
        { value: 'abgelehnt', label: getStatusLabel(t, 'abgelehnt', 'Abgelehnt') },
        { value: 'abgelaufen', label: getStatusLabel(t, 'abgelaufen', 'Abgelaufen') },
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
  ]

  const filteredAngebote = angebote.filter((angebot) => {
    const matchesSearch =
      angebot.nummer.toLowerCase().includes(searchTerm.toLowerCase()) ||
      angebot.kunde.toLowerCase().includes(searchTerm.toLowerCase())
    const matchesStatus = statusFilter === 'alle' || angebot.status === statusFilter
    
    // Erweiterte Filter
    if (filterValues.status && angebot.status !== filterValues.status) return false
    if (filterValues.kunde && !angebot.kunde.toLowerCase().includes(filterValues.kunde.toLowerCase())) return false
    if (filterValues.datum) {
      const angebotDate = new Date(angebot.datum).toISOString().split('T')[0]
      if (angebotDate !== filterValues.datum) return false
    }
    
    return matchesSearch && matchesStatus
  })

  const handleImport = async (importData: any[]) => {
    try {
      for (const row of importData) {
        // Transformiere CSV-Daten in Dokument-Format
        const doc = {
          number: row.Angebotsnummer || row.number || `ANG-${Date.now()}`,
          date: row.Datum || row.date || new Date().toISOString().split('T')[0],
          customerId: row.Kunde || row.customerId || '',
          status: 'ENTWURF',
          validUntil: row['Gültig bis'] || row.validUntil || '',
          lines: [],
          subtotalNet: 0,
          totalTax: 0,
          totalGross: parseFloat(row.Betrag?.replace(/[^\d,.-]/g, '').replace(',', '.')) || 0,
        }
        await saveDocument('sales_offer', doc)
      }
      toast({
        title: t('crud.messages.importSuccess'),
        description: `${importData.length} Angebote wurden importiert.`,
      })
      // Daten neu laden
      window.location.reload()
    } catch (error) {
      toast({
        variant: 'destructive',
        title: t('crud.messages.importError'),
        description: error instanceof Error ? error.message : 'Unbekannter Fehler',
      })
    }
  }

  const exportData = filteredAngebote.map(a => ({
    Angebotsnummer: a.nummer,
    Datum: formatDateForExport(a.datum),
    Kunde: a.kunde,
    Betrag: formatCurrencyForExport(a.betrag),
    'Gültig bis': formatDateForExport(a.gueltigBis),
    Status: getStatusLabel(t, a.status, a.status),
  }))

  const { handleExport, handlePrint } = useListActions({
    data: exportData,
    entityName: 'angebote',
  })

  const columns = [
    {
      key: 'nummer' as const,
      label: t('crud.fields.number'),
      render: (angebot: Angebot) => (
        <button
          onClick={() => navigate(`/sales/angebot/${angebot.id}`)}
          className="font-medium text-blue-600 hover:underline"
        >
          {angebot.nummer}
        </button>
      ),
    },
    {
      key: 'datum' as const,
      label: t('crud.fields.date'),
      render: (angebot: Angebot) => new Date(angebot.datum).toLocaleDateString('de-DE'),
    },
    {
      key: 'kunde' as const,
      label: t('crud.entities.customer'),
    },
    {
      key: 'betrag' as const,
      label: t('crud.fields.total'),
      render: (angebot: Angebot) =>
        new Intl.NumberFormat('de-DE', { style: 'currency', currency: 'EUR' }).format(angebot.betrag),
    },
    {
      key: 'gueltigBis' as const,
      label: t('crud.fields.validUntil'),
      render: (angebot: Angebot) => new Date(angebot.gueltigBis).toLocaleDateString('de-DE'),
    },
    {
      key: 'status' as const,
      label: t('crud.fields.status'),
      render: (angebot: Angebot) => (
        <Badge variant={statusVariantMap[angebot.status]}>{getStatusLabel(t, angebot.status, angebot.status)}</Badge>
      ),
    },
  ]

  return (
    <div className="space-y-4 p-6">
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-3xl font-bold">{getListTitle(t, entityTypeLabel)}</h1>
          <p className="text-muted-foreground">{t('crud.list.overview', { entityType: entityTypeLabel })}</p>
        </div>
        <Button onClick={() => navigate('/sales/angebot/neu')} className="gap-2">
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
              onChange={(e) => setStatusFilter(e.target.value as Angebot['status'] | 'alle')}
              className="rounded-md border border-input bg-background px-3 py-2"
            >
              <option value="alle">{t('crud.list.allStatus', { defaultValue: 'Alle Status' })}</option>
              <option value="offen">{getStatusLabel(t, 'offen', 'Offen')}</option>
              <option value="angenommen">{getStatusLabel(t, 'angenommen', 'Angenommen')}</option>
              <option value="abgelehnt">{getStatusLabel(t, 'abgelehnt', 'Abgelehnt')}</option>
              <option value="abgelaufen">{getStatusLabel(t, 'abgelaufen', 'Abgelaufen')}</option>
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
              expectedColumns={['Angebotsnummer', 'Datum', 'Kunde', 'Betrag', 'Gültig bis', 'Status']}
              entityName="Angebote"
            />
          </CardContent>
        </Card>
      )}

      <Card>
        <CardContent className="pt-6">
          <DataTable data={filteredAngebote} columns={columns} />
          <div className="mt-4 text-sm text-muted-foreground">
            {t('crud.list.showing', { count: filteredAngebote.length, total: mockAngebote.length, entityType: entityTypeLabel })}
          </div>
        </CardContent>
      </Card>
    </div>
  )
}
