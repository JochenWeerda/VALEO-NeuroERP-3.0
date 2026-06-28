import { useMemo } from 'react'
import { useNavigate } from '@/app/routing/typed-router'
import { useTranslation, type TFunction } from 'react-i18next'
import { useQueryClient } from '@tanstack/react-query'
import { ListReport } from '@/components/mask-builder'
import { formatDate, formatNumber } from '@/components/mask-builder/utils/formatting'
import { Badge } from '@/components/ui/badge'
import { ListConfig } from '@/components/mask-builder/types'
import { getEntityTypeLabel, getStatusLabel } from '@/features/crud/utils/i18n-helpers'
import { toast } from '@/hooks/use-toast'
import { useEinkaufAnfragen, type EinkaufAnfrage, einkaufKeys } from '@/lib/api/einkauf'
import { apiClient } from '@/lib/api-client'
import { OperationalCaseHeader } from '@/components/workflow/OperationalCaseHeader'
import { OperationalContextPanel } from '@/components/workflow/OperationalContextPanel'
import { OperationalTimeline } from '@/components/workflow/OperationalTimeline'
import { normalizeOperationalStatus } from '@/lib/operational-status'

const createAnfragenConfig = (t: TFunction, entityTypeLabel: string): ListConfig => ({
  title: entityTypeLabel,
  titleKey: 'crud.list.title',
  subtitle: t('crud.subtitles.managePurchaseRequests'),
  subtitleKey: 'crud.subtitles.managePurchaseRequests',
  type: 'list-report',
  columns: [
    {
      key: 'anfrageNummer',
      label: t('crud.fields.requestNumber'),
      labelKey: 'crud.fields.requestNumber',
      sortable: true,
      render: (value) => <code className="text-sm font-mono">{value}</code>
    },
    {
      key: 'typ',
      label: t('crud.fields.type'),
      labelKey: 'crud.fields.type',
      sortable: true,
      filterable: true,
      render: (value) => {
        const typLabels: Record<string, string> = {
          BANF: t('crud.fields.requisition'),
          ANF: t('crud.entities.purchaseRequest')
        }
        return <Badge variant="outline">{typLabels[String(value)] || String(value)}</Badge>
      }
    },
    {
      key: 'anforderer',
      label: t('crud.fields.requester'),
      labelKey: 'crud.fields.requester',
      sortable: true,
      filterable: true
    },
    {
      key: 'artikel',
      label: t('crud.fields.product'),
      labelKey: 'crud.fields.product',
      sortable: true,
      filterable: true
    },
    {
      key: 'menge',
      label: t('crud.fields.quantity'),
      labelKey: 'crud.fields.quantity',
      sortable: true,
      render: (value, item) => `${formatNumber(value, 2)} ${item.einheit || t('crud.fields.unit')}`
    },
    {
      key: 'prioritaet',
      label: t('crud.fields.priority'),
      labelKey: 'crud.fields.priority',
      sortable: true,
      filterable: true,
      render: (value) => {
        const prioLabels: Record<string, { label: string; variant: 'secondary' | 'default' | 'destructive' }> = {
          niedrig: { label: t('crud.fields.priorityLow'), variant: 'secondary' },
          normal: { label: t('crud.fields.priorityNormal'), variant: 'default' },
          hoch: { label: t('crud.fields.priorityHigh'), variant: 'destructive' },
          dringend: { label: t('crud.fields.priorityUrgent'), variant: 'destructive' }
        }
        const prio = prioLabels[String(value)] || { label: String(value), variant: 'secondary' as const }
        return <Badge variant={prio.variant}>{prio.label}</Badge>
      }
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
          ENTWURF: 'secondary',
          FREIGEGEBEN: 'default',
          ANGEBOTSPHASE: 'outline',
          BESTELLT: 'outline',
          ABGELEHNT: 'destructive',
        }
        return <Badge variant={variants[statusValue] || 'secondary'}>{statusLabel}</Badge>
      }
    },
    {
      key: 'faelligkeit',
      label: t('crud.fields.dueDate'),
      labelKey: 'crud.fields.dueDate',
      sortable: true,
      render: (value) => formatDate(value)
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
        { value: 'ENTWURF', label: t('status.draft'), labelKey: 'status.draft' },
        { value: 'FREIGEGEBEN', label: t('status.approved'), labelKey: 'status.approved' },
        { value: 'ANGEBOTSPHASE', label: t('crud.status.offerPhase'), labelKey: 'crud.status.offerPhase' },
        { value: 'BESTELLT', label: 'Bestellt' }
      ]
    },
    {
      name: 'prioritaet',
      label: t('crud.fields.priority'),
      labelKey: 'crud.fields.priority',
      type: 'select',
      options: [
        { value: 'niedrig', label: t('crud.fields.priorityLow'), labelKey: 'crud.fields.priorityLow' },
        { value: 'normal', label: t('crud.fields.priorityNormal'), labelKey: 'crud.fields.priorityNormal' },
        { value: 'hoch', label: t('crud.fields.priorityHigh'), labelKey: 'crud.fields.priorityHigh' },
        { value: 'dringend', label: t('crud.fields.priorityUrgent'), labelKey: 'crud.fields.priorityUrgent' }
      ]
    },
    {
      name: 'anforderer',
      label: t('crud.fields.requester'),
      labelKey: 'crud.fields.requester',
      type: 'text'
    },
    {
      name: 'artikel',
      label: t('crud.fields.product'),
      labelKey: 'crud.fields.product',
      type: 'text'
    }
  ],
  bulkActions: [],
  defaultSort: { field: 'createdAt', direction: 'desc' },
  pageSize: 25,
  api: {
    baseUrl: '/api/v1/einkauf/anfragen',
    endpoints: {
      list: '/api/v1/einkauf/anfragen',
      get: '/api/v1/einkauf/anfragen/{id}',
      create: '/api/v1/einkauf/anfragen',
      update: '/api/v1/einkauf/anfragen/{id}',
      delete: '/api/v1/einkauf/anfragen/{id}'
    }
  },
  permissions: ['einkauf.read', 'einkauf.write'],
  actions: []
})

async function bulkRequestMutation(
  selectedItems: Record<string, unknown>[],
  endpointSuffix: 'send' | 'convert-to-order',
  allowedStatuses: string[],
): Promise<{ ok: number; errors: string[]; createdOrderId?: string; createdOrderNumber?: string }> {
  let ok = 0
  const errors: string[] = []
  let createdOrderId: string | undefined
  let createdOrderNumber: string | undefined
  const eligible = selectedItems.filter((item) => allowedStatuses.includes(String(item.status || '').toUpperCase()))

  for (const item of eligible) {
    try {
      const response = await apiClient.post<{
        purchaseOrderId?: string
        purchaseOrderNumber?: string
      }>(`/api/v1/einkauf/anfragen/${encodeURIComponent(item.id)}/${endpointSuffix}`)
      createdOrderId = createdOrderId || response.data?.purchaseOrderId
      createdOrderNumber = createdOrderNumber || response.data?.purchaseOrderNumber
      ok += 1
    } catch (error: any) {
      errors.push(`${item.anfrageNummer || item.id}: ${error.response?.data?.detail ?? error.message}`)
    }
  }

  return { ok, errors, createdOrderId, createdOrderNumber }
}

export default function AnfragenListePage(): JSX.Element {
  const { t } = useTranslation()
  const navigate = useNavigate()
  const queryClient = useQueryClient()
  const { data: apiData = [], isLoading } = useEinkaufAnfragen()
  const data = useMemo(
    () => apiData.map((item: EinkaufAnfrage) => ({ ...item, einheit: 'Stk' })),
    [apiData]
  )
  const total = data.length
  const openCount = data.filter((item) => normalizeOperationalStatus(item.status) === 'offen').length
  const humanCount = data.filter((item) => normalizeOperationalStatus(item.status) === 'wartet_auf_mensch').length
  const reviewCount = data.filter((item) => normalizeOperationalStatus(item.status) === 'in_pruefung').length
  const externalCount = data.filter((item) => normalizeOperationalStatus(item.status) === 'wartet_auf_extern').length
  const urgentCount = data.filter((item) => item.prioritaet === 'dringend' || item.prioritaet === 'hoch').length
  const latestCreatedAt = data
    .map((item) => item.createdAt)
    .filter(Boolean)
    .sort()
    .at(-1)
  const entityType = 'purchaseRequest'
  const entityTypeLabel = getEntityTypeLabel(t, entityType, 'Anfrage')
  const baseConfig = createAnfragenConfig(t, entityTypeLabel)
  const anfragenConfig = useMemo<ListConfig>(() => ({
    ...baseConfig,
    bulkActions: [
      {
        key: 'freigeben',
        label: t('crud.actions.approve'),
        labelKey: 'crud.actions.approve',
        type: 'primary',
        onClick: async (selectedItems: Record<string, unknown>[]) => {
          const result = await bulkRequestMutation(selectedItems, 'send', ['ENTWURF', 'OFFEN'])
          queryClient.invalidateQueries({ queryKey: einkaufKeys.anfragen() })
          if (result.ok > 0) {
            toast({ title: 'Anfragen freigegeben', description: `${result.ok} Anfrage(n) in die Angebotsphase ueberfuehrt.` })
            return
          }
          toast({ variant: 'destructive', title: 'Keine freigabefaehigen Anfragen', description: result.errors[0] || 'Bitte Entwurfsanfragen markieren.' })
        }
      },
      {
        key: 'inBestellung',
        label: t('crud.actions.convertToOrder'),
        labelKey: 'crud.actions.convertToOrder',
        type: 'secondary',
        onClick: async (selectedItems: Record<string, unknown>[]) => {
          const result = await bulkRequestMutation(selectedItems, 'convert-to-order', ['FREIGEGEBEN', 'ANGEBOTSPHASE'])
          queryClient.invalidateQueries({ queryKey: einkaufKeys.anfragen() })
          if (result.ok > 0) {
            toast({
              title: 'Bestellungen erzeugt',
              description: result.createdOrderNumber
                ? `${result.ok} Bestellung(en) aus Anfragen erzeugt. Erste Bestellung: ${result.createdOrderNumber}.`
                : `${result.ok} Bestellung(en) aus Anfragen erzeugt.`,
            })
            if (result.ok === 1 && result.createdOrderId) {
              navigate(`/einkauf/bestellungen/${encodeURIComponent(result.createdOrderId)}`)
            }
            return
          }
          toast({ variant: 'destructive', title: 'Keine bestellbaren Anfragen', description: result.errors[0] || 'Bitte freigegebene Anfragen markieren.' })
        }
      }
    ],
  }), [baseConfig, navigate, queryClient, t])

  const handleCreate = () => {
    navigate('/einkauf/anfrage/neu')
  }

  const handleEdit = item => {
    if (item?.id) {
      navigate(`/einkauf/anfragen/${item.id}`)
    }
  }

  const handleDelete = async item => {
    if (!item?.id) return
    if (!confirm(t('crud.dialogs.delete.descriptionGeneric', { entityType: entityTypeLabel }))) return
    try {
      await apiClient.delete(`/api/v1/einkauf/anfragen/${item.id}`)
      toast({ title: t('crud.messages.deleteSuccess') })
      queryClient.invalidateQueries({ queryKey: einkaufKeys.anfragen() })
    } catch (e: any) {
      toast({ title: t('crud.messages.deleteError'), description: e.response?.data?.detail ?? e.message, variant: 'destructive' })
    }
  }

  const handleExport = () => {
    try {
      const csvHeader = `${t('crud.fields.requestNumber')};${t('crud.fields.requester')};${t('crud.fields.product')};${t('crud.fields.quantity')};${t('crud.fields.status')}\n`
      const csvContent = data.map(anfrage =>
        `"${anfrage.anfrageNummer}";"${anfrage.anforderer}";"${anfrage.artikel}";"${anfrage.menge}";"${anfrage.status}"`
      ).join('\n')

      const csv = csvHeader + csvContent
      const blob = new Blob([csv], { type: 'text/csv;charset=utf-8;' })
      const link = document.createElement('a')
      const url = URL.createObjectURL(blob)
      link.setAttribute('href', url)
      link.setAttribute('download', `anfragen-liste-${new Date().toISOString().split('T')[0]}.csv`)
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
    <div className="space-y-6">
      <OperationalCaseHeader
        title="Beschaffungsvorgang Anfragen"
        description="Anfragen steuern Bedarf, Angebotsphase und Folgebelege als zusammenhaengender Fall statt als lokale Listenquittung."
        status={
          urgentCount > 0
            ? 'eskaliert'
            : humanCount > 0
              ? 'wartet_auf_mensch'
              : reviewCount > 0
                ? 'in_pruefung'
                : externalCount > 0
                  ? 'wartet_auf_extern'
                  : 'offen'
        }
        owner="Einkauf / Bedarfsmeldung"
        blocker={urgentCount > 0 ? `${urgentCount} priorisierte Anfrage(n) brauchen zeitnahe Bearbeitung.` : null}
        nextAction={
          humanCount > 0
            ? `${humanCount} freigegebene Anfragen in Bestellung ueberfuehren`
            : openCount > 0
              ? `${openCount} offene Anfragen in die Angebotsphase geben`
              : 'Neue Bedarfslage aufnehmen'
        }
        caseLabel={`${total} Anfragevorgaenge`}
        tags={['Bedarf', 'Angebotsphase', 'Bestellung']}
      />

      <div className="grid gap-6 xl:grid-cols-[1.4fr_0.9fr]">
        <OperationalTimeline
          title="Fall- und Vorgangsbild"
          items={[
            latestCreatedAt
              ? {
                  label: 'Zuletzt erfasste Bedarfslage',
                  detail: `${total} Beschaffungsvorgaenge sind im Arbeitsraum sichtbar.`,
                  timestamp: latestCreatedAt,
                }
              : {
                  label: 'Noch keine Bedarfsdaten geladen',
                  detail: 'Sobald Anfragen vorhanden sind, erscheint hier die letzte Aktivitaet.',
                },
            {
              label: 'Freigabe und Angebotsphase',
              detail: `${openCount} offen, ${reviewCount} in Angebotsphase, ${humanCount} fuer Folgebeleg bereit.`,
            },
            {
              label: 'Risikobild',
              detail: urgentCount > 0 ? `${urgentCount} Anfrage(n) mit hoher oder dringender Prioritaet.` : 'Keine akut eskalierten Bedarfsvorgaenge.',
            },
          ]}
        />
        <OperationalContextPanel
          title="Kontext"
          sections={[
            {
              title: 'Ressourcenlage',
              items: [
                { label: 'Offene Bedarfsvorgaenge', value: String(openCount) },
                { label: 'Bestellreife Anfragen', value: String(humanCount) },
              ],
            },
            {
              title: 'Wirtschaftslage',
              items: [
                { label: 'Dringende Prioritaeten', value: String(urgentCount) },
                { label: 'Externe Phase', value: String(externalCount) },
              ],
            },
            {
              title: 'Governance',
              items: [
                { label: 'Naechster Schritt', value: humanCount > 0 ? 'Bestellung erzeugen' : 'Freigabe zur Angebotsphase' },
                { label: 'Owner', value: 'Einkauf / Bedarfsmeldung' },
              ],
            },
          ]}
        />
      </div>

      <ListReport
        config={anfragenConfig}
        data={data}
        total={total}
        onCreate={handleCreate}
        onEdit={handleEdit}
        onDelete={handleDelete}
        onExport={handleExport}
        onImport={() => {
          navigate('/einkauf/bestellungen?importContext=anfragen')
        }}
        isLoading={isLoading}
      />
    </div>
  )
}
