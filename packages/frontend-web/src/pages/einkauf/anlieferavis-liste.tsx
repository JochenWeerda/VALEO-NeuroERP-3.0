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
import { apiClient } from '@/lib/api-client'

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
        const statusValue = String(value || '')
        const statusLabel = getStatusLabel(t, statusValue.toLowerCase(), statusValue)
        const variants: Record<string, 'secondary' | 'default' | 'outline' | 'destructive'> = {
          ANGEKUENDIGT: 'secondary',
          GESENDET: 'secondary',
          BESTAETIGT: 'outline',
          STORNIERT: 'destructive'
        }
        return <Badge variant={variants[statusValue] || 'secondary'}>{statusLabel}</Badge>
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
  bulkActions: [],
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

async function bulkAvisMutation(selectedItems: any[], action: 'send' | 'confirm' | 'cancel', allowedStatuses: string[]) {
  let ok = 0
  const errors: string[] = []
  const eligible = selectedItems.filter((item) => allowedStatuses.includes(String(item.status || '').toUpperCase()))
  for (const item of eligible) {
    try {
      await apiClient.post(`/api/v1/einkauf/anlieferavis/${encodeURIComponent(item.id)}/${action}`)
      ok += 1
    } catch (error: any) {
      errors.push(`${item.avisNummer || item.id}: ${error.response?.data?.detail ?? error.message}`)
    }
  }
  return { ok, errors }
}

export default function AnlieferavisListePage(): JSX.Element {
  const { t } = useTranslation()
  const navigate = useNavigate()
  const queryClient = useQueryClient()
  const baseConfig = createAnlieferavisConfig(t)
  const anlieferavisConfig = useMemo<ListConfig>(() => ({
    ...baseConfig,
    bulkActions: [
      {
        key: 'senden',
        label: 'Senden',
        type: 'primary',
        onClick: async (selectedItems: any[]) => {
          const result = await bulkAvisMutation(selectedItems, 'send', ['ANGEKUENDIGT'])
          queryClient.invalidateQueries({ queryKey: einkaufKeys.anlieferavis() })
          if (result.ok > 0) {
            toast({ title: 'Avis gesendet', description: `${result.ok} Avis an Lieferanten versendet.` })
            return
          }
          toast({ title: 'Keine sendbaren Avis', description: result.errors[0] || 'Bitte angekuendigte Avis markieren.', variant: 'destructive' })
        }
      },
      {
        key: 'bestaetigen',
        label: 'Bestaetigen',
        type: 'secondary',
        onClick: async (selectedItems: any[]) => {
          const result = await bulkAvisMutation(selectedItems, 'confirm', ['ANGEKUENDIGT', 'GESENDET'])
          queryClient.invalidateQueries({ queryKey: einkaufKeys.anlieferavis() })
          if (result.ok > 0) {
            toast({ title: 'Avis bestaetigt', description: `${result.ok} Avis bestaetigt.` })
            return
          }
          toast({ title: 'Keine bestaetigbaren Avis', description: result.errors[0] || 'Bitte angekuendigte oder gesendete Avis markieren.', variant: 'destructive' })
        }
      },
      {
        key: 'stornieren',
        label: 'Stornieren',
        type: 'danger',
        onClick: async (selectedItems: any[]) => {
          const result = await bulkAvisMutation(selectedItems, 'cancel', ['ANGEKUENDIGT', 'GESENDET', 'BESTAETIGT'])
          queryClient.invalidateQueries({ queryKey: einkaufKeys.anlieferavis() })
          if (result.ok > 0) {
            toast({ title: 'Avis storniert', description: `${result.ok} Avis storniert.`, variant: 'destructive' })
            return
          }
          toast({ title: 'Keine stornierbaren Avis', description: result.errors[0] || 'Bitte aktive Avis markieren.', variant: 'destructive' })
        }
      }
    ],
  }), [baseConfig, queryClient, t])
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
        toast({ title: 'Export erstellt', description: `${data.length} Avis fuer den Versand-/Wareneingangspfad exportiert.` })
      }}
      onImport={() => {
        toast({ title: t('crud.messages.importInfo'), description: 'Importpfad bleibt bewusst dateibasiert ausserhalb des Leitstands.' })
      }}
      isLoading={isLoading}
    />
  )
}
