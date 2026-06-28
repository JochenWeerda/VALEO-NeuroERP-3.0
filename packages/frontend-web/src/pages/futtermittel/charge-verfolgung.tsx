import { useMemo, useRef } from 'react'
import { useNavigate } from '@/app/routing/typed-router'
import { useQueryClient } from '@tanstack/react-query'
import { ListReport } from '@/components/mask-builder'
import { useFutterChargen, type FutterCharge } from '@/lib/api/futter'
import { formatDate, formatNumber } from '@/components/mask-builder/utils/formatting'
import { Badge } from '@/components/ui/badge'
import { ListConfig } from '@/components/mask-builder/types'
import { toast } from '@/hooks/use-toast'
import { api } from '@/lib/axios'

// Konfiguration für Charge-Verfolgung ListReport
const chargeVerfolgungConfig: ListConfig = {
  title: 'Charge-Verfolgung',
  subtitle: 'Rückverfolgbarkeit nach EU 178/2002 - Vom Feld bis zum Tier',
  type: 'list-report',
  columns: [
    {
      key: 'chargenNummer',
      label: 'Chargen-Nr.',
      sortable: true,
      render: (value) => <code className="text-sm font-mono">{value}</code>
    },
    {
      key: 'futtermittel',
      label: 'Futtermittel',
      sortable: true,
      filterable: true
    },
    {
      key: 'menge',
      label: 'Menge (kg)',
      sortable: true,
      render: (value) => formatNumber(value, 0)
    },
    {
      key: 'herkunft',
      label: 'Herkunft',
      filterable: true,
      render: (value) => {
        const herkunftsLabels = {
          'deutschland': 'Deutschland',
          'eu': 'EU',
          'nicht-eu': 'Nicht-EU',
          'unbekannt': 'Unbekannt'
        }
        return <Badge variant="outline">{herkunftsLabels[value as keyof typeof herkunftsLabels] || value}</Badge>
      }
    },
    {
      key: 'produktionsdatum',
      label: 'Produktion',
      sortable: true,
      render: (value) => formatDate(value)
    },
    {
      key: 'verfallsdatum',
      label: 'Verfall',
      sortable: true,
      render: (value) => {
        const date = new Date(value)
        const now = new Date()
        const daysUntilExpiry = Math.ceil((date.getTime() - now.getTime()) / (1000 * 60 * 60 * 24))

        let variant: 'default' | 'secondary' | 'destructive' = 'secondary'
        if (daysUntilExpiry < 0) variant = 'destructive'
        else if (daysUntilExpiry < 30) variant = 'default'

        return <Badge variant={variant}>{formatDate(value)}</Badge>
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
          'reserviert': { label: 'Reserviert', variant: 'secondary' as const },
          'verwendet': { label: 'Verwendet', variant: 'outline' as const },
          'abgelaufen': { label: 'Abgelaufen', variant: 'destructive' as const },
          'recall': { label: 'Recall', variant: 'destructive' as const }
        }
        const status = statusLabels[value as keyof typeof statusLabels] || { label: value, variant: 'secondary' as const }
        return <Badge variant={status.variant}>{status.label}</Badge>
      }
    },
    {
      key: 'qsZertifikat',
      label: 'QS-Status',
      render: (value) => value ? <Badge variant="outline">Zertifiziert</Badge> : <Badge variant="secondary">Nicht zertifiziert</Badge>
    },
    {
      key: 'rueckverfolgbarkeit',
      label: 'Rückverfolgung',
      render: (value) => (
        <div className="flex gap-1">
          {value?.feld && <Badge variant="outline" className="text-xs">Feld</Badge>}
          {value?.produktion && <Badge variant="outline" className="text-xs">Prod.</Badge>}
          {value?.transport && <Badge variant="outline" className="text-xs">Transport</Badge>}
          {value?.lager && <Badge variant="outline" className="text-xs">Lager</Badge>}
        </div>
      )
    }
  ],
  filters: [
    {
      name: 'status',
      label: 'Status',
      type: 'select',
      options: [
        { value: 'aktiv', label: 'Aktiv' },
        { value: 'reserviert', label: 'Reserviert' },
        { value: 'verwendet', label: 'Verwendet' },
        { value: 'abgelaufen', label: 'Abgelaufen' },
        { value: 'recall', label: 'Recall' }
      ]
    },
    {
      name: 'herkunft',
      label: 'Herkunft',
      type: 'select',
      options: [
        { value: 'deutschland', label: 'Deutschland' },
        { value: 'eu', label: 'EU' },
        { value: 'nicht-eu', label: 'Nicht-EU' }
      ]
    },
    {
      name: 'futtermittel',
      label: 'Futtermittel',
      type: 'text'
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
  bulkActions: [],
  defaultSort: { field: 'produktionsdatum', direction: 'desc' },
  pageSize: 25,
  api: {
    baseUrl: '/api/v1/futter/chargen',
    endpoints: {
      list: '/api/v1/futter/chargen',
      get: '/api/v1/futter/chargen/{id}',
      create: '/api/v1/futter/chargen',
      update: '/api/v1/futter/chargen/{id}',
      delete: '/api/v1/futter/chargen/{id}'
    }
  },
  permissions: ['futtermittel.read', 'traceability.read'],
  actions: []
}

async function triggerChargenExport(): Promise<void> {
  try {
    const res = await api.post('/api/v1/export/list', { entity: 'futtermittel_chargen', format: 'csv' }, { responseType: 'blob' })
    const blob = res.data as Blob
    const url = URL.createObjectURL(blob)
    const a = document.createElement('a')
    a.href = url
    a.download = `export_chargen_${new Date().toISOString().slice(0, 10)}.csv`
    a.click()
    URL.revokeObjectURL(url)
    toast({ title: 'Export erstellt', description: 'Chargen-Daten als CSV heruntergeladen.' })
  } catch (_rawErr: unknown) {
        const e = _rawErr as { response?: { data?: { detail?: string } }; message?: string; name?: string }
    toast({ title: 'Export fehlgeschlagen', description: e.response?.data?.detail ?? e.message, variant: 'destructive' })
  }
}

export default function ChargeVerfolgungPage(): JSX.Element {
  const navigate = useNavigate()
  const queryClient = useQueryClient()
  const importInputRef = useRef<HTMLInputElement>(null)
  const { data: apiData = [], isLoading } = useFutterChargen()
  const data = useMemo(() => apiData.map((item: FutterCharge) => ({
    id: item.id,
    chargenNummer: item.chargenId,
    futtermittel: item.produkt,
    menge: item.menge,
    herkunft: 'deutschland',
    produktionsdatum: item.herstelldatum,
    verfallsdatum: item.mhd,
    status: item.status === 'in-pruefung' ? 'reserviert' : item.status,
    qsZertifikat: true,
    rueckverfolgbarkeit: { feld: true, produktion: true, transport: true, lager: true },
  })), [apiData])
  const total = data.length

  const chargenConfig: ListConfig = useMemo(() => ({
    ...chargeVerfolgungConfig,
    bulkActions: [
      {
        key: 'export',
        label: 'Exportieren',
        type: 'secondary' as const,
        onClick: () => { void triggerChargenExport() }
      },
      {
        key: 'recall',
        label: 'Recall einleiten',
        type: 'danger' as const,
        onClick: async (items: Record<string, unknown>[]) => {
          if (!confirm(`Rückruf für ${items.length} Charge(n) einleiten?`)) return
          let ok = 0; let err = 0
          for (const item of items) {
            try {
              await api.patch(`/api/v1/futter/chargen/${String(item.id ?? '')}`, { status: 'recall' })
              ok++
            } catch { err++ }
          }
          queryClient.invalidateQueries({ queryKey: ['futter', 'chargen'] })
          toast({
            title: 'Rückruf eingeleitet',
            description: `${ok} Charge(n) auf Recall gesetzt${err ? `, ${err} Fehler` : ''}.`,
            variant: 'destructive'
          })
        }
      },
      {
        key: 'trace',
        label: 'Rückverfolgung',
        type: 'secondary' as const,
        onClick: (items: Record<string, unknown>[]) => {
          if (items.length === 0) return
          if (items.length === 1) {
            navigate(`/charge/rueckverfolgung?chargeId=${String(items[0].id ?? '')}`)
            return
          }
          const selected = items.map((item) => item.id).join(',')
          navigate(`/charge/rueckverfolgung?selected=${selected}`)
        }
      }
    ]
  }), [queryClient, navigate])

  const handleCreate = () => {
    navigate('/futtermittel/chargen/neu')
  }

  const handleEdit = (item: Record<string, unknown>) => {
    if (item?.id) navigate(`/futtermittel/chargen/${String(item.id ?? '')}`)
  }

  const handleDelete = async (item: Record<string, unknown>) => {
    if (!item?.id) return
    if (!confirm(`Charge "${String(item.chargenNummer ?? item.id)}" wirklich löschen?`)) return
    try {
      await api.delete(`/api/v1/futter/chargen/${String(item.id ?? '')}`)
      toast({ title: 'Gelöscht', description: 'Charge wurde gelöscht.' })
      queryClient.invalidateQueries({ queryKey: ['futter', 'chargen'] })
    } catch (_rawErr: unknown) {
        const e = _rawErr as { response?: { data?: { detail?: string } }; message?: string; name?: string }
      toast({ title: 'Löschen fehlgeschlagen', description: e.response?.data?.detail ?? e.message, variant: 'destructive' })
    }
  }

  const handleExport = () => triggerChargenExport()

  const handleImport = () => {
    if (importInputRef.current) importInputRef.current.click()
  }

  const handleImportFile = async (e: React.ChangeEvent<HTMLInputElement>) => {
    const file = e.target.files?.[0]
    if (!file) return
    const formData = new FormData()
    formData.append('file', file)
    try {
      const res = await api.post('/api/v1/futter/import/chargen', formData, {
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
        config={chargenConfig}
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
