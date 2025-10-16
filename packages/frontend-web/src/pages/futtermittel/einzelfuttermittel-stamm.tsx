import { useState } from 'react'
import { useNavigate } from 'react-router-dom'
import { ObjectPage } from '@/components/mask-builder'
import { useMaskData, useMaskValidation, useMaskActions } from '@/components/mask-builder/hooks'
import { MaskConfig } from '@/components/mask-builder/types'
import { z } from 'zod'

// Zod-Schema für Validierung
const futtermittelSchema = z.object({
  artikelnummer: z.string().min(1, "Artikelnummer ist erforderlich"),
  name: z.string().min(1, "Name ist erforderlich"),
  typ: z.string().min(1, "Typ ist erforderlich"),
  hersteller: z.string().optional(),
  rohprotein: z.number().min(0).max(100).optional(),
  rohfett: z.number().min(0).max(100).optional(),
  rohfaser: z.number().min(0).max(100).optional(),
  rohasche: z.number().min(0).max(100).optional(),
  feuchte: z.number().min(0).max(100).optional(),
  euKennzeichnung: z.boolean().default(false),
  qsZertifikat: z.string().optional(),
  gueltigBis: z.string().optional(),
  lagerbestand: z.number().min(0).default(0),
  ekPreis: z.number().min(0).optional(),
  vkPreis: z.number().min(0).optional(),
})

// Konfiguration für die ObjectPage
const futtermittelConfig: MaskConfig = {
  title: 'Einzelfuttermittel-Stammdaten',
  subtitle: 'Verwaltung von Einzelfuttermitteln nach EU 68/2013',
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
          placeholder: 'z.B. EF-001'
        },
        {
          name: 'name',
          label: 'Name',
          type: 'text',
          required: true,
          placeholder: 'z.B. Weizenmehl'
        },
        {
          name: 'typ',
          label: 'Typ',
          type: 'select',
          required: true,
          options: [
            { value: 'getreide', label: 'Getreide' },
            { value: 'oelsaat', label: 'Ölsaaten' },
            { value: 'protein', label: 'Proteinfuttermittel' },
            { value: 'mineralstoff', label: 'Mineralstoffe' },
            { value: 'sonstiges', label: 'Sonstiges' }
          ]
        },
        {
          name: 'hersteller',
          label: 'Hersteller',
          type: 'lookup',
          endpoint: '/api/partners',
          displayField: 'name',
          valueField: 'id'
        }
      ],
      layout: 'grid',
      columns: 2
    },
    {
      key: 'inhaltsstoffe',
      label: 'Inhaltsstoffe',
      fields: [
        {
          name: 'rohprotein',
          label: 'Rohprotein (%)',
          type: 'number',
          min: 0,
          max: 100,
          step: 0.1,
          helpText: 'EU-Kennzeichnung: Pflichtangabe'
        },
        {
          name: 'rohfett',
          label: 'Rohfett (%)',
          type: 'number',
          min: 0,
          max: 100,
          step: 0.1,
          helpText: 'EU-Kennzeichnung: Pflichtangabe'
        },
        {
          name: 'rohfaser',
          label: 'Rohfaser (%)',
          type: 'number',
          min: 0,
          max: 100,
          step: 0.1,
          helpText: 'EU-Kennzeichnung: Pflichtangabe'
        },
        {
          name: 'rohasche',
          label: 'Rohasche (%)',
          type: 'number',
          min: 0,
          max: 100,
          step: 0.1,
          helpText: 'EU-Kennzeichnung: Pflichtangabe'
        },
        {
          name: 'feuchte',
          label: 'Feuchte (%)',
          type: 'number',
          min: 0,
          max: 100,
          step: 0.1,
          helpText: 'EU-Kennzeichnung: Pflichtangabe'
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
          name: 'euKennzeichnung',
          label: 'EU-Kennzeichnung erforderlich',
          type: 'boolean',
          helpText: 'Nach Verordnung (EU) Nr. 68/2013'
        },
        {
          name: 'qsZertifikat',
          label: 'QS-Zertifikatsnummer',
          type: 'text',
          placeholder: 'z.B. QS-123456'
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
    baseUrl: '/api/futtermittel/einzelfuttermittel',
    endpoints: {
      list: '/api/futtermittel/einzelfuttermittel',
      get: '/api/futtermittel/einzelfuttermittel/{id}',
      create: '/api/futtermittel/einzelfuttermittel',
      update: '/api/futtermittel/einzelfuttermittel/{id}',
      delete: '/api/futtermittel/einzelfuttermittel/{id}'
    }
  },
  validation: futtermittelSchema,
  permissions: ['futtermittel.write', 'futtermittel.admin']
}

export default function EinzelfuttermittelStammPage(): JSX.Element {
  const navigate = useNavigate()
  const [isDirty, setIsDirty] = useState(false)

  // Framework Hooks verwenden
  const { data, loading, saveData } = useMaskData({
    apiUrl: futtermittelConfig.api.baseUrl,
    id: 'new' // Für neue Datensätze
  })

  const { validate, showValidationToast } = useMaskValidation(futtermittelConfig.validation)

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
        navigate('/futtermittel/einzelfuttermittel/liste')
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
    navigate('/futtermittel/einzelfuttermittel/liste')
  }

  return (
    <ObjectPage
      config={futtermittelConfig}
      data={data}
      onSave={handleSave}
      onCancel={handleCancel}
      isLoading={loading}
    />
  )
}