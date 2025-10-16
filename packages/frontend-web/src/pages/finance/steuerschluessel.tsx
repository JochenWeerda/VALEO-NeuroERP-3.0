import { useState } from 'react'
import { useNavigate } from 'react-router-dom'
import { ObjectPage } from '@/components/mask-builder'
import { useMaskData, useMaskValidation, useMaskActions } from '@/components/mask-builder/hooks'
import { MaskConfig } from '@/components/mask-builder/types'
import { z } from 'zod'

// Zod-Schema für Steuerschlüssel
const steuerschluesselSchema = z.object({
  code: z.string().regex(/^\d{1,2}$/, "Code muss 1-2-stellig sein"),
  bezeichnung: z.string().min(1, "Bezeichnung ist erforderlich"),
  steuersatz: z.number().min(0).max(100, "Steuersatz muss zwischen 0-100% liegen"),
  ustvaPosition: z.string().min(1, "UStVA-Position ist erforderlich"),
  ustvaBezeichnung: z.string().min(1, "UStVA-Bezeichnung ist erforderlich"),
  intracom: z.boolean().default(false),
  export: z.boolean().default(false),
  reverseCharge: z.boolean().default(false),
  gueltigVon: z.string().regex(/^\d{4}-\d{2}-\d{2}$/, "Datum muss YYYY-MM-DD Format haben"),
  gueltigBis: z.string().optional(),
  notizen: z.string().optional()
})

// Konfiguration für Steuerschlüssel ObjectPage
const steuerschluesselConfig: MaskConfig = {
  title: 'Steuerschlüssel & MwSt-Sätze',
  subtitle: 'Verwaltung der Steuerschlüssel und Umsatzsteuersätze',
  type: 'object-page',
  tabs: [
    {
      key: 'allgemein',
      label: 'Allgemein',
      fields: [
        {
          name: 'code',
          label: 'Steuerschlüssel',
          type: 'text',
          required: true,
          placeholder: 'z.B. 1, 9, 10',
          maxLength: 2,
          helpText: 'Offizieller Steuerschlüssel nach deutschem Steuerrecht'
        },
        {
          name: 'bezeichnung',
          label: 'Bezeichnung',
          type: 'text',
          required: true,
          placeholder: 'z.B. Umsatzsteuer 19%'
        },
        {
          name: 'steuersatz',
          label: 'Steuersatz (%)',
          type: 'number',
          required: true,
          min: 0,
          max: 100,
          step: 0.01,
          placeholder: '19.00'
        },
        {
          name: 'gueltigVon',
          label: 'Gültig von',
          type: 'date',
          required: true
        },
        {
          name: 'gueltigBis',
          label: 'Gültig bis',
          type: 'date',
          helpText: 'Leer lassen für unbefristete Gültigkeit'
        }
      ],
      layout: 'grid',
      columns: 2
    },
    {
      key: 'ustva',
      label: 'UStVA-Mapping',
      fields: [
        {
          name: 'ustvaPosition',
          label: 'UStVA-Position',
          type: 'text',
          required: true,
          placeholder: 'z.B. 66, 81, 35, 77',
          helpText: 'Position in der Umsatzsteuervoranmeldung'
        },
        {
          name: 'ustvaBezeichnung',
          label: 'UStVA-Bezeichnung',
          type: 'text',
          required: true,
          placeholder: 'z.B. Steuerpflichtige Umsätze 19%'
        }
      ]
    },
    {
      key: 'sonderfaelle',
      label: 'Sonderfälle',
      fields: [
        {
          name: 'intracom',
          label: 'Intracommunity-Lieferung',
          type: 'boolean',
          helpText: 'Für innergemeinschaftliche Lieferungen (EU)'
        },
        {
          name: 'export',
          label: 'Ausfuhr/Export',
          type: 'boolean',
          helpText: 'Für Ausfuhren außerhalb der EU'
        },
        {
          name: 'reverseCharge',
          label: 'Reverse Charge',
          type: 'boolean',
          helpText: 'Umkehrung der Steuerschuldnerschaft'
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
          placeholder: 'Zusätzliche Informationen zum Steuerschlüssel...'
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
      key: 'ustva-export',
      label: 'UStVA Export',
      type: 'secondary'
    , onClick: () => {} }
  ],
  api: {
    baseUrl: '/api/finance/steuerschluessel',
    endpoints: {
      list: '/api/finance/steuerschluessel',
      get: '/api/finance/steuerschluessel/{id}',
      create: '/api/finance/steuerschluessel',
      update: '/api/finance/steuerschluessel/{id}',
      delete: '/api/finance/steuerschluessel/{id}'
    }
  } as any,
  validation: steuerschluesselSchema,
  permissions: ['fibu.read', 'fibu.write']
}

export default function SteuerschluesselPage(): JSX.Element {
  const navigate = useNavigate()
  const [isDirty, setIsDirty] = useState(false)

  const { data, loading, saveData } = useMaskData({
    apiUrl: steuerschluesselConfig.api.baseUrl,
    id: 'new'
  })

  const { validate, showValidationToast } = useMaskValidation(steuerschluesselConfig.validation)

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
        navigate('/finance/steuerschluessel')
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
    } else if (action === 'ustva-export') {
      // UStVA Export
      window.open('/api/finance/steuerschluessel/export', '_blank')
    }
  })

  const handleSave = async (formData: any) => {
    await handleAction('save', formData)
  }

  const handleCancel = () => {
    if (isDirty && !confirm('Ungespeicherte Änderungen gehen verloren. Wirklich abbrechen?')) {
      return
    }
    navigate('/finance/steuerschluessel')
  }

  return (
    <ObjectPage
      config={steuerschluesselConfig}
      data={data}
      onSave={handleSave}
      onCancel={handleCancel}
      isLoading={loading}
    />
  )
}