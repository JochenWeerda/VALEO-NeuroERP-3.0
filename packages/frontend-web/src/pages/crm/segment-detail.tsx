import { useState, useEffect } from 'react'
import { useNavigate, useParams } from 'react-router-dom'
import { useTranslation } from 'react-i18next'
import { ObjectPage } from '@/components/mask-builder'
import { useMaskData, useMaskValidation, useMaskActions } from '@/components/mask-builder/hooks'
import { MaskConfig } from '@/components/mask-builder/types'
import { z } from 'zod'
import { getEntityTypeLabel, getDetailTitle, getSuccessMessage, getErrorMessage, getStatusLabel } from '@/features/crud/utils/i18n-helpers'
import { createApiClient } from '@/components/mask-builder/utils/api'
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card'
import { Badge } from '@/components/ui/badge'
import { Button } from '@/components/ui/button'
import { formatDate } from '@/components/mask-builder/utils/formatting'
import { toast } from '@/hooks/use-toast'
import { ArrowLeft, History, Users, BarChart3, Settings } from 'lucide-react'
import { DataTable } from '@/components/ui/data-table'

// API Client
const apiClient = createApiClient('/api/crm-marketing')

// Zod-Schema für Segmente
const createSegmentSchema = (t: any) => z.object({
  name: z.string().min(1, t('crud.messages.validationError')),
  type: z.string().min(1, t('crud.messages.validationError')),
  status: z.string().optional(),
  description: z.string().optional(),
})

// Konfiguration für Segment ObjectPage
const createSegmentConfig = (t: any, entityTypeLabel: string): MaskConfig => ({
  title: entityTypeLabel,
  subtitle: t('crud.detail.manage', { entityType: entityTypeLabel }),
  type: 'object-page',
  tabs: [
    {
      key: 'grundinformationen',
      label: t('crud.detail.basicInfo'),
      fields: [
        {
          name: 'name',
          label: t('crud.fields.name'),
          type: 'text',
          required: true,
          placeholder: t('crud.tooltips.placeholders.name')
        },
        {
          name: 'description',
          label: t('crud.fields.description'),
          type: 'textarea',
          placeholder: t('crud.tooltips.placeholders.description')
        },
        {
          name: 'type',
          label: t('crud.fields.type'),
          type: 'select',
          required: true,
          readOnly: true,
          options: [
            { value: 'dynamic', label: t('crud.segments.types.dynamic') },
            { value: 'static', label: t('crud.segments.types.static') },
            { value: 'hybrid', label: t('crud.segments.types.hybrid') }
          ]
        },
        {
          name: 'status',
          label: t('crud.fields.status'),
          type: 'select',
          options: [
            { value: 'active', label: t('status.active') },
            { value: 'inactive', label: t('status.inactive') },
            { value: 'archived', label: t('crud.segments.status.archived') }
          ]
        },
        {
          name: 'member_count',
          label: t('crud.fields.memberCount'),
          type: 'text',
          readOnly: true
        },
        {
          name: 'last_calculated_at',
          label: t('crud.fields.lastCalculatedAt'),
          type: 'text',
          readOnly: true
        }
      ],
      layout: 'grid',
      columns: 2
    },
    {
      key: 'regeln',
      label: t('crud.segments.rules'),
      fields: [
        {
          name: 'rules_info',
          label: t('crud.segments.rulesInfo'),
          type: 'text',
          readOnly: true
        }
      ],
      layout: 'grid',
      columns: 1
    },
    {
      key: 'mitglieder',
      label: t('crud.segments.members'),
      fields: [
        {
          name: 'members_info',
          label: t('crud.segments.membersInfo'),
          type: 'text',
          readOnly: true
        }
      ],
      layout: 'grid',
      columns: 1
    },
    {
      key: 'performance',
      label: t('crud.segments.performance'),
      fields: [
        {
          name: 'performance_info',
          label: t('crud.segments.performanceInfo'),
          type: 'text',
          readOnly: true
        }
      ],
      layout: 'grid',
      columns: 1
    }
  ],
  actions: [
    {
      key: 'save',
      label: t('crud.actions.save'),
      type: 'primary'
    },
    {
      key: 'cancel',
      label: t('crud.actions.cancel'),
      type: 'secondary'
    },
    {
      key: 'calculate',
      label: t('crud.actions.calculate'),
      type: 'default'
    },
    {
      key: 'export',
      label: t('crud.actions.export'),
      type: 'default'
    }
  ],
  api: {
    baseUrl: '/api/crm-marketing/segments',
    endpoints: {
      get: '/api/crm-marketing/segments/{id}',
      create: '/api/crm-marketing/segments',
      update: '/api/crm-marketing/segments/{id}',
      delete: '/api/crm-marketing/segments/{id}'
    }
  },
  permissions: ['crm.read', 'marketing.read', 'marketing.write']
})

// Members List Component
function SegmentMembersList({ segmentId, segmentType }: { segmentId: string, segmentType: string }) {
  const { t } = useTranslation()
  const [members, setMembers] = useState<any[]>([])
  const [loading, setLoading] = useState(true)

  useEffect(() => {
    const loadMembers = async () => {
      try {
        const response = await apiClient.get(`/segments/${segmentId}/members`)
        if (response.success) {
          setMembers(response.data || [])
        }
      } catch (error) {
        console.error('Fehler beim Laden der Mitglieder:', error)
      } finally {
        setLoading(false)
      }
    }
    if (segmentId) {
      loadMembers()
    }
  }, [segmentId])

  if (loading) {
    return <div className="p-4">Lade Mitglieder...</div>
  }

  if (members.length === 0) {
    return <div className="p-4 text-muted-foreground">{t('crud.messages.noMembers')}</div>
  }

  const columns = [
    {
      key: 'contact_id' as const,
      label: t('crud.entities.contact'),
      render: (member: any) => member.contact_id || '-'
    },
    {
      key: 'added_at' as const,
      label: t('crud.fields.addedAt'),
      render: (member: any) => formatDate(member.added_at)
    },
    {
      key: 'added_by' as const,
      label: t('crud.fields.addedBy'),
      render: (member: any) => member.added_by || '-'
    }
  ]

  return (
    <DataTable
      data={members}
      columns={columns}
    />
  )
}

// Performance Component
function SegmentPerformanceTab({ segmentId }: { segmentId: string }) {
  const { t } = useTranslation()
  const [performance, setPerformance] = useState<any[]>([])
  const [loading, setLoading] = useState(true)

  useEffect(() => {
    const loadPerformance = async () => {
      try {
        const response = await apiClient.get(`/segments/${segmentId}/performance`)
        if (response.success) {
          setPerformance(response.data || [])
        }
      } catch (error) {
        console.error('Fehler beim Laden der Performance:', error)
      } finally {
        setLoading(false)
      }
    }
    if (segmentId) {
      loadPerformance()
    }
  }, [segmentId])

  if (loading) {
    return <div className="p-4">Lade Performance...</div>
  }

  if (performance.length === 0) {
    return <div className="p-4 text-muted-foreground">{t('crud.messages.noPerformanceData')}</div>
  }

  return (
    <div className="space-y-4">
      {performance.map((perf) => (
        <Card key={perf.id}>
          <CardContent className="pt-4">
            <div className="grid grid-cols-4 gap-4">
              <div>
                <div className="text-sm text-muted-foreground">{t('crud.fields.date')}</div>
                <div className="font-medium">{formatDate(perf.date)}</div>
              </div>
              <div>
                <div className="text-sm text-muted-foreground">{t('crud.fields.memberCount')}</div>
                <div className="font-medium">{perf.member_count}</div>
              </div>
              <div>
                <div className="text-sm text-muted-foreground">{t('crud.fields.activeMembers')}</div>
                <div className="font-medium">{perf.active_members}</div>
              </div>
              <div>
                <div className="text-sm text-muted-foreground">{t('crud.fields.conversionRate')}</div>
                <div className="font-medium">{perf.conversion_rate ? `${perf.conversion_rate}%` : '-'}</div>
              </div>
            </div>
          </CardContent>
        </Card>
      ))}
    </div>
  )
}

export default function SegmentDetailPage(): JSX.Element {
  const { t } = useTranslation()
  const navigate = useNavigate()
  const { id } = useParams<{ id: string }>()
  const [loading, setLoading] = useState(false)
  const entityType = 'segment'
  const entityTypeLabel = getEntityTypeLabel(t, entityType, 'Segment')
  const segmentConfig = createSegmentConfig(t, entityTypeLabel)
  const isNew = !id || id === 'new' || id === 'neu'

  const { data, saveData, isLoading: dataLoading } = useMaskData({
    apiUrl: segmentConfig.api.baseUrl,
    id: id || undefined
  })

  const { validate } = useMaskValidation({
    schema: createSegmentSchema(t)
  })

  const handleSave = async (formData: any) => {
    setLoading(true)
    try {
      // Validate
      const validationResult = validate(formData)
      if (!validationResult.valid) {
        toast({
          variant: 'destructive',
          title: t('crud.messages.validationError'),
          description: validationResult.errors.join(', ')
        })
        return
      }

      // Add tenant_id
      formData.tenant_id = '00000000-0000-0000-0000-000000000001' // TODO: Get from auth context

      await saveData(formData)
      toast({
        title: getSuccessMessage(t, isNew ? 'create' : 'update', entityType),
      })
      navigate('/crm/segments')
    } catch (error: any) {
      console.error('Save error:', error)
      toast({
        variant: 'destructive',
        title: getErrorMessage(t, isNew ? 'create' : 'update', entityType),
        description: error.message || t('crud.messages.unknownError')
      })
    } finally {
      setLoading(false)
    }
  }

  const handleCancel = () => {
    if (confirm(t('crud.messages.discardChanges'))) {
      navigate('/crm/segments')
    }
  }

  const handleAction = async (action: string, formData: any) => {
    if (!id) return

    if (action === 'calculate') {
      try {
        await apiClient.post(`/segments/${id}/calculate`, { force_full: false })
        toast({
          title: t('crud.messages.segmentCalculated'),
        })
        window.location.reload()
      } catch (error) {
        toast({
          variant: 'destructive',
          title: t('crud.messages.segmentCalculationError')
        })
      }
    } else if (action === 'export') {
      try {
        const response = await apiClient.get(`/segments/${id}/members`)
        if (response.success) {
          const members = response.data || []
          const csvHeader = `${t('crud.entities.contact')};${t('crud.fields.addedAt')}\n`
          const csvContent = members.map((member: any) =>
            `"${member.contact_id || ''}";"${formatDate(member.added_at)}"`
          ).join('\n')

          const csv = csvHeader + csvContent
          const blob = new Blob([csv], { type: 'text/csv;charset=utf-8;' })
          const url = window.URL.createObjectURL(blob)
          const link = document.createElement('a')
          link.href = url
          link.download = `segment-${id}-members-${new Date().toISOString().split('T')[0]}.csv`
          link.click()
          window.URL.revokeObjectURL(url)

          toast({
            title: t('crud.messages.exportSuccess'),
          })
        }
      } catch (error) {
        toast({
          variant: 'destructive',
          title: t('crud.messages.exportError')
        })
      }
    }
  }

  if (dataLoading && !isNew) {
    return (
      <div className="flex items-center justify-center p-8">
        <div className="text-center">
          <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-primary mx-auto mb-2"></div>
          <p>{t('crud.messages.loading')}</p>
        </div>
      </div>
    )
  }

  return (
    <div className="space-y-4">
      <div className="flex items-center justify-between">
        <div>
          <Button variant="ghost" onClick={() => navigate('/crm/segments')} className="mb-2">
            <ArrowLeft className="h-4 w-4 mr-2" />
            {t('crud.actions.back')}
          </Button>
          <h1 className="text-3xl font-bold">
            {isNew 
              ? t('crud.actions.create', { entityType: entityTypeLabel })
              : getDetailTitle(t, entityTypeLabel, id || '')
            }
          </h1>
        </div>
      </div>

      <div className="grid grid-cols-4 gap-4">
        <div className="col-span-3">
          <ObjectPage
            config={segmentConfig}
            data={data}
            onSave={handleSave}
            onCancel={handleCancel}
            onAction={handleAction}
            isLoading={loading || dataLoading}
          />
        </div>

        {!isNew && id && (
          <div className="col-span-1">
            <Card>
              <CardHeader>
                <CardTitle className="flex items-center gap-2">
                  <Users className="h-5 w-5" />
                  {t('crud.segments.members')}
                </CardTitle>
              </CardHeader>
              <CardContent>
                <SegmentMembersList segmentId={id} segmentType={data?.type || 'dynamic'} />
              </CardContent>
            </Card>

            <Card className="mt-4">
              <CardHeader>
                <CardTitle className="flex items-center gap-2">
                  <BarChart3 className="h-5 w-5" />
                  {t('crud.segments.performance')}
                </CardTitle>
              </CardHeader>
              <CardContent>
                <SegmentPerformanceTab segmentId={id} />
              </CardContent>
            </Card>
          </div>
        )}
      </div>
    </div>
  )
}

