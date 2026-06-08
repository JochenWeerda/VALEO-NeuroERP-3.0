import { useNavigate } from '@/app/routing/react-router-compat'
import { useTranslation } from 'react-i18next'
import { useQuery, useQueryClient } from '@tanstack/react-query'
import { ListReport } from '@/components/mask-builder'
import { formatDate } from '@/components/mask-builder/utils/formatting'
import { Badge } from '@/components/ui/badge'
import { ListConfig } from '@/components/mask-builder/types'
import { apiClient } from '@/lib/api-client'
import { getEntityTypeLabel, getStatusLabel, getSuccessMessage, getErrorMessage } from '@/features/crud/utils/i18n-helpers'
import { toast } from '@/hooks/use-toast'
import { ErrorState } from '@/components/ErrorState'

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
    baseUrl: '/api/v1/crm/campaigns',
    endpoints: {
      list: '/api/v1/crm/campaigns',
      get: '/api/v1/crm/campaigns/{id}',
      create: '/api/v1/crm/campaigns',
      update: '/api/v1/crm/campaigns/{id}',
      delete: '/api/v1/crm/campaigns/{id}'
    }
  },
  permissions: ['crm.read', 'marketing.read', 'marketing.write']
})

export default function CampaignsPage(): JSX.Element {
  const { t } = useTranslation()
  const navigate = useNavigate()
  const queryClient = useQueryClient()
  const entityType = 'campaign'
  const entityTypeLabel = getEntityTypeLabel(t, entityType, 'Kampagne')
  const campaignsConfig = createCampaignsConfig(t, entityTypeLabel)

  const { data: queryData, isLoading, isError, error, refetch } = useQuery({
    queryKey: ['crm', 'campaigns'],
    queryFn: async () => {
      const r = await apiClient.get('/api/v1/crm/campaigns')
      const items = Array.isArray(r.data) ? r.data : ((r.data as any).data || [])
      return { items, total: items.length }
    },
    staleTime: 2 * 60 * 1000,
  })

  if (isError) {
    return <ErrorState error={error as Error} onRetry={() => { void refetch() }} />
  }

  const data = queryData?.items || []
  const total = queryData?.total || 0

  const invalidate = () => queryClient.invalidateQueries({ queryKey: ['crm', 'campaigns'] })

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
    } catch {
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
      isLoading={isLoading}
      onEdit={(item) => navigate(`/crm/campaign/${item.id}`)}
      onDelete={async (item) => {
        if (confirm(t('crud.dialogs.delete.descriptionGeneric', { entityType: entityTypeLabel }))) {
          try {
            await apiClient.delete(`/api/v1/crm/campaigns/${item.id}`)
            toast({
              title: getSuccessMessage(t, 'delete', entityType),
            })
            invalidate()
          } catch {
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
