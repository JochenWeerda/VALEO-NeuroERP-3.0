import { useState } from 'react'
import { useNavigate } from 'react-router-dom'
import { useTranslation } from 'react-i18next'
import { ObjectPage } from '@/components/mask-builder'
import { useMaskData, useMaskValidation, useMaskActions } from '@/components/mask-builder/hooks'
import { MaskConfig } from '@/components/mask-builder/types'
import { getEntityTypeLabel } from '@/features/crud/utils/i18n-helpers'
import { z } from 'zod'

const entityType = 'taxKey'

export default function SteuerschluesselPage(): JSX.Element {
  const { t } = useTranslation()
  const navigate = useNavigate()
  const [isDirty, setIsDirty] = useState(false)
  const entityTypeLabel = getEntityTypeLabel(t, entityType, 'Steuerschlüssel')

  // Zod-Schema für Steuerschlüssel
  const steuerschluesselSchema = z.object({
    code: z.string().regex(/^\d{1,2}$/, t('crud.validation.taxKeyCodeFormat')),
    bezeichnung: z.string().min(1, t('crud.validation.required', { field: t('crud.fields.description') })),
    steuersatz: z.number().min(0).max(100, t('crud.validation.taxRateRange')),
    ustvaPosition: z.string().min(1, t('crud.validation.required', { field: t('crud.fields.ustvaPosition') })),
    ustvaBezeichnung: z.string().min(1, t('crud.validation.required', { field: t('crud.fields.ustvaBezeichnung') })),
    intracom: z.boolean().default(false),
    export: z.boolean().default(false),
    reverseCharge: z.boolean().default(false),
    gueltigVon: z.string().regex(/^\d{4}-\d{2}-\d{2}$/, t('crud.validation.dateFormat')),
    gueltigBis: z.string().optional(),
    notizen: z.string().optional(),
    debitAccount: z.string().optional(),
    creditAccount: z.string().optional(),
    country: z.string().default('DE'),
    region: z.string().optional()
  })

  // Konfiguration für Steuerschlüssel ObjectPage
  const steuerschluesselConfig: MaskConfig = {
    title: entityTypeLabel,
    subtitle: t('crud.tooltips.taxKeyManagement'),
    type: 'object-page',
    tabs: [
      {
        key: 'allgemein',
        label: t('crud.detail.basicInfo'),
        fields: [
          {
            name: 'code',
            label: t('crud.fields.taxKeyCode'),
            type: 'text',
            required: true,
            placeholder: t('crud.placeholders.taxKeyCode'),
            maxLength: 2,
            helpText: t('crud.tooltips.fields.taxKeyCode')
          },
          {
            name: 'bezeichnung',
            label: t('crud.fields.description'),
            type: 'text',
            required: true,
            placeholder: t('crud.placeholders.taxKeyDescription')
          },
          {
            name: 'steuersatz',
            label: t('crud.fields.taxRate'),
            type: 'number',
            required: true,
            min: 0,
            max: 100,
            step: 0.01,
            placeholder: '19.00',
            helpText: t('crud.tooltips.fields.taxRate')
          },
          {
            name: 'country',
            label: t('crud.fields.country'),
            type: 'select',
            required: true,
            options: [
              { value: 'DE', label: t('crud.fields.countryDE') },
              { value: 'AT', label: t('crud.fields.countryAT') },
              { value: 'CH', label: t('crud.fields.countryCH') },
              { value: 'NL', label: t('crud.fields.countryNL') },
              { value: 'FR', label: t('crud.fields.countryFR') }
            ],
            helpText: t('crud.tooltips.fields.taxKeyCountry')
          },
          {
            name: 'region',
            label: t('crud.fields.region'),
            type: 'text',
            placeholder: t('crud.placeholders.region'),
            helpText: t('crud.tooltips.fields.region')
          },
          {
            name: 'gueltigVon',
            label: t('crud.fields.validFrom'),
            type: 'date',
            required: true
          },
          {
            name: 'gueltigBis',
            label: t('crud.fields.validUntil'),
            type: 'date',
            helpText: t('crud.tooltips.fields.validUntil')
          }
        ],
        layout: 'grid',
        columns: 2
      },
      {
        key: 'ustva',
        label: t('crud.fields.ustvaMapping'),
        fields: [
          {
            name: 'ustvaPosition',
            label: t('crud.fields.ustvaPosition'),
            type: 'text',
            required: true,
            placeholder: t('crud.placeholders.ustvaPosition'),
            helpText: t('crud.tooltips.fields.ustvaPosition')
          },
          {
            name: 'ustvaBezeichnung',
            label: t('crud.fields.ustvaBezeichnung'),
            type: 'text',
            required: true,
            placeholder: t('crud.placeholders.ustvaBezeichnung'),
            helpText: t('crud.tooltips.fields.ustvaBezeichnung')
          }
        ]
      },
      {
        key: 'sonderfaelle',
        label: t('crud.fields.specialCases'),
        fields: [
          {
            name: 'intracom',
            label: t('crud.fields.intracomDelivery'),
            type: 'boolean',
            helpText: t('crud.tooltips.fields.intracomDelivery')
          },
          {
            name: 'export',
            label: t('crud.fields.export'),
            type: 'boolean',
            helpText: t('crud.tooltips.fields.export')
          },
          {
            name: 'reverseCharge',
            label: t('crud.fields.reverseCharge'),
            type: 'boolean',
            helpText: t('crud.tooltips.fields.reverseCharge')
          }
        ]
      },
      {
        key: 'konten',
        label: t('crud.fields.accounts'),
        fields: [
          {
            name: 'debitAccount',
            label: t('crud.fields.debitAccount'),
            type: 'text',
            placeholder: t('crud.placeholders.accountNumber'),
            helpText: t('crud.tooltips.fields.debitAccount')
          },
          {
            name: 'creditAccount',
            label: t('crud.fields.creditAccount'),
            type: 'text',
            placeholder: t('crud.placeholders.accountNumber'),
            helpText: t('crud.tooltips.fields.creditAccount')
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
            name: 'notizen',
            label: t('crud.fields.internalNotes'),
            type: 'textarea',
            placeholder: t('crud.placeholders.internalNotes')
          }
        ]
      }
    ],
    actions: [
      {
        key: 'validate',
        label: t('crud.actions.validate'),
        type: 'secondary'
      },
      {
        key: 'save',
        label: t('crud.actions.save'),
        type: 'primary'
      },
      {
        key: 'ustva-export',
        label: t('crud.actions.ustvaExport'),
        type: 'secondary'
      }
    ],
    api: {
      baseUrl: '/api/v1/finance/tax-keys',
      endpoints: {
        list: '/api/v1/finance/tax-keys',
        get: '/api/v1/finance/tax-keys/{id}',
        create: '/api/v1/finance/tax-keys',
        update: '/api/v1/finance/tax-keys/{id}',
        delete: '/api/v1/finance/tax-keys/{id}'
      }
    } as any,
    validation: steuerschluesselSchema,
    permissions: ['fibu.read', 'fibu.write']
  }

  const { data, loading, saveData } = useMaskData({
    apiUrl: steuerschluesselConfig.api.baseUrl,
    id: 'new'
  })

  const { validate, showValidationToast } = useMaskValidation(steuerschluesselConfig.validation)

  const { handleAction } = useMaskActions(async (action: string, formData: any) => {
    if (action === 'save') {
      const isValid = validate(formData)
      if (!isValid.isValid) {
        showValidationToast(isValid.errors)
        return
      }

      try {
        // Transform form data to match API schema
        const apiData = {
          code: formData.code,
          bezeichnung: formData.bezeichnung,
          steuersatz: parseFloat(formData.steuersatz),
          ustva_position: formData.ustvaPosition,
          ustva_bezeichnung: formData.ustvaBezeichnung,
          intracom: formData.intracom || false,
          export: formData.export || false,
          reverse_charge: formData.reverseCharge || false,
          gueltig_von: formData.gueltigVon,
          gueltig_bis: formData.gueltigBis || null,
          notizen: formData.notizen || null,
          debit_account: formData.debitAccount || null,
          credit_account: formData.creditAccount || null,
          country: formData.country || 'DE',
          region: formData.region || null
        }

        await saveData(apiData)
        setIsDirty(false)
        navigate('/finance/steuerschluessel')
      } catch (error) {
        // Error wird bereits in useMaskData behandelt
      }
    } else if (action === 'validate') {
      const isValid = validate(formData)
      if (isValid.isValid) {
        // Show success message via toast
        const { toast } = await import('@/components/ui/toast')
        toast({
          title: t('crud.messages.validationSuccess'),
          description: t('crud.messages.taxKeyValid'),
        })
      } else {
        showValidationToast(isValid.errors)
      }
    } else if (action === 'ustva-export') {
      // UStVA Export - redirect to export endpoint
      window.open('/api/v1/finance/tax-keys/export', '_blank')
    }
  })

  const handleSave = async (formData: any) => {
    await handleAction('save', formData)
  }

  const handleCancel = () => {
    if (isDirty && !confirm(t('crud.messages.unsavedChanges'))) {
      return
    }
    navigate('/finance/steuerschluessel')
  }

  return (
    <ObjectPage
      config={steuerschluesselConfig}
      data={data}
      onSave={handleSave}
      onCancel={handleCancel}
      isLoading={loading}
    />
  )
}
