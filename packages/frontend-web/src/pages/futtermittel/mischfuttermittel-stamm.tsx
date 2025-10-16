import { useState } from 'react'
import { useNavigate } from 'react-router-dom'
import { ObjectPage } from '@/components/mask-builder'
import { useMaskData, useMaskValidation, useMaskActions } from '@/components/mask-builder/hooks'
import { MaskConfig } from '@/components/mask-builder/types'
import { z } from 'zod'

// Zod-Schema für Mischfuttermittel
const mischfuttermittelSchema = z.object({
  artikelnummer: z.string().min(1, "Artikelnummer ist erforderlich"),
  name: z.string().min(1, "Name ist erforderlich"),
  typ: z.string().min(1, "Typ ist erforderlich"),
  futtergruppe: z.string().min(1, "Futtergruppe ist erforderlich"),
  tierart: z.string().min(1, "Tierart ist erforderlich"),
  lebensphase: z.string().min(1, "Lebensphase ist erforderlich"),
  komponenten: z.array(z.object({
    futtermittelId: z.string(),
    anteil: z.number().min(0).max(100)
  })).min(1, "Mindestens eine Komponente erforderlich"),
  gesamtRohprotein: z.number().min(0).max(100),
  gesamtRohfett: z.number().min(0).max(100),
  gesamtRohfaser: z.number().min(0).max(100),
  gesamtRohasche: z.number().min(0).max(100),
  umsetzbareEnergie: z.number().min(0),
  qsZertifikat: z.string().optional(),
  gueltigBis: z.string().optional(),
  lagerbestand: z.number().min(0).default(0),
  ekPreis: z.number().min(0).optional(),
  vkPreis: z.number().min(0).optional(),
})

// Konfiguration für Mischfuttermittel ObjectPage
const mischfuttermittelConfig: MaskConfig = {
  title: 'Mischfuttermittel-Stammdaten',
  subtitle: 'Verwaltung von Mischfuttermitteln nach EU 767/2009',
  type: 'object-page',
  tabs: [
    {
      key: 'allgemein',
      label: 'Allgemein',
      fields: [
        {
          name: 'artikelnummer',
          label: 'Artikelnummer',
          type: 'text',
          required: true,
          placeholder: 'z.B. MF-001'
        },
        {
          name: 'name',
          label: 'Name',
          type: 'text',
          required: true,
          placeholder: 'z.B. Milchviehfutter Premium'
        },
        {
          name: 'typ',
          label: 'Typ',
          type: 'select',
          required: true,
          options: [
            { value: 'alleinfuttermittel', label: 'Alleinfuttermittel' },
            { value: 'ergaenzungsfuttermittel', label: 'Ergänzungsfuttermittel' },
            { value: 'mineralstoffmischung', label: 'Mineralstoffmischung' }
          ]
        },
        {
          name: 'futtergruppe',
          label: 'Futtergruppe',
          type: 'select',
          required: true,
          options: [
            { value: 'milchvieh', label: 'Milchvieh' },
            { value: 'mastvieh', label: 'Mastvieh' },
            { value: 'schweine', label: 'Schweine' },
            { value: 'gefluegel', label: 'Geflügel' },
            { value: 'pferde', label: 'Pferde' },
            { value: 'schafe', label: 'Schafe' }
          ]
        }
      ],
      layout: 'grid',
      columns: 2
    },
    {
      key: 'zielgruppe',
      label: 'Zielgruppe',
      fields: [
        {
          name: 'tierart',
          label: 'Tierart',
          type: 'select',
          required: true,
          options: [
            { value: 'rind', label: 'Rind' },
            { value: 'schwein', label: 'Schwein' },
            { value: 'gefluegel', label: 'Geflügel' },
            { value: 'pferd', label: 'Pferd' },
            { value: 'schaf', label: 'Schaf' },
            { value: 'ziege', label: 'Ziege' }
          ]
        },
        {
          name: 'lebensphase',
          label: 'Lebensphase',
          type: 'select',
          required: true,
          options: [
            { value: 'aufzucht', label: 'Aufzucht' },
            { value: 'mast', label: 'Mast' },
            { value: 'laktation', label: 'Laktation' },
            { value: 'haltung', label: 'Haltung' },
            { value: 'alle', label: 'Alle Phasen' }
          ]
        }
      ]
    },
    {
      key: 'rezeptur',
      label: 'Rezeptur',
      fields: [
        {
          name: 'komponenten',
          label: 'Komponenten',
          type: 'textarea',
          helpText: 'Rezeptur-Komponenten werden separat verwaltet'
        }
      ]
    },
    {
      key: 'naehrwerte',
      label: 'Nährwerte',
      fields: [
        {
          name: 'gesamtRohprotein',
          label: 'Gesamt Rohprotein (%)',
          type: 'number',
          min: 0,
          max: 100,
          step: 0.1,
          readonly: true,
          helpText: 'Berechnet aus Rezeptur'
        },
        {
          name: 'gesamtRohfett',
          label: 'Gesamt Rohfett (%)',
          type: 'number',
          min: 0,
          max: 100,
          step: 0.1,
          readonly: true
        },
        {
          name: 'gesamtRohfaser',
          label: 'Gesamt Rohfaser (%)',
          type: 'number',
          min: 0,
          max: 100,
          step: 0.1,
          readonly: true
        },
        {
          name: 'gesamtRohasche',
          label: 'Gesamt Rohasche (%)',
          type: 'number',
          min: 0,
          max: 100,
          step: 0.1,
          readonly: true
        },
        {
          name: 'umsetzbareEnergie',
          label: 'Umsetzbare Energie (MJ/kg)',
          type: 'number',
          min: 0,
          step: 0.1,
          readonly: true
        }
      ],
      layout: 'grid',
      columns: 2
    },
    {
      key: 'qualitaet',
      label: 'Qualität & Zertifizierung',
      fields: [
        {
          name: 'qsZertifikat',
          label: 'QS-Zertifikatsnummer',
          type: 'text',
          placeholder: 'z.B. QS-MF-123456'
        },
        {
          name: 'gueltigBis',
          label: 'Zertifikat gültig bis',
          type: 'date'
        }
      ]
    },
    {
      key: 'lager',
      label: 'Lager & Preise',
      fields: [
        {
          name: 'lagerbestand',
          label: 'Lagerbestand (kg)',
          type: 'number',
          min: 0,
          defaultValue: 0
        },
        {
          name: 'ekPreis',
          label: 'EK-Preis (€/kg)',
          type: 'number',
          min: 0,
          step: 0.01
        },
        {
          name: 'vkPreis',
          label: 'VK-Preis (€/kg)',
          type: 'number',
          min: 0,
          step: 0.01
        }
      ],
      layout: 'grid',
      columns: 2
    }
  ],
  actions: [
    {
      key: 'calculate',
      label: 'Nährwerte berechnen',
      type: 'secondary',
      onClick: () => console.log('Calculate clicked')
    },
    {
      key: 'validate',
      label: 'Validieren',
      type: 'secondary',
      onClick: () => console.log('Validate clicked')
    },
    {
      key: 'save',
      label: 'Speichern',
      type: 'primary',
      onClick: () => console.log('Save clicked')
    }
  ],
  api: {
    baseUrl: '/api/futtermittel/mischfuttermittel',
    endpoints: {
      list: '/api/futtermittel/mischfuttermittel',
      get: '/api/futtermittel/mischfuttermittel/{id}',
      create: '/api/futtermittel/mischfuttermittel',
      update: '/api/futtermittel/mischfuttermittel/{id}',
      delete: '/api/futtermittel/mischfuttermittel/{id}'
    }
  },
  validation: mischfuttermittelSchema,
  permissions: ['futtermittel.write', 'futtermittel.admin']
}

export default function MischfuttermittelStammPage(): JSX.Element {
  const navigate = useNavigate()
  const [isDirty, setIsDirty] = useState(false)

  const { data, loading, saveData } = useMaskData({
    apiUrl: mischfuttermittelConfig.api.baseUrl,
    id: 'new'
  })

  const { validate, showValidationToast } = useMaskValidation(mischfuttermittelConfig.validation)

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
        navigate('/futtermittel/mischfuttermittel/liste')
      } catch (error) {
        // Error wird bereits in useMaskData behandelt
      }
    } else if (action === 'calculate') {
      // Nährwertberechnung implementieren
      alert('Nährwertberechnung wird implementiert')
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
    navigate('/futtermittel/mischfuttermittel/liste')
  }

  return (
    <ObjectPage
      config={mischfuttermittelConfig}
      data={data}
      onSave={handleSave}
      onCancel={handleCancel}
      isLoading={loading}
    />
  )
}