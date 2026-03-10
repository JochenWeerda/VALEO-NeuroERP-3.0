import { Suspense, lazy, useEffect, useRef, useState, type JSX } from 'react'
import { TrendingDown, TrendingUp } from 'lucide-react'
import styles from '../reports.module.css'

interface FinancialCardProps {
  label: string
  value: number
  deltaPercent: number
  sparkline: Array<{ period: string; value: number }>
  format?: 'currency' | 'number'
}

const currencyFormatter = new Intl.NumberFormat('de-DE', {
  style: 'currency',
  currency: 'EUR',
  maximumFractionDigits: 0,
})

const numberFormatter = new Intl.NumberFormat('de-DE', {
  maximumFractionDigits: 2,
})

const FinancialCardSparkline = lazy(() => import('./FinancialCardSparkline'))

export function FinancialCard(props: FinancialCardProps): JSX.Element {
  const { label, value, deltaPercent, sparkline, format = 'currency' } = props
  const deltaPositive = deltaPercent >= 0
  const [animatedValue, setAnimatedValue] = useState(0)
  const prevValueRef = useRef(0)

  useEffect(() => {
    const start = prevValueRef.current
    const end = value
    const duration = 700
    const startTime = performance.now()

    let frame = 0
    const step = (now: number) => {
      const progress = Math.min((now - startTime) / duration, 1)
      const eased = 1 - Math.pow(1 - progress, 3)
      setAnimatedValue(start + (end - start) * eased)
      if (progress < 1) {
        frame = requestAnimationFrame(step)
      } else {
        prevValueRef.current = end
      }
    }

    frame = requestAnimationFrame(step)
    return () => cancelAnimationFrame(frame)
  }, [value])

  return (
    <article className={styles.kpiCard}>
      <div className={styles.kpiHeader}>
        <p className={styles.kpiLabel}>{label}</p>
        <span className={deltaPositive ? styles.deltaPositive : styles.deltaNegative}>
          {deltaPositive ? <TrendingUp size={14} /> : <TrendingDown size={14} />}
          {numberFormatter.format(deltaPercent)}%
        </span>
      </div>

      <p className={styles.kpiValue}>
        {format === 'currency' ? currencyFormatter.format(animatedValue) : numberFormatter.format(animatedValue)}
      </p>

      <div className={styles.sparklineWrap}>
        <Suspense fallback={null}>
          <FinancialCardSparkline sparkline={sparkline} deltaPositive={deltaPositive} />
        </Suspense>
      </div>
    </article>
  )
}
