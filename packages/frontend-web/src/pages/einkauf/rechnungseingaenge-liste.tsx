import { useMemo } from 'react'
import { useNavigate } from 'react-router-dom'
import { useTranslation } from 'react-i18next'
import { ListReport } from '@/components/mask-builder'
import { formatDate, formatNumber } from '@/components/mask-builder/utils/formatting'
import { Badge } from '@/components/ui/badge'
import { ListConfig } from '@/components/mask-builder/types'
import { getEntityTypeLabel, getStatusLabel } from '@/features/crud/utils/i18n-helpers'
import { toast } from '@/hooks/use-toast'
import { useRechnungseingaenge, type Rechnungseingang } from '@/lib/api/einkauf'

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
  bulkActions: [
    {
      key: 'pruefen',
      label: t('crud.actions.review'),
      labelKey: 'crud.actions.review',
      type: 'secondary',
      onClick: () => console.log('Pruefen clicked')
    },
    {
      key: 'freigeben',
      label: t('crud.actions.approve'),
      labelKey: 'crud.actions.approve',
      type: 'primary',
      onClick: () => console.log('Freigeben clicked')
    },
    {
      key: 'verbuchen',
      label: t('crud.actions.post'),
      labelKey: 'crud.actions.post',
      type: 'primary',
      onClick: () => console.log('Verbuchen clicked')
    }
  ],
  defaultSort: { field: 'createdAt', direction: 'desc' },
  pageSize: 25,
  api: {
    baseUrl: '/api/einkauf/rechnungseingaenge',
    endpoints: {
      list: '/api/einkauf/rechnungseingaenge',
      get: '/api/einkauf/rechnungseingaenge/{id}',
      create: '/api/einkauf/rechnungseingaenge',
      update: '/api/einkauf/rechnungseingaenge/{id}',
      delete: '/api/einkauf/rechnungseingaenge/{id}'
    }
  },
  permissions: ['einkauf.read', 'einkauf.write', 'finance.read'],
  actions: []
})

export default function RechnungseingaengeListePage(): JSX.Element {
  const { t } = useTranslation()
  const navigate = useNavigate()
  const { data: apiData = [], isLoading } = useRechnungseingaenge()
  const data = useMemo(() => apiData.map((item: Rechnungseingang) => ({
    ...item,
    bestellung: { nummer: item.bestellung },
    wareneingang: { nummer: item.wareneingang },
  })), [apiData])
  const total = data.length
  const entityType = 'invoiceReceipt'
  const entityTypeLabel = getEntityTypeLabel(t, entityType, 'Rechnungseingang')
  const rechnungseingaengeConfig = createRechnungseingaengeConfig(t, entityTypeLabel)

  const handleCreate = () => {
    navigate('/einkauf/rechnungseingang/neu')
  }

  const handleEdit = (item: any) => {
    if (item?.id) {
      navigate(`/einkauf/rechnungseingaenge/${item.id}`)
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
    <ListReport
      config={rechnungseingaengeConfig}
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
