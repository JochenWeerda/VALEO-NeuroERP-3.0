import { useMemo, useState } from 'react'
import { useNavigate, useParams } from 'react-router-dom'
import { useTranslation } from 'react-i18next'
import { ObjectPage } from '@/components/mask-builder'
import { useMaskData } from '@/components/mask-builder/hooks'
import { MaskConfig } from '@/components/mask-builder/types'
import { getEntityTypeLabel } from '@/features/crud/utils/i18n-helpers'
import { toast } from '@/hooks/use-toast'
import {
  useRechnungseingangPruefen,
  useRechnungseingangFreigeben,
  useRechnungseingangVerbuchen,
} from '@/lib/api/einkauf'

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
          endpoint: '/api/v1/crm/business-partners?type=supplier',
          displayField: 'name',
          valueField: 'id'
        },
        {
          name: 'bestellungId',
          label: t('crud.entities.purchaseOrder'),
          type: 'lookup',
          endpoint: '/api/mcp/documents/purchase_order',
          displayField: 'number',
          valueField: 'id',
          helpText: t('crud.tooltips.fields.linkedOrder'),
          onChange: async (value: string) => {
            // Automatisches Laden von PO-Daten
            if (value) {
              try {
                const response = await fetch(`/api/mcp/documents/purchase_order/${value}`)
                if (response.ok) {
                  const po = await response.json()
                  // Setze Lieferant automatisch
                  if (po.supplierId) {
                    // Trigger update for supplierId field
                  }
                }
              } catch (error) {
                console.error('Fehler beim Laden der Bestellung:', error)
              }
            }
          }
        },
        {
          name: 'wareneingangId',
          label: t('crud.fields.goodsReceipt'),
          type: 'lookup',
          endpoint: '/api/purchase-workflow/goods-receipts',
          displayField: 'number',
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
          label: `${t('crud.fields.grossAmount')  } (€)`,
          type: 'number',
          required: true
        },
        {
          name: 'nettoBetrag',
          label: `${t('crud.fields.netAmount')  } (€)`,
          type: 'number'
        },
        {
          name: 'steuerBetrag',
          label: `${t('crud.fields.taxAmount')  } (€)`,
          type: 'number'
        },
        {
          name: 'steuerSatz',
          label: `${t('crud.fields.taxRate')  } (%)`,
          type: 'number',
          helpText: t('crud.tooltips.fields.taxRate')
        },
        {
          name: 'steuerCode',
          label: t('crud.fields.taxCode'),
          type: 'select',
          options: [
            { value: 'VAT_19', label: '19% MwSt. (VAT_19)' },
            { value: 'VAT_7', label: '7% MwSt. (VAT_7)' },
            { value: 'VAT_0', label: '0% MwSt. (VAT_0)' },
            { value: 'REVERSE_CHARGE', label: t('crud.fields.reverseCharge') },
            { value: 'EXEMPT', label: t('crud.fields.exempt') }
          ],
          helpText: t('crud.tooltips.fields.taxCode')
        },
        {
          name: 'accountCode',
          label: t('crud.fields.accountCode'),
          type: 'lookup',
          endpoint: '/api/v1/chart-of-accounts',
          displayField: 'number',
          valueField: 'id',
          helpText: t('crud.tooltips.fields.accountCode')
        },
        {
          name: 'costCenter',
          label: t('crud.fields.costCenter'),
          type: 'lookup',
          endpoint: '/api/v1/finance/cost-centers',
          displayField: 'name',
          valueField: 'id',
          helpText: t('crud.tooltips.fields.costCenter')
        },
        {
          name: 'project',
          label: t('crud.fields.project'),
          type: 'lookup',
          endpoint: '/api/projects',
          displayField: 'name',
          valueField: 'id',
          helpText: t('crud.tooltips.fields.project')
        }
      ]
    },
    {
      key: 'zahlung',
      label: t('crud.fields.paymentTerms'),
      fields: [
        {
          name: 'skonto.prozent',
          label: `${t('crud.fields.discount')  } (%)`,
          type: 'number'
        },
        {
          name: 'skonto.betrag',
          label: `${t('crud.fields.discountAmount')  } (€)`,
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
              label: `${t('crud.fields.taxRate')  } %`,
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
              label: `${t('crud.fields.total')  } (€)`,
              type: 'number'
            }
          ] as any,
          helpText: t('crud.tooltips.fields.deviations')
        },
        {
          name: 'matchStatus',
          label: t('crud.fields.matchStatus'),
          type: 'select',
          readonly: true,
          options: [
            { value: 'MATCHED', label: t('status.matched') },
            { value: 'PARTIAL', label: t('status.partial') },
            { value: 'UNMATCHED', label: t('status.unmatched') },
            { value: 'EXCEPTION', label: t('crud.fields.exceptions') }
          ],
          helpText: t('crud.tooltips.fields.matchStatus')
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
  actions: [], // set dynamically in component with data + API
  api: {
    baseUrl: '/api/v1/einkauf/rechnungseingaenge',
    endpoints: {
      list: '/api/v1/einkauf/rechnungseingaenge',
      get: '/api/v1/einkauf/rechnungseingaenge/{id}',
      create: '/api/v1/einkauf/rechnungseingaenge',
      update: '/api/v1/einkauf/rechnungseingaenge/{id}',
      delete: '/api/v1/einkauf/rechnungseingaenge/{id}'
    }
  },
  permissions: ['einkauf.read', 'einkauf.write', 'finance.read']
})

const ENTWURF_STATUSES = ['ENTWURF', 'ERFASST', 'OFFEN']

export default function RechnungseingangPage(): JSX.Element {
  const { t } = useTranslation()
  const navigate = useNavigate()
  const { id } = useParams<{ id: string }>()
  const [loading, setLoading] = useState(false)
  const entityType = 'invoiceReceipt'
  const entityTypeLabel = getEntityTypeLabel(t, entityType, 'Rechnungseingang')
  const baseConfig = createRechnungseingangConfig(t, entityTypeLabel)

  const { data, saveData, loadData } = useMaskData({
    apiUrl: baseConfig.api.baseUrl,
    id: id || undefined
  })

  const pruefenMutation = useRechnungseingangPruefen()
  const freigebenMutation = useRechnungseingangFreigeben()
  const verbuchenMutation = useRechnungseingangVerbuchen()

  const status = (data?.status as string) || ''
  const statusUpper = status.toUpperCase()

  const rechnungseingangConfig: MaskConfig = useMemo(() => ({
    ...baseConfig,
    actions: [
      {
        key: 'pruefen',
        label: t('crud.actions.review'),
        type: 'secondary',
        disabled: !data?.id || !ENTWURF_STATUSES.includes(statusUpper),
        onClick: async () => {
          if (!data?.id) return
          try {
            await pruefenMutation.mutateAsync(data.id)
            toast({ title: t('crud.messages.success'), description: t('status.reviewed') })
            await loadData()
          } catch (err: any) {
            toast({
              variant: 'destructive',
              title: t('crud.messages.error'),
              description: err?.response?.data?.detail || err?.message,
            })
          }
        },
      },
      {
        key: 'freigeben',
        label: t('crud.actions.approve'),
        type: 'primary',
        disabled: !data?.id || statusUpper !== 'GEPRUEFT',
        onClick: async () => {
          if (!data?.id) return
          try {
            await freigebenMutation.mutateAsync(data.id)
            toast({ title: t('crud.messages.success'), description: t('status.approved') })
            await loadData()
          } catch (err: any) {
            toast({
              variant: 'destructive',
              title: t('crud.messages.error'),
              description: err?.response?.data?.detail || err?.message,
            })
          }
        },
      },
      {
        key: 'verbuchen',
        label: t('crud.actions.post'),
        type: 'primary',
        disabled: !data?.id || statusUpper !== 'FREIGEGEBEN',
        onClick: async () => {
          if (!data?.id) return
          try {
            await verbuchenMutation.mutateAsync(data.id)
            toast({ title: t('crud.messages.success'), description: t('status.posted') })
            await loadData()
          } catch (err: any) {
            toast({
              variant: 'destructive',
              title: t('crud.messages.error'),
              description: err?.response?.data?.detail || err?.message,
            })
          }
        },
      },
      {
        key: 'abgleich',
        label: t('crud.actions.match'),
        type: 'secondary',
        onClick: () => {
          if (data?.id) navigate(`/einkauf/rechnung-abgleich?invoiceId=${data.id}`)
        },
      },
    ],
  }), [
    baseConfig,
    t,
    data?.id,
    statusUpper,
    loadData,
    pruefenMutation,
    freigebenMutation,
    verbuchenMutation,
    navigate,
  ])

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