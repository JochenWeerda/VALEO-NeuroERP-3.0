/**
 * Trend Chart
 *
 * Einfaches Linien-/Balkendiagramm für Trends
 * Nutzt lazy-loaded Recharts für Performance
 */

import { useMemo } from 'react'
import { cn } from '@/lib/utils'
import { TrendingUp, TrendingDown, Minus } from 'lucide-react'
import { LazyAreaChart, LazyBarChart } from '@/components/ui/lazy-charts'

export interface TrendDataPoint {
  label: string
  value: number
  previousValue?: number
}

interface TrendChartProps {
  title: string
  data: TrendDataPoint[]
  type?: 'line' | 'bar' | 'area'
  color?: 'primary' | 'success' | 'warning' | 'danger'
  height?: number
  showLegend?: boolean
  showGrid?: boolean
  formatValue?: (value: number) => string
  className?: string
}

const colorMap = {
  primary: {
    stroke: 'hsl(var(--chart-1-hsl))',
    fill: 'hsl(var(--chart-1-hsl) / 0.1)',
  },
  success: {
    stroke: 'hsl(var(--status-success-hsl))',
    fill: 'hsl(var(--status-success-hsl) / 0.1)',
  },
  warning: {
    stroke: 'hsl(var(--status-warning-hsl))',
    fill: 'hsl(var(--status-warning-hsl) / 0.1)',
  },
  danger: {
    stroke: 'hsl(var(--status-error-hsl))',
    fill: 'hsl(var(--status-error-hsl) / 0.1)',
  },
}

export function TrendChart({
  title,
  data,
  type = 'area',
  color = 'primary',
  height = 200,
  showLegend = false,
  showGrid = true,
  formatValue = (v) => v.toLocaleString('de-DE'),
  className,
}: TrendChartProps) {
  void showGrid
  // Berechne Trend
  const trend = useMemo(() => {
    if (data.length < 2) return null

    const current = data[data.length - 1].value
    const previous = data[data.length - 2].value
    const change = previous !== 0 ? ((current - previous) / previous) * 100 : 0

    return {
      direction: change > 0 ? 'up' : change < 0 ? 'down' : 'neutral',
      value: Math.abs(change).toFixed(1),
      current,
      previous,
    }
  }, [data])

  // Summe/Durchschnitt berechnen
  const summary = useMemo(() => {
    const sum = data.reduce((acc, d) => acc + d.value, 0)
    const avg = data.length > 0 ? sum / data.length : 0
    return { sum, avg }
  }, [data])

  const colors = colorMap[color]

  // Chart-Daten transformieren
  const chartData = data.map((d) => ({
    name: d.label,
    value: d.value,
    previousValue: d.previousValue,
  }))

  return (
    <div className={cn('bg-card rounded-xl border p-4', className)}>
      {/* Header */}
      <div className="flex items-start justify-between mb-4">
        <div>
          <h3 className="font-semibold text-muted-foreground">{title}</h3>
          <p className="text-2xl font-bold mt-1">
            {formatValue(summary.sum)}
          </p>
        </div>

        {trend && (
          <div
            className={cn(
              'flex items-center gap-1 px-2 py-1 rounded text-sm font-medium',
              trend.direction === 'up'
                ? 'bg-status-success/10 text-status-success'
                : trend.direction === 'down'
                  ? 'bg-status-error/10 text-status-error'
                  : 'bg-muted text-muted-foreground'
            )}
          >
            {trend.direction === 'up' && <TrendingUp className="h-4 w-4" />}
            {trend.direction === 'down' && <TrendingDown className="h-4 w-4" />}
            {trend.direction === 'neutral' && <Minus className="h-4 w-4" />}
            {trend.direction === 'up' && '+'}
            {trend.value}%
          </div>
        )}
      </div>

      {/* Chart */}
      <div style={{ height }}>
        {type === 'bar' ? (
          <LazyBarChart
            data={chartData}
            dataKey="value"
            fill={colors.stroke}
            height={height}
          />
        ) : (
          <LazyAreaChart
            data={chartData}
            dataKey="value"
            stroke={colors.stroke}
            fill={colors.fill}
            height={height}
          />
        )}
      </div>

      {/* Legend / Summary */}
      {showLegend && (
        <div className="flex items-center justify-between mt-4 pt-4 border-t text-sm">
          <div className="flex items-center gap-4">
            <div className="flex items-center gap-2">
              <div
                className="w-3 h-3 rounded-full"
                style={{ backgroundColor: colors.stroke }}
              />
              <span className="text-muted-foreground">Aktuell</span>
            </div>
          </div>
          <div className="text-muted-foreground">
            Ø {formatValue(summary.avg)}
          </div>
        </div>
      )}
    </div>
  )
}

/**
 * Mini Trend Indicator
 */
export function TrendIndicator({
  value,
  previousValue,
  format = 'percent',
  size = 'md',
  className,
}: {
  value: number
  previousValue: number
  format?: 'percent' | 'absolute' | 'both'
  size?: 'sm' | 'md' | 'lg'
  className?: string
}) {
  const change = previousValue !== 0 ? ((value - previousValue) / previousValue) * 100 : 0
  const absoluteChange = value - previousValue
  const direction = change > 0 ? 'up' : change < 0 ? 'down' : 'neutral'

  const sizeStyles = {
    sm: 'text-xs gap-0.5',
    md: 'text-sm gap-1',
    lg: 'text-base gap-1.5',
  }

  const iconSizes = {
    sm: 'h-3 w-3',
    md: 'h-4 w-4',
    lg: 'h-5 w-5',
  }

  const directionStyles = {
    up: 'text-status-success',
    down: 'text-status-error',
    neutral: 'text-muted-foreground',
  }

  return (
    <span
      className={cn(
        'inline-flex items-center font-medium',
        sizeStyles[size],
        directionStyles[direction],
        className
      )}
    >
      {direction === 'up' && <TrendingUp className={iconSizes[size]} />}
      {direction === 'down' && <TrendingDown className={iconSizes[size]} />}
      {direction === 'neutral' && <Minus className={iconSizes[size]} />}

      {format === 'percent' && (
        <span>
          {direction === 'up' && '+'}
          {change.toFixed(1)}%
        </span>
      )}

      {format === 'absolute' && (
        <span>
          {absoluteChange > 0 && '+'}
          {absoluteChange.toLocaleString('de-DE')}
        </span>
      )}

      {format === 'both' && (
        <span>
          {absoluteChange > 0 && '+'}
          {absoluteChange.toLocaleString('de-DE')} ({change.toFixed(1)}%)
        </span>
      )}
    </span>
  )
}

