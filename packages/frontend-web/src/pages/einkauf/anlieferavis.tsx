import { useState } from 'react'
import { useNavigate, useParams } from 'react-router-dom'
import { ObjectPage } from '@/components/mask-builder'
import { useMaskData } from '@/components/mask-builder/hooks'
import { MaskConfig } from '@/components/mask-builder/types'
import { z } from 'zod'

// Zod-Schema für Anlieferavis
const anlieferavisSchema = z.object({
  bestellungId: z.string().min(1, "Bestellung ist erforderlich"),
  avisNummer: z.string().min(1, "Avis-Nummer ist erforderlich"),
  status: z.enum(['GESENDET', 'BESTAETIGT', 'STORNIERT']),
  geplantesAnlieferDatum: z.string().min(1, "Anlieferdatum ist erforderlich"),
  fahrzeug: z.object({
    kennzeichen: z.string().min(1, "Kennzeichen ist erforderlich"),
    fahrer: z.string().min(1, "Fahrer ist erforderlich"),
    telefon: z.string().optional()
  }),
  positionen: z.array(z.object({
    positionId: z.string(),
    menge: z.number().min(0.1, "Menge muss > 0 sein"),
    chargenNummer: z.string().optional(),
    verpackung: z.string().optional()
  })),
  bemerkungen: z.string().optional()
})

// Konfiguration für Anlieferavis ObjectPage
const anlieferavisConfig: MaskConfig = {
  title: 'Anlieferavis',
  subtitle: 'Lieferavis für Wareneingangsvorbereitung',
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
          name: 'avisNummer',
          label: 'Avis-Nummer',
          type: 'text',
          required: true
        },
        {
          name: 'status',
          label: 'Status',
          type: 'select',
          required: true,
          options: [
            { value: 'GESENDET', label: 'Gesendet' },
            { value: 'BESTAETIGT', label: 'Bestätigt' },
            { value: 'STORNIERT', label: 'Storniert' }
          ]
        },
        {
          name: 'geplantesAnlieferDatum',
          label: 'Geplantes Anlieferdatum',
          type: 'datetime',
          required: true
        }
      ]
    },
    {
      key: 'fahrzeug',
      label: 'Fahrzeug & Fahrer',
      fields: [
        {
          name: 'fahrzeug.kennzeichen',
          label: 'Kennzeichen',
          type: 'text',
          required: true
        },
        {
          name: 'fahrzeug.fahrer',
          label: 'Fahrer',
          type: 'text',
          required: true
        },
        {
          name: 'fahrzeug.telefon',
          label: 'Telefon',
          type: 'text'
        }
      ]
    },
    {
      key: 'positionen',
      label: 'Positionen',
      fields: [
        {
          name: 'positionen',
          label: 'Avis-Positionen',
          type: 'table',
          required: true,
          columns: [
            {
              key: 'positionId',
              label: 'Bestellposition',
              type: 'text',
              required: true
            },
            {
              key: 'menge',
              label: 'Menge',
              type: 'number',
              required: true
            },
            {
              key: 'chargenNummer',
              label: 'Charge-Nr.',
              type: 'text'
            },
            {
              key: 'verpackung',
              label: 'Verpackung',
              type: 'text'
            }
          ] as any,
          helpText: 'Zu erwartende Lieferpositionen'
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
          placeholder: 'Zusätzliche Informationen zum Avis...'
        }
      ]
    }
  ],
  actions: [
    {
      key: 'senden',
      label: 'Avis senden',
      type: 'primary',
      onClick: () => console.log('Senden clicked')
    },
    {
      key: 'bestaetigen',
      label: 'Bestätigen',
      type: 'secondary',
      onClick: () => console.log('Bestätigen clicked')
    },
    {
      key: 'stornieren',
      label: 'Stornieren',
      type: 'danger',
      onClick: () => console.log('Stornieren clicked')
    }
  ],
  api: {
    baseUrl: '/api/einkauf/anlieferavis',
    endpoints: {
      list: '/api/einkauf/anlieferavis',
      get: '/api/einkauf/anlieferavis/{id}',
      create: '/api/einkauf/anlieferavis',
      update: '/api/einkauf/anlieferavis/{id}',
      delete: '/api/einkauf/anlieferavis/{id}'
    }
  },
  validation: anlieferavisSchema,
  permissions: ['einkauf.read', 'einkauf.write', 'warehouse.read']
}

export default function AnlieferavisPage(): JSX.Element {
  const navigate = useNavigate()
  const { id } = useParams<{ id: string }>()
  const [loading, setLoading] = useState(false)

  const { data, saveData } = useMaskData({
    apiUrl: anlieferavisConfig.api.baseUrl,
    id: id || undefined
  })

  const handleSave = async (formData: any) => {
    setLoading(true)
    try {
      await saveData(formData)
      navigate('/einkauf/anlieferavis')
    } catch (error) {
      console.error('Fehler beim Speichern:', error)
    } finally {
      setLoading(false)
    }
  }

  const handleCancel = () => {
    if (confirm('Änderungen wirklich verwerfen?')) {
      navigate('/einkauf/anlieferavis')
    }
  }

  return (
    <ObjectPage
      config={anlieferavisConfig}
      data={data}
      onSave={handleSave}
      onCancel={handleCancel}
      isLoading={loading}
    />
  )
}