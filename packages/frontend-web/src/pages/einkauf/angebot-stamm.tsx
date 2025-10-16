import { useState } from 'react'
import { useNavigate, useParams } from 'react-router-dom'
import { ObjectPage } from '@/components/mask-builder'
import { useMaskData } from '@/components/mask-builder/hooks'
import { MaskConfig } from '@/components/mask-builder/types'
import { z } from 'zod'

// Zod-Schema für Angebot
const angebotSchema = z.object({
  angebotNummer: z.string().min(1, "Angebot-Nummer ist erforderlich"),
  anfrageId: z.string().optional(),
  lieferantId: z.string().min(1, "Lieferant ist erforderlich"),
  artikel: z.string().min(1, "Artikel ist erforderlich"),
  menge: z.number().min(0.1, "Menge muss > 0 sein"),
  einheit: z.string().min(1, "Einheit ist erforderlich"),
  preis: z.number().min(0, "Preis muss >= 0 sein"),
  waehrung: z.string().default('EUR'),
  lieferzeit: z.number().min(1, "Lieferzeit muss >= 1 Tag sein"),
  gueltigBis: z.string().min(1, "Gültigkeitsdatum ist erforderlich"),
  status: z.enum(['ERFASST', 'GEPRUEFT', 'GENEHMIGT', 'ABGELEHNT']),
  mindestabnahme: z.number().optional(),
  zahlungsbedingungen: z.string().optional(),
  incoterms: z.string().optional(),
  bemerkungen: z.string().optional()
})

// Konfiguration für Angebot ObjectPage
const angebotConfig: MaskConfig = {
  title: 'Lieferantenangebot',
  subtitle: 'Preisangebot von Lieferanten verwalten',
  type: 'object-page',
  tabs: [
    {
      key: 'stammdaten',
      label: 'Stammdaten',
      fields: [
        {
          name: 'angebotNummer',
          label: 'Angebot-Nummer',
          type: 'text',
          required: true,
          readonly: true
        },
        {
          name: 'anfrageId',
          label: 'Anfrage',
          type: 'lookup',
          endpoint: '/api/einkauf/anfragen?status=FREIGEGEBEN',
          displayField: 'anfrageNummer',
          valueField: 'id',
          helpText: 'Verknüpfung mit bestehender Anfrage (optional)'
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
            { value: 'ERFASST', label: 'Erfasst' },
            { value: 'GEPRUEFT', label: 'Geprüft' },
            { value: 'GENEHMIGT', label: 'Genehmigt' },
            { value: 'ABGELEHNT', label: 'Abgelehnt' }
          ]
        }
      ]
    },
    {
      key: 'angebot',
      label: 'Angebotsdetails',
      fields: [
        {
          name: 'artikel',
          label: 'Artikel',
          type: 'lookup',
          required: true,
          endpoint: '/api/articles',
          displayField: 'name',
          valueField: 'id'
        },
        {
          name: 'menge',
          label: 'Menge',
          type: 'number',
          required: true
        },
        {
          name: 'einheit',
          label: 'Einheit',
          type: 'select',
          required: true,
          options: [
            { value: 'kg', label: 'kg' },
            { value: 't', label: 't' },
            { value: 'l', label: 'l' },
            { value: 'Stk', label: 'Stk' }
          ]
        },
        {
          name: 'preis',
          label: 'Preis',
          type: 'number',
          required: true
        },
        {
          name: 'waehrung',
          label: 'Währung',
          type: 'select',
          options: [
            { value: 'EUR', label: 'EUR' },
            { value: 'USD', label: 'USD' },
            { value: 'GBP', label: 'GBP' }
          ]
        },
        {
          name: 'lieferzeit',
          label: 'Lieferzeit (Tage)',
          type: 'number',
          required: true
        },
        {
          name: 'gueltigBis',
          label: 'Gültig bis',
          type: 'date',
          required: true
        }
      ]
    },
    {
      key: 'konditionen',
      label: 'Konditionen',
      fields: [
        {
          name: 'mindestabnahme',
          label: 'Mindestabnahme',
          type: 'number',
          helpText: 'Mindestmenge für Rabatte'
        },
        {
          name: 'zahlungsbedingungen',
          label: 'Zahlungsbedingungen',
          type: 'text',
          placeholder: 'z.B. 30 Tage netto'
        },
        {
          name: 'incoterms',
          label: 'Incoterms',
          type: 'select',
          options: [
            { value: 'EXW', label: 'EXW - Ab Werk' },
            { value: 'FCA', label: 'FCA - Frei Frachtführer' },
            { value: 'CPT', label: 'CPT - Frachtfrei bezahlt bis' },
            { value: 'CIP', label: 'CIP - Frachtfrei versichert bis' },
            { value: 'DAT', label: 'DAT - Geliefert Terminal' },
            { value: 'DAP', label: 'DAP - Geliefert benannter Ort' },
            { value: 'DDP', label: 'DDP - Geliefert verzollt' }
          ]
        },
        {
          name: 'bemerkungen',
          label: 'Bemerkungen',
          type: 'textarea',
          placeholder: 'Zusätzliche Informationen zum Angebot...'
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
      key: 'genehmigen',
      label: 'Genehmigen',
      type: 'primary',
      onClick: () => console.log('Genehmigen clicked')
    },
    {
      key: 'ablehnen',
      label: 'Ablehnen',
      type: 'danger',
      onClick: () => console.log('Ablehnen clicked')
    },
    {
      key: 'inBestellung',
      label: 'In Bestellung umwandeln',
      type: 'secondary',
      onClick: () => console.log('In Bestellung clicked')
    }
  ],
  api: {
    baseUrl: '/api/einkauf/angebote',
    endpoints: {
      list: '/api/einkauf/angebote',
      get: '/api/einkauf/angebote/{id}',
      create: '/api/einkauf/angebote',
      update: '/api/einkauf/angebote/{id}',
      delete: '/api/einkauf/angebote/{id}'
    }
  },
  validation: angebotSchema,
  permissions: ['einkauf.read', 'einkauf.write']
}

export default function AngebotStammPage(): JSX.Element {
  const navigate = useNavigate()
  const { id } = useParams<{ id: string }>()
  const [loading, setLoading] = useState(false)

  const { data, saveData } = useMaskData({
    apiUrl: angebotConfig.api.baseUrl,
    id: id || undefined
  })

  const handleSave = async (formData: any) => {
    setLoading(true)
    try {
      await saveData(formData)
      navigate('/einkauf/angebote')
    } catch (error) {
      console.error('Fehler beim Speichern:', error)
    } finally {
      setLoading(false)
    }
  }

  const handleCancel = () => {
    if (confirm('Änderungen wirklich verwerfen?')) {
      navigate('/einkauf/angebote')
    }
  }

  return (
    <ObjectPage
      config={angebotConfig}
      data={data}
      onSave={handleSave}
      onCancel={handleCancel}
      isLoading={loading}
    />
  )
}