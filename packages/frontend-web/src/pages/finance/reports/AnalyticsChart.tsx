import type { JSX } from 'react'
import {
  Area,
  Bar,
  CartesianGrid,
  Cell,
  ComposedChart,
  Pie,
  PieChart,
  ResponsiveContainer,
  Tooltip,
  XAxis,
  YAxis,
} from 'recharts'
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

const currencyFormatter = new Intl.NumberFormat('de-DE', {
  style: 'currency',
  currency: 'EUR',
  maximumFractionDigits: 0,
})

const donutColors = ['#005599', '#0EA870', '#D94A66']

export function AnalyticsChart({ cashflow, balanceShares }: AnalyticsChartProps): JSX.Element {
  return (
    <section className={styles.analyticsGrid}>
      <article className={styles.chartCard}>
        <div className={styles.panelHeader}>
          <h3>Cashflow Verlauf</h3>
          <p>Zuflüsse vs. Abflüsse und Netto-Effekt</p>
        </div>
        <div className={styles.chartCanvas}>
          <ResponsiveContainer width="100%" height="100%">
            <ComposedChart data={cashflow}>
              <CartesianGrid stroke="#E2E8F0" strokeDasharray="3 3" />
              <XAxis dataKey="period" stroke="#64748B" />
              <YAxis stroke="#64748B" tickFormatter={(value) => `${Math.round(value / 1000)}k`} />
              <Tooltip formatter={(value: number) => currencyFormatter.format(value)} />
              <Area dataKey="net" fill="#00559933" stroke="#005599" strokeWidth={2} />
              <Bar dataKey="inflow" fill="#0EA870" radius={[6, 6, 0, 0]} />
              <Bar dataKey="outflow" fill="#D94A66" radius={[6, 6, 0, 0]} />
            </ComposedChart>
          </ResponsiveContainer>
        </div>
      </article>

      <article className={styles.chartCard}>
        <div className={styles.panelHeader}>
          <h3>Bilanz-Verteilung</h3>
          <p>Aktiva, Fremdkapital, Eigenkapital</p>
        </div>
        <div className={styles.chartCanvas}>
          <ResponsiveContainer width="100%" height="100%">
            <PieChart>
              <Pie
                data={balanceShares}
                dataKey="value"
                nameKey="name"
                innerRadius={70}
                outerRadius={110}
                paddingAngle={2}
              >
                {balanceShares.map((_, index) => (
                  <Cell key={index} fill={donutColors[index % donutColors.length]} />
                ))}
              </Pie>
              <Tooltip formatter={(value: number) => currencyFormatter.format(value)} />
            </PieChart>
          </ResponsiveContainer>
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
