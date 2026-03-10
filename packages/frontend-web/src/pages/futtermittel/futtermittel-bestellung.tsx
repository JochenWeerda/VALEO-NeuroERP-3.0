import { useState } from 'react'
import { useNavigate } from 'react-router-dom'
import { Wizard } from '@/components/mask-builder'
import { useMaskData } from '@/components/mask-builder/hooks'
import { WizardConfig } from '@/components/mask-builder/types'
import { validateFields } from '@/components/mask-builder/validation'
import { toast } from '@/hooks/use-toast'

const bestellungWizardConfig: WizardConfig = {
  title: 'Futtermittel-Bestellung',
  subtitle: 'Neue Bestellung bei Lieferanten aufgeben',
  type: 'wizard',
  steps: [
    {
      key: 'lieferant',
      title: 'Lieferant auswählen',
      description: 'Wählen Sie den Lieferanten und grundlegende Bestellinformationen',
      fields: [
        {
          name: 'lieferantId',
          label: 'Lieferant',
          type: 'lookup',
          required: true,
          endpoint: '/api/partners?type=supplier',
          displayField: 'name',
          valueField: 'id',
          helpText: 'Nur zertifizierte Futtermittel-Lieferanten verfügbar'
        },
        {
          name: 'liefertermin',
          label: 'Gewünschter Liefertermin',
          type: 'date',
          required: true
        },
        {
          name: 'zahlungsbedingungen',
          label: 'Zahlungsbedingungen',
          type: 'select',
          options: [
            { value: 'sofort', label: 'Sofortzahlung' },
            { value: '14tage', label: '14 Tage' },
            { value: '30tage', label: '30 Tage' },
            { value: '60tage', label: '60 Tage' }
          ]
        }
      ]
    },
    {
      key: 'positionen',
      title: 'Bestellpositionen',
      description: 'Fügen Sie die gewünschten Futtermittel hinzu',
      fields: [
        {
          name: 'bestellpositionen',
          label: 'Positionen',
          type: 'table',
          required: true,
          columns: [
            {
              key: 'futtermittelId',
              label: 'Futtermittel',
              type: 'lookup',
              required: true
            },
            {
              key: 'menge',
              label: 'Menge',
              type: 'number',
              required: true
            },
            {
              key: 'einheit',
              label: 'Einheit',
              type: 'select',
              required: true
            },
            {
              key: 'preisProEinheit',
              label: 'Preis/Einheit',
              type: 'number'
            },
            {
              key: 'wunschtermin',
              label: 'Wunschtermin',
              type: 'date'
            }
          ] as any,
          helpText: 'Fügen Sie alle gewünschten Futtermittel hinzu'
        }
      ]
    },
    {
      key: 'zusammenfassung',
      title: 'Bestellung zusammenfassen',
      description: 'Überprüfen Sie alle Angaben vor dem Absenden',
      fields: [
        {
          name: 'bemerkungen',
          label: 'Bemerkungen',
          type: 'textarea',
          placeholder: 'Zusätzliche Anweisungen oder Bemerkungen...'
        }
      ]
    }
  ],
  actions: [
    {
      key: 'save-draft',
      label: 'Entwurf speichern',
      type: 'secondary',
      onClick: () => {}
    },
    {
      key: 'send-order',
      label: 'Bestellung absenden',
      type: 'primary',
      onClick: () => {}
    }
  ],
  api: {
    baseUrl: '/api/futtermittel/bestellungen',
    endpoints: {
      create: '/api/futtermittel/bestellungen',
      update: '/api/futtermittel/bestellungen/{id}'
    }
  },
  permissions: ['futtermittel.order', 'supplier.read'],
  onComplete: () => {} // Wird über Wizard-Props überschrieben
}

export default function FuttermittelBestellungPage(): JSX.Element {
  const navigate = useNavigate()
  const [loading, setLoading] = useState(false)

  const { saveData } = useMaskData({
    apiUrl: bestellungWizardConfig.api.baseUrl
  })

  const validate = (formData: any) => validateFields(bestellungWizardConfig.steps.flatMap((step) => step.fields), formData ?? {})
  const showValidationToast = (errors: Record<string, string>) => {
    toast({ variant: 'destructive', title: 'Validierungsfehler', description: `${Object.keys(errors).length} Feld(er) muessen korrigiert werden.` })
  }

  const handleComplete = async (formData: any) => {
    const errors = validate(formData)
    if (Object.keys(errors).length > 0) {
      showValidationToast(errors)
      return
    }

    setLoading(true)
    try {
      await saveData(formData)
      toast({ title: 'Bestellung abgesendet', description: 'Die Bestellung wurde erfolgreich übermittelt.' })
      navigate('/futtermittel/bestellungen')
    } catch (error) {
      toast({ title: 'Fehler', description: 'Bestellung konnte nicht abgesendet werden.', variant: 'destructive' })
    } finally {
      setLoading(false)
    }
  }

  const handleCancel = () => {
    if (confirm('Bestellung wirklich abbrechen? Nicht gespeicherte Daten gehen verloren.')) {
      navigate('/futtermittel')
    }
  }

  return (
    <Wizard
      config={bestellungWizardConfig}
      onComplete={handleComplete}
      onCancel={handleCancel}
      isLoading={loading}
    />
  )
}