import { useState } from 'react'
import { useNavigate } from 'react-router-dom'
import { useTranslation } from 'react-i18next'
import { ObjectPage } from '@/components/mask-builder'
import { useMaskData, useMaskValidation, useMaskActions } from '@/components/mask-builder/hooks'
import { MaskConfig } from '@/components/mask-builder/types'
import { z } from 'zod'
import { toast } from '@/hooks/use-toast'
import { getEntityTypeLabel } from '@/features/crud/utils/i18n-helpers'

// Zod-Schema für Zahlungslauf Kreditoren (wird in Komponente mit i18n erstellt)
const createZahlungslaufSchema = (t: any) => z.object({
  laufNummer: z.string().min(1, t('crud.messages.validationError')),
  ausfuehrungsDatum: z.string().regex(/^\d{4}-\d{2}-\d{2}$/, t('crud.messages.validationError')),
  gesamtBetrag: z.number().positive(t('crud.messages.validationError')),
  anzahlZahlungen: z.number().min(1, t('crud.messages.validationError')),
  status: z.enum(['entwurf', 'freigegeben', 'ausgefuehrt', 'storniert']),
  freigegebenAm: z.string().optional(),
  freigegebenDurch: z.string().optional(),
  ausgefuehrtAm: z.string().optional(),

  // SEPA-Details
  auftraggeberName: z.string().min(1, t('crud.messages.validationError')),
  auftraggeberIban: z.string().regex(/^[A-Z]{2}\d{2}[A-Z0-9]{11,30}$/, t('crud.messages.validationError')),
  auftraggeberBic: z.string().min(1, t('crud.messages.validationError')),

  // Zahlungen
  zahlungen: z.array(z.object({
    kreditorId: z.string().min(1, t('crud.messages.validationError')),
    kreditorName: z.string().min(1, t('crud.messages.validationError')),
    iban: z.string().regex(/^[A-Z]{2}\d{2}[A-Z0-9]{11,30}$/, t('crud.messages.validationError')),
    bic: z.string().min(1, t('crud.messages.validationError')),
    betrag: z.number().positive(t('crud.messages.validationError')),
    verwendungszweck: z.string().min(1, t('crud.messages.validationError')),
    skontoGenutzt: z.boolean().default(false),
    skontoBetrag: z.number().min(0).default(0),
    opReferenz: z.string().optional()
  })).min(1, t('crud.messages.validationError')),

  notizen: z.string().optional()
})

// Konfiguration für Zahlungslauf Kreditoren ObjectPage (wird in Komponente mit i18n erstellt)
const createZahlungslaufConfig = (t: any, entityTypeLabel: string): MaskConfig => ({
  title: entityTypeLabel,
  subtitle: t('crud.fields.createAndApproveSepaPayments'),
  type: 'object-page',
  tabs: [
    {
      key: 'grunddaten',
      label: t('crud.detail.basicInfo'),
      fields: [
        {
          name: 'laufNummer',
          label: t('crud.fields.runNumber'),
          type: 'text',
          required: true,
          placeholder: t('crud.tooltips.placeholders.runNumber')
        },
        {
          name: 'ausfuehrungsDatum',
          label: t('crud.fields.executionDate'),
          type: 'date',
          required: true
        },
        {
          name: 'status',
          label: t('crud.fields.status'),
          type: 'select',
          required: true,
          options: [
            { value: 'entwurf', label: t('status.draft') },
            { value: 'freigegeben', label: t('status.approved') },
            { value: 'ausgefuehrt', label: t('crud.fields.executed') },
            { value: 'storniert', label: t('crud.fields.cancelled') }
          ]
        },
        {
          name: 'gesamtBetrag',
          label: t('crud.fields.totalAmount'),
          type: 'number',
          readonly: true,
          step: 0.01
        },
        {
          name: 'anzahlZahlungen',
          label: t('crud.fields.numberOfPayments'),
          type: 'number',
          readonly: true
        }
      ],
      layout: 'grid',
      columns: 2
    },
    {
      key: 'auftraggeber',
      label: t('crud.fields.originator'),
      fields: [
        {
          name: 'auftraggeberName',
          label: t('crud.fields.name'),
          type: 'text',
          required: true,
          placeholder: t('crud.tooltips.placeholders.companyName')
        },
        {
          name: 'auftraggeberIban',
          label: t('crud.fields.iban'),
          type: 'text',
          required: true,
          placeholder: t('crud.tooltips.placeholders.iban')
        },
        {
          name: 'auftraggeberBic',
          label: t('crud.fields.bic'),
          type: 'text',
          required: true,
          placeholder: t('crud.tooltips.placeholders.bic')
        }
      ]
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
          onChange={(zahlungen) => {
            const gesamtBetrag = zahlungen.reduce((sum: number, z: any) => sum + (z.betrag || 0), 0)
            onChange({
              ..._data,
              zahlungen,
              gesamtBetrag,
              anzahlZahlungen: zahlungen.length
            })
          }}
        />
      )
    },
    {
      key: 'freigabe',
      label: t('crud.fields.approvalAndExecution'),
      fields: [
        {
          name: 'freigegebenAm',
          label: t('crud.fields.approvedOn'),
          type: 'date',
          readonly: true
        },
        {
          name: 'freigegebenDurch',
          label: t('crud.fields.approvedBy'),
          type: 'text',
          readonly: true
        },
        {
          name: 'ausgefuehrtAm',
          label: t('crud.fields.executedOn'),
          type: 'date',
          readonly: true
        }
      ],
      layout: 'grid',
      columns: 2
    },
    {
      key: 'notizen',
      label: t('crud.fields.notes'),
      fields: [
        {
          name: 'notizen',
          label: t('crud.fields.internalNotes'),
          type: 'textarea',
          placeholder: t('crud.tooltips.placeholders.paymentRunNotes')
        }
      ]
    }
  ],
  actions: [
    {
      key: 'add-payment',
      label: t('crud.actions.addPayment'),
      type: 'secondary'
    , onClick: () => {} },
    {
      key: 'validate',
      label: t('crud.actions.validate'),
      type: 'secondary'
    , onClick: () => {} },
    {
      key: 'preview',
      label: t('crud.actions.sepaPreview'),
      type: 'secondary'
    , onClick: () => {} },
    {
      key: 'approve',
      label: t('crud.actions.approve'),
      type: 'primary'
    , onClick: () => {} },
    {
      key: 'execute',
      label: t('crud.actions.execute'),
      type: 'primary'
    , onClick: () => {} },
    {
      key: 'export',
      label: t('crud.actions.sepaExport'),
      type: 'secondary'
    , onClick: () => {} }
  ],
  api: {
    baseUrl: '/api/finance/zahlungslauf-kreditoren',
    endpoints: {
      list: '/api/finance/zahlungslauf-kreditoren',
      get: '/api/finance/zahlungslauf-kreditoren/{id}',
      create: '/api/finance/zahlungslauf-kreditoren',
      update: '/api/finance/zahlungslauf-kreditoren/{id}',
      delete: '/api/finance/zahlungslauf-kreditoren/{id}'
    }
  } as any,
  validation: createZahlungslaufSchema(t),
  permissions: ['fibu.read', 'fibu.write', 'fibu.admin']
})

// Zahlungen-Tabelle Komponente
function ZahlungenTable({ data: _data, onChange }: { data: any[], onChange: (_data: any[]) => void }) {
  const { t } = useTranslation()
  const addZahlung = () => {
    onChange([..._data, {
      kreditorId: '',
      kreditorName: '',
      iban: '',
      bic: '',
      betrag: 0,
      verwendungszweck: '',
      skontoGenutzt: false,
      skontoBetrag: 0,
      opReferenz: ''
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

  return (
    <div className="space-y-4">
      <div className="flex justify-between items-center">
        <h3 className="text-lg font-semibold">{t('crud.fields.payments')}</h3>
        <button
          onClick={addZahlung}
          className="px-4 py-2 bg-blue-600 text-white rounded hover:bg-blue-700"
        >
          + {t('crud.actions.addPayment')}
        </button>
      </div>

      <div className="overflow-x-auto">
        <table className="min-w-full border border-gray-300">
          <thead className="bg-gray-50">
            <tr>
              <th className="px-4 py-2 border">{t('crud.entities.creditor')}</th>
              <th className="px-4 py-2 border">{t('crud.fields.iban')}</th>
              <th className="px-4 py-2 border">{t('crud.fields.amount')}</th>
              <th className="px-4 py-2 border">{t('crud.fields.purpose')}</th>
              <th className="px-4 py-2 border">{t('crud.fields.discount')}</th>
              <th className="px-4 py-2 border">{t('crud.fields.opReference')}</th>
              <th className="px-4 py-2 border">{t('crud.actions.delete')}</th>
            </tr>
          </thead>
          <tbody>
            {_data.map((zahlung, index) => (
              <tr key={index} className="border">
                <td className="px-4 py-2 border">
                  <div>
                    <input
                      type="text"
                      value={zahlung.kreditorId}
                      onChange={(e) => updateZahlung(index, 'kreditorId', e.target.value)}
                      className="w-full p-1 border rounded text-sm mb-1"
                      placeholder={t('crud.tooltips.placeholders.creditorNumber')}
                    />
                    <input
                      type="text"
                      value={zahlung.kreditorName}
                      onChange={(e) => updateZahlung(index, 'kreditorName', e.target.value)}
                      className="w-full p-1 border rounded text-sm"
                      placeholder={t('crud.fields.name')}
                    />
                  </div>
                </td>
                <td className="px-4 py-2 border">
                  <div>
                    <input
                      type="text"
                      value={zahlung.iban}
                      onChange={(e) => updateZahlung(index, 'iban', e.target.value)}
                      className="w-full p-1 border rounded text-sm mb-1"
                      placeholder={t('crud.fields.iban')}
                    />
                    <input
                      type="text"
                      value={zahlung.bic}
                      onChange={(e) => updateZahlung(index, 'bic', e.target.value)}
                      className="w-full p-1 border rounded text-sm"
                      placeholder={t('crud.fields.bic')}
                    />
                  </div>
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
                  <input
                    type="text"
                    value={zahlung.verwendungszweck}
                    onChange={(e) => updateZahlung(index, 'verwendungszweck', e.target.value)}
                    className="w-full p-1 border rounded"
                    placeholder={t('crud.tooltips.placeholders.invoiceNumber')}
                  />
                </td>
                <td className="px-4 py-2 border">
                  <div>
                    <input
                      type="checkbox"
                      checked={zahlung.skontoGenutzt || false}
                      onChange={(e) => updateZahlung(index, 'skontoGenutzt', e.target.checked)}
                      className="mr-2"
                    />
                    <input
                      type="number"
                      step="0.01"
                      value={zahlung.skontoBetrag}
                      onChange={(e) => updateZahlung(index, 'skontoBetrag', parseFloat(e.target.value) || 0)}
                      className="w-20 p-1 border rounded text-sm"
                      placeholder={t('crud.tooltips.placeholders.amount')}
                    />
                  </div>
                </td>
                <td className="px-4 py-2 border">
                  <input
                    type="text"
                    value={zahlung.opReferenz || ''}
                    onChange={(e) => updateZahlung(index, 'opReferenz', e.target.value)}
                    className="w-full p-1 border rounded text-sm"
                    placeholder={t('crud.tooltips.placeholders.opReference')}
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

export default function ZahlungslaufKreditorenPage(): JSX.Element {
  const { t } = useTranslation()
  const navigate = useNavigate()
  const [isDirty, setIsDirty] = useState(false)
  const entityType = 'paymentRun'
  const entityTypeLabel = getEntityTypeLabel(t, entityType, 'Zahlungslauf Kreditoren')
  const zahlungslaufConfig = createZahlungslaufConfig(t, entityTypeLabel)

  const { data, loading, saveData } = useMaskData({
    apiUrl: zahlungslaufConfig.api.baseUrl,
    id: 'new'
  })

  const { validate, showValidationToast } = useMaskValidation(zahlungslaufConfig.validation)

  const { handleAction } = useMaskActions(async (action: string, formData: any) => {
    if (action === 'add-payment') {
      // Neue Zahlung hinzufügen wird in der Tabelle behandelt
      // Dieser Button ist redundant, da die Tabelle ihren eigenen Button hat
      return
    } else if (action === 'validate') {
      const isValid = validate(formData)
      if (isValid.isValid) {
        toast({
          title: t('crud.messages.validationSuccess'),
          description: t('crud.messages.allDataCorrect'),
        })
      } else {
        showValidationToast(isValid.errors)
      }
    } else if (action === 'preview') {
      // SEPA-Vorschau
      if (!formData.id) {
        toast({
          variant: 'destructive',
          title: t('common.error'),
          description: t('crud.messages.savePaymentRunFirst'),
        })
        return
      }
      window.open(`/api/finance/zahlungslauf-kreditoren/${formData.id}/preview`, '_blank')
    } else if (action === 'approve') {
      // Freigeben
      if (!formData.id) {
        toast({
          variant: 'destructive',
          title: t('common.error'),
          description: t('crud.messages.savePaymentRunFirst'),
        })
        return
      }

      try {
        const response = await fetch(`/api/finance/zahlungslauf-kreditoren/${formData.id}/approve`, {
          method: 'POST',
          headers: {
            'Content-Type': 'application/json',
            'Authorization': `Bearer ${localStorage.getItem('token')}`,
          },
        })

        if (response.ok) {
          toast({
            title: t('crud.messages.approvalSuccess'),
            description: t('crud.messages.paymentRunApproved'),
          })
          // Refresh data
          window.location.reload()
        } else {
          const error = await response.json()
          toast({
            variant: 'destructive',
            title: t('crud.messages.approvalError'),
            description: error.detail || t('common.unknownError'),
          })
        }
      } catch (error) {
        toast({
          variant: 'destructive',
          title: t('crud.messages.networkError'),
          description: t('crud.messages.networkErrorDesc'),
        })
      }
    } else if (action === 'execute') {
      const isValid = validate(formData)
      if (!isValid.isValid) {
        showValidationToast(isValid.errors)
        return
      }

      try {
        await saveData(formData)
        setIsDirty(false)
        navigate('/finance/zahlungslauf-kreditoren')
      } catch (error) {
        // Error wird bereits in useMaskData behandelt
      }
    } else if (action === 'export') {
      if (!formData.id) {
        toast({
          variant: 'destructive',
          title: t('common.error'),
          description: t('crud.messages.savePaymentRunFirst'),
        })
        return
      }
      window.open(`/api/finance/zahlungslauf-kreditoren/${formData.id}/export`, '_blank')
    }
  })

  const handleSave = async (formData: any) => {
    await handleAction('execute', formData)
  }

  const handleCancel = () => {
    if (isDirty && !confirm(t('crud.messages.unsavedChanges'))) {
      return
    }
    navigate('/finance/zahlungslauf-kreditoren')
  }

  return (
    <ObjectPage
      config={zahlungslaufConfig}
      data={data}
      onSave={handleSave}
      onCancel={handleCancel}
      isLoading={loading}
    />
  )
}