import { useState } from 'react'
import { useNavigate } from 'react-router-dom'
import { ObjectPage } from '@/components/mask-builder'
import { useMaskData, useMaskValidation, useMaskActions } from '@/components/mask-builder/hooks'
import { MaskConfig } from '@/components/mask-builder/types'
import { z } from 'zod'

// Zod-Schema für Lieferanten
const lieferantenSchema = z.object({
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
  zahlungsbedingungen: z.string().default("30 Tage"),
  rabatt: z.number().min(0).max(100).default(0),
  mindestbestellwert: z.number().min(0).default(0),
  lieferzeit: z.number().min(0).default(7),
  qualitaetszertifikat: z.boolean().default(false),
  bioZertifiziert: z.boolean().default(false),
  letzteLieferung: z.string().optional(),
  umsatzGesamt: z.number().min(0).default(0),
  status: z.string().default("aktiv"),
  produkte: z.array(z.string()).default([]),
  bemerkungen: z.string().optional()
})

// Konfiguration für Lieferanten ObjectPage
const lieferantenConfig: MaskConfig = {
  title: 'Lieferanten-Stammdaten',
  subtitle: 'Verwaltung von Lieferanten-Stammdaten und Konditionen',
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
          placeholder: 'z.B. Agrar GmbH & Co. KG'
        },
        {
          name: 'anrede',
          label: 'Anrede',
          type: 'select',
          options: [
            { value: 'herr', label: 'Herr' },
            { value: 'frau', label: 'Frau' },
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
          placeholder: 'Schmidt'
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
          placeholder: 'Industriestraße 45'
        },
        {
          name: 'plz',
          label: 'PLZ',
          type: 'text',
          required: true,
          maxLength: 5,
          placeholder: '54321'
        },
        {
          name: 'ort',
          label: 'Ort',
          type: 'text',
          required: true,
          placeholder: 'Köln'
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
            { value: 'PL', label: 'Polen' },
            { value: 'FR', label: 'Frankreich' },
            { value: 'IT', label: 'Italien' }
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
          placeholder: '+49 221 123456'
        },
        {
          name: 'email',
          label: 'E-Mail',
          type: 'text',
          placeholder: 'max.schmidt@agrar-gmbh.de'
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
          placeholder: 'DE987654321'
        },
        {
          name: 'steuernummer',
          label: 'Steuernummer',
          type: 'text',
          placeholder: '987/654/32109'
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
          name: 'zahlungsbedingungen',
          label: 'Zahlungsbedingungen',
          type: 'select',
          options: [
            { value: 'sofort', label: 'Sofort' },
            { value: '7 Tage', label: '7 Tage' },
            { value: '14 Tage', label: '14 Tage' },
            { value: '30 Tage', label: '30 Tage' },
            { value: '60 Tage', label: '60 Tage' },
            { value: '90 Tage', label: '90 Tage' }
          ]
        },
        {
          name: 'rabatt',
          label: 'Rabatt (%)',
          type: 'number',
          min: 0,
          max: 100,
          step: 0.5,
          placeholder: '5.0'
        },
        {
          name: 'mindestbestellwert',
          label: 'Mindestbestellwert (€)',
          type: 'number',
          min: 0,
          step: 100,
          placeholder: '2500'
        },
        {
          name: 'lieferzeit',
          label: 'Standard-Lieferzeit (Tage)',
          type: 'number',
          min: 0,
          step: 1,
          placeholder: '7'
        }
      ],
      layout: 'grid',
      columns: 2
    },
    {
      key: 'zertifizierungen',
      label: 'Zertifizierungen',
      fields: [
        {
          name: 'qualitaetszertifikat',
          label: 'Qualitätszertifikat (QS/IFS)',
          type: 'boolean',
          helpText: 'Lieferant verfügt über gültiges Qualitätszertifikat'
        },
        {
          name: 'bioZertifiziert',
          label: 'Bio-zertifiziert',
          type: 'boolean',
          helpText: 'Lieferant ist bio-zertifiziert'
        },
        {
          name: 'produkte',
          label: 'Produktpalette',
          type: 'multiselect',
          helpText: 'Produktbereiche des Lieferanten'
        } as any
      ]
    },
    {
      key: 'umsatz',
      label: 'Umsatz & Historie',
      fields: [
        {
          name: 'letzteLieferung',
          label: 'Letzte Lieferung',
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
          placeholder: 'Besonderheiten, Vorlieben, Qualitätsbewertungen...'
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
    baseUrl: '/api/crm/lieferanten',
    endpoints: {
      list: '/api/crm/lieferanten',
      get: '/api/crm/lieferanten/{id}',
      create: '/api/crm/lieferanten',
      update: '/api/crm/lieferanten/{id}',
      delete: '/api/crm/lieferanten/{id}'
    }
  },
  validation: lieferantenSchema,
  permissions: ['crm.write', 'supplier.admin']
}

export default function LieferantenStammPage(): JSX.Element {
  const navigate = useNavigate()
  const [isDirty, setIsDirty] = useState(false)

  const { data, loading, saveData } = useMaskData({
    apiUrl: lieferantenConfig.api.baseUrl,
    id: 'new'
  })

  const { validate, showValidationToast } = useMaskValidation(lieferantenConfig.validation)

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
        navigate('/crm/lieferanten/liste')
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
    navigate('/crm/lieferanten/liste')
  }

  return (
    <ObjectPage
      config={lieferantenConfig}
      data={data}
      onSave={handleSave}
      onCancel={handleCancel}
      isLoading={loading}
    />
  )
}