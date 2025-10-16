import { useState } from 'react'
import { useNavigate } from 'react-router-dom'
import { ObjectPage } from '@/components/mask-builder'
import { useMaskData, useMaskValidation, useMaskActions } from '@/components/mask-builder/hooks'
import { MaskConfig } from '@/components/mask-builder/types'
import { z } from 'zod'

// Zod-Schema für Kunden
const kundenSchema = z.object({
  firma: z.string().min(1, "Firmenname ist erforderlich"),
  anrede: z.string().optional(),
  vorname: z.string().optional(),
  nachname: z.string().min(1, "Nachname ist erforderlich"),
  strasse: z.string().min(1, "Straße ist erforderlich"),
  plz: z.string().regex(/^\d{5}$/, "PLZ muss 5-stellig sein"),
  ort: z.string().min(1, "Ort ist erforderlich"),
  land: z.string().default("DE"),
  telefon: z.string().optional(),
  email: z.string().email("Ungültige E-Mail-Adresse").optional().or(z.literal("")),
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

// Konfiguration für Kunden ObjectPage
const kundenConfig: MaskConfig = {
  title: 'Kunden-Stammdaten',
  subtitle: 'Verwaltung von Geschäftspartner-Stammdaten',
  type: 'object-page',
  tabs: [
    {
      key: 'stammdaten',
      label: 'Stammdaten',
      fields: [
        {
          name: 'firma',
          label: 'Firmenname',
          type: 'text',
          required: true,
          placeholder: 'z.B. Müller Landwirtschaft GmbH'
        },
        {
          name: 'anrede',
          label: 'Anrede',
          type: 'select',
          options: [
            { value: 'herr', label: 'Herr' },
            { value: 'frau', label: 'Frau' },
            { value: 'familie', label: 'Familie' },
            { value: 'firma', label: 'Firma' }
          ]
        },
        {
          name: 'vorname',
          label: 'Vorname',
          type: 'text',
          placeholder: 'Max'
        },
        {
          name: 'nachname',
          label: 'Nachname',
          type: 'text',
          required: true,
          placeholder: 'Müller'
        }
      ],
      layout: 'grid',
      columns: 2
    },
    {
      key: 'adresse',
      label: 'Adresse',
      fields: [
        {
          name: 'strasse',
          label: 'Straße und Hausnummer',
          type: 'text',
          required: true,
          placeholder: 'Musterstraße 123'
        },
        {
          name: 'plz',
          label: 'PLZ',
          type: 'text',
          required: true,
          maxLength: 5,
          placeholder: '12345'
        },
        {
          name: 'ort',
          label: 'Ort',
          type: 'text',
          required: true,
          placeholder: 'Musterstadt'
        },
        {
          name: 'land',
          label: 'Land',
          type: 'select',
          required: true,
          options: [
            { value: 'DE', label: 'Deutschland' },
            { value: 'AT', label: 'Österreich' },
            { value: 'CH', label: 'Schweiz' },
            { value: 'NL', label: 'Niederlande' },
            { value: 'DK', label: 'Dänemark' },
            { value: 'PL', label: 'Polen' }
          ]
        }
      ],
      layout: 'grid',
      columns: 2
    },
    {
      key: 'kontakt',
      label: 'Kontakt',
      fields: [
        {
          name: 'telefon',
          label: 'Telefon',
          type: 'text',
          placeholder: '+49 123 456789'
        },
        {
          name: 'email',
          label: 'E-Mail',
          type: 'text',
          placeholder: 'max.mueller@example.com'
        }
      ]
    },
    {
      key: 'steuern',
      label: 'Steuern & Recht',
      fields: [
        {
          name: 'ustId',
          label: 'USt-ID',
          type: 'text',
          placeholder: 'DE123456789'
        },
        {
          name: 'steuernummer',
          label: 'Steuernummer',
          type: 'text',
          placeholder: '123/456/78901'
        }
      ],
      layout: 'grid',
      columns: 2
    },
    {
      key: 'konditionen',
      label: 'Konditionen',
      fields: [
        {
          name: 'kreditlimit',
          label: 'Kreditlimit (€)',
          type: 'number',
          min: 0,
          step: 100,
          placeholder: '5000'
        },
        {
          name: 'zahlungsbedingungen',
          label: 'Zahlungsbedingungen',
          type: 'select',
          options: [
            { value: 'sofort', label: 'Sofort' },
            { value: '7 Tage', label: '7 Tage' },
            { value: '14 Tage', label: '14 Tage' },
            { value: '30 Tage', label: '30 Tage' },
            { value: '60 Tage', label: '60 Tage' }
          ]
        },
        {
          name: 'rabatt',
          label: 'Rabatt (%)',
          type: 'number',
          min: 0,
          max: 100,
          step: 0.5,
          placeholder: '2.5'
        },
        {
          name: 'bonitaet',
          label: 'Bonität',
          type: 'select',
          options: [
            { value: 'ausgezeichnet', label: 'Ausgezeichnet' },
            { value: 'gut', label: 'Gut' },
            { value: 'mittel', label: 'Mittel' },
            { value: 'schlecht', label: 'Schlecht' },
            { value: 'unklar', label: 'Unklar' }
          ]
        }
      ],
      layout: 'grid',
      columns: 2
    },
    {
      key: 'umsatz',
      label: 'Umsatz & Historie',
      fields: [
        {
          name: 'letzteBestellung',
          label: 'Letzte Bestellung',
          type: 'date',
          readonly: true
        },
        {
          name: 'umsatzGesamt',
          label: 'Gesamtumsatz (€)',
          type: 'number',
          readonly: true,
          min: 0,
          step: 0.01
        },
        {
          name: 'status',
          label: 'Status',
          type: 'select',
          options: [
            { value: 'aktiv', label: 'Aktiv' },
            { value: 'inaktiv', label: 'Inaktiv' },
            { value: 'gesperrt', label: 'Gesperrt' }
          ]
        }
      ],
      layout: 'grid',
      columns: 2
    },
    {
      key: 'bemerkungen',
      label: 'Bemerkungen',
      fields: [
        {
          name: 'bemerkungen',
          label: 'Interne Bemerkungen',
          type: 'textarea',
          placeholder: 'Zusätzliche Informationen, Vorlieben, Besonderheiten...'
        }
      ]
    }
  ],
  actions: [
    {
      key: 'validate',
      label: 'Validieren',
      type: 'secondary',
      onClick: () => {}
    },
    {
      key: 'save',
      label: 'Speichern',
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
  validation: kundenSchema,
  permissions: ['crm.write', 'customer.admin']
}

export default function KundenStammPage(): JSX.Element {
  const navigate = useNavigate()
  const [isDirty, setIsDirty] = useState(false)

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
        alert('Validierung erfolgreich!')
      } else {
        showValidationToast(isValid.errors)
      }
    }
  })

  const handleSave = async (formData: any) => {
    await handleAction('save', formData)
  }

  const handleCancel = () => {
    if (isDirty && !confirm('Ungespeicherte Änderungen gehen verloren. Wirklich abbrechen?')) {
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