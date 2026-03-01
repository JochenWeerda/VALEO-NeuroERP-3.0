import { useMemo } from 'react'
import { useNavigate } from 'react-router-dom'
import { ListReport } from '@/components/mask-builder'
import { useEinzelfutter, type Einzelfutter } from '@/lib/api/futter'
import { toast } from '@/hooks/use-toast'
import { formatCurrency, formatNumber } from '@/components/mask-builder/utils/formatting'
import { Badge } from '@/components/ui/badge'
import { ListConfig } from '@/components/mask-builder/types'

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
  const { data: apiData = [], isLoading } = useEinzelfutter()
  const data = useMemo(() => apiData.map((item: Einzelfutter) => ({
    id: item.id,
    artikelnummer: item.artikelnummer,
    name: item.name,
    typ: item.kategorie,
    hersteller: '-',
    rohprotein: item.rohprotein,
    lagerbestand: item.bestand,
    vkPreis: item.preis,
    euKennzeichnung: false,
    qsZertifikat: null,
  })), [apiData])
  const total = data.length

  const handleCreate = () => {
    navigate('/futtermittel/einzelfuttermittel/stamm/new')
  }

  const handleEdit = (item: any) => {
    if (item?.id) navigate(`/futtermittel/einzelfuttermittel/stamm/${item.id}`)
  }

  const handleDelete = (_item: any) => toast({ title: 'Nicht verfügbar', description: 'Löschen über die Liste wird noch nicht unterstützt.' })

  const handleExport = () => {
    toast({ title: 'Export', description: 'Export-Funktion wird in Kürze bereitgestellt.' })
  }

  const handleImport = () => {
    toast({ title: 'Import', description: 'Import-Funktion wird in Kürze bereitgestellt.' })
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
      isLoading={isLoading}
    />
  )
}
