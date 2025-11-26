import { useState, useEffect } from 'react'
import { useNavigate } from 'react-router-dom'
import { useTranslation } from 'react-i18next'
import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query'
import { ObjectPage } from '@/components/mask-builder'
import { useMaskData, useMaskValidation, useMaskActions } from '@/components/mask-builder/hooks'
import { MaskConfig } from '@/components/mask-builder/types'
import { z } from 'zod'
import { getEntityTypeLabel } from '@/features/crud/utils/i18n-helpers'
import { validateIBAN, formatIBAN } from '@/lib/utils/iban-validator'
import { useIbanLookup } from '@/hooks/useIbanLookup'
import { apiClient } from '@/lib/api-client'
import { toast } from 'sonner'

// Zod-Schema für Bankkonten-Stammdaten
const createBankKontenSchema = (t: any) => z.object({
  account_number: z.string().min(1, t('crud.messages.validationError')),
  bank_name: z.string().min(1, t('crud.messages.validationError')),
  iban: z.string()
    .optional()
    .or(z.literal(""))
    .refine((val) => !val || val.trim() === "" || validateIBAN(val), {
      message: t('crud.messages.invalidIban'),
    }),
  bic: z.string().optional(),
  currency: z.string().length(3).default('EUR'),
  balance: z.number().default(0),
  is_active: z.boolean().default(true)
})

// Konfiguration für Bankkonten-Stammdaten ObjectPage
const createBankKontenConfig = (t: any, entityTypeLabel: string): MaskConfig => ({
  title: entityTypeLabel,
  subtitle: t('crud.fields.bankAccountMasterData'),
  type: 'object-page',
  tabs: [
    {
      key: 'grunddaten',
      label: t('crud.detail.basicInfo'),
      fields: [
        {
          name: 'account_number',
          label: t('crud.fields.accountNumber'),
          type: 'text',
          required: true,
          placeholder: t('crud.tooltips.placeholders.accountNumber')
        },
        {
          name: 'bank_name',
          label: t('crud.fields.bankName'),
          type: 'text',
          required: true,
          placeholder: t('crud.tooltips.placeholders.bankName')
        },
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
          name: 'currency',
          label: t('crud.fields.currency'),
          type: 'select',
          required: true,
          options: [
            { value: 'EUR', label: 'EUR - Euro' },
            { value: 'USD', label: 'USD - US Dollar' },
            { value: 'GBP', label: 'GBP - British Pound' },
            { value: 'CHF', label: 'CHF - Swiss Franc' }
          ]
        },
        {
          name: 'balance',
          label: t('crud.fields.balance'),
          type: 'number',
          step: 0.01,
          readonly: true,
          helpText: t('crud.tooltips.fields.balanceReadonly')
        },
        {
          name: 'is_active',
          label: t('crud.fields.isActive'),
          type: 'boolean',
          defaultValue: true
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
      type: 'primary',
      onClick: () => {}
    },
    {
      key: 'validate',
      label: t('crud.actions.validate'),
      type: 'secondary',
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
    baseUrl: '/api/v1/finance/bank-accounts',
    endpoints: {
      list: '/api/v1/finance/bank-accounts',
      get: '/api/v1/finance/bank-accounts/{id}',
      create: '/api/v1/finance/bank-accounts',
      update: '/api/v1/finance/bank-accounts/{id}',
      delete: '/api/v1/finance/bank-accounts/{id}'
    }
  } as any,
  validation: createBankKontenSchema(t),
  permissions: ['fibu.read', 'fibu.write']
})

export default function BankKontenStammPage(): JSX.Element {
  const { t } = useTranslation()
  const navigate = useNavigate()
  const queryClient = useQueryClient()
  const [isDirty, setIsDirty] = useState(false)
  const [formData, setFormData] = useState<any>({})
  const entityType = 'bankAccount'
  const entityTypeLabel = getEntityTypeLabel(t, entityType, 'Bankkonto')
  const bankKontenConfig = createBankKontenConfig(t, entityTypeLabel)

  const { data, loading, saveData, updateData } = useMaskData({
    apiUrl: bankKontenConfig.api.baseUrl,
    id: 'new'
  })

  const { validate, showValidationToast } = useMaskValidation(bankKontenConfig.validation)

  // IBAN Lookup Hook
  const { performLookup, isLoading: isIbanLoading, lookupData } = useIbanLookup({
    onSuccess: (result) => {
      if (result.valid && result.bank_name) {
        const updatedData = { ...formData }
        if (result.bank_name && !updatedData.bank_name) {
          updatedData.bank_name = result.bank_name
        }
        if (result.bic && !updatedData.bic) {
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
        }, 1000) // 1 second debounce
        
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
        }, 1000) // 1 second debounce
        
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
        navigate('/finance/bankkonten')
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
      window.open('/api/v1/finance/bank-accounts/export', '_blank')
    }
  })

  const handleSave = async (formData: any) => {
    await handleAction('save', formData)
  }

  const handleCancel = () => {
    if (isDirty && !confirm(t('crud.messages.unsavedChanges'))) {
      return
    }
    navigate('/finance/bankkonten')
  }

  return (
    <ObjectPage
      config={bankKontenConfig}
      data={data || formData}
      onChange={handleFormChange}
      onSave={handleSave}
      onCancel={handleCancel}
      isLoading={loading || isIbanLoading}
    />
  )
}

