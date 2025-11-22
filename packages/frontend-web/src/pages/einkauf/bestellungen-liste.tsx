import { useState, useEffect } from 'react'
import { useNavigate } from 'react-router-dom'
import { useTranslation } from 'react-i18next'
import { ListReport } from '@/components/mask-builder'
import { useMaskActions } from '@/components/mask-builder/hooks'
import { createApiClient } from '@/components/mask-builder/utils/api'
import { formatDate, formatNumber } from '@/components/mask-builder/utils/formatting'
import { Badge } from '@/components/ui/badge'
import { ListConfig } from '@/components/mask-builder/types'
import { toast } from '@/hooks/use-toast'
import { getEntityTypeLabel, getStatusLabel } from '@/features/crud/utils/i18n-helpers'

// API Client für Bestellungen
const apiClient = createApiClient('/api/einkauf')

// Konfiguration für Bestellungen ListReport (wird in Komponente mit i18n erstellt)
const createBestellungenConfig = (t: any, entityTypeLabel: string): ListConfig => ({
  title: entityTypeLabel,
  titleKey: 'crud.list.title',
  subtitle: t('crud.subtitles.managePurchaseOrders'),
  subtitleKey: 'crud.subtitles.managePurchaseOrders',
  type: 'list-report',
  columns: [
    {
      key: 'nummer',
      label: t('crud.fields.orderNumber'),
      labelKey: 'crud.fields.orderNumber',
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
          'TEILGELIEFERT': 'secondary',
          'VOLLGELIEFERT': 'outline',
          'STORNIERT': 'destructive'
        }
        return <Badge variant={variants[value as string] || 'secondary'}>{statusLabel}</Badge>
      }
    },
    {
      key: 'liefertermin',
      label: t('crud.fields.deliveryDate'),
      labelKey: 'crud.fields.deliveryDate',
      sortable: true,
      render: (value) => formatDate(value)
    },
    {
      key: 'gesamtbetrag',
      label: t('crud.fields.totalAmount'),
      labelKey: 'crud.fields.totalAmount',
      sortable: true,
      render: (value) => `${formatNumber(value, 2)} €`
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
        { value: 'TEILGELIEFERT', label: t('status.partial'), labelKey: 'status.partial' },
        { value: 'VOLLGELIEFERT', label: t('crud.status.fullyDelivered'), labelKey: 'crud.status.fullyDelivered' },
        { value: 'STORNIERT', label: t('status.cancelled'), labelKey: 'status.cancelled' }
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
      key: 'freigeben',
      label: t('crud.actions.approve'),
      labelKey: 'crud.actions.approve',
      type: 'primary',
      onClick: () => console.log('Freigeben clicked')
    },
    {
      key: 'stornieren',
      label: t('crud.actions.cancel'),
      labelKey: 'crud.actions.cancel',
      type: 'danger',
      onClick: () => console.log('Stornieren clicked')
    },
    {
      key: 'drucken',
      label: t('crud.actions.print'),
      labelKey: 'crud.actions.print',
      type: 'secondary',
      onClick: () => console.log('Drucken clicked')
    }
  ],
  defaultSort: { field: 'createdAt', direction: 'desc' },
  pageSize: 25,
  api: {
    baseUrl: '/api/einkauf/bestellungen',
    endpoints: {
      list: '/api/einkauf/bestellungen',
      get: '/api/einkauf/bestellungen/{id}',
      create: '/api/einkauf/bestellungen',
      update: '/api/einkauf/bestellungen/{id}',
      delete: '/api/einkauf/bestellungen/{id}'
    }
  },
  permissions: ['einkauf.read', 'einkauf.write'],
  actions: []
})

export default function BestellungenListePage(): JSX.Element {
  const { t } = useTranslation()
  const navigate = useNavigate()
  const [data, setData] = useState<any[]>([])
  const [total, setTotal] = useState(0)
  const [loading, setLoading] = useState(true)
  const entityType = 'purchaseOrder'
  const entityTypeLabel = getEntityTypeLabel(t, entityType, 'Bestellung')
  const bestellungenConfig = createBestellungenConfig(t, entityTypeLabel)

  const { handleAction } = useMaskActions(async (action: string, item: any) => {
    if (action === 'edit' && item) {
      navigate(`/einkauf/bestellungen/${item.id}`)
    } else if (action === 'delete' && item) {
      if (confirm(t('crud.dialogs.delete.descriptionGeneric', { entityType: entityTypeLabel }))) {
        try {
          await apiClient.delete(`/bestellungen/${item.id}`)
          loadData() // Liste neu laden
        } catch (error) {
          toast({
            variant: 'destructive',
            title: t('crud.messages.deleteError', { entityType: entityTypeLabel })
          })
        }
      }
    } else if (action === 'freigeben' && item) {
      try {
        await apiClient.post(`/bestellungen/${item.id}/freigeben`)
        loadData()
      } catch (error) {
        toast({
          variant: 'destructive',
          title: t('crud.messages.updateError', { entityType: entityTypeLabel })
        })
      }
    }
  })

  const loadData = async () => {
    setLoading(true)
    try {
      const response = await apiClient.get('/bestellungen')
      if (response.success) {
        setData((response.data as any).data || [])
        setTotal((response.data as any).total || 0)
      }
    } catch (error) {
      console.error('Fehler beim Laden der Daten:', error)
    } finally {
      setLoading(false)
    }
  }

  useEffect(() => {
    loadData()
  }, [])

  const handleCreate = () => {
    navigate('/einkauf/bestellung-anlegen')
  }

  const handleEdit = (item: any) => {
    handleAction('edit', item)
  }

  const handleDelete = (item: any) => {
    handleAction('delete', item)
  }

  const handleExport = () => {
    try {
      // Create CSV content
      const csvHeader = 'Bestell-Nr.;Lieferant;Status;Liefertermin;Gesamtbetrag;Erstellt\n'
      const csvContent = data.map((bestellung: any) =>
        `"${bestellung.nummer}";"${bestellung.lieferant}";"${bestellung.status}";"${bestellung.liefertermin}";"${bestellung.gesamtbetrag}";"${bestellung.createdAt}"`
      ).join('\n')

      const csv = csvHeader + csvContent

      // Create and download file
      const blob = new Blob([csv], { type: 'text/csv;charset=utf-8;' })
      const link = document.createElement('a')
      const url = URL.createObjectURL(blob)
      link.setAttribute('href', url)
      link.setAttribute('download', `bestellungen-liste-${new Date().toISOString().split('T')[0]}.csv`)
      link.style.visibility = 'hidden'
      document.body.appendChild(link)
      link.click()
      document.body.removeChild(link)

      toast({
        title: t('crud.messages.exportSuccess'),
        description: t('crud.messages.exportedItems', { count: data.length, entityType: entityTypeLabel }),
      })
    } catch (error) {
      toast({
        variant: 'destructive',
        title: t('crud.messages.exportError'),
        description: t('crud.messages.exportFailed'),
      })
    }
  }

  return (
    <ListReport
      config={bestellungenConfig}
      data={data}
      total={total}
      onCreate={handleCreate}
      onEdit={handleEdit}
      onDelete={handleDelete}
      onExport={handleExport}
      onImport={() => {
        toast({
          title: 'Import-Funktion',
          description: 'CSV-Import wird in der nächsten Version verfügbar sein.',
        })
      }}
      isLoading={loading}
    />
  )
}
