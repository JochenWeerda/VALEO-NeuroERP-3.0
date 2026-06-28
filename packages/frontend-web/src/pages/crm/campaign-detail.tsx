import { Suspense, lazy, useState, useEffect } from 'react'
import { useNavigate, useParams } from '@/app/routing/typed-router'
import { useTranslation, type TFunction } from 'react-i18next'
import { ObjectPage } from '@/components/mask-builder'
import { useMaskData } from '@/components/mask-builder/hooks'

import { MaskConfig } from '@/components/mask-builder/types'
import { getEntityTypeLabel, getDetailTitle, getSuccessMessage, getErrorMessage } from '@/features/crud/utils/i18n-helpers'
import { apiClient } from '@/lib/api-client'
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card'
import { Badge } from '@/components/ui/badge'
import { Button } from '@/components/ui/button'
import { formatDate } from '@/components/mask-builder/utils/formatting'
import { toast } from '@/hooks/use-toast'
import { useTenant } from '@/hooks/useTenant'
import { ArrowLeft, Users, BarChart3, Mail, Play, Pause, X } from 'lucide-react'
import { DataTable } from '@/components/ui/data-table'

const CampaignDetailPerformanceChart = lazy(() =>
  import('@/pages/crm/charts/CampaignDetailPerformanceChart').then((module) => ({ default: module.default })),
)


function validateCampaignForm(formData: Record<string, unknown>, t: TFunction): { valid: boolean; errors: string[] } {
  const errorMessage = t('crud.messages.validationError')
  const errors: string[] = []
  const name = String(formData.name ?? '').trim()
  const type = String(formData.type ?? '').trim()
  const segmentId = String(formData.segment_id ?? '').trim()
  const templateId = String(formData.template_id ?? '').trim()
  const senderEmail = String(formData.sender_email ?? '').trim()
  const budget = formData.budget

  if (!name) errors.push(errorMessage)
  if (!type) errors.push(errorMessage)
  if (segmentId && !/^[0-9a-f]{8}-[0-9a-f]{4}-[1-5][0-9a-f]{3}-[89ab][0-9a-f]{3}-[0-9a-f]{12}$/i.test(segmentId)) errors.push(errorMessage)
  if (templateId && !/^[0-9a-f]{8}-[0-9a-f]{4}-[1-5][0-9a-f]{3}-[89ab][0-9a-f]{3}-[0-9a-f]{12}$/i.test(templateId)) errors.push(errorMessage)
  if (senderEmail && !/^[^\s@]+@[^\s@]+\.[^\s@]+$/.test(senderEmail)) errors.push(errorMessage)
  if (budget !== undefined && budget !== null && budget !== '' && Number(budget) < 0) errors.push(errorMessage)

  return { valid: errors.length === 0, errors }
}

const createCampaignConfig = (t: TFunction, entityTypeLabel: string): MaskConfig => ({
  title: entityTypeLabel,
  subtitle: t('crud.detail.manage', { entityType: entityTypeLabel }),
  type: 'object-page',
  tabs: [
    {
      key: 'grundinformationen',
      label: t('crud.detail.basicInfo'),
      fields: [
        { name: 'name', label: t('crud.fields.name'), type: 'text', required: true, placeholder: t('crud.tooltips.placeholders.name') },
        { name: 'description', label: t('crud.fields.description'), type: 'textarea', placeholder: t('crud.tooltips.placeholders.description') },
        {
          name: 'type',
          label: t('crud.fields.type'),
          type: 'select',
          required: true,
          options: [
            { value: 'email', label: t('crud.campaigns.types.email') },
            { value: 'sms', label: t('crud.campaigns.types.sms') },
            { value: 'push', label: t('crud.campaigns.types.push') },
            { value: 'social', label: t('crud.campaigns.types.social') },
          ],
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
          ],
        },
        { name: 'segment_id', label: t('crud.fields.segment'), type: 'lookup', endpoint: '/api/v1/crm/segments', displayField: 'name', valueField: 'id' },
        { name: 'template_id', label: t('crud.fields.template'), type: 'lookup', endpoint: '/api/v1/crm/campaigns/templates', displayField: 'name', valueField: 'id' },
        { name: 'budget', label: t('crud.fields.budget'), type: 'currency', placeholder: t('crud.tooltips.placeholders.budget') },
        { name: 'spent', label: t('crud.fields.spent'), type: 'currency', readOnly: true },
      ],
      layout: 'grid',
      columns: 2,
    },
    {
      key: 'template',
      label: t('crud.campaigns.template'),
      fields: [
        { name: 'sender_name', label: t('crud.fields.senderName'), type: 'text', placeholder: t('crud.tooltips.placeholders.senderName') },
        { name: 'sender_email', label: t('crud.fields.senderEmail'), type: 'text', placeholder: t('crud.tooltips.placeholders.senderEmail') },
        { name: 'subject', label: t('crud.fields.subject'), type: 'text', placeholder: t('crud.tooltips.placeholders.subject') },
      ],
      layout: 'grid',
      columns: 1,
    },
    {
      key: 'schedule',
      label: t('crud.campaigns.schedule'),
      fields: [
        { name: 'scheduled_at', label: t('crud.fields.scheduledAt'), type: 'datetime', placeholder: t('crud.tooltips.placeholders.scheduledAt') },
        { name: 'started_at', label: t('crud.fields.startedAt'), type: 'datetime', readOnly: true },
        { name: 'completed_at', label: t('crud.fields.completedAt'), type: 'datetime', readOnly: true },
      ],
      layout: 'grid',
      columns: 1,
    },
  ],
  actions: [
    { key: 'save', label: t('crud.actions.save'), type: 'primary', onClick: () => undefined },
    { key: 'cancel', label: t('crud.actions.cancel'), type: 'secondary', onClick: () => undefined },
  ],
  api: {
    baseUrl: '/api/v1/crm/campaigns',
    endpoints: {
      get: '/api/v1/crm/campaigns/{id}',
      create: '/api/v1/crm/campaigns',
      update: '/api/v1/crm/campaigns/{id}',
      delete: '/api/v1/crm/campaigns/{id}',
    },
  },
  permissions: ['crm.read', 'marketing.read', 'marketing.write'],
})

function CampaignRecipientsList({ campaignId }: { campaignId: string }) {
  const { t } = useTranslation()
  const [recipients, setRecipients] = useState<Record<string, unknown>[]>([])
  const [loading, setLoading] = useState(true)

  useEffect(() => {
    const loadRecipients = async () => {
      try {
        const response = await apiClient.get<Record<string, unknown>[] | { items?: Record<string, unknown>[] }>(`/api/v1/crm/campaigns/${campaignId}/recipients`)
        const data = response.data
        setRecipients(Array.isArray(data) ? data : ((data as { items?: Record<string, unknown>[] }).items ?? []))
      } catch (error: any) {
        toast({ variant: 'destructive', title: 'Fehler beim Laden der Empfänger', description: error?.message })
      } finally {
        setLoading(false)
      }
    }
    if (campaignId) void loadRecipients()
  }, [campaignId])

  if (loading) return <div className="p-4">Lade Empfaenger...</div>
  if (recipients.length === 0) return <div className="p-4 text-muted-foreground">{t('crud.messages.noRecipients')}</div>

  const columns = [
    { key: 'email' as const, label: t('crud.fields.email'), render: (recipient: Record<string, unknown>) => (recipient.email as string) || '-' },
    {
      key: 'status' as const,
      label: t('crud.fields.status'),
      render: (recipient: Record<string, unknown>) => {
        const statusVariants: Record<string, 'default' | 'secondary' | 'destructive' | 'outline'> = {
          pending: 'secondary',
          sent: 'outline',
          delivered: 'default',
          bounced: 'destructive',
          failed: 'destructive',
        }
        return <Badge variant={statusVariants[recipient.status as string] || 'secondary'}>{(recipient.status as string) || '-'}</Badge>
      },
    },
    { key: 'sent_at' as const, label: t('crud.fields.sentAt'), render: (recipient: Record<string, unknown>) => (recipient.sent_at ? formatDate(recipient.sent_at as string) : '-') },
    { key: 'opened_at' as const, label: t('crud.fields.openedAt'), render: (recipient: Record<string, unknown>) => (recipient.opened_at ? formatDate(recipient.opened_at as string) : '-') },
    { key: 'clicked_at' as const, label: t('crud.fields.clickedAt'), render: (recipient: Record<string, unknown>) => (recipient.clicked_at ? formatDate(recipient.clicked_at as string) : '-') },
    { key: 'open_count' as const, label: t('crud.fields.openCount'), render: (recipient: Record<string, unknown>) => (recipient.open_count as number) || 0 },
    { key: 'click_count' as const, label: t('crud.fields.clickCount'), render: (recipient: Record<string, unknown>) => (recipient.click_count as number) || 0 },
  ]

  return <DataTable data={recipients} columns={columns} />
}

function CampaignPerformanceTab({ campaignId }: { campaignId: string }) {
  const { t } = useTranslation()
  const [performance, setPerformance] = useState<Record<string, unknown>[]>([])
  const [loading, setLoading] = useState(true)
  const [metrics, setMetrics] = useState<Record<string, unknown> | null>(null)

  useEffect(() => {
    const loadPerformance = async () => {
      try {
        const response = await apiClient.get<{ timeline?: unknown[] }>(`/api/v1/crm/campaigns/${campaignId}/analytics`)
        const perfData = response.data
        setPerformance(Array.isArray(perfData?.timeline) ? perfData.timeline : [])
        const campaignResponse = await apiClient.get<Record<string, unknown>>(`/api/v1/crm/campaigns/${campaignId}`)
        setMetrics(campaignResponse.data)
      } catch (error: any) {
        toast({ variant: 'destructive', title: 'Fehler beim Laden der Performance', description: error?.message })
      } finally {
        setLoading(false)
      }
    }
    if (campaignId) void loadPerformance()
  }, [campaignId])

  if (loading) return <div className="p-4">Lade Performance...</div>

  const chartData = performance.map((perf) => ({
    date: formatDate(perf.date),
    sent: perf.sent_count || 0,
    opened: perf.open_count || 0,
    clicked: perf.click_count || 0,
    converted: perf.conversion_count || 0,
  }))

  return (
    <div className="space-y-6">
      {metrics && (
        <div className="grid grid-cols-4 gap-4">
          <Card><CardHeader><CardTitle className="text-sm font-medium">{t('crud.fields.sentCount')}</CardTitle></CardHeader><CardContent><div className="text-2xl font-bold">{metrics.sent_count || 0}</div></CardContent></Card>
          <Card><CardHeader><CardTitle className="text-sm font-medium">{t('crud.fields.openRate')}</CardTitle></CardHeader><CardContent><div className="text-2xl font-bold">{metrics.sent_count > 0 ? `${(((metrics.open_count || 0) / metrics.sent_count) * 100).toFixed(1)}%` : '0%'}</div></CardContent></Card>
          <Card><CardHeader><CardTitle className="text-sm font-medium">{t('crud.fields.clickRate')}</CardTitle></CardHeader><CardContent><div className="text-2xl font-bold">{metrics.sent_count > 0 ? `${(((metrics.click_count || 0) / metrics.sent_count) * 100).toFixed(1)}%` : '0%'}</div></CardContent></Card>
          <Card><CardHeader><CardTitle className="text-sm font-medium">{t('crud.fields.conversionRate')}</CardTitle></CardHeader><CardContent><div className="text-2xl font-bold">{metrics.sent_count > 0 ? `${(((metrics.conversion_count || 0) / metrics.sent_count) * 100).toFixed(1)}%` : '0%'}</div></CardContent></Card>
        </div>
      )}

      {chartData.length > 0 && (
        <Card>
          <CardHeader><CardTitle>{t('crud.campaigns.performanceChart')}</CardTitle></CardHeader>
          <CardContent>
            <Suspense fallback={<div className="h-[300px] animate-pulse rounded bg-muted/40" />}>
              <CampaignDetailPerformanceChart
                chartData={chartData}
                labels={{
                  sent: t('crud.fields.sentCount'),
                  opened: t('crud.fields.openCount'),
                  clicked: t('crud.fields.clickCount'),
                  converted: t('crud.fields.conversionCount'),
                }}
              />
            </Suspense>
          </CardContent>
        </Card>
      )}

      {performance.length === 0 && <div className="p-4 text-muted-foreground">{t('crud.messages.noPerformanceData')}</div>}
    </div>
  )
}

function CampaignEventsList({ campaignId }: { campaignId: string }) {
  const { t } = useTranslation()
  const [events, setEvents] = useState<Record<string, unknown>[]>([])
  const [loading, setLoading] = useState(true)

  useEffect(() => {
    const loadEvents = async () => {
      try {
        const response = await apiClient.get<Record<string, unknown>[] | { items?: Record<string, unknown>[] }>(`/api/v1/crm/campaigns/${campaignId}/recipients`)
        const evData = response.data
        setEvents(Array.isArray(evData) ? evData : ((evData as { items?: Record<string, unknown>[] }).items ?? []))
      } catch (error: any) {
        toast({ variant: 'destructive', title: 'Fehler beim Laden der Events', description: error?.message })
      } finally {
        setLoading(false)
      }
    }
    if (campaignId) void loadEvents()
  }, [campaignId])

  if (loading) return <div className="p-4">Lade Events...</div>
  if (events.length === 0) return <div className="p-4 text-muted-foreground">{t('crud.messages.noEvents')}</div>

  const columns = [
    {
      key: 'event_type' as const,
      label: t('crud.fields.eventType'),
      render: (event: Record<string, unknown>) => {
        const typeLabels: Record<string, string> = {
          sent: t('crud.campaigns.events.sent'),
          delivered: t('crud.campaigns.events.delivered'),
          opened: t('crud.campaigns.events.opened'),
          clicked: t('crud.campaigns.events.clicked'),
          bounced: t('crud.campaigns.events.bounced'),
          converted: t('crud.campaigns.events.converted'),
        }
        return <Badge variant="outline">{typeLabels[event.event_type as string] || (event.event_type as string)}</Badge>
      },
    },
    { key: 'timestamp' as const, label: t('crud.fields.timestamp'), render: (event: Record<string, unknown>) => formatDate(event.timestamp as string) },
    { key: 'recipient_id' as const, label: t('crud.entities.recipient'), render: (event: Record<string, unknown>) => (event.recipient_id as string) || '-' },
  ]

  return <DataTable data={events} columns={columns} />
}

export default function CampaignDetailPage(): JSX.Element {
  const { t } = useTranslation()
  const navigate = useNavigate()
  const { id } = useParams<{ id: string }>()
  const { tenantId } = useTenant()
  const [loading, setLoading] = useState(false)
  const [pendingAction, setPendingAction] = useState<string | null>(null)
  const entityType = 'campaign'
  const entityTypeLabel = getEntityTypeLabel(t, entityType, 'Kampagne')
  const campaignConfig = createCampaignConfig(t, entityTypeLabel)
  const isNew = !id || id === 'new' || id === 'neu'

  const { data, saveData, isLoading: dataLoading } = useMaskData({ apiUrl: campaignConfig.api.baseUrl, id: id || undefined })
  
  const handleSave = async (formData: Record<string, unknown>) => {
    setLoading(true)
    try {
      const validationResult = validateCampaignForm(formData, t)
      if (!validationResult.valid) {
        toast({ variant: 'destructive', title: t('crud.messages.validationError'), description: validationResult.errors.join(', ') })
        return
      }

      formData.tenant_id = tenantId
      await saveData(formData)
      toast({ title: getSuccessMessage(t, isNew ? 'create' : 'update', entityType) })
      if (isNew && data?.id) navigate(`/crm/campaign/${data.id}`)
      else navigate('/crm/campaigns')
    } catch (error: any) {
      toast({ variant: 'destructive', title: getErrorMessage(t, isNew ? 'create' : 'update', entityType), description: error.message || t('crud.messages.unknownError') })
    } finally {
      setLoading(false)
    }
  }

  const handleCancel = () => {
    if (confirm(t('crud.messages.discardChanges'))) navigate('/crm/campaigns')
  }

  const handleStart = async () => {
    if (!id || pendingAction !== null) return
    setPendingAction('start')
    try {
      await apiClient.post(`/api/v1/crm/campaigns/${id}/activate`)
      toast({ title: t('crud.messages.campaignStarted') })
      window.location.reload()
    } catch {
      toast({ variant: 'destructive', title: t('crud.messages.campaignStartError') })
    } finally {
      setPendingAction(null)
    }
  }

  const handlePause = async () => {
    if (!id || pendingAction !== null) return
    setPendingAction('pause')
    try {
      await apiClient.post(`/api/v1/crm/campaigns/${id}/pause`)
      toast({ title: t('crud.messages.campaignPaused') })
      window.location.reload()
    } catch {
      toast({ variant: 'destructive', title: t('crud.messages.campaignPauseError') })
    } finally {
      setPendingAction(null)
    }
  }

  const handleCancelCampaign = async () => {
    if (!id || pendingAction !== null) return
    if (confirm(t('crud.dialogs.cancel.descriptionGeneric', { entityType: entityTypeLabel }))) {
      setPendingAction('cancel')
      try {
        await apiClient.post(`/api/v1/crm/campaigns/${id}/archive`)
        toast({ title: t('crud.messages.campaignCancelled') })
        window.location.reload()
      } catch {
        toast({ variant: 'destructive', title: t('crud.messages.campaignCancelError') })
      } finally {
        setPendingAction(null)
      }
    }
  }

  if (dataLoading && !isNew) {
    return <div className="flex items-center justify-center p-8"><div className="text-center"><div className="mx-auto mb-2 h-8 w-8 animate-spin rounded-full border-b-2 border-primary" /><p>{t('crud.messages.loading')}</p></div></div>
  }

  return (
    <div className="space-y-4">
      <div className="flex items-center justify-between">
        <div>
          <Button variant="ghost" onClick={() => navigate('/crm/campaigns')} className="mb-2"><ArrowLeft className="mr-2 h-4 w-4" />{t('crud.actions.back')}</Button>
          <h1 className="text-3xl font-bold">{isNew ? t('crud.actions.create', { entityType: entityTypeLabel }) : getDetailTitle(t, entityTypeLabel, data?.name || id || '')}</h1>
        </div>
        {!isNew && id && data?.status && (
          <div className="flex gap-2">
            {(data.status === 'draft' || data.status === 'scheduled' || data.status === 'paused') && <Button onClick={handleStart} variant="default" disabled={pendingAction !== null}><Play className="mr-2 h-4 w-4" />{t('crud.actions.start')}</Button>}
            {data.status === 'running' && <Button onClick={handlePause} variant="secondary" disabled={pendingAction !== null}><Pause className="mr-2 h-4 w-4" />{t('crud.actions.pause')}</Button>}
            {data.status !== 'completed' && data.status !== 'cancelled' && <Button onClick={handleCancelCampaign} variant="destructive" disabled={pendingAction !== null}><X className="mr-2 h-4 w-4" />{t('crud.actions.cancel')}</Button>}
          </div>
        )}
      </div>

      <div className="grid grid-cols-4 gap-4">
        <div className="col-span-3">
          <ObjectPage config={campaignConfig} data={data} onSave={handleSave} onCancel={handleCancel} onAction={async (key, fd) => key === 'save' ? handleSave(fd) : handleCancel()} isLoading={loading || dataLoading} />
        </div>

        {!isNew && id && (
          <div className="col-span-1 space-y-4">
            <Card><CardHeader><CardTitle className="flex items-center gap-2"><Users className="h-5 w-5" />{t('crud.campaigns.recipients')}</CardTitle></CardHeader><CardContent><CampaignRecipientsList campaignId={id} /></CardContent></Card>
            <Card><CardHeader><CardTitle className="flex items-center gap-2"><BarChart3 className="h-5 w-5" />{t('crud.campaigns.performance')}</CardTitle></CardHeader><CardContent><CampaignPerformanceTab campaignId={id} /></CardContent></Card>
            <Card><CardHeader><CardTitle className="flex items-center gap-2"><Mail className="h-5 w-5" />{t('crud.campaigns.events')}</CardTitle></CardHeader><CardContent><CampaignEventsList campaignId={id} /></CardContent></Card>
          </div>
        )}
      </div>
    </div>
  )
}
