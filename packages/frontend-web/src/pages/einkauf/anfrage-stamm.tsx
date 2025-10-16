import { useState } from 'react'
import { useNavigate, useParams } from 'react-router-dom'
import { ObjectPage } from '@/components/mask-builder'
import { useMaskData } from '@/components/mask-builder/hooks'
import { MaskConfig } from '@/components/mask-builder/types'
import { z } from 'zod'

// Zod-Schema für Anfrage
const anfrageSchema = z.object({
  anfrageNummer: z.string().min(1, "Anfrage-Nummer ist erforderlich"),
  typ: z.enum(['BANF', 'ANF']),
  anforderer: z.string().min(1, "Anforderer ist erforderlich"),
  artikel: z.string().min(1, "Artikel ist erforderlich"),
  menge: z.number().min(0.1, "Menge muss > 0 sein"),
  einheit: z.string().min(1, "Einheit ist erforderlich"),
  prioritaet: z.enum(['niedrig', 'normal', 'hoch', 'dringend']),
  faelligkeit: z.string().min(1, "Fälligkeit ist erforderlich"),
  status: z.enum(['ENTWURF', 'FREIGEGEBEN', 'ANGEBOTSPHASE']),
  begruendung: z.string().min(1, "Begründung ist erforderlich"),
  kostenstelle: z.string().optional(),
  projekt: z.string().optional(),
  bemerkungen: z.string().optional()
})

// Konfiguration für Anfrage ObjectPage
const anfrageConfig: MaskConfig = {
  title: 'Bedarfsanforderung',
  subtitle: 'Interne Bedarfsmeldung oder Anfrage erstellen',
  type: 'object-page',
  tabs: [
    {
      key: 'stammdaten',
      label: 'Stammdaten',
      fields: [
        {
          name: 'anfrageNummer',
          label: 'Anfrage-Nummer',
          type: 'text',
          required: true,
          readonly: true
        },
        {
          name: 'typ',
          label: 'Typ',
          type: 'select',
          required: true,
          options: [
            { value: 'BANF', label: 'Bedarfsanforderung (BANF)' },
            { value: 'ANF', label: 'Anfrage (ANF)' }
          ]
        },
        {
          name: 'anforderer',
          label: 'Anforderer',
          type: 'text',
          required: true
        },
        {
          name: 'status',
          label: 'Status',
          type: 'select',
          required: true,
          options: [
            { value: 'ENTWURF', label: 'Entwurf' },
            { value: 'FREIGEGEBEN', label: 'Freigegeben' },
            { value: 'ANGEBOTSPHASE', label: 'Angebotsphase' }
          ]
        }
      ]
    },
    {
      key: 'bedarf',
      label: 'Bedarf',
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
          name: 'prioritaet',
          label: 'Priorität',
          type: 'select',
          required: true,
          options: [
            { value: 'niedrig', label: 'Niedrig' },
            { value: 'normal', label: 'Normal' },
            { value: 'hoch', label: 'Hoch' },
            { value: 'dringend', label: 'Dringend' }
          ]
        },
        {
          name: 'faelligkeit',
          label: 'Fällig bis',
          type: 'date',
          required: true
        }
      ]
    },
    {
      key: 'details',
      label: 'Details',
      fields: [
        {
          name: 'begruendung',
          label: 'Begründung',
          type: 'textarea',
          required: true,
          placeholder: 'Warum wird dieser Bedarf angemeldet?'
        },
        {
          name: 'kostenstelle',
          label: 'Kostenstelle',
          type: 'lookup',
          endpoint: '/api/cost-centers',
          displayField: 'name',
          valueField: 'id'
        },
        {
          name: 'projekt',
          label: 'Projekt',
          type: 'lookup',
          endpoint: '/api/projects',
          displayField: 'name',
          valueField: 'id'
        },
        {
          name: 'bemerkungen',
          label: 'Bemerkungen',
          type: 'textarea',
          placeholder: 'Zusätzliche Informationen...'
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
      key: 'inBestellung',
      label: 'In Bestellung umwandeln',
      type: 'secondary',
      onClick: () => console.log('In Bestellung clicked')
    }
  ],
  api: {
    baseUrl: '/api/einkauf/anfragen',
    endpoints: {
      list: '/api/einkauf/anfragen',
      get: '/api/einkauf/anfragen/{id}',
      create: '/api/einkauf/anfragen',
      update: '/api/einkauf/anfragen/{id}',
      delete: '/api/einkauf/anfragen/{id}'
    }
  },
  validation: anfrageSchema,
  permissions: ['einkauf.read', 'einkauf.write']
}

export default function AnfrageStammPage(): JSX.Element {
  const navigate = useNavigate()
  const { id } = useParams<{ id: string }>()
  const [loading, setLoading] = useState(false)

  const { data, saveData } = useMaskData({
    apiUrl: anfrageConfig.api.baseUrl,
    id: id || undefined
  })

  const handleSave = async (formData: any) => {
    setLoading(true)
    try {
      await saveData(formData)
      navigate('/einkauf/anfragen')
    } catch (error) {
      console.error('Fehler beim Speichern:', error)
    } finally {
      setLoading(false)
    }
  }

  const handleCancel = () => {
    if (confirm('Änderungen wirklich verwerfen?')) {
      navigate('/einkauf/anfragen')
    }
  }

  return (
    <ObjectPage
      config={anfrageConfig}
      data={data}
      onSave={handleSave}
      onCancel={handleCancel}
      isLoading={loading}
    />
  )
}