import { useState } from 'react'
import { useNavigate } from 'react-router-dom'
import { useTranslation } from 'react-i18next'
import { ObjectPage } from '@/components/mask-builder'
import { useMaskData, useMaskValidation, useMaskActions } from '@/components/mask-builder/hooks'
import { MaskConfig } from '@/components/mask-builder/types'
import { z } from 'zod'
import { getEntityTypeLabel } from '@/features/crud/utils/i18n-helpers'
import { toast } from 'sonner'
import { apiClient } from '@/lib/api-client'

// Zod-Schema für OP-Debitoren (wird in Komponente mit i18n erstellt)
const createOpDebitorenSchema = (t: any) => z.object({
  debitorId: z.string().min(1, t('crud.messages.validationError')),
  opNummer: z.string().min(1, t('crud.messages.validationError')),
  rechnungId: z.string().optional(),
  buchungsdatum: z.string().regex(/^\d{4}-\d{2}-\d{2}$/, t('crud.messages.validationError')),
  faelligkeit: z.string().regex(/^\d{4}-\d{2}-\d{2}$/, t('crud.messages.validationError')),
  betrag: z.number().positive(t('crud.messages.validationError')),
  waehrung: z.string().default("EUR"),
  offen: z.number().min(0, t('crud.messages.validationError')),
  skontoBetrag: z.number().min(0).optional(),
  skontoDatum: z.string().optional(),
  zahlungen: z.array(z.object({
    datum: z.string(),
    betrag: z.number(),
    typ: z.enum(['zahlung', 'skonto', 'gutschrift', 'storno']),
    referenz: z.string().optional()
  })).optional(),
  status: z.enum(['offen', 'teilbezahlt', 'ausgeglichen', 'mahnung', 'inkasso']),
  letzteZahlung: z.string().optional(),
  mahnstufe: z.number().min(0).max(3).default(0),
  notizen: z.string().optional()
})

// Konfiguration für OP-Debitoren ObjectPage (wird in Komponente mit i18n erstellt)
const createOpDebitorenConfig = (t: any, entityTypeLabel: string): MaskConfig => ({
  title: entityTypeLabel,
  subtitle: t('crud.fields.opKreditoren.subtitle'),
  type: 'object-page',
  tabs: [
    {
      key: 'grunddaten',
      label: t('crud.detail.basicInfo'),
      fields: [
        {
          name: 'debitorId',
          label: t('crud.entities.debtor'),
          type: 'select',
          required: true,
          options: [
            { value: 'K001', label: 'K001 - Müller GmbH' },
            { value: 'K002', label: 'K002 - Schmidt KG' },
            { value: 'K003', label: 'K003 - Bauer e.K.' }
          ]
        },
        {
          name: 'opNummer',
          label: t('crud.fields.opReference'),
          type: 'text',
          required: true,
          placeholder: t('crud.tooltips.placeholders.opReference')
        },
        {
          name: 'rechnungId',
          label: t('crud.fields.invoiceNumber'),
          type: 'text',
          placeholder: t('crud.tooltips.placeholders.invoiceNumber')
        },
        {
          name: 'buchungsdatum',
          label: t('crud.fields.bookingDate'),
          type: 'date',
          required: true
        },
        {
          name: 'faelligkeit',
          label: t('crud.fields.dueDate'),
          type: 'date',
          required: true
        },
        {
          name: 'status',
          label: t('crud.fields.status'),
          type: 'select',
          required: true,
          options: [
            { value: 'offen', label: t('status.open') },
            { value: 'teilbezahlt', label: t('status.partial') },
            { value: 'ausgeglichen', label: t('status.settled') },
            { value: 'mahnung', label: t('crud.entities.dunning') },
            { value: 'inkasso', label: t('crud.fields.collection') }
          ]
        }
      ],
      layout: 'grid',
      columns: 2
    },
    {
      key: 'betrag',
      label: t('crud.fields.amounts'),
      fields: [
        {
          name: 'betrag',
          label: t('crud.fields.totalAmount'),
          type: 'number',
          required: true,
          step: 0.01,
          placeholder: '0.00'
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
          name: 'offen',
          label: t('crud.fields.openAmount'),
          type: 'number',
          readonly: true,
          step: 0.01
        },
        {
          name: 'skontoBetrag',
          label: t('crud.fields.discountAmount'),
          type: 'number',
          step: 0.01,
          helpText: t('crud.tooltips.fields.discountAvailable')
        },
        {
          name: 'skontoDatum',
          label: t('crud.fields.discountDeadline'),
          type: 'date',
          helpText: t('crud.tooltips.fields.discountDeadline')
        }
      ],
      layout: 'grid',
      columns: 2
    },
    {
      key: 'zahlungen',
      label: t('crud.fields.payments'),
      fields: []
    } as any,
    {
      key: 'zahlungen_custom',
      label: '',
      fields: [],
      customRender: (_data: any, onChange: (_data: any) => void) => (
        <ZahlungenTable
          data={_data.zahlungen || []}
          gesamtBetrag={_data.betrag || 0}
          onChange={(zahlungen) => {
            const totalPaid = zahlungen.reduce((sum: number, z: any) => sum + (z.betrag || 0), 0)
            onChange({
              ..._data,
              zahlungen,
              offen: (_data.betrag || 0) - totalPaid,
              letzteZahlung: zahlungen.length > 0 ? zahlungen[zahlungen.length - 1].datum : _data.letzteZahlung
            })
          }}
          t={t}
        />
      )
    },
    {
      key: 'mahnwesen',
      label: t('crud.entities.dunning'),
      fields: [
        {
          name: 'mahnstufe',
          label: t('crud.fields.dunningLevel'),
          type: 'select',
          options: [
            { value: 0, label: t('crud.fields.noDunning') },
            { value: 1, label: '1. ' + t('crud.entities.dunning') },
            { value: 2, label: '2. ' + t('crud.entities.dunning') },
            { value: 3, label: '3. ' + t('crud.entities.dunning') }
          ]
        },
        {
          name: 'letzteZahlung',
          label: t('crud.fields.lastPayment'),
          type: 'date',
          readonly: true
        }
      ]
    },
    {
      key: 'notizen',
      label: t('crud.fields.notes'),
      fields: [
        {
          name: 'notizen',
          label: t('crud.fields.internalNotes'),
          type: 'textarea',
          placeholder: t('crud.tooltips.placeholders.opNotes')
        }
      ]
    }
  ],
  actions: [
    {
      key: 'zahlung',
      label: t('crud.actions.recordPayment'),
      type: 'secondary',
      onClick: () => {}
    },
    {
      key: 'skonto',
      label: t('crud.actions.useDiscount'),
      type: 'secondary',
      onClick: () => {}
    },
    {
      key: 'ausgleich',
      label: t('crud.actions.settle'),
      type: 'primary',
      onClick: () => {}
    },
    {
      key: 'mahnung',
      label: t('crud.actions.createDunning'),
      type: 'danger',
      onClick: () => {}
    },
    {
      key: 'export',
      label: t('crud.actions.export'),
      type: 'secondary',
      onClick: () => {}
    }
  ],
  api: {
    baseUrl: '/api/v1/finance/open-items',
    endpoints: {
      list: '/api/v1/finance/open-items',
      get: '/api/v1/finance/open-items/{id}',
      create: '/api/v1/finance/open-items',
      update: '/api/v1/finance/open-items/{id}',
      delete: '/api/v1/finance/open-items/{id}'
    }
  } as any,
  validation: createOpDebitorenSchema(t),
  permissions: ['fibu.read', 'fibu.write']
})

// Zahlungen-Tabelle Komponente
function ZahlungenTable({ data: _data, gesamtBetrag, onChange, t }: {
  data: any[],
  gesamtBetrag: number,
  onChange: (_data: any[]) => void,
  t: any
}) {
  const addZahlung = () => {
    onChange([..._data, {
      datum: new Date().toISOString().split('T')[0],
      betrag: 0,
      typ: 'zahlung',
      referenz: ''
    }])
  }

  const updateZahlung = (index: number, field: string, value: any) => {
    const newData = [..._data]
    newData[index] = { ...newData[index], [field]: value }
    onChange(newData)
  }

  const removeZahlung = (index: number) => {
    onChange(_data.filter((_, i) => i !== index))
  }

  const totalPaid = _data.reduce((sum, z) => sum + (z.betrag || 0), 0)
  const remaining = gesamtBetrag - totalPaid

  return (
    <div className="space-y-4">
      <div className="flex justify-between items-center">
        <h3 className="text-lg font-semibold">{t('crud.fields.payments')}</h3>
        <div className="text-sm">
          <span className="font-semibold">{t('crud.fields.openAmount')}: {remaining.toFixed(2)} €</span>
          <button
            onClick={addZahlung}
            className="ml-4 px-4 py-2 bg-blue-600 text-white rounded hover:bg-blue-700"
          >
            + {t('crud.actions.addPayment')}
          </button>
        </div>
      </div>

      <div className="overflow-x-auto">
        <table className="min-w-full border border-gray-300">
          <thead className="bg-gray-50">
            <tr>
              <th className="px-4 py-2 border">{t('crud.fields.date')}</th>
              <th className="px-4 py-2 border">{t('crud.fields.amount')}</th>
              <th className="px-4 py-2 border">{t('crud.fields.type')}</th>
              <th className="px-4 py-2 border">{t('crud.fields.reference')}</th>
              <th className="px-4 py-2 border">{t('crud.actions.actions')}</th>
            </tr>
          </thead>
          <tbody>
            {_data.map((zahlung, index) => (
              <tr key={index} className="border">
                <td className="px-4 py-2 border">
                  <input
                    type="date"
                    value={zahlung.datum}
                    onChange={(e) => updateZahlung(index, 'datum', e.target.value)}
                    className="w-full p-1 border rounded"
                  />
                </td>
                <td className="px-4 py-2 border">
                  <input
                    type="number"
                    step="0.01"
                    value={zahlung.betrag}
                    onChange={(e) => updateZahlung(index, 'betrag', parseFloat(e.target.value) || 0)}
                    className="w-full p-1 border rounded"
                  />
                </td>
                <td className="px-4 py-2 border">
                  <select
                    value={zahlung.typ}
                    onChange={(e) => updateZahlung(index, 'typ', e.target.value)}
                    className="w-full p-1 border rounded"
                  >
                    <option value="zahlung">{t('crud.fields.payment')}</option>
                    <option value="skonto">{t('crud.fields.discount')}</option>
                    <option value="gutschrift">{t('crud.entities.creditNote')}</option>
                    <option value="storno">{t('crud.actions.reverse')}</option>
                  </select>
                </td>
                <td className="px-4 py-2 border">
                  <input
                    type="text"
                    value={zahlung.referenz || ''}
                    onChange={(e) => updateZahlung(index, 'referenz', e.target.value)}
                    className="w-full p-1 border rounded"
                    placeholder={t('crud.tooltips.placeholders.paymentReference')}
                  />
                </td>
                <td className="px-4 py-2 border">
                  <button
                    onClick={() => removeZahlung(index)}
                    className="px-2 py-1 bg-red-600 text-white rounded hover:bg-red-700"
                  >
                    ✕
                  </button>
                </td>
              </tr>
            ))}
          </tbody>
        </table>
      </div>
    </div>
  )
}

export default function OPDebitorenPage(): JSX.Element {
  const { t } = useTranslation()
  const navigate = useNavigate()
  const [isDirty, setIsDirty] = useState(false)
  const entityType = 'openItem'
  const entityTypeLabel = getEntityTypeLabel(t, entityType, 'OP-Verwaltung (Debitoren)')
  const opDebitorenConfig = createOpDebitorenConfig(t, entityTypeLabel)

  const { data, loading, saveData } = useMaskData({
    apiUrl: opDebitorenConfig.api.baseUrl,
    id: 'new'
  })

  const { validate, showValidationToast } = useMaskValidation(opDebitorenConfig.validation)

  const { handleAction } = useMaskActions(async (action: string, formData: any) => {
    if (action === 'zahlung') {
      // Zahlung buchen - fügt automatisch eine neue Zahlung hinzu
      const newZahlung = {
        datum: new Date().toISOString().split('T')[0],
        betrag: formData.offen || 0,
        typ: 'zahlung' as const,
        referenz: `Z-${Date.now()}`
      }

      const updatedZahlungen = [...(formData.zahlungen || []), newZahlung]
      const totalPaid = updatedZahlungen.reduce((sum: number, z: any) => sum + (z.betrag || 0), 0)

      formData.zahlungen = updatedZahlungen
      formData.offen = (formData.betrag || 0) - totalPaid
      formData.letzteZahlung = newZahlung.datum

      toast.success(t('crud.messages.paymentRecorded', { amount: newZahlung.betrag.toFixed(2) }))
    } else if (action === 'skonto') {
      // Skonto nutzen
      if (!formData.skontoBetrag || formData.skontoBetrag <= 0) {
        toast.error(t('crud.messages.noDiscountAvailable'))
        return
      }

      const skontoZahlung = {
        datum: new Date().toISOString().split('T')[0],
        betrag: formData.skontoBetrag,
        typ: 'skonto' as const,
        referenz: `SK-${Date.now()}`
      }

      const updatedZahlungen = [...(formData.zahlungen || []), skontoZahlung]
      const totalPaid = updatedZahlungen.reduce((sum: number, z: any) => sum + (z.betrag || 0), 0)

      formData.zahlungen = updatedZahlungen
      formData.offen = (formData.betrag || 0) - totalPaid
      formData.letzteZahlung = skontoZahlung.datum

      toast.success(t('crud.messages.discountUsed', { amount: skontoZahlung.betrag.toFixed(2) }))
    } else if (action === 'ausgleich') {
      const isValid = validate(formData)
      if (!isValid.isValid) {
        showValidationToast(isValid.errors)
        return
      }

      if (!formData.id) {
        toast.error(t('crud.messages.saveFirst'))
        return
      }

      // Process all payments as settlements
      if (formData.zahlungen && formData.zahlungen.length > 0) {
        try {
          for (const zahlung of formData.zahlungen) {
            if (zahlung.typ === 'storno') {
              // Skip reversed payments
              continue
            }

            const settlement = {
              op_id: formData.id,
              payment_amount: zahlung.betrag,
              payment_date: zahlung.datum,
              payment_reference: zahlung.referenz || `Z-${Date.now()}`,
              payment_type: zahlung.typ === 'skonto' ? 'discount' : 'payment',
              notes: zahlung.typ === 'gutschrift' ? t('crud.entities.creditNote') : null
            }

            await apiClient.post(`/api/v1/finance/open-items/${formData.id}/settle`, settlement)
          }

          toast.success(t('crud.messages.settlementSuccess'))
          setIsDirty(false)
          navigate('/finance/op-debitoren')
        } catch (error: any) {
          toast.error(error.message || t('crud.messages.settlementError'))
        }
      } else {
        // No payments to settle, just save the OP
        try {
          await saveData(formData)
          setIsDirty(false)
          toast.success(t('crud.messages.saveSuccess', { entityType: entityTypeLabel }))
          navigate('/finance/op-debitoren')
        } catch (error) {
          // Error wird bereits in useMaskData behandelt
        }
      }
    } else if (action === 'mahnung') {
      // Mahnung erstellen
      if (!formData.id) {
        toast.error(t('crud.messages.saveFirst'))
        return
      }

      try {
        const response = await fetch(`/api/finance/op-debitoren/${formData.id}/mahnung`, {
          method: 'POST',
          headers: {
            'Content-Type': 'application/json',
            'Authorization': `Bearer ${localStorage.getItem('token')}`,
          },
        })

        if (response.ok) {
          formData.mahnstufe = (formData.mahnstufe || 0) + 1
          toast.success(t('crud.messages.dunningCreated', { level: formData.mahnstufe }))
        } else {
          const error = await response.json()
          toast.error(error.detail || t('crud.messages.dunningError'))
        }
      } catch (error) {
        toast.error(t('crud.messages.networkError'))
      }
    } else if (action === 'export') {
      if (!formData.id) {
        toast.error(t('crud.messages.saveFirstGeneric'))
        return
      }
      window.open(`/api/v1/finance/open-items/${formData.id}/export`, '_blank')
    }
  })

  const handleSave = async (formData: any) => {
    await handleAction('ausgleich', formData)
  }

  const handleCancel = () => {
    if (isDirty && !confirm(t('crud.messages.unsavedChanges'))) {
      return
    }
    navigate('/finance/op-debitoren')
  }

  return (
    <ObjectPage
      config={opDebitorenConfig}
      data={data}
      onSave={handleSave}
      onCancel={handleCancel}
      isLoading={loading}
    />
  )
}
