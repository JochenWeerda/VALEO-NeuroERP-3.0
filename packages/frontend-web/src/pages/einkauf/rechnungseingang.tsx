import { useState } from 'react'
import { useNavigate, useParams } from 'react-router-dom'
import { ObjectPage } from '@/components/mask-builder'
import { useMaskData } from '@/components/mask-builder/hooks'
import { MaskConfig } from '@/components/mask-builder/types'
import { z } from 'zod'

// Zod-Schema für Rechnungseingang
const rechnungseingangSchema = z.object({
  lieferantId: z.string().min(1, "Lieferant ist erforderlich"),
  bestellungId: z.string().optional(),
  wareneingangId: z.string().optional(),
  rechnungsNummer: z.string().min(1, "Rechnungsnummer ist erforderlich"),
  rechnungsDatum: z.string().min(1, "Rechnungsdatum ist erforderlich"),
  status: z.enum(['ERFASST', 'GEPRUEFT', 'FREIGEGEBEN', 'VERBUCHT', 'BEZAHLT']),
  bruttoBetrag: z.number().min(0.01, "Betrag muss > 0 sein"),
  nettoBetrag: z.number().min(0),
  steuerBetrag: z.number().min(0),
  steuerSatz: z.number().min(0),
  skonto: z.object({
    prozent: z.number().min(0),
    betrag: z.number().min(0),
    frist: z.string().optional()
  }),
  zahlungsziel: z.string().min(1, "Zahlungsziel ist erforderlich"),
  positionen: z.array(z.object({
    artikelId: z.string(),
    menge: z.number(),
    preis: z.number(),
    steuerSatz: z.number(),
    gesamt: z.number()
  })),
  abweichungen: z.array(z.object({
    typ: z.enum(['MENGE', 'PREIS', 'QUALITAET']),
    beschreibung: z.string(),
    betrag: z.number().optional()
  })),
  bemerkungen: z.string().optional()
})

// Konfiguration für Rechnungseingang ObjectPage
const rechnungseingangConfig: MaskConfig = {
  title: 'Rechnungseingang',
  subtitle: 'Eingehende Lieferantenrechnung verarbeiten',
  type: 'object-page',
  tabs: [
    {
      key: 'stammdaten',
      label: 'Stammdaten',
      fields: [
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
          name: 'bestellungId',
          label: 'Bestellung',
          type: 'lookup',
          endpoint: '/api/einkauf/bestellungen',
          displayField: 'nummer',
          valueField: 'id',
          helpText: 'Verknüpfung mit Bestellung (optional)'
        },
        {
          name: 'wareneingangId',
          label: 'Wareneingang',
          type: 'lookup',
          endpoint: '/api/lager/wareneingaenge',
          displayField: 'nummer',
          valueField: 'id',
          helpText: 'Verknüpfung mit Wareneingang (optional)'
        },
        {
          name: 'rechnungsNummer',
          label: 'Rechnungsnummer',
          type: 'text',
          required: true
        },
        {
          name: 'rechnungsDatum',
          label: 'Rechnungsdatum',
          type: 'date',
          required: true
        },
        {
          name: 'status',
          label: 'Status',
          type: 'select',
          required: true,
          options: [
            { value: 'ERFASST', label: 'Erfasst' },
            { value: 'GEPRUEFT', label: 'Geprüft' },
            { value: 'FREIGEGEBEN', label: 'Freigegeben' },
            { value: 'VERBUCHT', label: 'Verbucht' },
            { value: 'BEZAHLT', label: 'Bezahlt' }
          ]
        }
      ]
    },
    {
      key: 'betrag',
      label: 'Beträge',
      fields: [
        {
          name: 'bruttoBetrag',
          label: 'Bruttobetrag (€)',
          type: 'number',
          required: true
        },
        {
          name: 'nettoBetrag',
          label: 'Nettobetrag (€)',
          type: 'number'
        },
        {
          name: 'steuerBetrag',
          label: 'Steuerbetrag (€)',
          type: 'number'
        },
        {
          name: 'steuerSatz',
          label: 'Steuersatz (%)',
          type: 'number'
        }
      ]
    },
    {
      key: 'zahlung',
      label: 'Zahlungskonditionen',
      fields: [
        {
          name: 'skonto.prozent',
          label: 'Skonto (%)',
          type: 'number'
        },
        {
          name: 'skonto.betrag',
          label: 'Skonto-Betrag (€)',
          type: 'number'
        },
        {
          name: 'skonto.frist',
          label: 'Skonto-Frist',
          type: 'text',
          placeholder: 'z.B. 14 Tage'
        },
        {
          name: 'zahlungsziel',
          label: 'Zahlungsziel',
          type: 'text',
          required: true,
          placeholder: 'z.B. 30 Tage netto'
        }
      ]
    },
    {
      key: 'positionen',
      label: 'Positionen',
      fields: [
        {
          name: 'positionen',
          label: 'Rechnungspositionen',
          type: 'table',
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
              key: 'preis',
              label: 'Preis',
              type: 'number',
              required: true
            },
            {
              key: 'steuerSatz',
              label: 'Steuer %',
              type: 'number'
            },
            {
              key: 'gesamt',
              label: 'Gesamt',
              type: 'number'
            }
          ] as any,
          helpText: 'Detaillierte Rechnungspositionen'
        }
      ]
    },
    {
      key: 'abweichungen',
      label: 'Abweichungen',
      fields: [
        {
          name: 'abweichungen',
          label: 'Abweichungen',
          type: 'table',
          columns: [
            {
              key: 'typ',
              label: 'Typ',
              type: 'select',
              required: true,
              options: [
                { value: 'MENGE', label: 'Menge' },
                { value: 'PREIS', label: 'Preis' },
                { value: 'QUALITAET', label: 'Qualität' }
              ]
            },
            {
              key: 'beschreibung',
              label: 'Beschreibung',
              type: 'text',
              required: true
            },
            {
              key: 'betrag',
              label: 'Betrag (€)',
              type: 'number'
            }
          ] as any,
          helpText: 'Abweichungen zur Bestellung/Wareneingang'
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
          placeholder: 'Zusätzliche Informationen zur Rechnung...'
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
      key: 'freigeben',
      label: 'Freigeben',
      type: 'primary',
      onClick: () => console.log('Freigeben clicked')
    },
    {
      key: 'verbuchen',
      label: 'Verbuchen',
      type: 'primary',
      onClick: () => console.log('Verbuchen clicked')
    }
  ],
  api: {
    baseUrl: '/api/einkauf/rechnungseingaenge',
    endpoints: {
      list: '/api/einkauf/rechnungseingaenge',
      get: '/api/einkauf/rechnungseingaenge/{id}',
      create: '/api/einkauf/rechnungseingaenge',
      update: '/api/einkauf/rechnungseingaenge/{id}',
      delete: '/api/einkauf/rechnungseingaenge/{id}'
    }
  },
  validation: rechnungseingangSchema,
  permissions: ['einkauf.read', 'einkauf.write', 'finance.read']
}

export default function RechnungseingangPage(): JSX.Element {
  const navigate = useNavigate()
  const { id } = useParams<{ id: string }>()
  const [loading, setLoading] = useState(false)

  const { data, saveData } = useMaskData({
    apiUrl: rechnungseingangConfig.api.baseUrl,
    id: id || undefined
  })

  const handleSave = async (formData: any) => {
    setLoading(true)
    try {
      await saveData(formData)
      navigate('/einkauf/rechnungseingaenge')
    } catch (error) {
      console.error('Fehler beim Speichern:', error)
    } finally {
      setLoading(false)
    }
  }

  const handleCancel = () => {
    if (confirm('Änderungen wirklich verwerfen?')) {
      navigate('/einkauf/rechnungseingaenge')
    }
  }

  return (
    <ObjectPage
      config={rechnungseingangConfig}
      data={data}
      onSave={handleSave}
      onCancel={handleCancel}
      isLoading={loading}
    />
  )
}