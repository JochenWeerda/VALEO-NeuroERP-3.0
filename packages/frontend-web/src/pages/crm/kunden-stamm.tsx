import { useState } from 'react'
import { useNavigate } from 'react-router-dom'
import { useTranslation } from 'react-i18next'
import { ObjectPage } from '@/components/mask-builder'
import { useMaskData, useMaskValidation, useMaskActions } from '@/components/mask-builder/hooks'
import { MaskConfig } from '@/components/mask-builder/types'
import { z } from 'zod'
import { getEntityTypeLabel } from '@/features/crud/utils/i18n-helpers'

// Zod-Schema für Kunden (wird in Komponente mit i18n erstellt)
const createKundenSchema = (t: any) => z.object({
  firma: z.string().min(1, t('crud.messages.validationError')),
  anrede: z.string().optional(),
  vorname: z.string().optional(),
  nachname: z.string().min(1, t('crud.messages.validationError')),
  strasse: z.string().min(1, t('crud.messages.validationError')),
  plz: z.string().regex(/^\d{5}$/, t('crud.messages.validationError')),
  ort: z.string().min(1, t('crud.messages.validationError')),
  land: z.string().default("DE"),
  telefon: z.string().optional(),
  email: z.string().email(t('crud.messages.validationError')).optional().or(z.literal("")),
  ustId: z.string().optional(),
  steuernummer: z.string().optional(),
  kreditlimit: z.number().min(0).default(0),
  zahlungsbedingungen: z.string().default("14 Tage"),
  rabatt: z.number().min(0).max(100).default(0),
  bonitaet: z.string().default("gut"),
  letzteBestellung: z.string().optional(),
  umsatzGesamt: z.number().min(0).default(0),
  status: z.string().default("aktiv"),
  bemerkungen: z.string().optional()
})

// Konfiguration für Kunden ObjectPage (wird in Komponente mit i18n erstellt)
const createKundenConfig = (t: any, entityTypeLabel: string): MaskConfig => ({
  title: entityTypeLabel,
  subtitle: t('crud.detail.manage', { entityType: entityTypeLabel }),
  type: 'object-page',
  tabs: [
    {
      key: 'stammdaten',
      label: t('crud.detail.basicInfo'),
      fields: [
        {
          name: 'firma',
          label: t('crud.fields.companyName'),
          type: 'text',
          required: true,
          placeholder: t('crud.tooltips.placeholders.companyName')
        },
        {
          name: 'anrede',
          label: t('crud.fields.salutation'),
          type: 'select',
          options: [
            { value: 'herr', label: t('crud.fields.salutationMr') },
            { value: 'frau', label: t('crud.fields.salutationMrs') },
            { value: 'familie', label: t('crud.fields.salutationFamily') },
            { value: 'firma', label: t('crud.fields.salutationCompany') }
          ]
        },
        {
          name: 'vorname',
          label: t('crud.fields.firstName'),
          type: 'text',
          placeholder: t('crud.tooltips.placeholders.firstName')
        },
        {
          name: 'nachname',
          label: t('crud.fields.lastName'),
          type: 'text',
          required: true,
          placeholder: t('crud.tooltips.placeholders.lastName')
        }
      ],
      layout: 'grid',
      columns: 2
    },
    {
      key: 'adresse',
      label: t('crud.fields.address'),
      fields: [
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
          maxLength: 5,
          placeholder: t('crud.tooltips.placeholders.postalCode')
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
          required: true,
          options: [
            { value: 'DE', label: t('crud.fields.countryDE') },
            { value: 'AT', label: t('crud.fields.countryAT') },
            { value: 'CH', label: t('crud.fields.countryCH') },
            { value: 'NL', label: t('crud.fields.countryNL') },
            { value: 'DK', label: t('crud.fields.countryDK') },
            { value: 'PL', label: t('crud.fields.countryPL') }
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
        }
      ]
    },
    {
      key: 'steuern',
      label: t('crud.fields.taxesAndLegal'),
      fields: [
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
      key: 'konditionen',
      label: t('crud.fields.terms'),
      fields: [
        {
          name: 'kreditlimit',
          label: t('crud.fields.creditLimit'),
          type: 'number',
          min: 0,
          step: 100,
          placeholder: t('crud.tooltips.placeholders.creditLimit')
        },
        {
          name: 'zahlungsbedingungen',
          label: t('crud.fields.paymentTerms'),
          type: 'select',
          options: [
            { value: 'sofort', label: t('crud.fields.paymentTermsImmediate') },
            { value: '7 Tage', label: t('crud.fields.paymentTerms7Days') },
            { value: '14 Tage', label: t('crud.fields.paymentTermsNet14') },
            { value: '30 Tage', label: t('crud.fields.paymentTermsNet30') },
            { value: '60 Tage', label: t('crud.fields.paymentTermsNet60') }
          ]
        },
        {
          name: 'rabatt',
          label: t('crud.fields.discountPercent'),
          type: 'number',
          min: 0,
          max: 100,
          step: 0.5,
          placeholder: t('crud.tooltips.placeholders.discount')
        },
        {
          name: 'bonitaet',
          label: t('crud.fields.creditRating'),
          type: 'select',
          options: [
            { value: 'ausgezeichnet', label: t('crud.fields.creditRatingExcellent') },
            { value: 'gut', label: t('crud.fields.creditRatingGood') },
            { value: 'mittel', label: t('crud.fields.creditRatingMedium') },
            { value: 'schlecht', label: t('crud.fields.creditRatingPoor') },
            { value: 'unklar', label: t('crud.fields.creditRatingUnclear') }
          ]
        }
      ],
      layout: 'grid',
      columns: 2
    },
    {
      key: 'umsatz',
      label: t('crud.fields.revenueAndHistory'),
      fields: [
        {
          name: 'letzteBestellung',
          label: t('crud.fields.lastOrder'),
          type: 'date',
          readonly: true
        },
        {
          name: 'umsatzGesamt',
          label: t('crud.fields.totalRevenue'),
          type: 'number',
          readonly: true,
          min: 0,
          step: 0.01
        },
        {
          name: 'status',
          label: t('crud.fields.status'),
          type: 'select',
          options: [
            { value: 'aktiv', label: t('status.active') },
            { value: 'inaktiv', label: t('status.inactive') },
            { value: 'gesperrt', label: t('crud.fields.statusBlocked') }
          ]
        }
      ],
      layout: 'grid',
      columns: 2
    },
    {
      key: 'bemerkungen',
      label: t('crud.fields.notes'),
      fields: [
        {
          name: 'bemerkungen',
          label: t('crud.fields.internalNotes'),
          type: 'textarea',
          placeholder: t('crud.tooltips.placeholders.customerNotes')
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
    }
  ],
  api: {
    baseUrl: '/api/crm/kunden',
    endpoints: {
      list: '/api/crm/kunden',
      get: '/api/crm/kunden/{id}',
      create: '/api/crm/kunden',
      update: '/api/crm/kunden/{id}',
      delete: '/api/crm/kunden/{id}'
    }
  },
  validation: createKundenSchema(t),
  permissions: ['crm.write', 'customer.admin']
})

export default function KundenStammPage(): JSX.Element {
  const { t } = useTranslation()
  const navigate = useNavigate()
  const [isDirty, setIsDirty] = useState(false)
  const entityType = 'customer'
  const entityTypeLabel = getEntityTypeLabel(t, entityType, 'Kunde')
  const kundenConfig = createKundenConfig(t, entityTypeLabel)

  const { data, loading, saveData } = useMaskData({
    apiUrl: kundenConfig.api.baseUrl,
    id: 'new'
  })

  const { validate, showValidationToast } = useMaskValidation(kundenConfig.validation)

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
        navigate('/crm/kunden/liste')
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
    }
  })

  const handleSave = async (formData: any) => {
    await handleAction('save', formData)
  }

  const handleCancel = () => {
    if (isDirty && !confirm(t('crud.messages.discardChanges'))) {
      return
    }
    navigate('/crm/kunden/liste')
  }

  return (
    <ObjectPage
      config={kundenConfig}
      data={data}
      onSave={handleSave}
      onCancel={handleCancel}
      isLoading={loading}
    />
  )
}