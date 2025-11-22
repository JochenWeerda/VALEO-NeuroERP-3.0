import { useState } from 'react'
import { useNavigate } from 'react-router-dom'
import { useTranslation } from 'react-i18next'
import { ObjectPage } from '@/components/mask-builder'
import { useMaskData, useMaskValidation, useMaskActions } from '@/components/mask-builder/hooks'
import { MaskConfig } from '@/components/mask-builder/types'
import { z } from 'zod'
import { toast } from '@/hooks/use-toast'
import { getEntityTypeLabel } from '@/features/crud/utils/i18n-helpers'

// Zod-Schema für Mahnwesen (wird in Komponente mit i18n erstellt)
const createMahnwesenSchema = (t: any) => z.object({
  opId: z.string().min(1, t('crud.messages.validationError')),
  debitorId: z.string().min(1, t('crud.messages.validationError')),
  mahnstufe: z.number().min(1).max(3, t('crud.messages.validationError')),
  mahnDatum: z.string().regex(/^\d{4}-\d{2}-\d{2}$/, t('crud.messages.validationError')),
  faelligkeit: z.string().regex(/^\d{4}-\d{2}-\d{2}$/, t('crud.messages.validationError')),
  betrag: z.number().positive(t('crud.messages.validationError')),
  mahngebuehr: z.number().min(0, t('crud.messages.validationError')).default(0),
  zinsen: z.number().min(0, t('crud.messages.validationError')).default(0),
  gesamtForderung: z.number().positive(t('crud.messages.validationError')),
  text: z.string().min(1, t('crud.messages.validationError')),
  frist: z.string().optional(),
  status: z.enum(['erstellt', 'versendet', 'bezahlt', 'inkasso']),
  versandDatum: z.string().optional(),
  zahlungEingang: z.string().optional(),
  notizen: z.string().optional()
})

// Konfiguration für Mahnwesen ObjectPage (wird in Komponente mit i18n erstellt)
const createMahnwesenConfig = (t: any, entityTypeLabel: string): MaskConfig => ({
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
          type: 'select',
          required: true,
          options: [
            { value: 'K001', label: 'K001 - Müller GmbH' },
            { value: 'K002', label: 'K002 - Schmidt KG' },
            { value: 'K003', label: 'K003 - Bauer e.K.' }
          ]
        },
        {
          name: 'mahnstufe',
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
          name: 'mahnDatum',
          label: t('crud.fields.dunningDate'),
          type: 'date',
          required: true
        },
        {
          name: 'faelligkeit',
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
            { value: 'erstellt', label: t('status.recorded') },
            { value: 'versendet', label: t('status.sent') },
            { value: 'bezahlt', label: t('status.paid') },
            { value: 'inkasso', label: t('crud.fields.collection') }
          ]
        }
      ],
      layout: 'grid',
      columns: 2
    },
    {
      key: 'betrag',
      label: t('crud.fields.amount'),
      fields: [
        {
          name: 'betrag',
          label: t('crud.fields.openAmount'),
          type: 'number',
          required: true,
          step: 0.01,
          readonly: true,
          helpText: t('crud.tooltips.fields.amountFromOp')
        },
        {
          name: 'mahngebuehr',
          label: t('crud.fields.dunningFee'),
          type: 'number',
          step: 0.01,
          placeholder: t('crud.tooltips.placeholders.dunningFee'),
          helpText: t('crud.tooltips.fields.dunningFee')
        },
        {
          name: 'zinsen',
          label: t('crud.fields.interest'),
          type: 'number',
          step: 0.01,
          placeholder: t('crud.tooltips.placeholders.interest'),
          helpText: t('crud.tooltips.fields.interest')
        },
        {
          name: 'gesamtForderung',
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
          name: 'frist',
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
          name: 'versandDatum',
          label: t('crud.fields.sentDate'),
          type: 'date'
        },
        {
          name: 'zahlungEingang',
          label: t('crud.fields.paymentReceived'),
          type: 'date'
        }
      ]
    },
    {
      key: 'notizen',
      label: t('crud.fields.notes'),
      fields: [
        {
          name: 'notizen',
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
      type: 'secondary'
    , onClick: () => {} },
    {
      key: 'preview',
      label: t('crud.actions.preview'),
      type: 'secondary'
    , onClick: () => {} },
    {
      key: 'send',
      label: t('crud.actions.send'),
      type: 'primary'
    , onClick: () => {} },
    {
      key: 'payment',
      label: t('crud.actions.bookPayment'),
      type: 'secondary'
    , onClick: () => {} },
    {
      key: 'inkasso',
      label: t('crud.actions.handOverToCollection'),
      type: 'danger'
    , onClick: () => {} },
    {
      key: 'export',
      label: t('crud.actions.pdfExport'),
      type: 'secondary'
    , onClick: () => {} }
  ],
  api: {
    baseUrl: '/api/finance/mahnwesen',
    endpoints: {
      list: '/api/finance/mahnwesen',
      get: '/api/finance/mahnwesen/{id}',
      create: '/api/finance/mahnwesen',
      update: '/api/finance/mahnwesen/{id}',
      delete: '/api/finance/mahnwesen/{id}'
    }
  } as any,
  validation: createMahnwesenSchema(t),
  permissions: ['fibu.read', 'fibu.write']
})

export default function MahnwesenPage(): JSX.Element {
  const { t } = useTranslation()
  const navigate = useNavigate()
  const [isDirty, setIsDirty] = useState(false)
  const entityType = 'dunning'
  const entityTypeLabel = getEntityTypeLabel(t, entityType, 'Mahnwesen')
  const mahnwesenConfig = createMahnwesenConfig(t, entityTypeLabel)

  const { data, loading, saveData } = useMaskData({
    apiUrl: mahnwesenConfig.api.baseUrl,
    id: 'new'
  })

  const { validate, showValidationToast } = useMaskValidation(mahnwesenConfig.validation)

  const { handleAction } = useMaskActions(async (action: string, formData: any) => {
    if (action === 'generate') {
      // Mahnung generieren - berechne Gesamtforderung
      const gesamtForderung = (formData.betrag || 0) + (formData.mahngebuehr || 0) + (formData.zinsen || 0)
      formData.gesamtForderung = gesamtForderung

      // Generiere Standard-Mahntext basierend auf Mahnstufe
      if (!formData.text || formData.text.trim() === '') {
        const mahnstufe = formData.mahnstufe || 1
        const betrag = formData.betrag || 0
        const frist = formData.frist || '7 Tage'

        formData.text = t('crud.messages.dunningTextTemplate', {
          mahnstufeText: mahnstufe > 1 ? t('crud.messages.dunningTextPrevious', { level: mahnstufe - 1 }) + ' ' : '',
          betrag: betrag.toFixed(2),
          frist: frist
        })
      }

      toast({
        title: t('crud.messages.dunningGenerated'),
        description: t('crud.messages.dunningGeneratedDesc', { level: formData.mahnstufe }),
      })
    } else if (action === 'preview') {
      // Vorschau
      if (!formData.id) {
        toast({
          variant: 'destructive',
          title: t('common.error'),
          description: t('crud.messages.saveFirst'),
        })
        return
      }
      window.open(`/api/finance/mahnwesen/${formData.id}/preview`, '_blank')
    } else if (action === 'send') {
      const isValid = validate(formData)
      if (!isValid.isValid) {
        showValidationToast(isValid.errors)
        return
      }

      try {
        await saveData(formData)
        setIsDirty(false)
        toast({
          title: t('crud.messages.dunningSent'),
          description: t('crud.messages.dunningSentDesc'),
        })
        navigate('/finance/mahnwesen')
      } catch (error) {
        // Error wird bereits in useMaskData behandelt
      }
    } else if (action === 'payment') {
      // Zahlung buchen
      if (!formData.id) {
        toast({
          variant: 'destructive',
          title: t('common.error'),
          description: t('crud.messages.saveFirst'),
        })
        return
      }

      try {
        const response = await fetch(`/api/finance/mahnwesen/${formData.id}/payment`, {
          method: 'POST',
          headers: {
            'Content-Type': 'application/json',
            'Authorization': `Bearer ${localStorage.getItem('token')}`,
          },
          body: JSON.stringify({
            betrag: formData.gesamtForderung || 0,
            datum: new Date().toISOString().split('T')[0]
          })
        })

        if (response.ok) {
          formData.status = 'bezahlt'
          formData.zahlungEingang = new Date().toISOString().split('T')[0]
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
    } else if (action === 'inkasso') {
      // Inkasso übergeben
      if (!formData.id) {
        toast({
          variant: 'destructive',
          title: t('common.error'),
          description: t('crud.messages.saveFirst'),
        })
        return
      }

      try {
        const response = await fetch(`/api/finance/mahnwesen/${formData.id}/inkasso`, {
          method: 'POST',
          headers: {
            'Content-Type': 'application/json',
            'Authorization': `Bearer ${localStorage.getItem('token')}`,
          },
        })

        if (response.ok) {
          formData.status = 'inkasso'
          toast({
            title: t('crud.messages.collectionHandedOver'),
            description: t('crud.messages.collectionHandedOverDesc'),
          })
        } else {
          const error = await response.json()
          toast({
            variant: 'destructive',
            title: t('crud.messages.collectionError'),
            description: error.detail || t('crud.messages.collectionErrorDesc'),
          })
        }
      } catch (error) {
        toast({
          variant: 'destructive',
          title: t('crud.messages.networkError'),
          description: t('crud.messages.networkErrorDesc'),
        })
      }
    } else if (action === 'export') {
      if (!formData.id) {
        toast({
          variant: 'destructive',
          title: t('common.error'),
          description: t('crud.messages.saveFirst'),
        })
        return
      }
      window.open(`/api/finance/mahnwesen/${formData.id}/export`, '_blank')
    }
  })

  const handleSave = async (formData: any) => {
    await handleAction('send', formData)
  }

  const handleCancel = () => {
    if (isDirty && !confirm(t('crud.messages.unsavedChanges'))) {
      return
    }
    navigate('/finance/mahnwesen')
  }

  return (
    <ObjectPage
      config={mahnwesenConfig}
      data={data}
      onSave={handleSave}
      onCancel={handleCancel}
      isLoading={loading}
    />
  )
}