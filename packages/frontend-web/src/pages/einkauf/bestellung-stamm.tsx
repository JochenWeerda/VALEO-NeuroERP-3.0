import { useState } from 'react'
import { useNavigate, useParams } from 'react-router-dom'
import { useTranslation } from 'react-i18next'
import { ObjectPage } from '@/components/mask-builder'
import { useMaskData } from '@/components/mask-builder/hooks'
import { MaskConfig } from '@/components/mask-builder/types'
import { z } from 'zod'
import { getEntityTypeLabel } from '@/features/crud/utils/i18n-helpers'

// Zod-Schema für Bestellung (wird in Komponente mit i18n erstellt)
const createBestellungSchema = (t: any) => z.object({
  nummer: z.string().min(1, t('crud.messages.validationError')),
  lieferantId: z.string().min(1, t('crud.messages.validationError')),
  status: z.enum(['ENTWURF', 'FREIGEGEBEN', 'TEILGELIEFERT', 'VOLLGELIEFERT', 'STORNIERT']),
  liefertermin: z.string().min(1, t('crud.messages.validationError')),
  zahlungsbedingungen: z.string().optional(),
  positionen: z.array(z.object({
    artikelId: z.string().min(1, t('crud.messages.validationError')),
    menge: z.number().min(0.1, t('crud.messages.validationError')),
    einheit: z.string().min(1, t('crud.messages.validationError')),
    preis: z.number().min(0, t('crud.messages.validationError')),
    wunschtermin: z.string().optional()
  })).min(1, t('crud.messages.validationError')),
  bemerkungen: z.string().optional()
})

// Konfiguration für Bestellung ObjectPage (wird in Komponente mit i18n erstellt)
const createBestellungConfig = (t: any, entityTypeLabel: string): MaskConfig => ({
  title: entityTypeLabel,
  subtitle: t('crud.actions.edit'),
  type: 'object-page',
  tabs: [
    {
      key: 'stammdaten',
      label: t('crud.detail.basicInfo'),
      fields: [
        {
          name: 'nummer',
          label: t('crud.fields.number'),
          type: 'text',
          required: true,
          readonly: true
        },
        {
          name: 'lieferantId',
          label: t('crud.entities.supplier'),
          type: 'lookup',
          required: true,
          endpoint: '/api/partners?type=supplier',
          displayField: 'name',
          valueField: 'id'
        },
        {
          name: 'status',
          label: t('crud.fields.status'),
          type: 'select',
          required: true,
          options: [
            { value: 'ENTWURF', label: t('status.draft') },
            { value: 'FREIGEGEBEN', label: t('status.approved') },
            { value: 'TEILGELIEFERT', label: t('status.partial') },
            { value: 'VOLLGELIEFERT', label: t('status.completed') },
            { value: 'STORNIERT', label: t('status.cancelled') }
          ]
        },
        {
          name: 'liefertermin',
          label: t('crud.fields.deliveryDate'),
          type: 'date',
          required: true
        },
        {
          name: 'zahlungsbedingungen',
          label: t('crud.fields.paymentTerms'),
          type: 'select',
          options: [
            { value: 'sofort', label: t('crud.fields.paymentTermsImmediate') },
            { value: '14tage', label: t('crud.fields.paymentTermsNet14') },
            { value: '30tage', label: t('crud.fields.paymentTermsNet30') },
            { value: '60tage', label: t('crud.fields.paymentTermsNet60') }
          ]
        }
      ]
    },
    {
      key: 'positionen',
      label: t('crud.fields.items'),
      fields: [
        {
          name: 'positionen',
          label: t('crud.fields.items'),
          type: 'table',
          required: true,
          columns: [
            {
              key: 'artikelId',
              label: t('crud.fields.product'),
              type: 'lookup',
              required: true
            },
            {
              key: 'menge',
              label: t('crud.fields.quantity'),
              type: 'number',
              required: true
            },
            {
              key: 'einheit',
              label: t('crud.fields.unit'),
              type: 'select',
              required: true
            },
            {
              key: 'preis',
              label: t('crud.fields.price'),
              type: 'number'
            },
            {
              key: 'wunschtermin',
              label: t('crud.fields.dueDate'),
              type: 'date'
            }
          ] as any,
          helpText: t('crud.fields.items')
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
          placeholder: t('crud.fields.notes')
        }
      ]
    }
  ],
  actions: [
    {
      key: 'freigeben',
      label: t('crud.actions.approve'),
      type: 'primary',
      onClick: () => console.log('Freigeben clicked')
    },
    {
      key: 'stornieren',
      label: t('crud.actions.cancel'),
      type: 'danger',
      onClick: () => console.log('Stornieren clicked')
    },
    {
      key: 'drucken',
      label: t('crud.actions.print'),
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
  validation: createBestellungSchema(t),
  permissions: ['einkauf.read', 'einkauf.write']
})

export default function BestellungStammPage(): JSX.Element {
  const { t } = useTranslation()
  const navigate = useNavigate()
  const { id } = useParams<{ id: string }>()
  const [loading, setLoading] = useState(false)
  const entityType = 'purchaseOrder'
  const entityTypeLabel = getEntityTypeLabel(t, entityType, 'Bestellung')
  const bestellungConfig = createBestellungConfig(t, entityTypeLabel)

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
      console.error(t('crud.messages.updateError', { entityType: entityTypeLabel }), error)
    } finally {
      setLoading(false)
    }
  }

  const handleCancel = () => {
    if (confirm(t('crud.messages.discardChanges'))) {
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