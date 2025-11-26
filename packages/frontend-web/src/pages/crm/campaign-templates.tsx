import { useState, useEffect } from 'react'
import { useNavigate } from 'react-router-dom'
import { useTranslation } from 'react-i18next'
import { ListReport } from '@/components/mask-builder'
import { createApiClient } from '@/components/mask-builder/utils/api'
import { formatDate } from '@/components/mask-builder/utils/formatting'
import { Badge } from '@/components/ui/badge'
import { ListConfig, Action } from '@/components/mask-builder/types'
import { getEntityTypeLabel, getStatusLabel, getSuccessMessage, getErrorMessage } from '@/features/crud/utils/i18n-helpers'
import { toast } from '@/hooks/use-toast'

// API Client
const apiClient = createApiClient('/api/crm-marketing')

// Konfiguration für Campaign Templates ListReport
const createTemplatesConfig = (t: any, entityTypeLabel: string, handleAction: (actionKey: string, data?: any) => Promise<void>): ListConfig => ({
  title: entityTypeLabel,
  titleKey: 'crud.list.title',
  subtitle: t('crud.subtitles.manageTemplates'),
  subtitleKey: 'crud.subtitles.manageTemplates',
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
      key: 'subject',
      label: t('crud.fields.subject'),
      labelKey: 'crud.fields.subject',
      sortable: true,
    },
    {
      key: 'is_active',
      label: t('crud.fields.isActive'),
      labelKey: 'crud.fields.isActive',
      sortable: true,
      render: (value) => {
        return (
          <Badge variant={value ? 'default' : 'secondary'}>
            {value ? t('status.active') : t('status.inactive')}
          </Badge>
        )
      }
    },
    {
      key: 'usage_count',
      label: t('crud.fields.usageCount'),
      labelKey: 'crud.fields.usageCount',
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
      name: 'is_active',
      label: t('crud.fields.isActive'),
      type: 'select',
      options: [
        { value: 'true', label: t('status.active') },
        { value: 'false', label: t('status.inactive') },
      ]
    }
  ],
  bulkActions: [
    {
      key: 'activate',
      label: t('crud.actions.activate'),
      type: 'primary',
      onClick: () => handleAction('activate', null)
    },
    {
      key: 'deactivate',
      label: t('crud.actions.deactivate'),
      type: 'secondary',
      onClick: () => handleAction('deactivate', null)
    },
    {
      key: 'export',
      label: t('crud.actions.export'),
      type: 'secondary',
      onClick: () => handleAction('export', null)
    }
  ],
  actions: [
    {
      key: 'create',
      label: t('crud.actions.create'),
      type: 'primary',
      onClick: () => handleAction('create')
    },
    {
      key: 'edit',
      label: t('crud.actions.edit'),
      type: 'secondary',
      onClick: (item: any) => handleAction('edit', item)
    },
    {
      key: 'delete',
      label: t('crud.actions.delete'),
      type: 'danger',
      onClick: (item: any) => handleAction('delete', item)
    },
    {
      key: 'duplicate',
      label: t('crud.actions.duplicate'),
      type: 'secondary',
      onClick: (item: any) => handleAction('duplicate', item)
    }
  ],
  api: {
    baseUrl: '/api/crm-marketing/campaigns/templates',
    endpoints: {
      list: '/api/crm-marketing/campaigns/templates',
      get: '/api/crm-marketing/campaigns/templates/{id}',
      create: '/api/crm-marketing/campaigns/templates',
      update: '/api/crm-marketing/campaigns/templates/{id}',
      delete: '/api/crm-marketing/campaigns/templates/{id}'
    }
  },
  permissions: ['crm.read', 'marketing.read', 'marketing.write']
})

export default function CampaignTemplatesPage(): JSX.Element {
  const { t } = useTranslation()
  const navigate = useNavigate()
  const [data, setData] = useState<any[]>([])
  const [total, setTotal] = useState(0)
  const [loading, setLoading] = useState(true)
  const entityType = 'campaignTemplate'
  const entityTypeLabel = getEntityTypeLabel(t, entityType, 'Kampagnen-Vorlage')

  const handleAction = async (action: string, item: any = null) => {
    if (action === 'create') {
      navigate('/crm/campaign-template/new')
    } else if (action === 'edit' && item) {
      navigate(`/crm/campaign-template/${item.id}`)
    } else if (action === 'delete' && item) {
      if (confirm(t('crud.dialogs.delete.descriptionGeneric', { entityType: entityTypeLabel }))) {
        try {
          await apiClient.delete(`/campaigns/templates/${item.id}`)
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
    } else if (action === 'duplicate' && item) {
      try {
        const response = await apiClient.post(`/campaigns/templates/${item.id}/duplicate`)
        if (response.success || response.id) {
          toast({
            title: t('crud.messages.templateDuplicated'),
          })
          loadData()
        }
      } catch (error) {
        toast({
          variant: 'destructive',
          title: t('crud.messages.templateDuplicateError'),
        })
      }
    } else if (action === 'activate' && item) {
      try {
        await apiClient.post(`/campaigns/templates/${item.id}/activate`)
        toast({
          title: t('crud.messages.templateActivated'),
        })
        loadData()
      } catch (error) {
        toast({
          variant: 'destructive',
          title: t('crud.messages.templateActivateError'),
        })
      }
    } else if (action === 'deactivate' && item) {
      try {
        await apiClient.post(`/campaigns/templates/${item.id}/deactivate`)
        toast({
          title: t('crud.messages.templateDeactivated'),
        })
        loadData()
      } catch (error) {
        toast({
          variant: 'destructive',
          title: t('crud.messages.templateDeactivateError'),
        })
      }
    } else if (action === 'export') {
      handleExport()
    }
  }

  const templatesConfig = createTemplatesConfig(t, entityTypeLabel, handleAction)

  const loadData = async () => {
    setLoading(true)
    try {
      const response = await apiClient.get('/campaigns/templates', {
        params: {
          tenant_id: '00000000-0000-0000-0000-000000000001' // TODO: Get from auth context
        }
      })

      if (response.success || Array.isArray(response)) {
        const items = Array.isArray(response) ? response : (response.data || [])
        setData(items)
        setTotal(items.length)
      }
    } catch (error) {
      console.error('Fehler beim Laden der Templates:', error)
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
    navigate('/crm/campaign-template/new')
  }

  const handleExport = () => {
    try {
      const csvHeader = `${t('crud.fields.name')};${t('crud.fields.type')};${t('crud.fields.subject')};${t('crud.fields.isActive')};${t('crud.fields.usageCount')};${t('crud.fields.createdAt')}\n`
      const csvContent = data.map((item: any) =>
        `"${item.name || ''}";"${item.type || ''}";"${item.subject || ''}";"${item.is_active ? t('status.active') : t('status.inactive')}";"${item.usage_count || 0}";"${item.created_at || ''}"`
      ).join('\n')

      const csv = csvHeader + csvContent
      const blob = new Blob([csv], { type: 'text/csv;charset=utf-8;' })
      const link = document.createElement('a')
      const url = URL.createObjectURL(blob)
      link.setAttribute('href', url)
      link.setAttribute('download', `campaign-templates-${new Date().toISOString().split('T')[0]}.csv`)
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
      config={templatesConfig}
      data={data}
      total={total}
      isLoading={loading}
      onCreate={handleCreate}
      onExport={handleExport}
    />
  )
}

