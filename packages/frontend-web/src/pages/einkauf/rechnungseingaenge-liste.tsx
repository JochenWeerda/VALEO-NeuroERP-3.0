import { useMemo } from 'react'
import { useNavigate } from 'react-router-dom'
import { useTranslation } from 'react-i18next'
import { useQueryClient } from '@tanstack/react-query'
import { ListReport } from '@/components/mask-builder'
import { formatDate, formatNumber } from '@/components/mask-builder/utils/formatting'
import { Badge } from '@/components/ui/badge'
import { ListConfig } from '@/components/mask-builder/types'
import { getEntityTypeLabel, getStatusLabel } from '@/features/crud/utils/i18n-helpers'
import { toast } from '@/hooks/use-toast'
import { apiClient } from '@/lib/api-client'
import { useRechnungseingaenge, type Rechnungseingang, einkaufKeys } from '@/lib/api/einkauf'
import { OperationalCaseHeader } from '@/components/workflow/OperationalCaseHeader'
import { OperationalContextPanel } from '@/components/workflow/OperationalContextPanel'
import { OperationalTimeline } from '@/components/workflow/OperationalTimeline'
import { normalizeOperationalStatus } from '@/lib/operational-status'

const createRechnungseingaengeConfig = (t: any, entityTypeLabel: string): ListConfig => ({
  title: entityTypeLabel,
  titleKey: 'crud.list.title',
  subtitle: t('crud.subtitles.manageInvoiceReceipts'),
  subtitleKey: 'crud.subtitles.manageInvoiceReceipts',
  type: 'list-report',
  columns: [
    {
      key: 'rechnungsNummer',
      label: t('crud.fields.invoiceNumber'),
      labelKey: 'crud.fields.invoiceNumber',
      sortable: true,
      render: (value) => <code className="text-sm font-mono">{value}</code>
    },
    {
      key: 'lieferant',
      label: t('crud.entities.supplier'),
      labelKey: 'crud.entities.supplier',
      sortable: true,
      filterable: true
    },
    {
      key: 'bestellung',
      label: t('crud.entities.purchaseOrder'),
      labelKey: 'crud.entities.purchaseOrder',
      sortable: true,
      render: (value) => value?.nummer || '-'
    },
    {
      key: 'wareneingang',
      label: t('crud.fields.goodsReceipt'),
      labelKey: 'crud.fields.goodsReceipt',
      sortable: true,
      render: (value) => value?.nummer || '-'
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
          ERFASST: 'secondary',
          GEPRUEFT: 'default',
          FREIGEGEBEN: 'outline',
          VERBUCHT: 'outline',
          BEZAHLT: 'outline'
        }
        return <Badge variant={variants[value as string] || 'secondary'}>{statusLabel}</Badge>
      }
    },
    {
      key: 'bruttoBetrag',
      label: `${t('crud.fields.grossAmount')} (EUR)`,
      labelKey: 'crud.fields.grossAmount',
      sortable: true,
      render: (value) => `${formatNumber(value, 2)} EUR`
    },
    {
      key: 'rechnungsDatum',
      label: t('crud.fields.invoiceDate'),
      labelKey: 'crud.fields.invoiceDate',
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
        { value: 'ERFASST', label: t('status.recorded'), labelKey: 'status.recorded' },
        { value: 'GEPRUEFT', label: t('status.reviewed'), labelKey: 'status.reviewed' },
        { value: 'FREIGEGEBEN', label: t('status.approved'), labelKey: 'status.approved' },
        { value: 'VERBUCHT', label: t('status.posted'), labelKey: 'status.posted' },
        { value: 'BEZAHLT', label: t('status.paid'), labelKey: 'status.paid' }
      ]
    },
    {
      name: 'lieferant',
      label: t('crud.entities.supplier'),
      labelKey: 'crud.entities.supplier',
      type: 'text'
    }
  ],
  bulkActions: [], // set in component with API calls
  defaultSort: { field: 'createdAt', direction: 'desc' },
  pageSize: 25,
  api: {
    baseUrl: '/api/v1/einkauf/rechnungseingaenge',
    endpoints: {
      list: '/api/v1/einkauf/rechnungseingaenge',
      get: '/api/v1/einkauf/rechnungseingaenge/{id}',
      create: '/api/v1/einkauf/rechnungseingaenge',
      update: '/api/v1/einkauf/rechnungseingaenge/{id}',
      delete: '/api/v1/einkauf/rechnungseingaenge/{id}'
    }
  },
  permissions: ['einkauf.read', 'einkauf.write', 'finance.read'],
  actions: []
})

const ENTWURF_STATUSES = ['ENTWURF', 'ERFASST', 'OFFEN']

async function bulkWorkflow(
  selectedItems: Array<{ id: string; status?: string }>,
  endpointSuffix: 'pruefen' | 'freigeben' | 'verbuchen',
  allowedStatuses: string[],
): Promise<{ ok: number; err: number; messages: string[] }> {
  const base = '/api/v1/einkauf/rechnungseingaenge'
  let ok = 0
  let err = 0
  const messages: string[] = []
  const toProcess = selectedItems.filter((item) =>
    allowedStatuses.includes((item.status || '').toUpperCase()),
  )
  for (const item of toProcess) {
    try {
      await apiClient.post(`${base}/${encodeURIComponent(item.id)}/${endpointSuffix}`)
      ok += 1
    } catch (e: any) {
      err += 1
      messages.push(
        (item as any).rechnungsNummer || item.id
          ? `${(item as any).rechnungsNummer || item.id}: ${e?.response?.data?.detail || e?.message}`
          : e?.response?.data?.detail || e?.message,
      )
    }
  }
  return { ok, err, messages }
}

export default function RechnungseingaengeListePage(): JSX.Element {
  const { t } = useTranslation()
  const navigate = useNavigate()
  const queryClient = useQueryClient()
  const { data: apiData = [], isLoading } = useRechnungseingaenge()
  const data = useMemo(() => apiData.map((item: Rechnungseingang) => ({
    ...item,
    bestellung: { nummer: item.bestellung },
    wareneingang: { nummer: item.wareneingang },
  })), [apiData])
  const reviewedCount = data.filter((item) => String(item.status || '').toUpperCase() === 'GEPRUEFT').length
  const approvedCount = data.filter((item) => String(item.status || '').toUpperCase() === 'FREIGEGEBEN').length
  const draftCount = data.filter((item) => ENTWURF_STATUSES.includes(String(item.status || '').toUpperCase())).length
  const totalAmount = data.reduce((sum, item) => sum + Number(item.bruttoBetrag || 0), 0)
  const total = data.length
  const entityType = 'invoiceReceipt'
  const entityTypeLabel = getEntityTypeLabel(t, entityType, 'Rechnungseingang')
  const baseConfig = createRechnungseingaengeConfig(t, entityTypeLabel)
  const operationalStatus = normalizeOperationalStatus(
    approvedCount > 0
      ? 'wartet_auf_mensch'
      : reviewedCount > 0
        ? 'in_pruefung'
        : draftCount > 0
          ? 'offen'
          : 'abgeschlossen',
  )
  const blocker = approvedCount > 0
    ? `${approvedCount} Rechnungseingaenge warten auf Verbuchung.`
    : reviewedCount > 0
      ? `${reviewedCount} Rechnungseingaenge warten auf Freigabe.`
      : null
  const contextSections = [
    {
      title: 'Workflowdruck',
      items: [
        { label: 'Erfasst/Entwurf', value: `${draftCount}` },
        { label: 'Geprueft', value: `${reviewedCount}` },
        { label: 'Freigegeben', value: `${approvedCount}` },
      ],
    },
    {
      title: 'Wirtschaft',
      items: [
        { label: 'Gesamtbetrag', value: `${formatNumber(totalAmount, 2)} EUR` },
        { label: 'Anzahl', value: `${total}` },
        { label: 'Naechster Hebel', value: approvedCount > 0 ? 'Verbuchen' : reviewedCount > 0 ? 'Freigeben' : 'Pruefen' },
      ],
    },
  ]
  const timelineItems = [
    { label: 'Sammelarbeitsplatz geladen', detail: `${total} Rechnungseingaenge in der aktuellen Sicht.` },
    ...(approvedCount > 0 ? [{ label: 'Verbuchungsstau', detail: `${approvedCount} Positionen koennen jetzt gepostet werden.` }] : []),
    ...(reviewedCount > 0 ? [{ label: 'Freigabestau', detail: `${reviewedCount} Positionen stehen zur Freigabe.` }] : []),
  ]

  const rechnungseingaengeConfig: ListConfig = useMemo(() => ({
    ...baseConfig,
    bulkActions: [
      {
        key: 'pruefen',
        label: t('crud.actions.review'),
        labelKey: 'crud.actions.review',
        type: 'secondary',
        onClick: async (selectedItems: any[]) => {
          const { ok, err, messages } = await bulkWorkflow(
            selectedItems,
            'pruefen',
            ENTWURF_STATUSES,
          )
          queryClient.invalidateQueries({ queryKey: einkaufKeys.rechnungseingaenge() })
          if (err === 0 && ok > 0) {
            toast({ title: t('crud.messages.success'), description: `${t('status.reviewed')  } (${ok})` })
          } else if (ok > 0) {
            toast({ title: t('status.reviewed'), description: `${ok} OK, ${err} Fehler. ${messages.slice(0, 2).join(' ')}` })
          } else if (messages.length) {
            toast({ variant: 'destructive', title: t('crud.messages.error'), description: messages.slice(0, 2).join(' ') })
          } else if (selectedItems.length === 0) {
            toast({ variant: 'destructive', title: t('crud.messages.noSelection'), description: t('crud.messages.selectAtLeastOne') })
          } else {
            toast({ variant: 'destructive', title: t('crud.messages.error'), description: 'Keine Rechnungseingaenge im Status Erfasst/Entwurf/Offen.' })
          }
        },
      },
      {
        key: 'freigeben',
        label: t('crud.actions.approve'),
        labelKey: 'crud.actions.approve',
        type: 'primary',
        onClick: async (selectedItems: any[]) => {
          const { ok, err, messages } = await bulkWorkflow(
            selectedItems,
            'freigeben',
            ['GEPRUEFT'],
          )
          queryClient.invalidateQueries({ queryKey: einkaufKeys.rechnungseingaenge() })
          if (err === 0 && ok > 0) {
            toast({ title: t('crud.messages.success'), description: `${t('status.approved')  } (${ok})` })
          } else if (ok > 0) {
            toast({ title: t('status.approved'), description: `${ok} OK, ${err} Fehler. ${messages.slice(0, 2).join(' ')}` })
          } else if (messages.length) {
            toast({ variant: 'destructive', title: t('crud.messages.error'), description: messages.slice(0, 2).join(' ') })
          } else if (selectedItems.length === 0) {
            toast({ variant: 'destructive', title: t('crud.messages.noSelection'), description: t('crud.messages.selectAtLeastOne') })
          } else {
            toast({ variant: 'destructive', title: t('crud.messages.error'), description: 'Keine Rechnungseingaenge im Status Geprüft.' })
          }
        },
      },
      {
        key: 'verbuchen',
        label: t('crud.actions.post'),
        labelKey: 'crud.actions.post',
        type: 'primary',
        onClick: async (selectedItems: any[]) => {
          const { ok, err, messages } = await bulkWorkflow(
            selectedItems,
            'verbuchen',
            ['FREIGEGEBEN'],
          )
          queryClient.invalidateQueries({ queryKey: einkaufKeys.rechnungseingaenge() })
          if (err === 0 && ok > 0) {
            toast({ title: t('crud.messages.success'), description: `${t('status.posted')  } (${ok})` })
          } else if (ok > 0) {
            toast({ title: t('status.posted'), description: `${ok} OK, ${err} Fehler. ${messages.slice(0, 2).join(' ')}` })
          } else if (messages.length) {
            toast({ variant: 'destructive', title: t('crud.messages.error'), description: messages.slice(0, 2).join(' ') })
          } else if (selectedItems.length === 0) {
            toast({ variant: 'destructive', title: t('crud.messages.noSelection'), description: t('crud.messages.selectAtLeastOne') })
          } else {
            toast({ variant: 'destructive', title: t('crud.messages.error'), description: 'Keine Rechnungseingaenge im Status Freigegeben.' })
          }
        },
      },
    ],
  }), [baseConfig, t, queryClient])

  const handleCreate = () => {
    navigate('/einkauf/rechnungseingang/neu')
  }

  const handleEdit = (item: any) => {
    if (item?.id) {
      navigate(`/einkauf/rechnungseingaenge/${item.id}`)
    }
  }

  const handleDelete = async (item: any) => {
    if (!item?.id) return
    if (!confirm(t('crud.dialogs.delete.descriptionGeneric', { entityType: entityTypeLabel }))) return
    try {
      await apiClient.delete(`/api/v1/einkauf/rechnungen/${item.id}`)
      toast({ title: t('crud.messages.deleteSuccess') })
      queryClient.invalidateQueries({ queryKey: einkaufKeys.rechnungseingaenge() })
    } catch (e: any) {
      toast({ title: t('crud.messages.deleteError'), description: e.response?.data?.detail ?? e.message, variant: 'destructive' })
    }
  }

  const handleExport = () => {
    try {
      const csvHeader = `${t('crud.fields.invoiceNumber')};${t('crud.entities.supplier')};${t('crud.fields.grossAmount')};${t('crud.fields.status')}\n`
      const csvContent = data.map((rechnung: any) =>
        `"${rechnung.rechnungsNummer}";"${rechnung.lieferant}";"${rechnung.bruttoBetrag}";"${rechnung.status}"`
      ).join('\n')

      const csv = csvHeader + csvContent
      const blob = new Blob([csv], { type: 'text/csv;charset=utf-8;' })
      const link = document.createElement('a')
      const url = URL.createObjectURL(blob)
      link.setAttribute('href', url)
      link.setAttribute('download', `rechnungseingaenge-liste-${new Date().toISOString().split('T')[0]}.csv`)
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
        title="Rechnungseingaenge steuern"
        description="Die Liste bleibt schlank, zeigt aber direkt den Freigabe- und Verbuchungsdruck der aktuellen Sicht."
        status={operationalStatus}
        owner="Einkauf / FIBU"
        blocker={blocker}
        nextAction={approvedCount > 0 ? 'Freigegebene Eingaenge verbuchen' : reviewedCount > 0 ? 'Gepruefte Eingaenge freigeben' : 'Neue Eingaenge pruefen'}
        caseLabel="Sammelarbeitsplatz"
        tags={['Einkauf', 'FIBU']}
      />
      <div className="grid gap-4 lg:grid-cols-[1.35fr_1fr]">
        <OperationalTimeline title="Aktuelle Lage" items={timelineItems} />
        <OperationalContextPanel title="Listenkontext" sections={contextSections} />
      </div>
      <ListReport
        config={rechnungseingaengeConfig}
        data={data}
        total={total}
        onCreate={handleCreate}
        onEdit={handleEdit}
        onDelete={handleDelete}
        onExport={handleExport}
        onImport={() => {
          navigate('/einkauf/bestellungen?importContext=rechnungseingaenge')
        }}
        isLoading={isLoading}
      />
    </div>
  )
}
