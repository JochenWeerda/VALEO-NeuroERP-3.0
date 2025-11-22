import { useState } from 'react'
import { useNavigate, useParams } from 'react-router-dom'
import { useTranslation } from 'react-i18next'
import { ObjectPage } from '@/components/mask-builder'
import { useMaskData } from '@/components/mask-builder/hooks'
import { MaskConfig } from '@/components/mask-builder/types'
import { z } from 'zod'
import { getEntityTypeLabel } from '@/features/crud/utils/i18n-helpers'

// Zod-Schema für Rechnungseingang (wird in Komponente mit i18n erstellt)
const createRechnungseingangSchema = (t: any) => z.object({
  lieferantId: z.string().min(1, t('crud.messages.validationError')),
  bestellungId: z.string().optional(),
  wareneingangId: z.string().optional(),
  rechnungsNummer: z.string().min(1, t('crud.messages.validationError')),
  rechnungsDatum: z.string().min(1, t('crud.messages.validationError')),
  status: z.enum(['ERFASST', 'GEPRUEFT', 'FREIGEGEBEN', 'VERBUCHT', 'BEZAHLT']),
  bruttoBetrag: z.number().min(0.01, t('crud.messages.validationError')),
  nettoBetrag: z.number().min(0),
  steuerBetrag: z.number().min(0),
  steuerSatz: z.number().min(0),
  skonto: z.object({
    prozent: z.number().min(0),
    betrag: z.number().min(0),
    frist: z.string().optional()
  }),
  zahlungsziel: z.string().min(1, t('crud.messages.validationError')),
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

// Konfiguration für Rechnungseingang ObjectPage (wird in Komponente mit i18n erstellt)
const createRechnungseingangConfig = (t: any, entityTypeLabel: string): MaskConfig => ({
  title: entityTypeLabel,
  subtitle: t('crud.actions.process'),
  type: 'object-page',
  tabs: [
    {
      key: 'stammdaten',
      label: t('crud.detail.basicInfo'),
      fields: [
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
          name: 'bestellungId',
          label: t('crud.entities.purchaseOrder'),
          type: 'lookup',
          endpoint: '/api/einkauf/bestellungen',
          displayField: 'nummer',
          valueField: 'id',
          helpText: t('crud.tooltips.fields.linkedOrder')
        },
        {
          name: 'wareneingangId',
          label: t('crud.fields.goodsReceipt'),
          type: 'lookup',
          endpoint: '/api/lager/wareneingaenge',
          displayField: 'nummer',
          valueField: 'id',
          helpText: t('crud.tooltips.fields.linkedGoodsReceipt')
        },
        {
          name: 'rechnungsNummer',
          label: t('crud.fields.invoiceNumber'),
          type: 'text',
          required: true
        },
        {
          name: 'rechnungsDatum',
          label: t('crud.fields.invoiceDate'),
          type: 'date',
          required: true
        },
        {
          name: 'status',
          label: t('crud.fields.status'),
          type: 'select',
          required: true,
          options: [
            { value: 'ERFASST', label: t('status.recorded') },
            { value: 'GEPRUEFT', label: t('status.reviewed') },
            { value: 'FREIGEGEBEN', label: t('status.approved') },
            { value: 'VERBUCHT', label: t('status.posted') },
            { value: 'BEZAHLT', label: t('status.paid') }
          ]
        }
      ]
    },
    {
      key: 'betrag',
      label: t('crud.fields.amounts'),
      fields: [
        {
          name: 'bruttoBetrag',
          label: t('crud.fields.grossAmount') + ' (€)',
          type: 'number',
          required: true
        },
        {
          name: 'nettoBetrag',
          label: t('crud.fields.netAmount') + ' (€)',
          type: 'number'
        },
        {
          name: 'steuerBetrag',
          label: t('crud.fields.taxAmount') + ' (€)',
          type: 'number'
        },
        {
          name: 'steuerSatz',
          label: t('crud.fields.taxRate') + ' (%)',
          type: 'number'
        }
      ]
    },
    {
      key: 'zahlung',
      label: t('crud.fields.paymentTerms'),
      fields: [
        {
          name: 'skonto.prozent',
          label: t('crud.fields.discount') + ' (%)',
          type: 'number'
        },
        {
          name: 'skonto.betrag',
          label: t('crud.fields.discountAmount') + ' (€)',
          type: 'number'
        },
        {
          name: 'skonto.frist',
          label: t('crud.fields.discountPeriod'),
          type: 'text',
          placeholder: t('crud.tooltips.placeholders.discountPeriod')
        },
        {
          name: 'zahlungsziel',
          label: t('crud.fields.paymentDue'),
          type: 'text',
          required: true,
          placeholder: t('crud.tooltips.placeholders.paymentTerms')
        }
      ]
    },
    {
      key: 'positionen',
      label: t('crud.fields.items'),
      fields: [
        {
          name: 'positionen',
          label: t('crud.fields.invoiceItems'),
          type: 'table',
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
              key: 'preis',
              label: t('crud.fields.price'),
              type: 'number',
              required: true
            },
            {
              key: 'steuerSatz',
              label: t('crud.fields.taxRate') + ' %',
              type: 'number'
            },
            {
              key: 'gesamt',
              label: t('crud.fields.total'),
              type: 'number'
            }
          ] as any,
          helpText: t('crud.tooltips.fields.invoiceItems')
        }
      ]
    },
    {
      key: 'abweichungen',
      label: t('crud.fields.deviations'),
      fields: [
        {
          name: 'abweichungen',
          label: t('crud.fields.deviations'),
          type: 'table',
          columns: [
            {
              key: 'typ',
              label: t('crud.fields.type'),
              type: 'select',
              required: true,
              options: [
                { value: 'MENGE', label: t('crud.fields.quantity') },
                { value: 'PREIS', label: t('crud.fields.price') },
                { value: 'QUALITAET', label: t('crud.fields.quality') }
              ]
            },
            {
              key: 'beschreibung',
              label: t('crud.fields.description'),
              type: 'text',
              required: true
            },
            {
              key: 'betrag',
              label: t('crud.fields.total') + ' (€)',
              type: 'number'
            }
          ] as any,
          helpText: t('crud.tooltips.fields.deviations')
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
          placeholder: t('crud.tooltips.placeholders.invoiceNotes')
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
      key: 'freigeben',
      label: t('crud.actions.approve'),
      type: 'primary',
      onClick: () => console.log('Freigeben clicked')
    },
    {
      key: 'verbuchen',
      label: t('crud.actions.post'),
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
  validation: createRechnungseingangSchema(t),
  permissions: ['einkauf.read', 'einkauf.write', 'finance.read']
})

export default function RechnungseingangPage(): JSX.Element {
  const { t } = useTranslation()
  const navigate = useNavigate()
  const { id } = useParams<{ id: string }>()
  const [loading, setLoading] = useState(false)
  const entityType = 'invoiceReceipt'
  const entityTypeLabel = getEntityTypeLabel(t, entityType, 'Rechnungseingang')
  const rechnungseingangConfig = createRechnungseingangConfig(t, entityTypeLabel)

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
      console.error(t('crud.messages.updateError', { entityType: entityTypeLabel }), error)
    } finally {
      setLoading(false)
    }
  }

  const handleCancel = () => {
    if (confirm(t('crud.messages.discardChanges'))) {
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