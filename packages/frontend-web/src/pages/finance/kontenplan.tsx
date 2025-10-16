import { useState } from 'react'
import { useNavigate } from 'react-router-dom'
import { ObjectPage } from '@/components/mask-builder'
import { useMaskData, useMaskValidation, useMaskActions } from '@/components/mask-builder/hooks'
import { MaskConfig } from '@/components/mask-builder/types'
import { z } from 'zod'

// Zod-Schema für Kontenplan
const kontenplanSchema = z.object({
  kontonummer: z.string().regex(/^\d{4,8}$/, "Kontonummer muss 4-8-stellig sein"),
  bezeichnung: z.string().min(1, "Bezeichnung ist erforderlich"),
  kontenart: z.enum(['Aktiva', 'Passiva', 'Aufwand', 'Ertrag', 'Kostenstelle', 'Kostenträger']),
  kontengruppe: z.string().min(1, "Kontengruppe ist erforderlich"),
  steuerschluessel: z.string().optional(),
  ustvaPosition: z.string().optional(),
  sperrstatus: z.boolean().default(false),
  auswertungsgruppe: z.string().optional(),
  notizen: z.string().optional(),
  anfangsbestand: z.number().default(0),
  waehrung: z.string().default("EUR"),
  periode: z.string().regex(/^\d{4}-\d{2}$/, "Periode muss YYYY-MM Format haben")
})

// Konfiguration für Kontenplan ObjectPage
const kontenplanConfig: MaskConfig = {
  title: 'Kontenplan',
  subtitle: 'Verwaltung des Kontenplans (SKR04)',
  type: 'object-page',
  tabs: [
    {
      key: 'allgemein',
      label: 'Allgemein',
      fields: [
        {
          name: 'kontonummer',
          label: 'Kontonummer',
          type: 'text',
          required: true,
          placeholder: 'z.B. 1000',
          maxLength: 8
        },
        {
          name: 'bezeichnung',
          label: 'Bezeichnung',
          type: 'text',
          required: true,
          placeholder: 'z.B. Kasse'
        },
        {
          name: 'kontenart',
          label: 'Kontenart',
          type: 'select',
          required: true,
          options: [
            { value: 'Aktiva', label: 'Aktiva' },
            { value: 'Passiva', label: 'Passiva' },
            { value: 'Aufwand', label: 'Aufwand' },
            { value: 'Ertrag', label: 'Ertrag' },
            { value: 'Kostenstelle', label: 'Kostenstelle' },
            { value: 'Kostenträger', label: 'Kostenträger' }
          ]
        },
        {
          name: 'kontengruppe',
          label: 'Kontengruppe',
          type: 'text',
          required: true,
          placeholder: 'z.B. 10 - Anlagevermögen'
        },
        {
          name: 'periode',
          label: 'Periode',
          type: 'text',
          required: true,
          placeholder: '2025-01',
          pattern: '^\\d{4}-\\d{2}$'
         } as any, {}
      ],
      layout: 'grid',
      columns: 2
    },
    {
      key: 'steuer',
      label: 'Steuer',
      fields: [
        {
          name: 'steuerschluessel',
          label: 'Steuerschlüssel',
          type: 'select',
          options: [
            { value: '1', label: '1 - Umsatzsteuer 19%' },
            { value: '2', label: '2 - Umsatzsteuer 7%' },
            { value: '3', label: '3 - Umsatzsteuer 0%' },
            { value: '8', label: '8 - nicht steuerbar' },
            { value: '9', label: '9 - Vorsteuer 19%' },
            { value: '10', label: '10 - Vorsteuer 7%' }
          ]
        },
        {
          name: 'ustvaPosition',
          label: 'UStVA-Position',
          type: 'text',
          placeholder: 'z.B. 66, 81, 35'
        }
      ]
    },
    {
      key: 'auswertung',
      label: 'Auswertung',
      fields: [
        {
          name: 'auswertungsgruppe',
          label: 'Auswertungsgruppe',
          type: 'text',
          placeholder: 'z.B. GuV, Bilanz'
        },
        {
          name: 'anfangsbestand',
          label: 'Anfangsbestand',
          type: 'number',
          step: 0.01,
          placeholder: '0.00'
        },
        {
          name: 'waehrung',
          label: 'Währung',
          type: 'select',
          options: [
            { value: 'EUR', label: 'EUR' },
            { value: 'USD', label: 'USD' },
            { value: 'GBP', label: 'GBP' }
          ]
        }
      ],
      layout: 'grid',
      columns: 2
    },
    {
      key: 'sperrstatus',
      label: 'Sperrstatus',
      fields: [
        {
          name: 'sperrstatus',
          label: 'Konto gesperrt',
          type: 'boolean',
          helpText: 'Gesperrte Konten können nicht für Buchungen verwendet werden'
        }
      ]
    },
    {
      key: 'notizen',
      label: 'Notizen',
      fields: [
        {
          name: 'notizen',
          label: 'Interne Notizen',
          type: 'textarea',
          placeholder: 'Zusätzliche Informationen zum Konto...'
        }
      ]
    }
  ],
  actions: [
    {
      key: 'validate',
      label: 'Validieren',
      type: 'secondary'
    , onClick: () => {} },
    {
      key: 'save',
      label: 'Speichern',
      type: 'primary'
    , onClick: () => {} },
    {
      key: 'export',
      label: 'DATEV Export',
      type: 'secondary'
    , onClick: () => {} }
  ],
  api: {
    baseUrl: '/api/finance/kontenplan',
    endpoints: {
      list: '/api/finance/kontenplan',
      get: '/api/finance/kontenplan/{id}',
      create: '/api/finance/kontenplan',
      update: '/api/finance/kontenplan/{id}',
      delete: '/api/finance/kontenplan/{id}'
    }
  } as any,
  validation: kontenplanSchema,
  permissions: ['fibu.read', 'fibu.write']
}

export default function KontenplanPage(): JSX.Element {
  const navigate = useNavigate()
  const [isDirty, setIsDirty] = useState(false)

  const { data, loading, saveData } = useMaskData({
    apiUrl: kontenplanConfig.api.baseUrl,
    id: 'new'
  })

  const { validate, showValidationToast } = useMaskValidation(kontenplanConfig.validation)

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
        navigate('/finance/kontenplan')
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
    } else if (action === 'export') {
      // DATEV Export
      window.open('/api/finance/kontenplan/export', '_blank')
    }
  })

  const handleSave = async (formData: any) => {
    await handleAction('save', formData)
  }

  const handleCancel = () => {
    if (isDirty && !confirm('Ungespeicherte Änderungen gehen verloren. Wirklich abbrechen?')) {
      return
    }
    navigate('/finance/kontenplan')
  }

  return (
    <ObjectPage
      config={kontenplanConfig}
      data={data}
      onSave={handleSave}
      onCancel={handleCancel}
      isLoading={loading}
    />
  )
}