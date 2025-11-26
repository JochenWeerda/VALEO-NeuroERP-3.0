import { useState, useEffect } from 'react'
import { useNavigate, useParams, useSearchParams } from 'react-router-dom'
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
import { ArrowLeft, History, Mail, RefreshCw } from 'lucide-react'

// API Client
const apiClient = createApiClient('/api/crm-consent')

// Zod-Schema für Consents
const createConsentSchema = (t: any) => z.object({
  contact_id: z.string().uuid(t('crud.messages.validationError')),
  channel: z.string().min(1, t('crud.messages.validationError')),
  consent_type: z.string().min(1, t('crud.messages.validationError')),
  source: z.string().default('manual'),
  expires_at: z.string().optional(),
})

// Konfiguration für Consent ObjectPage
const createConsentConfig = (t: any, entityTypeLabel: string): MaskConfig => ({
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
          // TODO: Load contacts from API
        },
        {
          name: 'channel',
          label: t('crud.fields.channel'),
          type: 'select',
          required: true,
          options: [
            { value: 'email', label: t('crud.channels.email') },
            { value: 'sms', label: t('crud.channels.sms') },
            { value: 'phone', label: t('crud.channels.phone') },
            { value: 'postal', label: t('crud.channels.postal') }
          ]
        },
        {
          name: 'consent_type',
          label: t('crud.fields.consentType'),
          type: 'select',
          required: true,
          options: [
            { value: 'marketing', label: t('crud.consentTypes.marketing') },
            { value: 'service', label: t('crud.consentTypes.service') },
            { value: 'required', label: t('crud.consentTypes.required') }
          ]
        },
        {
          name: 'status',
          label: t('crud.fields.status'),
          type: 'select',
          readOnly: true,
          options: [
            { value: 'pending', label: t('status.pending') },
            { value: 'granted', label: t('status.granted') },
            { value: 'denied', label: t('status.denied') },
            { value: 'revoked', label: t('status.revoked') }
          ]
        },
        {
          name: 'source',
          label: t('crud.fields.source'),
          type: 'select',
          options: [
            { value: 'web_form', label: t('crud.sources.webForm') },
            { value: 'api', label: t('crud.sources.api') },
            { value: 'import', label: t('crud.sources.import') },
            { value: 'manual', label: t('crud.sources.manual') }
          ],
          default: 'manual'
        },
        {
          name: 'expires_at',
          label: t('crud.fields.expiresAt'),
          type: 'date',
          placeholder: t('crud.tooltips.placeholders.expiresAt')
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
          name: 'granted_at',
          label: t('crud.fields.grantedAt'),
          type: 'text',
          readOnly: true
        },
        {
          name: 'denied_at',
          label: t('crud.fields.deniedAt'),
          type: 'text',
          readOnly: true
        },
        {
          name: 'revoked_at',
          label: t('crud.fields.revokedAt'),
          type: 'text',
          readOnly: true
        },
        {
          name: 'double_opt_in_confirmed_at',
          label: t('crud.fields.confirmedAt'),
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
      key: 'revoke',
      label: t('crud.actions.revoke'),
      type: 'destructive'
    },
    {
      key: 'resendConfirmation',
      label: t('crud.actions.resendConfirmation'),
      type: 'default'
    }
  ],
  api: {
    baseUrl: '/api/crm-consent/consents',
    endpoints: {
      get: '/api/crm-consent/consents/{id}',
      create: '/api/crm-consent/consents',
      update: '/api/crm-consent/consents/{id}',
      delete: '/api/crm-consent/consents/{id}'
    }
  },
  permissions: ['crm.read', 'consent.read', 'consent.write']
})

// History Component
function ConsentHistoryTab({ consentId }: { consentId: string }) {
  const { t } = useTranslation()
  const [history, setHistory] = useState<any[]>([])
  const [loading, setLoading] = useState(true)

  useEffect(() => {
    const loadHistory = async () => {
      try {
        const response = await apiClient.get(`/consents/${consentId}/history`)
        if (response.success) {
          setHistory(response.data || [])
        }
      } catch (error) {
        console.error('Fehler beim Laden der History:', error)
      } finally {
        setLoading(false)
      }
    }
    if (consentId) {
      loadHistory()
    }
  }, [consentId])

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
                {entry.reason && (
                  <div className="text-xs text-muted-foreground mt-1">
                    {t('crud.fields.reason')}: {entry.reason}
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

export default function ConsentDetailPage(): JSX.Element {
  const { t } = useTranslation()
  const navigate = useNavigate()
  const { id } = useParams<{ id: string }>()
  const [loading, setLoading] = useState(false)
  const entityType = 'consent'
  const entityTypeLabel = getEntityTypeLabel(t, entityType, 'Consent')
  const consentConfig = createConsentConfig(t, entityTypeLabel)
  const isNew = !id || id === 'new' || id === 'neu'

  const { data, saveData, isLoading: dataLoading } = useMaskData({
    apiUrl: consentConfig.api.baseUrl,
    id: id || undefined
  })

  const { validate } = useMaskValidation({
    schema: createConsentSchema(t)
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
      
      // Set contact_id from query param if creating new
      if (isNew && contactIdFromQuery) {
        formData.contact_id = contactIdFromQuery
      }

      await saveData(formData)
      toast({
        title: getSuccessMessage(t, isNew ? 'create' : 'update', entityType),
      })
      navigate('/crm/consents')
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
      navigate('/crm/consents')
    }
  }

  const handleAction = async (action: string, formData: any) => {
    if (action === 'revoke' && id) {
      try {
        await apiClient.post(`/consents/${id}/revoke`)
        toast({
          title: t('crud.messages.consentRevoked'),
        })
        navigate('/crm/consents')
      } catch (error) {
        toast({
          variant: 'destructive',
          title: t('crud.messages.consentRevokeError')
        })
      }
    } else if (action === 'resendConfirmation' && id) {
      // TODO: Implement resend confirmation email
      toast({
        title: t('crud.messages.comingSoon'),
        description: t('crud.messages.resendConfirmationComingSoon')
      })
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
          <Button variant="ghost" onClick={() => navigate('/crm/consents')} className="mb-2">
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
            config={consentConfig}
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
                <ConsentHistoryTab consentId={id} />
              </CardContent>
            </Card>
          </div>
        )}
      </div>
    </div>
  )
}

