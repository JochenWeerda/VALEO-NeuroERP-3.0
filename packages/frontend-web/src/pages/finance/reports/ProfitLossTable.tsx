import { useMemo, useState, type JSX } from 'react'
import { ChevronDown, ChevronRight } from 'lucide-react'
import styles from '../reports.module.css'

export interface ProfitLossLine {
  account_number: string
  account_name: string
  amount: number
}

interface ProfitLossTableProps {
  currentRevenue: ProfitLossLine[]
  currentExpenses: ProfitLossLine[]
  previousRevenue: ProfitLossLine[]
  previousExpenses: ProfitLossLine[]
}

interface AggregatedRow {
  key: string
  account: string
  accountName: string
  current: number
  previous: number
}

const currencyFormatter = new Intl.NumberFormat('de-DE', {
  style: 'currency',
  currency: 'EUR',
  maximumFractionDigits: 0,
})

function aggregateRows(current: ProfitLossLine[], previous: ProfitLossLine[]): AggregatedRow[] {
  const map = new Map<string, AggregatedRow>()

  for (const row of current) {
    map.set(row.account_number, {
      key: row.account_number,
      account: row.account_number,
      accountName: row.account_name,
      current: row.amount,
      previous: 0,
    })
  }

  for (const row of previous) {
    const existing = map.get(row.account_number)
    if (existing) {
      existing.previous = row.amount
    } else {
      map.set(row.account_number, {
        key: row.account_number,
        account: row.account_number,
        accountName: row.account_name,
        current: 0,
        previous: row.amount,
      })
    }
  }

  return Array.from(map.values()).sort((a, b) => a.account.localeCompare(b.account))
}

export function ProfitLossTable({
  currentRevenue,
  currentExpenses,
  previousRevenue,
  previousExpenses,
}: ProfitLossTableProps): JSX.Element {
  const [openRevenue, setOpenRevenue] = useState(true)
  const [openExpenses, setOpenExpenses] = useState(true)

  const rowsRevenue = useMemo(
    () => aggregateRows(currentRevenue, previousRevenue),
    [currentRevenue, previousRevenue],
  )
  const rowsExpenses = useMemo(
    () => aggregateRows(currentExpenses, previousExpenses),
    [currentExpenses, previousExpenses],
  )

  const renderRows = (rows: AggregatedRow[]): JSX.Element[] =>
    rows.map((row) => {
      const delta = row.current - row.previous
      const base = Math.abs(row.previous) > 0.001 ? Math.abs(row.previous) : 1
      const deltaPercent = (delta / base) * 100
      const barWidth = `${Math.min(100, Math.abs(deltaPercent))}%`

      return (
        <tr key={row.key} className={styles.dataRow}>
          <td className={styles.accountColumn}>{row.account}</td>
          <td>{row.accountName}</td>
          <td className={styles.numberColumn}>{currencyFormatter.format(row.current)}</td>
          <td className={styles.numberColumn}>{currencyFormatter.format(row.previous)}</td>
          <td className={styles.deltaColumn}>
            <span className={delta >= 0 ? styles.deltaPositive : styles.deltaNegative}>
              {deltaPercent.toFixed(1)}%
            </span>
            <span className={styles.deltaBarTrack}>
              <span
                className={delta >= 0 ? styles.deltaBarPositive : styles.deltaBarNegative}
                style={{ width: barWidth }}
              />
            </span>
          </td>
        </tr>
      )
    })

  return (
    <div className={styles.tablePanel}>
      <div className={styles.panelHeader}>
        <h3>GuV Deep-Dive</h3>
        <p>Aktuell vs. Vorjahr inkl. Abweichungsindikator</p>
      </div>

      <div className={styles.tableScroller}>
        <table className={styles.table}>
          <thead>
            <tr>
              <th>Konto</th>
              <th>Bezeichnung</th>
              <th>Aktuell</th>
              <th>Vorjahr</th>
              <th>Delta</th>
            </tr>
          </thead>
          <tbody>
            <tr className={styles.sectionRow}>
              <td colSpan={5}>
                <button type="button" className={styles.sectionToggle} onClick={() => setOpenRevenue((v) => !v)}>
                  {openRevenue ? <ChevronDown size={16} /> : <ChevronRight size={16} />}
                  Erlöse
                </button>
              </td>
            </tr>
            {openRevenue ? renderRows(rowsRevenue) : null}

            <tr className={styles.sectionRow}>
              <td colSpan={5}>
                <button type="button" className={styles.sectionToggle} onClick={() => setOpenExpenses((v) => !v)}>
                  {openExpenses ? <ChevronDown size={16} /> : <ChevronRight size={16} />}
                  Aufwendungen
                </button>
              </td>
            </tr>
            {openExpenses ? renderRows(rowsExpenses) : null}
          </tbody>
        </table>
      </div>
    </div>
  )
}
