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
const apiClient = createApiClient('/api/crm-marketing')

// Konfiguration für Segmente ListReport
const createSegmentsConfig = (t: any, entityTypeLabel: string): ListConfig => ({
  title: entityTypeLabel,
  titleKey: 'crud.list.title',
  subtitle: t('crud.subtitles.manageSegments'),
  subtitleKey: 'crud.subtitles.manageSegments',
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
          dynamic: t('crud.segments.types.dynamic'),
          static: t('crud.segments.types.static'),
          hybrid: t('crud.segments.types.hybrid'),
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
          active: 'default',
          inactive: 'secondary',
          archived: 'outline',
        }
        return (
          <Badge variant={statusVariants[value] || 'secondary'}>
            {getStatusLabel(t, value, value)}
          </Badge>
        )
      }
    },
    {
      key: 'member_count',
      label: t('crud.fields.memberCount'),
      labelKey: 'crud.fields.memberCount',
      sortable: true,
      render: (value) => value?.toLocaleString() || '0'
    },
    {
      key: 'last_calculated_at',
      label: t('crud.fields.lastCalculatedAt'),
      labelKey: 'crud.fields.lastCalculatedAt',
      sortable: true,
      render: (value) => value ? formatDate(value) : '-'
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
      key: 'type',
      label: t('crud.fields.type'),
      type: 'select',
      options: [
        { value: 'dynamic', label: t('crud.segments.types.dynamic') },
        { value: 'static', label: t('crud.segments.types.static') },
        { value: 'hybrid', label: t('crud.segments.types.hybrid') },
      ]
    },
    {
      key: 'status',
      label: t('crud.fields.status'),
      type: 'select',
      options: [
        { value: 'active', label: t('status.active') },
        { value: 'inactive', label: t('status.inactive') },
        { value: 'archived', label: t('crud.segments.status.archived') },
      ]
    }
  ],
  bulkActions: [
    {
      key: 'calculate',
      label: t('crud.actions.calculate'),
      action: 'calculate'
    },
    {
      key: 'export',
      label: t('crud.actions.export'),
      action: 'export'
    },
    {
      key: 'archive',
      label: t('crud.actions.archive'),
      action: 'archive'
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
    baseUrl: '/api/crm-marketing/segments',
    endpoints: {
      list: '/api/crm-marketing/segments',
      get: '/api/crm-marketing/segments/{id}',
      create: '/api/crm-marketing/segments',
      update: '/api/crm-marketing/segments/{id}',
      delete: '/api/crm-marketing/segments/{id}'
    }
  },
  permissions: ['crm.read', 'marketing.read', 'marketing.write']
})

export default function SegmentsPage(): JSX.Element {
  const { t } = useTranslation()
  const navigate = useNavigate()
  const [data, setData] = useState<any[]>([])
  const [total, setTotal] = useState(0)
  const [loading, setLoading] = useState(true)
  const entityType = 'segment'
  const entityTypeLabel = getEntityTypeLabel(t, entityType, 'Segment')
  const segmentsConfig = createSegmentsConfig(t, entityTypeLabel)

  const { handleAction } = useMaskActions(async (action: string, item: any) => {
    if (action === 'edit' && item) {
      navigate(`/crm/segment/${item.id}`)
    } else if (action === 'delete' && item) {
      if (confirm(t('crud.dialogs.delete.descriptionGeneric', { entityType: entityTypeLabel }))) {
        try {
          await apiClient.delete(`/segments/${item.id}`)
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
    } else if (action === 'calculate' && item) {
      try {
        await apiClient.post(`/segments/${item.id}/calculate`, { force_full: false })
        toast({
          title: t('crud.messages.segmentCalculated'),
        })
        loadData()
      } catch (error) {
        toast({
          variant: 'destructive',
          title: t('crud.messages.segmentCalculationError'),
        })
      }
    }
  })

  const loadData = async () => {
    setLoading(true)
    try {
      const response = await apiClient.get('/segments', {
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
      console.error('Fehler beim Laden der Segmente:', error)
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
    navigate('/crm/segment/new')
  }

  const handleExport = () => {
    try {
      const csvHeader = `${t('crud.fields.name')};${t('crud.fields.type')};${t('crud.fields.status')};${t('crud.fields.memberCount')};${t('crud.fields.createdAt')}\n`
      const csvContent = data.map((item: any) =>
        `"${item.name || ''}";"${item.type || ''}";"${item.status || ''}";"${item.member_count || 0}";"${item.created_at || ''}"`
      ).join('\n')

      const csv = csvHeader + csvContent
      const blob = new Blob([csv], { type: 'text/csv;charset=utf-8;' })
      const link = document.createElement('a')
      const url = URL.createObjectURL(blob)
      link.setAttribute('href', url)
      link.setAttribute('download', `segments-${new Date().toISOString().split('T')[0]}.csv`)
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
      config={segmentsConfig}
      data={data}
      total={total}
      loading={loading}
      onAction={handleAction}
      onCreate={handleCreate}
      onExport={handleExport}
    />
  )
}

