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
import { Button } from '@/components/ui/button'
import { formatDate } from '@/components/mask-builder/utils/formatting'
import { toast } from '@/hooks/use-toast'
import { ArrowLeft, FileText, Copy } from 'lucide-react'

// API Client
const apiClient = createApiClient('/api/crm-marketing')

// Zod-Schema für Campaign Templates
const createTemplateSchema = (t: any) => z.object({
  name: z.string().min(1, t('crud.messages.validationError')),
  type: z.string().min(1, t('crud.messages.validationError')),
  subject: z.string().optional(),
  body_html: z.string().optional(),
  body_text: z.string().optional(),
  sender_name: z.string().optional(),
  sender_email: z.string().email().optional().or(z.literal('')),
  is_active: z.boolean().default(true),
  description: z.string().optional(),
})

// Konfiguration für Campaign Template ObjectPage
const createTemplateConfig = (t: any, entityTypeLabel: string): MaskConfig => ({
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
          name: 'is_active',
          label: t('crud.fields.isActive'),
          type: 'boolean',
        },
        {
          name: 'usage_count',
          label: t('crud.fields.usageCount'),
          type: 'number',
          readOnly: true
        },
        {
          name: 'created_at',
          label: t('crud.fields.createdAt'),
          type: 'text',
          readOnly: true
        }
      ],
      layout: 'grid',
      columns: 2
    },
    {
      key: 'inhalt',
      label: t('crud.campaigns.templateContent'),
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
        },
        {
          name: 'body_html',
          label: t('crud.fields.bodyHtml'),
          type: 'textarea',
          placeholder: t('crud.tooltips.placeholders.bodyHtml'),
          rows: 10
        },
        {
          name: 'body_text',
          label: t('crud.fields.bodyText'),
          type: 'textarea',
          placeholder: t('crud.tooltips.placeholders.bodyText'),
          rows: 10
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
    baseUrl: '/api/crm-marketing/campaigns/templates',
    endpoints: {
      get: '/api/crm-marketing/campaigns/templates/{id}',
      create: '/api/crm-marketing/campaigns/templates',
      update: '/api/crm-marketing/campaigns/templates/{id}',
      delete: '/api/crm-marketing/campaigns/templates/{id}'
    }
  },
  permissions: ['crm.read', 'marketing.read', 'marketing.write']
})

export default function CampaignTemplateDetailPage(): JSX.Element {
  const { t } = useTranslation()
  const navigate = useNavigate()
  const { id } = useParams<{ id: string }>()
  const [loading, setLoading] = useState(false)
  const entityType = 'campaignTemplate'
  const entityTypeLabel = getEntityTypeLabel(t, entityType, 'Kampagnen-Vorlage')
  const templateConfig = createTemplateConfig(t, entityTypeLabel)
  const isNew = !id || id === 'new' || id === 'neu'

  const { data, saveData, isLoading: dataLoading } = useMaskData({
    apiUrl: templateConfig.api.baseUrl,
    id: id || undefined
  })

  const { validate } = useMaskValidation({
    schema: createTemplateSchema(t)
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
        navigate(`/crm/campaign-template/${data.id}`)
      } else {
        navigate('/crm/campaign-templates')
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
      navigate('/crm/campaign-templates')
    }
  }

  const handleDuplicate = async () => {
    if (!id) return
    try {
      const response = await apiClient.post(`/campaigns/templates/${id}/duplicate`)
      if (response.success || response.id) {
        const newId = response.success ? response.data?.id || response.data?.id : response.id
        toast({
          title: t('crud.messages.templateDuplicated'),
        })
        navigate(`/crm/campaign-template/${newId}`)
      }
    } catch (error) {
      toast({
        variant: 'destructive',
        title: t('crud.messages.templateDuplicateError')
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
          <Button variant="ghost" onClick={() => navigate('/crm/campaign-templates')} className="mb-2">
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
        {!isNew && id && (
          <Button onClick={handleDuplicate} variant="outline">
            <Copy className="h-4 w-4 mr-2" />
            {t('crud.actions.duplicate')}
          </Button>
        )}
      </div>

      <ObjectPage
        config={templateConfig}
        data={data}
        onSave={handleSave}
        onCancel={handleCancel}
        isLoading={loading || dataLoading}
      />
    </div>
  )
}

