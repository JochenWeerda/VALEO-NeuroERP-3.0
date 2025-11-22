import { useState } from 'react'
import { useNavigate, useParams } from 'react-router-dom'
import { useTranslation } from 'react-i18next'
import { ObjectPage } from '@/components/mask-builder'
import { useMaskData } from '@/components/mask-builder/hooks'
import { MaskConfig } from '@/components/mask-builder/types'
import { z } from 'zod'
import { getEntityTypeLabel } from '@/features/crud/utils/i18n-helpers'

// Zod-Schema für Auftragsbestätigung (wird in Komponente mit i18n erstellt)
const createAuftragsbestaetigungSchema = (t: any) => z.object({
  bestellungId: z.string().min(1, t('crud.messages.validationError')),
  bestaetigungsNummer: z.string().min(1, t('crud.messages.validationError')),
  status: z.enum(['OFFEN', 'GEPRUEFT', 'BESTAETIGT']),
  bestaetigteTermine: z.array(z.object({
    positionId: z.string(),
    bestaetigterTermin: z.string().min(1, t('crud.messages.validationError')),
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

// Konfiguration für Auftragsbestätigung ObjectPage (wird in Komponente mit i18n erstellt)
const createAuftragsbestaetigungConfig = (t: any, entityTypeLabel: string): MaskConfig => ({
  title: entityTypeLabel,
  subtitle: t('crud.tooltips.fields.orderConfirmation'),
  type: 'object-page',
  tabs: [
    {
      key: 'stammdaten',
      label: t('crud.detail.basicInfo'),
      fields: [
        {
          name: 'bestellungId',
          label: t('crud.entities.purchaseOrder'),
          type: 'lookup',
          required: true,
          endpoint: '/api/einkauf/bestellungen?status=FREIGEGEBEN',
          displayField: 'nummer',
          valueField: 'id'
        },
        {
          name: 'bestaetigungsNummer',
          label: t('crud.fields.confirmationNumber'),
          type: 'text',
          required: true
        },
        {
          name: 'status',
          label: t('crud.fields.status'),
          type: 'select',
          required: true,
          options: [
            { value: 'OFFEN', label: t('status.pending') },
            { value: 'GEPRUEFT', label: t('status.reviewed') },
            { value: 'BESTAETIGT', label: t('status.confirmed') }
          ]
        }
      ]
    },
    {
      key: 'termine',
      label: t('crud.fields.dateConfirmations'),
      fields: [
        {
          name: 'bestaetigteTermine',
          label: t('crud.fields.dateDeviations'),
          type: 'table',
          columns: [
            {
              key: 'positionId',
              label: t('crud.fields.item'),
              type: 'text',
              required: true
            },
            {
              key: 'bestaetigterTermin',
              label: t('crud.fields.confirmedDate'),
              type: 'date',
              required: true
            },
            {
              key: 'abweichung',
              label: t('crud.fields.deviation'),
              type: 'text'
            }
          ] as any,
          helpText: t('crud.tooltips.fields.dateDeviations')
        }
      ]
    },
    {
      key: 'preise',
      label: t('crud.fields.priceDeviations'),
      fields: [
        {
          name: 'preisabweichungen',
          label: t('crud.fields.priceChanges'),
          type: 'table',
          columns: [
            {
              key: 'positionId',
              label: t('crud.fields.item'),
              type: 'text',
              required: true
            },
            {
              key: 'urspruenglicherPreis',
              label: t('crud.fields.originalPrice'),
              type: 'number',
              required: true
            },
            {
              key: 'neuerPreis',
              label: t('crud.fields.newPrice'),
              type: 'number',
              required: true
            },
            {
              key: 'begruendung',
              label: t('crud.fields.reason'),
              type: 'text'
            }
          ] as any,
          helpText: t('crud.tooltips.fields.priceDeviations')
        }
      ]
    },
    {
      key: 'belege',
      label: t('crud.detail.additionalInfo'),
      fields: [
        {
          name: 'bemerkungen',
          label: t('crud.fields.notes'),
          type: 'textarea',
          placeholder: t('crud.tooltips.placeholders.confirmationNotes')
        }
      ]
    }
  ],
  actions: [
    {
      key: 'pruefen',
      label: t('crud.actions.review'),
      type: 'secondary',
      onClick: () => console.log('Prüfen clicked')
    },
    {
      key: 'bestaetigen',
      label: t('crud.actions.confirm'),
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
  validation: createAuftragsbestaetigungSchema(t),
  permissions: ['einkauf.read', 'einkauf.write']
})

export default function AuftragsbestaetigungPage(): JSX.Element {
  const { t } = useTranslation()
  const navigate = useNavigate()
  const { id } = useParams<{ id: string }>()
  const [loading, setLoading] = useState(false)
  const entityType = 'orderConfirmation'
  const entityTypeLabel = getEntityTypeLabel(t, entityType, 'Auftragsbestätigung')
  const auftragsbestaetigungConfig = createAuftragsbestaetigungConfig(t, entityTypeLabel)

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
      console.error(t('crud.messages.updateError', { entityType: entityTypeLabel }), error)
    } finally {
      setLoading(false)
    }
  }

  const handleCancel = () => {
    if (confirm(t('crud.messages.discardChanges'))) {
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