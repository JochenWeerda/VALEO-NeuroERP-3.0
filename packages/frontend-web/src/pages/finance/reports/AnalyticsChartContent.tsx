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

interface AnalyticsChartContentProps {
  cashflow: CashflowPoint[]
  balanceShares: BalanceShare[]
}

const currencyFormatter = new Intl.NumberFormat('de-DE', {
  style: 'currency',
  currency: 'EUR',
  maximumFractionDigits: 0,
})

const donutColors = ['#005599', '#0EA870', '#D94A66']

const AnalyticsCashflowChart = lazy(() => import('./charts/AnalyticsCashflowChart'))
const AnalyticsBalanceShareChart = lazy(() => import('./charts/AnalyticsBalanceShareChart'))

function ChartFallback(): JSX.Element {
  return <div className={styles.chartCanvas} />
}

export default function AnalyticsChartContent({ cashflow, balanceShares }: AnalyticsChartContentProps): JSX.Element {
  return (
    <section className={styles.analyticsGrid}>
      <article className={styles.chartCard}>
        <div className={styles.panelHeader}>
          <h3>Cashflow Verlauf</h3>
          <p>Zufluesse vs. Abfluesse und Netto-Effekt</p>
        </div>
        <div className={styles.chartCanvas}>
          <Suspense fallback={<ChartFallback />}>
            <AnalyticsCashflowChart cashflow={cashflow} currencyFormatter={currencyFormatter} />
          </Suspense>
        </div>
      </article>

      <article className={styles.chartCard}>
        <div className={styles.panelHeader}>
          <h3>Bilanz-Verteilung</h3>
          <p>Aktiva, Fremdkapital, Eigenkapital</p>
        </div>
        <div className={styles.chartCanvas}>
          <Suspense fallback={<ChartFallback />}>
            <AnalyticsBalanceShareChart
              balanceShares={balanceShares}
              donutColors={donutColors}
              currencyFormatter={currencyFormatter}
            />
          </Suspense>
        </div>
        <div className={styles.legend}>
          {balanceShares.map((item, index) => (
            <div key={item.name} className={styles.legendItem}>
              <span className={styles.legendDot} style={{ backgroundColor: donutColors[index % donutColors.length] }} />
              <span>{item.name}</span>
              <strong>{currencyFormatter.format(item.value)}</strong>
            </div>
          ))}
        </div>
      </article>
    </section>
  )
}
