import { useState, useEffect } from 'react'
import { useNavigate, useParams } from '@/app/routing/typed-router'
import { useTranslation } from 'react-i18next'
import type { TFunction } from 'i18next'
import { z } from 'zod'
import { ObjectPage } from '@/components/mask-builder'
import { useMaskData, useMaskActions } from '@/components/mask-builder/hooks'

import { MaskConfig } from '@/components/mask-builder/types'
import { getEntityTypeLabel, getDetailTitle, getSuccessMessage, getErrorMessage } from '@/features/crud/utils/i18n-helpers'
import { apiClient } from '@/lib/api-client'
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card'
import { Button } from '@/components/ui/button'
import { formatDate } from '@/components/mask-builder/utils/formatting'
import { toast } from '@/hooks/use-toast'
import { useTenant } from '@/hooks/useTenant'
import { ArrowLeft, Users, BarChart3 } from 'lucide-react'
import { ModuleToolbar } from '@/components/navigation/ModuleToolbar'
import { DataTable, type LegacyColumnDef } from '@/components/ui/data-table'
import { recordArrayFromResponse, renderValue, stringValue } from '@/lib/record-utils'

// API Client

// Zod-Schema für Segmente
const createSegmentSchema = (t: TFunction) => z.object({
  name: z.string().min(1, t('crud.messages.validationError')),
  type: z.string().min(1, t('crud.messages.validationError')),
  status: z.string().optional(),
  description: z.string().optional(),
})

function validateSegmentForm(formData: unknown, t: TFunction): { valid: boolean; errors: string[] } {
  const result = createSegmentSchema(t).safeParse(formData)
  return result.success
    ? { valid: true, errors: [] }
    : { valid: false, errors: result.error.issues.map((issue: { message: string }) => issue.message) }
}

// Konfiguration für Segment ObjectPage
const createSegmentConfig = (t: TFunction, entityTypeLabel: string): MaskConfig => ({
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
    baseUrl: '/api/v1/crm/segments',
    endpoints: {
      get: '/api/v1/crm/segments/{id}',
      create: '/api/v1/crm/segments',
      update: '/api/v1/crm/segments/{id}',
      delete: '/api/v1/crm/segments/{id}'
    }
  },
  permissions: ['crm.read', 'marketing.read', 'marketing.write']
})

// Members List Component
function SegmentMembersList({ segmentId }: { segmentId: string }) {
  const { t } = useTranslation()
  const [members, setMembers] = useState<Record<string, unknown>[]>([])
  const [loading, setLoading] = useState(true)

  useEffect(() => {
    const loadMembers = async () => {
      try {
        const response = await apiClient.get(`/api/v1/crm/segments/${segmentId}/members`)
        setMembers(recordArrayFromResponse(response.data))
      } catch (_rawErr: unknown) {
        const error = _rawErr as { response?: { data?: { detail?: string } }; message?: string; name?: string }
        toast({ variant: 'destructive', title: 'Fehler beim Laden der Mitglieder', description: error?.message })
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

  const columns: LegacyColumnDef<Record<string, unknown>>[] = [
    {
      key: 'contact_id' as const,
      label: t('crud.entities.contact'),
      render: (member) => renderValue(member.contact_id, '-')
    },
    {
      key: 'added_at' as const,
      label: t('crud.fields.addedAt'),
      render: (member) => formatDate(stringValue(member.added_at))
    },
    {
      key: 'added_by' as const,
      label: t('crud.fields.addedBy'),
      render: (member) => renderValue(member.added_by, '-')
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
  const [performance, setPerformance] = useState<Record<string, unknown>[]>([])
  const [loading, setLoading] = useState(true)

  useEffect(() => {
    const loadPerformance = async () => {
      try {
        const response = await apiClient.get(`/api/v1/crm/segments/${segmentId}/performance`)
        setPerformance(recordArrayFromResponse(response.data))
      } catch (_rawErr: unknown) {
        const error = _rawErr as { response?: { data?: { detail?: string } }; message?: string; name?: string }
        toast({ variant: 'destructive', title: 'Fehler beim Laden der Performance-Daten', description: error?.message })
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
        <Card key={stringValue(perf.id)}>
          <CardContent className="pt-4">
            <div className="grid grid-cols-4 gap-4">
              <div>
                <div className="text-sm text-muted-foreground">{t('crud.fields.date')}</div>
                <div className="font-medium">{formatDate(stringValue(perf.date))}</div>
              </div>
              <div>
                <div className="text-sm text-muted-foreground">{t('crud.fields.memberCount')}</div>
                <div className="font-medium">{renderValue(perf.member_count)}</div>
              </div>
              <div>
                <div className="text-sm text-muted-foreground">{t('crud.fields.activeMembers')}</div>
                <div className="font-medium">{renderValue(perf.active_members)}</div>
              </div>
              <div>
                <div className="text-sm text-muted-foreground">{t('crud.fields.conversionRate')}</div>
                <div className="font-medium">{perf.conversion_rate ? `${String(perf.conversion_rate)}%` : '-'}</div>
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
  const { tenantId } = useTenant()
  const [loading, setLoading] = useState(false)
  const entityType = 'segment'
  const entityTypeLabel = getEntityTypeLabel(t, entityType, 'Segment')
  const segmentConfig = createSegmentConfig(t, entityTypeLabel)
  const isNew = !id || id === 'new' || id === 'neu'

  const { data, saveData, isLoading: dataLoading } = useMaskData<Record<string, unknown>>({
    apiUrl: segmentConfig.api.baseUrl,
    id: id || undefined
  })


  const handleSave = async (formData: Record<string, unknown>) => {
    setLoading(true)
    try {
      // Validate
      const validationResult = validateSegmentForm(formData, t)
      if (!validationResult.valid) {
        toast({
          variant: 'destructive',
          title: t('crud.messages.validationError'),
          description: validationResult.errors.join(', ')
        })
        return
      }

      formData.tenant_id = tenantId

      await saveData(formData)
      toast({
        title: getSuccessMessage(t, isNew ? 'create' : 'update', entityType),
      })
      navigate('/crm/segments')
    } catch (_rawErr: unknown) {
      const error = _rawErr as { response?: { data?: { detail?: string } }; message?: string; name?: string }
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

  const { handleAction, loadingActionKey } = useMaskActions(async (action: string) => {
    if (!id) return

    if (action === 'calculate') {
      try {
        await apiClient.post(`/api/v1/crm/segments/${id}/calculate`, { force_full: false })
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
        const response = await apiClient.get<Record<string, unknown>[]>(`/api/v1/crm/segments/${id}/members`)
        if (response.data) {
          const members = response.data || []
          const csvHeader = `${t('crud.entities.contact')};${t('crud.fields.addedAt')}\n`
          const csvContent = members.map(member =>
            `"${String(member.contact_id ?? '')}";"${formatDate(member.added_at as string)}"`
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
  })

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
      <ModuleToolbar backTarget="/crm/segments" closeTarget="/crm/segments" title={isNew ? t('crud.actions.create', { entityType: entityTypeLabel }) : getDetailTitle(t, entityTypeLabel, id || '')} />
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
            loadingActionKey={loadingActionKey}
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
                <SegmentMembersList segmentId={id} />
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

