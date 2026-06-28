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
import { useEinkaufAngebote, type EinkaufAngebot, einkaufKeys } from '@/lib/api/einkauf'
import { apiClient } from '@/lib/api-client'
import { OperationalCaseHeader } from '@/components/workflow/OperationalCaseHeader'
import { OperationalContextPanel } from '@/components/workflow/OperationalContextPanel'
import { OperationalTimeline } from '@/components/workflow/OperationalTimeline'
import { normalizeOperationalStatus } from '@/lib/operational-status'

const createAngeboteConfig = (t: TFunction, entityTypeLabel: string): ListConfig => ({
  title: entityTypeLabel,
  titleKey: 'crud.list.title',
  subtitle: t('crud.subtitles.managePurchaseOffers'),
  subtitleKey: 'crud.subtitles.managePurchaseOffers',
  type: 'list-report',
  columns: [
    {
      key: 'angebotNummer',
      label: t('crud.fields.offerNumber'),
      labelKey: 'crud.fields.offerNumber',
      sortable: true,
      render: (value) => <code className="text-sm font-mono">{value}</code>
    },
    {
      key: 'anfrage',
      label: t('crud.entities.purchaseRequest'),
      labelKey: 'crud.entities.purchaseRequest',
      sortable: true,
      render: (value) => value?.anfrageNummer || '-'
    },
    {
      key: 'lieferant',
      label: t('crud.entities.supplier'),
      labelKey: 'crud.entities.supplier',
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
      key: 'preis',
      label: t('crud.fields.price'),
      labelKey: 'crud.fields.price',
      sortable: true,
      render: (value, item) => `${formatNumber(value, 2)} EUR/${item.einheit || t('crud.fields.unit')}`
    },
    {
      key: 'gueltigBis',
      label: t('crud.fields.validUntil'),
      labelKey: 'crud.fields.validUntil',
      sortable: true,
      render: (value) => formatDate(value)
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
          ERFASST: 'secondary',
          GEPRUEFT: 'default',
          GENEHMIGT: 'outline',
          IN_BESTELLUNG: 'outline',
          ABGELEHNT: 'destructive'
        }
        return <Badge variant={variants[statusValue] || 'secondary'}>{statusLabel}</Badge>
      }
    },
    {
      key: 'lieferzeit',
      label: t('crud.fields.deliveryTime'),
      labelKey: 'crud.fields.deliveryTime',
      sortable: true,
      render: (value) => {
        if (typeof value === 'number') {
          return `${value} ${t('crud.fields.days')}`
        }
        return value || '-'
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
        { value: 'ERFASST', label: t('status.recorded'), labelKey: 'status.recorded' },
        { value: 'GEPRUEFT', label: t('status.reviewed'), labelKey: 'status.reviewed' },
        { value: 'GENEHMIGT', label: t('status.approved'), labelKey: 'status.approved' },
        { value: 'IN_BESTELLUNG', label: 'In Bestellung' },
        { value: 'ABGELEHNT', label: t('status.rejected'), labelKey: 'status.rejected' }
      ]
    },
    {
      name: 'lieferant',
      label: t('crud.entities.supplier'),
      labelKey: 'crud.entities.supplier',
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
    baseUrl: '/api/v1/einkauf/angebote',
    endpoints: {
      list: '/api/v1/einkauf/angebote',
      get: '/api/v1/einkauf/angebote/{id}',
      create: '/api/v1/einkauf/angebote',
      update: '/api/v1/einkauf/angebote/{id}',
      delete: '/api/v1/einkauf/angebote/{id}'
    }
  },
  permissions: ['einkauf.read', 'einkauf.write'],
  actions: []
})

async function bulkOfferMutation(
  selectedItems: Record<string, unknown>[],
  endpointSuffix: 'review' | 'approve' | 'reject' | 'convert-to-order',
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
      }>(`/api/v1/einkauf/angebote/${encodeURIComponent(item.id)}/${endpointSuffix}`)
      createdOrderId = createdOrderId || response.data?.purchaseOrderId
      createdOrderNumber = createdOrderNumber || response.data?.purchaseOrderNumber
      ok += 1
    } catch (_rawErr: unknown) {
      const error = _rawErr as { response?: { data?: { detail?: string } }; message?: string; name?: string }
      errors.push(`${String(item.angebotNummer ?? item.id ?? '')}: ${error.response?.data?.detail ?? error.message}`)
    }
  }

  return { ok, errors, createdOrderId, createdOrderNumber }
}

export default function AngeboteListePage(): JSX.Element {
  const { t } = useTranslation()
  const navigate = useNavigate()
  const queryClient = useQueryClient()
  const { data: apiData = [], isLoading } = useEinkaufAngebote()
  const data = useMemo(() => apiData.map((item: EinkaufAngebot) => ({
    ...item,
    anfrage: { anfrageNummer: item.anfrage },
    einheit: 'Stk',
  })), [apiData])
  const total = data.length
  const approvedCount = data.filter((item) => normalizeOperationalStatus(item.status) === 'wartet_auf_mensch').length
  const externalCount = data.filter((item) => normalizeOperationalStatus(item.status) === 'wartet_auf_extern').length
  const blockedCount = data.filter((item) => normalizeOperationalStatus(item.status) === 'blockiert').length
  const reviewedCount = data.filter((item) => normalizeOperationalStatus(item.status) === 'in_pruefung').length
  const latestCreatedAt = data
    .map((item) => item.createdAt)
    .filter(Boolean)
    .sort()
    .at(-1)
  const entityType = 'purchaseOffer'
  const entityTypeLabel = getEntityTypeLabel(t, entityType, 'Angebot')
  const baseConfig = createAngeboteConfig(t, entityTypeLabel)
  const angeboteConfig = useMemo<ListConfig>(() => ({
    ...baseConfig,
    bulkActions: [
      {
        key: 'pruefen',
        label: t('crud.actions.review'),
        labelKey: 'crud.actions.review',
        type: 'secondary',
        onClick: async (selectedItems: Record<string, unknown>[]) => {
          const result = await bulkOfferMutation(selectedItems, 'review', ['ERFASST', 'OFFEN', 'ENTWURF'])
          queryClient.invalidateQueries({ queryKey: einkaufKeys.angebote() })
          if (result.ok > 0) {
            toast({ title: 'Angebote geprueft', description: `${result.ok} Angebot(e) auf GEPRUEFT gesetzt.` })
            return
          }
          toast({ variant: 'destructive', title: 'Keine pruefbaren Angebote', description: result.errors[0] || 'Bitte Angebote im Status Erfasst/Entwurf markieren.' })
        }
      },
      {
        key: 'genehmigen',
        label: t('crud.actions.approve'),
        labelKey: 'crud.actions.approve',
        type: 'primary',
        onClick: async (selectedItems: Record<string, unknown>[]) => {
          const result = await bulkOfferMutation(selectedItems, 'approve', ['GEPRUEFT', 'GENEHMIGT'])
          queryClient.invalidateQueries({ queryKey: einkaufKeys.angebote() })
          if (result.ok > 0) {
            toast({ title: 'Angebote genehmigt', description: `${result.ok} Angebot(e) freigegeben.` })
            return
          }
          toast({ variant: 'destructive', title: 'Keine genehmigbaren Angebote', description: result.errors[0] || 'Bitte gepruefte Angebote markieren.' })
        }
      },
      {
        key: 'ablehnen',
        label: t('crud.actions.reject'),
        labelKey: 'crud.actions.reject',
        type: 'danger',
        onClick: async (selectedItems: Record<string, unknown>[]) => {
          const result = await bulkOfferMutation(selectedItems, 'reject', ['ERFASST', 'GEPRUEFT', 'GENEHMIGT', 'OFFEN'])
          queryClient.invalidateQueries({ queryKey: einkaufKeys.angebote() })
          if (result.ok > 0) {
            toast({ title: 'Angebote abgelehnt', description: `${result.ok} Angebot(e) auf ABGELEHNT gesetzt.`, variant: 'destructive' })
            return
          }
          toast({ variant: 'destructive', title: 'Keine ablehnbaren Angebote', description: result.errors[0] || 'Bitte offene oder gepruefte Angebote markieren.' })
        }
      },
      {
        key: 'inBestellung',
        label: t('crud.actions.convertToOrder'),
        labelKey: 'crud.actions.convertToOrder',
        type: 'secondary',
        onClick: async (selectedItems: Record<string, unknown>[]) => {
          const result = await bulkOfferMutation(selectedItems, 'convert-to-order', ['GEPRUEFT', 'GENEHMIGT'])
          queryClient.invalidateQueries({ queryKey: einkaufKeys.angebote() })
          if (result.ok > 0) {
            toast({
              title: 'Bestellungen erzeugt',
              description: result.createdOrderNumber
                ? `${result.ok} Bestellung(en) erzeugt. Erste Bestellung: ${result.createdOrderNumber}.`
                : `${result.ok} Bestellung(en) erzeugt.`,
            })
            if (result.ok === 1 && result.createdOrderId) {
              navigate(`/einkauf/bestellungen/${encodeURIComponent(result.createdOrderId)}`)
            }
            return
          }
          toast({ variant: 'destructive', title: 'Keine bestellbaren Angebote', description: result.errors[0] || 'Bitte gepruefte oder genehmigte Angebote markieren.' })
        }
      }
    ],
  }), [baseConfig, navigate, queryClient, t])

  const handleCreate = () => {
    navigate('/einkauf/angebot/neu')
  }

  const handleEdit = item => {
    if (item?.id) {
      navigate(`/einkauf/angebote/${item.id}`)
    }
  }

  const handleDelete = async item => {
    if (!item?.id) return
    if (!confirm(t('crud.dialogs.delete.descriptionGeneric', { entityType: entityTypeLabel }))) return
    try {
      await apiClient.delete(`/api/v1/einkauf/angebote/${item.id}`)
      toast({ title: t('crud.messages.deleteSuccess') })
      queryClient.invalidateQueries({ queryKey: einkaufKeys.angebote() })
    } catch (_rawErr: unknown) {
      const e = _rawErr as { response?: { data?: { detail?: string } }; message?: string; name?: string }
      toast({ title: t('crud.messages.deleteError'), description: e.response?.data?.detail ?? e.message, variant: 'destructive' })
    }
  }

  const handleExport = () => {
    try {
      const csvHeader = `${t('crud.fields.offerNumber')};${t('crud.entities.supplier')};${t('crud.fields.product')};${t('crud.fields.price')};${t('crud.fields.status')}\n`
      const csvContent = data.map(angebot =>
        `"${angebot.angebotNummer}";"${angebot.lieferant}";"${angebot.artikel}";"${angebot.preis}";"${angebot.status}"`
      ).join('\n')

      const csv = csvHeader + csvContent
      const blob = new Blob([csv], { type: 'text/csv;charset=utf-8;' })
      const link = document.createElement('a')
      const url = URL.createObjectURL(blob)
      link.setAttribute('href', url)
      link.setAttribute('download', `angebote-liste-${new Date().toISOString().split('T')[0]}.csv`)
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
        title="Einkaufsvorgang Angebote"
        description="Angebote werden nicht mehr nur gesammelt quittiert, sondern als operativer Vorgangsraum mit Review-, Freigabe- und Folgebeleglage gefuehrt."
        status={
          blockedCount > 0
            ? 'eskaliert'
            : approvedCount > 0
              ? 'wartet_auf_mensch'
              : reviewedCount > 0
                ? 'in_pruefung'
                : externalCount > 0
                  ? 'wartet_auf_extern'
                  : 'offen'
        }
        owner="Einkauf / Lieferantenmanagement"
        blocker={blockedCount > 0 ? `${blockedCount} Angebot(e) sind blockiert oder abgelehnt und brauchen Nachsteuerung.` : null}
        nextAction={
          approvedCount > 0
            ? `${approvedCount} freigabereife Angebote in Bestellung ueberfuehren`
            : reviewedCount > 0
              ? `${reviewedCount} gepruefte Angebote genehmigen`
              : 'Neue Angebote erfassen oder bestehende Vorgangsbelege nachziehen'
        }
        caseLabel={`${total} Angebotsvorgaenge`}
        tags={['Vorgang', 'Preisvergleich', 'Folgebeleg']}
      />

      <div className="grid gap-6 xl:grid-cols-[1.4fr_0.9fr]">
        <OperationalTimeline
          title="Vorgangstimeline"
          items={[
            latestCreatedAt
              ? {
                  label: 'Zuletzt erfasste Angebotslage aktualisiert',
                  detail: `${total} Angebote stehen im aktuellen Arbeitsraum.`,
                  timestamp: latestCreatedAt,
                }
              : {
                  label: 'Noch keine Angebotslage geladen',
                  detail: 'Sobald Angebote vorliegen, erscheint hier die zuletzt erkannte Aktivitaet.',
                },
            {
              label: 'Review-Fokus',
              detail: `${reviewedCount} Vorgaenge stehen in Pruefung; ${approvedCount} warten auf menschliche Freigabe.`,
            },
            {
              label: 'Risikobild',
              detail: blockedCount > 0 ? `${blockedCount} blockierte oder abgelehnte Angebote belasten den Folgeprozess.` : 'Aktuell kein akuter Angebotsblocker.',
            },
          ]}
        />
        <OperationalContextPanel
          title="Kontext"
          sections={[
            {
              title: 'Ressourcenlage',
              items: [
                { label: 'Geprueft', value: String(reviewedCount) },
                { label: 'In Bestellung', value: String(externalCount) },
              ],
            },
            {
              title: 'Wirtschaftslage',
              items: [
                { label: 'Angebote gesamt', value: String(total) },
                { label: 'Freigabereif', value: String(approvedCount) },
              ],
            },
            {
              title: 'Governance',
              items: [
                { label: 'Blockiert/abgelehnt', value: String(blockedCount) },
                { label: 'Naechster Schritt', value: approvedCount > 0 ? 'Folgebeleg erzeugen' : 'Review abschliessen' },
              ],
            },
          ]}
        />
      </div>

      <ListReport
        config={angeboteConfig}
        data={data}
        total={total}
        onCreate={handleCreate}
        onEdit={handleEdit}
        onDelete={handleDelete}
        onExport={handleExport}
        onImport={() => {
          navigate('/einkauf/bestellungen?importContext=angebote')
        }}
        isLoading={isLoading}
      />
    </div>
  )
}
