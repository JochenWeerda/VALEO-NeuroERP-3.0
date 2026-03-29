import { useState } from 'react'
import { useNavigate, useParams } from 'react-router-dom'
import { useTranslation } from 'react-i18next'
import { ObjectPage } from '@/components/mask-builder'
import { useMaskData, useMaskActions } from '@/components/mask-builder/hooks'
import { MaskConfig } from '@/components/mask-builder/types'
import { getFieldsFromMaskConfig, validateFields } from '@/components/mask-builder/validation'
import { toast } from '@/hooks/use-toast'
import { getEntityTypeLabel } from '@/features/crud/utils/i18n-helpers'

const createCreditNoteConfig = (t: any, entityTypeLabel: string): MaskConfig => ({
  title: `${t('crud.actions.create')}/${t('crud.actions.edit')} ${entityTypeLabel}`,
  subtitle: t('crud.tooltips.fields.creditNote'),
  type: 'object-page',
  tabs: [
    {
      key: 'grunddaten',
      label: t('crud.detail.basicInfo'),
      fields: [
        {
          name: 'number',
          label: t('crud.fields.number'),
          type: 'text',
          required: true,
          placeholder: t('crud.tooltips.placeholders.creditNoteNumber')
        },
        {
          name: 'date',
          label: t('crud.fields.date'),
          type: 'date',
          required: true
        },
        {
          name: 'customerId',
          label: t('crud.entities.customer'),
          type: 'lookup',
          required: true,
          endpoint: '/api/v1/crm/customers',
          displayField: 'name',
          valueField: 'id'
        },
        {
          name: 'sourceInvoice',
          label: t('crud.fields.sourceInvoice'),
          type: 'lookup',
          endpoint: '/api/v1/finance/invoices',
          displayField: 'number',
          valueField: 'id',
          helpText: t('crud.tooltips.fields.sourceInvoice')
        },
        {
          name: 'reason',
          label: t('crud.fields.reason'),
          type: 'select',
          required: true,
          options: [
            { value: 'return', label: t('crud.fields.reasonReturn') },
            { value: 'discount', label: t('crud.fields.reasonDiscount') },
            { value: 'error', label: t('crud.fields.reasonError') },
            { value: 'complaint', label: t('crud.fields.reasonComplaint') },
            { value: 'other', label: t('crud.dialogs.amend.types.other') }
          ]
        },
        {
          name: 'reasonText',
          label: t('crud.fields.reasonDetails'),
          type: 'textarea',
          placeholder: t('crud.tooltips.placeholders.creditNoteReason')
        },
        {
          name: 'status',
          label: t('crud.fields.status'),
          type: 'select',
          required: true,
          options: [
            { value: 'draft', label: t('status.draft') },
            { value: 'approved', label: t('status.approved') },
            { value: 'sent', label: t('status.sent') },
            { value: 'paid', label: t('status.paid') },
            { value: 'cancelled', label: t('status.cancelled') }
          ]
        }
      ],
      layout: 'grid',
      columns: 2
    },
    {
      key: 'positionen',
      label: t('crud.fields.items'),
      fields: [
        {
          name: 'lines',
          label: t('crud.fields.creditNoteItems'),
          type: 'table',
          required: true,
          columns: [
            { key: 'article', label: t('crud.fields.product'), type: 'lookup', required: true },
            { key: 'qty', label: t('crud.fields.quantity'), type: 'number', required: true },
            { key: 'price', label: t('crud.fields.price'), type: 'number', required: true },
            { key: 'vatRate', label: `${t('crud.fields.taxRate')  } %`, type: 'number', required: true },
            { key: 'discount', label: `${t('crud.fields.discount')  } %`, type: 'number' }
          ],
          minRows: 1,
          helpText: t('crud.tooltips.fields.creditNoteItems')
        }
      ]
    },
    {
      key: 'betrag',
      label: t('crud.fields.amounts'),
      fields: [
        {
          name: 'subtotalNet',
          label: t('crud.fields.netAmount'),
          type: 'number',
          required: true,
          step: 0.01,
          readonly: true,
          helpText: t('crud.tooltips.fields.subtotalNet')
        },
        {
          name: 'totalDiscount',
          label: t('crud.fields.totalDiscount'),
          type: 'number',
          step: 0.01,
          readonly: true,
          helpText: t('crud.tooltips.fields.totalDiscount')
        },
        {
          name: 'totalTax',
          label: t('crud.fields.totalTax'),
          type: 'number',
          required: true,
          step: 0.01,
          readonly: true,
          helpText: t('crud.tooltips.fields.totalTax')
        },
        {
          name: 'totalGross',
          label: t('crud.fields.grossAmount'),
          type: 'number',
          required: true,
          step: 0.01,
          readonly: true,
          helpText: t('crud.tooltips.fields.totalGross')
        }
      ],
      layout: 'grid',
      columns: 2
    },
    {
      key: 'zahlung',
      label: t('crud.fields.paymentAndDue'),
      fields: [
        {
          name: 'paymentTerms',
          label: t('crud.fields.paymentTerms'),
          type: 'select',
          required: true,
          options: [
            { value: 'immediate', label: t('crud.fields.paymentTermsImmediate') },
            { value: 'net30', label: t('crud.fields.paymentTermsNet30') },
            { value: 'net60', label: t('crud.fields.paymentTermsNet60') },
            { value: 'net90', label: t('crud.fields.paymentTermsNet90') }
          ]
        },
        {
          name: 'dueDate',
          label: t('crud.fields.dueDate'),
          type: 'date',
          required: true
        }
      ]
    },
    {
      key: 'notizen',
      label: t('crud.fields.notes'),
      fields: [
        {
          name: 'notes',
          label: t('crud.fields.internalNotes'),
          type: 'textarea',
          placeholder: t('crud.tooltips.placeholders.creditNoteNotes')
        }
      ]
    }
  ],
  actions: [
    {
      key: 'calculate',
      label: t('crud.actions.recalculate'),
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
      key: 'approve',
      label: t('crud.actions.approve'),
      type: 'primary',
      onClick: () => {}
    },
    {
      key: 'send',
      label: t('crud.actions.send'),
      type: 'primary',
      onClick: () => {}
    },
    {
      key: 'print',
      label: t('crud.actions.print'),
      type: 'secondary',
      onClick: () => {}
    },
    {
      key: 'cancel',
      label: t('crud.actions.cancel'),
      type: 'danger',
      onClick: () => {}
    }
  ],
  api: {
    baseUrl: '/api/v1/sales/credit-notes',
    endpoints: {
      list: '/api/v1/sales/credit-notes',
      get: '/api/v1/sales/credit-notes/{id}',
      create: '/api/v1/sales/credit-notes',
      update: '/api/v1/sales/credit-notes/{id}',
      delete: '/api/v1/sales/credit-notes/{id}'
    }
  },
  permissions: ['sales.write', 'sales.credit_notes']
})

export default function CreditNoteEditorPage(): JSX.Element {
  const { t } = useTranslation()
  const navigate = useNavigate()
  const { id } = useParams()
  const [isDirty, setIsDirty] = useState(false)
  const entityType = 'creditNote'
  const entityTypeLabel = getEntityTypeLabel(t, entityType, 'Gutschrift')
  const creditNoteConfig = createCreditNoteConfig(t, entityTypeLabel)

  const { data, loading, saveData } = useMaskData({
    apiUrl: creditNoteConfig.api.baseUrl,
    id: id ?? 'new'
  })

  const validate = (formData: any) => validateFields(getFieldsFromMaskConfig(creditNoteConfig), formData ?? {})
  const showValidationToast = (errors: Record<string, string>) => {
    toast({ variant: 'destructive', title: t('crud.messages.validationError'), description: `${Object.keys(errors).length} Feld(er) muessen korrigiert werden.` })
  }

  const { handleAction } = useMaskActions(async (action: string, formData: Record<string, unknown>) => {
    if (action === 'calculate') {
      toast({ title: 'Neuberechnung', description: t('crud.messages.recalculateFunction', { defaultValue: 'Beträge werden neu berechnet.' }) })
    } else if (action === 'preview') {
      // Vorschau anzeigen
      window.open('/api/v1/sales/credit-notes/preview', '_blank')
    } else if (action === 'approve') {
      const errors = validate(formData)
      if (Object.keys(errors).length > 0) {
        showValidationToast(errors)
        return
      }

      try {
        await saveData({ ...formData, status: 'approved' })
        setIsDirty(false)
        navigate('/sales/credit-notes')
      } catch (error) {
        // Error wird bereits in useMaskData behandelt
      }
    } else if (action === 'send') {
      const errors = validate(formData)
      if (Object.keys(errors).length > 0) {
        showValidationToast(errors)
        return
      }

      try {
        await saveData({ ...formData, status: 'sent' })
        setIsDirty(false)
        navigate('/sales/credit-notes')
      } catch (error) {
        // Error wird bereits in useMaskData behandelt
      }
    } else if (action === 'print') {
      window.open('/api/v1/sales/credit-notes/print', '_blank')
    } else if (action === 'cancel') {
      if (window.confirm(t('crud.dialogs.cancel.descriptionGeneric', { entityType: entityTypeLabel }))) {
        try {
          await saveData({ ...formData, status: 'cancelled' })
          setIsDirty(false)
          navigate('/sales/credit-notes')
        } catch (error) {
          // Error wird bereits in useMaskData behandelt
        }
      }
    }
  })

  const handleSave = async (formData: Record<string, unknown>) => {
    await handleAction('approve', formData)
  }

  const handleCancel = () => {
    if (isDirty && !confirm(t('crud.messages.discardChanges'))) {
      return
    }
    navigate('/sales/credit-notes')
  }

  return (
    <ObjectPage
      config={creditNoteConfig}
      data={data}
      onSave={handleSave}
      onCancel={handleCancel}
      onAction={handleAction}
      isLoading={loading}
    />
  )
}