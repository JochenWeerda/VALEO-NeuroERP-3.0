import { Suspense, lazy, type JSX } from 'react'
import styles from '../reports.module.css'

interface CashflowPoint {
  period: string
  inflow: number
  outflow: number
  net: number
}

interface BalanceShare {
  name: string
  value: number
}

interface AnalyticsChartProps {
  cashflow: CashflowPoint[]
  balanceShares: BalanceShare[]
}

const AnalyticsChartContent = lazy(() => import('./AnalyticsChartContent'))

export function AnalyticsChart({ cashflow, balanceShares }: AnalyticsChartProps): JSX.Element {
  return (
    <Suspense fallback={<section className={styles.analyticsGrid}><article className={styles.chartCard} /><article className={styles.chartCard} /></section>}>
      <AnalyticsChartContent cashflow={cashflow} balanceShares={balanceShares} />
    </Suspense>
  )
}
