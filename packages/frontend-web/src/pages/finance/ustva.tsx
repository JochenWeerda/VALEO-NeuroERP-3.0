import { useState } from 'react'
import { useNavigate, useSearchParams } from '@/app/routing/typed-router'
import { useTranslation } from 'react-i18next'
import type { TFunction } from 'i18next'
import { ObjectPage } from '@/components/mask-builder'
import { useMaskData, useMaskActions } from '@/components/mask-builder/hooks'
import { MaskConfig } from '@/components/mask-builder/types'
import { getFieldsFromMaskConfig, validateFields } from '@/components/mask-builder/validation'
import { toast } from '@/hooks/use-toast'
import { apiClient, getAxiosErrorMessage } from '@/lib/api-client'
import { getEntityTypeLabel } from '@/features/crud/utils/i18n-helpers'
import { buildDecisionView } from '@/policy/decision-view'
import { ProcessStatusPanel } from '@/components/workflow/ProcessStatusPanel'
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
import { useApprovalDensityProfile } from '@/features/workflow/useApprovalDensityProfile'
import { useFibuCockpit } from '@/lib/api/fibu'
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card'
import { normalizeOperationalStatus } from '@/lib/operational-status'

type VatRoleFocus = 'all' | 'accounting' | 'tax-advisor' | 'controller' | 'management'

const vatRoleProfiles: Array<{ id: VatRoleFocus; label: string; description: string }> = [
  { id: 'all', label: 'Alle', description: 'Gesamtbild fuer Berechnung, Freigabe und ELSTER-Einreichung.' },
  { id: 'accounting', label: 'FIBU', description: 'Umsaetze, Vorsteuer, Abweichungen und Buchungsgrundlage pruefen.' },
  { id: 'tax-advisor', label: 'Steuerbuero', description: 'Meldefaehigkeit, ELSTER-Export und Nachweise pruefen.' },
  { id: 'controller', label: 'Controlling', description: 'Abweichungen, Liquiditaetswirkung und Periodenvergleich einordnen.' },
  { id: 'management', label: 'Leitung', description: 'Abgabestatus, Stopper und Restrisiken entscheiden.' },
]

const createUstvaConfig = (t: TFunction, entityTypeLabel: string): MaskConfig => ({
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
         },
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
    },
    {
      key: 'abweichungen_custom',
      label: '',
      fields: [],
      customRender: (_data: Record<string, unknown>, onChange: (_data: Record<string, unknown>) => void) => (
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
  },
  permissions: ['fibu.read', 'fibu.write', 'fibu.admin']
})

// Abweichungen-Tabelle Komponente
function AbweichungenTable({ data: _data, onChange }: { data: Record<string, unknown>[], onChange: (_data: Record<string, unknown>[]) => void }) {
  const { t } = useTranslation()
  const addAbweichung = () => {
    onChange([..._data, {
      position: '',
      beschreibung: '',
      betrag: 0,
      grund: ''
    }])
  }

  const updateAbweichung = (index: number, field: string, value: unknown) => {
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

function mapVatReturnPayload(payload: Record<string, unknown> | null | undefined): Record<string, unknown> | null | undefined {
  if (!payload || typeof payload !== 'object') {
    return payload
  }
  return {
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
  }
}

export default function UStVAPage(): JSX.Element {
  const { t } = useTranslation()
  const navigate = useNavigate()
  const [searchParams] = useSearchParams()
  const { data: fibuCockpit } = useFibuCockpit()
  const workflowInstanceId = searchParams.get('workflowInstanceId')
  const workflowProcess = searchParams.get('workflowProcess')
  const workflowCase = searchParams.get('workflowCase')
  const [isDirty, setIsDirty] = useState(false)
  const [workspaceData, setWorkspaceData] = useState<Record<string, unknown>>({})
  const [roleFocus, setRoleFocus] = useState<VatRoleFocus>('all')
  const entityType = 'ustva'
  const entityTypeLabel = getEntityTypeLabel(t, entityType, 'Umsatzsteuervoranmeldung')
  const ustvaConfig = createUstvaConfig(t, entityTypeLabel)
  const currentActor = localStorage.getItem('userEmail') || localStorage.getItem('username') || 'api'

  const { data, loading } = useMaskData({
    apiUrl: ustvaConfig.api.baseUrl,
    id: 'new',
    transformResponse: (payload: Record<string, unknown>) => mapVatReturnPayload(payload) ?? payload,
  })

  const validate = (formData: Record<string, unknown>) => validateFields(getFieldsFromMaskConfig(ustvaConfig), formData ?? {})
  const showValidationToast = (errors: Record<string, string>) => {
    toast({ variant: 'destructive', title: t('crud.messages.validationError'), description: `${Object.keys(errors).length} Feld(er) muessen korrigiert werden.` })
  }

  const applyVATReturnResponse = (response: Record<string, unknown> | undefined) => {
    const mapped = mapVatReturnPayload(response)
    if (!mapped) {
      return
    }
    setWorkspaceData(mapped)
  }

  const { handleAction, loadingActionKey } = useMaskActions(async (action: string, formData: Record<string, unknown>) => {
    if (action === 'calculate') {
      try {
        const result = await apiClient.post<Record<string, unknown>>('/api/v1/finance/vat-return/calculate', {
          period: formData?.periode,
        })
        toast({ title: t('crud.messages.calculationCompleted'), description: t('crud.messages.ustvaAmountsRecalculated') })
        applyVATReturnResponse(result as Record<string, unknown>)
      } catch (error: unknown) {
        toast({ variant: 'destructive', title: t('common.error'), description: getAxiosErrorMessage(error) })
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
        const response = await apiClient.post(`/api/v1/finance/vat-return/${formData.id as string}/approve`, {
          approved_by: currentActor,
        })
        applyVATReturnResponse(response as Record<string, unknown>)
        toast({
          title: t('crud.messages.approvalSuccess'),
          description: t('crud.messages.ustvaApproved'),
        })
      } catch (error: unknown) {
        toast({
          variant: 'destructive',
          title: t('crud.messages.networkError'),
          description: getAxiosErrorMessage(error),
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
        const response = await apiClient.post(`/api/v1/finance/vat-return/${formData.id as string}/submit`, {
          submitted_by: currentActor,
        })
        applyVATReturnResponse(response as Record<string, unknown>)
        setIsDirty(false)
        if (workflowInstanceId && workflowProcess) {
          try {
            await apiClient.post(`/api/v1/process/flow-spines/${workflowProcess}/instances/${workflowInstanceId}/transitions`, {
              node_id: 'meldewesen',
              new_status: 'ok',
            })
          } catch { /* best-effort, don't block user */ }
        }
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
      try {
        const res = await apiClient.post<{ url?: string }>('/api/v1/export/list', {
          entity: 'vat_return',
          format: 'xml',
          id: formData.id,
        })
        if (res?.url) window.open(res.url, '_blank')
        toast({ title: t('crud.actions.xmlExport'), description: t('crud.messages.exportCreated', { defaultValue: 'Export erstellt' }) })
      } catch (error: unknown) {
        toast({ variant: 'destructive', title: t('common.error'), description: getAxiosErrorMessage(error) })
      }
    }
  })

  const handleSave = async (formData: Record<string, unknown>) => {
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
  const approvalDensityProfile = useApprovalDensityProfile('finance-vat', approvalDecisionView)
  const operationalStatus = normalizeOperationalStatus(
    effectiveData?.status || (effectiveData?.approval_can_submit ? 'wartet_auf_mensch' : workflowInstanceId ? 'in_pruefung' : 'offen'),
  )
  const operationalBlocker =
    effectiveData?.approval_can_submit === false
      ? 'Die UStVA ist noch nicht abgabefaehig. Freigabe- oder Regelkontext fehlt.'
      : null
  const contextSections = [
    {
      title: 'Meldekontext',
      items: [
        { label: 'Periode', value: effectiveData?.periode || fibuCockpit.tax.latest_period || 'n/a' },
        { label: 'Status', value: effectiveData?.status || 'Entwurf' },
        { label: 'ELSTER-Referenz', value: effectiveData?.elsterReferenz || 'noch nicht vergeben' },
      ],
    },
    {
      title: 'FIBU-Lage',
      items: [
        { label: 'UStVA-Laeufe', value: `${fibuCockpit.tax.vat_return_count}` },
        { label: 'Validiert / Freigegeben', value: `${fibuCockpit.tax.validated_count} / ${fibuCockpit.tax.approved_count}` },
        { label: 'eBilanz / E-Clearing', value: `${fibuCockpit.tax.e_bilanz_ready ? 'bereit' : 'vorbereiten'} / ${fibuCockpit.tax.e_clearing_ready ? 'bereit' : 'offen'}` },
      ],
    },
  ]
  const timelineItems = [
    {
      label: effectiveData?.status === 'submitted' ? 'UStVA eingereicht' : 'UStVA in Bearbeitung',
      detail: effectiveData?.status === 'submitted'
        ? 'Die Meldung hat den fachlichen Uebergang in den Einreichungspfad erreicht.'
        : 'Der Vorgang befindet sich noch in Berechnung, Pruefung oder Freigabe.',
      timestamp: effectiveData?.abgegebenAm || effectiveData?.freigegebenAm || null,
    },
    {
      label: workflowInstanceId ? 'Flow-Spine aktiv' : 'Kein Workflowpfad aktiv',
      detail: workflowInstanceId
        ? `${workflowCase || workflowProcess} fuehrt den Vorgang aktuell mit.`
        : 'Die Maske laeuft ohne expliziten Flow-Spine-Kontext.',
    },
  ]
  const deviations = Array.isArray(effectiveData?.abweichungen) ? effectiveData.abweichungen : []
  const nextVatAction = effectiveData?.approval_can_submit ? 'ELSTER-Einreichung vorbereiten' : 'Abweichungen, Regeln oder Freigabe klaeren'
  const taskItems: UxTaskItem[] = [
    {
      label: 'Periode und Stammdaten pruefen',
      done: Boolean(effectiveData?.periode || fibuCockpit.tax.latest_period) && Boolean(effectiveData?.steuerpflichtiger),
      hint: 'Periode, Meldezeitraum, Steuerpflichtiger und USt-ID muessen stimmen.',
    },
    {
      label: 'Steuerwerte und Abweichungen klaeren',
      done: deviations.length === 0 || deviations.every(item => item.grund),
      hint: deviations.length > 0 ? `${deviations.length} Abweichung(en) mit Begruendung pruefen.` : 'Keine Abweichungen im Arbeitsstand erfasst.',
    },
    {
      label: 'Freigabe und Regelkontext pruefen',
      done: Boolean(effectiveData?.approval_can_submit),
      hint: effectiveData?.approval_can_submit ? 'Meldung ist abgabefaehig.' : 'Freigabe, Regel oder Validierung fehlt noch.',
    },
    {
      label: 'ELSTER-Einreichung oder XML-Export',
      done: effectiveData?.status === 'submitted',
      hint: effectiveData?.status === 'submitted' ? 'Meldung wurde eingereicht.' : 'Nach Freigabe Einreichung oder XML-Export starten.',
    },
  ]
  const crudCapabilities = [
    { key: 'create', label: 'Anlegen', available: true, hint: 'Neue UStVA kann fuer eine Periode erstellt werden.' },
    { key: 'read', label: 'Lesen', available: true, hint: 'Meldekontext, FIBU-Lage, Status und ELSTER-Referenz sind sichtbar.' },
    { key: 'update', label: 'Aendern', available: effectiveData?.status !== 'submitted', hint: effectiveData?.status === 'submitted' ? 'Eingereichte Meldungen nicht direkt aendern.' : 'Entwurf und Pruefstand koennen korrigiert werden.' },
    { key: 'delete', label: 'Loeschen/Storno', available: false, hint: 'Fachlich nur mit Korrektur- oder Stornopfad, nicht als Direktloeschung.' },
    { key: 'approve', label: 'Freigeben', available: Boolean(effectiveData?.id), hint: 'Freigabe erfolgt ueber Workflow-/Policy-Status.' },
    { key: 'export', label: 'XML/ELSTER', available: Boolean(effectiveData?.approval_can_submit), hint: 'Export oder Einreichung erst nach Abgabefaehigkeit.' },
    { key: 'audit', label: 'Audit', available: true, hint: 'Meldeverlauf und Entscheidung bleiben nachvollziehbar.' },
  ]

  return (
    <>
      <div className="space-y-4 px-4 pb-4">
        <OperationalCaseHeader
          title="UStVA-Follow-up"
          description="Der Meldevorgang wird als Freigabe- und Einreichungsfall ueber dem Fachformular gefuehrt."
          status={operationalStatus}
          owner="Steuer / FIBU"
          blocker={operationalBlocker}
          nextAction={nextVatAction}
          caseLabel="Vorgang: Steueranmeldung"
          tags={['FIBU', 'ELSTER']}
        />
        <RoleFocusBar
          roles={vatRoleProfiles}
          value={roleFocus}
          visibleCount={roleFocus === 'all' ? 4 : 1}
          totalCount={4}
          onChange={setRoleFocus}
        />
        <ManagementDecisionPanel
          decision={{
            allowed: Boolean(effectiveData?.approval_can_submit),
            allowedLabel: 'Abgabefaehig',
            blockedLabel: 'Abgabe gestoppt',
            summary: effectiveData?.approval_can_submit
              ? 'Die UStVA ist fachlich freigegeben und kann fuer ELSTER vorbereitet werden.'
              : 'Die UStVA ist noch nicht abgabefaehig. Pruefe Abweichungen, Regelkontext und Freigabe.',
            blockerCount: effectiveData?.approval_can_submit ? 0 : 1,
            nextFocus: nextVatAction,
            template: { label: 'UStVA pruefen und einreichen', href: '/finance/ustva' },
          }}
        />
        <div className="grid gap-4 xl:grid-cols-[minmax(0,2fr)_360px]">
          <OperationalTaskPlan items={taskItems} />
          <NextActionPanel action={nextVatAction} tone={effectiveData?.approval_can_submit ? 'emerald' : deviations.length > 0 ? 'amber' : 'blue'} />
        </div>
        <div className="grid gap-4 xl:grid-cols-[minmax(0,2fr)_360px]">
          <OperationalTimeline title="Meldeverlauf" items={timelineItems} />
          <OperationalContextPanel title="UStVA-Kontext" sections={contextSections} />
        </div>
        <CrudCapabilityChecklist capabilities={crudCapabilities} />
      </div>
      <div className="grid gap-4 px-4 pb-4 md:grid-cols-4">
        <Card>
          <CardHeader className="pb-2"><CardTitle className="text-sm">UStVA-Läufe</CardTitle></CardHeader>
          <CardContent><div className="text-2xl font-semibold">{fibuCockpit.tax.vat_return_count}</div></CardContent>
        </Card>
        <Card>
          <CardHeader className="pb-2"><CardTitle className="text-sm">Validiert / Freigegeben</CardTitle></CardHeader>
          <CardContent><div className="text-2xl font-semibold">{fibuCockpit.tax.validated_count} / {fibuCockpit.tax.approved_count}</div></CardContent>
        </Card>
        <Card>
          <CardHeader className="pb-2"><CardTitle className="text-sm">eBilanz / E-Clearing</CardTitle></CardHeader>
          <CardContent><div className="text-sm font-semibold">{fibuCockpit.tax.e_bilanz_ready ? 'bereit' : 'vorbereiten'} / {fibuCockpit.tax.e_clearing_ready ? 'bereit' : 'offen'}</div></CardContent>
        </Card>
        <Card>
          <CardHeader className="pb-2"><CardTitle className="text-sm">Letzte Periode</CardTitle></CardHeader>
          <CardContent><div className="text-sm font-semibold">{fibuCockpit.tax.latest_period ?? 'n/a'}</div></CardContent>
        </Card>
      </div>
      {workflowInstanceId && (
        <div className="mb-4 rounded-md border border-indigo-500/30 bg-indigo-500/10 px-4 py-2 text-sm text-indigo-200">
          Flow-Spine: {workflowCase || workflowProcess} (Instanz {workflowInstanceId.slice(0, 8)}...)
        </div>
      )}
      {effectiveData?.id && approvalDecisionView !== null ? (
        <ProcessStatusPanel view={approvalDecisionView} className="mb-4 px-4 py-3" densityProfileOverride={approvalDensityProfile}>
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
        loadingActionKey={loadingActionKey}
      />
    </>
  )
}
