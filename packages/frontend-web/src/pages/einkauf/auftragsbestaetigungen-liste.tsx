import { useState, useEffect } from 'react'
import { useNavigate } from 'react-router-dom'
import { ListReport } from '@/components/mask-builder'
import { useMaskActions } from '@/components/mask-builder/hooks'
import { createApiClient } from '@/components/mask-builder/utils/api'
import { formatDate } from '@/components/mask-builder/utils/formatting'
import { Badge } from '@/components/ui/badge'
import { ListConfig } from '@/components/mask-builder/types'

// API Client für Auftragsbestätigungen
const apiClient = createApiClient('/api/einkauf')

// Konfiguration für Auftragsbestätigungen ListReport
const auftragsbestaetigungenConfig: ListConfig = {
  title: 'Auftragsbestätigungen',
  subtitle: 'Lieferanten-Rückmeldungen verwalten',
  type: 'list-report',
  columns: [
    {
      key: 'bestaetigungsNummer',
      label: 'AB-Nr.',
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
        const statusLabels = {
          'OFFEN': { label: 'Offen', variant: 'secondary' as const },
          'GEPRUEFT': { label: 'Geprüft', variant: 'default' as const },
          'BESTAETIGT': { label: 'Bestätigt', variant: 'outline' as const }
        }
        const status = statusLabels[value as keyof typeof statusLabels] || { label: value, variant: 'secondary' as const }
        return <Badge variant={status.variant}>{status.label}</Badge>
      }
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
        { value: 'OFFEN', label: 'Offen' },
        { value: 'GEPRUEFT', label: 'Geprüft' },
        { value: 'BESTAETIGT', label: 'Bestätigt' }
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
      key: 'bestaetigen',
      label: 'Bestätigen',
      type: 'primary',
      onClick: () => console.log('Bestätigen clicked')
    }
  ],
  defaultSort: { field: 'createdAt', direction: 'desc' },
  pageSize: 25,
  api: {
    baseUrl: '/api/einkauf/auftragsbestaetigungen',
    endpoints: {
      list: '/api/einkauf/auftragsbestaetigungen',
      get: '/api/einkauf/auftragsbestaetigungen/{id}',
      create: '/api/einkauf/auftragsbestaetigungen',
      update: '/api/einkauf/auftragsbestaetigungen/{id}',
      delete: '/api/einkauf/auftragsbestaetigungen/{id}'
    }
  },
  permissions: ['einkauf.read', 'einkauf.write'],
  actions: []
}

export default function AuftragsbestaetigungenListePage(): JSX.Element {
  const navigate = useNavigate()
  const [data, setData] = useState<any[]>([])
  const [total, setTotal] = useState(0)
  const [loading, setLoading] = useState(true)

  const { handleAction } = useMaskActions(async (action: string, item: any) => {
    if (action === 'edit' && item) {
      navigate(`/einkauf/auftragsbestaetigungen/${item.id}`)
    } else if (action === 'delete' && item) {
      if (confirm(`Auftragsbestätigung "${item.bestaetigungsNummer}" wirklich löschen?`)) {
        try {
          await apiClient.delete(`/auftragsbestaetigungen/${item.id}`)
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
      const response = await apiClient.get('/auftragsbestaetigungen')
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
    navigate('/einkauf/auftragsbestaetigung/neu')
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
      config={auftragsbestaetigungenConfig}
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