import { useState, useEffect } from 'react'
import { useNavigate } from 'react-router-dom'
import { useTranslation } from 'react-i18next'
import { ListReport } from '@/components/mask-builder'
import { useMaskActions } from '@/components/mask-builder/hooks'
import { createApiClient } from '@/components/mask-builder/utils/api'
import { formatDate } from '@/components/mask-builder/utils/formatting'
import { Badge } from '@/components/ui/badge'
import { ListConfig } from '@/components/mask-builder/types'
import { getEntityTypeLabel, getStatusLabel, getSuccessMessage, getErrorMessage } from '@/features/crud/utils/i18n-helpers'
import { toast } from '@/hooks/use-toast'

// API Client
const apiClient = createApiClient('/api/crm-gdpr')

// Konfiguration für GDPR-Requests ListReport
const createGDPRRequestsConfig = (t: any, entityTypeLabel: string): ListConfig => ({
  title: entityTypeLabel,
  titleKey: 'crud.list.title',
  subtitle: t('crud.subtitles.manageGDPRRequests'),
  subtitleKey: 'crud.subtitles.manageGDPRRequests',
  type: 'list-report',
  columns: [
    {
      key: 'contact_id',
      label: t('crud.entities.contact'),
      labelKey: 'crud.entities.contact',
      sortable: true,
    },
    {
      key: 'request_type',
      label: t('crud.fields.requestType'),
      labelKey: 'crud.fields.requestType',
      sortable: true,
      render: (value) => {
        const typeLabels: Record<string, string> = {
          access: t('crud.gdpr.requestTypes.access'),
          deletion: t('crud.gdpr.requestTypes.deletion'),
          portability: t('crud.gdpr.requestTypes.portability'),
          objection: t('crud.gdpr.requestTypes.objection'),
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
          pending: 'secondary',
          in_progress: 'default',
          completed: 'default',
          rejected: 'destructive',
          cancelled: 'outline',
        }
        return (
          <Badge variant={statusVariants[value] || 'secondary'}>
            {getStatusLabel(t, value, value)}
          </Badge>
        )
      }
    },
    {
      key: 'requested_at',
      label: t('crud.fields.requestedAt'),
      labelKey: 'crud.fields.requestedAt',
      sortable: true,
      render: (value) => formatDate(value)
    },
    {
      key: 'completed_at',
      label: t('crud.fields.completedAt'),
      labelKey: 'crud.fields.completedAt',
      sortable: true,
      render: (value) => value ? formatDate(value) : '-'
    },
    {
      key: 'verified_at',
      label: t('crud.fields.verifiedAt'),
      labelKey: 'crud.fields.verifiedAt',
      sortable: true,
      render: (value) => value ? formatDate(value) : '-'
    },
    {
      key: 'is_self_request',
      label: t('crud.fields.selfRequest'),
      labelKey: 'crud.fields.selfRequest',
      sortable: true,
      render: (value) => value ? t('crud.messages.yes') : t('crud.messages.no')
    }
  ],
  filters: [
    {
      key: 'request_type',
      label: t('crud.fields.requestType'),
      type: 'select',
      options: [
        { value: 'access', label: t('crud.gdpr.requestTypes.access') },
        { value: 'deletion', label: t('crud.gdpr.requestTypes.deletion') },
        { value: 'portability', label: t('crud.gdpr.requestTypes.portability') },
        { value: 'objection', label: t('crud.gdpr.requestTypes.objection') },
      ]
    },
    {
      key: 'status',
      label: t('crud.fields.status'),
      type: 'select',
      options: [
        { value: 'pending', label: t('status.pending') },
        { value: 'in_progress', label: t('status.inProgress') },
        { value: 'completed', label: t('status.completed') },
        { value: 'rejected', label: t('status.rejected') },
        { value: 'cancelled', label: t('status.cancelled') },
      ]
    }
  ],
  bulkActions: [
    {
      key: 'export',
      label: t('crud.actions.export'),
      action: 'export'
    },
    {
      key: 'markCompleted',
      label: t('crud.actions.markCompleted'),
      action: 'markCompleted'
    }
  ],
  actions: [
    {
      key: 'create',
      label: t('crud.actions.create'),
      type: 'primary'
    },
    {
      key: 'edit',
      label: t('crud.actions.edit'),
      type: 'default'
    },
    {
      key: 'delete',
      label: t('crud.actions.delete'),
      type: 'destructive'
    }
  ],
  api: {
    baseUrl: '/api/crm-gdpr/gdpr/requests',
    endpoints: {
      list: '/api/crm-gdpr/gdpr/requests',
      get: '/api/crm-gdpr/gdpr/requests/{id}',
      create: '/api/crm-gdpr/gdpr/requests',
      update: '/api/crm-gdpr/gdpr/requests/{id}',
      delete: '/api/crm-gdpr/gdpr/requests/{id}'
    }
  },
  permissions: ['crm.read', 'gdpr.read', 'gdpr.write']
})

export default function GDPRRequestsPage(): JSX.Element {
  const { t } = useTranslation()
  const navigate = useNavigate()
  const [data, setData] = useState<any[]>([])
  const [total, setTotal] = useState(0)
  const [loading, setLoading] = useState(true)
  const entityType = 'gdprRequest'
  const entityTypeLabel = getEntityTypeLabel(t, entityType, 'DSGVO-Anfrage')
  const gdprRequestsConfig = createGDPRRequestsConfig(t, entityTypeLabel)

  const { handleAction } = useMaskActions(async (action: string, item: any) => {
    if (action === 'edit' && item) {
      navigate(`/crm/gdpr-request/${item.id}`)
    } else if (action === 'delete' && item) {
      if (confirm(t('crud.dialogs.delete.descriptionGeneric', { entityType: entityTypeLabel }))) {
        try {
          await apiClient.delete(`/gdpr/requests/${item.id}`)
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
    }
  })

  const loadData = async () => {
    setLoading(true)
    try {
      const response = await apiClient.get('/gdpr/requests', {
        params: {
          tenant_id: '00000000-0000-0000-0000-000000000001' // TODO: Get from auth context
        }
      })
      
      if (response.success) {
        const items = response.data || []
        setData(items)
        setTotal(items.length)
      }
    } catch (error) {
      console.error('Fehler beim Laden der GDPR-Requests:', error)
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
    navigate('/crm/gdpr-request/new')
  }

  const handleExport = () => {
    try {
      const csvHeader = `${t('crud.fields.contact')};${t('crud.fields.requestType')};${t('crud.fields.status')};${t('crud.fields.requestedAt')};${t('crud.fields.completedAt')}\n`
      const csvContent = data.map((item: any) =>
        `"${item.contact_id || ''}";"${item.request_type || ''}";"${item.status || ''}";"${item.requested_at || ''}";"${item.completed_at || ''}"`
      ).join('\n')

      const csv = csvHeader + csvContent
      const blob = new Blob([csv], { type: 'text/csv;charset=utf-8;' })
      const link = document.createElement('a')
      const url = URL.createObjectURL(blob)
      link.setAttribute('href', url)
      link.setAttribute('download', `gdpr-requests-${new Date().toISOString().split('T')[0]}.csv`)
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
      config={gdprRequestsConfig}
      data={data}
      total={total}
      loading={loading}
      onAction={handleAction}
      onCreate={handleCreate}
      onExport={handleExport}
    />
  )
}

