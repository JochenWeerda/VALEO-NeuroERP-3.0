import { type JSX } from 'react'

interface FinancialCardSparklineProps {
  sparkline: Array<{ period: string; value: number }>
  deltaPositive: boolean
}

export default function FinancialCardSparkline({ sparkline, deltaPositive }: FinancialCardSparklineProps): JSX.Element {
  const width = 180
  const height = 72
  const padding = 6
  const values = sparkline.map((item) => item.value)
  const maxValue = Math.max(...values, 1)
  const minValue = Math.min(...values, 0)
  const range = Math.max(maxValue - minValue, 1)
  const points = sparkline
    .map((item, index) => {
      const x = sparkline.length > 1 ? (index / (sparkline.length - 1)) * (width - padding * 2) + padding : width / 2
      const y = height - padding - ((item.value - minValue) / range) * (height - padding * 2)
      return `${x},${y}`
    })
    .join(' ')

  return (
    <svg viewBox={`0 0 ${width} ${height}`} className="h-full w-full overflow-visible">
      <polyline
        fill="none"
        stroke={deltaPositive ? '#0EA870' : '#D94A66'}
        strokeWidth="2.5"
        points={points}
        strokeLinejoin="round"
        strokeLinecap="round"
      />
    </svg>
  )
}
