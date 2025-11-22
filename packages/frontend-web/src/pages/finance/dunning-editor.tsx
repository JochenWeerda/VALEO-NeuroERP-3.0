import { useState } from 'react'
import { useNavigate, useParams } from 'react-router-dom'
import { useTranslation } from 'react-i18next'
import { ObjectPage } from '@/components/mask-builder'
import { useMaskData, useMaskValidation, useMaskActions } from '@/components/mask-builder/hooks'
import { MaskConfig } from '@/components/mask-builder/types'
import { z } from 'zod'
import { toast } from '@/hooks/use-toast'
import { getEntityTypeLabel } from '@/features/crud/utils/i18n-helpers'

// Zod-Schema für Dunning (wird in Komponente mit i18n erstellt)
const createDunningSchema = (t: any) => z.object({
  opId: z.string().min(1, t('crud.messages.validationError')),
  debitorId: z.string().min(1, t('crud.messages.validationError')),
  dunningLevel: z.number().min(1).max(3, t('crud.messages.validationError')),
  dunningDate: z.string().regex(/^\d{4}-\d{2}-\d{2}$/, t('crud.messages.validationError')),
  dueDate: z.string().regex(/^\d{4}-\d{2}-\d{2}$/, t('crud.messages.validationError')),
  amount: z.number().positive(t('crud.messages.validationError')),
  dunningFee: z.number().min(0, t('crud.messages.validationError')).default(0),
  interest: z.number().min(0, t('crud.messages.validationError')).default(0),
  totalAmount: z.number().positive(t('crud.messages.validationError')),
  text: z.string().min(1, t('crud.messages.validationError')),
  paymentDeadline: z.string().optional(),
  status: z.enum(['created', 'sent', 'paid', 'escalated', 'collection']),
  sentDate: z.string().optional(),
  paymentDate: z.string().optional(),
  notes: z.string().optional(),
  reminderCount: z.number().min(0).default(0),
  lastReminderDate: z.string().optional()
})

// Konfiguration für Dunning ObjectPage (wird in Komponente mit i18n erstellt)
const createDunningConfig = (t: any, entityTypeLabel: string): MaskConfig => ({
  title: entityTypeLabel,
  subtitle: t('crud.actions.edit'),
  type: 'object-page',
  tabs: [
    {
      key: 'grunddaten',
      label: t('crud.detail.basicInfo'),
      fields: [
        {
          name: 'opId',
          label: t('crud.fields.opReference'),
          type: 'text',
          required: true,
          placeholder: t('crud.tooltips.placeholders.opReference')
        },
        {
          name: 'debitorId',
          label: t('crud.entities.debtor'),
          type: 'lookup',
          required: true,
          endpoint: '/api/finance/debitors',
          displayField: 'name',
          valueField: 'id'
        },
        {
          name: 'dunningLevel',
          label: t('crud.fields.dunningLevel'),
          type: 'select',
          required: true,
          options: [
            { value: 1, label: t('crud.fields.dunningLevel1') },
            { value: 2, label: t('crud.fields.dunningLevel2') },
            { value: 3, label: t('crud.fields.dunningLevel3') }
          ]
        },
        {
          name: 'dunningDate',
          label: t('crud.fields.dunningDate'),
          type: 'date',
          required: true
        },
        {
          name: 'dueDate',
          label: t('crud.fields.originalDueDate'),
          type: 'date',
          required: true
        },
        {
          name: 'status',
          label: t('crud.fields.status'),
          type: 'select',
          required: true,
          options: [
            { value: 'created', label: t('status.recorded') },
            { value: 'sent', label: t('status.sent') },
            { value: 'paid', label: t('status.paid') },
            { value: 'escalated', label: t('crud.fields.escalated') },
            { value: 'collection', label: t('crud.fields.collection') }
          ]
        }
      ],
      layout: 'grid',
      columns: 2
    },
    {
      key: 'betrag',
      label: t('crud.fields.amountAndFees'),
      fields: [
        {
          name: 'amount',
          label: t('crud.fields.openAmount'),
          type: 'number',
          required: true,
          step: 0.01,
          readonly: true,
          helpText: t('crud.tooltips.fields.amountFromOp')
        },
        {
          name: 'dunningFee',
          label: t('crud.fields.dunningFee'),
          type: 'number',
          step: 0.01,
          placeholder: t('crud.tooltips.placeholders.dunningFee'),
          helpText: t('crud.tooltips.fields.dunningFee')
        },
        {
          name: 'interest',
          label: t('crud.fields.interest'),
          type: 'number',
          step: 0.01,
          placeholder: t('crud.tooltips.placeholders.interest'),
          helpText: t('crud.tooltips.fields.interest')
        },
        {
          name: 'totalAmount',
          label: t('crud.fields.totalClaim'),
          type: 'number',
          required: true,
          step: 0.01,
          readonly: true,
          helpText: t('crud.tooltips.fields.totalClaim')
        }
      ],
      layout: 'grid',
      columns: 2
    },
    {
      key: 'text',
      label: t('crud.fields.dunningText'),
      fields: [
        {
          name: 'text',
          label: t('crud.fields.dunningText'),
          type: 'textarea',
          required: true,
          placeholder: t('crud.tooltips.placeholders.dunningText')
        },
        {
          name: 'paymentDeadline',
          label: t('crud.fields.paymentDeadline'),
          type: 'text',
          placeholder: t('crud.tooltips.placeholders.paymentDeadline')
        }
      ]
    },
    {
      key: 'versand',
      label: t('crud.fields.shippingAndPayment'),
      fields: [
        {
          name: 'sentDate',
          label: t('crud.fields.sentDate'),
          type: 'date'
        },
        {
          name: 'paymentDate',
          label: t('crud.fields.paymentReceived'),
          type: 'date'
        },
        {
          name: 'reminderCount',
          label: t('crud.fields.remindersSent'),
          type: 'number',
          readonly: true,
          helpText: t('crud.tooltips.fields.remindersSent')
        },
        {
          name: 'lastReminderDate',
          label: t('crud.fields.lastReminder'),
          type: 'date',
          readonly: true
        }
      ],
      layout: 'grid',
      columns: 2
    },
    {
      key: 'notizen',
      label: t('crud.fields.notes'),
      fields: [
        {
          name: 'notes',
          label: t('crud.fields.internalNotes'),
          type: 'textarea',
          placeholder: t('crud.tooltips.placeholders.dunningNotes')
        }
      ]
    }
  ],
  actions: [
    {
      key: 'generate',
      label: t('crud.actions.generateDunning'),
      type: 'secondary',
      onClick: () => {}
    },
    {
      key: 'preview',
      label: t('crud.actions.preview'),
      type: 'secondary',
      onClick: () => {}
    },
    {
      key: 'send',
      label: t('crud.actions.send'),
      type: 'primary',
      onClick: () => {}
    },
    {
      key: 'payment',
      label: t('crud.actions.bookPayment'),
      type: 'secondary',
      onClick: () => {}
    },
    {
      key: 'escalate',
      label: t('crud.actions.escalate'),
      type: 'danger',
      onClick: () => {}
    },
    {
      key: 'collection',
      label: t('crud.actions.handOverToCollection'),
      type: 'danger',
      onClick: () => {}
    },
    {
      key: 'export',
      label: t('crud.actions.pdfExport'),
      type: 'secondary',
      onClick: () => {}
    }
  ],
  api: {
    baseUrl: '/api/finance/dunning',
    endpoints: {
      list: '/api/finance/dunning',
      get: '/api/finance/dunning/{id}',
      create: '/api/finance/dunning',
      update: '/api/finance/dunning/{id}',
      delete: '/api/finance/dunning/{id}'
    }
  },
  validation: createDunningSchema(t),
  permissions: ['finance.write', 'finance.dunning']
})

export default function DunningEditorPage(): JSX.Element {
  const { t } = useTranslation()
  const navigate = useNavigate()
  const { id } = useParams()
  const [isDirty, setIsDirty] = useState(false)
  const entityType = 'dunning'
  const entityTypeLabel = getEntityTypeLabel(t, entityType, 'Mahnung')
  const dunningConfig = createDunningConfig(t, entityTypeLabel)

  const { data, loading, saveData } = useMaskData({
    apiUrl: dunningConfig.api.baseUrl,
    id: id ?? 'new'
  })

  const { validate, showValidationToast } = useMaskValidation(dunningConfig.validation)

  const { handleAction } = useMaskActions(async (action: string, formData: Record<string, unknown>) => {
    if (action === 'generate') {
      // Mahnung generieren - berechne Gesamtforderung und generiere Text
      const gesamtForderung = (formData.amount as number || 0) + (formData.dunningFee as number || 0) + (formData.interest as number || 0)
      formData.totalAmount = gesamtForderung

      // Generiere Standard-Mahntext basierend auf Mahnstufe
      if (!formData.text || (formData.text as string).trim() === '') {
        const mahnstufe = formData.dunningLevel as number || 1
        const betrag = formData.amount as number || 0
        const frist = formData.paymentDeadline as string || '7 Tage'

        formData.text = t('crud.messages.dunningTextTemplate', {
          mahnstufeText: mahnstufe > 1 ? t('crud.messages.dunningTextPrevious', { level: mahnstufe - 1 }) + ' ' : '',
          betrag: betrag.toFixed(2),
          frist: frist
        })
      }

      toast({
        title: t('crud.messages.dunningGenerated'),
        description: t('crud.messages.dunningGeneratedDesc', { level: formData.dunningLevel }),
      })
    } else if (action === 'preview') {
      // Vorschau
      if (!id || id === 'new') {
        toast({
          variant: 'destructive',
          title: t('common.error'),
          description: t('crud.messages.saveFirst'),
        })
        return
      }
      window.open(`/api/finance/dunning/${id}/preview`, '_blank')
    } else if (action === 'send') {
      const isValid = validate(formData)
      if (!isValid.isValid) {
        showValidationToast(isValid.errors)
        return
      }

      try {
        await saveData({ ...formData, status: 'sent', sentDate: new Date().toISOString().split('T')[0] })
        setIsDirty(false)
        toast({
          title: t('crud.messages.dunningSent'),
          description: t('crud.messages.dunningSentDesc'),
        })
        navigate('/finance/dunning')
      } catch (error) {
        // Error wird bereits in useMaskData behandelt
      }
    } else if (action === 'payment') {
      // Zahlung buchen
      if (!id || id === 'new') {
        toast({
          variant: 'destructive',
          title: t('common.error'),
          description: t('crud.messages.saveFirst'),
        })
        return
      }

      try {
        const response = await fetch(`/api/finance/dunning/${id}/payment`, {
          method: 'POST',
          headers: {
            'Content-Type': 'application/json',
            'Authorization': `Bearer ${localStorage.getItem('token')}`,
          },
          body: JSON.stringify({
            betrag: formData.totalAmount || 0,
            datum: new Date().toISOString().split('T')[0]
          })
        })

        if (response.ok) {
          formData.status = 'paid'
          formData.paymentDate = new Date().toISOString().split('T')[0]
          toast({
            title: t('crud.messages.paymentBooked'),
            description: t('crud.messages.paymentBookedDesc'),
          })
        } else {
          const error = await response.json()
          toast({
            variant: 'destructive',
            title: t('crud.messages.paymentError'),
            description: error.detail || t('crud.messages.paymentErrorDesc'),
          })
        }
      } catch (error) {
        toast({
          variant: 'destructive',
          title: t('crud.messages.networkError'),
          description: t('crud.messages.networkErrorDesc'),
        })
      }
    } else if (action === 'escalate') {
      if (window.confirm(t('crud.messages.escalateConfirm'))) {
        try {
          await saveData({ ...formData, status: 'escalated' })
          setIsDirty(false)
          toast({
            title: t('crud.messages.dunningEscalated'),
            description: t('crud.messages.dunningEscalatedDesc'),
          })
          navigate('/finance/dunning')
        } catch (error) {
          // Error wird bereits in useMaskData behandelt
        }
      }
    } else if (action === 'collection') {
      if (window.confirm(t('crud.messages.collectionConfirm'))) {
        try {
          await saveData({ ...formData, status: 'collection' })
          setIsDirty(false)
          toast({
            title: t('crud.messages.collectionHandedOver'),
            description: t('crud.messages.collectionHandedOverDesc'),
          })
          navigate('/finance/dunning')
        } catch (error) {
          // Error wird bereits in useMaskData behandelt
        }
      }
    } else if (action === 'export') {
      if (!id || id === 'new') {
        toast({
          variant: 'destructive',
          title: t('common.error'),
          description: t('crud.messages.saveFirst'),
        })
        return
      }
      window.open(`/api/finance/dunning/${id}/export`, '_blank')
    }
  })

  const handleSave = async (formData: Record<string, unknown>) => {
    await handleAction('send', formData)
  }

  const handleCancel = () => {
    if (isDirty && !confirm(t('crud.messages.unsavedChanges'))) {
      return
    }
    navigate('/finance/dunning')
  }

  return (
    <ObjectPage
      config={dunningConfig}
      data={data}
      onSave={handleSave}
      onCancel={handleCancel}
      isLoading={loading}
    />
  )
}