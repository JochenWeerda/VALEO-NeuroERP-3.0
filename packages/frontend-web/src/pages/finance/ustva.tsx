import { useState } from 'react'
import { useNavigate } from 'react-router-dom'
import { useTranslation } from 'react-i18next'
import { ObjectPage } from '@/components/mask-builder'
import { useMaskData, useMaskValidation, useMaskActions } from '@/components/mask-builder/hooks'
import { MaskConfig } from '@/components/mask-builder/types'
import { z } from 'zod'
import { toast } from '@/hooks/use-toast'
import { getEntityTypeLabel } from '@/features/crud/utils/i18n-helpers'

// Zod-Schema für UStVA (wird in Komponente mit i18n erstellt)
const createUstvaSchema = (t: any) => z.object({
  periode: z.string().regex(/^\d{4}-\d{2}$/, t('crud.messages.validationError')),
  voranmeldungszeitraum: z.enum(['monatlich', 'quartalsweise']),
  steuerpflichtiger: z.string().min(1, t('crud.messages.validationError')),
  ustId: z.string().optional(),
  steuerberater: z.string().optional(),

  // Umsätze
  umsatz19: z.number().default(0),
  umsatz7: z.number().default(0),
  umsatz0: z.number().default(0),
  umsatzSonstige: z.number().default(0),
  gesamtUmsatz: z.number().default(0),

  // Vorsteuer
  vorsteuer19: z.number().default(0),
  vorsteuer7: z.number().default(0),
  vorsteuer0: z.number().default(0),
  vorsteuerSonstige: z.number().default(0),
  gesamtVorsteuer: z.number().default(0),

  // Berechnung
  ust19: z.number().default(0),
  ust7: z.number().default(0),
  ust0: z.number().default(0),
  ustSonstige: z.number().default(0),
  gesamtUst: z.number().default(0),

  // Abweichungen
  abweichungen: z.array(z.object({
    position: z.string(),
    beschreibung: z.string(),
    betrag: z.number(),
    grund: z.string()
  })).optional(),

  // Status
  status: z.enum(['entwurf', 'pruefung', 'freigegeben', 'abgegeben']),
  freigegebenAm: z.string().optional(),
  freigegebenDurch: z.string().optional(),
  abgegebenAm: z.string().optional(),
  elsterReferenz: z.string().optional(),
  notizen: z.string().optional()
})

// Konfiguration für UStVA ObjectPage (wird in Komponente mit i18n erstellt)
const createUstvaConfig = (t: any, entityTypeLabel: string): MaskConfig => ({
  title: entityTypeLabel,
  subtitle: t('crud.fields.createAndSubmitUstva'),
  type: 'object-page',
  tabs: [
    {
      key: 'grunddaten',
      label: t('crud.detail.basicInfo'),
      fields: [
        {
          name: 'periode',
          label: t('crud.fields.period'),
          type: 'text',
          required: true,
          placeholder: t('crud.tooltips.placeholders.period'),
          pattern: '^\\d{4}-\\d{2}$'
         } as any, {},
        {
          name: 'voranmeldungszeitraum',
          label: t('crud.fields.declarationPeriod'),
          type: 'select',
          required: true,
          options: [
            { value: 'monatlich', label: t('crud.fields.monthly') },
            { value: 'quartalsweise', label: t('crud.fields.quarterly') }
          ]
        },
        {
          name: 'steuerpflichtiger',
          label: t('crud.fields.taxpayer'),
          type: 'text',
          required: true,
          placeholder: t('crud.tooltips.placeholders.company')
        },
        {
          name: 'ustId',
          label: t('crud.fields.vatId'),
          type: 'text',
          placeholder: t('crud.tooltips.placeholders.vatId')
        },
        {
          name: 'steuerberater',
          label: t('crud.fields.taxAdvisor'),
          type: 'text',
          placeholder: t('crud.tooltips.placeholders.taxAdvisor')
        },
        {
          name: 'status',
          label: t('crud.fields.status'),
          type: 'select',
          required: true,
          options: [
            { value: 'entwurf', label: t('status.draft') },
            { value: 'pruefung', label: t('crud.fields.inReview') },
            { value: 'freigegeben', label: t('status.approved') },
            { value: 'abgegeben', label: t('crud.fields.submitted') }
          ]
        }
      ],
      layout: 'grid',
      columns: 2
    },
    {
      key: 'umsatz',
      label: t('crud.fields.revenue'),
      fields: [
        {
          name: 'umsatz19',
          label: t('crud.fields.revenue19'),
          type: 'number',
          step: 0.01,
          placeholder: t('crud.tooltips.placeholders.amount')
        },
        {
          name: 'umsatz7',
          label: t('crud.fields.revenue7'),
          type: 'number',
          step: 0.01,
          placeholder: t('crud.tooltips.placeholders.amount')
        },
        {
          name: 'umsatz0',
          label: t('crud.fields.revenue0'),
          type: 'number',
          step: 0.01,
          placeholder: t('crud.tooltips.placeholders.amount')
        },
        {
          name: 'umsatzSonstige',
          label: t('crud.fields.revenueOther'),
          type: 'number',
          step: 0.01,
          placeholder: t('crud.tooltips.placeholders.amount')
        },
        {
          name: 'gesamtUmsatz',
          label: t('crud.fields.totalRevenue'),
          type: 'number',
          readonly: true,
          step: 0.01
        }
      ],
      layout: 'grid',
      columns: 2
    },
    {
      key: 'vorsteuer',
      label: t('crud.fields.inputTax'),
      fields: [
        {
          name: 'vorsteuer19',
          label: t('crud.fields.inputTax19'),
          type: 'number',
          step: 0.01,
          placeholder: t('crud.tooltips.placeholders.amount')
        },
        {
          name: 'vorsteuer7',
          label: t('crud.fields.inputTax7'),
          type: 'number',
          step: 0.01,
          placeholder: t('crud.tooltips.placeholders.amount')
        },
        {
          name: 'vorsteuer0',
          label: t('crud.fields.inputTax0'),
          type: 'number',
          step: 0.01,
          placeholder: t('crud.tooltips.placeholders.amount')
        },
        {
          name: 'vorsteuerSonstige',
          label: t('crud.fields.inputTaxOther'),
          type: 'number',
          step: 0.01,
          placeholder: t('crud.tooltips.placeholders.amount')
        },
        {
          name: 'gesamtVorsteuer',
          label: t('crud.fields.totalInputTax'),
          type: 'number',
          readonly: true,
          step: 0.01
        }
      ],
      layout: 'grid',
      columns: 2
    },
    {
      key: 'berechnung',
      label: t('crud.fields.calculation'),
      fields: [
        {
          name: 'ust19',
          label: t('crud.fields.vat19'),
          type: 'number',
          readonly: true,
          step: 0.01
        },
        {
          name: 'ust7',
          label: t('crud.fields.vat7'),
          type: 'number',
          readonly: true,
          step: 0.01
        },
        {
          name: 'ust0',
          label: t('crud.fields.vat0'),
          type: 'number',
          readonly: true,
          step: 0.01
        },
        {
          name: 'ustSonstige',
          label: t('crud.fields.vatOther'),
          type: 'number',
          readonly: true,
          step: 0.01
        },
        {
          name: 'gesamtUst',
          label: t('crud.fields.totalVat'),
          type: 'number',
          readonly: true,
          step: 0.01,
          helpText: t('crud.tooltips.fields.vatMinusInputTax')
        }
      ],
      layout: 'grid',
      columns: 2
    },
    {
      key: 'abweichungen',
      label: t('crud.fields.deviations'),
      fields: []
    } as any,
    {
      key: 'abweichungen_custom',
      label: '',
      fields: [],
      customRender: (_data: any, onChange: (_data: any) => void) => (
        <AbweichungenTable
          data={_data.abweichungen || []}
          onChange={(abweichungen) => onChange({ ..._data, abweichungen })}
        />
      )
    },
    {
      key: 'freigabe',
      label: t('crud.fields.approvalAndSubmission'),
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
          name: 'abgegebenAm',
          label: t('crud.fields.submittedOn'),
          type: 'date',
          readonly: true
        },
        {
          name: 'elsterReferenz',
          label: t('crud.fields.elsterReference'),
          type: 'text',
          readonly: true,
          placeholder: t('crud.tooltips.placeholders.elsterReference')
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
          placeholder: t('crud.tooltips.placeholders.ustvaNotes')
        }
      ]
    }
  ],
  actions: [
    {
      key: 'calculate',
      label: t('crud.actions.recalculate'),
      type: 'secondary'
    , onClick: () => {} },
    {
      key: 'validate',
      label: t('crud.actions.validate'),
      type: 'secondary'
    , onClick: () => {} },
    {
      key: 'approve',
      label: t('crud.actions.approve'),
      type: 'primary'
    , onClick: () => {} },
    {
      key: 'submit',
      label: t('crud.actions.submitToElster'),
      type: 'primary'
    , onClick: () => {} },
    {
      key: 'export',
      label: t('crud.actions.xmlExport'),
      type: 'secondary'
    , onClick: () => {} }
  ],
  api: {
    baseUrl: '/api/finance/ustva',
    endpoints: {
      list: '/api/finance/ustva',
      get: '/api/finance/ustva/{id}',
      create: '/api/finance/ustva',
      update: '/api/finance/ustva/{id}',
      delete: '/api/finance/ustva/{id}'
    }
  } as any,
  validation: createUstvaSchema(t),
  permissions: ['fibu.read', 'fibu.write', 'fibu.admin']
})

// Abweichungen-Tabelle Komponente
function AbweichungenTable({ data: _data, onChange }: { data: any[], onChange: (_data: any[]) => void }) {
  const { t } = useTranslation()
  const addAbweichung = () => {
    onChange([..._data, {
      position: '',
      beschreibung: '',
      betrag: 0,
      grund: ''
    }])
  }

  const updateAbweichung = (index: number, field: string, value: any) => {
    const newData = [..._data]
    newData[index] = { ...newData[index], [field]: value }
    onChange(newData)
  }

  const removeAbweichung = (index: number) => {
    onChange(_data.filter((_, i) => i !== index))
  }

  return (
    <div className="space-y-4">
      <div className="flex justify-between items-center">
        <h3 className="text-lg font-semibold">{t('crud.fields.deviations')}</h3>
        <button
          onClick={addAbweichung}
          className="px-4 py-2 bg-blue-600 text-white rounded hover:bg-blue-700"
        >
          + {t('crud.actions.addDeviation')}
        </button>
      </div>

      <div className="overflow-x-auto">
        <table className="min-w-full border border-gray-300">
          <thead className="bg-gray-50">
            <tr>
              <th className="px-4 py-2 border">{t('crud.fields.position')}</th>
              <th className="px-4 py-2 border">{t('crud.fields.description')}</th>
              <th className="px-4 py-2 border">{t('crud.fields.amount')}</th>
              <th className="px-4 py-2 border">{t('crud.fields.reason')}</th>
              <th className="px-4 py-2 border">{t('crud.actions.delete')}</th>
            </tr>
          </thead>
          <tbody>
            {_data.map((abweichung, index) => (
              <tr key={index} className="border">
                <td className="px-4 py-2 border">
                  <input
                    type="text"
                    value={abweichung.position}
                    onChange={(e) => updateAbweichung(index, 'position', e.target.value)}
                    className="w-full p-1 border rounded"
                    placeholder={t('crud.tooltips.placeholders.position')}
                  />
                </td>
                <td className="px-4 py-2 border">
                  <input
                    type="text"
                    value={abweichung.beschreibung}
                    onChange={(e) => updateAbweichung(index, 'beschreibung', e.target.value)}
                    className="w-full p-1 border rounded"
                    placeholder={t('crud.tooltips.placeholders.deviationDescription')}
                  />
                </td>
                <td className="px-4 py-2 border">
                  <input
                    type="number"
                    step="0.01"
                    value={abweichung.betrag}
                    onChange={(e) => updateAbweichung(index, 'betrag', parseFloat(e.target.value) || 0)}
                    className="w-full p-1 border rounded"
                  />
                </td>
                <td className="px-4 py-2 border">
                  <input
                    type="text"
                    value={abweichung.grund}
                    onChange={(e) => updateAbweichung(index, 'grund', e.target.value)}
                    className="w-full p-1 border rounded"
                    placeholder={t('crud.tooltips.placeholders.reason')}
                  />
                </td>
                <td className="px-4 py-2 border">
                  <button
                    onClick={() => removeAbweichung(index)}
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

export default function UStVAPage(): JSX.Element {
  const { t } = useTranslation()
  const navigate = useNavigate()
  const [isDirty, setIsDirty] = useState(false)
  const entityType = 'ustva'
  const entityTypeLabel = getEntityTypeLabel(t, entityType, 'Umsatzsteuervoranmeldung')
  const ustvaConfig = createUstvaConfig(t, entityTypeLabel)

  const { data, loading, saveData } = useMaskData({
    apiUrl: ustvaConfig.api.baseUrl,
    id: 'new'
  })

  const { validate, showValidationToast } = useMaskValidation(ustvaConfig.validation)

  const { handleAction } = useMaskActions(async (action: string, formData: any) => {
    if (action === 'calculate') {
      // Berechnung durchführen
      const calculated = {
        ...formData,
        gesamtUmsatz: (formData.umsatz19 || 0) + (formData.umsatz7 || 0) + (formData.umsatz0 || 0) + (formData.umsatzSonstige || 0),
        gesamtVorsteuer: (formData.vorsteuer19 || 0) + (formData.vorsteuer7 || 0) + (formData.vorsteuer0 || 0) + (formData.vorsteuerSonstige || 0),
        ust19: (formData.umsatz19 || 0) * 0.19,
        ust7: (formData.umsatz7 || 0) * 0.07,
        ust0: 0,
        ustSonstige: (formData.umsatzSonstige || 0) * 0.19, // Annahme 19% für sonstige
        gesamtUst: ((formData.umsatz19 || 0) * 0.19) + ((formData.umsatz7 || 0) * 0.07) + ((formData.umsatzSonstige || 0) * 0.19) - ((formData.vorsteuer19 || 0) + (formData.vorsteuer7 || 0) + (formData.vorsteuer0 || 0) + (formData.vorsteuerSonstige || 0))
      }

      // Update form data with calculations
      Object.keys(calculated).forEach(key => {
        if (key !== 'formData') {
          formData[key] = calculated[key as keyof typeof calculated]
        }
      })

      toast({
        title: t('crud.messages.calculationCompleted'),
        description: t('crud.messages.ustvaAmountsRecalculated'),
      })
    } else if (action === 'validate') {
      const isValid = validate(formData)
      if (isValid.isValid) {
        toast({
          title: t('crud.messages.validationSuccess'),
          description: t('crud.messages.ustvaDataCorrect'),
        })
      } else {
        showValidationToast(isValid.errors)
      }
    } else if (action === 'approve') {
      // Freigeben
      if (!formData.id) {
        toast({
          variant: 'destructive',
          title: t('common.error'),
          description: t('crud.messages.saveUstvaFirst'),
        })
        return
      }

      try {
        const response = await fetch(`/api/finance/ustva/${formData.id}/approve`, {
          method: 'POST',
          headers: {
            'Content-Type': 'application/json',
            'Authorization': `Bearer ${localStorage.getItem('token')}`,
          },
        })

        if (response.ok) {
          toast({
            title: t('crud.messages.approvalSuccess'),
            description: t('crud.messages.ustvaApproved'),
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
    } else if (action === 'submit') {
      const isValid = validate(formData)
      if (!isValid.isValid) {
        showValidationToast(isValid.errors)
        return
      }

      try {
        await saveData(formData)
        setIsDirty(false)
        toast({
          title: t('crud.messages.ustvaSubmitted'),
          description: t('crud.messages.ustvaSubmittedDesc'),
        })
        navigate('/finance/ustva')
      } catch (error) {
        // Error wird bereits in useMaskData behandelt
      }
    } else if (action === 'export') {
      if (!formData.id) {
        toast({
          variant: 'destructive',
          title: t('common.error'),
          description: t('crud.messages.saveUstvaFirst'),
        })
        return
      }
      window.open(`/api/finance/ustva/${formData.id}/export`, '_blank')
    }
  })

  const handleSave = async (formData: any) => {
    await handleAction('submit', formData)
  }

  const handleCancel = () => {
    if (isDirty && !confirm(t('crud.messages.unsavedChanges'))) {
      return
    }
    navigate('/finance/ustva')
  }

  return (
    <ObjectPage
      config={ustvaConfig}
      data={data}
      onSave={handleSave}
      onCancel={handleCancel}
      isLoading={loading}
    />
  )
}