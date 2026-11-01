import { useRef, useState } from 'react'
import type { RenderPlan } from '../../render-plan/types'
import { canDomainAction, fieldsEditable, useDomainDispatch } from '../intake/domain-runtime'
import { useBankOptions } from '@/features/finance/useBankOptions'
import type { BankReconciliationResult } from '@/features/finance/bank-contracts'
import { apiClient } from '@/lib/api-client'
import { toast } from '@/hooks/use-toast'

type Line = { booking_date: string; amount: string; remittance_info?: string; reference?: string; status: string; creditor_name?: string; debtor_name?: string }
type ImportResult = { statement_id: string; imported_lines: number; error_lines: number; import_errors: string[]; opening_balance: string; closing_balance: string; lines: Line[] }
const money = (value: number | null | undefined, currency = 'EUR') => value == null ? 'Nicht ermittelt' : `${value.toFixed(2)} ${currency}`
const errorText = (error: unknown) => {
  const err = error as { response?: { data?: { detail?: string } }; message?: string }
  return err.response?.data?.detail ?? err.message ?? 'Unbekannter Fehler'
}

export default function BankSurface({ plan }: { plan: RenderPlan }): JSX.Element {
  const { data: accounts = [], isError: accountError } = useBankOptions()
  const [account, setAccount] = useState('')
  const [file, setFile] = useState<File | null>(null)
  const [statement, setStatement] = useState<ImportResult | null>(null)
  const [comparison, setComparison] = useState<BankReconciliationResult | null>(null)
  const [pending, setPending] = useState(false)
  const pendingRef = useRef(false)
  const clear = () => { setStatement(null); setComparison(null) }
  const editable = fieldsEditable(plan, ['kontoId', 'camtFile'])
  const runImport = async () => {
    if (pendingRef.current || !canDomainAction(plan, 'import') || !editable) return
    if (!account || !file) { toast({ variant: 'destructive', title: 'Bankkonto und Datei auswählen' }); return }
    pendingRef.current = true; setPending(true)
    try {
      const name = file.name.toLowerCase()
      const format = name.endsWith('.xml') || name.endsWith('.camt') ? 'CAMT' : name.endsWith('.940') || name.endsWith('.sta') ? 'MT940' : 'CSV'
      const body = new FormData(); body.append('file', file)
      const response = await apiClient.post<ImportResult>(`/api/v1/finance/bank-statements/import?format=${format}&bank_account_id=${encodeURIComponent(account)}`, body, { headers: { 'Content-Type': 'multipart/form-data' } })
      setStatement(response.data); setComparison(null)
      toast({ title: 'Kontoauszug importiert', description: `${response.data.imported_lines} Zeilen importiert` })
      if (response.data.import_errors?.length) toast({ variant: 'destructive', title: 'Importwarnungen', description: `${response.data.error_lines} Zeilen mit Fehlern` })
    } catch (err) { clear(); toast({ variant: 'destructive', title: 'Import fehlgeschlagen', description: errorText(err) }) }
    finally { pendingRef.current = false; setPending(false) }
  }
  const validate = async () => {
    if (pendingRef.current || !canDomainAction(plan, 'validate')) return
    if (!statement || !account) { toast({ variant: 'destructive', title: 'Bitte zuerst einen Kontoauszug importieren' }); return }
    pendingRef.current = true; setPending(true); setComparison(null)
    try {
      const res = await apiClient.post<BankReconciliationResult>(`/api/v1/finance/bank-reconciliation/${encodeURIComponent(statement.statement_id)}/reconcile?bank_account_id=${encodeURIComponent(account)}&auto_book=false`)
      const value = res.data; setComparison(value)
      if (value.comparison_state === 'INCOMPLETE') {
        const balance = value.balance_comparison
        const reason = balance.bank_balance_state === 'CSV_SYNTHETIC' ? 'CSV-Dateien enthalten keinen Bank-Saldonachweis.' : balance.accounting_state === 'MAPPING_REQUIRED' ? 'Bankkonto ist noch nicht mit einem Hauptbuchkonto verbunden.' : balance.accounting_state === 'NO_POSTED_ENTRIES' ? 'Für den Stichtag liegen keine belegten Hauptbuchbuchungen vor.' : 'Es gibt Teilzuordnungen oder unbekannte Statuswerte.'
        toast({ variant: 'destructive', title: 'Saldennachweis unvollständig', description: reason })
      } else if (value.comparison_state === 'BALANCES_EQUAL') toast({ title: 'Salden stimmen überein' })
      else toast({ variant: 'destructive', title: 'Salden weichen ab', description: money(value.balance_comparison.difference == null ? null : Number(value.balance_comparison.difference), value.balance_comparison.currency) })
    } catch (err) { toast({ variant: 'destructive', title: 'Abgleich fehlgeschlagen', description: errorText(err) }) }
    finally { pendingRef.current = false; setPending(false) }
  }
  const exportResult = () => {
    if (pendingRef.current || !canDomainAction(plan, 'export')) return
    if (!statement) { toast({ variant: 'destructive', title: 'Bitte zuerst einen Kontoauszug importieren' }); return }
    const cell = (value: unknown) => {
      let text = String(value ?? '')
      if (/^[\s]*[=+@-]/.test(text) && !/^-?\d+(?:[.,]\d+)?$/.test(text)) text = "'" + text
      return '"' + text.replace(/"/g, '""') + '"'
    }
    const rows = [['Datum', 'Betrag', 'Verwendungszweck', 'Referenz', 'Status'], ...statement.lines.map(line => [line.booking_date, line.amount, line.remittance_info ?? '', line.reference ?? '', line.status])]
    const blob = new Blob(['\ufeff' + rows.map(row => row.map(cell).join(';')).join('\r\n')], { type: 'text/csv;charset=utf-8' })
    const url = URL.createObjectURL(blob)
    const link = document.createElement('a'); link.href = url; link.download = 'bankabgleich.csv'; link.click()
    URL.revokeObjectURL(url)
  }
  useDomainDispatch(plan, { import: runImport, validate, export: exportResult })
  const counts = comparison?.line_counts
  const unmatched = counts ? counts.unmatched + counts.partial + counts.unknown : statement?.lines.filter(line => line.status !== 'MATCHED').length
  const currency = comparison?.balance_comparison.currency ?? 'EUR'
  return <section className="space-y-4" aria-label="Bankabgleich Arbeitsbereich">
    {accountError && <p role="alert">Bankkonten konnten nicht geladen werden.</p>}
    <div className="grid gap-3 md:grid-cols-2">
      <label>Bankkonto<select className="block min-h-touch w-full rounded border p-2" value={account} disabled={!editable || pending} onChange={event => { setAccount(event.target.value); clear() }}><option value="">Bitte wählen</option>{accounts.map(a => <option key={a.id} value={a.id}>{a.account_number} - {a.bank_name}</option>)}</select></label>
      <label>Kontoauszug<input className="block min-h-touch w-full" type="file" accept=".xml,.camt,.940,.sta,.csv" disabled={!editable || pending} onChange={event => { setFile(event.target.files?.[0] ?? null); clear() }} /></label>
    </div>
    {pending && <p role="status">Verarbeitung läuft …</p>}
    <div className="grid gap-2 md:grid-cols-4 text-sm"><span>Startsaldo: {money(statement ? Number(statement.opening_balance) : null)}</span><span>Endsaldo: {money(statement ? Number(statement.closing_balance) : null)}</span><span>Umsatzsumme: {money(statement ? statement.lines.reduce((sum, line) => sum + Number(line.amount), 0) : null)}</span><span>Zugeordnet: {counts?.matched ?? statement?.lines.filter(line => line.status === 'MATCHED').length ?? '—'}</span><span>Nicht zugeordnet: {unmatched ?? '—'}</span><span>Hauptbuchsaldo: {money(comparison?.balance_comparison.accounting_balance == null ? null : Number(comparison.balance_comparison.accounting_balance), currency)}</span><span>Differenz: {money(comparison?.balance_comparison.difference == null ? null : Math.abs(Number(comparison.balance_comparison.difference)), currency)}</span></div>
    <p role="status">{!comparison || comparison.comparison_state === 'INCOMPLETE' ? 'Saldennachweis unvollständig' : comparison.comparison_state === 'BALANCES_EQUAL' ? 'Salden stimmen überein' : 'Salden weichen ab'}</p>
    <h2 className="font-semibold">Umsatzzeilen</h2><div className="overflow-auto"><table className="w-full text-sm"><thead><tr><th>Datum</th><th>Betrag</th><th>Verwendungszweck</th><th>Referenz</th><th>Zuordnung</th></tr></thead><tbody>{statement?.lines.map((line, i) => <tr key={`${line.reference ?? ''}-${i}`}><td>{line.booking_date}</td><td className="text-right">{money(Number(line.amount))}</td><td>{line.remittance_info ?? line.reference ?? ''}</td><td>{line.reference ?? '—'}</td><td>{line.status}</td></tr>)}</tbody></table></div>
    <h2 className="font-semibold">Importprotokoll</h2>{statement?.import_errors?.length ? <ul role="alert">{statement.import_errors.map((error, i) => <li key={`${error}-${i}`}>{error}</li>)}</ul> : <p>Keine Importfehler.</p>}
    {comparison?.differences?.length ? <section><h2 className="font-semibold">Differenzen</h2><pre className="whitespace-pre-wrap text-sm">{JSON.stringify(comparison.differences, null, 2)}</pre></section> : null}
  </section>
}
