import { useState } from 'react'
import { useNavigate } from 'react-router-dom'
import { useTranslation } from 'react-i18next'
import { ObjectPage } from '@/components/mask-builder'
import { useMaskData, useMaskActions } from '@/components/mask-builder/hooks'
import { MaskConfig } from '@/components/mask-builder/types'
import { getFieldsFromMaskConfig, validateFields } from '@/components/mask-builder/validation'
import { toast } from '@/hooks/use-toast'
import { apiClient } from '@/lib/axios'
import { getEntityTypeLabel } from '@/features/crud/utils/i18n-helpers'
import { buildDecisionView } from '@/policy/decision-view'
import { ProcessStatusPanel } from '@/components/workflow/ProcessStatusPanel'

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
         } as any,
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
            { value: 'draft', label: t('status.draft') },
            { value: 'validated', label: t('crud.fields.inReview') },
            { value: 'approved', label: t('status.approved') },
            { value: 'submitted', label: t('crud.fields.submitted') }
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
    { key: 'calculate', label: t('crud.actions.recalculate'), type: 'secondary' },
    { key: 'validate', label: t('crud.actions.validate'), type: 'secondary' },
    { key: 'approve', label: t('crud.actions.approve'), type: 'primary' },
    { key: 'submit', label: t('crud.actions.submitToElster'), type: 'primary' },
    { key: 'export', label: t('crud.actions.xmlExport'), type: 'secondary' }
  ],
  api: {
    baseUrl: '/api/v1/finance/vat-return',
    endpoints: {
      list: '/api/v1/finance/vat-return',
      get: '/api/v1/finance/vat-return/{id}',
      create: '/api/v1/finance/vat-return',
      update: '/api/v1/finance/vat-return/{id}',
      delete: '/api/v1/finance/vat-return/{id}'
    }
  } as any,
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
  const [actionLoadingKey, setActionLoadingKey] = useState<string | null>(null)
  const [workspaceData, setWorkspaceData] = useState<any>({})
  const entityType = 'ustva'
  const entityTypeLabel = getEntityTypeLabel(t, entityType, 'Umsatzsteuervoranmeldung')
  const ustvaConfig = createUstvaConfig(t, entityTypeLabel)
  const currentActor = localStorage.getItem('userEmail') || localStorage.getItem('username') || 'api'

  const { data, loading } = useMaskData({
    apiUrl: ustvaConfig.api.baseUrl,
    id: 'new',
    transformResponse: (response: any) => {
      if (response?.data) {
        return {
          ...response.data,
          periode: response.data.period,
          voranmeldungszeitraum: response.data.return_type === 'quarterly' ? 'quartalsweise' : 'monatlich',
          steuerpflichtiger: response.data.taxpayer_name,
          ustId: response.data.vat_id,
          gesamtUmsatz: response.data.total_sales_net,
          gesamtVorsteuer: response.data.total_input_tax,
          gesamtUst: response.data.vat_payable,
          status: response.data.status,
          freigegebenAm: response.data.approved_at,
          freigegebenDurch: response.data.approved_by,
          abgegebenAm: response.data.submitted_at,
          elsterReferenz: response.data.elster_reference,
          approval_status: response.data.approval_status,
          approval_can_submit: response.data.approval_can_submit,
          approval_override_resolution: response.data.approval_override_resolution,
          approval_explainability: response.data.approval_explainability,
        }
      }
      return response
    }
  })

  const validate = (formData: any) => validateFields(getFieldsFromMaskConfig(ustvaConfig), formData ?? {})
  const showValidationToast = (errors: Record<string, string>) => {
    toast({ variant: 'destructive', title: t('crud.messages.validationError'), description: `${Object.keys(errors).length} Feld(er) muessen korrigiert werden.` })
  }

  const applyVATReturnResponse = (response: any) => {
    const payload = response?.data ?? response
    if (!payload) {
      return
    }
    setWorkspaceData({
      ...payload,
      periode: payload.period,
      voranmeldungszeitraum: payload.return_type === 'quarterly' ? 'quartalsweise' : 'monatlich',
      steuerpflichtiger: payload.taxpayer_name,
      ustId: payload.vat_id,
      gesamtUmsatz: payload.total_sales_net,
      gesamtVorsteuer: payload.total_input_tax,
      gesamtUst: payload.vat_payable,
      status: payload.status,
      freigegebenAm: payload.approved_at,
      freigegebenDurch: payload.approved_by,
      abgegebenAm: payload.submitted_at,
      elsterReferenz: payload.elster_reference,
      approval_status: payload.approval_status,
      approval_can_submit: payload.approval_can_submit,
      approval_override_resolution: payload.approval_override_resolution,
      approval_explainability: payload.approval_explainability,
    })
  }

  const { handleAction } = useMaskActions(async (action: string, formData: any) => {
    if (action === 'calculate') {
      setActionLoadingKey('calculate')
      try {
        const result = await apiClient.post<Record<string, unknown>>('/api/v1/finance/vat-return/calculate', {
          period: formData?.periode,
        })
        toast({ title: t('crud.messages.calculationCompleted'), description: t('crud.messages.ustvaAmountsRecalculated') })
        applyVATReturnResponse(result)
      } catch (error: any) {
        const msg = error.response?.data?.detail ?? error.message
        toast({ variant: 'destructive', title: t('common.error'), description: msg })
      } finally {
        setActionLoadingKey(null)
      }
      return
    }
    if (action === 'validate') {
      const errors = validate(formData)
      if (Object.keys(errors).length === 0) {
        toast({
          title: t('crud.messages.validationSuccess'),
          description: t('crud.messages.ustvaDataCorrect'),
        })
      } else {
        showValidationToast(errors)
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
        const response = await apiClient.post(`/api/v1/finance/vat-return/${formData.id}/approve`, {
          approved_by: currentActor,
        })
        applyVATReturnResponse(response)
        toast({
          title: t('crud.messages.approvalSuccess'),
          description: t('crud.messages.ustvaApproved'),
        })
      } catch (error: any) {
        toast({
          variant: 'destructive',
          title: t('crud.messages.networkError'),
          description: error.response?.data?.detail ?? t('crud.messages.networkErrorDesc'),
        })
      }
    } else if (action === 'submit') {
      const errors = validate(formData)
      if (Object.keys(errors).length > 0) {
        showValidationToast(errors)
        return
      }
      if (!formData.id) {
        toast({
          variant: 'destructive',
          title: t('common.error'),
          description: t('crud.messages.saveUstvaFirst'),
        })
        return
      }
      if (formData.approval_can_submit !== true) {
        toast({
          variant: 'destructive',
          title: t('crud.messages.validationError'),
          description: t('crud.messages.ustvaApproved'),
        })
        return
      }

      try {
        const response = await apiClient.post(`/api/v1/finance/vat-return/${formData.id}/submit`, {
          submitted_by: currentActor,
        })
        applyVATReturnResponse(response)
        setIsDirty(false)
        toast({
          title: t('crud.messages.ustvaSubmitted'),
          description: t('crud.messages.ustvaSubmittedDesc'),
        })
        navigate('/finance/ustva')
      } catch (error) {
        // Error wird bereits in useMaskData behandelt
      }
    }
    if (action === 'export') {
      if (!formData.id) {
        toast({ variant: 'destructive', title: t('common.error'), description: t('crud.messages.saveUstvaFirst') })
        return
      }
      setActionLoadingKey('export')
      try {
        const res = await apiClient.post<{ url?: string }>('/api/v1/export/list', { entity: 'vat_return', format: 'xml', id: formData.id })
        if (res?.url) window.open(res.url, '_blank')
        toast({ title: t('crud.actions.xmlExport'), description: t('crud.messages.exportCreated', { defaultValue: 'Export erstellt' }) })
      } catch (error: any) {
        const msg = error.response?.data?.detail ?? error.message
        toast({ variant: 'destructive', title: t('common.error'), description: msg })
      } finally {
        setActionLoadingKey(null)
      }
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

  const effectiveData = Object.keys(workspaceData).length > 0 ? workspaceData : data
  const approvalDecisionView = buildDecisionView(effectiveData?.approval_explainability)

  return (
    <>
      {effectiveData?.id && approvalDecisionView !== null ? (
        <ProcessStatusPanel view={approvalDecisionView} className="mb-4 px-4 py-3">
          <div className="mt-3 grid gap-3 md:grid-cols-3">
            <div>
              <div className="text-xs uppercase tracking-wide text-current/70">Workflowstatus</div>
              <div className="mt-1 font-medium">{effectiveData.approval_status || effectiveData.status || '-'}</div>
            </div>
            <div>
              <div className="text-xs uppercase tracking-wide text-current/70">Abgabefaehig</div>
              <div className="mt-1 font-medium">{effectiveData.approval_can_submit ? 'Ja' : 'Nein'}</div>
            </div>
            <div>
              <div className="text-xs uppercase tracking-wide text-current/70">Regel</div>
              <div className="mt-1 font-medium">{effectiveData.approval_override_resolution?.rule_id || '-'}</div>
            </div>
          </div>
        </ProcessStatusPanel>
      ) : null}
      <ObjectPage
        config={ustvaConfig}
        data={effectiveData}
        onSave={handleSave}
        onCancel={handleCancel}
        isLoading={loading}
        onAction={(key, formData) => handleAction(key, formData)}
        loadingActionKey={actionLoadingKey}
      />
    </>
  )
}
