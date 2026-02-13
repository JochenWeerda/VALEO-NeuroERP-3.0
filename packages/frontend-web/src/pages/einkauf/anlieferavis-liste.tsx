import { useMemo } from 'react'
import { useNavigate } from 'react-router-dom'
import { useTranslation } from 'react-i18next'
import { ListReport } from '@/components/mask-builder'
import { formatDate } from '@/components/mask-builder/utils/formatting'
import { Badge } from '@/components/ui/badge'
import { ListConfig } from '@/components/mask-builder/types'
import { getStatusLabel } from '@/features/crud/utils/i18n-helpers'
import { toast } from '@/hooks/use-toast'
import { useAnlieferavis, type Anlieferavis } from '@/lib/api/einkauf'

const createAnlieferavisConfig = (t: any): ListConfig => ({
  title: 'Anlieferavis',
  subtitle: 'Lieferavise fuer Wareneingangsvorbereitung',
  type: 'list-report',
  columns: [
    {
      key: 'avisNummer',
      label: 'Avis-Nr.',
      sortable: true,
      render: (value) => <code className="text-sm font-mono">{value}</code>
    },
    {
      key: 'bestellung',
      label: 'Bestellung',
      sortable: true,
      render: (value) => value?.nummer || '-'
    },
    {
      key: 'lieferant',
      label: 'Lieferant',
      sortable: true,
      filterable: true
    },
    {
      key: 'status',
      label: 'Status',
      sortable: true,
      filterable: true,
      render: (value) => {
        const statusLabel = getStatusLabel(t, (value as string).toLowerCase(), value as string)
        const variants: Record<string, 'secondary' | 'default' | 'outline' | 'destructive'> = {
          ANGEKUENDIGT: 'secondary',
          GESENDET: 'secondary',
          BESTAETIGT: 'outline',
          STORNIERT: 'destructive'
        }
        return <Badge variant={variants[value as string] || 'secondary'}>{statusLabel}</Badge>
      }
    },
    {
      key: 'geplantesAnlieferDatum',
      label: 'Geplantes Datum',
      sortable: true,
      render: (value) => formatDate(value)
    },
    {
      key: 'fahrzeug',
      label: 'Fahrzeug',
      render: (value) => value?.kennzeichen || '-'
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
        { value: 'ANGEKUENDIGT', label: 'Angekuendigt' },
        { value: 'GESENDET', label: 'Gesendet' },
        { value: 'BESTAETIGT', label: 'Bestaetigt' },
        { value: 'STORNIERT', label: 'Storniert' }
      ]
    },
    {
      name: 'lieferant',
      label: 'Lieferant',
      type: 'text'
    }
  ],
  bulkActions: [
    {
      key: 'senden',
      label: 'Senden',
      type: 'primary',
      onClick: () => console.log('Senden clicked')
    },
    {
      key: 'bestaetigen',
      label: 'Bestaetigen',
      type: 'secondary',
      onClick: () => console.log('Bestaetigen clicked')
    },
    {
      key: 'stornieren',
      label: 'Stornieren',
      type: 'danger',
      onClick: () => console.log('Stornieren clicked')
    }
  ],
  defaultSort: { field: 'createdAt', direction: 'desc' },
  pageSize: 25,
  api: {
    baseUrl: '/api/einkauf/anlieferavis',
    endpoints: {
      list: '/api/einkauf/anlieferavis',
      get: '/api/einkauf/anlieferavis/{id}',
      create: '/api/einkauf/anlieferavis',
      update: '/api/einkauf/anlieferavis/{id}',
      delete: '/api/einkauf/anlieferavis/{id}'
    }
  },
  permissions: ['einkauf.read', 'einkauf.write', 'warehouse.read'],
  actions: []
})

export default function AnlieferavisListePage(): JSX.Element {
  const { t } = useTranslation()
  const navigate = useNavigate()
  const anlieferavisConfig = createAnlieferavisConfig(t)
  const { data: apiData = [], isLoading } = useAnlieferavis()
  const data = useMemo(() => apiData.map((item: Anlieferavis) => ({
    ...item,
    bestellung: { nummer: item.bestellung },
    fahrzeug: { kennzeichen: item.kennzeichen },
  })), [apiData])
  const total = data.length

  const handleCreate = () => {
    navigate('/einkauf/anlieferavis/neu')
  }

  const handleEdit = (item: any) => {
    if (item?.id) {
      navigate(`/einkauf/anlieferavis/${item.id}`)
    }
  }

  const handleDelete = (_item: any) => {
    toast({
      title: t('crud.messages.importInfo'),
      description: 'Loeschen wird in dieser Ansicht noch nicht unterstuetzt.',
    })
  }

  return (
    <ListReport
      config={anlieferavisConfig}
      data={data}
      total={total}
      onCreate={handleCreate}
      onEdit={handleEdit}
      onDelete={handleDelete}
      onExport={() => {
        toast({ title: t('crud.messages.importInfo'), description: t('crud.messages.importComingSoon') })
      }}
      onImport={() => {
        toast({ title: t('crud.messages.importInfo'), description: t('crud.messages.importComingSoon') })
      }}
      isLoading={isLoading}
    />
  )
}
