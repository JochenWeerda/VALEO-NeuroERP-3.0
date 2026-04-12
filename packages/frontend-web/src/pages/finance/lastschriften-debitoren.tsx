import { useState } from 'react'
import { useNavigate } from 'react-router-dom'
import { useTranslation } from 'react-i18next'
import { ObjectPage } from '@/components/mask-builder'
import { OperationalCaseHeader } from '@/components/workflow/OperationalCaseHeader'
import { OperationalContextPanel } from '@/components/workflow/OperationalContextPanel'
import { OperationalTimeline } from '@/components/workflow/OperationalTimeline'
import { useMaskData, useMaskActions } from '@/components/mask-builder/hooks'
import { MaskConfig } from '@/components/mask-builder/types'
import { getFieldsFromMaskConfig, validateFields } from '@/components/mask-builder/validation'
import { getEntityTypeLabel } from '@/features/crud/utils/i18n-helpers'
import { lookupIBAN, formatIBAN, validateIBAN } from '@/lib/utils/iban-validator'
import { toast } from '@/hooks/use-toast'
import { apiClient } from '@/lib/api-client'
import { ModuleToolbar } from '@/components/navigation/ModuleToolbar'
import { LeaveConfirmDialog } from '@/components/LeaveConfirmDialog'
import { useUnsavedChanges } from '@/hooks/useUnsavedChanges'
import { Card } from '@/components/ui/card'
import { buildDecisionView } from '@/policy/decision-view'
import { ProcessStatusPanel } from '@/components/workflow/ProcessStatusPanel'
import { useApprovalDensityProfile } from '@/features/workflow/useApprovalDensityProfile'
import { normalizeOperationalStatus } from '@/lib/operational-status'

const createLastschriftenConfig = (t: any, entityTypeLabel: string): MaskConfig => ({
  title: entityTypeLabel,
  subtitle: t('crud.fields.collectSepaDirectDebits'),
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
          placeholder: t('crud.tooltips.placeholders.directDebitRunNumber'),
        },
        {
          name: 'ausfuehrungsDatum',
          label: t('crud.fields.executionDate'),
          type: 'date',
          required: true,
        },
        {
          name: 'status',
          label: t('crud.fields.status'),
          type: 'select',
          required: true,
          options: [
            { value: 'entwurf', label: t('status.draft') },
            { value: 'zur_freigabe', label: t('finance.apInvoices.pendingApproval', { defaultValue: 'Zur Freigabe' }) },
            { value: 'freigegeben', label: t('status.approved') },
            { value: 'ausgefuehrt', label: t('crud.fields.executed') },
            { value: 'storniert', label: t('crud.fields.cancelled') },
          ],
        },
        {
          name: 'gesamtBetrag',
          label: t('crud.fields.totalAmount'),
          type: 'number',
          readonly: true,
          step: 0.01,
        },
        {
          name: 'anzahlLastschriften',
          label: t('crud.fields.numberOfDirectDebits'),
          type: 'number',
          readonly: true,
        },
      ],
      layout: 'grid',
      columns: 2,
    },
    {
      key: 'creditor',
      label: t('crud.fields.creditorInformation'),
      fields: [
        {
          name: 'creditorId',
          label: t('crud.fields.creditorId'),
          type: 'text',
          required: true,
          placeholder: t('crud.tooltips.placeholders.creditorId'),
        },
        {
          name: 'auftraggeberName',
          label: t('crud.fields.originatorName'),
          type: 'text',
          required: true,
          placeholder: t('crud.tooltips.placeholders.companyName'),
        },
        {
          name: 'auftraggeberIban',
          label: t('crud.fields.originatorIban'),
          type: 'text',
          required: true,
          pattern: '^[A-Z]{2}\\d{2}[A-Z0-9]{11,30}$',
          placeholder: t('crud.tooltips.placeholders.iban'),
        },
      ],
    },
    {
      key: 'lastschriften',
      label: t('crud.fields.directDebits'),
      fields: [],
    } as any,
    {
      key: 'lastschriften_custom',
      label: '',
      fields: [],
      customRender: (_data: any, onChange: (_data: any) => void) => (
        <LastschriftenTable
          data={_data.lastschriften || []}
          onChange={(lastschriften) => {
            const gesamtBetrag = lastschriften.reduce((sum: number, l: any) => sum + (l.betrag || 0), 0)
            onChange({
              ..._data,
              lastschriften,
              gesamtBetrag,
              anzahlLastschriften: lastschriften.length,
            })
          }}
        />
      ),
    },
    {
      key: 'freigabe',
      label: t('crud.fields.approvalAndExecution'),
      fields: [
        {
          name: 'freigegebenAm',
          label: t('crud.fields.approvedOn'),
          type: 'date',
          readonly: true,
        },
        {
          name: 'freigegebenDurch',
          label: t('crud.fields.approvedBy'),
          type: 'text',
          readonly: true,
        },
        {
          name: 'ausgefuehrtAm',
          label: t('crud.fields.executedOn'),
          type: 'date',
          readonly: true,
        },
      ],
      layout: 'grid',
      columns: 2,
    },
    {
      key: 'notizen',
      label: t('crud.fields.notes'),
      fields: [
        {
          name: 'notizen',
          label: t('crud.fields.internalNotes'),
          type: 'textarea',
          placeholder: t('crud.tooltips.placeholders.directDebitRunNotes'),
        },
      ],
    },
  ],
  actions: [
    { key: 'add-direct-debit', label: t('crud.actions.addDirectDebit'), type: 'secondary' },
    { key: 'validate-mandates', label: t('crud.actions.validateMandates'), type: 'secondary' },
    { key: 'preview', label: t('crud.actions.sepaPreview'), type: 'secondary' },
    { key: 'approve', label: t('crud.actions.approve'), type: 'primary' },
    { key: 'execute', label: t('crud.actions.execute'), type: 'primary' },
    { key: 'export', label: t('crud.actions.sepaExport'), type: 'secondary' },
  ],
  api: {
    baseUrl: '/api/v1/finance/direct-debits',
    endpoints: {
      list: '/api/v1/finance/direct-debits',
      get: '/api/v1/finance/direct-debits/{id}',
      create: '/api/v1/finance/direct-debits',
      update: '/api/v1/finance/direct-debits/{id}',
      delete: '/api/v1/finance/direct-debits/{id}',
    },
  } as any,
  permissions: ['fibu.read', 'fibu.write', 'fibu.admin'],
})

function LastschriftenTable({ data: _data, onChange }: { data: any[]; onChange: (_data: any[]) => void }) {
  const { t } = useTranslation()

  const addLastschrift = () => {
    onChange([
      ..._data,
      {
        debitorId: '',
        debitorName: '',
        iban: '',
        bic: '',
        betrag: 0,
        mandatReferenz: '',
        mandatDatum: '',
        verwendungszweck: '',
        sequenzTyp: 'FRST',
        opReferenz: '',
      },
    ])
  }

  const updateLastschrift = async (index: number, field: string, value: any) => {
    const newData = [..._data]

    if (field === 'iban' && value) {
      const normalized = value.replace(/\s/g, '').replace(/-/g, '').toUpperCase()
      const formatted = formatIBAN(normalized)
      newData[index] = { ...newData[index], [field]: formatted }

      if (normalized.length >= 15 && normalized.length <= 34 && validateIBAN(normalized)) {
        setTimeout(async () => {
          try {
            const result = await lookupIBAN(normalized)
            if (result.valid && result.bic) {
              const updatedData = [..._data]
              updatedData[index] = {
                ...updatedData[index],
                iban: formatted,
                bic: result.bic || updatedData[index].bic,
              }
              onChange(updatedData)
              toast.success(
                t('crud.messages.ibanLookupSuccess', {
                  defaultValue: 'BIC automatisch ausgefuellt',
                  bankName: result.bank_name || '',
                }),
              )
            }
          } catch (error) {
            console.warn('IBAN lookup failed:', error)
          }
        }, 1000)
      }
    } else {
      newData[index] = { ...newData[index], [field]: value }
    }

    onChange(newData)
  }

  const removeLastschrift = (index: number) => {
    onChange(_data.filter((_, i) => i !== index))
  }

  return (
    <div className="space-y-4">
      <div className="flex justify-between items-center">
        <h3 className="text-lg font-semibold">{t('crud.fields.directDebits')}</h3>
        <button onClick={addLastschrift} className="px-4 py-2 bg-blue-600 text-white rounded hover:bg-blue-700">
          + {t('crud.actions.addDirectDebit')}
        </button>
      </div>

      <div className="overflow-x-auto">
        <table className="min-w-full border border-gray-300">
          <thead className="bg-gray-50">
            <tr>
              <th className="px-4 py-2 border">{t('crud.entities.debtor')}</th>
              <th className="px-4 py-2 border">{t('crud.fields.iban')}</th>
              <th className="px-4 py-2 border">{t('crud.fields.amount')}</th>
              <th className="px-4 py-2 border">{t('crud.fields.mandate')}</th>
              <th className="px-4 py-2 border">{t('crud.fields.sequence')}</th>
              <th className="px-4 py-2 border">{t('crud.fields.purpose')}</th>
              <th className="px-4 py-2 border">{t('crud.fields.opReference')}</th>
              <th className="px-4 py-2 border">{t('crud.actions.delete')}</th>
            </tr>
          </thead>
          <tbody>
            {_data.map((lastschrift, index) => (
              <tr key={index} className="border">
                <td className="px-4 py-2 border">
                  <div>
                    <input
                      type="text"
                      value={lastschrift.debitorId}
                      onChange={(e) => updateLastschrift(index, 'debitorId', e.target.value)}
                      className="w-full p-1 border rounded text-sm mb-1"
                      placeholder={t('crud.tooltips.placeholders.debtorNumber')}
                    />
                    <input
                      type="text"
                      value={lastschrift.debitorName}
                      onChange={(e) => updateLastschrift(index, 'debitorName', e.target.value)}
                      className="w-full p-1 border rounded text-sm"
                      placeholder={t('crud.fields.name')}
                    />
                  </div>
                </td>
                <td className="px-4 py-2 border">
                  <div>
                    <input
                      type="text"
                      value={lastschrift.iban}
                      onChange={(e) => updateLastschrift(index, 'iban', e.target.value)}
                      className="w-full p-1 border rounded text-sm mb-1"
                      placeholder={t('crud.fields.iban')}
                    />
                    <input
                      type="text"
                      value={lastschrift.bic || ''}
                      onChange={(e) => updateLastschrift(index, 'bic', e.target.value)}
                      className="w-full p-1 border rounded text-sm"
                      placeholder={t('crud.tooltips.placeholders.bicOptional')}
                    />
                  </div>
                </td>
                <td className="px-4 py-2 border">
                  <input
                    type="number"
                    step="0.01"
                    value={lastschrift.betrag}
                    onChange={(e) => updateLastschrift(index, 'betrag', parseFloat(e.target.value) || 0)}
                    className="w-full p-1 border rounded"
                  />
                </td>
                <td className="px-4 py-2 border">
                  <div>
                    <input
                      type="text"
                      value={lastschrift.mandatReferenz}
                      onChange={(e) => updateLastschrift(index, 'mandatReferenz', e.target.value)}
                      className="w-full p-1 border rounded text-sm mb-1"
                      placeholder={t('crud.tooltips.placeholders.mandateReference')}
                    />
                    <input
                      type="date"
                      value={lastschrift.mandatDatum}
                      onChange={(e) => updateLastschrift(index, 'mandatDatum', e.target.value)}
                      className="w-full p-1 border rounded text-sm"
                    />
                  </div>
                </td>
                <td className="px-4 py-2 border">
                  <select
                    value={lastschrift.sequenzTyp}
                    onChange={(e) => updateLastschrift(index, 'sequenzTyp', e.target.value)}
                    className="w-full p-1 border rounded"
                  >
                    <option value="FRST">{t('crud.fields.sequenceFRST')}</option>
                    <option value="RCUR">{t('crud.fields.sequenceRCUR')}</option>
                    <option value="FNAL">{t('crud.fields.sequenceFNAL')}</option>
                    <option value="OOFF">{t('crud.fields.sequenceOOFF')}</option>
                  </select>
                </td>
                <td className="px-4 py-2 border">
                  <input
                    type="text"
                    value={lastschrift.verwendungszweck}
                    onChange={(e) => updateLastschrift(index, 'verwendungszweck', e.target.value)}
                    className="w-full p-1 border rounded"
                    placeholder={t('crud.tooltips.placeholders.invoiceNumber')}
                  />
                </td>
                <td className="px-4 py-2 border">
                  <input
                    type="text"
                    value={lastschrift.opReferenz || ''}
                    onChange={(e) => updateLastschrift(index, 'opReferenz', e.target.value)}
                    className="w-full p-1 border rounded text-sm"
                    placeholder={t('crud.tooltips.placeholders.opReference')}
                  />
                </td>
                <td className="px-4 py-2 border">
                  <button onClick={() => removeLastschrift(index)} className="px-2 py-1 bg-red-600 text-white rounded hover:bg-red-700">
                    x
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

export default function LastschriftenDebitorenPage(): JSX.Element {
  const { t } = useTranslation()
  const navigate = useNavigate()
  const [isDirty, setIsDirty] = useState(false)
  const [formData, setFormData] = useState<any>({})
  const [actionLoadingKey, setActionLoadingKey] = useState<string | null>(null)
  const entityType = 'directDebit'
  const entityTypeLabel = getEntityTypeLabel(t, entityType, 'Lastschriften Debitoren')
  const lastschriftenConfig = createLastschriftenConfig(t, entityTypeLabel)

  const { data, loading, saveData, setData } = useMaskData({
    apiUrl: lastschriftenConfig.api.baseUrl,
    id: 'new',
  })

  const initialFormData = {
    laufNummer: '',
    ausfuehrungsDatum: new Date().toISOString().slice(0, 10),
    gesamtBetrag: 0,
    anzahlLastschriften: 0,
    status: 'entwurf',
    approval_status: 'draft',
    approval_can_execute: false,
    approval_override_resolution: null,
    approval_explainability: null,
    freigegebenAm: '',
    freigegebenDurch: '',
    ausgefuehrtAm: '',
    creditorId: '',
    auftraggeberName: '',
    auftraggeberIban: '',
    lastschriften: [],
    notizen: '',
  }
  const safeFormData = { ...initialFormData, ...(data ?? formData ?? {}) }
  const approvalDecisionView = buildDecisionView(safeFormData.approval_explainability)
  const approvalDensityProfile = useApprovalDensityProfile('finance-direct-debit', approvalDecisionView)
  const directDebits = Array.isArray(safeFormData.lastschriften) ? safeFormData.lastschriften : []
  const debitCount = Number(safeFormData.anzahlLastschriften || directDebits.length || 0)
  const totalAmount = Number(safeFormData.gesamtBetrag || 0)
  const missingMandates = directDebits.filter((entry: any) => !entry.mandatReferenz || !entry.mandatDatum).length
  const operationalStatus = normalizeOperationalStatus(
    safeFormData.status === 'ausgefuehrt'
      ? 'abgeschlossen'
      : missingMandates > 0
        ? 'wartet_auf_mensch'
        : safeFormData.approval_can_execute
          ? 'in_pruefung'
          : debitCount > 0
            ? 'teilweise'
            : 'offen',
  )
  const contextSections = [
    {
      title: 'Debitorenlauf',
      items: [
        { label: 'Laufnummer', value: safeFormData.laufNummer || 'Noch kein Lauf' },
        { label: 'Lastschriften', value: `${debitCount}` },
        { label: 'Ausfuehrung', value: safeFormData.ausfuehrungsDatum || '-' },
      ],
    },
    {
      title: 'Mandatslage',
      items: [
        { label: 'Fehlende Mandate', value: `${missingMandates}` },
        { label: 'Approval-Status', value: safeFormData.approval_status || safeFormData.status || 'draft' },
        { label: 'Naechste Aktion', value: missingMandates > 0 ? 'Mandate vervollstaendigen' : safeFormData.approval_can_execute ? 'SEPA-Export oder Ausfuehrung starten' : 'Freigabe vorbereiten' },
      ],
    },
  ]
  const timelineItems = [
    {
      label: debitCount > 0 ? 'Lastschriftlauf aufgebaut' : 'Kein Debitorenlauf vorbereitet',
      detail: debitCount > 0
        ? `${debitCount} Debitoren mit ${new Intl.NumberFormat('de-DE', { style: 'currency', currency: 'EUR', maximumFractionDigits: 0 }).format(totalAmount)} im aktuellen Lauf.`
        : 'Es sind noch keine Lastschriften fuer den aktuellen Lauf vorhanden.',
    },
    {
      label: missingMandates > 0 ? 'Mandatsluecken erkannt' : 'Mandate konsistent',
      detail: missingMandates > 0
        ? `${missingMandates} Eintraege blockieren Freigabe oder Ausfuehrung wegen fehlender Mandatsdaten.`
        : 'Mandats- und Debitorenlage erlaubt den naechsten Freigabeschritt.',
    },
  ]

  const validate = (currentFormData: any) => validateFields(getFieldsFromMaskConfig(lastschriftenConfig), currentFormData ?? {})
  const showValidationToast = (errors: Record<string, string>) => {
    toast({ variant: 'destructive', title: t('crud.messages.validationError'), description: `${Object.keys(errors).length} Feld(er) muessen korrigiert werden.` })
  }

  const handleFormChange = (newData: any) => {
    setFormData(newData)
    setIsDirty(true)

    const auftraggeberIban = newData?.auftraggeberIban
    if (auftraggeberIban && auftraggeberIban.replace(/\s/g, '').length >= 15) {
      const normalized = auftraggeberIban.replace(/\s/g, '').replace(/-/g, '').toUpperCase()
      if (normalized.length >= 15 && normalized.length <= 34 && validateIBAN(normalized)) {
        setTimeout(async () => {
          try {
            const result = await lookupIBAN(normalized)
            if (result.valid && result.bic) {
              const updatedData = { ...newData, auftraggeberIban: formatIBAN(normalized) }
              setFormData(updatedData)
              setData(updatedData)
              toast.success(
                t('crud.messages.ibanLookupSuccess', {
                  defaultValue: 'BIC automatisch ausgefuellt',
                  bankName: result.bank_name || '',
                }),
              )
            }
          } catch (error) {
            console.warn('IBAN lookup failed:', error)
          }
        }, 1000)
      }
    }
  }

  const { handleAction } = useMaskActions(async (action: string, currentFormData: any) => {
    if (action === 'add-direct-debit') {
      toast({ title: 'Hinweis', description: 'Lastschriften werden direkt in der Tabelle hinzugefuegt.' })
      return
    }

    if (action === 'validate-mandates') {
      const lastschriften: any[] = currentFormData?.lastschriften ?? []
      const errors: string[] = []
      lastschriften.forEach((ls: any, idx: number) => {
        if (!ls.iban) errors.push(`Zeile ${idx + 1}: IBAN fehlt`)
        if (!ls.bic) errors.push(`Zeile ${idx + 1}: BIC fehlt`)
        if (!ls.mandatReferenz) errors.push(`Zeile ${idx + 1}: Mandat-Referenz fehlt`)
        if (!ls.mandatDatum) errors.push(`Zeile ${idx + 1}: Mandat-Datum fehlt`)
        if (!ls.debitorId) errors.push(`Zeile ${idx + 1}: Debitor fehlt`)
      })
      if (lastschriften.length === 0) {
        toast({ title: 'Mandatspruefung', description: 'Keine Lastschriften vorhanden.', variant: 'destructive' })
      } else if (errors.length > 0) {
        toast({ title: `Mandatspruefung: ${errors.length} Fehler`, description: errors.slice(0, 3).join(' | '), variant: 'destructive' })
      } else {
        toast({ title: 'Mandatspruefung erfolgreich', description: `${lastschriften.length} Mandate geprueft - alle vollstaendig.` })
      }
      return
    }

    if (action === 'preview') {
      const runId = currentFormData?.id
      if (!runId) {
        toast({ variant: 'destructive', title: t('common.error'), description: t('crud.messages.saveFirst') })
        return
      }
      setActionLoadingKey('preview')
      try {
        const response = await apiClient.get<{
          total_amount: number
          debitor_count: number
          mandate_valid_count: number
          mandate_expired_count: number
          sepa_ready: boolean
        }>(`/api/v1/finance/followup/lastschriften/${runId}/preview`)
        const preview = response.data
        toast({
          title: t('crud.actions.sepaPreview', { defaultValue: 'SEPA-Vorschau' }),
          description: `${preview.debitor_count} Debitoren · ${preview.total_amount.toFixed(2)} € · ${preview.mandate_expired_count} abgelaufene Mandate`,
        })
      } catch (error: any) {
        const msg = error.response?.data?.detail ?? error.message
        toast({ variant: 'destructive', title: t('common.error'), description: msg })
      } finally {
        setActionLoadingKey(null)
      }
      return
    }

    if (action === 'approve') {
      const errors = validate(currentFormData)
      if (Object.keys(errors).length > 0) {
        showValidationToast(errors)
        return
      }

      setActionLoadingKey('approve')
      try {
        const runId = currentFormData?.id
        if (runId) {
          const response = await apiClient.post(`/api/v1/finance/direct-debits/${runId}/approve`, {
            approved_by: currentFormData?.freigegebenDurch ?? 'current-user',
          })
          setData(response.data)
        } else {
          const created = await saveData({ ...currentFormData, status: 'zur_freigabe' })
          const createdId = created?.id
          if (!createdId) {
            throw new Error('Direct debit run could not be created')
          }
          const response = await apiClient.post(`/api/v1/finance/direct-debits/${createdId}/approve`, {
            approved_by: currentFormData?.freigegebenDurch ?? 'current-user',
          })
          setData(response.data)
        }
        setIsDirty(false)
        toast({ title: 'Freigegeben', description: 'Lastschriftlauf wurde freigegeben.' })
      } catch (error: any) {
        const msg = error.response?.data?.detail ?? error.message
        toast({ variant: 'destructive', title: t('common.error'), description: msg })
      } finally {
        setActionLoadingKey(null)
      }
      return
    }

    if (action === 'execute') {
      const errors = validate(currentFormData)
      if (Object.keys(errors).length > 0) {
        showValidationToast(errors)
        return
      }

      setActionLoadingKey('execute')
      try {
        const runId = currentFormData?.id
        if (runId) {
          const response = await apiClient.post(`/api/v1/finance/direct-debits/${runId}/execute`, {})
          setData(response.data)
        } else {
          const created = await saveData({ ...currentFormData, status: 'zur_freigabe' })
          const createdId = created?.id
          if (!createdId) {
            throw new Error('Direct debit run could not be created')
          }
          await apiClient.post(`/api/v1/finance/direct-debits/${createdId}/approve`, {
            approved_by: currentFormData?.freigegebenDurch ?? 'current-user',
          })
          const response = await apiClient.post(`/api/v1/finance/direct-debits/${createdId}/execute`, {})
          setData(response.data)
        }
        toast({ title: t('crud.messages.executed', { defaultValue: 'Zahlungslauf ausgefuehrt' }) })
        setIsDirty(false)
      } catch (error: any) {
        const msg = error.response?.data?.detail ?? error.message
        toast({ variant: 'destructive', title: t('common.error'), description: msg })
      } finally {
        setActionLoadingKey(null)
      }
      return
    }

    if (action === 'export') {
      const runId = currentFormData?.id
      if (!runId) {
        toast({ variant: 'destructive', title: t('common.error'), description: t('crud.messages.saveFirst') })
        return
      }
      setActionLoadingKey('export')
      try {
        const response = await apiClient.post<{ export_id: string; download_url: string | null }>(
          `/api/v1/finance/followup/lastschriften/${runId}/export`,
          { format: 'sepa_xml' },
        )
        const result = response.data
        if (result.download_url) {
          window.open(result.download_url, '_blank')
        } else {
          toast({
            title: t('crud.actions.sepaExport', { defaultValue: 'SEPA-Export gestartet' }),
            description: `Export-ID: ${result.export_id}`,
          })
        }
      } catch (error: any) {
        const msg = error.response?.data?.detail ?? error.message
        toast({ variant: 'destructive', title: t('common.error'), description: msg })
      } finally {
        setActionLoadingKey(null)
      }
    }
  })

  const handleSave = async (currentFormData: any) => {
    const errors = validate(currentFormData)
    if (Object.keys(errors).length > 0) {
      showValidationToast(errors)
      return
    }

    await saveData({ ...currentFormData, status: currentFormData?.status ?? 'entwurf' })
    setIsDirty(false)
  }

  const handleCancel = () => {
    navigate('/finance/lastschriften-debitoren')
  }

  const blocker = useUnsavedChanges(isDirty)

  return (
    <>
      <ModuleToolbar backTarget="/finance/lastschriften-debitoren" closeTarget="/finance/lastschriften-debitoren" title={entityTypeLabel} />
      <LeaveConfirmDialog blocker={blocker} onSave={() => handleSave(safeFormData)} title={t('crud.messages.unsavedChanges', { defaultValue: 'Ungespeicherte Aenderungen' })} description={t('crud.messages.unsavedChangesDescription', { defaultValue: 'Moechten Sie speichern, verwerfen oder hier bleiben?' })} />
      <div className="mx-4 mt-4 space-y-4">
        <OperationalCaseHeader
          title="Lastschriften Debitoren"
          description="Der Debitorenlauf wird als Mandats-, Freigabe- und Ausfuehrungsfall komprimiert dargestellt."
          status={operationalStatus}
          owner="Debitorenbuchhaltung"
          blocker={missingMandates > 0 ? `${missingMandates} Lastschriften haben unvollstaendige Mandatsdaten.` : null}
          nextAction={missingMandates > 0 ? 'Mandatsdaten vervollstaendigen und erneut pruefen' : safeFormData.approval_can_execute ? 'SEPA-Datei exportieren oder Lastschriften ausfuehren' : 'Freigabe vorbereiten'}
          caseLabel="Vorgang: Debitorenlauf"
          tags={['FIBU', 'SEPA', 'Mandat']}
        />
        <div className="grid gap-4 xl:grid-cols-[minmax(0,2fr)_360px]">
          <OperationalTimeline title="Lastschriftverlauf" items={timelineItems} />
          <OperationalContextPanel title="Lastschrift-Kontext" sections={contextSections} />
        </div>
      </div>
      {approvalDecisionView !== null ? (
        <ProcessStatusPanel view={approvalDecisionView} className="mx-4 mt-4 px-4 py-3" densityProfileOverride={approvalDensityProfile}>
          <div className="mt-3 grid gap-3 md:grid-cols-3">
            <div className="rounded-md border bg-white/50 p-3">
              <div className="text-xs uppercase tracking-wide text-current/70">Workflowstatus</div>
              <div className="mt-1 font-medium">{safeFormData.approval_status || '-'}</div>
            </div>
            <div className="rounded-md border bg-white/50 p-3">
              <div className="text-xs uppercase tracking-wide text-current/70">Ausfuehrbar</div>
              <div className="mt-1 font-medium">{safeFormData.approval_can_execute ? 'Ja' : 'Nein'}</div>
            </div>
            <div className="rounded-md border bg-white/50 p-3">
              <div className="text-xs uppercase tracking-wide text-current/70">Regel</div>
              <div className="mt-1 font-medium">{safeFormData.approval_override_resolution?.rule_id || '-'}</div>
            </div>
          </div>
        </ProcessStatusPanel>
      ) : null}
      <ObjectPage
        config={lastschriftenConfig}
        data={safeFormData}
        onChange={handleFormChange}
        onSave={handleSave}
        onCancel={handleCancel}
        isLoading={loading}
        onAction={(key, fd) => handleAction(key, fd ?? safeFormData)}
        loadingActionKey={actionLoadingKey}
      />
    </>
  )
}
