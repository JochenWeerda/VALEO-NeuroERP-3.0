import { useMemo } from 'react'
import { useNavigate } from 'react-router-dom'
import { useTranslation } from 'react-i18next'
import { ListReport } from '@/components/mask-builder'
import { formatDate } from '@/components/mask-builder/utils/formatting'
import { Badge } from '@/components/ui/badge'
import { ListConfig } from '@/components/mask-builder/types'
import { getEntityTypeLabel, getStatusLabel } from '@/features/crud/utils/i18n-helpers'
import { toast } from '@/hooks/use-toast'
import { useAuftragsbestaetigungen, type Auftragsbestaetigung } from '@/lib/api/einkauf'

const createAuftragsbestaetigungenConfig = (t: any, entityTypeLabel: string): ListConfig => ({
  title: entityTypeLabel,
  titleKey: 'crud.list.title',
  subtitle: t('crud.subtitles.manageOrderConfirmations'),
  subtitleKey: 'crud.subtitles.manageOrderConfirmations',
  type: 'list-report',
  columns: [
    {
      key: 'bestaetigungsNummer',
      label: t('crud.fields.confirmationNumber'),
      labelKey: 'crud.fields.confirmationNumber',
      sortable: true,
      render: (value) => <code className="text-sm font-mono">{value}</code>
    },
    {
      key: 'bestellung',
      label: t('crud.entities.purchaseOrder'),
      labelKey: 'crud.entities.purchaseOrder',
      sortable: true,
      render: (value) => value?.nummer || '-'
    },
    {
      key: 'lieferant',
      label: t('crud.entities.supplier'),
      labelKey: 'crud.entities.supplier',
      sortable: true,
      filterable: true
    },
    {
      key: 'status',
      label: t('crud.fields.status'),
      labelKey: 'crud.fields.status',
      sortable: true,
      filterable: true,
      render: (value) => {
        const statusLabel = getStatusLabel(t, value as string, value as string)
        const variants: Record<string, 'secondary' | 'default' | 'outline' | 'destructive'> = {
          OFFEN: 'secondary',
          GEPRUEFT: 'default',
          BESTAETIGT: 'outline'
        }
        return <Badge variant={variants[value as string] || 'secondary'}>{statusLabel}</Badge>
      }
    },
    {
      key: 'createdAt',
      label: t('crud.fields.createdAt'),
      labelKey: 'crud.fields.createdAt',
      sortable: true,
      render: (value) => formatDate(value)
    }
  ],
  filters: [
    {
      name: 'status',
      label: t('crud.fields.status'),
      labelKey: 'crud.fields.status',
      type: 'select',
      options: [
        { value: 'OFFEN', label: t('status.pending'), labelKey: 'status.pending' },
        { value: 'GEPRUEFT', label: t('status.reviewed'), labelKey: 'status.reviewed' },
        { value: 'BESTAETIGT', label: t('status.confirmed'), labelKey: 'status.confirmed' }
      ]
    },
    {
      name: 'lieferant',
      label: t('crud.entities.supplier'),
      labelKey: 'crud.entities.supplier',
      type: 'text'
    }
  ],
  bulkActions: [
    {
      key: 'pruefen',
      label: t('crud.actions.review'),
      labelKey: 'crud.actions.review',
      type: 'secondary',
      onClick: () => toast({ title: 'Prüfen', description: 'Auftragsbestätigung wurde zur Prüfung markiert.' })
    },
    {
      key: 'bestaetigen',
      label: t('crud.actions.confirm'),
      labelKey: 'crud.actions.confirm',
      type: 'primary',
      onClick: () => toast({ title: 'Bestätigt', description: 'Auftragsbestätigung wurde bestätigt.' })
    }
  ],
  defaultSort: { field: 'createdAt', direction: 'desc' },
  pageSize: 25,
  api: {
    baseUrl: '/api/einkauf/auftragsbestaetigungen',
    endpoints: {
      list: '/api/einkauf/auftragsbestaetigungen',
      get: '/api/einkauf/auftragsbestaetigungen/{id}',
      create: '/api/einkauf/auftragsbestaetigungen',
      update: '/api/einkauf/auftragsbestaetigungen/{id}',
      delete: '/api/einkauf/auftragsbestaetigungen/{id}'
    }
  },
  permissions: ['einkauf.read', 'einkauf.write'],
  actions: []
})

export default function AuftragsbestaetigungenListePage(): JSX.Element {
  const { t } = useTranslation()
  const navigate = useNavigate()
  const { data: apiData = [], isLoading } = useAuftragsbestaetigungen()
  const data = useMemo(() => apiData.map((item: Auftragsbestaetigung) => ({
    ...item,
    bestellung: { nummer: item.bestellung },
  })), [apiData])
  const total = data.length
  const entityType = 'orderConfirmation'
  const entityTypeLabel = getEntityTypeLabel(t, entityType, 'Auftragsbestaetigung')
  const auftragsbestaetigungenConfig = createAuftragsbestaetigungenConfig(t, entityTypeLabel)

  const handleCreate = () => {
    navigate('/einkauf/auftragsbestaetigung/neu')
  }

  const handleEdit = (item: any) => {
    if (item?.id) {
      navigate(`/einkauf/auftragsbestaetigungen/${item.id}`)
    }
  }

  const handleDelete = (_item: any) => {
    toast({
      title: t('crud.messages.importInfo'),
      description: 'Loeschen wird in dieser Ansicht noch nicht unterstuetzt.',
    })
  }

  const handleExport = () => {
    try {
      const csvHeader = `${t('crud.fields.confirmationNumber')};${t('crud.entities.purchaseOrder')};${t('crud.entities.supplier')};${t('crud.fields.status')}\n`
      const csvContent = data.map((ab: any) =>
        `"${ab.bestaetigungsNummer}";"${ab.bestellung?.nummer || ''}";"${ab.lieferant}";"${ab.status}"`
      ).join('\n')

      const csv = csvHeader + csvContent
      const blob = new Blob([csv], { type: 'text/csv;charset=utf-8;' })
      const link = document.createElement('a')
      const url = URL.createObjectURL(blob)
      link.setAttribute('href', url)
      link.setAttribute('download', `auftragsbestaetigungen-liste-${new Date().toISOString().split('T')[0]}.csv`)
      link.style.visibility = 'hidden'
      document.body.appendChild(link)
      link.click()
      document.body.removeChild(link)

      toast({
        title: t('crud.messages.exportSuccess'),
        description: t('crud.messages.exportedItems', { count: data.length, entityType: entityTypeLabel }),
      })
    } catch {
      toast({
        variant: 'destructive',
        title: t('crud.messages.exportError'),
        description: t('crud.messages.exportFailed'),
      })
    }
  }

  return (
    <ListReport
      config={auftragsbestaetigungenConfig}
      data={data}
      total={total}
      onCreate={handleCreate}
      onEdit={handleEdit}
      onDelete={handleDelete}
      onExport={handleExport}
      onImport={() => {
        toast({
          title: t('crud.messages.importInfo'),
          description: t('crud.messages.importComingSoon'),
        })
      }}
      isLoading={isLoading}
    />
  )
}
