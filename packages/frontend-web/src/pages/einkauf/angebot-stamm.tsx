import { useState } from 'react'
import { useNavigate, useParams } from 'react-router-dom'
import { useTranslation } from 'react-i18next'
import { ObjectPage } from '@/components/mask-builder'
import { useMaskData } from '@/components/mask-builder/hooks'
import { MaskConfig } from '@/components/mask-builder/types'
import { z } from 'zod'
import { getEntityTypeLabel } from '@/features/crud/utils/i18n-helpers'

// Zod-Schema für Angebot (wird in Komponente mit i18n erstellt)
const createAngebotSchema = (t: any) => z.object({
  angebotNummer: z.string().min(1, t('crud.messages.validationError')),
  anfrageId: z.string().optional(),
  lieferantId: z.string().min(1, t('crud.messages.validationError')),
  artikel: z.string().min(1, t('crud.messages.validationError')),
  menge: z.number().min(0.1, t('crud.messages.validationError')),
  einheit: z.string().min(1, t('crud.messages.validationError')),
  preis: z.number().min(0, t('crud.messages.validationError')),
  waehrung: z.string().default('EUR'),
  lieferzeit: z.number().min(1, t('crud.messages.validationError')),
  gueltigBis: z.string().min(1, t('crud.messages.validationError')),
  status: z.enum(['ERFASST', 'GEPRUEFT', 'GENEHMIGT', 'ABGELEHNT']),
  mindestabnahme: z.number().optional(),
  zahlungsbedingungen: z.string().optional(),
  incoterms: z.string().optional(),
  bemerkungen: z.string().optional()
})

// Konfiguration für Angebot ObjectPage (wird in Komponente mit i18n erstellt)
const createAngebotConfig = (t: any, entityTypeLabel: string): MaskConfig => ({
  title: entityTypeLabel,
  subtitle: t('crud.actions.edit'),
  type: 'object-page',
  tabs: [
    {
      key: 'stammdaten',
      label: t('crud.detail.basicInfo'),
      fields: [
        {
          name: 'angebotNummer',
          label: t('crud.fields.number'),
          type: 'text',
          required: true,
          readonly: true
        },
        {
          name: 'anfrageId',
          label: t('crud.entities.purchaseRequest'),
          type: 'lookup',
          endpoint: '/api/einkauf/anfragen?status=FREIGEGEBEN',
          displayField: 'anfrageNummer',
          valueField: 'id',
          helpText: t('crud.tooltips.fields.linkedRequest')
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
            { value: 'ERFASST', label: t('status.recorded') },
            { value: 'GEPRUEFT', label: t('status.reviewed') },
            { value: 'GENEHMIGT', label: t('status.approved') },
            { value: 'ABGELEHNT', label: t('status.rejected') }
          ]
        }
      ]
    },
    {
      key: 'angebot',
      label: t('crud.detail.offerDetails'),
      fields: [
        {
          name: 'artikel',
          label: t('crud.fields.product'),
          type: 'lookup',
          required: true,
          endpoint: '/api/articles',
          displayField: 'name',
          valueField: 'id'
        },
        {
          name: 'menge',
          label: t('crud.fields.quantity'),
          type: 'number',
          required: true
        },
        {
          name: 'einheit',
          label: t('crud.fields.unit'),
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
          label: t('crud.fields.price'),
          type: 'number',
          required: true
        },
        {
          name: 'waehrung',
          label: t('crud.fields.currency'),
          type: 'select',
          options: [
            { value: 'EUR', label: 'EUR' },
            { value: 'USD', label: 'USD' },
            { value: 'GBP', label: 'GBP' }
          ]
        },
        {
          name: 'lieferzeit',
          label: t('crud.fields.deliveryTime'),
          type: 'number',
          required: true
        },
        {
          name: 'gueltigBis',
          label: t('crud.fields.validUntil'),
          type: 'date',
          required: true
        }
      ]
    },
    {
      key: 'konditionen',
      label: t('crud.fields.conditions'),
      fields: [
        {
          name: 'mindestabnahme',
          label: t('crud.fields.minimumOrder'),
          type: 'number',
          helpText: t('crud.tooltips.fields.minimumOrder')
        },
        {
          name: 'zahlungsbedingungen',
          label: t('crud.fields.paymentTerms'),
          type: 'text',
          placeholder: t('crud.tooltips.placeholders.paymentTerms')
        },
        {
          name: 'incoterms',
          label: t('crud.fields.incoterms'),
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
          label: t('crud.fields.notes'),
          type: 'textarea',
          placeholder: t('crud.tooltips.placeholders.offerNotes')
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
      key: 'genehmigen',
      label: t('crud.actions.approve'),
      type: 'primary',
      onClick: () => console.log('Genehmigen clicked')
    },
    {
      key: 'ablehnen',
      label: t('crud.actions.reject'),
      type: 'danger',
      onClick: () => console.log('Ablehnen clicked')
    },
    {
      key: 'inBestellung',
      label: t('crud.actions.convertToOrder'),
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
  validation: createAngebotSchema(t),
  permissions: ['einkauf.read', 'einkauf.write']
})

export default function AngebotStammPage(): JSX.Element {
  const { t } = useTranslation()
  const navigate = useNavigate()
  const { id } = useParams<{ id: string }>()
  const [loading, setLoading] = useState(false)
  const entityType = 'purchaseOffer'
  const entityTypeLabel = getEntityTypeLabel(t, entityType, 'Angebot')
  const angebotConfig = createAngebotConfig(t, entityTypeLabel)

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
      console.error(t('crud.messages.updateError', { entityType: entityTypeLabel }), error)
    } finally {
      setLoading(false)
    }
  }

  const handleCancel = () => {
    if (confirm(t('crud.messages.discardChanges'))) {
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