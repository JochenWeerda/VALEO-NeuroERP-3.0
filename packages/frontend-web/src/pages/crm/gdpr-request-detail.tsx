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
import { ArrowLeft, History, Download, CheckCircle2, XCircle, FileText } from 'lucide-react'

// API Client
const apiClient = createApiClient('/api/crm-gdpr')

// Zod-Schema für GDPR-Requests
const createGDPRRequestSchema = (t: any) => z.object({
  request_type: z.string().min(1, t('crud.messages.validationError')),
  contact_id: z.string().uuid(t('crud.messages.validationError')),
  notes: z.string().optional(),
})

// Konfiguration für GDPR-Request ObjectPage
const createGDPRRequestConfig = (t: any, entityTypeLabel: string): MaskConfig => ({
  title: entityTypeLabel,
  subtitle: t('crud.detail.manage', { entityType: entityTypeLabel }),
  type: 'object-page',
  tabs: [
    {
      key: 'grundinformationen',
      label: t('crud.detail.basicInfo'),
      fields: [
        {
          name: 'contact_id',
          label: t('crud.entities.contact'),
          type: 'text',
          required: true,
          placeholder: t('crud.tooltips.placeholders.selectContact')
        },
        {
          name: 'request_type',
          label: t('crud.fields.requestType'),
          type: 'select',
          required: true,
          readOnly: true,
          options: [
            { value: 'access', label: t('crud.gdpr.requestTypes.access') },
            { value: 'deletion', label: t('crud.gdpr.requestTypes.deletion') },
            { value: 'portability', label: t('crud.gdpr.requestTypes.portability') },
            { value: 'objection', label: t('crud.gdpr.requestTypes.objection') }
          ]
        },
        {
          name: 'status',
          label: t('crud.fields.status'),
          type: 'select',
          readOnly: true,
          options: [
            { value: 'pending', label: t('status.pending') },
            { value: 'in_progress', label: t('status.inProgress') },
            { value: 'completed', label: t('status.completed') },
            { value: 'rejected', label: t('status.rejected') },
            { value: 'cancelled', label: t('status.cancelled') }
          ]
        },
        {
          name: 'is_self_request',
          label: t('crud.fields.selfRequest'),
          type: 'checkbox',
          readOnly: true
        },
        {
          name: 'notes',
          label: t('crud.fields.notes'),
          type: 'textarea',
          placeholder: t('crud.tooltips.placeholders.internalNotes')
        }
      ],
      layout: 'grid',
      columns: 2
    },
    {
      key: 'verifizierung',
      label: t('crud.gdpr.verification'),
      fields: [
        {
          name: 'verified_at',
          label: t('crud.fields.verifiedAt'),
          type: 'text',
          readOnly: true
        },
        {
          name: 'verification_method',
          label: t('crud.fields.verificationMethod'),
          type: 'select',
          readOnly: true,
          options: [
            { value: 'email', label: t('crud.gdpr.verificationMethods.email') },
            { value: 'id_card', label: t('crud.gdpr.verificationMethods.idCard') },
            { value: 'manual', label: t('crud.gdpr.verificationMethods.manual') },
            { value: 'other', label: t('crud.gdpr.verificationMethods.other') }
          ]
        }
      ],
      layout: 'grid',
      columns: 2
    },
    {
      key: 'response',
      label: t('crud.gdpr.response'),
      fields: [
        {
          name: 'response_file_format',
          label: t('crud.fields.fileFormat'),
          type: 'text',
          readOnly: true
        },
        {
          name: 'completed_at',
          label: t('crud.fields.completedAt'),
          type: 'text',
          readOnly: true
        },
        {
          name: 'rejection_reason',
          label: t('crud.fields.rejectionReason'),
          type: 'textarea',
          readOnly: true
        }
      ],
      layout: 'grid',
      columns: 2
    },
    {
      key: 'timestamps',
      label: t('crud.detail.timestamps'),
      fields: [
        {
          name: 'requested_at',
          label: t('crud.fields.requestedAt'),
          type: 'text',
          readOnly: true
        },
        {
          name: 'completed_at',
          label: t('crud.fields.completedAt'),
          type: 'text',
          readOnly: true
        },
        {
          name: 'rejected_at',
          label: t('crud.fields.rejectedAt'),
          type: 'text',
          readOnly: true
        },
        {
          name: 'created_at',
          label: t('crud.fields.createdAt'),
          type: 'text',
          readOnly: true
        },
        {
          name: 'updated_at',
          label: t('crud.fields.updatedAt'),
          type: 'text',
          readOnly: true
        }
      ],
      layout: 'grid',
      columns: 2
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
      key: 'verify',
      label: t('crud.actions.verify'),
      type: 'default'
    },
    {
      key: 'generateExport',
      label: t('crud.actions.generateExport'),
      type: 'default'
    },
    {
      key: 'deleteData',
      label: t('crud.actions.deleteData'),
      type: 'destructive'
    },
    {
      key: 'reject',
      label: t('crud.actions.reject'),
      type: 'destructive'
    },
    {
      key: 'downloadExport',
      label: t('crud.actions.downloadExport'),
      type: 'default'
    }
  ],
  api: {
    baseUrl: '/api/crm-gdpr/gdpr/requests',
    endpoints: {
      get: '/api/crm-gdpr/gdpr/requests/{id}',
      create: '/api/crm-gdpr/gdpr/requests',
      update: '/api/crm-gdpr/gdpr/requests/{id}',
      delete: '/api/crm-gdpr/gdpr/requests/{id}'
    }
  },
  permissions: ['crm.read', 'gdpr.read', 'gdpr.write']
})

// History Component
function GDPRRequestHistoryTab({ requestId }: { requestId: string }) {
  const { t } = useTranslation()
  const [history, setHistory] = useState<any[]>([])
  const [loading, setLoading] = useState(true)

  useEffect(() => {
    const loadHistory = async () => {
      try {
        const response = await apiClient.get(`/gdpr/requests/${requestId}/history`)
        if (response.success) {
          setHistory(response.data || [])
        }
      } catch (error) {
        console.error('Fehler beim Laden der History:', error)
      } finally {
        setLoading(false)
      }
    }
    if (requestId) {
      loadHistory()
    }
  }, [requestId])

  if (loading) {
    return <div className="p-4">Lade History...</div>
  }

  if (history.length === 0) {
    return <div className="p-4 text-muted-foreground">{t('crud.messages.noHistory')}</div>
  }

  return (
    <div className="space-y-4">
      {history.map((entry) => (
        <Card key={entry.id}>
          <CardContent className="pt-4">
            <div className="flex items-start justify-between">
              <div className="flex-1">
                <div className="font-medium">{t(`crud.actions.${entry.action}`, { defaultValue: entry.action })}</div>
                <div className="text-sm text-muted-foreground mt-1">
                  {entry.old_status && (
                    <span className="line-through text-red-600">
                      {getStatusLabel(t, entry.old_status, entry.old_status)}
                    </span>
                  )}
                  {entry.old_status && entry.new_status && ' → '}
                  {entry.new_status && (
                    <span className="text-green-600">
                      {getStatusLabel(t, entry.new_status, entry.new_status)}
                    </span>
                  )}
                </div>
                {entry.notes && (
                  <div className="text-xs text-muted-foreground mt-1">
                    {entry.notes}
                  </div>
                )}
              </div>
              <div className="text-right text-sm text-muted-foreground">
                <div>{entry.changed_by}</div>
                <div>{formatDate(entry.changed_at)}</div>
              </div>
            </div>
          </CardContent>
        </Card>
      ))}
    </div>
  )
}

export default function GDPRRequestDetailPage(): JSX.Element {
  const { t } = useTranslation()
  const navigate = useNavigate()
  const { id } = useParams<{ id: string }>()
  const [loading, setLoading] = useState(false)
  const entityType = 'gdprRequest'
  const entityTypeLabel = getEntityTypeLabel(t, entityType, 'DSGVO-Anfrage')
  const gdprRequestConfig = createGDPRRequestConfig(t, entityTypeLabel)
  const isNew = !id || id === 'new' || id === 'neu'

  const { data, saveData, isLoading: dataLoading } = useMaskData({
    apiUrl: gdprRequestConfig.api.baseUrl,
    id: id || undefined
  })

  const { validate } = useMaskValidation({
    schema: createGDPRRequestSchema(t)
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
      formData.requested_by = formData.requested_by || 'system' // TODO: Get from auth context

      await saveData(formData)
      toast({
        title: getSuccessMessage(t, isNew ? 'create' : 'update', entityType),
      })
      navigate('/crm/gdpr-requests')
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
      navigate('/crm/gdpr-requests')
    }
  }

  const handleAction = async (action: string, formData: any) => {
    if (!id) return

    if (action === 'verify') {
      try {
        await apiClient.post(`/gdpr/requests/${id}/verify`, {
          verification_method: 'manual', // TODO: Get from form or dialog
          verification_token: null
        })
        toast({
          title: t('crud.messages.verificationSuccess'),
        })
        window.location.reload() // Reload to show updated status
      } catch (error) {
        toast({
          variant: 'destructive',
          title: t('crud.messages.verificationError')
        })
      }
    } else if (action === 'generateExport') {
      try {
        await apiClient.post(`/gdpr/requests/${id}/export`, {
          format: 'json', // TODO: Get from form or dialog
          data_areas: ['all']
        })
        toast({
          title: t('crud.messages.exportGenerated'),
        })
        window.location.reload()
      } catch (error) {
        toast({
          variant: 'destructive',
          title: t('crud.messages.exportError')
        })
      }
    } else if (action === 'deleteData') {
      if (confirm(t('crud.gdpr.confirmDeleteData'))) {
        try {
          await apiClient.post(`/gdpr/requests/${id}/delete`, {
            reason: t('crud.gdpr.gdprRequest'),
            anonymize_only: true
          })
          toast({
            title: t('crud.messages.dataDeleted'),
          })
          window.location.reload()
        } catch (error) {
          toast({
            variant: 'destructive',
            title: t('crud.messages.deleteError')
          })
        }
      }
    } else if (action === 'reject') {
      const reason = prompt(t('crud.gdpr.enterRejectionReason'))
      if (reason) {
        try {
          await apiClient.post(`/gdpr/requests/${id}/reject`, {
            rejection_reason: reason
          })
          toast({
            title: t('crud.messages.requestRejected'),
          })
          window.location.reload()
        } catch (error) {
          toast({
            variant: 'destructive',
            title: t('crud.messages.rejectError')
          })
        }
      }
    } else if (action === 'downloadExport') {
      try {
        const response = await fetch(`/api/crm-gdpr/gdpr/requests/${id}/download`)
        if (response.ok) {
          const blob = await response.blob()
          const url = window.URL.createObjectURL(blob)
          const link = document.createElement('a')
          link.href = url
          link.download = `gdpr-export-${id}.${data?.response_file_format || 'json'}`
          link.click()
          window.URL.revokeObjectURL(url)
          toast({
            title: t('crud.messages.downloadStarted'),
          })
        } else {
          throw new Error('Download failed')
        }
      } catch (error) {
        toast({
          variant: 'destructive',
          title: t('crud.messages.downloadError')
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
          <Button variant="ghost" onClick={() => navigate('/crm/gdpr-requests')} className="mb-2">
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
            config={gdprRequestConfig}
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
                  <History className="h-5 w-5" />
                  {t('crud.detail.history')}
                </CardTitle>
              </CardHeader>
              <CardContent>
                <GDPRRequestHistoryTab requestId={id} />
              </CardContent>
            </Card>

            {data?.response_file_path && (
              <Card className="mt-4">
                <CardHeader>
                  <CardTitle className="flex items-center gap-2">
                    <FileText className="h-5 w-5" />
                    {t('crud.gdpr.export')}
                  </CardTitle>
                </CardHeader>
                <CardContent>
                  <div className="space-y-2">
                    <div className="text-sm">
                      <strong>{t('crud.fields.fileFormat')}:</strong> {data.response_file_format?.toUpperCase()}
                    </div>
                    <Button
                      onClick={() => handleAction('downloadExport', data)}
                      className="w-full"
                    >
                      <Download className="h-4 w-4 mr-2" />
                      {t('crud.actions.downloadExport')}
                    </Button>
                  </div>
                </CardContent>
              </Card>
            )}
          </div>
        )}
      </div>
    </div>
  )
}

