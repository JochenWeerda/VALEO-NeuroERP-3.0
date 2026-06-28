import { useState, useEffect } from 'react'
import { useNavigate } from '@/app/routing/typed-router'
import { useTranslation, type TFunction } from 'react-i18next'
import { ObjectPage } from '@/components/mask-builder'
import { useMaskData, useMaskActions } from '@/components/mask-builder/hooks'
import { MaskConfig } from '@/components/mask-builder/types'
import { getFieldsFromMaskConfig, validateFields } from '@/components/mask-builder/validation'
import { getEntityTypeLabel } from '@/features/crud/utils/i18n-helpers'
import { validateIBAN } from '@/lib/utils/iban-validator'
import { validateVatIdFormat } from '@/lib/utils/vat-validator'
import { useIbanLookup } from '@/hooks/useIbanLookup'
import { toast } from 'sonner'
import { apiClient } from '@/lib/api-client'
import { useTenant } from '@/hooks/useTenant'

const createKreditorenConfig = (t: TFunction, entityTypeLabel: string): MaskConfig => ({
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
          maxLength: 8,
          pattern: '^\\d{6,8}$'
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
          maxLength: 5,
          pattern: '^\\d{5}$'
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
          pattern: '^[^\\s@]+@[^\\s@]+\\.[^\\s@]+$',
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
          pattern: '^[A-Z]{2}\\d{2}[A-Z0-9]{11,30}$',
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
        } as Field,
        {
          name: 'skontoTage',
          label: t('crud.fields.discountDays'),
          type: 'number'
        } as Field,
        {
          name: 'skontoProzent',
          label: t('crud.fields.discountPercent'),
          type: 'number'
        } as Field,
        {
          name: 'kreditlimit',
          label: t('crud.fields.creditLimit'),
          type: 'number'
        } as Field
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
    { key: 'validate', label: t('crud.actions.validate'), type: 'secondary' },
    { key: 'save', label: t('crud.actions.save'), type: 'primary' },
    { key: 'sanktionspruefung', label: t('crud.actions.sanctionsCheck'), type: 'secondary' },
    { key: 'export', label: t('crud.actions.export'), type: 'secondary' }
  ],
  api: {
    baseUrl: '/api/v1/finance/creditors',
    endpoints: {
      list: '/api/v1/finance/creditors',
      get: '/api/v1/finance/creditors/{id}',
      create: '/api/v1/finance/creditors',
      update: '/api/v1/finance/creditors/{id}',
      delete: '/api/v1/finance/creditors/{id}'
      // sanctions: '/api/v1/finance/creditors/{id}/sanctions',
      // export: '/api/v1/finance/creditors/export'
    }
  },
  permissions: ['fibu.read', 'fibu.write']
})

/** Formular (camelCase) → API /api/v1/finance/creditors (snake_case) */
function toApiCreditor(form: Record<string, unknown>, tenantId: string): Record<string, unknown> {
  return {
    tenant_id: tenantId,
    creditor_number: form.kreditorNummer,
    company_name: form.firma,
    contact_person: form.ansprechpartner ?? undefined,
    street: form.strasse ?? '',
    postal_code: form.plz ?? '',
    city: form.ort ?? '',
    country: (form.land as string) ?? 'DE',
    phone: form.telefon ?? undefined,
    email: form.email || undefined,
    vat_id: form.ustId || undefined,
    tax_number: form.steuernummer ?? undefined,
    iban: form.iban || undefined,
    bic: form.bic ?? undefined,
    bank_name: form.bankname ?? undefined,
    account_holder: form.kontoinhaber ?? undefined,
    payment_terms_days: Number(form.zahlungsziel) || 30,
    discount_days: Number(form.skontoTage) || 0,
    discount_percent: Number(form.skontoProzent) || 0,
    credit_limit: Number(form.kreditlimit) || 0,
    is_active: (form.vertragsstatus as string) === 'aktiv',
    notes: form.notizen ?? undefined,
  }
}

/** API-Antwort (snake_case) → Formular (camelCase) für Anzeige/Bearbeitung */
export function fromApiCreditor(api: Record<string, unknown>): Record<string, unknown> {
  return {
    id: api.id,
    kreditorNummer: api.creditor_number,
    firma: api.company_name,
    ansprechpartner: api.contact_person,
    strasse: api.street ?? '',
    plz: api.postal_code ?? '',
    ort: api.city ?? '',
    land: api.country ?? 'DE',
    telefon: api.phone,
    email: api.email,
    ustId: api.vat_id,
    steuernummer: api.tax_number,
    iban: api.iban,
    bic: api.bic,
    bankname: api.bank_name,
    kontoinhaber: api.account_holder,
    zahlungsziel: Number(api.payment_terms_days) || 30,
    skontoTage: Number(api.discount_days) || 0,
    skontoProzent: Number(api.discount_percent) || 0,
    kreditlimit: Number(api.credit_limit) || 0,
    vertragsstatus: api.is_active === true ? 'aktiv' : (api.is_active === false ? 'gesperrt' : 'aktiv'),
    notizen: api.notes,
  }
}

export default function KreditorenStammPage(): JSX.Element {
  const { t } = useTranslation()
  const navigate = useNavigate()
  const [isDirty, setIsDirty] = useState(false)
  const [formData, setFormData] = useState<Record<string, unknown>>({})
  const entityType = 'creditor'
  const entityTypeLabel = getEntityTypeLabel(t, entityType, 'Kreditor')
  const kreditorenConfig = createKreditorenConfig(t, entityTypeLabel)

  const { tenantId } = useTenant()
  const { data, loading, saveData, setData } = useMaskData({
    apiUrl: kreditorenConfig.api.baseUrl,
    id: 'new'
  })

  const validate = (formData: Record<string, unknown>) => validateFields(getFieldsFromMaskConfig(kreditorenConfig), formData ?? {})
  const showValidationToast = (errors: Record<string, string>) => {
    toast.error(Object.values(errors).join(', '))
  }

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
        setData(updatedData as Record<string, unknown>)
        toast.success(t('crud.messages.ibanLookupSuccess', { 
          defaultValue: 'Bankinformationen automatisch ausgefüllt',
          bankName: result.bank_name 
        }))
      }
    },
    onError: (error) => {
      // Silent error - user can still enter IBAN manually
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

  const { handleAction, loadingActionKey } = useMaskActions(async (action: string, formData: Record<string, unknown>) => {
    if (action === 'save') {
      const errors = validate(formData)
      if (Object.keys(errors).length > 0) {
        showValidationToast(errors)
        return
      }

      try {
        const apiPayload = toApiCreditor(formData, tenantId ?? 'system')
        await saveData(apiPayload)
        setIsDirty(false)
        navigate('/finance/kreditoren')
      } catch (error) {
        // Error wird bereits in useMaskData behandelt
      }
    } else if (action === 'validate') {
      const errors = validate(formData)
      if (Object.keys(errors).length === 0) {
        toast.success(t('crud.messages.validationSuccess', { defaultValue: 'Validierung erfolgreich' }))
      } else {
        showValidationToast(errors)
      }
    } else if (action === 'sanktionspruefung') {
      const name = formData?.firma || formData?.name || ''
      const land = formData?.land || 'DE'
      if (!name) {
        toast('Firmenname fehlt — bitte Stammdaten zuerst ausfüllen.')
        return
      }
      try {
        const res = await apiClient.post<{
          treffer: boolean
          ergebnis: string
          listen: string[]
          geprueft_am: string
          hinweis: string
        }>('/api/v1/crm/sanktionspruefung', { name, land })
        const result = res as Record<string, unknown>
        if (result?.treffer) {
          toast.error(`Sanktionstreffer: ${String(result.ergebnis ?? '')}`)
        } else {
          toast.success(`Sanktionsprüfung OK: ${String(result?.ergebnis ?? 'Kein Treffer')}`)
        }
      } catch (_rawErr: unknown) {
        const e = _rawErr as { response?: { data?: { detail?: string } }; message?: string; name?: string }
        const msg = e.response?.data?.detail ?? e.message
        toast.error(`Sanktionsprüfung fehlgeschlagen: ${msg}`)
      }
    } else if (action === 'export') {
      try {
        const res = await apiClient.post<{ url?: string }>('/api/v1/export/list', { entity: 'creditors', format: 'pdf', id: formData?.id })
        if (res?.url) window.open(res.url, '_blank')
        toast.success(t('crud.messages.exportCreated', { defaultValue: 'Export erstellt' }))
      } catch (_rawErr: unknown) {
        const error = _rawErr as { response?: { data?: { detail?: string } }; message?: string; name?: string }
        const msg = error.response?.data?.detail ?? error.message
        toast.error(msg)
      }
    }
  })

  // Handle form data changes for IBAN lookup
  const handleFormChange = (newData: Record<string, unknown>) => {
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
      setData(updatedData as Record<string, unknown>)
    }
  }, [lookupData, formData, setData])

  const handleSave = async (formData: Record<string, unknown>) => {
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
      data={data ? fromApiCreditor(data as Record<string, unknown>) : formData}
      onChange={handleFormChange}
      onSave={handleSave}
      onCancel={handleCancel}
      isLoading={loading || isIbanLoading}
      onAction={(key, fd) => handleAction(key, fd ?? formData)}
      loadingActionKey={loadingActionKey}
    />
  )
}
