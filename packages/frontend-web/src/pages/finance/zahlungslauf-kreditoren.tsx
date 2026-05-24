import { useState } from 'react'
import { useNavigate } from 'react-router-dom'
import { useTranslation } from 'react-i18next'
import { ObjectPage } from '@/components/mask-builder'
import { OperationalCaseHeader } from '@/components/workflow/OperationalCaseHeader'
import { OperationalContextPanel } from '@/components/workflow/OperationalContextPanel'
import { OperationalTimeline } from '@/components/workflow/OperationalTimeline'
import {
  CrudCapabilityChecklist,
  ManagementDecisionPanel,
  NextActionPanel,
  OperationalTaskPlan,
  RoleFocusBar,
  type UxTaskItem,
} from '@/components/workflow'
import { useMaskData, useMaskActions } from '@/components/mask-builder/hooks'
import { MaskConfig } from '@/components/mask-builder/types'
import { getFieldsFromMaskConfig, validateFields } from '@/components/mask-builder/validation'
import { toast } from '@/hooks/use-toast'
import { getEntityTypeLabel } from '@/features/crud/utils/i18n-helpers'
import { ModuleToolbar } from '@/components/navigation/ModuleToolbar'
import { LeaveConfirmDialog } from '@/components/LeaveConfirmDialog'
import { useUnsavedChanges } from '@/hooks/useUnsavedChanges'
import { validateIBAN, formatIBAN, lookupIBAN } from '@/lib/utils/iban-validator'
import { buildDecisionView } from '@/policy/decision-view'
import { ProcessStatusPanel } from '@/components/workflow/ProcessStatusPanel'
import { useApprovalDensityProfile } from '@/features/workflow/useApprovalDensityProfile'
import { normalizeOperationalStatus } from '@/lib/operational-status'
import { apiClient } from '@/lib/api-client'

type FinanceRoleFocus = 'all' | 'accounting' | 'treasury' | 'controller' | 'tax-advisor' | 'management'

const financeRoleProfiles: Array<{ id: FinanceRoleFocus; label: string; description: string }> = [
  { id: 'all', label: 'Alle', description: 'Gesamtbild fuer Zahlungslauf, Freigabe und Ausfuehrung.' },
  { id: 'accounting', label: 'Buchhaltung', description: 'Stammdaten, offene Posten, Buchungs- und Belegqualitaet.' },
  { id: 'treasury', label: 'Zahlungsverkehr', description: 'SEPA-Datei, Ausfuehrungsdatum, IBAN/BIC und Bankfreigabe.' },
  { id: 'controller', label: 'Controlling', description: 'Betrag, Skonto, Liquiditaetswirkung und Abweichungen.' },
  { id: 'tax-advisor', label: 'Steuerbuero', description: 'Nachvollziehbare Export- und Buchungsgrundlage.' },
  { id: 'management', label: 'Leitung', description: 'Freigabestatus, Stopper, Risiko und Entscheidung.' },
]

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
            { value: 'draft', label: t('status.draft') },
            { value: 'approved', label: t('status.approved') },
            { value: 'executed', label: t('crud.fields.executed') },
            { value: 'cancelled', label: t('crud.fields.cancelled') }
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
            // Berechne Gesamtbetrag mit Skonto
            const gesamtBetrag = zahlungen.reduce((sum: number, z: any) => {
              const betrag = z.betrag || 0
              const skontoBetrag = z.skontoGenutzt && z.skontoBetrag ? z.skontoBetrag : 0
              return sum + betrag - skontoBetrag
            }, 0)
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
      key: 'approve',
      label: t('crud.actions.approve'),
      type: 'primary',
      onClick: async (data: any) => {
        if (!data.id) {
          toast({
            variant: 'destructive',
            title: t('crud.messages.validationError'),
            description: t('crud.messages.savePaymentRunFirst')
          })
          return
        }
        if (data.approval_status !== 'executed') {
          toast({
            variant: 'destructive',
            title: t('crud.messages.validationError'),
            description: t('crud.messages.paymentRunMustBeApproved')
          })
          return
        }
        try {
          const actor = localStorage.getItem('userEmail') || localStorage.getItem('username') || 'api'
          const response = await fetch(`/api/v1/finance/payment-runs/${data.id}/approve`, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ approved_by: actor })
          })
          if (response.ok) {
            toast({
              title: t('crud.messages.paymentRunApproved'),
              description: t('crud.messages.paymentRunApprovedDesc')
            })
          } else {
            throw new Error(await response.text())
          }
        } catch (error: any) {
          toast({
            variant: 'destructive',
            title: t('crud.messages.updateError', { entityType: entityTypeLabel }),
            description: error.message
          })
        }
      }
    },
    {
      key: 'sepaPreview',
      label: t('crud.actions.sepaPreview'),
      type: 'secondary',
      onClick: async (data: any) => {
        if (!data.id) {
          toast({
            variant: 'destructive',
            title: t('crud.messages.validationError'),
            description: t('crud.messages.savePaymentRunFirst')
          })
          return
        }
        try {
          const response = await fetch(`/api/v1/finance/payment-runs/${data.id}/sepa-xml`)
          if (response.ok) {
            const blob = await response.blob()
            const url = window.URL.createObjectURL(blob)
            window.open(url, '_blank')
          } else {
            throw new Error(await response.text())
          }
        } catch (error: any) {
          toast({
            variant: 'destructive',
            title: t('crud.messages.loadDataError'),
            description: error.message
          })
        }
      }
    },
    {
      key: 'sepaExport',
      label: t('crud.actions.sepaExport'),
      type: 'primary',
      onClick: async (data: any) => {
        if (!data.id) {
          toast({
            variant: 'destructive',
            title: t('crud.messages.validationError'),
            description: t('crud.messages.savePaymentRunFirst')
          })
          return
        }
        if (data.approval_can_execute !== true) {
          toast({
            variant: 'destructive',
            title: t('crud.messages.validationError'),
            description: t('crud.messages.paymentRunMustBeApproved')
          })
          return
        }
        try {
          // Execute payment run (generates SEPA XML and updates status)
          const actor = localStorage.getItem('userEmail') || localStorage.getItem('username') || 'api'
          const executeResponse = await fetch(`/api/v1/finance/payment-runs/${data.id}/execute`, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ executed_by: actor })
          })
          if (!executeResponse.ok) {
            throw new Error(await executeResponse.text())
          }
          // Download SEPA XML
          const sepaResponse = await fetch(`/api/v1/finance/payment-runs/${data.id}/sepa-xml`)
          if (sepaResponse.ok) {
            const blob = await sepaResponse.blob()
            const url = window.URL.createObjectURL(blob)
            const a = document.createElement('a')
            a.href = url
            a.download = `SEPA_${data.laufNummer || data.run_number || data.id}.xml`
            document.body.appendChild(a)
            a.click()
            document.body.removeChild(a)
            window.URL.revokeObjectURL(url)
            toast({
              title: t('crud.messages.sepaExportSuccess'),
              description: t('crud.messages.sepaFileDownloaded')
            })
          } else {
            throw new Error(await sepaResponse.text())
          }
        } catch (error: any) {
          toast({
            variant: 'destructive',
            title: t('crud.messages.sepaExportError'),
            description: error.message
          })
        }
      }
    },
    {
      key: 'checkReturns',
      label: t('crud.actions.checkReturns'),
      type: 'secondary',
      onClick: async (data: any) => {
        if (!data.id) {
          toast({
            variant: 'destructive',
            title: t('crud.messages.validationError'),
            description: t('crud.messages.savePaymentRunFirst')
          })
          return
        }
        try {
          const res = await apiClient.get<any>(`/api/v1/finance/payment-runs/${data.id}`)
          const run = res.data
          const returnedCount = (run?.payments ?? []).filter((p: any) => p.status === 'returned').length
          if (returnedCount > 0) {
            toast({
              variant: 'destructive',
              title: t('crud.messages.returnsFound', { count: returnedCount }),
              description: t('crud.messages.returnsNeedProcessing')
            })
          } else {
            toast({
              title: t('crud.messages.noReturns'),
              description: t('crud.messages.allPaymentsSuccessful')
            })
          }
        } catch (error: any) {
          toast({
            variant: 'destructive',
            title: t('crud.messages.loadDataError'),
            description: error.response?.data?.detail || error.message
          })
        }
      }
    }
  ],
  api: {
    baseUrl: '/api/v1/finance/payment-runs',
    endpoints: {
      list: '/api/v1/finance/payment-runs',
      get: '/api/v1/finance/payment-runs/{id}',
      create: '/api/v1/finance/payment-runs',
      update: '/api/v1/finance/payment-runs/{id}',
      delete: '/api/v1/finance/payment-runs/{id}'
    }
  } as any,
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

  const updateZahlung = async (index: number, field: string, value: any) => {
    const newData = [..._data]
    
    // Format IBAN if field is iban
    if (field === 'iban' && value) {
      const normalized = value.replace(/\s/g, '').replace(/-/g, '').toUpperCase()
      const formatted = formatIBAN(normalized)
      newData[index] = { ...newData[index], [field]: formatted }
      
      // Auto-lookup IBAN when it changes and seems complete
      if (normalized.length >= 15 && normalized.length <= 34 && validateIBAN(normalized)) {
        // Debounce IBAN lookup
        setTimeout(async () => {
          try {
            const result = await lookupIBAN(normalized)
            if (result.valid && result.bic) {
              const updatedData = [..._data]
              updatedData[index] = {
                ...updatedData[index],
                iban: formatted,
                bic: result.bic || updatedData[index].bic
              }
              onChange(updatedData)
              toast.success(t('crud.messages.ibanLookupSuccess', {
                defaultValue: 'BIC automatisch ausgefüllt',
                bankName: result.bank_name || ''
              }))
            }
          } catch (error) {
            // Silent error for auto-lookup
          }
        }, 1000)
      }
    } else {
      newData[index] = { ...newData[index], [field]: value }
    }
    
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
  const [formData, setFormData] = useState<any>({})
  const [roleFocus, setRoleFocus] = useState<FinanceRoleFocus>('all')
  const currentActor = localStorage.getItem('userEmail') || localStorage.getItem('username') || 'api'
  const entityType = 'paymentRun'
  const entityTypeLabel = getEntityTypeLabel(t, entityType, 'Zahlungslauf Kreditoren')
  const zahlungslaufConfig = createZahlungslaufConfig(t, entityTypeLabel)

  const { data, loading, saveData, updateData } = useMaskData({
    apiUrl: zahlungslaufConfig.api.baseUrl,
    id: 'new',
    transformResponse: (response: any) => {
      // Transform API response to match frontend format
      if (response.data) {
        return {
          ...response.data,
          laufNummer: response.data.run_number,
          ausfuehrungsDatum: response.data.execution_date,
          gesamtBetrag: response.data.total_amount,
          anzahlZahlungen: response.data.payment_count,
          status: response.data.status,
          auftraggeberName: response.data.initiator_name,
          auftraggeberIban: response.data.initiator_iban,
          auftraggeberBic: response.data.initiator_bic,
          zahlungen: response.data.payments || [],
          freigegebenAm: response.data.approved_at,
          freigegebenDurch: response.data.approved_by,
          ausgefuehrtAm: response.data.executed_at,
          notizen: response.data.notes,
          approval_status: response.data.approval_status,
          approval_can_execute: response.data.approval_can_execute,
          approval_override_resolution: response.data.approval_override_resolution,
          approval_explainability: response.data.approval_explainability
        }
      }
      return response
    }
  })

  const validate = (formData: any) => validateFields(getFieldsFromMaskConfig(zahlungslaufConfig), formData ?? {})
  const showValidationToast = (errors: Record<string, string>) => {
    toast.error(`${Object.keys(errors).length} Feld(er) muessen korrigiert werden.`)
  }

  // IBAN Lookup for Auftraggeber-IBAN
  const handleAuftraggeberIbanChange = async (iban: string) => {
    const normalized = iban.replace(/\s/g, '').replace(/-/g, '').toUpperCase()
    if (normalized.length >= 15 && normalized.length <= 34 && validateIBAN(normalized)) {
      try {
        const result = await lookupIBAN(normalized)
        if (result.valid && result.bic) {
          const updatedData = { ...formData, ...data }
          updatedData.auftraggeberIban = formatIBAN(normalized)
          if (result.bic && !updatedData.auftraggeberBic) {
            updatedData.auftraggeberBic = result.bic
          }
          setFormData(updatedData)
          updateData?.(updatedData)
          toast.success(t('crud.messages.ibanLookupSuccess', {
            defaultValue: 'BIC automatisch ausgefüllt',
            bankName: result.bank_name || 'Bank'
          }))
        }
      } catch (error) {
        // Silent error for auto-lookup
      }
    }
  }

  // Handle form data changes
  const handleFormChange = (newData: any) => {
    setFormData(newData)
    setIsDirty(true)
    
    // Auto-lookup Auftraggeber-IBAN
    if (newData?.auftraggeberIban) {
      const timer = setTimeout(() => {
        handleAuftraggeberIbanChange(newData.auftraggeberIban)
      }, 1000)
      return () => clearTimeout(timer)
    }
  }

  const { handleAction, loadingActionKey } = useMaskActions(async (action: string, formData: any) => {
    if (action === 'add-payment') {
      // Neue Zahlung hinzufügen wird in der Tabelle behandelt
      // Dieser Button ist redundant, da die Tabelle ihren eigenen Button hat
      return
    } else if (action === 'validate') {
      const errors = validate(formData)
      if (Object.keys(errors).length === 0) {
        toast({
          title: t('crud.messages.validationSuccess'),
          description: t('crud.messages.allDataCorrect'),
        })
      } else {
        showValidationToast(errors)
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
      window.open(`/api/v1/finance/payment-runs/${formData.id}/sepa-xml`, '_blank')
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
        const response = await fetch(`/api/v1/finance/payment-runs/${formData.id}/approve`, {
          method: 'POST',
          headers: {
            'Content-Type': 'application/json',
            'Authorization': `Bearer ${localStorage.getItem('token')}`,
          },
          body: JSON.stringify({ approved_by: currentActor }),
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
      const errors = validate(formData)
      if (Object.keys(errors).length > 0) {
        showValidationToast(errors)
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
      if (formData.approval_status !== 'executed') {
        toast({
          variant: 'destructive',
          title: t('crud.messages.validationError'),
          description: t('crud.messages.paymentRunMustBeApproved'),
        })
        return
      }
      window.open(`/api/v1/finance/payment-runs/${formData.id}/sepa-xml`, '_blank')
    }
  })

  const handleSave = async (formData: any) => {
    await handleAction('execute', formData)
  }

  const handleCancel = () => {
    navigate('/finance/zahlungslauf-kreditoren')
  }

  const blocker = useUnsavedChanges(isDirty)
  const effectiveData = data || formData
  const approvalDecisionView = buildDecisionView(effectiveData?.approval_explainability)
  const approvalDensityProfile = useApprovalDensityProfile('finance-payment-run', approvalDecisionView)
  const payments = Array.isArray(effectiveData?.zahlungen) ? effectiveData.zahlungen : []
  const totalAmount = Number(effectiveData?.gesamtBetrag || 0)
  const paymentCount = Number(effectiveData?.anzahlZahlungen || payments.length || 0)
  const skontoCount = payments.filter((payment: any) => payment.skontoGenutzt && Number(payment.skontoBetrag || 0) > 0).length
  const operationalStatus = normalizeOperationalStatus(
    effectiveData?.status === 'executed'
      ? 'abgeschlossen'
      : effectiveData?.approval_can_execute
        ? 'wartet_auf_mensch'
        : paymentCount > 0
          ? 'in_pruefung'
          : 'offen',
  )
  const contextSections = [
    {
      title: 'Zahlungslage',
      items: [
        { label: 'Laufnummer', value: effectiveData?.laufNummer || effectiveData?.run_number || 'Noch kein Lauf' },
        { label: 'Zahlungen', value: `${paymentCount}` },
        { label: 'Ausfuehrung', value: effectiveData?.ausfuehrungsDatum || '-' },
      ],
    },
    {
      title: 'Governance',
      items: [
        { label: 'Approval-Status', value: effectiveData?.approval_status || effectiveData?.status || 'draft' },
        { label: 'Skonto genutzt', value: `${skontoCount}` },
        { label: 'Naechste Aktion', value: effectiveData?.approval_can_execute ? 'SEPA exportieren oder Lauf ausfuehren' : paymentCount > 0 ? 'Freigabe und Pruefung abschliessen' : 'Zahlungen erfassen' },
      ],
    },
  ]
  const timelineItems = [
    {
      label: paymentCount > 0 ? 'Zahlungen im Lauf vorbereitet' : 'Lauf noch leer',
      detail: paymentCount > 0
        ? `${paymentCount} Zahlungen mit ${new Intl.NumberFormat('de-DE', { style: 'currency', currency: 'EUR', maximumFractionDigits: 0 }).format(totalAmount)} im aktuellen Lauf.`
        : 'Der Zahlungslauf enthaelt noch keine operativen Positionen.',
    },
    {
      label: effectiveData?.approval_can_execute ? 'Freigabe liegt vor' : 'Freigabe noch offen',
      detail: effectiveData?.approval_can_execute
        ? 'Der Lauf kann in die Ausfuehrung oder den SEPA-Export uebergehen.'
        : 'Approval- und Policy-Pruefung halten den Lauf noch vor der Ausfuehrung.',
    },
  ]
  const nextPaymentAction = effectiveData?.approval_can_execute
    ? 'SEPA-Datei erstellen oder Lauf ausfuehren'
    : paymentCount > 0
      ? 'Freigabe und Policy-Pruefung abschliessen'
      : 'Zahlungen in den Lauf aufnehmen'
  const taskItems: UxTaskItem[] = [
    {
      label: 'Zahlungen erfassen',
      done: paymentCount > 0,
      hint: paymentCount > 0 ? `${paymentCount} Zahlung(en) im Lauf` : 'Mindestens eine Kreditorenzahlung aufnehmen.',
    },
    {
      label: 'Bank- und Stammdaten pruefen',
      done: Boolean(effectiveData?.auftraggeberIban || effectiveData?.initiator_iban) && Boolean(effectiveData?.auftraggeberBic || effectiveData?.initiator_bic),
      hint: 'Auftraggeber-IBAN, BIC und Ausfuehrungsdatum muessen plausibel sein.',
    },
    {
      label: 'Freigabe und Policy pruefen',
      done: Boolean(effectiveData?.approval_can_execute),
      hint: effectiveData?.approval_can_execute ? 'Zahlungslauf ist ausfuehrbar.' : 'Freigabe oder Regelpruefung blockiert die Ausfuehrung noch.',
    },
    {
      label: 'SEPA exportieren oder ausfuehren',
      done: effectiveData?.status === 'executed',
      hint: effectiveData?.status === 'executed' ? 'Lauf wurde ausgefuehrt.' : 'Nach Freigabe SEPA-Datei erstellen oder Lauf ausfuehren.',
    },
  ]
  const crudCapabilities = [
    { key: 'create', label: 'Anlegen', available: true, hint: 'Neue Zahlungslaufe koennen erfasst und gespeichert werden.' },
    { key: 'read', label: 'Lesen', available: true, hint: 'Status, Betrag, Zahlungen, Freigabe und Kontext sind sichtbar.' },
    { key: 'update', label: 'Aendern', available: effectiveData?.status !== 'executed', hint: effectiveData?.status === 'executed' ? 'Ausgefuehrte Laeufe nicht direkt aendern.' : 'Entwurf und Pruefstand koennen angepasst werden.' },
    { key: 'delete', label: 'Loeschen/Storno', available: true, hint: 'Fachlich als Storno oder Abbruch behandeln, nicht still entfernen.' },
    { key: 'approve', label: 'Freigeben', available: Boolean(effectiveData?.id), hint: 'Freigabe erfolgt mit verantwortlicher Person und Policy-Status.' },
    { key: 'export', label: 'SEPA Export', available: Boolean(effectiveData?.approval_can_execute), hint: 'Export erst nach Freigabe und Regelpruefung.' },
    { key: 'audit', label: 'Audit', available: true, hint: 'Zahlungspfad und Entscheidung bleiben nachvollziehbar.' },
  ]

  return (
    <>
      <ModuleToolbar backTarget="/finance/zahlungslauf-kreditoren" closeTarget="/finance/zahlungslauf-kreditoren" title={entityTypeLabel} />
      <LeaveConfirmDialog blocker={blocker} onSave={() => handleSave(formData)} title={t('crud.messages.unsavedChanges', { defaultValue: 'Ungespeicherte Änderungen' })} description={t('crud.messages.unsavedChangesDescription', { defaultValue: 'Möchten Sie speichern, verwerfen oder hier bleiben?' })} />
      <div className="mx-4 mt-4 space-y-4">
        <OperationalCaseHeader
          title="Zahlungslauf Kreditoren"
          description="Der Kreditorenlauf wird als FIBU-Operatorraum mit Freigabe-, Skonto- und Ausfuehrungsdruck gefuehrt."
          status={operationalStatus}
          owner="Zahlungsverkehr"
          blocker={!effectiveData?.approval_can_execute && paymentCount > 0 ? 'Der Lauf ist noch nicht freigegeben oder policy-konform ausfuehrbar.' : null}
          nextAction={nextPaymentAction}
          caseLabel="Vorgang: Kreditorenlauf"
          tags={['FIBU', 'SEPA', 'L3']}
        />
        <RoleFocusBar
          roles={financeRoleProfiles}
          value={roleFocus}
          visibleCount={roleFocus === 'all' ? 4 : 1}
          totalCount={4}
          onChange={setRoleFocus}
        />
        <ManagementDecisionPanel
          decision={{
            allowed: Boolean(effectiveData?.approval_can_execute),
            allowedLabel: 'Zahlung ausfuehrbar',
            blockedLabel: 'Zahlung gestoppt',
            summary: effectiveData?.approval_can_execute
              ? 'Der Zahlungslauf ist freigegeben und kann exportiert oder ausgefuehrt werden.'
              : paymentCount > 0
                ? 'Der Zahlungslauf enthaelt Zahlungen, ist aber noch nicht freigegeben oder policy-konform ausfuehrbar.'
                : 'Der Zahlungslauf ist noch leer. Erfasse zuerst die Zahlungen und pruefe danach Freigabe und Bankdaten.',
            blockerCount: effectiveData?.approval_can_execute ? 0 : 1,
            nextFocus: nextPaymentAction,
            template: { label: 'Zahlungslauf pruefen und freigeben', href: '/finance/zahlungslauf-kreditoren' },
          }}
        />
        <div className="grid gap-4 xl:grid-cols-[minmax(0,2fr)_360px]">
          <OperationalTaskPlan items={taskItems} />
          <NextActionPanel action={nextPaymentAction} tone={effectiveData?.approval_can_execute ? 'emerald' : paymentCount > 0 ? 'amber' : 'blue'} />
        </div>
        <div className="grid gap-4 xl:grid-cols-[minmax(0,2fr)_360px]">
          <OperationalTimeline title="Zahlungspfad" items={timelineItems} />
          <OperationalContextPanel title="Zahlungslauf-Kontext" sections={contextSections} />
        </div>
        <CrudCapabilityChecklist capabilities={crudCapabilities} />
      </div>
      {effectiveData?.id && approvalDecisionView !== null ? (
        <ProcessStatusPanel view={approvalDecisionView} className="mb-4 px-4 py-3" densityProfileOverride={approvalDensityProfile}>
          <div className="mt-3 grid gap-3 md:grid-cols-3">
            <div>
              <div className="text-xs uppercase tracking-wide text-current/70">Workflowstatus</div>
              <div className="mt-1 font-medium">{effectiveData.approval_status || effectiveData.status || '-'}</div>
            </div>
            <div>
              <div className="text-xs uppercase tracking-wide text-current/70">Ausfuehrbar</div>
              <div className="mt-1 font-medium">{effectiveData.approval_can_execute ? 'Ja' : 'Nein'}</div>
            </div>
            <div>
              <div className="text-xs uppercase tracking-wide text-current/70">Regel</div>
              <div className="mt-1 font-medium">{effectiveData.approval_override_resolution?.rule_id || '-'}</div>
            </div>
          </div>
        </ProcessStatusPanel>
      ) : null}
      <ObjectPage
        config={zahlungslaufConfig}
        data={effectiveData}
        onChange={handleFormChange}
        onSave={handleSave}
        onCancel={handleCancel}
        onAction={handleAction}
        isLoading={loading}
        loadingActionKey={loadingActionKey}
      />
    </>
  )
}
