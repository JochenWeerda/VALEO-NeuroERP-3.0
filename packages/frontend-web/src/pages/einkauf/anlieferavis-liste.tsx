import { useMemo } from 'react'
import { useNavigate } from 'react-router-dom'
import { useTranslation } from 'react-i18next'
import { useQueryClient } from '@tanstack/react-query'
import { ListReport } from '@/components/mask-builder'
import { formatDate } from '@/components/mask-builder/utils/formatting'
import { Badge } from '@/components/ui/badge'
import { ListConfig } from '@/components/mask-builder/types'
import { getStatusLabel } from '@/features/crud/utils/i18n-helpers'
import { toast } from '@/hooks/use-toast'
import { useAnlieferavis, type Anlieferavis, einkaufKeys } from '@/lib/api/einkauf'
import { apiClient } from '@/lib/axios'

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
      onClick: () => toast({ title: 'Avis gesendet', description: 'Anlieferavis wurde an den Lieferanten gesendet.' })
    },
    {
      key: 'bestaetigen',
      label: 'Bestaetigen',
      type: 'secondary',
      onClick: () => toast({ title: 'Avis bestätigt', description: 'Anlieferavis wurde bestätigt.' })
    },
    {
      key: 'stornieren',
      label: 'Stornieren',
      type: 'danger',
      onClick: () => toast({ title: 'Avis storniert', description: 'Anlieferavis wurde storniert.', variant: 'destructive' })
    }
  ],
  defaultSort: { field: 'createdAt', direction: 'desc' },
  pageSize: 25,
  api: {
    baseUrl: '/api/v1/einkauf/anlieferavis',
    endpoints: {
      list: '/api/v1/einkauf/anlieferavis',
      get: '/api/v1/einkauf/anlieferavis/{id}',
      create: '/api/v1/einkauf/anlieferavis',
      update: '/api/v1/einkauf/anlieferavis/{id}',
      delete: '/api/v1/einkauf/anlieferavis/{id}'
    }
  },
  permissions: ['einkauf.read', 'einkauf.write', 'warehouse.read'],
  actions: []
})

export default function AnlieferavisListePage(): JSX.Element {
  const { t } = useTranslation()
  const navigate = useNavigate()
  const queryClient = useQueryClient()
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

  const handleDelete = async (item: any) => {
    if (!item?.id) return
    if (!confirm(t('crud.dialogs.delete.descriptionGeneric', { entityType: 'Anlieferavis' }))) return
    try {
      await apiClient.delete(`/api/v1/einkauf/anlieferavis/${item.id}`)
      toast({ title: t('crud.messages.deleteSuccess') })
      queryClient.invalidateQueries({ queryKey: einkaufKeys.anlieferavis() })
    } catch (e: any) {
      toast({ title: t('crud.messages.deleteError'), description: e.response?.data?.detail ?? e.message, variant: 'destructive' })
    }
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
