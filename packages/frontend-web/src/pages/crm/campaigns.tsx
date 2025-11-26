import { useState, useEffect } from 'react'
import { useNavigate } from 'react-router-dom'
import { useTranslation } from 'react-i18next'
import { ListReport } from '@/components/mask-builder'
import { useMaskActions } from '@/components/mask-builder/hooks'
import { createApiClient } from '@/components/mask-builder/utils/api'
import { formatDate, formatCurrency } from '@/components/mask-builder/utils/formatting'
import { Badge } from '@/components/ui/badge'
import { ListConfig } from '@/components/mask-builder/types'
import { getEntityTypeLabel, getStatusLabel, getSuccessMessage, getErrorMessage } from '@/features/crud/utils/i18n-helpers'
import { toast } from '@/hooks/use-toast'

// API Client
const apiClient = createApiClient('/api/crm-marketing')

// Konfiguration für Campaigns ListReport
const createCampaignsConfig = (t: any, entityTypeLabel: string): ListConfig => ({
  title: entityTypeLabel,
  titleKey: 'crud.list.title',
  subtitle: t('crud.subtitles.manageCampaigns'),
  subtitleKey: 'crud.subtitles.manageCampaigns',
  type: 'list-report',
  columns: [
    {
      key: 'name',
      label: t('crud.fields.name'),
      labelKey: 'crud.fields.name',
      sortable: true,
    },
    {
      key: 'type',
      label: t('crud.fields.type'),
      labelKey: 'crud.fields.type',
      sortable: true,
      render: (value) => {
        const typeLabels: Record<string, string> = {
          email: t('crud.campaigns.types.email'),
          sms: t('crud.campaigns.types.sms'),
          push: t('crud.campaigns.types.push'),
          social: t('crud.campaigns.types.social'),
        }
        return <Badge variant="outline">{typeLabels[value] || value}</Badge>
      }
    },
    {
      key: 'status',
      label: t('crud.fields.status'),
      labelKey: 'crud.fields.status',
      sortable: true,
      render: (value) => {
        const statusVariants: Record<string, 'default' | 'secondary' | 'destructive' | 'outline'> = {
          draft: 'secondary',
          scheduled: 'outline',
          running: 'default',
          paused: 'secondary',
          completed: 'default',
          cancelled: 'destructive',
        }
        return (
          <Badge variant={statusVariants[value] || 'secondary'}>
            {getStatusLabel(t, value, value)}
          </Badge>
        )
      }
    },
    {
      key: 'sent_count',
      label: t('crud.fields.sentCount'),
      labelKey: 'crud.fields.sentCount',
      sortable: true,
      render: (value) => value?.toLocaleString() || '0'
    },
    {
      key: 'open_count',
      label: t('crud.fields.openCount'),
      labelKey: 'crud.fields.openCount',
      sortable: true,
      render: (value) => value?.toLocaleString() || '0'
    },
    {
      key: 'click_count',
      label: t('crud.fields.clickCount'),
      labelKey: 'crud.fields.clickCount',
      sortable: true,
      render: (value) => value?.toLocaleString() || '0'
    },
    {
      key: 'created_at',
      label: t('crud.fields.createdAt'),
      labelKey: 'crud.fields.createdAt',
      sortable: true,
      render: (value) => formatDate(value)
    }
  ],
  filters: [
    {
      name: 'type',
      label: t('crud.fields.type'),
      type: 'select',
      options: [
        { value: 'email', label: t('crud.campaigns.types.email') },
        { value: 'sms', label: t('crud.campaigns.types.sms') },
        { value: 'push', label: t('crud.campaigns.types.push') },
        { value: 'social', label: t('crud.campaigns.types.social') },
      ]
    },
    {
      name: 'status',
      label: t('crud.fields.status'),
      type: 'select',
      options: [
        { value: 'draft', label: t('status.draft') },
        { value: 'scheduled', label: t('crud.campaigns.status.scheduled') },
        { value: 'running', label: t('status.running') },
        { value: 'paused', label: t('status.onHold') },
        { value: 'completed', label: t('status.completed') },
        { value: 'cancelled', label: t('status.cancelled') },
      ]
    }
  ],
  bulkActions: [],
  actions: [],
  api: {
    baseUrl: '/api/crm-marketing/campaigns',
    endpoints: {
      list: '/api/crm-marketing/campaigns',
      get: '/api/crm-marketing/campaigns/{id}',
      create: '/api/crm-marketing/campaigns',
      update: '/api/crm-marketing/campaigns/{id}',
      delete: '/api/crm-marketing/campaigns/{id}'
    }
  },
  permissions: ['crm.read', 'marketing.read', 'marketing.write']
})

export default function CampaignsPage(): JSX.Element {
  const { t } = useTranslation()
  const navigate = useNavigate()
  const [data, setData] = useState<any[]>([])
  const [total, setTotal] = useState(0)
  const [loading, setLoading] = useState(true)
  const entityType = 'campaign'
  const entityTypeLabel = getEntityTypeLabel(t, entityType, 'Kampagne')
  const campaignsConfig = createCampaignsConfig(t, entityTypeLabel)

  const { handleAction } = useMaskActions(async (action: string, item: any) => {
    if (action === 'edit' && item) {
      navigate(`/crm/campaign/${item.id}`)
    } else if (action === 'delete' && item) {
      if (confirm(t('crud.dialogs.delete.descriptionGeneric', { entityType: entityTypeLabel }))) {
        try {
          await apiClient.delete(`/campaigns/${item.id}`)
          toast({
            title: getSuccessMessage(t, 'delete', entityType),
          })
          loadData()
        } catch (error) {
          toast({
            variant: 'destructive',
            title: getErrorMessage(t, 'delete', entityType),
          })
        }
      }
    } else if (action === 'start' && item) {
      try {
        await apiClient.post(`/campaigns/${item.id}/start`)
        toast({
          title: t('crud.messages.campaignStarted'),
        })
        loadData()
      } catch (error) {
        toast({
          variant: 'destructive',
          title: t('crud.messages.campaignStartError'),
        })
      }
    } else if (action === 'pause' && item) {
      try {
        await apiClient.post(`/campaigns/${item.id}/pause`)
        toast({
          title: t('crud.messages.campaignPaused'),
        })
        loadData()
      } catch (error) {
        toast({
          variant: 'destructive',
          title: t('crud.messages.campaignPauseError'),
        })
      }
    } else if (action === 'cancel' && item) {
      if (confirm(t('crud.dialogs.cancel.descriptionGeneric', { entityType: entityTypeLabel }))) {
        try {
          await apiClient.post(`/campaigns/${item.id}/cancel`)
          toast({
            title: t('crud.messages.campaignCancelled'),
          })
          loadData()
        } catch (error) {
          toast({
            variant: 'destructive',
            title: t('crud.messages.campaignCancelError'),
          })
        }
      }
    }
  })

  const loadData = async () => {
    setLoading(true)
    try {
      const response = await apiClient.get('/campaigns', {
        params: {
          tenant_id: '00000000-0000-0000-0000-000000000001' // TODO: Get from auth context
        }
      })
      
      if (response.success) {
        const items = Array.isArray(response.data) ? response.data : []
        setData(items)
        setTotal(items.length)
      } else {
        const items = Array.isArray(response) ? response : []
        setData(items)
        setTotal(items.length)
      }
    } catch (error) {
      console.error('Fehler beim Laden der Kampagnen:', error)
      toast({
        variant: 'destructive',
        title: t('crud.messages.loadError')
      })
    } finally {
      setLoading(false)
    }
  }

  useEffect(() => {
    loadData()
  }, [])

  const handleCreate = () => {
    navigate('/crm/campaign/new')
  }

  const handleExport = () => {
    try {
      const csvHeader = `${t('crud.fields.name')};${t('crud.fields.type')};${t('crud.fields.status')};${t('crud.fields.sentCount')};${t('crud.fields.openCount')};${t('crud.fields.clickCount')};${t('crud.fields.createdAt')}\n`
      const csvContent = data.map((item: any) =>
        `"${item.name || ''}";"${item.type || ''}";"${item.status || ''}";"${item.sent_count || 0}";"${item.open_count || 0}";"${item.click_count || 0}";"${item.created_at || ''}"`
      ).join('\n')

      const csv = csvHeader + csvContent
      const blob = new Blob([csv], { type: 'text/csv;charset=utf-8;' })
      const link = document.createElement('a')
      const url = URL.createObjectURL(blob)
      link.setAttribute('href', url)
      link.setAttribute('download', `campaigns-${new Date().toISOString().split('T')[0]}.csv`)
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
      })
    }
  }

  return (
    <ListReport
      config={campaignsConfig}
      data={data}
      total={total}
      isLoading={loading}
      onEdit={(item) => navigate(`/crm/campaign/${item.id}`)}
      onDelete={async (item) => {
        if (confirm(t('crud.dialogs.delete.descriptionGeneric', { entityType: entityTypeLabel }))) {
          try {
            await apiClient.delete(`/campaigns/${item.id}`)
            toast({
              title: getSuccessMessage(t, 'delete', entityType),
            })
            loadData()
          } catch (error) {
            toast({
              variant: 'destructive',
              title: getErrorMessage(t, 'delete', entityType),
            })
          }
        }
      }}
      onCreate={handleCreate}
      onExport={handleExport}
    />
  )
}
