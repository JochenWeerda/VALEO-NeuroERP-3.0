import { useState, useEffect } from 'react'
import { useNavigate } from 'react-router-dom'
import { ListReport } from '@/components/mask-builder'
import { useMaskActions } from '@/components/mask-builder/hooks'
import { createApiClient } from '@/components/mask-builder/utils/api'
import { formatCurrency, formatNumber } from '@/components/mask-builder/utils/formatting'
import { Badge } from '@/components/ui/badge'
import { ListConfig } from '@/components/mask-builder/types'

// API Client für Kunden
const apiClient = createApiClient('/api/crm')

// Konfiguration für Kunden ListReport
const kundenListConfig: ListConfig = {
  title: 'Kunden-Liste',
  subtitle: 'Übersicht aller Geschäftspartner',
  type: 'list-report',
  columns: [
    {
      key: 'firma',
      label: 'Firma',
      sortable: true,
      filterable: true,
      render: (value, row) => (
        <div>
          <div className="font-medium">{value || `${row.vorname} ${row.nachname}`}</div>
          {value && row.nachname && <div className="text-sm text-muted-foreground">{row.vorname} {row.nachname}</div>}
        </div>
      )
    },
    {
      key: 'ort',
      label: 'Ort',
      sortable: true,
      filterable: true,
      render: (value, row) => `${row.plz} ${value}`
    },
    {
      key: 'telefon',
      label: 'Telefon',
      render: (value) => value || '-'
    },
    {
      key: 'email',
      label: 'E-Mail',
      render: (value) => value ? <a href={`mailto:${value}`} className="text-blue-600 hover:underline">{value}</a> : '-'
    },
    {
      key: 'umsatzGesamt',
      label: 'Gesamtumsatz',
      sortable: true,
      render: (value) => formatCurrency(value || 0)
    },
    {
      key: 'letzteBestellung',
      label: 'Letzte Bestellung',
      sortable: true,
      render: (value) => value ? new Date(value).toLocaleDateString('de-DE') : '-'
    },
    {
      key: 'bonitaet',
      label: 'Bonität',
      sortable: true,
      filterable: true,
      render: (value) => {
        const colors = {
          'ausgezeichnet': 'bg-green-100 text-green-800',
          'gut': 'bg-blue-100 text-blue-800',
          'mittel': 'bg-yellow-100 text-yellow-800',
          'schlecht': 'bg-red-100 text-red-800',
          'unklar': 'bg-gray-100 text-gray-800'
        }
        return <Badge className={colors[value as keyof typeof colors] || colors.unklar}>{value}</Badge>
      }
    },
    {
      key: 'status',
      label: 'Status',
      sortable: true,
      filterable: true,
      render: (value) => {
        const statusLabels = {
          'aktiv': { label: 'Aktiv', variant: 'default' as const },
          'inaktiv': { label: 'Inaktiv', variant: 'secondary' as const },
          'gesperrt': { label: 'Gesperrt', variant: 'destructive' as const }
        }
        const status = statusLabels[value as keyof typeof statusLabels] || statusLabels.aktiv
        return <Badge variant={status.variant}>{status.label}</Badge>
      }
    },
    {
      key: 'kreditlimit',
      label: 'Kreditlimit',
      sortable: true,
      render: (value) => value ? formatCurrency(value) : '-'
    },
    {
      key: 'rabatt',
      label: 'Rabatt',
      sortable: true,
      render: (value) => value ? `${formatNumber(value, 1)}%` : '-'
    }
  ],
  filters: [
    {
      name: 'status',
      label: 'Status',
      type: 'select',
      options: [
        { value: 'aktiv', label: 'Aktiv' },
        { value: 'inaktiv', label: 'Inaktiv' },
        { value: 'gesperrt', label: 'Gesperrt' }
      ]
    },
    {
      name: 'bonitaet',
      label: 'Bonität',
      type: 'select',
      options: [
        { value: 'ausgezeichnet', label: 'Ausgezeichnet' },
        { value: 'gut', label: 'Gut' },
        { value: 'mittel', label: 'Mittel' },
        { value: 'schlecht', label: 'Schlecht' },
        { value: 'unklar', label: 'Unklar' }
      ]
    },
    {
      name: 'ort',
      label: 'Ort',
      type: 'text'
    },
    {
      name: 'umsatzGesamt',
      label: 'Umsatz von',
      type: 'number',
      min: 0
    },
    {
      name: 'umsatzGesamt',
      label: 'Umsatz bis',
      type: 'number',
      min: 0
    }
  ],
  bulkActions: [
    {
      key: 'export',
      label: 'Exportieren',
      type: 'secondary',
      onClick: () => console.log('Export clicked')
    },
    {
      key: 'newsletter',
      label: 'Newsletter senden',
      type: 'secondary',
      onClick: () => console.log('Newsletter clicked')
    },
    {
      key: 'block',
      label: 'Sperren',
      type: 'danger',
      onClick: () => console.log('Block clicked')
    }
  ],
  defaultSort: { field: 'firma', direction: 'asc' },
  pageSize: 25,
  api: {
    baseUrl: '/api/crm/kunden',
    endpoints: {
      list: '/api/crm/kunden',
      get: '/api/crm/kunden/{id}',
      create: '/api/crm/kunden',
      update: '/api/crm/kunden/{id}',
      delete: '/api/crm/kunden/{id}'
    }
  },
  permissions: ['crm.read', 'customer.read'],
  actions: []
}

export default function KundenListePage(): JSX.Element {
  const navigate = useNavigate()
  const [data, setData] = useState<any[]>([])
  const [total, setTotal] = useState(0)
  const [loading, setLoading] = useState(true)

  const { handleAction } = useMaskActions(async (action: string, item: any) => {
    if (action === 'edit' && item) {
      navigate(`/crm/kunden/stamm/${item.id}`)
    } else if (action === 'delete' && item) {
      if (confirm(`Kunden "${item.firma || item.nachname}" wirklich löschen?`)) {
        try {
          await apiClient.delete(`/kunden/${item.id}`)
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
      const response = await apiClient.get('/kunden')
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
    navigate('/crm/kunden/stamm/new')
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
      config={kundenListConfig}
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