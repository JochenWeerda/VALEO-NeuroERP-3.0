import { useState, useEffect } from 'react'
import { useNavigate } from 'react-router-dom'
import { ListReport } from '@/components/mask-builder'
import { useMaskActions } from '@/components/mask-builder/hooks'
import { createApiClient } from '@/components/mask-builder/utils/api'
import { formatDate, formatNumber } from '@/components/mask-builder/utils/formatting'
import { Badge } from '@/components/ui/badge'
import { ListConfig } from '@/components/mask-builder/types'

// API Client für Angebote
const apiClient = createApiClient('/api/einkauf')

// Konfiguration für Angebote ListReport
const angeboteConfig: ListConfig = {
  title: 'Lieferantenangebote',
  subtitle: 'Eingehende Preisangebote verwalten',
  type: 'list-report',
  columns: [
    {
      key: 'angebotNummer',
      label: 'Angebot-Nr.',
      sortable: true,
      render: (value) => <code className="text-sm font-mono">{value}</code>
    },
    {
      key: 'anfrage',
      label: 'Anfrage',
      sortable: true,
      render: (value) => value?.anfrageNummer || '-'
    },
    {
      key: 'lieferant',
      label: 'Lieferant',
      sortable: true,
      filterable: true
    },
    {
      key: 'artikel',
      label: 'Artikel',
      sortable: true,
      filterable: true
    },
    {
      key: 'preis',
      label: 'Preis',
      sortable: true,
      render: (value, item) => `${formatNumber(value, 2)} €/${item.einheit || 'Stk'}`
    },
    {
      key: 'gueltigBis',
      label: 'Gültig bis',
      sortable: true,
      render: (value) => formatDate(value)
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
          'GENEHMIGT': { label: 'Genehmigt', variant: 'outline' as const },
          'ABGELEHNT': { label: 'Abgelehnt', variant: 'destructive' as const }
        }
        const status = statusLabels[value as keyof typeof statusLabels] || { label: value, variant: 'secondary' as const }
        return <Badge variant={status.variant}>{status.label}</Badge>
      }
    },
    {
      key: 'lieferzeit',
      label: 'Lieferzeit',
      sortable: true,
      render: (value) => `${value} Tage`
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
        { value: 'GENEHMIGT', label: 'Genehmigt' },
        { value: 'ABGELEHNT', label: 'Abgelehnt' }
      ]
    },
    {
      name: 'lieferant',
      label: 'Lieferant',
      type: 'text'
    },
    {
      name: 'artikel',
      label: 'Artikel',
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
      key: 'genehmigen',
      label: 'Genehmigen',
      type: 'primary',
      onClick: () => console.log('Genehmigen clicked')
    },
    {
      key: 'ablehnen',
      label: 'Ablehnen',
      type: 'danger',
      onClick: () => console.log('Ablehnen clicked')
    },
    {
      key: 'inBestellung',
      label: 'In Bestellung umwandeln',
      type: 'secondary',
      onClick: () => console.log('In Bestellung clicked')
    }
  ],
  defaultSort: { field: 'createdAt', direction: 'desc' },
  pageSize: 25,
  api: {
    baseUrl: '/api/einkauf/angebote',
    endpoints: {
      list: '/api/einkauf/angebote',
      get: '/api/einkauf/angebote/{id}',
      create: '/api/einkauf/angebote',
      update: '/api/einkauf/angebote/{id}',
      delete: '/api/einkauf/angebote/{id}'
    }
  },
  permissions: ['einkauf.read', 'einkauf.write'],
  actions: []
}

export default function AngeboteListePage(): JSX.Element {
  const navigate = useNavigate()
  const [data, setData] = useState<any[]>([])
  const [total, setTotal] = useState(0)
  const [loading, setLoading] = useState(true)

  const { handleAction } = useMaskActions(async (action: string, item: any) => {
    if (action === 'edit' && item) {
      navigate(`/einkauf/angebote/${item.id}`)
    } else if (action === 'delete' && item) {
      if (confirm(`Angebot "${item.angebotNummer}" wirklich löschen?`)) {
        try {
          await apiClient.delete(`/angebote/${item.id}`)
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
      const response = await apiClient.get('/angebote')
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
    navigate('/einkauf/angebot/neu')
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
      config={angeboteConfig}
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