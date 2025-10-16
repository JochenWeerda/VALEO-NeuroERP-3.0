import { useState, useEffect } from 'react'
import { useNavigate } from 'react-router-dom'
import { ListReport } from '@/components/mask-builder'
import { useMaskActions } from '@/components/mask-builder/hooks'
import { createApiClient } from '@/components/mask-builder/utils/api'
import { formatDate, formatNumber } from '@/components/mask-builder/utils/formatting'
import { Badge } from '@/components/ui/badge'
import { ListConfig } from '@/components/mask-builder/types'

// API Client für Bestellungen
const apiClient = createApiClient('/api/einkauf')

// Konfiguration für Bestellungen ListReport
const bestellungenConfig: ListConfig = {
  title: 'Bestellungen',
  subtitle: 'Einkaufsbestellungen verwalten',
  type: 'list-report',
  columns: [
    {
      key: 'nummer',
      label: 'Bestell-Nr.',
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
      key: 'status',
      label: 'Status',
      sortable: true,
      filterable: true,
      render: (value) => {
        const statusLabels = {
          'ENTWURF': { label: 'Entwurf', variant: 'secondary' as const },
          'FREIGEGEBEN': { label: 'Freigegeben', variant: 'default' as const },
          'TEILGELIEFERT': { label: 'Teilgeliefert', variant: 'secondary' as const },
          'VOLLGELIEFERT': { label: 'Vollgeliefert', variant: 'outline' as const },
          'STORNIERT': { label: 'Storniert', variant: 'destructive' as const }
        }
        const status = statusLabels[value as keyof typeof statusLabels] || { label: value, variant: 'secondary' as const }
        return <Badge variant={status.variant}>{status.label}</Badge>
      }
    },
    {
      key: 'liefertermin',
      label: 'Liefertermin',
      sortable: true,
      render: (value) => formatDate(value)
    },
    {
      key: 'gesamtbetrag',
      label: 'Gesamtbetrag',
      sortable: true,
      render: (value) => `${formatNumber(value, 2)} €`
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
        { value: 'ENTWURF', label: 'Entwurf' },
        { value: 'FREIGEGEBEN', label: 'Freigegeben' },
        { value: 'TEILGELIEFERT', label: 'Teilgeliefert' },
        { value: 'VOLLGELIEFERT', label: 'Vollgeliefert' },
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
      key: 'freigeben',
      label: 'Freigeben',
      type: 'primary',
      onClick: () => console.log('Freigeben clicked')
    },
    {
      key: 'stornieren',
      label: 'Stornieren',
      type: 'danger',
      onClick: () => console.log('Stornieren clicked')
    },
    {
      key: 'drucken',
      label: 'Drucken',
      type: 'secondary',
      onClick: () => console.log('Drucken clicked')
    }
  ],
  defaultSort: { field: 'createdAt', direction: 'desc' },
  pageSize: 25,
  api: {
    baseUrl: '/api/einkauf/bestellungen',
    endpoints: {
      list: '/api/einkauf/bestellungen',
      get: '/api/einkauf/bestellungen/{id}',
      create: '/api/einkauf/bestellungen',
      update: '/api/einkauf/bestellungen/{id}',
      delete: '/api/einkauf/bestellungen/{id}'
    }
  },
  permissions: ['einkauf.read', 'einkauf.write'],
  actions: []
}

export default function BestellungenListePage(): JSX.Element {
  const navigate = useNavigate()
  const [data, setData] = useState<any[]>([])
  const [total, setTotal] = useState(0)
  const [loading, setLoading] = useState(true)

  const { handleAction } = useMaskActions(async (action: string, item: any) => {
    if (action === 'edit' && item) {
      navigate(`/einkauf/bestellungen/${item.id}`)
    } else if (action === 'delete' && item) {
      if (confirm(`Bestellung "${item.nummer}" wirklich löschen?`)) {
        try {
          await apiClient.delete(`/bestellungen/${item.id}`)
          loadData() // Liste neu laden
        } catch (error) {
          alert('Fehler beim Löschen')
        }
      }
    } else if (action === 'freigeben' && item) {
      try {
        await apiClient.post(`/bestellungen/${item.id}/freigeben`)
        loadData()
      } catch (error) {
        alert('Fehler beim Freigeben')
      }
    }
  })

  const loadData = async () => {
    setLoading(true)
    try {
      const response = await apiClient.get('/bestellungen')
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
    navigate('/einkauf/bestellung-anlegen')
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
      config={bestellungenConfig}
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
