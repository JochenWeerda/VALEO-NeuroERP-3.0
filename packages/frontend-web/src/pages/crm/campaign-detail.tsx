import { useState, useEffect } from 'react'
import { useNavigate, useParams } from 'react-router-dom'
import { useTranslation } from 'react-i18next'
import { ObjectPage } from '@/components/mask-builder'
import { useMaskData, useMaskValidation } from '@/components/mask-builder/hooks'
import { MaskConfig } from '@/components/mask-builder/types'
import { z } from 'zod'
import { getEntityTypeLabel, getDetailTitle, getSuccessMessage, getErrorMessage } from '@/features/crud/utils/i18n-helpers'
import { createApiClient } from '@/components/mask-builder/utils/api'
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card'
import { Badge } from '@/components/ui/badge'
import { Button } from '@/components/ui/button'
import { formatDate, formatCurrency } from '@/components/mask-builder/utils/formatting'
import { toast } from '@/hooks/use-toast'
import { ArrowLeft, Users, BarChart3, Mail, Calendar, Play, Pause, X } from 'lucide-react'
import { DataTable } from '@/components/ui/data-table'
import { LineChart, Line, BarChart, Bar, PieChart, Pie, Cell, XAxis, YAxis, CartesianGrid, Tooltip, Legend, ResponsiveContainer } from 'recharts'

// API Client
const apiClient = createApiClient('/api/crm-marketing')

// Zod-Schema für Campaigns
const createCampaignSchema = (t: any) => z.object({
  name: z.string().min(1, t('crud.messages.validationError')),
  type: z.string().min(1, t('crud.messages.validationError')),
  status: z.string().optional(),
  description: z.string().optional(),
  segment_id: z.string().uuid().optional().or(z.literal('')),
  template_id: z.string().uuid().optional().or(z.literal('')),
  scheduled_at: z.string().optional(),
  sender_name: z.string().optional(),
  sender_email: z.string().email().optional().or(z.literal('')),
  subject: z.string().optional(),
  budget: z.number().min(0).optional(),
})

// Konfiguration für Campaign ObjectPage
const createCampaignConfig = (t: any, entityTypeLabel: string): MaskConfig => ({
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
          options: [
            { value: 'email', label: t('crud.campaigns.types.email') },
            { value: 'sms', label: t('crud.campaigns.types.sms') },
            { value: 'push', label: t('crud.campaigns.types.push') },
            { value: 'social', label: t('crud.campaigns.types.social') }
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
            { value: 'cancelled', label: t('status.cancelled') }
          ]
        },
        {
          name: 'segment_id',
          label: t('crud.fields.segment'),
          type: 'lookup',
          endpoint: '/api/crm-marketing/segments',
          displayField: 'name',
          valueField: 'id'
        },
        {
          name: 'template_id',
          label: t('crud.fields.template'),
          type: 'lookup',
          endpoint: '/api/crm-marketing/campaigns/templates',
          displayField: 'name',
          valueField: 'id'
        },
        {
          name: 'budget',
          label: t('crud.fields.budget'),
          type: 'currency',
          placeholder: t('crud.tooltips.placeholders.budget')
        },
        {
          name: 'spent',
          label: t('crud.fields.spent'),
          type: 'currency',
          readOnly: true
        }
      ],
      layout: 'grid',
      columns: 2
    },
    {
      key: 'template',
      label: t('crud.campaigns.template'),
      fields: [
        {
          name: 'sender_name',
          label: t('crud.fields.senderName'),
          type: 'text',
          placeholder: t('crud.tooltips.placeholders.senderName')
        },
        {
          name: 'sender_email',
          label: t('crud.fields.senderEmail'),
          type: 'text',
          placeholder: t('crud.tooltips.placeholders.senderEmail')
        },
        {
          name: 'subject',
          label: t('crud.fields.subject'),
          type: 'text',
          placeholder: t('crud.tooltips.placeholders.subject')
        }
      ],
      layout: 'grid',
      columns: 1
    },
    {
      key: 'schedule',
      label: t('crud.campaigns.schedule'),
      fields: [
        {
          name: 'scheduled_at',
          label: t('crud.fields.scheduledAt'),
          type: 'datetime',
          placeholder: t('crud.tooltips.placeholders.scheduledAt')
        },
        {
          name: 'started_at',
          label: t('crud.fields.startedAt'),
          type: 'datetime',
          readOnly: true
        },
        {
          name: 'completed_at',
          label: t('crud.fields.completedAt'),
          type: 'datetime',
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
      type: 'primary',
      onClick: () => {}
    },
    {
      key: 'cancel',
      label: t('crud.actions.cancel'),
      type: 'secondary',
      onClick: () => {}
    }
  ],
  api: {
    baseUrl: '/api/crm-marketing/campaigns',
    endpoints: {
      get: '/api/crm-marketing/campaigns/{id}',
      create: '/api/crm-marketing/campaigns',
      update: '/api/crm-marketing/campaigns/{id}',
      delete: '/api/crm-marketing/campaigns/{id}'
    }
  },
  permissions: ['crm.read', 'marketing.read', 'marketing.write']
})

// Recipients List Component
function CampaignRecipientsList({ campaignId }: { campaignId: string }) {
  const { t } = useTranslation()
  const [recipients, setRecipients] = useState<any[]>([])
  const [loading, setLoading] = useState(true)

  useEffect(() => {
    const loadRecipients = async () => {
      try {
        const response = await apiClient.get(`/campaigns/${campaignId}/recipients`)
        if (response.success || Array.isArray(response)) {
          const data = response.success ? response.data : response
          setRecipients(Array.isArray(data) ? data : [])
        }
      } catch (error) {
        console.error('Fehler beim Laden der Empfänger:', error)
      } finally {
        setLoading(false)
      }
    }
    if (campaignId) {
      loadRecipients()
    }
  }, [campaignId])

  if (loading) {
    return <div className="p-4">Lade Empfänger...</div>
  }

  if (recipients.length === 0) {
    return <div className="p-4 text-muted-foreground">{t('crud.messages.noRecipients')}</div>
  }

  const columns = [
    {
      key: 'email' as const,
      label: t('crud.fields.email'),
      render: (recipient: any) => recipient.email || '-'
    },
    {
      key: 'status' as const,
      label: t('crud.fields.status'),
      render: (recipient: any) => {
        const statusVariants: Record<string, 'default' | 'secondary' | 'destructive' | 'outline'> = {
          pending: 'secondary',
          sent: 'outline',
          delivered: 'default',
          bounced: 'destructive',
          failed: 'destructive',
        }
        return (
          <Badge variant={statusVariants[recipient.status] || 'secondary'}>
            {recipient.status || '-'}
          </Badge>
        )
      }
    },
    {
      key: 'sent_at' as const,
      label: t('crud.fields.sentAt'),
      render: (recipient: any) => recipient.sent_at ? formatDate(recipient.sent_at) : '-'
    },
    {
      key: 'opened_at' as const,
      label: t('crud.fields.openedAt'),
      render: (recipient: any) => recipient.opened_at ? formatDate(recipient.opened_at) : '-'
    },
    {
      key: 'clicked_at' as const,
      label: t('crud.fields.clickedAt'),
      render: (recipient: any) => recipient.clicked_at ? formatDate(recipient.clicked_at) : '-'
    },
    {
      key: 'open_count' as const,
      label: t('crud.fields.openCount'),
      render: (recipient: any) => recipient.open_count || 0
    },
    {
      key: 'click_count' as const,
      label: t('crud.fields.clickCount'),
      render: (recipient: any) => recipient.click_count || 0
    }
  ]

  return (
    <DataTable
      data={recipients}
      columns={columns}
    />
  )
}

// Performance Component
function CampaignPerformanceTab({ campaignId }: { campaignId: string }) {
  const { t } = useTranslation()
  const [performance, setPerformance] = useState<any[]>([])
  const [loading, setLoading] = useState(true)
  const [metrics, setMetrics] = useState<any>(null)

  useEffect(() => {
    const loadPerformance = async () => {
      try {
        const response = await apiClient.get(`/campaigns/${campaignId}/performance`)
        if (response.success || Array.isArray(response)) {
          const data = response.success ? response.data : response
          setPerformance(Array.isArray(data) ? data : [])
        }
        
        // Load campaign metrics
        const campaignResponse = await apiClient.get(`/campaigns/${campaignId}`)
        if (campaignResponse.success || campaignResponse.id) {
          const campaign = campaignResponse.success ? campaignResponse.data : campaignResponse
          setMetrics(campaign)
        }
      } catch (error) {
        console.error('Fehler beim Laden der Performance:', error)
      } finally {
        setLoading(false)
      }
    }
    if (campaignId) {
      loadPerformance()
    }
  }, [campaignId])

  if (loading) {
    return <div className="p-4">Lade Performance...</div>
  }

  const chartData = performance.map((perf) => ({
    date: formatDate(perf.date),
    sent: perf.sent_count || 0,
    opened: perf.open_count || 0,
    clicked: perf.click_count || 0,
    converted: perf.conversion_count || 0
  }))

  return (
    <div className="space-y-6">
      {metrics && (
        <div className="grid grid-cols-4 gap-4">
          <Card>
            <CardHeader>
              <CardTitle className="text-sm font-medium">{t('crud.fields.sentCount')}</CardTitle>
            </CardHeader>
            <CardContent>
              <div className="text-2xl font-bold">{metrics.sent_count || 0}</div>
            </CardContent>
          </Card>
          <Card>
            <CardHeader>
              <CardTitle className="text-sm font-medium">{t('crud.fields.openRate')}</CardTitle>
            </CardHeader>
            <CardContent>
              <div className="text-2xl font-bold">
                {metrics.sent_count > 0 
                  ? `${((metrics.open_count || 0) / metrics.sent_count * 100).toFixed(1)}%`
                  : '0%'}
              </div>
            </CardContent>
          </Card>
          <Card>
            <CardHeader>
              <CardTitle className="text-sm font-medium">{t('crud.fields.clickRate')}</CardTitle>
            </CardHeader>
            <CardContent>
              <div className="text-2xl font-bold">
                {metrics.sent_count > 0 
                  ? `${((metrics.click_count || 0) / metrics.sent_count * 100).toFixed(1)}%`
                  : '0%'}
              </div>
            </CardContent>
          </Card>
          <Card>
            <CardHeader>
              <CardTitle className="text-sm font-medium">{t('crud.fields.conversionRate')}</CardTitle>
            </CardHeader>
            <CardContent>
              <div className="text-2xl font-bold">
                {metrics.sent_count > 0 
                  ? `${((metrics.conversion_count || 0) / metrics.sent_count * 100).toFixed(1)}%`
                  : '0%'}
              </div>
            </CardContent>
          </Card>
        </div>
      )}

      {chartData.length > 0 && (
        <Card>
          <CardHeader>
            <CardTitle>{t('crud.campaigns.performanceChart')}</CardTitle>
          </CardHeader>
          <CardContent>
            <ResponsiveContainer width="100%" height={300}>
              <LineChart data={chartData}>
                <CartesianGrid strokeDasharray="3 3" />
                <XAxis dataKey="date" />
                <YAxis />
                <Tooltip />
                <Legend />
                <Line type="monotone" dataKey="sent" stroke="#8884d8" name={t('crud.fields.sentCount')} />
                <Line type="monotone" dataKey="opened" stroke="#82ca9d" name={t('crud.fields.openCount')} />
                <Line type="monotone" dataKey="clicked" stroke="#ffc658" name={t('crud.fields.clickCount')} />
                <Line type="monotone" dataKey="converted" stroke="#ff7300" name={t('crud.fields.conversionCount')} />
              </LineChart>
            </ResponsiveContainer>
          </CardContent>
        </Card>
      )}

      {performance.length === 0 && (
        <div className="p-4 text-muted-foreground">{t('crud.messages.noPerformanceData')}</div>
      )}
    </div>
  )
}

// Events List Component
function CampaignEventsList({ campaignId }: { campaignId: string }) {
  const { t } = useTranslation()
  const [events, setEvents] = useState<any[]>([])
  const [loading, setLoading] = useState(true)

  useEffect(() => {
    const loadEvents = async () => {
      try {
        const response = await apiClient.get(`/campaigns/${campaignId}/events`)
        if (response.success || Array.isArray(response)) {
          const data = response.success ? response.data : response
          setEvents(Array.isArray(data) ? data : [])
        }
      } catch (error) {
        console.error('Fehler beim Laden der Events:', error)
      } finally {
        setLoading(false)
      }
    }
    if (campaignId) {
      loadEvents()
    }
  }, [campaignId])

  if (loading) {
    return <div className="p-4">Lade Events...</div>
  }

  if (events.length === 0) {
    return <div className="p-4 text-muted-foreground">{t('crud.messages.noEvents')}</div>
  }

  const columns = [
    {
      key: 'event_type' as const,
      label: t('crud.fields.eventType'),
      render: (event: any) => {
        const typeLabels: Record<string, string> = {
          sent: t('crud.campaigns.events.sent'),
          delivered: t('crud.campaigns.events.delivered'),
          opened: t('crud.campaigns.events.opened'),
          clicked: t('crud.campaigns.events.clicked'),
          bounced: t('crud.campaigns.events.bounced'),
          converted: t('crud.campaigns.events.converted')
        }
        return <Badge variant="outline">{typeLabels[event.event_type] || event.event_type}</Badge>
      }
    },
    {
      key: 'timestamp' as const,
      label: t('crud.fields.timestamp'),
      render: (event: any) => formatDate(event.timestamp)
    },
    {
      key: 'recipient_id' as const,
      label: t('crud.entities.recipient'),
      render: (event: any) => event.recipient_id || '-'
    }
  ]

  return (
    <DataTable
      data={events}
      columns={columns}
    />
  )
}

export default function CampaignDetailPage(): JSX.Element {
  const { t } = useTranslation()
  const navigate = useNavigate()
  const { id } = useParams<{ id: string }>()
  const [loading, setLoading] = useState(false)
  const entityType = 'campaign'
  const entityTypeLabel = getEntityTypeLabel(t, entityType, 'Kampagne')
  const campaignConfig = createCampaignConfig(t, entityTypeLabel)
  const isNew = !id || id === 'new' || id === 'neu'

  const { data, saveData, isLoading: dataLoading } = useMaskData({
    apiUrl: campaignConfig.api.baseUrl,
    id: id || undefined
  })

  const { validate } = useMaskValidation({
    schema: createCampaignSchema(t)
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
      if (isNew && data?.id) {
        navigate(`/crm/campaign/${data.id}`)
      } else {
        navigate('/crm/campaigns')
      }
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
      navigate('/crm/campaigns')
    }
  }

  const handleStart = async () => {
    if (!id) return
    try {
      await apiClient.post(`/campaigns/${id}/start`)
      toast({
        title: t('crud.messages.campaignStarted'),
      })
      window.location.reload()
    } catch (error) {
      toast({
        variant: 'destructive',
        title: t('crud.messages.campaignStartError')
      })
    }
  }

  const handlePause = async () => {
    if (!id) return
    try {
      await apiClient.post(`/campaigns/${id}/pause`)
      toast({
        title: t('crud.messages.campaignPaused'),
      })
      window.location.reload()
    } catch (error) {
      toast({
        variant: 'destructive',
        title: t('crud.messages.campaignPauseError')
      })
    }
  }

  const handleCancelCampaign = async () => {
    if (!id) return
    if (confirm(t('crud.dialogs.cancel.descriptionGeneric', { entityType: entityTypeLabel }))) {
      try {
        await apiClient.post(`/campaigns/${id}/cancel`)
        toast({
          title: t('crud.messages.campaignCancelled'),
        })
        window.location.reload()
      } catch (error) {
        toast({
          variant: 'destructive',
          title: t('crud.messages.campaignCancelError')
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
          <Button variant="ghost" onClick={() => navigate('/crm/campaigns')} className="mb-2">
            <ArrowLeft className="h-4 w-4 mr-2" />
            {t('crud.actions.back')}
          </Button>
          <h1 className="text-3xl font-bold">
            {isNew 
              ? t('crud.actions.create', { entityType: entityTypeLabel })
              : getDetailTitle(t, entityTypeLabel, data?.name || id || '')
            }
          </h1>
        </div>
        {!isNew && id && data?.status && (
          <div className="flex gap-2">
            {data.status === 'draft' || data.status === 'scheduled' || data.status === 'paused' ? (
              <Button onClick={handleStart} variant="default">
                <Play className="h-4 w-4 mr-2" />
                {t('crud.actions.start')}
              </Button>
            ) : null}
            {data.status === 'running' ? (
              <Button onClick={handlePause} variant="secondary">
                <Pause className="h-4 w-4 mr-2" />
                {t('crud.actions.pause')}
              </Button>
            ) : null}
            {data.status !== 'completed' && data.status !== 'cancelled' ? (
              <Button onClick={handleCancelCampaign} variant="destructive">
                <X className="h-4 w-4 mr-2" />
                {t('crud.actions.cancel')}
              </Button>
            ) : null}
          </div>
        )}
      </div>

      <div className="grid grid-cols-4 gap-4">
        <div className="col-span-3">
          <ObjectPage
            config={campaignConfig}
            data={data}
            onSave={handleSave}
            onCancel={handleCancel}
            isLoading={loading || dataLoading}
          />
        </div>

        {!isNew && id && (
          <div className="col-span-1 space-y-4">
            <Card>
              <CardHeader>
                <CardTitle className="flex items-center gap-2">
                  <Users className="h-5 w-5" />
                  {t('crud.campaigns.recipients')}
                </CardTitle>
              </CardHeader>
              <CardContent>
                <CampaignRecipientsList campaignId={id} />
              </CardContent>
            </Card>

            <Card>
              <CardHeader>
                <CardTitle className="flex items-center gap-2">
                  <BarChart3 className="h-5 w-5" />
                  {t('crud.campaigns.performance')}
                </CardTitle>
              </CardHeader>
              <CardContent>
                <CampaignPerformanceTab campaignId={id} />
              </CardContent>
            </Card>

            <Card>
              <CardHeader>
                <CardTitle className="flex items-center gap-2">
                  <Mail className="h-5 w-5" />
                  {t('crud.campaigns.events')}
                </CardTitle>
              </CardHeader>
              <CardContent>
                <CampaignEventsList campaignId={id} />
              </CardContent>
            </Card>
          </div>
        )}
      </div>
    </div>
  )
}
