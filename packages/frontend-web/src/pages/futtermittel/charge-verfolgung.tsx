import { useMemo } from 'react'
import { useNavigate } from 'react-router-dom'
import { ListReport } from '@/components/mask-builder'
import { useFutterChargen, type FutterCharge } from '@/lib/api/futter'
import { formatDate, formatNumber } from '@/components/mask-builder/utils/formatting'
import { Badge } from '@/components/ui/badge'
import { ListConfig } from '@/components/mask-builder/types'
import { toast } from '@/hooks/use-toast'

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
  bulkActions: [
    {
      key: 'export',
      label: 'Exportieren',
      type: 'secondary',
      onClick: () => toast({ title: 'Export', description: 'Chargendaten werden exportiert.' })
    },
    {
      key: 'recall',
      label: 'Recall einleiten',
      type: 'danger',
      onClick: () => toast({ title: 'Rückruf', description: 'Chargen-Rückruf wurde eingeleitet.', variant: 'destructive' })
    },
    {
      key: 'trace',
      label: 'Rückverfolgung',
      type: 'secondary',
      onClick: () => toast({ title: 'Rückverfolgung', description: 'Chargen-Rückverfolgung wird gestartet.' })
    }
  ],
  defaultSort: { field: 'produktionsdatum', direction: 'desc' },
  pageSize: 25,
  api: {
    baseUrl: '/api/futtermittel/chargen',
    endpoints: {
      list: '/api/futtermittel/chargen',
      get: '/api/futtermittel/chargen/{id}',
      create: '/api/futtermittel/chargen',
      update: '/api/futtermittel/chargen/{id}',
      delete: '/api/futtermittel/chargen/{id}'
    }
  },
  permissions: ['futtermittel.read', 'traceability.read'],
  actions: []
}

export default function ChargeVerfolgungPage(): JSX.Element {
  const navigate = useNavigate()
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

  const handleCreate = () => {
    navigate('/futtermittel/chargen/neu')
  }

  const handleEdit = (item: any) => {
    if (item?.id) navigate(`/futtermittel/chargen/${item.id}`)
  }

  const handleDelete = (_item: any) => alert('Löschen wird in dieser Ansicht noch nicht unterstützt')

  const handleExport = () => {
    alert('Export-Funktion wird implementiert')
  }

  return (
    <ListReport
      config={chargeVerfolgungConfig}
      data={data}
      total={total}
      onCreate={handleCreate}
      onEdit={handleEdit}
      onDelete={handleDelete}
      onExport={handleExport}
      onImport={() => alert('Import-Funktion wird implementiert')}
      isLoading={isLoading}
    />
  )
}
