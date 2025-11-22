import { useState, useEffect } from 'react'
import { useNavigate } from 'react-router-dom'
import { useTranslation } from 'react-i18next'
import { ListReport } from '@/components/mask-builder'
import { useMaskActions } from '@/components/mask-builder/hooks'
import { createApiClient } from '@/components/mask-builder/utils/api'
import { formatDate, formatNumber } from '@/components/mask-builder/utils/formatting'
import { Badge } from '@/components/ui/badge'
import { ListConfig } from '@/components/mask-builder/types'
import { getEntityTypeLabel, getStatusLabel } from '@/features/crud/utils/i18n-helpers'
import { toast } from '@/hooks/use-toast'

// API Client für Angebote
const apiClient = createApiClient('/api/einkauf')

// Konfiguration für Angebote ListReport (wird in Komponente mit i18n erstellt)
const createAngeboteConfig = (t: any, entityTypeLabel: string): ListConfig => ({
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
      render: (value, item) => `${formatNumber(value, 2)} €/${item.einheit || t('crud.fields.unit')}`
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
        const statusLabel = getStatusLabel(t, value as string, value as string)
        const variants: Record<string, 'secondary' | 'default' | 'outline' | 'destructive'> = {
          'ERFASST': 'secondary',
          'GEPRUEFT': 'default',
          'GENEHMIGT': 'outline',
          'ABGELEHNT': 'destructive'
        }
        return <Badge variant={variants[value as string] || 'secondary'}>{statusLabel}</Badge>
      }
    },
    {
      key: 'lieferzeit',
      label: t('crud.fields.deliveryTime'),
      labelKey: 'crud.fields.deliveryTime',
      sortable: true,
      render: (value) => `${value} ${t('crud.fields.days')}`
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
  bulkActions: [
    {
      key: 'pruefen',
      label: t('crud.actions.review'),
      labelKey: 'crud.actions.review',
      type: 'secondary',
      onClick: () => console.log('Prüfen clicked')
    },
    {
      key: 'genehmigen',
      label: t('crud.actions.approve'),
      labelKey: 'crud.actions.approve',
      type: 'primary',
      onClick: () => console.log('Genehmigen clicked')
    },
    {
      key: 'ablehnen',
      label: t('crud.actions.reject'),
      labelKey: 'crud.actions.reject',
      type: 'danger',
      onClick: () => console.log('Ablehnen clicked')
    },
    {
      key: 'inBestellung',
      label: t('crud.actions.convertToOrder'),
      labelKey: 'crud.actions.convertToOrder',
      type: 'secondary',
      onClick: () => console.log('In Bestellung clicked')
    }
  ],
  defaultSort: { field: 'createdAt', direction: 'desc' },
  pageSize: 25,
  api: {
    baseUrl: '/api/einkauf/angebote',
    endpoints: {
      list: '/api/einkauf/angebote',
      get: '/api/einkauf/angebote/{id}',
      create: '/api/einkauf/angebote',
      update: '/api/einkauf/angebote/{id}',
      delete: '/api/einkauf/angebote/{id}'
    }
  },
  permissions: ['einkauf.read', 'einkauf.write'],
  actions: []
})

export default function AngeboteListePage(): JSX.Element {
  const { t } = useTranslation()
  const navigate = useNavigate()
  const [data, setData] = useState<any[]>([])
  const [total, setTotal] = useState(0)
  const [loading, setLoading] = useState(true)
  const entityType = 'purchaseOffer'
  const entityTypeLabel = getEntityTypeLabel(t, entityType, 'Angebot')
  const angeboteConfig = createAngeboteConfig(t, entityTypeLabel)

  const { handleAction } = useMaskActions(async (action: string, item: any) => {
    if (action === 'edit' && item) {
      navigate(`/einkauf/angebote/${item.id}`)
    } else if (action === 'delete' && item) {
      if (confirm(t('crud.dialogs.delete.descriptionGeneric', { entityType: entityTypeLabel }))) {
        try {
          await apiClient.delete(`/angebote/${item.id}`)
          loadData() // Liste neu laden
        } catch (error) {
          toast({
            variant: 'destructive',
            title: t('crud.messages.deleteError', { entityType: entityTypeLabel })
          })
        }
      }
    }
  })

  const loadData = async () => {
    setLoading(true)
    try {
      const response = await apiClient.get('/angebote')
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
    navigate('/einkauf/angebot/neu')
  }

  const handleEdit = (item: any) => {
    handleAction('edit', item)
  }

  const handleDelete = (item: any) => {
    handleAction('delete', item)
  }

  const handleExport = () => {
    try {
      const csvHeader = `${t('crud.fields.offerNumber')};${t('crud.entities.supplier')};${t('crud.fields.product')};${t('crud.fields.price')};${t('crud.fields.status')}\n`
      const csvContent = data.map((angebot: any) =>
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
      config={angeboteConfig}
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
      isLoading={loading}
    />
  )
}