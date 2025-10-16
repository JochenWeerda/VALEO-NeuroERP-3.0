import { useState, useEffect } from 'react'
import { useNavigate } from 'react-router-dom'
import { ListReport } from '@/components/mask-builder'
import { useMaskActions } from '@/components/mask-builder/hooks'
import { createApiClient } from '@/components/mask-builder/utils/api'
import { formatDate, formatNumber } from '@/components/mask-builder/utils/formatting'
import { Badge } from '@/components/ui/badge'
import { ListConfig } from '@/components/mask-builder/types'

// API Client für Rechnungseingänge
const apiClient = createApiClient('/api/einkauf')

// Konfiguration für Rechnungseingänge ListReport
const rechnungseingaengeConfig: ListConfig = {
  title: 'Rechnungseingänge',
  subtitle: 'Eingehende Lieferantenrechnungen verwalten',
  type: 'list-report',
  columns: [
    {
      key: 'rechnungsNummer',
      label: 'Rechnungs-Nr.',
      sortable: true,
      render: (value) => <code className="text-sm font-mono">{value}</code>
    },
    {
      key: 'lieferant',
      label: 'Lieferant',
      sortable: true,
      filterable: true
    },
    {
      key: 'bestellung',
      label: 'Bestellung',
      sortable: true,
      render: (value) => value?.nummer || '-'
    },
    {
      key: 'wareneingang',
      label: 'Wareneingang',
      sortable: true,
      render: (value) => value?.nummer || '-'
    },
    {
      key: 'status',
      label: 'Status',
      sortable: true,
      filterable: true,
      render: (value) => {
        const statusLabels = {
          'ERFASST': { label: 'Erfasst', variant: 'secondary' as const },
          'GEPRUEFT': { label: 'Geprüft', variant: 'default' as const },
          'FREIGEGEBEN': { label: 'Freigegeben', variant: 'outline' as const },
          'VERBUCHT': { label: 'Verbucht', variant: 'outline' as const },
          'BEZAHLT': { label: 'Bezahlt', variant: 'outline' as const }
        }
        const status = statusLabels[value as keyof typeof statusLabels] || { label: value, variant: 'secondary' as const }
        return <Badge variant={status.variant}>{status.label}</Badge>
      }
    },
    {
      key: 'bruttoBetrag',
      label: 'Brutto (€)',
      sortable: true,
      render: (value) => `${formatNumber(value, 2)} €`
    },
    {
      key: 'rechnungsDatum',
      label: 'Rechnungsdatum',
      sortable: true,
      render: (value) => formatDate(value)
    },
    {
      key: 'createdAt',
      label: 'Erstellt',
      sortable: true,
      render: (value) => formatDate(value)
    }
  ],
  filters: [
    {
      name: 'status',
      label: 'Status',
      type: 'select',
      options: [
        { value: 'ERFASST', label: 'Erfasst' },
        { value: 'GEPRUEFT', label: 'Geprüft' },
        { value: 'FREIGEGEBEN', label: 'Freigegeben' },
        { value: 'VERBUCHT', label: 'Verbucht' },
        { value: 'BEZAHLT', label: 'Bezahlt' }
      ]
    },
    {
      name: 'lieferant',
      label: 'Lieferant',
      type: 'text'
    }
  ],
  bulkActions: [
    {
      key: 'pruefen',
      label: 'Prüfen',
      type: 'secondary',
      onClick: () => console.log('Prüfen clicked')
    },
    {
      key: 'freigeben',
      label: 'Freigeben',
      type: 'primary',
      onClick: () => console.log('Freigeben clicked')
    },
    {
      key: 'verbuchen',
      label: 'Verbuchen',
      type: 'primary',
      onClick: () => console.log('Verbuchen clicked')
    }
  ],
  defaultSort: { field: 'createdAt', direction: 'desc' },
  pageSize: 25,
  api: {
    baseUrl: '/api/einkauf/rechnungseingaenge',
    endpoints: {
      list: '/api/einkauf/rechnungseingaenge',
      get: '/api/einkauf/rechnungseingaenge/{id}',
      create: '/api/einkauf/rechnungseingaenge',
      update: '/api/einkauf/rechnungseingaenge/{id}',
      delete: '/api/einkauf/rechnungseingaenge/{id}'
    }
  },
  permissions: ['einkauf.read', 'einkauf.write', 'finance.read'],
  actions: []
}

export default function RechnungseingaengeListePage(): JSX.Element {
  const navigate = useNavigate()
  const [data, setData] = useState<any[]>([])
  const [total, setTotal] = useState(0)
  const [loading, setLoading] = useState(true)

  const { handleAction } = useMaskActions(async (action: string, item: any) => {
    if (action === 'edit' && item) {
      navigate(`/einkauf/rechnungseingaenge/${item.id}`)
    } else if (action === 'delete' && item) {
      if (confirm(`Rechnung "${item.rechnungsNummer}" wirklich löschen?`)) {
        try {
          await apiClient.delete(`/rechnungseingaenge/${item.id}`)
          loadData() // Liste neu laden
        } catch (error) {
          alert('Fehler beim Löschen')
        }
      }
    }
  })

  const loadData = async () => {
    setLoading(true)
    try {
      const response = await apiClient.get('/rechnungseingaenge')
      if (response.success) {
        setData((response.data as any).data || [])
        setTotal((response.data as any).total || 0)
      }
    } catch (error) {
      console.error('Fehler beim Laden der Daten:', error)
    } finally {
      setLoading(false)
    }
  }

  useEffect(() => {
    loadData()
  }, [])

  const handleCreate = () => {
    navigate('/einkauf/rechnungseingang/neu')
  }

  const handleEdit = (item: any) => {
    handleAction('edit', item)
  }

  const handleDelete = (item: any) => {
    handleAction('delete', item)
  }

  const handleExport = () => {
    alert('Export-Funktion wird implementiert')
  }

  return (
    <ListReport
      config={rechnungseingaengeConfig}
      data={data}
      total={total}
      onCreate={handleCreate}
      onEdit={handleEdit}
      onDelete={handleDelete}
      onExport={handleExport}
      onImport={() => alert('Import-Funktion wird implementiert')}
      isLoading={loading}
    />
  )
}