import { useMemo, useState } from 'react'
import { useNavigate } from '@/app/routing/react-router-compat'
import { LeaveConfirmDialog } from '@/components/LeaveConfirmDialog'
import { ObjectPage } from '@/components/mask-builder'
import { useMaskActions, useMaskData } from '@/components/mask-builder/hooks'
import { MaskConfig } from '@/components/mask-builder/types'
import { getFieldsFromMaskConfig, validateFields } from '@/components/mask-builder/validation'
import { ModuleToolbar } from '@/components/navigation/ModuleToolbar'
import { toast } from '@/hooks/use-toast'
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
        { name: 'artikelnummer', label: 'Artikelnummer', type: 'text', required: true, placeholder: 'z.B. EF-001' },
        { name: 'name', label: 'Name', type: 'text', required: true, placeholder: 'z.B. Weizenmehl' },
        {
          name: 'typ',
          label: 'Typ',
          type: 'select',
          required: true,
          options: [
            { value: 'getreide', label: 'Getreide' },
            { value: 'oelsaat', label: 'Oelsaaten' },
            { value: 'protein', label: 'Proteinfuttermittel' },
            { value: 'mineralstoff', label: 'Mineralstoffe' },
            { value: 'sonstiges', label: 'Sonstiges' },
          ],
        },
        {
          name: 'hersteller',
          label: 'Hersteller',
          type: 'lookup',
          endpoint: '/api/v1/crm/business-partners',
          displayField: 'name',
          valueField: 'id',
        },
      ],
      layout: 'grid',
      columns: 2,
    },
    {
      key: 'inhaltsstoffe',
      label: 'Inhaltsstoffe',
      fields: [
        { name: 'rohprotein', label: 'Rohprotein (%)', type: 'number', min: 0, max: 100, step: 0.1, helpText: 'EU-Kennzeichnung: Pflichtangabe' },
        { name: 'rohfett', label: 'Rohfett (%)', type: 'number', min: 0, max: 100, step: 0.1, helpText: 'EU-Kennzeichnung: Pflichtangabe' },
        { name: 'rohfaser', label: 'Rohfaser (%)', type: 'number', min: 0, max: 100, step: 0.1, helpText: 'EU-Kennzeichnung: Pflichtangabe' },
        { name: 'rohasche', label: 'Rohasche (%)', type: 'number', min: 0, max: 100, step: 0.1, helpText: 'EU-Kennzeichnung: Pflichtangabe' },
        { name: 'feuchte', label: 'Feuchte (%)', type: 'number', min: 0, max: 100, step: 0.1, helpText: 'EU-Kennzeichnung: Pflichtangabe' },
      ],
      layout: 'grid',
      columns: 2,
    },
    {
      key: 'qualitaet',
      label: 'Qualitaet & Zertifizierung',
      fields: [
        { name: 'euKennzeichnung', label: 'EU-Kennzeichnung erforderlich', type: 'boolean', helpText: 'Nach Verordnung (EU) Nr. 68/2013' },
        { name: 'qsZertifikat', label: 'QS-Zertifikatsnummer', type: 'text', placeholder: 'z.B. QS-123456' },
        { name: 'gueltigBis', label: 'Zertifikat gueltig bis', type: 'date' },
      ],
    },
    {
      key: 'lager',
      label: 'Lager & Preise',
      fields: [
        { name: 'lagerbestand', label: 'Lagerbestand (kg)', type: 'number', min: 0, defaultValue: 0 },
        { name: 'ekPreis', label: 'EK-Preis (EUR/kg)', type: 'number', min: 0, step: 0.01 },
        { name: 'vkPreis', label: 'VK-Preis (EUR/kg)', type: 'number', min: 0, step: 0.01 },
      ],
      layout: 'grid',
      columns: 2,
    },
  ],
  actions: [
    { key: 'validate', label: 'Validieren', type: 'secondary' },
    { key: 'save', label: 'Speichern', type: 'primary' },
  ],
  api: {
    baseUrl: '/api/v1/futter/einzelfuttermittel',
    endpoints: {
      list: '/api/v1/futter/einzelfuttermittel',
      get: '/api/v1/futter/einzelfuttermittel/{id}',
      create: '/api/v1/futter/einzelfuttermittel',
      update: '/api/v1/futter/einzelfuttermittel/{id}',
      delete: '/api/v1/futter/einzelfuttermittel/{id}',
    },
  },
  permissions: ['futtermittel.write', 'futtermittel.admin'],
}

export default function EinzelfuttermittelStammPage(): JSX.Element {
  const navigate = useNavigate()
  const [isDirty, setIsDirty] = useState(false)

  const { data, loading, saveData } = useMaskData({
    apiUrl: futtermittelConfig.api.baseUrl,
    id: 'new',
  })

  const validate = (formData: any) => validateFields(getFieldsFromMaskConfig(futtermittelConfig), formData ?? {})
  const showValidationToast = (errors: Record<string, string>) => {
    toast({
      variant: 'destructive',
      title: 'Validierungsfehler',
      description: `${Object.keys(errors).length} Feld(er) muessen korrigiert werden.`,
    })
  }

  const { handleAction, loadingActionKey } = useMaskActions(async (action: string, formData: any) => {
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
      } catch {
        // already handled in useMaskData
      }
      return
    }

    if (action === 'validate') {
      const errors = validate(formData)
      if (Object.keys(errors).length === 0) {
        toast({ title: 'Validierung erfolgreich', description: 'Alle Felder sind korrekt ausgefuellt.' })
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
  const objectConfig = useMemo(
    () => ({
      ...futtermittelConfig,
      actions: [
        {
          key: 'validate',
          label: 'Validieren',
          type: 'secondary' as const,
          onClick: () => { void handleAction('validate', data) },
        },
        {
          key: 'save',
          label: 'Speichern',
          type: 'primary' as const,
          onClick: () => { void handleAction('save', data) },
        },
      ],
    }),
    [data, handleAction],
  )

  return (
    <>
      <ModuleToolbar
        backTarget="/futtermittel/einzelfuttermittel/liste"
        closeTarget="/futtermittel/einzelfuttermittel/liste"
        title="Einzelfuttermittel-Stamm"
      />
      <LeaveConfirmDialog
        blocker={blocker}
        onSave={() => handleSave(data)}
        title="Ungespeicherte Aenderungen"
        description="Moechten Sie speichern, verwerfen oder hier bleiben?"
      />
      <ObjectPage
        config={objectConfig}
        data={data}
        onSave={handleSave}
        onCancel={handleCancel}
        isLoading={loading}
        loadingActionKey={loadingActionKey}
      />
    </>
  )
}
