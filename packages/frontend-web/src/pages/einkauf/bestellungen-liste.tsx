import { useNavigate } from 'react-router-dom'
import { useTranslation } from 'react-i18next'
import { ListReport } from '@/components/mask-builder'
import { useMaskActions } from '@/components/mask-builder/hooks'
import { formatDate, formatNumber } from '@/components/mask-builder/utils/formatting'
import { Badge } from '@/components/ui/badge'
import { ListConfig } from '@/components/mask-builder/types'
import { toast } from '@/hooks/use-toast'
import { getEntityTypeLabel, getStatusLabel } from '@/features/crud/utils/i18n-helpers'
import { usePurchaseOrders, useApprovePurchaseOrder, useCancelPurchaseOrder, INCOTERM_OPTIONS } from '@/lib/api/purchase-orders'

// Konfiguration für Bestellungen ListReport (wird in Komponente mit i18n erstellt)
const createBestellungenConfig = (t: any, entityTypeLabel: string): ListConfig => ({
  title: entityTypeLabel,
  titleKey: 'crud.list.title',
  subtitle: t('crud.subtitles.managePurchaseOrders'),
  subtitleKey: 'crud.subtitles.managePurchaseOrders',
  type: 'list-report',
  columns: [
    {
      key: 'purchaseOrderNumber',
      label: t('crud.fields.orderNumber'),
      labelKey: 'crud.fields.orderNumber',
      sortable: true,
      render: (value) => <code className="text-sm font-mono">{value}</code>
    },
    {
      key: 'subject',
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
          'ENTWURF': 'secondary',
          'FREIGEGEBEN': 'default',
          'BESTELLT': 'default',
          'TEILGELIEFERT': 'secondary',
          'GELIEFERT': 'outline',
          'STORNIERT': 'destructive'
        }
        return <Badge variant={variants[value as string] || 'secondary'}>{statusLabel}</Badge>
      }
    },
    {
      key: 'incoterms',
      label: 'Incoterms',
      labelKey: 'crud.fields.incoterms',
      sortable: true,
      render: (value) => {
        if (!value) return <span className="text-muted-foreground">–</span>
        const option = INCOTERM_OPTIONS.find(o => o.value === value)
        return <span title={option?.label}>{value as string}</span>
      }
    },
    {
      key: 'deliveryDate',
      label: t('crud.fields.deliveryDate'),
      labelKey: 'crud.fields.deliveryDate',
      sortable: true,
      render: (value) => formatDate(value)
    },
    {
      key: 'totalAmount',
      label: t('crud.fields.totalAmount'),
      labelKey: 'crud.fields.totalAmount',
      sortable: true,
      render: (value) => `${formatNumber(value, 2)} €`
    },
    {
      key: 'externalReference',
      label: 'Ext. Referenz',
      labelKey: 'crud.fields.externalReference',
      sortable: true,
      render: (value) => value ? <span className="text-xs font-mono">{value as string}</span> : <span className="text-muted-foreground">–</span>
    },
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
        { value: 'BESTELLT', label: 'Bestellt', labelKey: 'status.ordered' },
        { value: 'TEILGELIEFERT', label: t('status.partial'), labelKey: 'status.partial' },
        { value: 'GELIEFERT', label: 'Geliefert', labelKey: 'status.delivered' },
        { value: 'STORNIERT', label: t('status.cancelled'), labelKey: 'status.cancelled' }
      ]
    },
    {
      name: 'search',
      label: t('crud.entities.supplier'),
      labelKey: 'crud.entities.supplier',
      type: 'text'
    }
  ],
  bulkActions: [
    {
      key: 'freigeben',
      label: t('crud.actions.approve'),
      labelKey: 'crud.actions.approve',
      type: 'primary',
      onClick: () => { /* Freigabe über handleAction gesteuert */ }
    },
    {
      key: 'stornieren',
      label: t('crud.actions.cancel'),
      labelKey: 'crud.actions.cancel',
      type: 'danger',
      onClick: () => { /* Storno über handleAction gesteuert */ }
    },
    {
      key: 'drucken',
      label: t('crud.actions.print'),
      labelKey: 'crud.actions.print',
      type: 'secondary',
      onClick: () => { /* Druck-Funktion - noch nicht implementiert */ }
    }
  ],
  defaultSort: { field: 'createdAt', direction: 'desc' },
  pageSize: 25,
  api: {
    baseUrl: '/api/v1/purchase-orders',
    endpoints: {
      list: '/api/v1/purchase-orders',
      get: '/api/v1/purchase-orders/{id}',
      create: '/api/v1/purchase-orders',
      update: '/api/v1/purchase-orders/{id}',
      delete: '/api/v1/purchase-orders/{id}'
    }
  },
  permissions: ['einkauf.read', 'einkauf.write'],
  actions: []
})

export default function BestellungenListePage(): JSX.Element {
  const { t } = useTranslation()
  const navigate = useNavigate()
  const entityType = 'purchaseOrder'
  const entityTypeLabel = getEntityTypeLabel(t, entityType, 'Bestellung')
  const bestellungenConfig = createBestellungenConfig(t, entityTypeLabel)

  const { data: orders, isLoading } = usePurchaseOrders()
  const approveMutation = useApprovePurchaseOrder()
  const cancelMutation = useCancelPurchaseOrder()

  const data = orders ?? []

  const { handleAction } = useMaskActions(async (action: string, item: any) => {
    if (action === 'edit' && item) {
      navigate(`/einkauf/bestellungen/${item.id}`)
    } else if (action === 'freigeben' && item) {
      try {
        await approveMutation.mutateAsync(item.id)
        toast({ title: 'Bestellung freigegeben' })
      } catch {
        toast({ variant: 'destructive', title: t('crud.messages.updateError', { entityType: entityTypeLabel }) })
      }
    } else if (action === 'stornieren' && item) {
      const reason = prompt('Stornierungsgrund:')
      if (reason) {
        try {
          await cancelMutation.mutateAsync({ id: item.id, reason })
          toast({ title: 'Bestellung storniert' })
        } catch {
          toast({ variant: 'destructive', title: t('crud.messages.updateError', { entityType: entityTypeLabel }) })
        }
      }
    }
  })

  const handleCreate = () => {
    navigate('/einkauf/bestellungen/neu')
  }

  const handleEdit = (item: any) => {
    handleAction('edit', item)
  }

  const handleExport = () => {
    try {
      const csvHeader = `Bestellnr.;Betreff;Status;Incoterms;Liefertermin;Gesamtbetrag;Ext. Referenz\n`
      const csvContent = data.map((po) =>
        `"${po.purchaseOrderNumber}";"${po.subject}";"${po.status}";"${po.incoterms ?? ''}";"${po.deliveryDate}";"${po.totalAmount}";"${po.externalReference ?? ''}"`
      ).join('\n')

      const blob = new Blob([csvHeader + csvContent], { type: 'text/csv;charset=utf-8;' })
      const link = document.createElement('a')
      const url = URL.createObjectURL(blob)
      link.setAttribute('href', url)
      link.setAttribute('download', `Bestellungen-${new Date().toISOString().split('T')[0]}.csv`)
      link.style.visibility = 'hidden'
      document.body.appendChild(link)
      link.click()
      document.body.removeChild(link)

      toast({
        title: t('crud.messages.exportSuccess'),
        description: t('crud.messages.exportedItems', { count: data.length, entityType: entityTypeLabel }),
      })
    } catch {
      toast({ variant: 'destructive', title: t('crud.messages.exportError') })
    }
  }

  return (
    <ListReport
      config={bestellungenConfig}
      data={data}
      total={data.length}
      onCreate={handleCreate}
      onEdit={handleEdit}
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


