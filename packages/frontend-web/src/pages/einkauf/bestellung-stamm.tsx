import { useState } from 'react'
import { useNavigate, useParams } from 'react-router-dom'
import { ObjectPage } from '@/components/mask-builder'
import { useMaskData } from '@/components/mask-builder/hooks'
import { MaskConfig } from '@/components/mask-builder/types'
import { z } from 'zod'

// Zod-Schema für Bestellung
const bestellungSchema = z.object({
  nummer: z.string().min(1, "Bestellnummer ist erforderlich"),
  lieferantId: z.string().min(1, "Lieferant ist erforderlich"),
  status: z.enum(['ENTWURF', 'FREIGEGEBEN', 'TEILGELIEFERT', 'VOLLGELIEFERT', 'STORNIERT']),
  liefertermin: z.string().min(1, "Liefertermin ist erforderlich"),
  zahlungsbedingungen: z.string().optional(),
  positionen: z.array(z.object({
    artikelId: z.string().min(1, "Artikel ist erforderlich"),
    menge: z.number().min(0.1, "Menge muss größer 0 sein"),
    einheit: z.string().min(1, "Einheit ist erforderlich"),
    preis: z.number().min(0, "Preis muss >= 0 sein"),
    wunschtermin: z.string().optional()
  })).min(1, "Mindestens eine Position erforderlich"),
  bemerkungen: z.string().optional()
})

// Konfiguration für Bestellung ObjectPage
const bestellungConfig: MaskConfig = {
  title: 'Bestellung',
  subtitle: 'Einkaufsbestellung bearbeiten',
  type: 'object-page',
  tabs: [
    {
      key: 'stammdaten',
      label: 'Stammdaten',
      fields: [
        {
          name: 'nummer',
          label: 'Bestellnummer',
          type: 'text',
          required: true,
          readonly: true
        },
        {
          name: 'lieferantId',
          label: 'Lieferant',
          type: 'lookup',
          required: true,
          endpoint: '/api/partners?type=supplier',
          displayField: 'name',
          valueField: 'id'
        },
        {
          name: 'status',
          label: 'Status',
          type: 'select',
          required: true,
          options: [
            { value: 'ENTWURF', label: 'Entwurf' },
            { value: 'FREIGEGEBEN', label: 'Freigegeben' },
            { value: 'TEILGELIEFERT', label: 'Teilgeliefert' },
            { value: 'VOLLGELIEFERT', label: 'Vollgeliefert' },
            { value: 'STORNIERT', label: 'Storniert' }
          ]
        },
        {
          name: 'liefertermin',
          label: 'Liefertermin',
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
      label: 'Positionen',
      fields: [
        {
          name: 'positionen',
          label: 'Bestellpositionen',
          type: 'table',
          required: true,
          columns: [
            {
              key: 'artikelId',
              label: 'Artikel',
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
              key: 'preis',
              label: 'Preis',
              type: 'number'
            },
            {
              key: 'wunschtermin',
              label: 'Wunschtermin',
              type: 'date'
            }
          ] as any,
          helpText: 'Bestellpositionen verwalten'
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
          placeholder: 'Zusätzliche Informationen zur Bestellung...'
        }
      ]
    }
  ],
  actions: [
    {
      key: 'freigeben',
      label: 'Freigeben',
      type: 'primary',
      onClick: () => console.log('Freigeben clicked')
    },
    {
      key: 'stornieren',
      label: 'Stornieren',
      type: 'danger',
      onClick: () => console.log('Stornieren clicked')
    },
    {
      key: 'drucken',
      label: 'Drucken',
      type: 'secondary',
      onClick: () => console.log('Drucken clicked')
    }
  ],
  api: {
    baseUrl: '/api/einkauf/bestellungen',
    endpoints: {
      list: '/api/einkauf/bestellungen',
      get: '/api/einkauf/bestellungen/{id}',
      create: '/api/einkauf/bestellungen',
      update: '/api/einkauf/bestellungen/{id}',
      delete: '/api/einkauf/bestellungen/{id}'
    }
  },
  validation: bestellungSchema,
  permissions: ['einkauf.read', 'einkauf.write']
}

export default function BestellungStammPage(): JSX.Element {
  const navigate = useNavigate()
  const { id } = useParams<{ id: string }>()
  const [loading, setLoading] = useState(false)

  const { data, saveData } = useMaskData({
    apiUrl: bestellungConfig.api.baseUrl,
    id: id || undefined
  })

  const handleSave = async (formData: any) => {
    setLoading(true)
    try {
      await saveData(formData)
      navigate('/einkauf/bestellungen-liste')
    } catch (error) {
      console.error('Fehler beim Speichern:', error)
    } finally {
      setLoading(false)
    }
  }

  const handleCancel = () => {
    if (confirm('Änderungen wirklich verwerfen?')) {
      navigate('/einkauf/bestellungen-liste')
    }
  }

  return (
    <ObjectPage
      config={bestellungConfig}
      data={data}
      onSave={handleSave}
      onCancel={handleCancel}
      isLoading={loading}
    />
  )
}