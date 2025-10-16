import { useState, useEffect } from 'react'
import { useNavigate } from 'react-router-dom'
import { ListReport } from '@/components/mask-builder'
import { useMaskActions } from '@/components/mask-builder/hooks'
import { createApiClient } from '@/components/mask-builder/utils/api'
import { formatDate, formatNumber } from '@/components/mask-builder/utils/formatting'
import { Badge } from '@/components/ui/badge'
import { ListConfig } from '@/components/mask-builder/types'

// API Client für Anfragen
const apiClient = createApiClient('/api/einkauf')

// Konfiguration für Anfragen ListReport
const anfragenConfig: ListConfig = {
  title: 'Bedarfsanforderungen',
  subtitle: 'Interne Bedarfsmeldungen und Anfragen',
  type: 'list-report',
  columns: [
    {
      key: 'anfrageNummer',
      label: 'Anfrage-Nr.',
      sortable: true,
      render: (value) => <code className="text-sm font-mono">{value}</code>
    },
    {
      key: 'typ',
      label: 'Typ',
      sortable: true,
      filterable: true,
      render: (value) => {
        const typLabels = {
          'BANF': 'Bedarfsanforderung',
          'ANF': 'Anfrage'
        }
        return <Badge variant="outline">{typLabels[value as keyof typeof typLabels] || value}</Badge>
      }
    },
    {
      key: 'anforderer',
      label: 'Anforderer',
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
      key: 'menge',
      label: 'Menge',
      sortable: true,
      render: (value, item) => `${formatNumber(value, 2)} ${item.einheit || 'Stk'}`
    },
    {
      key: 'prioritaet',
      label: 'Priorität',
      sortable: true,
      filterable: true,
      render: (value) => {
        const prioLabels = {
          'niedrig': { label: 'Niedrig', variant: 'secondary' as const },
          'normal': { label: 'Normal', variant: 'default' as const },
          'hoch': { label: 'Hoch', variant: 'destructive' as const },
          'dringend': { label: 'Dringend', variant: 'destructive' as const }
        }
        const prio = prioLabels[value as keyof typeof prioLabels] || { label: value, variant: 'secondary' as const }
        return <Badge variant={prio.variant}>{prio.label}</Badge>
      }
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
          'ANGEBOTSPHASE': { label: 'Angebotsphase', variant: 'outline' as const }
        }
        const status = statusLabels[value as keyof typeof statusLabels] || { label: value, variant: 'secondary' as const }
        return <Badge variant={status.variant}>{status.label}</Badge>
      }
    },
    {
      key: 'faelligkeit',
      label: 'Fällig bis',
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
        { value: 'ENTWURF', label: 'Entwurf' },
        { value: 'FREIGEGEBEN', label: 'Freigegeben' },
        { value: 'ANGEBOTSPHASE', label: 'Angebotsphase' }
      ]
    },
    {
      name: 'prioritaet',
      label: 'Priorität',
      type: 'select',
      options: [
        { value: 'niedrig', label: 'Niedrig' },
        { value: 'normal', label: 'Normal' },
        { value: 'hoch', label: 'Hoch' },
        { value: 'dringend', label: 'Dringend' }
      ]
    },
    {
      name: 'anforderer',
      label: 'Anforderer',
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
      key: 'freigeben',
      label: 'Freigeben',
      type: 'primary',
      onClick: () => console.log('Freigeben clicked')
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
    baseUrl: '/api/einkauf/anfragen',
    endpoints: {
      list: '/api/einkauf/anfragen',
      get: '/api/einkauf/anfragen/{id}',
      create: '/api/einkauf/anfragen',
      update: '/api/einkauf/anfragen/{id}',
      delete: '/api/einkauf/anfragen/{id}'
    }
  },
  permissions: ['einkauf.read', 'einkauf.write'],
  actions: []
}

export default function AnfragenListePage(): JSX.Element {
  const navigate = useNavigate()
  const [data, setData] = useState<any[]>([])
  const [total, setTotal] = useState(0)
  const [loading, setLoading] = useState(true)

  const { handleAction } = useMaskActions(async (action: string, item: any) => {
    if (action === 'edit' && item) {
      navigate(`/einkauf/anfragen/${item.id}`)
    } else if (action === 'delete' && item) {
      if (confirm(`Anfrage "${item.anfrageNummer}" wirklich löschen?`)) {
        try {
          await apiClient.delete(`/anfragen/${item.id}`)
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
      const response = await apiClient.get('/anfragen')
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
    navigate('/einkauf/anfrage/neu')
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
      config={anfragenConfig}
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