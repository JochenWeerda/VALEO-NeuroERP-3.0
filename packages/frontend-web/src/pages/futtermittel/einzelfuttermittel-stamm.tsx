import { useState } from 'react'
import { useNavigate } from 'react-router-dom'
import { ObjectPage } from '@/components/mask-builder'
import { useMaskData, useMaskActions } from '@/components/mask-builder/hooks'
import { MaskConfig } from '@/components/mask-builder/types'
import { getFieldsFromMaskConfig, validateFields } from '@/components/mask-builder/validation'
import { toast } from '@/hooks/use-toast'
import { ModuleToolbar } from '@/components/navigation/ModuleToolbar'
import { LeaveConfirmDialog } from '@/components/LeaveConfirmDialog'
import { useUnsavedChanges } from '@/hooks/useUnsavedChanges'

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
          endpoint: '/api/v1/crm/business-partners',
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
      onClick: () => toast({ title: 'Validierung', description: 'Futtermittel-Daten werden validiert.' })
    },
    {
      key: 'save',
      label: 'Speichern',
      type: 'primary',
      onClick: () => toast({ title: 'Gespeichert', description: 'Einzelfuttermittel wurde gespeichert.' })
    }
  ],
  api: {
    baseUrl: '/api/v1/futter/einzelfuttermittel',
    endpoints: {
      list: '/api/v1/futter/einzelfuttermittel',
      get: '/api/v1/futter/einzelfuttermittel/{id}',
      create: '/api/v1/futter/einzelfuttermittel',
      update: '/api/v1/futter/einzelfuttermittel/{id}',
      delete: '/api/v1/futter/einzelfuttermittel/{id}'
    }
  },
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

  const validate = (formData: any) => validateFields(getFieldsFromMaskConfig(futtermittelConfig), formData ?? {})
  const showValidationToast = (errors: Record<string, string>) => {
    toast({ variant: 'destructive', title: 'Validierungsfehler', description: `${Object.keys(errors).length} Feld(er) muessen korrigiert werden.` })
  }

  const { handleAction } = useMaskActions(async (action: string, formData: any) => {
    if (action === 'save') {
      const errors = validate(formData)
      if (Object.keys(errors).length > 0) {
        showValidationToast(errors)
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
      const errors = validate(formData)
      if (Object.keys(errors).length === 0) {
        toast({ title: 'Validierung erfolgreich', description: 'Alle Felder sind korrekt ausgefüllt.' })
      } else {
        showValidationToast(errors)
      }
    }
  })

  const handleSave = async (formData: any) => {
    await handleAction('save', formData)
  }

  const handleCancel = () => {
    navigate('/futtermittel/einzelfuttermittel/liste')
  }

  const blocker = useUnsavedChanges(isDirty)

  return (
    <>
      <ModuleToolbar backTarget="/futtermittel/einzelfuttermittel/liste" closeTarget="/futtermittel/einzelfuttermittel/liste" title="Einzelfuttermittel-Stamm" />
      <LeaveConfirmDialog blocker={blocker} onSave={() => handleSave(data)} title="Ungespeicherte Änderungen" description="Möchten Sie speichern, verwerfen oder hier bleiben?" />
      <ObjectPage
        config={futtermittelConfig}
        data={data}
        onSave={handleSave}
        onCancel={handleCancel}
        isLoading={loading}
      />
    </>
  )
}
