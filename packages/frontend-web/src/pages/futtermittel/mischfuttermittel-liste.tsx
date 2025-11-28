import { useState, useEffect } from 'react'
import { useNavigate } from 'react-router-dom'
import { ListReport } from '@/components/mask-builder'
import { useMaskActions } from '@/components/mask-builder/hooks'
import { createApiClient } from '@/components/mask-builder/utils/api'
import { formatCurrency, formatNumber } from '@/components/mask-builder/utils/formatting'
import { Badge } from '@/components/ui/badge'
import { ListConfig } from '@/components/mask-builder/types'

// API Client für Mischfuttermittel
const apiClient = createApiClient('/api/futtermittel')

// Konfiguration für Mischfuttermittel ListReport
const mischfuttermittelListConfig: ListConfig = {
  title: 'Mischfuttermittel-Liste',
  subtitle: 'Übersicht aller Mischfuttermittel nach EU 767/2009',
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
          alleinfuttermittel: 'Alleinfuttermittel',
          ergaenzungsfuttermittel: 'Ergänzungsfuttermittel',
          mineralstoffmischung: 'Mineralstoffmischung'
        }
        return <Badge variant="outline">{typeLabels[value as keyof typeof typeLabels] || value}</Badge>
      }
    },
    {
      key: 'futtergruppe',
      label: 'Futtergruppe',
      sortable: true,
      filterable: true,
      render: (value) => {
        const groupLabels = {
          milchvieh: 'Milchvieh',
          mastvieh: 'Mastvieh',
          schweine: 'Schweine',
          gefluegel: 'Geflügel',
          pferde: 'Pferde',
          schafe: 'Schafe'
        }
        return <Badge variant="secondary">{groupLabels[value as keyof typeof groupLabels] || value}</Badge>
      }
    },
    {
      key: 'tierart',
      label: 'Tierart',
      filterable: true,
      render: (value) => {
        const tierLabels = {
          rind: 'Rind',
          schwein: 'Schwein',
          gefluegel: 'Geflügel',
          pferd: 'Pferd',
          schaf: 'Schaf',
          ziege: 'Ziege'
        }
        return tierLabels[value as keyof typeof tierLabels] || value
      }
    },
    {
      key: 'lebensphase',
      label: 'Lebensphase',
      filterable: true,
      render: (value) => {
        const phaseLabels = {
          aufzucht: 'Aufzucht',
          mast: 'Mast',
          laktation: 'Laktation',
          haltung: 'Haltung',
          alle: 'Alle Phasen'
        }
        return phaseLabels[value as keyof typeof phaseLabels] || value
      }
    },
    {
      key: 'gesamtRohprotein',
      label: 'Rohprotein (%)',
      sortable: true,
      render: (value) => value ? formatNumber(value, 1) : '-'
    },
    {
      key: 'umsetzbareEnergie',
      label: 'Energie (MJ/kg)',
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
        { value: 'alleinfuttermittel', label: 'Alleinfuttermittel' },
        { value: 'ergaenzungsfuttermittel', label: 'Ergänzungsfuttermittel' },
        { value: 'mineralstoffmischung', label: 'Mineralstoffmischung' }
      ]
    },
    {
      name: 'futtergruppe',
      label: 'Futtergruppe',
      type: 'select',
      options: [
        { value: 'milchvieh', label: 'Milchvieh' },
        { value: 'mastvieh', label: 'Mastvieh' },
        { value: 'schweine', label: 'Schweine' },
        { value: 'gefluegel', label: 'Geflügel' },
        { value: 'pferde', label: 'Pferde' },
        { value: 'schafe', label: 'Schafe' }
      ]
    },
    {
      name: 'tierart',
      label: 'Tierart',
      type: 'select',
      options: [
        { value: 'rind', label: 'Rind' },
        { value: 'schwein', label: 'Schwein' },
        { value: 'gefluegel', label: 'Geflügel' },
        { value: 'pferd', label: 'Pferd' },
        { value: 'schaf', label: 'Schaf' },
        { value: 'ziege', label: 'Ziege' }
      ]
    },
    {
      name: 'qsZertifikat',
      label: 'QS-zertifiziert',
      type: 'select',
      options: [
        { value: 'true', label: 'Ja' },
        { value: 'false', label: 'Nein' }
      ]
    }
  ],
  bulkActions: [
    {
      key: 'export',
      label: 'Exportieren',
      type: 'secondary',
      onClick: () => { /* Export-Logik implementieren */ }
    },
    {
      key: 'recalculate',
      label: 'Nährwerte neu berechnen',
      type: 'secondary',
      onClick: () => { /* Neuberechnung implementieren */ }
    },
    {
      key: 'delete',
      label: 'Löschen',
      type: 'danger',
      onClick: () => { /* Bulk-Delete implementieren */ }
    }
  ],
  defaultSort: { field: 'name', direction: 'asc' },
  pageSize: 25,
  api: {
    baseUrl: '/api/futtermittel/mischfuttermittel',
    endpoints: {
      list: '/api/futtermittel/mischfuttermittel',
      get: '/api/futtermittel/mischfuttermittel/{id}',
      create: '/api/futtermittel/mischfuttermittel',
      update: '/api/futtermittel/mischfuttermittel/{id}',
      delete: '/api/futtermittel/mischfuttermittel/{id}'
    }
  },
  permissions: ['futtermittel.read', 'futtermittel.write'],
  actions: []
}

export default function MischfuttermittelListePage(): JSX.Element {
  const navigate = useNavigate()
  const [data, setData] = useState<any[]>([])
  const [total, setTotal] = useState(0)
  const [loading, setLoading] = useState(true)

  const { handleAction } = useMaskActions(async (action: string, item: any) => {
    if (action === 'edit' && item) {
      navigate(`/futtermittel/mischfuttermittel/stamm/${item.id}`)
    } else if (action === 'delete' && item) {
      if (confirm(`Möchten Sie "${item.name}" wirklich löschen?`)) {
        try {
          await apiClient.delete(`/mischfuttermittel/${item.id}`)
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
      const response = await apiClient.get('/mischfuttermittel')
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
    navigate('/futtermittel/mischfuttermittel/stamm/new')
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
      config={mischfuttermittelListConfig}
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