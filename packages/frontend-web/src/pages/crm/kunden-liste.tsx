import { useNavigate } from 'react-router-dom'
import { useTranslation } from 'react-i18next'
import { useQuery, useQueryClient } from '@tanstack/react-query'
import { ListReport } from '@/components/mask-builder'
import { formatCurrency, formatNumber } from '@/components/mask-builder/utils/formatting'
import { Badge } from '@/components/ui/badge'
import { ListConfig } from '@/components/mask-builder/types'
import { apiClient } from '@/lib/api-client'
import { toast } from '@/hooks/use-toast'
import { getEntityTypeLabel } from '@/features/crud/utils/i18n-helpers'

// Konfiguration für Kunden ListReport (wird in Komponente mit i18n erstellt)
const createKundenListConfig = (t: any, entityTypeLabel: string): ListConfig => ({
  title: entityTypeLabel,
  titleKey: 'crud.list.title',
  subtitle: t('crud.subtitles.manageCustomers'),
  subtitleKey: 'crud.subtitles.manageCustomers',
  type: 'list-report',
  columns: [
    {
      key: 'firma',
      label: t('crud.fields.company'),
      labelKey: 'crud.fields.company',
      sortable: true,
      filterable: true,
      render: (value, row) => (
        <div>
          <div className="font-medium">{value || `${row.vorname} ${row.nachname}`}</div>
          {value && row.nachname && <div className="text-sm text-muted-foreground">{row.vorname} {row.nachname}</div>}
        </div>
      )
    },
    {
      key: 'ort',
      label: t('crud.fields.location'),
      labelKey: 'crud.fields.location',
      sortable: true,
      filterable: true,
      render: (value, row) => `${row.plz} ${value}`
    },
    {
      key: 'telefon',
      label: t('crud.fields.phone'),
      labelKey: 'crud.fields.phone',
      render: (value) => value || '-'
    },
    {
      key: 'email',
      label: t('crud.fields.email'),
      labelKey: 'crud.fields.email',
      render: (value) => value ? <a href={`mailto:${value}`} className="text-blue-600 hover:underline">{value}</a> : '-'
    },
    {
      key: 'umsatzGesamt',
      label: t('crud.fields.totalRevenue'),
      labelKey: 'crud.fields.totalRevenue',
      sortable: true,
      render: (value) => formatCurrency(value || 0)
    },
    {
      key: 'letzteBestellung',
      label: t('crud.fields.lastOrder'),
      labelKey: 'crud.fields.lastOrder',
      sortable: true,
      render: (value) => value ? new Date(value).toLocaleDateString('de-DE') : '-'
    },
    {
      key: 'bonitaet',
      label: t('crud.fields.creditRating'),
      labelKey: 'crud.fields.creditRating',
      sortable: true,
      filterable: true,
      render: (value) => {
        const colors = {
          'ausgezeichnet': 'bg-green-100 text-green-800',
          'gut': 'bg-blue-100 text-blue-800',
          'mittel': 'bg-yellow-100 text-yellow-800',
          'schlecht': 'bg-red-100 text-red-800',
          'unklar': 'bg-gray-100 text-gray-800'
        }
        return <Badge className={colors[value as keyof typeof colors] || colors.unklar}>{value}</Badge>
      }
    },
    {
      key: 'status',
      label: t('crud.fields.status'),
      labelKey: 'crud.fields.status',
      sortable: true,
      filterable: true,
      render: (value) => {
        const statusLabels = {
          'aktiv': { label: t('status.active'), variant: 'default' as const },
          'inaktiv': { label: t('status.inactive'), variant: 'secondary' as const },
          'gesperrt': { label: t('status.blocked'), variant: 'destructive' as const }
        }
        const status = statusLabels[value as keyof typeof statusLabels] || statusLabels.aktiv
        return <Badge variant={status.variant}>{status.label}</Badge>
      }
    },
    {
      key: 'kreditlimit',
      label: t('crud.fields.creditLimit'),
      labelKey: 'crud.fields.creditLimit',
      sortable: true,
      render: (value) => value ? formatCurrency(value) : '-'
    },
    {
      key: 'rabatt',
      label: t('crud.fields.discount'),
      labelKey: 'crud.fields.discount',
      sortable: true,
      render: (value) => value ? `${formatNumber(value, 1)}%` : '-'
    }
  ],
  filters: [
    {
      name: 'status',
      label: t('crud.fields.status'),
      labelKey: 'crud.fields.status',
      type: 'select',
      options: [
        { value: 'aktiv', label: t('status.active'), labelKey: 'status.active' },
        { value: 'inaktiv', label: t('status.inactive'), labelKey: 'status.inactive' },
        { value: 'gesperrt', label: t('status.blocked'), labelKey: 'status.blocked' }
      ]
    },
    {
      name: 'bonitaet',
      label: t('crud.fields.creditRating'),
      labelKey: 'crud.fields.creditRating',
      type: 'select',
      options: [
        { value: 'ausgezeichnet', label: t('crud.fields.creditRatingExcellent'), labelKey: 'crud.fields.creditRatingExcellent' },
        { value: 'gut', label: t('crud.fields.creditRatingGood'), labelKey: 'crud.fields.creditRatingGood' },
        { value: 'mittel', label: t('crud.fields.creditRatingMedium'), labelKey: 'crud.fields.creditRatingMedium' },
        { value: 'schlecht', label: t('crud.fields.creditRatingPoor'), labelKey: 'crud.fields.creditRatingPoor' },
        { value: 'unklar', label: t('crud.fields.creditRatingUnclear'), labelKey: 'crud.fields.creditRatingUnclear' }
      ]
    },
    {
      name: 'ort',
      label: t('crud.fields.location'),
      labelKey: 'crud.fields.location',
      type: 'text'
    },
    {
      name: 'umsatzGesamtMin',
      label: t('crud.fields.revenueFrom'),
      labelKey: 'crud.fields.revenueFrom',
      type: 'number',
      min: 0,
      step: 100,
      placeholder: t('crud.tooltips.placeholders.minRevenue'),
      placeholderKey: 'crud.tooltips.placeholders.minRevenue'
    },
    {
      name: 'umsatzGesamtMax',
      label: t('crud.fields.revenueTo'),
      labelKey: 'crud.fields.revenueTo',
      type: 'number',
      min: 0,
      step: 100,
      placeholder: t('crud.tooltips.placeholders.maxRevenue'),
      placeholderKey: 'crud.tooltips.placeholders.maxRevenue'
    },
    {
      name: 'letzteBestellungVon',
      label: t('crud.fields.orderDateFrom'),
      labelKey: 'crud.fields.orderDateFrom',
      type: 'date',
      maxDate: new Date().toISOString().split('T')[0]
    },
    {
      name: 'letzteBestellungBis',
      label: t('crud.fields.orderDateTo'),
      labelKey: 'crud.fields.orderDateTo',
      type: 'date',
      maxDate: new Date().toISOString().split('T')[0]
    }
  ],
  bulkActions: [
    {
      key: 'export',
      label: t('crud.actions.export'),
      labelKey: 'crud.actions.export',
      type: 'secondary',
      onClick: () => { /* Export-Funktion wird über onExport-Handler gesteuert */ }
    },
    {
      key: 'newsletter',
      label: t('crud.actions.sendNewsletter'),
      labelKey: 'crud.actions.sendNewsletter',
      type: 'secondary',
      onClick: () => { /* Newsletter-Funktion - noch nicht implementiert */ }
    },
    {
      key: 'block',
      label: t('crud.actions.block'),
      labelKey: 'crud.actions.block',
      type: 'danger',
      onClick: () => { /* Block-Funktion - noch nicht implementiert */ }
    }
  ],
  defaultSort: { field: 'firma', direction: 'asc' },
  pageSize: 25,
  api: {
    baseUrl: '/api/crm/kunden',
    endpoints: {
      list: '/api/crm/kunden',
      get: '/api/crm/kunden/{id}',
      create: '/api/crm/kunden',
      update: '/api/crm/kunden/{id}',
      delete: '/api/crm/kunden/{id}'
    }
  },
  permissions: ['crm.read', 'customer.read'],
  actions: []
})

export default function KundenListePage(): JSX.Element {
  const { t } = useTranslation()
  const navigate = useNavigate()
  const queryClient = useQueryClient()
  const entityType = 'customer'
  const entityTypeLabel = getEntityTypeLabel(t, entityType, 'Kunde')
  const kundenListConfig = createKundenListConfig(t, entityTypeLabel)

  const { data: queryData, isLoading } = useQuery({
    queryKey: ['crm', 'kunden'],
    queryFn: async () => {
      try {
        const r = await apiClient.get('/api/crm/kunden')
        if (r.data) {
          const raw = r.data as any
          const items = raw.data || (Array.isArray(raw) ? raw : [])
          const total = raw.total || items.length
          return { items, total }
        }
      } catch { /* API nicht erreichbar */ }
      return { items: [], total: 0 }
    },
    staleTime: 2 * 60 * 1000,
  })

  const data = queryData?.items || []
  const total = queryData?.total || 0

  const invalidate = () => queryClient.invalidateQueries({ queryKey: ['crm', 'kunden'] })

  const handleCreate = () => {
    navigate('/crm/kunden/stamm/new')
  }

  const handleEdit = (item: any) => {
    navigate(`/crm/kunden/stamm/${item.id}`)
  }

  const handleDelete = async (item: any) => {
    if (confirm(t('crud.dialogs.delete.descriptionGeneric', { entityType: entityTypeLabel }))) {
      try {
        await apiClient.delete(`/api/crm/kunden/${item.id}`)
        invalidate()
      } catch {
        toast({
          variant: 'destructive',
          title: t('crud.messages.deleteError', { entityType: entityTypeLabel })
        })
      }
    }
  }

  const handleExport = () => {
    try {
      const csvHeader = `${t('crud.fields.company')};${t('crud.fields.city')};${t('crud.fields.phone')};${t('crud.fields.email')};${t('crud.fields.totalRevenue')};${t('crud.fields.status')}\n`
      const csvContent = data.map((customer: any) =>
        `"${customer.firma || `${customer.vorname} ${customer.nachname}`}";"${customer.plz} ${customer.ort}";"${customer.telefon || ''}";"${customer.email || ''}";"${customer.umsatzGesamt || 0}";"${t(`status.${customer.status || 'active'}`, { defaultValue: customer.status || 'aktiv' })}"`
      ).join('\n')

      const csv = csvHeader + csvContent

      const blob = new Blob([csv], { type: 'text/csv;charset=utf-8;' })
      const link = document.createElement('a')
      const url = URL.createObjectURL(blob)
      link.setAttribute('href', url)
      link.setAttribute('download', `${t('crud.fields.customersList')}-${new Date().toISOString().split('T')[0]}.csv`)
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
      config={kundenListConfig}
      data={data}
      total={total}
      onCreate={handleCreate}
      onEdit={handleEdit}
      onDelete={handleDelete}
      onExport={handleExport}
      onImport={() => toast({ title: 'Import', description: t('crud.messages.importFunctionInfo', { defaultValue: 'Import-Funktion wird in Kürze bereitgestellt.' }) })}
      isLoading={isLoading}
    />
  )
}
