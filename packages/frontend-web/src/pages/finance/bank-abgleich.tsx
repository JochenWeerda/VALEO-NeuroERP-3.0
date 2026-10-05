import { useEffect } from 'react'
import { useNavigate } from '@/app/routing/typed-router'
import { useTranslation } from 'react-i18next'
import type { TFunction } from 'i18next'
import { ObjectPage } from '@/components/mask-builder'
import { useMaskData, useMaskActions } from '@/components/mask-builder/hooks'
import { MaskConfig } from '@/components/mask-builder/types'
import { toast } from '@/hooks/use-toast'
import { apiClient } from '@/lib/api-client'
import { getEntityTypeLabel } from '@/features/crud/utils/i18n-helpers'
import type { BankReconciliationResult } from '@/features/finance/bank-contracts'
import { useBankOptions } from '@/features/finance/useBankOptions'
import { useTenant } from '@/hooks/useTenant'
import { OperationalCaseHeader } from '@/components/workflow/OperationalCaseHeader'
import { OperationalContextPanel } from '@/components/workflow/OperationalContextPanel'
import { OperationalTimeline } from '@/components/workflow/OperationalTimeline'
import { normalizeOperationalStatus } from '@/lib/operational-status'
import { numberValue, recordArrayFromResponse, stringValue } from '@/lib/record-utils'
import { Callout } from '@/components/ui/callout'
import { useTouchDevice } from '@/hooks/useTouchDevice'

const createBankAbgleichConfig = (t: TFunction, entityTypeLabel: string, bankOptions: { value: string; label: string }[]): MaskConfig => ({
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
          options: bankOptions
        },
        {
          name: 'camtFile',
          label: t('crud.fields.camtFile'),
          type: 'file',
          accept: '.xml,.camt,.940,.sta,.csv',
          helpText: t('crud.tooltips.fields.camtFile')
        },

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
    },
    {
      key: 'zuordnung_custom',
      label: '',
      fields: [],
      customRender: (_data: Record<string, unknown>) => (
        <BankZuordnungTable data={recordArrayFromResponse(_data.zuordnungData)} />
      )
    },
    {
      key: 'import_protokoll',
      label: t('crud.fields.importLog', { defaultValue: 'Import-Protokoll' }),
      fields: [],
      customRender: (_data: Record<string, unknown>) => (
        <BankImportErrorList errors={Array.isArray(_data.importErrors) ? _data.importErrors.map(String) : []} />
      )
    },
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
    { key: 'validate', label: t('crud.actions.validate'), type: 'primary' },
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
  },
  permissions: ['fibu.read', 'fibu.write']
})

// Bank-Zuordnung Tabelle Komponente
function BankZuordnungTable({ data: _data }: { data: Record<string, unknown>[] }) {
  const { t } = useTranslation()

  return (
    <div className="space-y-4">
      <div className="flex justify-between items-center">
        <h3 className="text-lg font-semibold">{t('crud.fields.assignBankTransactions')}</h3>
        <div className="text-sm text-gray-600">
          {t('crud.fields.assignedCount', { assigned: _data.filter(d => d.zugeordnet).length, total: _data.length })}
        </div>
      </div>

      <div className="overflow-x-auto max-h-96">
        <table className="min-w-full border border-border">
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
              <tr key={index} className={`border ${row.zugeordnet ? 'bg-[hsl(var(--color-semantic-success-50-hsl))]' : ''}`}>
                <td className="px-4 py-2 border">{stringValue(row.datum)}</td>
                <td className="px-4 py-2 border text-right">
                  {numberValue(row.betrag).toFixed(2)} EUR
                </td>
                <td className="px-4 py-2 border max-w-xs truncate" title={stringValue(row.verwendungszweck)}>
                  {stringValue(row.verwendungszweck)}
                </td>
                <td className="px-4 py-2 border">
                  {stringValue(row.gegenkonto, "—")}
                </td>
                <td className="px-4 py-2 border">
                  {stringValue(row.opReferenz)}
                </td>
                <td className="px-4 py-2 border text-center">
                  <input
                    type="checkbox"
                    checked={row.zugeordnet === true}
                    disabled
                    readOnly
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
      <Callout variant="success" className="rounded border p-3 text-sm">
        {t('crud.messages.noImportErrors', { defaultValue: 'Keine Importfehler.' })}
      </Callout>
    )
  }

  return (
    <div className="space-y-2">
      <div className="text-sm font-medium text-status-error">
        {t('crud.messages.importWarnings', { defaultValue: 'Import-Warnungen' })}: {errors.length}
      </div>
      <div className="max-h-56 overflow-auto rounded border">
        <ul className="divide-y">
          {errors.map((err, idx) => (
            <li key={`${err}-${idx}`} className="px-3 py-2 text-sm text-status-error">
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
  const isTouch = useTouchDevice()
  const navigate = useNavigate()
  const { data: accounts = [], isError: accountLoadFailed } = useBankOptions()
  const { tenantId } = useTenant()
  const entityType = 'bankReconciliation'
  const entityTypeLabel = getEntityTypeLabel(t, entityType, 'Bank-Abgleich')
  const bankAbgleichConfig = createBankAbgleichConfig(t, entityTypeLabel, accounts.map(account => ({ value: account.id, label: `${account.account_number} - ${account.bank_name}` })))

  const { data, loading, setData } = useMaskData({
    apiUrl: bankAbgleichConfig.api.baseUrl,
    autoLoad: false
  })
  useEffect(() => setData(null), [tenantId, setData])
  const operationalStatus = normalizeOperationalStatus(
    data?.comparisonState === 'BALANCES_EQUAL' ? 'abgeschlossen' : data?.comparisonState === 'DIFFERENCES' ? 'blockiert' : 'offen'
  )
  const contextSections = [
    {
      title: 'Objekt',
      items: [
        { label: 'Bankkonto', value: stringValue(data?.kontoId, 'Noch nicht gewaehlt') },
        { label: 'Statement', value: stringValue(data?.statementId, 'Noch nicht importiert') },
        { label: 'Periode', value: stringValue(data?.periode, '-') },
      ],
    },
    {
      title: 'Wirtschaftslage',
      items: [
        { label: 'Startsaldo', value: `${numberValue(data?.startSaldo).toFixed(2)} EUR` },
        { label: 'Endsaldo', value: `${numberValue(data?.endSaldo).toFixed(2)} EUR` },
        { label: 'Differenz', value: data?.abgleichsDifferenz == null ? 'Nicht ermittelt' : `${Math.abs(numberValue(data.abgleichsDifferenz)).toFixed(2)} ${stringValue(data.currency, 'EUR')}` },
      ],
    },
    {
      title: 'Governance',
      items: [
        { label: 'Nicht zugeordnet', value: String(numberValue(data?.nichtZugeordnet)) },
        { label: 'Importfehler', value: String(Array.isArray(data?.importErrors) ? data.importErrors.length : 0) },
        { label: 'Naechste Aktion', value: numberValue(data?.nichtZugeordnet) > 0 ? 'Zuordnung pruefen und validieren' : 'Saldenvergleich pruefen' },
      ],
    },
  ]
  const timelineItems = [
    { label: 'Bankabgleich geoeffnet', detail: entityTypeLabel },
    data?.statementId ? { label: 'Statement importiert', detail: stringValue(data.statementId) } : null,
    numberValue(data?.nichtZugeordnet) > 0 ? { label: 'Manuelle Klaerung offen', detail: `${numberValue(data?.nichtZugeordnet)} Umsatzzeile(n) ohne Zuordnung` } : null,
  ].filter((item): item is { label: string; detail: string } => item !== null)

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
        const camtFile = formData.camtFile instanceof Blob ? formData.camtFile : null
        const fileName = camtFile instanceof File ? camtFile.name : ''
        let format = 'CSV'
        if (fileName.endsWith('.xml') || fileName.endsWith('.camt')) {
          format = 'CAMT'
        } else if (fileName.endsWith('.940') || fileName.endsWith('.sta')) {
          format = 'MT940'
        }

        // Create FormData for file upload
        const uploadFormData = new FormData()
        if (camtFile) uploadFormData.append('file', camtFile)

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
          `/api/v1/finance/bank-statements/import?format=${String(format ?? '')}&bank_account_id=${String(formData.kontoId ?? '')}`,
          uploadFormData,
          { headers: { 'Content-Type': 'multipart/form-data' } }
        )
        const result = res.data

        // Transform API response to form data format
        const umsaetze = result.lines.map((line) => ({
          datum: line.booking_date,
          betrag: Number(line.amount),
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
        formData.abgleichsDifferenz = Math.abs(Number(formData.startSaldo) + Number(formData.gebuchteUmsaetze) - Number(formData.endSaldo))
        formData.statementId = result.statement_id
        formData.comparisonState = 'INCOMPLETE'
        formData.abgleichsDifferenz = null
        setData({ ...formData })
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
        const res = await apiClient.post<BankReconciliationResult>(
          `/api/v1/finance/bank-reconciliation/${String(formData.statementId ?? '')}/reconcile?bank_account_id=${String(formData.kontoId ?? '')}&auto_book=false`
        )
        const result = res.data

        formData.abgleichsDifferenz = result.balance_comparison.difference == null ? null : Math.abs(Number(result.balance_comparison.difference))
        formData.comparisonState = result.comparison_state
        formData.currency = result.balance_comparison.currency
        formData.periode = result.balance_comparison.statement_date?.slice(0, 7)
        formData.zugeordnet = result.line_counts?.matched || 0
        formData.nichtZugeordnet = result.line_counts.unmatched + result.line_counts.partial + result.line_counts.unknown

        setData({ ...formData })
        if (result.comparison_state === 'INCOMPLETE') {
          const balance = result.balance_comparison
          const reason = balance.bank_balance_state === 'CSV_SYNTHETIC'
            ? 'CSV-Dateien enthalten keinen Bank-Saldonachweis.'
            : balance.accounting_state === 'MAPPING_REQUIRED'
              ? 'Bankkonto ist noch nicht mit einem Hauptbuchkonto verbunden.'
              : balance.accounting_state === 'NO_POSTED_ENTRIES'
                ? 'Fuer den Stichtag liegen keine belegten Hauptbuchbuchungen vor.'
                : 'Es gibt Teilzuordnungen oder unbekannte Statuswerte.'
          toast({ variant: 'destructive', title: 'Saldennachweis unvollstaendig', description: reason })
        } else if (result.comparison_state === 'BALANCES_EQUAL') {
          toast({
            title: t('crud.messages.validationSuccess'),
            description: t('crud.messages.reconciliationBalanced'),
          })
        } else {
          toast({
            variant: 'destructive',
            title: t('crud.messages.reconciliationNotBalanced'),
            description: t('crud.messages.reconciliationNotBalancedDesc', { 
              difference: result.balance_comparison.difference == null ? 'Nicht ermittelt' : Number(result.balance_comparison.difference).toFixed(2)
            }),
          })
        }

        formData.differences = result.differences
      } catch (_rawErr: unknown) {
        const error = _rawErr as { response?: { data?: { detail?: string } }; message?: string; name?: string }
        formData.comparisonState = 'INCOMPLETE'
        formData.abgleichsDifferenz = null
        setData({ ...formData })
        toast({
          variant: 'destructive',
          title: t('crud.messages.reconciliationError'),
          description: error.response?.data?.detail || error.message || t('crud.messages.networkError'),
        })
      }
    } else if (action === 'export') {
      if (!formData.id) {
        toast({ variant: 'destructive', title: t('common.error'), description: t('crud.messages.saveReconciliationFirst') })
        return
      }
      try {
        const res = await apiClient.post<{ url?: string }>('/api/v1/export/list', { entity: 'bank_reconciliation', format: 'pdf', id: formData.id })
        if (res.data.url) window.open(res.data.url, '_blank')
        toast({ title: t('crud.actions.export'), description: t('crud.messages.exportCreated', { defaultValue: 'Export erstellt' }) })
      } catch (_rawErr: unknown) {
        const error = _rawErr as { response?: { data?: { detail?: string } }; message?: string; name?: string }
        const msg = error.response?.data?.detail ?? error.message
        toast({ variant: 'destructive', title: t('common.error'), description: msg })
      }
    }
  })

  const handleSave = async (formData: Record<string, unknown>) => {
    await handleAction('validate', formData)
  }

  const handleCancel = () => {
    navigate('/finance/bank')
  }

  return (
    <div className="space-y-4 p-3 md:p-4">
      {accountLoadFailed ? <Callout variant="error">Bankkonten konnten nicht geladen werden.</Callout> : null}
      <ObjectPage
        config={bankAbgleichConfig}
        data={data}
        onChange={(next) => {
          if (next.kontoId !== data?.kontoId || next.camtFile !== data?.camtFile) {
            setData({ ...next, comparisonState: 'INCOMPLETE', abgleichsDifferenz: null })
          }
        }}
        onSave={handleSave}
        onCancel={handleCancel}
        isLoading={loading}
        onAction={(key, formData) => handleAction(key, formData)}
        loadingActionKey={loadingActionKey}
      />
      {!isTouch ? (
        <>
          <OperationalCaseHeader
            title="Bankabgleich"
            description="Import und Pruefung von Bankkontoauszuegen. Buchungen erfolgen im Journal."
            status={operationalStatus}
            owner="Finanzbuchhaltung"
            blocker={data?.abgleichsDifferenz == null ? 'Saldennachweis noch nicht ermittelt.' : Math.abs(Number(data.abgleichsDifferenz)) >= 0.01 ? 'Abgleichsdifferenz ist noch nicht null.' : Number(data?.nichtZugeordnet || 0) > 0 ? 'Es gibt noch nicht zugeordnete Umsatzzeilen.' : null}
            nextAction={Number(data?.nichtZugeordnet || 0) > 0 ? 'Zuordnung abschliessen' : data?.statementId ? 'Saldenvergleich pruefen' : 'Kontoauszug importieren'}
            caseLabel={stringValue(data?.statementId, 'Neuer Abgleich')}
            tags={['FIBU', 'Bank']}
          />
          <div className="grid gap-4 xl:grid-cols-[1.3fr_0.7fr]">
            <OperationalTimeline title="Abgleichsverlauf" items={timelineItems} />
            <OperationalContextPanel sections={contextSections} />
          </div>
        </>
      ) : null}
    </div>
  )
}
