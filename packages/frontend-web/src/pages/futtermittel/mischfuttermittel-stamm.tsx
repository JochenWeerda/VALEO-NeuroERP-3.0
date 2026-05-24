import { useMemo, useState } from 'react'
import { useNavigate } from 'react-router-dom'
import { ObjectPage } from '@/components/mask-builder'
import { useMaskActions, useMaskData } from '@/components/mask-builder/hooks'
import { MaskConfig } from '@/components/mask-builder/types'
import { getFieldsFromMaskConfig, validateFields } from '@/components/mask-builder/validation'
import { toast } from '@/hooks/use-toast'
import { api } from '@/lib/axios'

const mischfuttermittelConfig: MaskConfig = {
  title: 'Mischfuttermittel-Stammdaten',
  subtitle: 'Verwaltung von Mischfuttermitteln nach EU 767/2009',
  type: 'object-page',
  tabs: [
    {
      key: 'allgemein',
      label: 'Allgemein',
      fields: [
        { name: 'artikelnummer', label: 'Artikelnummer', type: 'text', required: true, placeholder: 'z.B. MF-001' },
        { name: 'name', label: 'Name', type: 'text', required: true, placeholder: 'z.B. Milchviehfutter Premium' },
        {
          name: 'typ',
          label: 'Typ',
          type: 'select',
          required: true,
          options: [
            { value: 'alleinfuttermittel', label: 'Alleinfuttermittel' },
            { value: 'ergaenzungsfuttermittel', label: 'Ergaenzungsfuttermittel' },
            { value: 'mineralstoffmischung', label: 'Mineralstoffmischung' },
          ],
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
            { value: 'gefluegel', label: 'Gefluegel' },
            { value: 'pferde', label: 'Pferde' },
            { value: 'schafe', label: 'Schafe' },
          ],
        },
      ],
      layout: 'grid',
      columns: 2,
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
            { value: 'gefluegel', label: 'Gefluegel' },
            { value: 'pferd', label: 'Pferd' },
            { value: 'schaf', label: 'Schaf' },
            { value: 'ziege', label: 'Ziege' },
          ],
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
            { value: 'alle', label: 'Alle Phasen' },
          ],
        },
      ],
    },
    {
      key: 'rezeptur',
      label: 'Rezeptur',
      fields: [
        { name: 'komponenten', label: 'Komponenten', type: 'textarea', helpText: 'Rezeptur-Komponenten werden separat verwaltet' },
      ],
    },
    {
      key: 'naehrwerte',
      label: 'Naehrwerte',
      fields: [
        { name: 'gesamtRohprotein', label: 'Gesamt Rohprotein (%)', type: 'number', min: 0, max: 100, step: 0.1, readonly: true, helpText: 'Berechnet aus Rezeptur' },
        { name: 'gesamtRohfett', label: 'Gesamt Rohfett (%)', type: 'number', min: 0, max: 100, step: 0.1, readonly: true },
        { name: 'gesamtRohfaser', label: 'Gesamt Rohfaser (%)', type: 'number', min: 0, max: 100, step: 0.1, readonly: true },
        { name: 'gesamtRohasche', label: 'Gesamt Rohasche (%)', type: 'number', min: 0, max: 100, step: 0.1, readonly: true },
        { name: 'umsetzbareEnergie', label: 'Umsetzbare Energie (MJ/kg)', type: 'number', min: 0, step: 0.1, readonly: true },
      ],
      layout: 'grid',
      columns: 2,
    },
    {
      key: 'qualitaet',
      label: 'Qualitaet & Zertifizierung',
      fields: [
        { name: 'qsZertifikat', label: 'QS-Zertifikatsnummer', type: 'text', placeholder: 'z.B. QS-MF-123456' },
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
    { key: 'calculate', label: 'Naehrwerte berechnen', type: 'secondary' },
    { key: 'validate', label: 'Validieren', type: 'secondary' },
    { key: 'save', label: 'Speichern', type: 'primary' },
  ],
  api: {
    baseUrl: '/api/v1/futter/mischfuttermittel',
    endpoints: {
      list: '/api/v1/futter/mischfuttermittel',
      get: '/api/v1/futter/mischfuttermittel/{id}',
      create: '/api/v1/futter/mischfuttermittel',
      update: '/api/v1/futter/mischfuttermittel/{id}',
      delete: '/api/v1/futter/mischfuttermittel/{id}',
    },
  },
  permissions: ['futtermittel.write', 'futtermittel.admin'],
}

export default function MischfuttermittelStammPage(): JSX.Element {
  const navigate = useNavigate()
  const [isDirty, setIsDirty] = useState(false)

  const { data, loading, saveData } = useMaskData({
    apiUrl: mischfuttermittelConfig.api.baseUrl,
    id: 'new',
  })

  const validate = (formData: any) => validateFields(getFieldsFromMaskConfig(mischfuttermittelConfig), formData ?? {})
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
        navigate('/futtermittel/mischfuttermittel/liste')
      } catch {
        // already handled by useMaskData
      }
      return
    }

    if (action === 'calculate') {
      const komponenten = (formData.komponenten as Array<{ futtermittelId: string; anteil: number }>) ?? []
      if (komponenten.length === 0) {
        toast({ title: 'Keine Komponenten', description: 'Bitte zuerst Rezeptur-Komponenten erfassen.', variant: 'destructive' })
        return
      }

      try {
        const res = await api.post('/api/v1/futter/mischfuttermittel/naehrwerte/berechnen', {
          komponenten,
          fan: 2.5,
          modus: 'beratung',
        })
        const result = res.data as {
          gesamtRohprotein: number
          me_fan1: number
          nel: number
          sidp: number
          formelwerk_energie: string
          formelwerk_protein: string
          omd_methode: string
          omd_fan1_pct: number
        }
        toast({
          title: `Naehrwerte berechnet (${result.formelwerk_energie} / ${result.formelwerk_protein})`,
          description: [
            `XP: ${result.gesamtRohprotein} g/kg TM`,
            `ME FAN1: ${result.me_fan1} MJ/kg TM`,
            `NEL: ${result.nel} MJ/kg TM`,
            `sidP: ${result.sidp} g/kg TM`,
            `OMD: ${result.omd_fan1_pct}% (${result.omd_methode})`,
          ].join(' | '),
        })
      } catch (e: any) {
        toast({ title: 'Berechnung fehlgeschlagen', description: e.response?.data?.detail ?? e.message, variant: 'destructive' })
      }
      return
    }

    if (action === 'validate') {
      const errors = validate(formData)
      if (Object.keys(errors).length === 0) {
        toast({ title: 'Validierung erfolgreich', description: 'Alle Pflichtfelder sind korrekt ausgefuellt.' })
      } else {
        showValidationToast(errors)
      }
    }
  })

  const handleSave = async (formData: any) => {
    await handleAction('save', formData)
  }

  const handleCancel = () => {
    if (isDirty && !confirm('Ungespeicherte Aenderungen gehen verloren. Wirklich abbrechen?')) return
    navigate('/futtermittel/mischfuttermittel/liste')
  }

  const objectConfig = useMemo(
    () => ({
      ...mischfuttermittelConfig,
      actions: [
        {
          key: 'calculate',
          label: 'Naehrwerte berechnen',
          type: 'secondary' as const,
          onClick: () => { void handleAction('calculate', data) },
        },
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
    <ObjectPage
      config={objectConfig}
      data={data}
      onSave={handleSave}
      onCancel={handleCancel}
      isLoading={loading}
      loadingActionKey={loadingActionKey}
    />
  )
}
