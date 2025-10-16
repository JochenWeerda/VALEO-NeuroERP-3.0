import { useState } from 'react'
import { useNavigate, useParams } from 'react-router-dom'
import { ObjectPage } from '@/components/mask-builder'
import { useMaskData } from '@/components/mask-builder/hooks'
import { MaskConfig } from '@/components/mask-builder/types'
import { z } from 'zod'

// Zod-Schema für Auftragsbestätigung
const auftragsbestaetigungSchema = z.object({
  bestellungId: z.string().min(1, "Bestellung ist erforderlich"),
  bestaetigungsNummer: z.string().min(1, "Bestätigungsnummer ist erforderlich"),
  status: z.enum(['OFFEN', 'GEPRUEFT', 'BESTAETIGT']),
  bestaetigteTermine: z.array(z.object({
    positionId: z.string(),
    bestaetigterTermin: z.string().min(1, "Termin ist erforderlich"),
    abweichung: z.string().optional()
  })),
  preisabweichungen: z.array(z.object({
    positionId: z.string(),
    urspruenglicherPreis: z.number(),
    neuerPreis: z.number(),
    begruendung: z.string().optional()
  })),
  bemerkungen: z.string().optional()
})

// Konfiguration für Auftragsbestätigung ObjectPage
const auftragsbestaetigungConfig: MaskConfig = {
  title: 'Auftragsbestätigung',
  subtitle: 'Lieferanten-Rückmeldung zu Bestellung',
  type: 'object-page',
  tabs: [
    {
      key: 'stammdaten',
      label: 'Stammdaten',
      fields: [
        {
          name: 'bestellungId',
          label: 'Bestellung',
          type: 'lookup',
          required: true,
          endpoint: '/api/einkauf/bestellungen?status=FREIGEGEBEN',
          displayField: 'nummer',
          valueField: 'id'
        },
        {
          name: 'bestaetigungsNummer',
          label: 'AB-Nummer',
          type: 'text',
          required: true
        },
        {
          name: 'status',
          label: 'Status',
          type: 'select',
          required: true,
          options: [
            { value: 'OFFEN', label: 'Offen' },
            { value: 'GEPRUEFT', label: 'Geprüft' },
            { value: 'BESTAETIGT', label: 'Bestätigt' }
          ]
        }
      ]
    },
    {
      key: 'termine',
      label: 'Terminbestätigungen',
      fields: [
        {
          name: 'bestaetigteTermine',
          label: 'Terminabweichungen',
          type: 'table',
          columns: [
            {
              key: 'positionId',
              label: 'Position',
              type: 'text',
              required: true
            },
            {
              key: 'bestaetigterTermin',
              label: 'Bestätigter Termin',
              type: 'date',
              required: true
            },
            {
              key: 'abweichung',
              label: 'Abweichung',
              type: 'text'
            }
          ] as any,
          helpText: 'Terminliche Abweichungen vom Lieferanten'
        }
      ]
    },
    {
      key: 'preise',
      label: 'Preisabweichungen',
      fields: [
        {
          name: 'preisabweichungen',
          label: 'Preisänderungen',
          type: 'table',
          columns: [
            {
              key: 'positionId',
              label: 'Position',
              type: 'text',
              required: true
            },
            {
              key: 'urspruenglicherPreis',
              label: 'Ursprünglicher Preis',
              type: 'number',
              required: true
            },
            {
              key: 'neuerPreis',
              label: 'Neuer Preis',
              type: 'number',
              required: true
            },
            {
              key: 'begruendung',
              label: 'Begründung',
              type: 'text'
            }
          ] as any,
          helpText: 'Preisliche Abweichungen vom Lieferanten'
        }
      ]
    },
    {
      key: 'belege',
      label: 'Belege',
      fields: [
        {
          name: 'bemerkungen',
          label: 'Bemerkungen',
          type: 'textarea',
          placeholder: 'Zusätzliche Informationen zur Auftragsbestätigung...'
        }
      ]
    }
  ],
  actions: [
    {
      key: 'pruefen',
      label: 'Prüfen',
      type: 'secondary',
      onClick: () => console.log('Prüfen clicked')
    },
    {
      key: 'bestaetigen',
      label: 'Bestätigen',
      type: 'primary',
      onClick: () => console.log('Bestätigen clicked')
    }
  ],
  api: {
    baseUrl: '/api/einkauf/auftragsbestaetigungen',
    endpoints: {
      list: '/api/einkauf/auftragsbestaetigungen',
      get: '/api/einkauf/auftragsbestaetigungen/{id}',
      create: '/api/einkauf/auftragsbestaetigungen',
      update: '/api/einkauf/auftragsbestaetigungen/{id}',
      delete: '/api/einkauf/auftragsbestaetigungen/{id}'
    }
  },
  validation: auftragsbestaetigungSchema,
  permissions: ['einkauf.read', 'einkauf.write']
}

export default function AuftragsbestaetigungPage(): JSX.Element {
  const navigate = useNavigate()
  const { id } = useParams<{ id: string }>()
  const [loading, setLoading] = useState(false)

  const { data, saveData } = useMaskData({
    apiUrl: auftragsbestaetigungConfig.api.baseUrl,
    id: id || undefined
  })

  const handleSave = async (formData: any) => {
    setLoading(true)
    try {
      await saveData(formData)
      navigate('/einkauf/auftragsbestaetigungen')
    } catch (error) {
      console.error('Fehler beim Speichern:', error)
    } finally {
      setLoading(false)
    }
  }

  const handleCancel = () => {
    if (confirm('Änderungen wirklich verwerfen?')) {
      navigate('/einkauf/auftragsbestaetigungen')
    }
  }

  return (
    <ObjectPage
      config={auftragsbestaetigungConfig}
      data={data}
      onSave={handleSave}
      onCancel={handleCancel}
      isLoading={loading}
    />
  )
}