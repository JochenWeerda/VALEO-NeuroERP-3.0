import { useState } from 'react'
import { useNavigate } from '@/app/routing/typed-router'
import { useTranslation, type TFunction } from 'react-i18next'
import { useQuery, useQueryClient } from '@tanstack/react-query'
import { useMaskActions } from '@/components/mask-builder/hooks'
import { ListReport } from '@/components/mask-builder'
import { formatDate } from '@/components/mask-builder/utils/formatting'
import { Badge } from '@/components/ui/badge'
import { ListConfig } from '@/components/mask-builder/types'
import { apiClient } from '@/lib/api-client'
import { getEntityTypeLabel, getStatusLabel, getSuccessMessage, getErrorMessage } from '@/features/crud/utils/i18n-helpers'
import { toast } from '@/hooks/use-toast'
import { ErrorState } from '@/components/ErrorState'

// Konfiguration für GDPR-Requests ListReport
const createGDPRRequestsConfig = (t: TFunction, entityTypeLabel: string): ListConfig => ({
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
    baseUrl: '/api/v1/gdpr/requests',
    endpoints: {
      list: '/api/v1/gdpr/requests',
      get: '/api/v1/gdpr/requests/{id}',
      create: '/api/v1/gdpr/requests',
      update: '/api/v1/gdpr/requests/{id}',
      delete: '/api/v1/gdpr/requests/{id}'
    }
  },
  permissions: ['crm.read', 'gdpr.read', 'gdpr.write']
})

export default function GDPRRequestsPage(): JSX.Element {
  const { t } = useTranslation()
  const navigate = useNavigate()
  const queryClient = useQueryClient()
  const entityType = 'gdprRequest'
  const entityTypeLabel = getEntityTypeLabel(t, entityType, 'DSGVO-Anfrage')
  const gdprRequestsConfig = createGDPRRequestsConfig(t, entityTypeLabel)

  const { data: queryData, isLoading, isError, error, refetch } = useQuery({
    queryKey: ['crm', 'gdpr-requests'],
    queryFn: async () => {
      const r = await apiClient.get('/api/v1/gdpr/requests')
      const raw = r.data as Record<string, unknown>
      const items = Array.isArray(raw) ? raw : (raw.data || [])
      return { items, total: items.length }
    },
    staleTime: 2 * 60 * 1000,
  })

  const [pendingRows, setPendingRows] = useState<Set<string>>(new Set())

  const invalidate = () => queryClient.invalidateQueries({ queryKey: ['crm', 'gdpr-requests'] })

  async function withPending(key: string, fn: () => Promise<void>) {
    if (pendingRows.has(key)) return
    setPendingRows(prev => new Set(prev).add(key))
    try { await fn() } finally {
      setPendingRows(prev => { const s = new Set(prev); s.delete(key); return s })
    }
  }

  const { handleAction } = useMaskActions(async (action: string, item: Record<string, unknown>) => {
    if (action === 'edit' && item) {
      navigate(`/crm/gdpr-request/${item.id as string}`)
    } else if (action === 'delete' && item) {
      if (!confirm(t('crud.dialogs.delete.descriptionGeneric', { entityType: entityTypeLabel }))) return
      await withPending(String(item.id), async () => {
        try {
          await apiClient.delete(`/api/v1/gdpr/requests/${item.id as string}`)
          toast({ title: getSuccessMessage(t, 'delete', entityType) })
          invalidate()
        } catch {
          toast({ variant: 'destructive', title: getErrorMessage(t, 'delete', entityType) })
        }
      })
    }
  })

  if (isError) {
    return <ErrorState error={error as Error} onRetry={() => { void refetch() }} />
  }

  const data = queryData?.items || []
  const total = queryData?.total || 0

  const handleCreate = () => {
    navigate('/crm/gdpr-request/new')
  }

  const handleExport = () => {
    try {
      const csvHeader = `${t('crud.fields.contact')};${t('crud.fields.requestType')};${t('crud.fields.status')};${t('crud.fields.requestedAt')};${t('crud.fields.completedAt')}\n`
      const csvContent = data.map(item =>
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
    } catch {
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
      loading={isLoading}
      pendingRows={pendingRows}
      onAction={handleAction}
      onCreate={handleCreate}
      onExport={handleExport}
    />
  )
}
