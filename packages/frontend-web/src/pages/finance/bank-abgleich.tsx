import { useState } from 'react'
import { useNavigate } from '@/app/routing/typed-router'
import { useTranslation, type TFunction } from 'react-i18next'
import { ObjectPage } from '@/components/mask-builder'
import { useMaskData, useMaskActions } from '@/components/mask-builder/hooks'
import { MaskConfig } from '@/components/mask-builder/types'
import { getFieldsFromMaskConfig, validateFields } from '@/components/mask-builder/validation'
import { toast } from '@/hooks/use-toast'
import { apiClient } from '@/lib/api-client'
import { getEntityTypeLabel } from '@/features/crud/utils/i18n-helpers'
import { useTenant } from '@/hooks/useTenant'
import { OperationalCaseHeader } from '@/components/workflow/OperationalCaseHeader'
import { OperationalContextPanel } from '@/components/workflow/OperationalContextPanel'
import { OperationalTimeline } from '@/components/workflow/OperationalTimeline'
import { normalizeOperationalStatus } from '@/lib/operational-status'

const createBankAbgleichConfig = (t: TFunction, entityTypeLabel: string): MaskConfig => ({
  title: entityTypeLabel,
  subtitle: t('crud.fields.bankReconciliation'),
  type: 'object-page',
  tabs: [
    {
      key: 'import',
      label: t('crud.fields.camtImport'),
      fields: [
        {
          name: 'kontoId',
          label: t('crud.fields.bankAccount'),
          type: 'select',
          required: true,
          options: [
            { value: '1200', label: `1200 - ${  t('crud.fields.bankAccount')  } Deutsche Bank` },
            { value: '1300', label: `1300 - ${  t('crud.fields.bankAccount')  } Commerzbank` },
            { value: '1400', label: `1400 - ${  t('crud.fields.bankAccount')  } Sparkasse` }
          ]
        },
        {
          name: 'periode',
          label: t('crud.fields.period'),
          type: 'text',
          required: true,
          placeholder: t('crud.tooltips.placeholders.period'),
          pattern: '^\\d{4}-\\d{2}$'
         } as Field,
        {
          name: 'camtFile',
          label: t('crud.fields.camtFile'),
          type: 'file',
          accept: '.xml,.camt,.940,.sta,.csv',
          helpText: t('crud.tooltips.fields.camtFile')
        } as Field,
        {
          name: 'abgleichsDatum',
          label: t('crud.fields.reconciliationDate'),
          type: 'date',
          required: true
        }
      ],
      layout: 'grid',
      columns: 2
    },
    {
      key: 'salden',
      label: t('crud.fields.balances'),
      fields: [
        {
          name: 'startSaldo',
          label: t('crud.fields.openingBalance'),
          type: 'number',
          readonly: true,
          step: 0.01,
          helpText: t('crud.tooltips.fields.importedFromCamt')
        },
        {
          name: 'endSaldo',
          label: t('crud.fields.closingBalance'),
          type: 'number',
          readonly: true,
          step: 0.01,
          helpText: t('crud.tooltips.fields.importedFromCamt')
        },
        {
          name: 'gebuchteUmsaetze',
          label: t('crud.fields.bookedTransactions'),
          type: 'number',
          readonly: true,
          step: 0.01,
          helpText: t('crud.tooltips.fields.sumOfImportedTransactions')
        }
      ],
      layout: 'grid',
      columns: 3
    },
    {
      key: 'zuordnung',
      label: t('crud.fields.assignment'),
      fields: []
    } as Field,
    {
      key: 'zuordnung_custom',
      label: '',
      fields: [],
      customRender: (_data: Record<string, unknown>, onChange: (_data: Record<string, unknown>) => void) => (
        <BankZuordnungTable
          data={_data.zuordnungData || []}
          onChange={(zuordnungData) => onChange({ ..._data, zuordnungData })}
        />
      )
    },
    {
      key: 'regeln',
      label: t('crud.fields.rulesAndStatistics'),
      fields: [
        {
          name: 'regelAngewendet',
          label: t('crud.fields.appliedRules'),
          type: 'custom',
          customRender: (value: unknown) => (
            <div className="space-y-2">
              {(value || []).map((regel, index) => (
                <div key={index} className="flex justify-between p-2 bg-gray-50 rounded">
                  <span>{regel.regelName}</span>
                  <span>{regel.zugeordnet}/{regel.treffer} {t('crud.fields.matches')}</span>
                </div>
              ))}
            </div>
          )
        }
      ]
    },
    {
      key: 'import_protokoll',
      label: t('crud.fields.importLog', { defaultValue: 'Import-Protokoll' }),
      fields: [],
      customRender: (_data: Record<string, unknown>) => (
        <BankImportErrorList errors={_data.importErrors || []} />
      )
    } as Field,
    {
      key: 'abgleich',
      label: t('crud.fields.reconciliation'),
      fields: [
        {
          name: 'zugeordnet',
          label: t('crud.fields.assignedTransactions'),
          type: 'number',
          readonly: true
        },
        {
          name: 'nichtZugeordnet',
          label: t('crud.fields.unassignedTransactions'),
          type: 'number',
          readonly: true
        },
        {
          name: 'abgleichsDifferenz',
          label: t('crud.fields.reconciliationDifference'),
          type: 'number',
          readonly: true,
          step: 0.01,
          helpText: t('crud.tooltips.fields.reconciliationMustBeZero')
        },
        {
          name: 'accountingBalance',
          label: t('crud.fields.accountingBalance'),
          type: 'number',
          readonly: true,
          step: 0.01,
          helpText: t('crud.tooltips.fields.accountingBalanceFromLedger')
        }
      ],
      layout: 'grid',
      columns: 3
    }
  ],
  actions: [
    { key: 'import', label: t('crud.actions.camtImport'), type: 'secondary' },
    { key: 'auto-assign', label: t('crud.actions.autoAssign'), type: 'secondary' },
    { key: 'validate', label: t('crud.actions.validate'), type: 'secondary' },
    { key: 'book', label: t('crud.actions.book'), type: 'primary' },
    { key: 'export', label: t('crud.actions.export'), type: 'secondary' }
  ],
  api: {
    baseUrl: '/api/v1/finance/bank-statements',
    endpoints: {
      list: '/api/v1/finance/bank-statements',
      get: '/api/v1/finance/bank-statements/{id}',
      create: '/api/v1/finance/bank-statements',
      update: '/api/v1/finance/bank-statements/{id}',
      delete: '/api/v1/finance/bank-statements/{id}'
    }
  } as Field,
  permissions: ['fibu.read', 'fibu.write']
})

// Bank-Zuordnung Tabelle Komponente
function BankZuordnungTable({ data: _data, onChange }: { data: Record<string, unknown>[], onChange: (_data: Record<string, unknown>[]) => void }) {
  const { t } = useTranslation()
  const updateZuordnung = (index: number, field: string, value: unknown) => {
    const newData = [..._data]
    newData[index] = { ...newData[index], [field]: value }
    onChange(newData)
  }

  const toggleZuordnung = (index: number) => {
    const newData = [..._data]
    newData[index].zugeordnet = !newData[index].zugeordnet
    onChange(newData)
  }

  return (
    <div className="space-y-4">
      <div className="flex justify-between items-center">
        <h3 className="text-lg font-semibold">{t('crud.fields.assignBankTransactions')}</h3>
        <div className="text-sm text-gray-600">
          {t('crud.fields.assignedCount', { assigned: _data.filter(d => d.zugeordnet).length, total: _data.length })}
        </div>
      </div>

      <div className="overflow-x-auto max-h-96">
        <table className="min-w-full border border-gray-300">
          <thead className="bg-gray-50 sticky top-0">
            <tr>
              <th className="px-4 py-2 border">{t('crud.fields.date')}</th>
              <th className="px-4 py-2 border">{t('crud.fields.amount')}</th>
              <th className="px-4 py-2 border">{t('crud.fields.purpose')}</th>
              <th className="px-4 py-2 border">{t('crud.fields.counterAccount')}</th>
              <th className="px-4 py-2 border">{t('crud.fields.opReference')}</th>
              <th className="px-4 py-2 border">{t('crud.fields.assigned')}</th>
            </tr>
          </thead>
          <tbody>
            {_data.map((row, index) => (
              <tr key={index} className={`border ${row.zugeordnet ? 'bg-green-50' : ''}`}>
                <td className="px-4 py-2 border">{row.datum}</td>
                <td className="px-4 py-2 border text-right">
                  {row.betrag?.toFixed(2)} €
                </td>
                <td className="px-4 py-2 border max-w-xs truncate" title={row.verwendungszweck}>
                  {row.verwendungszweck}
                </td>
                <td className="px-4 py-2 border">
                  <input
                    type="text"
                    value={row.gegenkonto || ''}
                    onChange={(e) => updateZuordnung(index, 'gegenkonto', e.target.value)}
                    className="w-full p-1 border rounded text-sm"
                    placeholder={t('crud.tooltips.placeholders.account')}
                  />
                </td>
                <td className="px-4 py-2 border">
                  <input
                    type="text"
                    value={row.opReferenz || ''}
                    onChange={(e) => updateZuordnung(index, 'opReferenz', e.target.value)}
                    className="w-full p-1 border rounded text-sm"
                    placeholder={t('crud.tooltips.placeholders.opReference')}
                  />
                </td>
                <td className="px-4 py-2 border text-center">
                  <input
                    type="checkbox"
                    checked={row.zugeordnet || false}
                    onChange={() => toggleZuordnung(index)}
                    className="h-4 w-4"
                  />
                </td>
              </tr>
            ))}
          </tbody>
        </table>
      </div>
    </div>
  )
}

function BankImportErrorList({ errors }: { errors: string[] }) {
  const { t } = useTranslation()
  if (!errors || errors.length === 0) {
    return (
      <div className="rounded border border-green-200 bg-green-50 p-3 text-sm text-green-800">
        {t('crud.messages.noImportErrors', { defaultValue: 'Keine Importfehler.' })}
      </div>
    )
  }

  return (
    <div className="space-y-2">
      <div className="text-sm font-medium text-red-700">
        {t('crud.messages.importWarnings', { defaultValue: 'Import-Warnungen' })}: {errors.length}
      </div>
      <div className="max-h-56 overflow-auto rounded border">
        <ul className="divide-y">
          {errors.map((err, idx) => (
            <li key={`${err}-${idx}`} className="px-3 py-2 text-sm text-red-700">
              {err}
            </li>
          ))}
        </ul>
      </div>
    </div>
  )
}

export default function BankAbgleichPage(): JSX.Element {
  const { t } = useTranslation()
  const navigate = useNavigate()
  const { tenantId } = useTenant()
  const [isDirty, setIsDirty] = useState(false)
  const entityType = 'bankReconciliation'
  const entityTypeLabel = getEntityTypeLabel(t, entityType, 'Bank-Abgleich')
  const bankAbgleichConfig = createBankAbgleichConfig(t, entityTypeLabel)

  const { data, loading } = useMaskData({
    apiUrl: bankAbgleichConfig.api.baseUrl,
    id: 'new'
  })
  const operationalStatus = normalizeOperationalStatus(
    !data ? 'offen' : Math.abs(Number(data.abgleichsDifferenz || 0)) >= 0.01 ? 'blockiert' : Number(data.nichtZugeordnet || 0) > 0 ? 'wartet_auf_mensch' : 'abgeschlossen'
  )
  const contextSections = [
    {
      title: 'Objekt',
      items: [
        { label: 'Bankkonto', value: data?.kontoId || 'Noch nicht gewaehlt' },
        { label: 'Statement', value: data?.statementId || 'Noch nicht importiert' },
        { label: 'Periode', value: data?.periode || '-' },
      ],
    },
    {
      title: 'Wirtschaftslage',
      items: [
        { label: 'Startsaldo', value: `${Number(data?.startSaldo || 0).toFixed(2)} EUR` },
        { label: 'Endsaldo', value: `${Number(data?.endSaldo || 0).toFixed(2)} EUR` },
        { label: 'Differenz', value: `${Math.abs(Number(data?.abgleichsDifferenz || 0)).toFixed(2)} EUR` },
      ],
    },
    {
      title: 'Governance',
      items: [
        { label: 'Nicht zugeordnet', value: String(Number(data?.nichtZugeordnet || 0)) },
        { label: 'Importfehler', value: String(Array.isArray(data?.importErrors) ? data.importErrors.length : 0) },
        { label: 'Naechste Aktion', value: Number(data?.nichtZugeordnet || 0) > 0 ? 'Zuordnung pruefen und validieren' : 'Abgleich verbuchen' },
      ],
    },
  ]
  const timelineItems = [
    { label: 'Bankabgleich geoeffnet', detail: entityTypeLabel },
    data?.statementId ? { label: 'Statement importiert', detail: data.statementId } : null,
    Number(data?.nichtZugeordnet || 0) > 0 ? { label: 'Manuelle Klaerung offen', detail: `${data.nichtZugeordnet} Umsatzzeile(n) ohne Zuordnung` } : null,
  ].filter((item): item is { label: string; detail: string } => item !== null)

  type ReconcileResult = {
    balance_comparison: { difference: number; is_balanced: boolean }
    line_counts?: { matched?: number; unmatched?: number }
    total_differences?: number
    differences?: unknown[]
    booking_suggestions?: unknown
  }

  const validate = (formData: Record<string, unknown>) => validateFields(getFieldsFromMaskConfig(bankAbgleichConfig), formData ?? {})
  const showValidationToast = (errors: Record<string, string>) => {
    toast({
      variant: 'destructive',
      title: t('crud.messages.validationError'),
      description: `${Object.keys(errors).length} Feld(er) muessen korrigiert werden.`,
    })
  }

  const { handleAction, loadingActionKey } = useMaskActions(async (action: string, formData: Record<string, unknown>) => {
    if (action === 'import') {
      // Bank Statement Import - use real API
      if (!formData.camtFile) {
        toast({
          variant: 'destructive',
          title: t('crud.messages.validationError'),
          description: t('crud.messages.selectFileFirst'),
        })
        return
      }

      if (!formData.kontoId) {
        toast({
          variant: 'destructive',
          title: t('crud.messages.validationError'),
          description: t('crud.messages.selectBankAccountFirst'),
        })
        return
      }

      try {
        // Determine file format from extension
        const fileName = formData.camtFile.name || ''
        let format = 'CSV'
        if (fileName.endsWith('.xml') || fileName.endsWith('.camt')) {
          format = 'CAMT'
        } else if (fileName.endsWith('.940') || fileName.endsWith('.sta')) {
          format = 'MT940'
        }

        // Create FormData for file upload
        const uploadFormData = new FormData()
        uploadFormData.append('file', formData.camtFile)

        // Call import API
        type ImportResult = {
          statement_id: string
          imported_lines: number
          error_lines: number
          import_errors: string[]
          opening_balance: string
          closing_balance: string
          lines: Array<{
            booking_date: string
            amount: string
            remittance_info?: string
            reference?: string
            status: string
            creditor_name?: string
            debtor_name?: string
          }>
        }
        const res = await apiClient.post<ImportResult>(
          `/api/v1/finance/bank-statements/import?format=${String(format ?? '')}&bank_account_id=${String(formData.kontoId ?? '')}&tenant_id=${String(encodeURIComponent(tenantId) ?? '')}`,
          uploadFormData,
          { headers: { 'Content-Type': 'multipart/form-data' } }
        )
        const result = res.data

        // Transform API response to form data format
        const umsaetze = result.lines.map((line: Record<string, unknown>) => ({
          datum: line.booking_date,
          betrag: parseFloat(line.amount),
          verwendungszweck: line.remittance_info || line.reference || '',
          gegenkonto: '', // Will be assigned during matching
          opReferenz: line.reference || '',
          zugeordnet: line.status === 'MATCHED',
          creditor_name: line.creditor_name,
          debtor_name: line.debtor_name
        }))

        formData.zuordnungData = umsaetze
        formData.startSaldo = parseFloat(result.opening_balance)
        formData.endSaldo = parseFloat(result.closing_balance)
        formData.gebuchteUmsaetze = umsaetze.reduce((sum, u) => sum + Number((u as Record<string, unknown>).betrag || 0), 0)
        formData.nichtZugeordnet = umsaetze.filter(u => !u.zugeordnet).length
        formData.zugeordnet = umsaetze.filter(u => u.zugeordnet).length
        formData.abgleichsDifferenz = Math.abs(Number(formData.startSaldo) + Number(formData.gebuchteUmsaetze) - formData.endSaldo)
        formData.statementId = result.statement_id
        formData.importErrors = result.import_errors || []

        toast({
          title: t('crud.messages.camtFileImported'),
          description: t('crud.messages.camtFileImportedDesc', { count: result.imported_lines }),
        })

        if (result.import_errors && result.import_errors.length > 0) {
          toast({
            variant: 'destructive',
            title: t('crud.messages.importWarnings'),
            description: `${result.error_lines} ${t('crud.messages.linesWithErrors')}`,
          })
        }
      } catch (_rawErr: unknown) {
        const error = _rawErr as { response?: { data?: { detail?: string } }; message?: string; name?: string }
        toast({
          variant: 'destructive',
          title: t('crud.messages.importError'),
          description: error.message || t('crud.messages.importFailed'),
        })
      }
    } else if (action === 'auto-assign') {
      // Auto-Zuordnung - wende einfache Regeln an
      if (!formData.zuordnungData || formData.zuordnungData.length === 0) {
        toast({
          variant: 'destructive',
          title: t('crud.messages.noData'),
          description: t('crud.messages.importCamtFileFirst'),
        })
        return
      }

      const rules = [
        { name: 'Rechnung-Zuordnung', pattern: /Rechnung|RE-/, konto: '4400' },
        { name: 'Kunden-Zuordnung', pattern: /K001|K002|K003/, konto: '1400' },
        { name: 'Strom-Zuordnung', pattern: /Strom|Stadtwerke/, konto: '4100' },
        { name: 'Büro-Zuordnung', pattern: /Büro|Material/, konto: '4650' }
      ]

      let zugeordnetCount = 0
      const regelStats = rules.map(regel => ({ regelName: regel.name, treffer: 0, zugeordnet: 0 }))

      formData.zuordnungData.forEach(umsatz => {
        if (!umsatz.zugeordnet) {
          rules.forEach((regel, index) => {
            if (regel.pattern.test(umsatz.verwendungszweck)) {
              regelStats[index].treffer++
              if (!umsatz.gegenkonto) {
                umsatz.gegenkonto = regel.konto
                umsatz.zugeordnet = true
                regelStats[index].zugeordnet++
                zugeordnetCount++
              }
            }
          })
        }
      })

      formData.regelAngewendet = regelStats
      formData.zugeordnet = (Number(formData.zugeordnet) || 0) + zugeordnetCount
      formData.nichtZugeordnet = formData.zuordnungData.length - formData.zugeordnet

      toast({
        title: t('crud.messages.autoAssignCompleted'),
        description: t('crud.messages.autoAssignCompletedDesc', { count: zugeordnetCount }),
      })
    } else if (action === 'validate') {
      // Validate reconciliation using backend API
      if (!formData.statementId || !formData.kontoId) {
        toast({
          variant: 'destructive',
          title: t('crud.messages.validationError'),
          description: t('crud.messages.importCamtFileFirst'),
        })
        return
      }

      try {
        const res = await apiClient.post<ReconcileResult>(
          `/api/v1/finance/bank-reconciliation/${String(formData.statementId ?? '')}/reconcile?bank_account_id=${String(formData.kontoId ?? '')}&tenant_id=${String(encodeURIComponent(tenantId) ?? '')}&auto_book=false`
        )
        const result = res.data

        formData.abgleichsDifferenz = Math.abs(result.balance_comparison.difference)
        formData.zugeordnet = result.line_counts?.matched || 0
        formData.nichtZugeordnet = result.line_counts?.unmatched || 0

        if (result.balance_comparison.is_balanced && result.total_differences === 0) {
          toast({
            title: t('crud.messages.validationSuccess'),
            description: t('crud.messages.reconciliationBalanced'),
          })
        } else {
          toast({
            variant: 'destructive',
            title: t('crud.messages.reconciliationNotBalanced'),
            description: t('crud.messages.reconciliationNotBalancedDesc', { 
              difference: result.balance_comparison.difference.toFixed(2) 
            }),
          })
        }

        // Show differences if any
        if (result.differences && result.differences.length > 0) {
          formData.differences = result.differences
          formData.bookingSuggestions = result.booking_suggestions
        }
      } catch (_rawErr: unknown) {
        const error = _rawErr as { response?: { data?: { detail?: string } }; message?: string; name?: string }
        toast({
          variant: 'destructive',
          title: t('crud.messages.reconciliationError'),
          description: error.message || t('crud.messages.networkError'),
        })
      }
    } else if (action === 'book') {
      const validationErrors = validate(formData)
      if (Object.keys(validationErrors).length > 0) {
        showValidationToast(validationErrors)
        return
      }
      if (!formData.statementId || !formData.kontoId) {
        toast({ variant: 'destructive', title: t('crud.messages.validationError'), description: t('crud.messages.importCamtFileFirst') })
        return
      }
      const differenz = Math.abs(formData.abgleichsDifferenz || 0)
      if (differenz >= 0.01) {
        toast({ variant: 'destructive', title: t('crud.messages.bookingNotPossible'), description: t('crud.messages.reconciliationMustBeBalanced') })
        return
      }
      try {
        const res = await apiClient.post<ReconcileResult>(
          `/api/v1/finance/bank-reconciliation/${String(formData.statementId ?? '')}/reconcile?bank_account_id=${String(formData.kontoId ?? '')}&tenant_id=${String(encodeURIComponent(tenantId) ?? '')}&auto_book=true`
        )
        const result = res.data
        formData.zugeordnet = result.line_counts?.matched || formData.zugeordnet || 0
        formData.nichtZugeordnet = result.line_counts?.unmatched || formData.nichtZugeordnet || 0
        formData.abgleichsDifferenz = Math.abs(result.balance_comparison?.difference || 0)
        toast({ title: t('crud.messages.reconciliationBooked'), description: t('crud.messages.reconciliationBookedDesc') })
        setIsDirty(false)
        navigate('/finance/bank')
      } catch (_rawErr: unknown) {
        const error = _rawErr as { response?: { data?: { detail?: string } }; message?: string; name?: string }
        const msg = error.response?.data?.detail ?? error.message
        toast({ variant: 'destructive', title: t('common.error'), description: msg })
      }
    } else if (action === 'export') {
      if (!formData.id) {
        toast({ variant: 'destructive', title: t('common.error'), description: t('crud.messages.saveReconciliationFirst') })
        return
      }
      try {
        const res = await apiClient.post<{ url?: string }>('/api/v1/export/list', { entity: 'bank_reconciliation', format: 'pdf', id: formData.id })
        if (res?.url) window.open(res.url, '_blank')
        toast({ title: t('crud.actions.export'), description: t('crud.messages.exportCreated', { defaultValue: 'Export erstellt' }) })
      } catch (_rawErr: unknown) {
        const error = _rawErr as { response?: { data?: { detail?: string } }; message?: string; name?: string }
        const msg = error.response?.data?.detail ?? error.message
        toast({ variant: 'destructive', title: t('common.error'), description: msg })
      }
    }
  })

  const handleSave = async (formData: Record<string, unknown>) => {
    await handleAction('book', formData)
  }

  const handleCancel = () => {
    if (isDirty && !confirm(t('crud.messages.unsavedChanges'))) {
      return
    }
    navigate('/finance/bank')
  }

  return (
    <div className="space-y-4 p-4">
      <OperationalCaseHeader
        title="Bankabgleich"
        description="Import, Validierung und Buchung von Bankkontoauszuegen ohne Medienbruch."
        status={operationalStatus}
        owner="Finanzbuchhaltung"
        blocker={Math.abs(Number(data?.abgleichsDifferenz || 0)) >= 0.01 ? 'Abgleichsdifferenz ist noch nicht null.' : Number(data?.nichtZugeordnet || 0) > 0 ? 'Es gibt noch nicht zugeordnete Umsatzzeilen.' : null}
        nextAction={Number(data?.nichtZugeordnet || 0) > 0 ? 'Zuordnung abschliessen' : data?.statementId ? 'Validieren und verbuchen' : 'Kontoauszug importieren'}
        caseLabel={data?.statementId || 'Neuer Abgleich'}
        tags={['FIBU', 'Bank']}
      />
      <div className="grid gap-4 xl:grid-cols-[1.3fr_0.7fr]">
        <OperationalTimeline title="Abgleichsverlauf" items={timelineItems} />
        <OperationalContextPanel sections={contextSections} />
      </div>
      <ObjectPage
        config={bankAbgleichConfig}
        data={data}
        onSave={handleSave}
        onCancel={handleCancel}
        isLoading={loading}
        onAction={(key, formData) => handleAction(key, formData)}
        loadingActionKey={loadingActionKey}
      />
    </div>
  )
}
