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

// API Client für Anfragen
const apiClient = createApiClient('/api/einkauf')

// Konfiguration für Anfragen ListReport (wird in Komponente mit i18n erstellt)
const createAnfragenConfig = (t: any, entityTypeLabel: string): ListConfig => ({
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
          'BANF': t('crud.fields.requisition'),
          'ANF': t('crud.entities.purchaseRequest')
        }
        return <Badge variant="outline">{typLabels[value] || value}</Badge>
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
          'niedrig': { label: t('crud.fields.priorityLow'), variant: 'secondary' },
          'normal': { label: t('crud.fields.priorityNormal'), variant: 'default' },
          'hoch': { label: t('crud.fields.priorityHigh'), variant: 'destructive' },
          'dringend': { label: t('crud.fields.priorityUrgent'), variant: 'destructive' }
        }
        const prio = prioLabels[value] || { label: value, variant: 'secondary' as const }
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
        const statusLabel = getStatusLabel(t, value as string, value as string)
        const variants: Record<string, 'secondary' | 'default' | 'outline' | 'destructive'> = {
          'ENTWURF': 'secondary',
          'FREIGEGEBEN': 'default',
          'ANGEBOTSPHASE': 'outline'
        }
        return <Badge variant={variants[value as string] || 'secondary'}>{statusLabel}</Badge>
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
        { value: 'ANGEBOTSPHASE', label: t('crud.status.offerPhase'), labelKey: 'crud.status.offerPhase' }
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
  bulkActions: [
    {
      key: 'freigeben',
      label: t('crud.actions.approve'),
      labelKey: 'crud.actions.approve',
      type: 'primary',
      onClick: () => console.log('Freigeben clicked')
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
    baseUrl: '/api/einkauf/anfragen',
    endpoints: {
      list: '/api/einkauf/anfragen',
      get: '/api/einkauf/anfragen/{id}',
      create: '/api/einkauf/anfragen',
      update: '/api/einkauf/anfragen/{id}',
      delete: '/api/einkauf/anfragen/{id}'
    }
  },
  permissions: ['einkauf.read', 'einkauf.write'],
  actions: []
})

export default function AnfragenListePage(): JSX.Element {
  const { t } = useTranslation()
  const navigate = useNavigate()
  const [data, setData] = useState<any[]>([])
  const [total, setTotal] = useState(0)
  const [loading, setLoading] = useState(true)
  const entityType = 'purchaseRequest'
  const entityTypeLabel = getEntityTypeLabel(t, entityType, 'Anfrage')
  const anfragenConfig = createAnfragenConfig(t, entityTypeLabel)

  const { handleAction } = useMaskActions(async (action: string, item: any) => {
    if (action === 'edit' && item) {
      navigate(`/einkauf/anfragen/${item.id}`)
    } else if (action === 'delete' && item) {
      if (confirm(t('crud.dialogs.delete.descriptionGeneric', { entityType: entityTypeLabel }))) {
        try {
          await apiClient.delete(`/anfragen/${item.id}`)
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
      const response = await apiClient.get('/anfragen')
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
    navigate('/einkauf/anfrage/neu')
  }

  const handleEdit = (item: any) => {
    handleAction('edit', item)
  }

  const handleDelete = (item: any) => {
    handleAction('delete', item)
  }

  const handleExport = () => {
    try {
      const csvHeader = `${t('crud.fields.requestNumber')};${t('crud.fields.requester')};${t('crud.fields.product')};${t('crud.fields.quantity')};${t('crud.fields.status')}\n`
      const csvContent = data.map((anfrage: any) =>
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
      config={anfragenConfig}
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