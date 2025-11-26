import { useState, useEffect } from 'react'
import { useNavigate } from 'react-router-dom'
import { useTranslation } from 'react-i18next'
import { ListReport } from '@/components/mask-builder'
import { useMaskActions } from '@/components/mask-builder/hooks'
import { createApiClient } from '@/components/mask-builder/utils/api'
import { formatDate } from '@/components/mask-builder/utils/formatting'
import { Badge } from '@/components/ui/badge'
import { ListConfig } from '@/components/mask-builder/types'
import { getStatusLabel } from '@/features/crud/utils/i18n-helpers'

// API Client für Anlieferavis
const apiClient = createApiClient('/api/einkauf')

// Konfiguration für Anlieferavis ListReport
const createAnlieferavisConfig = (t: any): ListConfig => ({
  title: 'Anlieferavis',
  subtitle: 'Lieferavise für Wareneingangsvorbereitung',
  type: 'list-report',
  columns: [
    {
      key: 'avisNummer',
      label: 'Avis-Nr.',
      sortable: true,
      render: (value) => <code className="text-sm font-mono">{value}</code>
    },
    {
      key: 'bestellung',
      label: 'Bestellung',
      sortable: true,
      render: (value) => value?.nummer || '-'
    },
    {
      key: 'lieferant',
      label: 'Lieferant',
      sortable: true,
      filterable: true
    },
    {
      key: 'status',
      label: 'Status',
      sortable: true,
      filterable: true,
      render: (value) => {
        const statusLabel = getStatusLabel(t, (value as string).toLowerCase(), value as string)
        const variants: Record<string, 'secondary' | 'default' | 'outline' | 'destructive'> = {
          'GESENDET': 'secondary',
          'BESTAETIGT': 'outline',
          'STORNIERT': 'destructive'
        }
        return <Badge variant={variants[value as string] || 'secondary'}>{statusLabel}</Badge>
      }
    },
    {
      key: 'geplantesAnlieferDatum',
      label: 'Geplantes Datum',
      sortable: true,
      render: (value) => formatDate(value)
    },
    {
      key: 'fahrzeug',
      label: 'Fahrzeug',
      render: (value) => value?.kennzeichen || '-'
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
        { value: 'GESENDET', label: 'Gesendet' },
        { value: 'BESTAETIGT', label: 'Bestätigt' },
        { value: 'STORNIERT', label: 'Storniert' }
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
      key: 'senden',
      label: 'Senden',
      type: 'primary',
      onClick: () => console.log('Senden clicked')
    },
    {
      key: 'bestaetigen',
      label: 'Bestätigen',
      type: 'secondary',
      onClick: () => console.log('Bestätigen clicked')
    },
    {
      key: 'stornieren',
      label: 'Stornieren',
      type: 'danger',
      onClick: () => console.log('Stornieren clicked')
    }
  ],
  defaultSort: { field: 'createdAt', direction: 'desc' },
  pageSize: 25,
  api: {
    baseUrl: '/api/einkauf/anlieferavis',
    endpoints: {
      list: '/api/einkauf/anlieferavis',
      get: '/api/einkauf/anlieferavis/{id}',
      create: '/api/einkauf/anlieferavis',
      update: '/api/einkauf/anlieferavis/{id}',
      delete: '/api/einkauf/anlieferavis/{id}'
    }
  },
  permissions: ['einkauf.read', 'einkauf.write', 'warehouse.read'],
  actions: []
})

export default function AnlieferavisListePage(): JSX.Element {
  const { t } = useTranslation()
  const navigate = useNavigate()
  const anlieferavisConfig = createAnlieferavisConfig(t)
  const [data, setData] = useState<any[]>([])
  const [total, setTotal] = useState(0)
  const [loading, setLoading] = useState(true)

  const { handleAction } = useMaskActions(async (action: string, item: any) => {
    if (action === 'edit' && item) {
      navigate(`/einkauf/anlieferavis/${item.id}`)
    } else if (action === 'delete' && item) {
      if (confirm(`Anlieferavis "${item.avisNummer}" wirklich löschen?`)) {
        try {
          await apiClient.delete(`/anlieferavis/${item.id}`)
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
      const response = await apiClient.get('/anlieferavis')
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
    navigate('/einkauf/anlieferavis/neu')
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
      config={anlieferavisConfig}
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