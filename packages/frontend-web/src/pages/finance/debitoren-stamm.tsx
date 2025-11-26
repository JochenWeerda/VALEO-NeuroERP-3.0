import { useState, useEffect } from 'react'
import { useNavigate } from 'react-router-dom'
import { useTranslation } from 'react-i18next'
import { ObjectPage } from '@/components/mask-builder'
import { useMaskData, useMaskValidation, useMaskActions } from '@/components/mask-builder/hooks'
import { MaskConfig } from '@/components/mask-builder/types'
import { z } from 'zod'
import { getEntityTypeLabel } from '@/features/crud/utils/i18n-helpers'
import { validateIBAN, formatIBAN } from '@/lib/utils/iban-validator'
import { useIbanLookup } from '@/hooks/useIbanLookup'
import { toast } from 'sonner'

// Zod-Schema für Debitoren-Stammdaten (wird in Komponente mit i18n erstellt)
const createDebitorenSchema = (t: any) => z.object({
  debtor_number: z.string().regex(/^\d{6,8}$/, t('crud.messages.validationError')),
  company_name: z.string().min(1, t('crud.messages.validationError')),
  contact_person: z.string().optional(),
  street: z.string().min(1, t('crud.messages.validationError')),
  postal_code: z.string().regex(/^\d{5}$/, t('crud.messages.validationError')),
  city: z.string().min(1, t('crud.messages.validationError')),
  country: z.string().default("DE"),
  phone: z.string().optional(),
  email: z.string().email().optional().or(z.literal("")),
  vat_id: z.string().optional(),
  tax_number: z.string().optional(),

  // Bankverbindung
  iban: z.string()
    .optional()
    .or(z.literal(""))
    .refine((val) => !val || val.trim() === "" || validateIBAN(val), {
      message: t('crud.messages.invalidIban'),
    }),
  bic: z.string().optional(),
  bank_name: z.string().optional(),
  account_holder: z.string().optional(),

  // Konditionen
  payment_terms_days: z.number().min(0, t('crud.messages.validationError')).default(30),
  discount_days: z.number().min(0).default(0),
  discount_percent: z.number().min(0).max(100).default(0),
  credit_limit: z.number().min(0).default(0),

  // Status
  is_active: z.boolean().default(true),
  notes: z.string().optional()
})

// Konfiguration für Debitoren-Stammdaten ObjectPage (wird in Komponente mit i18n erstellt)
const createDebitorenConfig = (t: any, entityTypeLabel: string): MaskConfig => ({
  title: entityTypeLabel,
  subtitle: t('crud.actions.edit'),
  type: 'object-page',
  tabs: [
    {
      key: 'stammdaten',
      label: t('crud.detail.basicInfo'),
      fields: [
        {
          name: 'debtor_number',
          label: t('crud.fields.debtorNumber'),
          type: 'text',
          required: true,
          placeholder: t('crud.tooltips.placeholders.debtorNumber'),
          maxLength: 8
        },
        {
          name: 'company_name',
          label: t('crud.fields.company'),
          type: 'text',
          required: true,
          placeholder: t('crud.tooltips.placeholders.company')
        },
        {
          name: 'contact_person',
          label: t('crud.fields.contactPerson'),
          type: 'text',
          placeholder: t('crud.tooltips.placeholders.contactPerson')
        },
        {
          name: 'street',
          label: t('crud.fields.street'),
          type: 'text',
          required: true,
          placeholder: t('crud.tooltips.placeholders.street')
        },
        {
          name: 'postal_code',
          label: t('crud.fields.postalCode'),
          type: 'text',
          required: true,
          placeholder: t('crud.tooltips.placeholders.postalCode'),
          maxLength: 5
        },
        {
          name: 'city',
          label: t('crud.fields.city'),
          type: 'text',
          required: true,
          placeholder: t('crud.tooltips.placeholders.city')
        },
        {
          name: 'country',
          label: t('crud.fields.country'),
          type: 'select',
          options: [
            { value: 'DE', label: t('crud.fields.countryDE') },
            { value: 'AT', label: t('crud.fields.countryAT') },
            { value: 'CH', label: t('crud.fields.countryCH') },
            { value: 'NL', label: t('crud.fields.countryNL') },
            { value: 'FR', label: t('crud.fields.countryFR') }
          ]
        }
      ],
      layout: 'grid',
      columns: 2
    },
    {
      key: 'kontakt',
      label: t('crud.fields.contact'),
      fields: [
        {
          name: 'phone',
          label: t('crud.fields.phone'),
          type: 'text',
          placeholder: t('crud.tooltips.placeholders.phone')
        },
        {
          name: 'email',
          label: t('crud.fields.email'),
          type: 'text',
          placeholder: t('crud.tooltips.placeholders.email')
        },
        {
          name: 'vat_id',
          label: t('crud.fields.vatId'),
          type: 'text',
          placeholder: t('crud.tooltips.placeholders.vatId')
        },
        {
          name: 'tax_number',
          label: t('crud.fields.taxNumber'),
          type: 'text',
          placeholder: t('crud.tooltips.placeholders.taxNumber')
        }
      ],
      layout: 'grid',
      columns: 2
    },
    {
      key: 'bankverbindung',
      label: t('crud.fields.bankDetails'),
      fields: [
        {
          name: 'iban',
          label: t('crud.fields.iban'),
          type: 'text',
          placeholder: t('crud.tooltips.placeholders.iban')
        },
        {
          name: 'bic',
          label: t('crud.fields.bic'),
          type: 'text',
          placeholder: t('crud.tooltips.placeholders.bic')
        },
        {
          name: 'bank_name',
          label: t('crud.fields.bankName'),
          type: 'text',
          placeholder: t('crud.tooltips.placeholders.bankName')
        },
        {
          name: 'account_holder',
          label: t('crud.fields.accountHolder'),
          type: 'text',
          placeholder: t('crud.tooltips.placeholders.accountHolder')
        }
      ],
      layout: 'grid',
      columns: 2
    },
    {
      key: 'konditionen',
      label: t('crud.fields.terms'),
      fields: [
        {
          name: 'payment_terms_days',
          label: t('crud.fields.paymentDueDays'),
          type: 'number'
        } as any,
        {
          name: 'discount_days',
          label: t('crud.fields.discountDays'),
          type: 'number'
        } as any,
        {
          name: 'discount_percent',
          label: t('crud.fields.discountPercent'),
          type: 'number'
        } as any,
        {
          name: 'credit_limit',
          label: t('crud.fields.creditLimit'),
          type: 'number'
        } as any
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
          placeholder: t('crud.tooltips.placeholders.debtorNotes')
        }
      ]
    }
  ],
  actions: [
    {
      key: 'validate',
      label: t('crud.actions.validate'),
      type: 'secondary',
      onClick: () => {}
    },
    {
      key: 'save',
      label: t('crud.actions.save'),
      type: 'primary',
      onClick: () => {}
    },
    {
      key: 'export',
      label: t('crud.actions.export'),
      type: 'secondary',
      onClick: () => {}
    }
  ],
  api: {
    baseUrl: '/api/v1/finance/debtors',
    endpoints: {
      list: '/api/v1/finance/debtors',
      get: '/api/v1/finance/debtors/{id}',
      create: '/api/v1/finance/debtors',
      update: '/api/v1/finance/debtors/{id}',
      delete: '/api/v1/finance/debtors/{id}'
    }
  } as any,
  validation: createDebitorenSchema(t),
  permissions: ['fibu.read', 'fibu.write']
})

export default function DebitorenStammPage(): JSX.Element {
  const { t } = useTranslation()
  const navigate = useNavigate()
  const [isDirty, setIsDirty] = useState(false)
  const [formData, setFormData] = useState<any>({})
  const entityType = 'debtor'
  const entityTypeLabel = getEntityTypeLabel(t, entityType, 'Debitor')
  const debitorenConfig = createDebitorenConfig(t, entityTypeLabel)

  const { data, loading, saveData, updateData } = useMaskData({
    apiUrl: debitorenConfig.api.baseUrl,
    id: 'new'
  })

  const { validate, showValidationToast } = useMaskValidation(debitorenConfig.validation)

  // IBAN Lookup Hook
  const { performLookup, isLoading: isIbanLoading, lookupData } = useIbanLookup({
    onSuccess: (result) => {
      if (result.valid && result.bank_name) {
        const updatedData = { ...formData }
        if (result.bank_name) {
          updatedData.bank_name = result.bank_name
        }
        if (result.bic) {
          updatedData.bic = result.bic
        }
        setFormData(updatedData)
        updateData?.(updatedData)
        
        toast.success(t('crud.messages.ibanLookupSuccess', { 
          defaultValue: 'Bankinformationen automatisch ausgefüllt',
          bankName: result.bank_name 
        }))
      }
    },
    onError: (error) => {
      console.warn('IBAN lookup failed:', error)
    },
    autoLookup: false
  })

  // Auto-lookup IBAN when it changes and seems complete
  useEffect(() => {
    const iban = formData?.iban
    if (iban && iban.replace(/\s/g, '').length >= 15) {
      const normalized = iban.replace(/\s/g, '').replace(/-/g, '').toUpperCase()
      if (normalized.length >= 15 && normalized.length <= 34 && validateIBAN(normalized)) {
        const timer = setTimeout(() => {
          performLookup(normalized)
        }, 1000)
        
        return () => clearTimeout(timer)
      }
    }
  }, [formData?.iban, performLookup])

  // Update form data when IBAN lookup succeeds
  useEffect(() => {
    if (lookupData?.valid && lookupData.bank_name && formData) {
      const updatedData = { ...formData }
      if (lookupData.bank_name && !updatedData.bank_name) {
        updatedData.bank_name = lookupData.bank_name
      }
      if (lookupData.bic && !updatedData.bic) {
        updatedData.bic = lookupData.bic
      }
      setFormData(updatedData)
      updateData?.(updatedData)
    }
  }, [lookupData, formData, updateData])

  // Handle form data changes for IBAN lookup
  const handleFormChange = (newData: any) => {
    setFormData(newData)
    setIsDirty(true)
    
    // Auto-lookup IBAN when it changes
    const iban = newData?.iban
    if (iban && iban.replace(/\s/g, '').length >= 15) {
      const normalized = iban.replace(/\s/g, '').replace(/-/g, '').toUpperCase()
      if (normalized.length >= 15 && normalized.length <= 34 && validateIBAN(normalized)) {
        const timer = setTimeout(() => {
          performLookup(normalized)
        }, 1000)
        
        return () => clearTimeout(timer)
      }
    }
  }

  const { handleAction } = useMaskActions(async (action: string, formData: any) => {
    if (action === 'save') {
      const isValid = validate(formData)
      if (!isValid.isValid) {
        showValidationToast(isValid.errors)
        return
      }

      try {
        // Format IBAN before saving
        if (formData.iban) {
          formData.iban = formatIBAN(formData.iban)
        }

        await saveData({
          ...formData,
          tenant_id: 'system' // TODO: Get from context
        })
        setIsDirty(false)
        toast.success(t('crud.messages.saveSuccess', { entityType: entityTypeLabel }))
        navigate('/finance/debitoren')
      } catch (error) {
        // Error wird bereits in useMaskData behandelt
      }
    } else if (action === 'validate') {
      const isValid = validate(formData)
      if (isValid.isValid) {
        toast.success(t('crud.messages.validationSuccess'))
      } else {
        showValidationToast(isValid.errors)
      }
    } else if (action === 'export') {
      window.open('/api/v1/finance/debtors/export', '_blank')
    }
  })

  const handleSave = async (formData: any) => {
    await handleAction('save', formData)
  }

  const handleCancel = () => {
    if (isDirty && !confirm(t('crud.messages.unsavedChanges'))) {
      return
    }
    navigate('/finance/debitoren')
  }

  return (
    <ObjectPage
      config={debitorenConfig}
      data={data || formData}
      onChange={handleFormChange}
      onSave={handleSave}
      onCancel={handleCancel}
      isLoading={loading || isIbanLoading}
    />
  )
}

