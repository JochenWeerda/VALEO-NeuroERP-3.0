import { useMemo, useRef } from 'react'
import { useNavigate } from '@/app/routing/typed-router'
import { useQueryClient } from '@tanstack/react-query'
import { ListReport } from '@/components/mask-builder'
import { bulkDeleteFutterItems, useEinzelfutter, type Einzelfutter } from '@/lib/api/futter'
import { toast } from '@/hooks/use-toast'
import { formatCurrency, formatNumber } from '@/components/mask-builder/utils/formatting'
import { Badge } from '@/components/ui/badge'
import { ListConfig } from '@/components/mask-builder/types'
import { api } from '@/lib/axios'
import { apiClient } from '@/lib/api-client'

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
    baseUrl: '/api/v1/futter/einzelfuttermittel',
    endpoints: {
      list: '/api/v1/futter/einzelfuttermittel',
      get: '/api/v1/futter/einzelfuttermittel/{id}',
      create: '/api/v1/futter/einzelfuttermittel',
      update: '/api/v1/futter/einzelfuttermittel/{id}',
      delete: '/api/v1/futter/einzelfuttermittel/{id}'
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
  } catch (_rawErr: unknown) {
        const e = _rawErr as { response?: { data?: { detail?: string } }; message?: string; name?: string }
    toast({ title: 'Export fehlgeschlagen', description: e.response?.data?.detail ?? e.message, variant: 'destructive' })
  }
}

export default function EinzelfuttermittelListePage(): JSX.Element {
  const navigate = useNavigate()
  const queryClient = useQueryClient()
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

  const einzelfuttermittelConfig: ListConfig = useMemo(() => ({
    ...futtermittelListConfig,
    bulkActions: [
      {
        key: 'export',
        label: 'Exportieren',
        type: 'secondary' as const,
        onClick: (items: Record<string, unknown>[]) => {
          void triggerFutterExport('futtermittel_einzel', `Einzelfuttermittel (${items.length})`)
        }
      },
      {
        key: 'delete',
        label: 'Löschen',
        type: 'danger' as const,
        onClick: async (items: Record<string, unknown>[]) => {
          if (!confirm(`${items.length} Einzelfuttermittel wirklich löschen?`)) return
          const result = await bulkDeleteFutterItems('einzelfuttermittel', items.map((item) => item.id))
          queryClient.invalidateQueries({ queryKey: ['futter', 'einzel'] })
          toast({
            title: 'Bulk-Löschen',
            description: `${result.deleted} gelöscht${result.errors.length || result.missing_ids.length ? `, ${result.errors.length + result.missing_ids.length} Probleme` : ''}.`,
            variant: result.errors.length || result.missing_ids.length ? 'destructive' : 'default',
          })
        }
      }
    ]
  }), [queryClient])

  const handleCreate = () => {
    navigate('/futtermittel/einzelfuttermittel/stamm/new')
  }

  const handleEdit = (item: Record<string, unknown>) => {
    if (item?.id) navigate(`/futtermittel/einzelfuttermittel/stamm/${String(item.id ?? '')}`)
  }

  const handleDelete = async (item: Record<string, unknown>) => {
    if (!item?.id) return
    if (!confirm(`Einzelfuttermittel "${String(item.name ?? '')}" wirklich löschen?`)) return
    try {
      await apiClient.delete(`/api/v1/futter/einzelfuttermittel/${String(item.id ?? '')}`)
      toast({ title: 'Gelöscht', description: `${String(item.name ?? '')} wurde gelöscht.` })
      queryClient.invalidateQueries({ queryKey: ['futter', 'einzel'] })
    } catch (_rawErr: unknown) {
        const e = _rawErr as { response?: { data?: { detail?: string } }; message?: string; name?: string }
      toast({ title: 'Löschen fehlgeschlagen', description: e.response?.data?.detail ?? e.message, variant: 'destructive' })
    }
  }

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
      const { created = 0, updated = 0, errors = [] } = (res.data as Record<string, unknown>) ?? {}
      toast({
        title: 'Import abgeschlossen',
        description: `${String(created ?? '')} neu, ${String(updated ?? '')} aktualisiert${errors.length ? `, ${errors.length} Fehler` : ''}.`,
      })
    } catch (_rawErr: unknown) {
        const e = _rawErr as { response?: { data?: { detail?: string } }; message?: string; name?: string }
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
        config={einzelfuttermittelConfig}
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


