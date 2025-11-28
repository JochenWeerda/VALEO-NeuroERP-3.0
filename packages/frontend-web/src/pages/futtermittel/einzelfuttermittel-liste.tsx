import { useState, useEffect } from 'react'
import { useNavigate } from 'react-router-dom'
import { ListReport } from '@/components/mask-builder'
import { useMaskActions } from '@/components/mask-builder/hooks'
import { createApiClient } from '@/components/mask-builder/utils/api'
import { formatCurrency, formatNumber } from '@/components/mask-builder/utils/formatting'
import { Badge } from '@/components/ui/badge'
import { ListConfig } from '@/components/mask-builder/types'

// API Client für Futtermittel
const apiClient = createApiClient('/api/futtermittel')

// Konfiguration für die ListReport
const futtermittelListConfig: ListConfig = {
  title: 'Einzelfuttermittel-Liste',
  subtitle: 'Übersicht aller Einzelfuttermittel nach EU 68/2013',
  type: 'list-report',
  columns: [
    {
      key: 'artikelnummer',
      label: 'Artikelnummer',
      sortable: true,
      render: (value) => <code className="text-sm">{value}</code>
    },
    {
      key: 'name',
      label: 'Name',
      sortable: true,
      filterable: true
    },
    {
      key: 'typ',
      label: 'Typ',
      sortable: true,
      filterable: true,
      render: (value) => {
        const typeLabels = {
          getreide: 'Getreide',
          oelsaat: 'Ölsaaten',
          protein: 'Proteinfuttermittel',
          mineralstoff: 'Mineralstoffe',
          sonstiges: 'Sonstiges'
        }
        return <Badge variant="outline">{typeLabels[value as keyof typeof typeLabels] || value}</Badge>
      }
    },
    {
      key: 'hersteller',
      label: 'Hersteller',
      filterable: true
    },
    {
      key: 'rohprotein',
      label: 'Rohprotein (%)',
      sortable: true,
      render: (value) => value ? formatNumber(value, 1) : '-'
    },
    {
      key: 'lagerbestand',
      label: 'Lagerbestand (kg)',
      sortable: true,
      render: (value) => formatNumber(value || 0, 0)
    },
    {
      key: 'vkPreis',
      label: 'VK-Preis (€/kg)',
      sortable: true,
      render: (value) => value ? formatCurrency(value) : '-'
    },
    {
      key: 'euKennzeichnung',
      label: 'EU-Kennzeichnung',
      render: (value) => (
        <Badge variant={value ? 'default' : 'secondary'}>
          {value ? 'Erforderlich' : 'Nicht erforderlich'}
        </Badge>
      )
    },
    {
      key: 'qsZertifikat',
      label: 'QS-Zertifikat',
      render: (value) => value ? <Badge variant="outline">{value}</Badge> : '-'
    }
  ],
  filters: [
    {
      name: 'typ',
      label: 'Typ',
      type: 'select',
      options: [
        { value: 'getreide', label: 'Getreide' },
        { value: 'oelsaat', label: 'Ölsaaten' },
        { value: 'protein', label: 'Proteinfuttermittel' },
        { value: 'mineralstoff', label: 'Mineralstoffe' },
        { value: 'sonstiges', label: 'Sonstiges' }
      ]
    },
    {
      name: 'euKennzeichnung',
      label: 'EU-Kennzeichnung',
      type: 'select',
      options: [
        { value: 'true', label: 'Erforderlich' },
        { value: 'false', label: 'Nicht erforderlich' }
      ]
    },
    {
      name: 'hersteller',
      label: 'Hersteller',
      type: 'text'
    }
  ],
  bulkActions: [
    {
      key: 'export',
      label: 'Exportieren',
      type: 'secondary',
      onClick: () => {}
    },
    {
      key: 'delete',
      label: 'Löschen',
      type: 'danger',
      onClick: () => {}
    }
  ],
  defaultSort: { field: 'name', direction: 'asc' },
  pageSize: 25,
  api: {
    baseUrl: '/api/futtermittel/einzelfuttermittel',
    endpoints: {
      list: '/api/futtermittel/einzelfuttermittel',
      get: '/api/futtermittel/einzelfuttermittel/{id}',
      create: '/api/futtermittel/einzelfuttermittel',
      update: '/api/futtermittel/einzelfuttermittel/{id}',
      delete: '/api/futtermittel/einzelfuttermittel/{id}'
    }
  },
  permissions: ['futtermittel.read', 'futtermittel.write'],
  actions: []
}

export default function EinzelfuttermittelListePage(): JSX.Element {
  const navigate = useNavigate()
  const [data, setData] = useState<any[]>([])
  const [total, setTotal] = useState(0)
  const [loading, setLoading] = useState(true)

  // Framework Hooks verwenden
  const { handleAction } = useMaskActions(async (action: string, item: any) => {
    if (action === 'edit' && item) {
      navigate(`/futtermittel/einzelfuttermittel/stamm/${item.id}`)
    } else if (action === 'delete' && item) {
      if (confirm(`Möchten Sie "${item.name}" wirklich löschen?`)) {
        try {
          await apiClient.delete(`/einzelfuttermittel/${item.id}`)
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
      const response = await apiClient.get('/einzelfuttermittel')
      if (response.success) {
        setData((response.data as any).data || [])
        setTotal((response.data as any).total || 0)
      }
    } catch (_error) {
      // API nicht erreichbar - leere Daten beibehalten
      setData([])
      setTotal(0)
    } finally {
      setLoading(false)
    }
  }

  useEffect(() => {
    loadData()
  }, [])

  const handleCreate = () => {
    navigate('/futtermittel/einzelfuttermittel/stamm/new')
  }

  const handleEdit = (item: any) => {
    handleAction('edit', item)
  }

  const handleDelete = (item: any) => {
    handleAction('delete', item)
  }

  const handleExport = () => {
    // Export-Logik hier implementieren
    alert('Export-Funktion wird implementiert')
  }

  const handleImport = () => {
    // Import-Logik hier implementieren
    alert('Import-Funktion wird implementiert')
  }

  return (
    <ListReport
      config={futtermittelListConfig}
      data={data}
      total={total}
      onCreate={handleCreate}
      onEdit={handleEdit}
      onDelete={handleDelete}
      onExport={handleExport}
      onImport={handleImport}
      isLoading={loading}
    />
  )
}