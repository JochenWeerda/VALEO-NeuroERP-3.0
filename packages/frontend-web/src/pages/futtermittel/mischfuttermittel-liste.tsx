import { useMemo, useRef } from 'react'
import { useNavigate } from 'react-router-dom'
import { useQueryClient } from '@tanstack/react-query'
import { ListReport } from '@/components/mask-builder'
import { toast } from '@/hooks/use-toast'
import { useMischfutter, type Mischfutter } from '@/lib/api/futter'
import { formatCurrency, formatNumber } from '@/components/mask-builder/utils/formatting'
import { Badge } from '@/components/ui/badge'
import { ListConfig } from '@/components/mask-builder/types'
import { api } from '@/lib/axios'

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

async function triggerMischExport(): Promise<void> {
  try {
    const res = await api.post('/api/v1/export/list', { entity: 'futtermittel_misch', format: 'csv' }, { responseType: 'blob' })
    const blob = res.data as Blob
    const url = URL.createObjectURL(blob)
    const a = document.createElement('a')
    a.href = url
    a.download = `export_mischfuttermittel_${new Date().toISOString().slice(0, 10)}.csv`
    a.click()
    URL.revokeObjectURL(url)
    toast({ title: 'Export erstellt', description: 'Mischfuttermittel als CSV heruntergeladen.' })
  } catch (e: any) {
    toast({ title: 'Export fehlgeschlagen', description: e.response?.data?.detail ?? e.message, variant: 'destructive' })
  }
}

export default function MischfuttermittelListePage(): JSX.Element {
  const navigate = useNavigate()
  const queryClient = useQueryClient()
  const importInputRef = useRef<HTMLInputElement>(null)
  const { data: apiData = [], isLoading } = useMischfutter()
  const data = useMemo(() => apiData.map((item: Mischfutter) => ({
    id: item.id,
    artikelnummer: item.artikelnummer,
    name: item.name,
    typ: item.status === 'in-produktion' ? 'ergaenzungsfuttermittel' : 'alleinfuttermittel',
    futtergruppe: item.tierart.toLowerCase(),
    tierart: item.tierart.toLowerCase(),
    lebensphase: item.phase.toLowerCase(),
    gesamtRohprotein: 0,
    umsetzbareEnergie: 0,
    lagerbestand: item.bestand,
    vkPreis: item.preis,
    qsZertifikat: null,
  })), [apiData])
  const total = data.length

  const handleCreate = () => {
    navigate('/futtermittel/mischfuttermittel/stamm/new')
  }

  const handleEdit = (item: any) => {
    if (item?.id) navigate(`/futtermittel/mischfuttermittel/stamm/${item.id}`)
  }

  const handleDelete = async (item: any) => {
    if (!item?.id) return
    if (!confirm(`Mischfuttermittel "${item.name}" wirklich löschen?`)) return
    try {
      await api.delete(`/api/v1/futter/mischfuttermittel/${item.id}`)
      toast({ title: 'Gelöscht', description: `${item.name} wurde gelöscht.` })
      queryClient.invalidateQueries({ queryKey: ['futter', 'misch'] })
    } catch (e: any) {
      toast({ title: 'Löschen fehlgeschlagen', description: e.response?.data?.detail ?? e.message, variant: 'destructive' })
    }
  }

  const handleExport = () => triggerMischExport()

  const handleImport = () => {
    if (importInputRef.current) importInputRef.current.click()
  }

  const handleImportFile = async (e: React.ChangeEvent<HTMLInputElement>) => {
    const file = e.target.files?.[0]
    if (!file) return
    const formData = new FormData()
    formData.append('file', file)
    try {
      const res = await api.post('/api/v1/futter/import/mischfuttermittel', formData, {
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
        config={mischfuttermittelListConfig}
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
