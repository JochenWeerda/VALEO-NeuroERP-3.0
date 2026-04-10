import { useMemo } from 'react'
import { useNavigate } from 'react-router-dom'
import { useTranslation } from 'react-i18next'
import { useQueryClient } from '@tanstack/react-query'
import { ListReport } from '@/components/mask-builder'
import { OperationalCaseHeader } from '@/components/workflow/OperationalCaseHeader'
import { OperationalContextPanel } from '@/components/workflow/OperationalContextPanel'
import { OperationalTimeline } from '@/components/workflow/OperationalTimeline'
import { formatDate } from '@/components/mask-builder/utils/formatting'
import { Badge } from '@/components/ui/badge'
import { ListConfig } from '@/components/mask-builder/types'
import { getEntityTypeLabel, getStatusLabel } from '@/features/crud/utils/i18n-helpers'
import { toast } from '@/hooks/use-toast'
import { useAuftragsbestaetigungen, type Auftragsbestaetigung, einkaufKeys } from '@/lib/api/einkauf'
import { apiClient } from '@/lib/api-client'
import { normalizeOperationalStatus } from '@/lib/operational-status'

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
        const statusValue = String(value || '')
        const statusLabel = getStatusLabel(t, statusValue, statusValue)
        const variants: Record<string, 'secondary' | 'default' | 'outline' | 'destructive'> = {
          OFFEN: 'secondary',
          GEPRUEFT: 'default',
          BESTAETIGT: 'outline'
        }
        return <Badge variant={variants[statusValue] || 'secondary'}>{statusLabel}</Badge>
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
  bulkActions: [],
  defaultSort: { field: 'createdAt', direction: 'desc' },
  pageSize: 25,
  api: {
    baseUrl: '/api/v1/einkauf/auftragsbestaetigungen',
    endpoints: {
      list: '/api/v1/einkauf/auftragsbestaetigungen',
      get: '/api/v1/einkauf/auftragsbestaetigungen/{id}',
      create: '/api/v1/einkauf/auftragsbestaetigungen',
      update: '/api/v1/einkauf/auftragsbestaetigungen/{id}',
      delete: '/api/v1/einkauf/auftragsbestaetigungen/{id}'
    }
  },
  permissions: ['einkauf.read', 'einkauf.write'],
  actions: []
})

async function bulkConfirmationMutation(selectedItems: any[], action: 'review' | 'confirm', allowedStatuses: string[]) {
  let ok = 0
  const errors: string[] = []
  const eligible = selectedItems.filter((item) => allowedStatuses.includes(String(item.status || '').toUpperCase()))
  for (const item of eligible) {
    try {
      await apiClient.post(`/api/v1/einkauf/auftragsbestaetigungen/${encodeURIComponent(item.id)}/${action}`)
      ok += 1
    } catch (error: any) {
      errors.push(`${item.bestaetigungsNummer || item.id}: ${error.response?.data?.detail ?? error.message}`)
    }
  }
  return { ok, errors }
}

export default function AuftragsbestaetigungenListePage(): JSX.Element {
  const { t } = useTranslation()
  const navigate = useNavigate()
  const queryClient = useQueryClient()
  const { data: apiData = [], isLoading } = useAuftragsbestaetigungen()
  const data = useMemo(() => apiData.map((item: Auftragsbestaetigung) => ({
    ...item,
    bestellung: { nummer: item.bestellung },
  })), [apiData])
  const total = data.length
  const reviewedCount = data.filter((item) => item.status === 'GEPRUEFT').length
  const confirmedCount = data.filter((item) => item.status === 'BESTAETIGT').length
  const openCount = data.filter((item) => item.status === 'OFFEN').length
  const entityType = 'orderConfirmation'
  const entityTypeLabel = getEntityTypeLabel(t, entityType, 'Auftragsbestaetigung')
  const operationalStatus = normalizeOperationalStatus(
    openCount > 0 ? 'in_pruefung' : reviewedCount > 0 ? 'wartet_auf_mensch' : confirmedCount === total && total > 0 ? 'abgeschlossen' : 'offen',
  )
  const blocker = openCount > 0 ? `${openCount} Bestaetigung(en) sind noch ungeprueft.` : null
  const contextSections = [
    {
      title: 'Bestaetigungsstand',
      items: [
        { label: 'Offen', value: `${openCount}` },
        { label: 'Geprueft', value: `${reviewedCount}` },
        { label: 'Bestaetigt', value: `${confirmedCount}` },
      ],
    },
    {
      title: 'Vorgangslage',
      items: [
        { label: 'Lieferanten', value: `${new Set(data.map((item) => item.lieferant).filter(Boolean)).size}` },
        { label: 'Bezug zu Bestellungen', value: `${data.filter((item) => item.bestellung?.nummer).length}` },
        { label: 'Naechste Bulk-Aktion', value: openCount > 0 ? 'Pruefen' : reviewedCount > 0 ? 'Bestaetigen' : 'Archivieren' },
      ],
    },
  ]
  const timelineItems = [
    {
      label: openCount > 0 ? 'Pruefrueckstand vorhanden' : 'Pruefstand stabil',
      detail: openCount > 0
        ? `${openCount} Bestaetigungen muessen noch fachlich geprueft werden.`
        : 'Alle erfassten Bestaetigungen haben mindestens einen Pruefstand erreicht.',
    },
    {
      label: confirmedCount > 0 ? 'Bestaetigungen in Folgeabwicklung' : 'Noch keine final bestaetigten Dokumente',
      detail: confirmedCount > 0
        ? `${confirmedCount} Dokumente koennen in Liefer- und Rechnungsfolge uebergehen.`
        : 'Finale Lieferfreigaben entstehen erst nach Bestaetigung.',
    },
  ]
  const baseConfig = createAuftragsbestaetigungenConfig(t, entityTypeLabel)
  const auftragsbestaetigungenConfig = useMemo<ListConfig>(() => ({
    ...baseConfig,
    bulkActions: [
      {
        key: 'pruefen',
        label: t('crud.actions.review'),
        labelKey: 'crud.actions.review',
        type: 'secondary',
        onClick: async (selectedItems: any[]) => {
          const result = await bulkConfirmationMutation(selectedItems, 'review', ['OFFEN'])
          queryClient.invalidateQueries({ queryKey: einkaufKeys.bestaetigungen() })
          if (result.ok > 0) {
            toast({ title: 'Auftragsbestaetigungen geprueft', description: `${result.ok} Auftragsbestaetigung(en) geprueft.` })
            return
          }
          toast({ variant: 'destructive', title: 'Keine pruefbaren Bestaetigungen', description: result.errors[0] || 'Bitte offene Auftragsbestaetigungen markieren.' })
        }
      },
      {
        key: 'bestaetigen',
        label: t('crud.actions.confirm'),
        labelKey: 'crud.actions.confirm',
        type: 'primary',
        onClick: async (selectedItems: any[]) => {
          const result = await bulkConfirmationMutation(selectedItems, 'confirm', ['OFFEN', 'GEPRUEFT'])
          queryClient.invalidateQueries({ queryKey: einkaufKeys.bestaetigungen() })
          if (result.ok > 0) {
            toast({ title: 'Auftragsbestaetigungen bestaetigt', description: `${result.ok} Auftragsbestaetigung(en) bestaetigt.` })
            return
          }
          toast({ variant: 'destructive', title: 'Keine bestaetigbaren Auftragsbestaetigungen', description: result.errors[0] || 'Bitte offene oder gepruefte Bestaetigungen markieren.' })
        }
      }
    ],
  }), [baseConfig, queryClient, t])

  const handleCreate = () => {
    navigate('/einkauf/auftragsbestaetigung/neu')
  }

  const handleEdit = (item: any) => {
    if (item?.id) {
      navigate(`/einkauf/auftragsbestaetigungen/${item.id}`)
    }
  }

  const handleDelete = async (item: any) => {
    if (!item?.id) return
    if (!confirm(t('crud.dialogs.delete.descriptionGeneric', { entityType: entityTypeLabel }))) return
    try {
      await apiClient.delete(`/api/v1/einkauf/auftragsbestaetigungen/${item.id}`)
      toast({ title: t('crud.messages.deleteSuccess') })
      queryClient.invalidateQueries({ queryKey: einkaufKeys.bestaetigungen() })
    } catch (e: any) {
      toast({ title: t('crud.messages.deleteError'), description: e.response?.data?.detail ?? e.message, variant: 'destructive' })
    }
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
    <div className="space-y-4">
      <OperationalCaseHeader
        title="Auftragsbestaetigungen"
        description="Bestaetigungen werden als Pruef- und Freigabevorgang mit klarer Bulk-Aktion ueber der Liste gefuehrt."
        status={operationalStatus}
        owner="Einkauf"
        blocker={blocker}
        nextAction={openCount > 0 ? 'Offene Bestaetigungen pruefen' : reviewedCount > 0 ? 'Gepruefte Bestaetigungen final bestaetigen' : 'Bestaetigte Folgewege nutzen'}
        caseLabel="Vorgang: Lieferfreigabe"
        tags={['Einkauf', 'Bestellung']}
      />
      <div className="grid gap-4 xl:grid-cols-[minmax(0,2fr)_360px]">
        <OperationalTimeline title="Pruef- und Freigabeverlauf" items={timelineItems} />
        <OperationalContextPanel title="Bestaetigungskontext" sections={contextSections} />
      </div>
      <ListReport
        config={auftragsbestaetigungenConfig}
        data={data}
        total={total}
        onCreate={handleCreate}
        onEdit={handleEdit}
        onDelete={handleDelete}
        onExport={handleExport}
        onImport={() => {
          navigate('/einkauf/bestellungen?importContext=auftragsbestaetigungen')
        }}
        isLoading={isLoading}
      />
    </div>
  )
}
