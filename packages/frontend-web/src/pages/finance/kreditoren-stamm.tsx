import { useState, useEffect } from 'react'
import { useNavigate } from 'react-router-dom'
import { useTranslation } from 'react-i18next'
import { ObjectPage } from '@/components/mask-builder'
import { useMaskData, useMaskValidation, useMaskActions } from '@/components/mask-builder/hooks'
import { MaskConfig } from '@/components/mask-builder/types'
import { z } from 'zod'
import { getEntityTypeLabel } from '@/features/crud/utils/i18n-helpers'
import { validateIBAN, formatIBAN, lookupIBAN } from '@/lib/utils/iban-validator'
import { useIbanLookup } from '@/hooks/useIbanLookup'
import { toast } from 'sonner'

// Zod-Schema für Kreditoren-Stammdaten (wird in Komponente mit i18n erstellt)
const createKreditorenSchema = (t: any) => z.object({
  kreditorNummer: z.string().regex(/^\d{6,8}$/, t('crud.messages.validationError')),
  firma: z.string().min(1, t('crud.messages.validationError')),
  ansprechpartner: z.string().optional(),
  strasse: z.string().min(1, t('crud.messages.validationError')),
  plz: z.string().regex(/^\d{5}$/, t('crud.messages.validationError')),
  ort: z.string().min(1, t('crud.messages.validationError')),
  land: z.string().default("DE"),
  telefon: z.string().optional(),
  email: z.string().email().optional().or(z.literal("")),
  ustId: z.string().optional(),
  steuernummer: z.string().optional(),

  // Bankverbindung
  iban: z.string()
    .optional()
    .or(z.literal(""))
    .refine((val) => !val || val.trim() === "" || validateIBAN(val), {
      message: t('crud.messages.invalidIban'),
    }),
  bic: z.string().optional(),
  bankname: z.string().optional(),
  kontoinhaber: z.string().optional(),

  // Konditionen
  zahlungsziel: z.number().min(0, t('crud.messages.validationError')).default(30),
  skontoTage: z.number().min(0).default(0),
  skontoProzent: z.number().min(0).max(100).default(0),
  kreditlimit: z.number().min(0).default(0),

  // Compliance
  sanktionslisteGeprueft: z.boolean().default(false),
  sanktionslisteGeprueftAm: z.string().optional(),
  vertragsstatus: z.enum(['aktiv', 'gekündigt', 'gesperrt']),
  letzteLieferung: z.string().optional(),
  notizen: z.string().optional()
})

// Konfiguration für Kreditoren-Stammdaten ObjectPage (wird in Komponente mit i18n erstellt)
const createKreditorenConfig = (t: any, entityTypeLabel: string): MaskConfig => ({
  title: entityTypeLabel,
  subtitle: t('crud.actions.edit'),
  type: 'object-page',
  tabs: [
    {
      key: 'stammdaten',
      label: t('crud.detail.basicInfo'),
      fields: [
        {
          name: 'kreditorNummer',
          label: t('crud.fields.creditorNumber'),
          type: 'text',
          required: true,
          placeholder: t('crud.tooltips.placeholders.creditorNumber'),
          maxLength: 8
        },
        {
          name: 'firma',
          label: t('crud.fields.company'),
          type: 'text',
          required: true,
          placeholder: t('crud.tooltips.placeholders.company')
        },
        {
          name: 'ansprechpartner',
          label: t('crud.fields.contactPerson'),
          type: 'text',
          placeholder: t('crud.tooltips.placeholders.contactPerson')
        },
        {
          name: 'strasse',
          label: t('crud.fields.street'),
          type: 'text',
          required: true,
          placeholder: t('crud.tooltips.placeholders.street')
        },
        {
          name: 'plz',
          label: t('crud.fields.postalCode'),
          type: 'text',
          required: true,
          placeholder: t('crud.tooltips.placeholders.postalCode'),
          maxLength: 5
        },
        {
          name: 'ort',
          label: t('crud.fields.city'),
          type: 'text',
          required: true,
          placeholder: t('crud.tooltips.placeholders.city')
        },
        {
          name: 'land',
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
          name: 'telefon',
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
          name: 'ustId',
          label: t('crud.fields.vatId'),
          type: 'text',
          placeholder: t('crud.tooltips.placeholders.vatId')
        },
        {
          name: 'steuernummer',
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
          name: 'bankname',
          label: t('crud.fields.bankName'),
          type: 'text',
          placeholder: t('crud.tooltips.placeholders.bankName')
        },
        {
          name: 'kontoinhaber',
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
          name: 'zahlungsziel',
          label: t('crud.fields.paymentDueDays'),
          type: 'number'
        } as any,
        {
          name: 'skontoTage',
          label: t('crud.fields.discountDays'),
          type: 'number'
        } as any,
        {
          name: 'skontoProzent',
          label: t('crud.fields.discountPercent'),
          type: 'number'
        } as any,
        {
          name: 'kreditlimit',
          label: t('crud.fields.creditLimit'),
          type: 'number'
        } as any
      ],
      layout: 'grid',
      columns: 2
    },
    {
      key: 'compliance',
      label: t('crud.fields.compliance'),
      fields: [
        {
          name: 'sanktionslisteGeprueft',
          label: t('crud.fields.sanctionsChecked'),
          type: 'boolean'
        },
        {
          name: 'sanktionslisteGeprueftAm',
          label: t('crud.fields.checkedOn'),
          type: 'date',
          readonly: true
        },
        {
          name: 'vertragsstatus',
          label: t('crud.fields.contractStatus'),
          type: 'select',
          required: true,
          options: [
            { value: 'aktiv', label: t('status.active') },
            { value: 'gekündigt', label: t('crud.fields.terminated') },
            { value: 'gesperrt', label: t('crud.fields.blocked') }
          ]
        },
        {
          name: 'letzteLieferung',
          label: t('crud.fields.lastDelivery'),
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
          name: 'notizen',
          label: t('crud.fields.internalNotes'),
          type: 'textarea',
          placeholder: t('crud.tooltips.placeholders.creditorNotes')
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
      key: 'sanktionspruefung',
      label: t('crud.actions.sanctionsCheck'),
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
    baseUrl: '/api/finance/kreditoren',
    endpoints: {
      list: '/api/finance/kreditoren',
      get: '/api/finance/kreditoren/{id}',
      create: '/api/finance/kreditoren',
      update: '/api/finance/kreditoren/{id}',
      delete: '/api/finance/kreditoren/{id}'
      // sanctions: '/api/finance/kreditoren/{id}/sanctions',
      // export: '/api/finance/kreditoren/export'
    }
  },
  validation: createKreditorenSchema(t),
  permissions: ['fibu.read', 'fibu.write']
})

export default function KreditorenStammPage(): JSX.Element {
  const { t } = useTranslation()
  const navigate = useNavigate()
  const [isDirty, setIsDirty] = useState(false)
  const [formData, setFormData] = useState<any>({})
  const entityType = 'creditor'
  const entityTypeLabel = getEntityTypeLabel(t, entityType, 'Kreditor')
  const kreditorenConfig = createKreditorenConfig(t, entityTypeLabel)

  const { data, loading, saveData, updateData } = useMaskData({
    apiUrl: kreditorenConfig.api.baseUrl,
    id: 'new'
  })

  const { validate, showValidationToast } = useMaskValidation(kreditorenConfig.validation)

  // IBAN Lookup Hook
  const { performLookup, isLoading: isIbanLoading, lookupData } = useIbanLookup({
    onSuccess: (result) => {
      if (result.valid && result.bank_name) {
        // Auto-fill bank name and BIC if available
        const updatedData = { ...formData }
        if (result.bank_name) {
          updatedData.bankname = result.bank_name
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
      // Silent error - user can still enter IBAN manually
      console.warn('IBAN lookup failed:', error)
    },
    autoLookup: false // Manual lookup via button
  })

  // Auto-lookup IBAN when it changes and seems complete
  useEffect(() => {
    const iban = formData?.iban
    if (iban && iban.replace(/\s/g, '').length >= 15) {
      const normalized = iban.replace(/\s/g, '').replace(/-/g, '').toUpperCase()
      if (normalized.length >= 15 && normalized.length <= 34 && validateIBAN(normalized)) {
        // Debounce: wait a bit before looking up
        const timer = setTimeout(() => {
          performLookup(normalized)
        }, 1000) // 1 second debounce
        
        return () => clearTimeout(timer)
      }
    }
  }, [formData?.iban, performLookup])

  const { handleAction } = useMaskActions(async (action: string, formData: any) => {
    if (action === 'save') {
      const isValid = validate(formData)
      if (!isValid.isValid) {
        showValidationToast(isValid.errors)
        return
      }

      try {
        await saveData(formData)
        setIsDirty(false)
        navigate('/finance/kreditoren')
      } catch (error) {
        // Error wird bereits in useMaskData behandelt
      }
    } else if (action === 'validate') {
      const isValid = validate(formData)
      if (isValid.isValid) {
        alert(t('crud.messages.validationSuccess'))
      } else {
        showValidationToast(isValid.errors)
      }
    } else if (action === 'sanktionspruefung') {
      // Sanktionsprüfung
      alert(t('crud.messages.sanctionsCheckInfo'))
    } else if (action === 'export') {
      window.open('/api/finance/kreditoren/export', '_blank')
    }
  })

  // Handle form data changes for IBAN lookup
  const handleFormChange = (newData: any) => {
    setFormData(newData)
    setIsDirty(true)
    
    // Auto-lookup IBAN when it changes
    const iban = newData?.iban
    if (iban && iban.replace(/\s/g, '').length >= 15) {
      const normalized = iban.replace(/\s/g, '').replace(/-/g, '').toUpperCase()
      if (normalized.length >= 15 && normalized.length <= 34 && validateIBAN(normalized)) {
        // Debounce: wait a bit before looking up
        const timer = setTimeout(() => {
          performLookup(normalized)
        }, 1000) // 1 second debounce
        
        return () => clearTimeout(timer)
      }
    }
  }

  // Update form data when IBAN lookup succeeds
  useEffect(() => {
    if (lookupData?.valid && lookupData.bank_name && formData) {
      const updatedData = { ...formData }
      if (lookupData.bank_name && !updatedData.bankname) {
        updatedData.bankname = lookupData.bank_name
      }
      if (lookupData.bic && !updatedData.bic) {
        updatedData.bic = lookupData.bic
      }
      setFormData(updatedData)
      updateData?.(updatedData)
    }
  }, [lookupData, formData, updateData])

  const handleSave = async (formData: any) => {
    await handleAction('save', formData)
  }

  const handleCancel = () => {
    if (isDirty && !confirm(t('crud.messages.unsavedChanges'))) {
      return
    }
    navigate('/finance/kreditoren')
  }

  return (
    <ObjectPage
      config={kreditorenConfig}
      data={data || formData}
      onChange={handleFormChange}
      onSave={handleSave}
      onCancel={handleCancel}
      isLoading={loading || isIbanLoading}
    />
  )
}