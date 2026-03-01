import { useMemo, useRef } from 'react'
import { useNavigate } from 'react-router-dom'
import { ListReport } from '@/components/mask-builder'
import { useEinzelfutter, type Einzelfutter } from '@/lib/api/futter'
import { toast } from '@/hooks/use-toast'
import { formatCurrency, formatNumber } from '@/components/mask-builder/utils/formatting'
import { Badge } from '@/components/ui/badge'
import { ListConfig } from '@/components/mask-builder/types'
import { api } from '@/lib/axios'

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

async function triggerFutterExport(entity: string, label: string): Promise<void> {
  try {
    const res = await api.post('/api/v1/export/list', { entity, format: 'csv' }, { responseType: 'blob' })
    const blob = res.data as Blob
    const url = URL.createObjectURL(blob)
    const a = document.createElement('a')
    a.href = url
    a.download = `export_${entity}_${new Date().toISOString().slice(0, 10)}.csv`
    a.click()
    URL.revokeObjectURL(url)
    toast({ title: 'Export erstellt', description: `${label} als CSV heruntergeladen.` })
  } catch (e: any) {
    toast({ title: 'Export fehlgeschlagen', description: e.response?.data?.detail ?? e.message, variant: 'destructive' })
  }
}

export default function EinzelfuttermittelListePage(): JSX.Element {
  const navigate = useNavigate()
  const importInputRef = useRef<HTMLInputElement>(null)
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

  const handleExport = () => triggerFutterExport('futtermittel_einzel', 'Einzelfuttermittel')

  const handleImport = () => {
    if (importInputRef.current) importInputRef.current.click()
  }

  const handleImportFile = async (e: React.ChangeEvent<HTMLInputElement>) => {
    const file = e.target.files?.[0]
    if (!file) return
    const formData = new FormData()
    formData.append('file', file)
    try {
      const res = await api.post('/api/v1/futter/import/einzelfuttermittel', formData, {
        headers: { 'Content-Type': 'multipart/form-data' },
      })
      const { created = 0, updated = 0, errors = [] } = (res.data as any) ?? {}
      toast({
        title: 'Import abgeschlossen',
        description: `${created} neu, ${updated} aktualisiert${errors.length ? `, ${errors.length} Fehler` : ''}.`,
      })
    } catch (e: any) {
      toast({ title: 'Import fehlgeschlagen', description: e.response?.data?.detail ?? e.message, variant: 'destructive' })
    }
    e.target.value = ''
  }

  return (
    <>
      <input
        ref={importInputRef}
        type="file"
        accept=".csv"
        className="hidden"
        onChange={handleImportFile}
      />
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
    </>
  )
}
