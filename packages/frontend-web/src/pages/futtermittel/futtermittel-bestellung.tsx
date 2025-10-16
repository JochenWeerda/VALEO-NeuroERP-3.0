import { useState } from 'react'
import { useNavigate } from 'react-router-dom'
import { Wizard } from '@/components/mask-builder'
import { useMaskData, useMaskValidation } from '@/components/mask-builder/hooks'
import { WizardConfig } from '@/components/mask-builder/types'
import { z } from 'zod'

// Zod-Schema für Bestellung
const bestellungSchema = z.object({
  lieferantId: z.string().min(1, "Lieferant ist erforderlich"),
  bestellpositionen: z.array(z.object({
    futtermittelId: z.string(),
    menge: z.number().min(0.1, "Menge muss größer 0 sein"),
    einheit: z.string(),
    preisProEinheit: z.number().min(0),
    wunschtermin: z.string().optional()
  })).min(1, "Mindestens eine Position erforderlich"),
  liefertermin: z.string().min(1, "Liefertermin ist erforderlich"),
  zahlungsbedingungen: z.string().optional(),
  bemerkungen: z.string().optional()
})

// Konfiguration für Bestellung Wizard
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
      ],
      validation: z.object({
        lieferantId: z.string().min(1),
        liefertermin: z.string().min(1)
      })
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
      ],
      validation: z.object({
        bestellpositionen: z.array(z.object({
          futtermittelId: z.string().min(1),
          menge: z.number().min(0.1),
          einheit: z.string().min(1)
        })).min(1)
      })
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
  validation: bestellungSchema,
  permissions: ['futtermittel.order', 'supplier.read'],
  onComplete: () => {} // Wird über Wizard-Props überschrieben
}

export default function FuttermittelBestellungPage(): JSX.Element {
  const navigate = useNavigate()
  const [loading, setLoading] = useState(false)

  const { saveData } = useMaskData({
    apiUrl: bestellungWizardConfig.api.baseUrl
  })

  const { validate, showValidationToast } = useMaskValidation(bestellungWizardConfig.validation)

  const handleComplete = async (formData: any) => {
    const isValid = validate(formData)
    if (!isValid.isValid) {
      showValidationToast(isValid.errors)
      return
    }

    setLoading(true)
    try {
      await saveData(formData)
      alert('Bestellung wurde erfolgreich abgesendet!')
      navigate('/futtermittel/bestellungen')
    } catch (error) {
      alert('Fehler beim Absenden der Bestellung')
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