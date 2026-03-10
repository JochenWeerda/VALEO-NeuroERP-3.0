import { useMemo, useState, type JSX } from 'react'
import { useQuery } from '@tanstack/react-query'
import { Download, FileSpreadsheet, FileText, Search, Sheet, X } from 'lucide-react'
import { api, apiClient } from '@/lib/axios'
import { AnalyticsChart } from './reports/AnalyticsChart'
import { FinancialCard } from './reports/FinancialCard'
import { ProfitLossTable, type ProfitLossLine } from './reports/ProfitLossTable'
import { Sidebar } from './reports/Sidebar'
import styles from './reports.module.css'

interface BalanceSheetItem {
  account_number: string
  account_name: string
  balance: number | string
}

interface BalanceSheet {
  period: string
  total_assets: number | string
  total_liabilities: number | string
  total_equity: number | string
  assets: BalanceSheetItem[]
  liabilities: BalanceSheetItem[]
  equity: BalanceSheetItem[]
}

interface ProfitLossItem {
  account_number: string
  account_name: string
  amount: number | string
}

interface ProfitLoss {
  period: string
  total_revenue: number | string
  total_expenses: number | string
  net_income: number | string
  revenue: ProfitLossItem[]
  expenses: ProfitLossItem[]
}

interface BwaItem {
  description: string
  current_period: number | string
}

interface Bwa {
  period: string
  total_revenue: number | string
  total_costs: number | string
  net_result: number | string
  items: BwaItem[]
}

interface JournalLine {
  account_id?: string
  description?: string
  debit_amount?: number | string
  credit_amount?: number | string
}

interface JournalEntry {
  id: string
  document_number?: string
  reference?: string
  description?: string
  entry_date?: string
  total_debit?: number | string
  total_credit?: number | string
  status?: string
  lines?: JournalLine[]
}

interface JournalListResponse {
  items: JournalEntry[]
}

const EMPTY_BALANCE_SHEET: BalanceSheet = {
  period: '',
  total_assets: 0,
  total_liabilities: 0,
  total_equity: 0,
  assets: [],
  liabilities: [],
  equity: [],
}

const EMPTY_PROFIT_LOSS: ProfitLoss = {
  period: '',
  total_revenue: 0,
  total_expenses: 0,
  net_income: 0,
  revenue: [],
  expenses: [],
}

const EMPTY_BWA: Bwa = {
  period: '',
  total_revenue: 0,
  total_costs: 0,
  net_result: 0,
  items: [],
}

const EMPTY_PROFIT_LOSS_SERIES: Array<{ period: string; pl: ProfitLoss }> = []

const EMPTY_JOURNAL_ENTRIES: JournalEntry[] = []

const periodFormatter = new Intl.DateTimeFormat('de-DE', { month: 'short' })

function toNumber(value: number | string | undefined): number {
  if (value === undefined) return 0
  const cast = Number(value)
  return Number.isFinite(cast) ? cast : 0
}

function formatAmount(value: number): string {
  return value.toLocaleString('de-DE', { minimumFractionDigits: 2, maximumFractionDigits: 2 })
}

function getCurrentPeriod(): string {
  const now = new Date()
  return `${now.getFullYear()}-${String(now.getMonth() + 1).padStart(2, '0')}`
}

function offsetPeriod(basePeriod: string, monthsDelta: number): string {
  const [year, month] = basePeriod.split('-').map(Number)
  const date = new Date(year, month - 1 + monthsDelta, 1)
  return `${date.getFullYear()}-${String(date.getMonth() + 1).padStart(2, '0')}`
}

async function fetchBalanceSheet(period: string): Promise<BalanceSheet> {
  return apiClient.get<BalanceSheet>('/api/v1/finance/financial-reports/balance-sheet', { params: { period } })
}

async function fetchProfitLoss(period: string): Promise<ProfitLoss> {
  return apiClient.get<ProfitLoss>('/api/v1/finance/financial-reports/profit-loss', { params: { period } })
}

async function fetchBwa(period: string): Promise<Bwa> {
  return apiClient.get<Bwa>('/api/v1/finance/financial-reports/bwa', { params: { period } })
}

async function fetchProfitLossSeries(period: string): Promise<Array<{ period: string; pl: ProfitLoss }>> {
  const periods = Array.from({ length: 7 }, (_, index) => offsetPeriod(period, -6 + index))
  const rows = await Promise.all(periods.map(async (p) => ({ period: p, pl: await fetchProfitLoss(p) })))
  return rows
}

async function fetchJournalEntries(period: string): Promise<JournalEntry[]> {
  const startDate = `${period}-01`
  const endDate = `${period}-31`
  const result = await apiClient.get<JournalListResponse>('/api/v1/finance/journal-entries', {
    params: { start_date: startDate, end_date: endDate, limit: 50 },
  })
  return Array.isArray(result.items) ? result.items : []
}

function toCsv(profitLoss: ProfitLoss): string {
  const rows = [
    ['Art', 'Konto', 'Bezeichnung', 'Betrag'],
    ...profitLoss.revenue.map((item) => ['Erlös', item.account_number, item.account_name, String(item.amount)]),
    ...profitLoss.expenses.map((item) => ['Aufwand', item.account_number, item.account_name, String(item.amount)]),
  ]
  return rows.map((row) => row.map((cell) => `"${String(cell).replaceAll('"', '""')}"`).join(';')).join('\n')
}

function downloadBlob(blob: Blob, filename: string): void {
  const url = URL.createObjectURL(blob)
  const anchor = document.createElement('a')
  anchor.href = url
  anchor.download = filename
  anchor.click()
  URL.revokeObjectURL(url)
}

export default function FinanceReportsPage(): JSX.Element {
  const [period, setPeriod] = useState(getCurrentPeriod())
  const [search, setSearch] = useState('')
  const [isJournalOpen, setIsJournalOpen] = useState(false)
  const [isExportOpen, setIsExportOpen] = useState(false)
  const [expandedJournalEntryId, setExpandedJournalEntryId] = useState<string | null>(null)
  const [journalDetails, setJournalDetails] = useState<Record<string, JournalEntry>>({})
  const [journalDetailLoading, setJournalDetailLoading] = useState<Record<string, boolean>>({})

  const balanceQuery = useQuery({
    queryKey: ['finance', 'balance-sheet', period],
    queryFn: () => fetchBalanceSheet(period),
    initialData: EMPTY_BALANCE_SHEET,
  })
  const profitLossQuery = useQuery({
    queryKey: ['finance', 'profit-loss', period],
    queryFn: () => fetchProfitLoss(period),
    initialData: EMPTY_PROFIT_LOSS,
  })
  const previousYearProfitLossQuery = useQuery({
    queryKey: ['finance', 'profit-loss', `${Number(period.slice(0, 4)) - 1}-${period.slice(5)}`],
    queryFn: () => fetchProfitLoss(`${Number(period.slice(0, 4)) - 1}-${period.slice(5)}`),
    initialData: EMPTY_PROFIT_LOSS,
  })
  const bwaQuery = useQuery({
    queryKey: ['finance', 'bwa', period],
    queryFn: () => fetchBwa(period),
    initialData: EMPTY_BWA,
  })
  const seriesQuery = useQuery({
    queryKey: ['finance', 'profit-loss-series', period],
    queryFn: () => fetchProfitLossSeries(period),
    initialData: EMPTY_PROFIT_LOSS_SERIES,
  })
  const journalQuery = useQuery({
    queryKey: ['finance', 'journal-entries', period],
    queryFn: () => fetchJournalEntries(period),
    enabled: isJournalOpen,
    initialData: EMPTY_JOURNAL_ENTRIES,
  })

  const isLoading =
    balanceQuery.isLoading || profitLossQuery.isLoading || bwaQuery.isLoading || seriesQuery.isLoading

  const balanceSheet = balanceQuery.data
  const profitLoss = profitLossQuery.data
  const previousYearProfitLoss = previousYearProfitLossQuery.data
  const bwa = bwaQuery.data
  const series = seriesQuery.data

  const liquidity = toNumber(balanceSheet?.total_assets) - toNumber(balanceSheet?.total_liabilities)
  const ebitda = toNumber(profitLoss?.net_income)

  const liquiditySeries = series.map((point) => ({
    period: point.period,
    value: toNumber(point.pl.total_revenue) - toNumber(point.pl.total_expenses),
  }))
  const ebitdaSeries = series.map((point) => ({
    period: point.period,
    value: toNumber(point.pl.net_income),
  }))

  const previousLiquidity = liquiditySeries.length > 1 ? liquiditySeries[liquiditySeries.length - 2].value : liquidity
  const previousEbitda = ebitdaSeries.length > 1 ? ebitdaSeries[ebitdaSeries.length - 2].value : ebitda
  const liquidityDelta = previousLiquidity !== 0 ? ((liquidity - previousLiquidity) / Math.abs(previousLiquidity)) * 100 : 0
  const ebitdaDelta = previousEbitda !== 0 ? ((ebitda - previousEbitda) / Math.abs(previousEbitda)) * 100 : 0

  const cashflow = series.map((point) => {
    const inflow = toNumber(point.pl.total_revenue)
    const outflow = toNumber(point.pl.total_expenses)
    return {
      period: periodFormatter.format(new Date(`${point.period}-01`)),
      inflow,
      outflow,
      net: inflow - outflow,
    }
  })

  const balanceShares = [
    { name: 'Aktiva', value: toNumber(balanceSheet?.total_assets) },
    { name: 'Fremdkapital', value: toNumber(balanceSheet?.total_liabilities) },
    { name: 'Eigenkapital', value: toNumber(balanceSheet?.total_equity) },
  ]

  const plRowsCurrentRevenue: ProfitLossLine[] =
    profitLoss?.revenue.map((row) => ({
      account_number: row.account_number,
      account_name: row.account_name,
      amount: toNumber(row.amount),
    })) ?? []

  const plRowsCurrentExpenses: ProfitLossLine[] =
    profitLoss?.expenses.map((row) => ({
      account_number: row.account_number,
      account_name: row.account_name,
      amount: toNumber(row.amount),
    })) ?? []

  const plRowsPreviousRevenue: ProfitLossLine[] =
    previousYearProfitLoss?.revenue.map((row) => ({
      account_number: row.account_number,
      account_name: row.account_name,
      amount: toNumber(row.amount),
    })) ?? []

  const plRowsPreviousExpenses: ProfitLossLine[] =
    previousYearProfitLoss?.expenses.map((row) => ({
      account_number: row.account_number,
      account_name: row.account_name,
      amount: toNumber(row.amount),
    })) ?? []

  const searchableRows = useMemo(
    () => [
      ...(balanceSheet?.assets ?? []),
      ...(balanceSheet?.liabilities ?? []),
      ...(balanceSheet?.equity ?? []),
      ...(profitLoss?.revenue ?? []),
      ...(profitLoss?.expenses ?? []),
    ],
    [balanceSheet, profitLoss],
  )

  const filteredSearchRows = searchableRows
    .filter((row) => {
      const needle = search.trim().toLowerCase()
      if (needle.length === 0) return false
      return (
        row.account_number.toLowerCase().includes(needle) ||
        row.account_name.toLowerCase().includes(needle)
      )
    })
    .slice(0, 8)

  async function runExport(type: 'pdf' | 'excel' | 'csv'): Promise<void> {
    if (!profitLoss) return

    if (type === 'csv') {
      const csv = toCsv(profitLoss)
      const blob = new Blob([csv], { type: 'text/csv;charset=utf-8' })
      downloadBlob(blob, `guv_${period}.csv`)
      setIsExportOpen(false)
      return
    }

    const extension = type === 'pdf' ? 'pdf' : 'xlsx'
    const response = await api.get(`/api/v1/finance/financial-reports/export/profit-loss`, {
      params: { period, format: type },
      responseType: 'blob',
    })
    downloadBlob(response.data as Blob, `guv_${period}.${extension}`)
    setIsExportOpen(false)
  }

  async function loadJournalDetail(entryId: string): Promise<void> {
    if (journalDetails[entryId] || journalDetailLoading[entryId]) return
    setJournalDetailLoading((prev) => ({ ...prev, [entryId]: true }))
    try {
      const detail = await apiClient.get<JournalEntry>(`/api/v1/finance/journal-entries/${entryId}`)
      setJournalDetails((prev) => ({ ...prev, [entryId]: detail }))
    } finally {
      setJournalDetailLoading((prev) => ({ ...prev, [entryId]: false }))
    }
  }

  function toggleJournalDetails(entryId: string): void {
    setExpandedJournalEntryId((prev) => (prev === entryId ? null : entryId))
    if (!journalDetails[entryId]) {
      void loadJournalDetail(entryId)
    }
  }

  return (
    <div className={styles.shell}>
      <Sidebar />
      <main className={styles.main}>
        <header className={styles.toolbar}>
          <div className={styles.commandWrap}>
            <Search size={18} />
            <input
              type="text"
              placeholder="Konto suchen (Strg+K)"
              value={search}
              onChange={(event) => setSearch(event.target.value)}
            />
            <kbd>Ctrl K</kbd>
          </div>

          <div className={styles.periodAndExport}>
            <input type="month" value={period} onChange={(event) => setPeriod(event.target.value)} />
            <div className={styles.exportWrap}>
              <button
                type="button"
                aria-label="Export öffnen"
                className={styles.exportButton}
                onClick={() => setIsExportOpen((v) => !v)}
              >
                <Download size={16} />
                Export
              </button>
              {isExportOpen ? (
                <div className={styles.exportMenu}>
                  <button type="button" onClick={() => void runExport('pdf')}>
                    <FileText size={14} />
                    PDF
                  </button>
                  <button type="button" onClick={() => void runExport('excel')}>
                    <FileSpreadsheet size={14} />
                    Excel
                  </button>
                  <button type="button" onClick={() => void runExport('csv')}>
                    <Sheet size={14} />
                    CSV
                  </button>
                </div>
              ) : null}
            </div>
            <button
              type="button"
              aria-label="Journal öffnen"
              className={styles.journalButton}
              onClick={() => setIsJournalOpen(true)}
            >
              Journal
            </button>
          </div>
        </header>

        {filteredSearchRows.length > 0 ? (
          <div className={styles.searchResults}>
            {filteredSearchRows.map((row) => (
              <div key={`${row.account_number}-${row.account_name}`} className={styles.searchRow}>
                <span>{row.account_number}</span>
                <span>{row.account_name}</span>
              </div>
            ))}
          </div>
        ) : null}

        {isLoading ? (
          <section className={styles.skeletonGrid}>
            <div className={styles.skeletonCard} />
            <div className={styles.skeletonCard} />
            <div className={styles.skeletonLarge} />
            <div className={styles.skeletonLarge} />
          </section>
        ) : (
          <>
            <section className={styles.kpiGrid}>
              <FinancialCard
                label="Liquidität"
                value={liquidity}
                deltaPercent={liquidityDelta}
                sparkline={liquiditySeries}
              />
              <FinancialCard
                label="EBITDA"
                value={ebitda}
                deltaPercent={ebitdaDelta}
                sparkline={ebitdaSeries}
              />
              <FinancialCard
                label="Umsatz"
                value={toNumber(bwa?.total_revenue)}
                deltaPercent={0}
                sparkline={series.map((point) => ({
                  period: point.period,
                  value: toNumber(point.pl.total_revenue),
                }))}
              />
            </section>

            <AnalyticsChart cashflow={cashflow} balanceShares={balanceShares} />

            <ProfitLossTable
              currentRevenue={plRowsCurrentRevenue}
              currentExpenses={plRowsCurrentExpenses}
              previousRevenue={plRowsPreviousRevenue}
              previousExpenses={plRowsPreviousExpenses}
            />
          </>
        )}
      </main>

      {isJournalOpen ? (
        <div className={styles.modalBackdrop} role="dialog" aria-modal="true">
          <section className={styles.modal}>
            <header className={styles.modalHeader}>
              <h3>Journal · Buchungssätze</h3>
              <button type="button" onClick={() => setIsJournalOpen(false)} aria-label="Schließen">
                <X size={16} />
              </button>
            </header>
            <div className={styles.modalBody}>
              {journalQuery.isLoading ? (
                <div className={styles.modalSkeleton} />
              ) : (
                (journalQuery.data ?? []).map((entry) => (
                  <article key={entry.id} className={styles.journalEntry}>
                    <div className={styles.journalHead}>
                      <strong>{entry.document_number ?? entry.id}</strong>
                      <span>{entry.entry_date ?? 'ohne Datum'}</span>
                      <span>{entry.status ?? 'draft'}</span>
                    </div>
                    <p>{entry.description ?? entry.reference ?? 'ohne Beschreibung'}</p>
                    <div className={styles.journalAmounts}>
                      <span>Soll: {toNumber(entry.total_debit).toLocaleString('de-DE')}</span>
                      <span>Haben: {toNumber(entry.total_credit).toLocaleString('de-DE')}</span>
                    </div>
                    <button
                      type="button"
                      className={styles.journalDetailsButton}
                      onClick={() => toggleJournalDetails(entry.id)}
                    >
                      {expandedJournalEntryId === entry.id ? 'Details ausblenden' : 'Details anzeigen'}
                    </button>
                    {expandedJournalEntryId === entry.id ? (
                      <div className={styles.journalLinesWrap}>
                        {journalDetailLoading[entry.id] ? (
                          <div className={styles.journalLinesLoading}>Lade Buchungszeilen...</div>
                        ) : (
                          (journalDetails[entry.id]?.lines ?? []).length > 0 ? (
                            <table className={styles.journalLinesTable}>
                              <thead>
                                <tr>
                                  <th>Konto</th>
                                  <th>Text</th>
                                  <th>Soll</th>
                                  <th>Haben</th>
                                </tr>
                              </thead>
                              <tbody>
                                {(journalDetails[entry.id]?.lines ?? []).map((line, index) => (
                                  <tr key={`${entry.id}-${index}`}>
                                    <td>{line.account_id ?? '-'}</td>
                                    <td>{line.description ?? '-'}</td>
                                    <td>{formatAmount(toNumber(line.debit_amount))}</td>
                                    <td>{formatAmount(toNumber(line.credit_amount))}</td>
                                  </tr>
                                ))}
                              </tbody>
                              <tfoot>
                                {(() => {
                                  const lines = journalDetails[entry.id]?.lines ?? []
                                  const sumDebit = lines.reduce((acc, line) => acc + toNumber(line.debit_amount), 0)
                                  const sumCredit = lines.reduce((acc, line) => acc + toNumber(line.credit_amount), 0)
                                  const difference = sumDebit - sumCredit
                                  const isBalanced = Math.abs(difference) < 0.01
                                  return (
                                    <>
                                      <tr className={styles.journalLinesTotalRow}>
                                        <td colSpan={2}>Summe</td>
                                        <td>{formatAmount(sumDebit)}</td>
                                        <td>{formatAmount(sumCredit)}</td>
                                      </tr>
                                      <tr>
                                        <td colSpan={4}>
                                          <div className={isBalanced ? styles.journalCheckOk : styles.journalCheckWarn}>
                                            {isBalanced
                                              ? 'Line-Level Check: Soll/Haben ausgeglichen.'
                                              : `Warnung: Ungleichgewicht ${formatAmount(difference)} (Soll - Haben).`}
                                          </div>
                                        </td>
                                      </tr>
                                    </>
                                  )
                                })()}
                              </tfoot>
                            </table>
                          ) : (
                            <div className={styles.journalLinesLoading}>Keine Detailzeilen verfügbar.</div>
                          )
                        )}
                      </div>
                    ) : null}
                  </article>
                ))
              )}
            </div>
          </section>
        </div>
      ) : null}
    </div>
  )
}
