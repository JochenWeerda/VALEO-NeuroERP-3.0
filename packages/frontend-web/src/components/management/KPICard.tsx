/**
 * KPI Card
 *
 * Kompakte Anzeige von Kennzahlen für Management Dashboard
 * Metro Design, responsive für Desktop und Tablet
 */

import { ReactNode } from 'react'
import { cn } from '@/lib/utils'
import { TrendingUp, TrendingDown, Minus, ArrowRight, Info } from 'lucide-react'
import {
  Tooltip,
  TooltipContent,
  TooltipProvider,
  TooltipTrigger,
} from '@/components/ui/tooltip'

export interface KPICardProps {
  title: string
  value: string | number
  unit?: string
  trend?: {
    value: number
    label?: string
    period?: string
  }
  target?: {
    value: number
    label?: string
  }
  icon?: ReactNode
  color?: 'default' | 'primary' | 'success' | 'warning' | 'danger'
  size?: 'sm' | 'md' | 'lg'
  loading?: boolean
  onClick?: () => void
  tooltip?: string
  sparkline?: number[]
  className?: string
}

const colorStyles = {
  default: {
    bg: 'bg-card',
    icon: 'bg-muted text-muted-foreground',
    value: 'text-foreground',
  },
  primary: {
    bg: 'bg-primary/5 border-primary/20',
    icon: 'bg-primary/10 text-primary',
    value: 'text-primary',
  },
  success: {
    bg: 'bg-[hsl(var(--color-semantic-success-50-hsl))] border-[hsl(var(--color-semantic-success-500-hsl)/0.25)]',
    icon: 'bg-[hsl(var(--color-semantic-success-500-hsl)/0.15)] text-[hsl(var(--color-semantic-success-700-hsl))]',
    value: 'text-[hsl(var(--color-semantic-success-700-hsl))]',
  },
  warning: {
    bg: 'bg-secondary border-accent/30',
    icon: 'bg-accent/20 text-accent-foreground',
    value: 'text-accent-foreground',
  },
  danger: {
    bg: 'bg-destructive/5 border-destructive/25',
    icon: 'bg-destructive/10 text-destructive',
    value: 'text-destructive',
  },
}

const sizeStyles = {
  sm: {
    card: 'p-3',
    title: 'text-xs',
    value: 'text-xl',
    icon: 'h-8 w-8',
    iconSize: 'h-4 w-4',
  },
  md: {
    card: 'p-4',
    title: 'text-sm',
    value: 'text-2xl',
    icon: 'h-10 w-10',
    iconSize: 'h-5 w-5',
  },
  lg: {
    card: 'p-5',
    title: 'text-sm',
    value: 'text-3xl',
    icon: 'h-12 w-12',
    iconSize: 'h-6 w-6',
  },
}

export function KPICard({
  title,
  value,
  unit,
  trend,
  target,
  icon,
  color = 'default',
  size = 'md',
  loading = false,
  onClick,
  tooltip,
  sparkline,
  className,
}: KPICardProps) {
  const colors = colorStyles[color]
  const sizes = sizeStyles[size]

  // Trend-Berechnung
  const trendDirection = trend
    ? trend.value > 0
      ? 'up'
      : trend.value < 0
        ? 'down'
        : 'neutral'
    : null

  const trendColors = {
    up: 'text-emerald-600',
    down: 'text-red-600',
    neutral: 'text-muted-foreground',
  }

  // Target-Erreichung
  const targetProgress = target
    ? typeof value === 'number'
      ? (value / target.value) * 100
      : 0
    : null

  const content = (
    <div
      className={cn(
        'rounded-xl border transition-all',
        colors.bg,
        sizes.card,
        onClick && 'cursor-pointer hover:shadow-md active:scale-[0.98]',
        loading && 'animate-pulse',
        className
      )}
      onClick={onClick}
    >
      <div className="flex items-start justify-between gap-3">
        {/* Icon */}
        {icon && (
          <div
            className={cn(
              'shrink-0 flex items-center justify-center rounded-lg',
              colors.icon,
              sizes.icon
            )}
          >
            {icon}
          </div>
        )}

        {/* Content */}
        <div className="flex-1 min-w-0">
          {/* Title */}
          <div className="flex items-center gap-1.5">
            <h3
              className={cn(
                'font-medium text-muted-foreground truncate',
                sizes.title
              )}
            >
              {title}
            </h3>
            {tooltip && (
              <TooltipProvider>
                <Tooltip>
                  <TooltipTrigger>
                    <Info className="h-3.5 w-3.5 text-muted-foreground/50" />
                  </TooltipTrigger>
                  <TooltipContent>
                    <p className="text-sm">{tooltip}</p>
                  </TooltipContent>
                </Tooltip>
              </TooltipProvider>
            )}
          </div>

          {/* Value */}
          <div className="flex items-baseline gap-1.5 mt-1">
            {loading ? (
              <div className="h-8 w-24 bg-muted rounded animate-pulse" />
            ) : (
              <>
                <span className={cn('font-bold tabular-nums', sizes.value, colors.value)}>
                  {typeof value === 'number' ? value.toLocaleString('de-DE') : value}
                </span>
                {unit && (
                  <span className="text-sm text-muted-foreground">{unit}</span>
                )}
              </>
            )}
          </div>

          {/* Trend */}
          {trend && trendDirection && (
            <div className="flex items-center gap-1.5 mt-2">
              <span className={cn('flex items-center gap-0.5 text-sm font-medium', trendColors[trendDirection])}>
                {trendDirection === 'up' && <TrendingUp className="h-4 w-4" />}
                {trendDirection === 'down' && <TrendingDown className="h-4 w-4" />}
                {trendDirection === 'neutral' && <Minus className="h-4 w-4" />}
                {trend.value > 0 && '+'}
                {trend.value}%
              </span>
              {trend.period && (
                <span className="text-xs text-muted-foreground">{trend.period}</span>
              )}
            </div>
          )}

          {/* Target Progress */}
          {target && targetProgress !== null && (
            <div className="mt-3">
              <div className="flex items-center justify-between text-xs mb-1">
                <span className="text-muted-foreground">{target.label || 'Ziel'}</span>
                <span className="font-medium">
                  {targetProgress.toFixed(0)}%
                </span>
              </div>
              <div className="h-1.5 bg-muted rounded-full overflow-hidden">
                <div
                  className={cn(
                    'h-full rounded-full transition-all',
                    targetProgress >= 100
                      ? 'bg-emerald-500'
                      : targetProgress >= 75
                        ? 'bg-primary'
                        : targetProgress >= 50
                          ? 'bg-amber-500'
                          : 'bg-red-500'
                  )}
                  style={{ width: `${Math.min(targetProgress, 100)}%` }}
                />
              </div>
            </div>
          )}

          {/* Sparkline */}
          {sparkline && sparkline.length > 0 && (
            <div className="mt-3">
              <Sparkline data={sparkline} color={color} />
            </div>
          )}
        </div>

        {/* Arrow for clickable */}
        {onClick && (
          <ArrowRight className="h-5 w-5 text-muted-foreground shrink-0" />
        )}
      </div>
    </div>
  )

  return content
}

/**
 * Mini Sparkline Chart
 */
function Sparkline({
  data,
  color = 'default',
}: {
  data: number[]
  color?: string
}) {
  const max = Math.max(...data)
  const min = Math.min(...data)
  const range = max - min || 1

  const points = data.map((value, index) => {
    const x = (index / (data.length - 1)) * 100
    const y = 100 - ((value - min) / range) * 100
    return `${x},${y}`
  })

  const strokeColor =
    color === 'success'
      ? 'stroke-emerald-500'
      : color === 'danger'
        ? 'stroke-red-500'
        : color === 'warning'
          ? 'stroke-amber-500'
          : color === 'primary'
            ? 'stroke-primary'
            : 'stroke-muted-foreground'

  return (
    <svg
      viewBox="0 0 100 30"
      preserveAspectRatio="none"
      className="w-full h-8"
    >
      <polyline
        points={points.join(' ')}
        fill="none"
        strokeWidth="2"
        strokeLinecap="round"
        strokeLinejoin="round"
        className={strokeColor}
      />
    </svg>
  )
}

/**
 * KPI Card Grid
 */
export function KPIGrid({
  children,
  columns = 4,
  className,
}: {
  children: ReactNode
  columns?: 2 | 3 | 4 | 5 | 6
  className?: string
}) {
  const gridCols = {
    2: 'grid-cols-1 sm:grid-cols-2',
    3: 'grid-cols-1 sm:grid-cols-2 lg:grid-cols-3',
    4: 'grid-cols-1 sm:grid-cols-2 lg:grid-cols-4',
    5: 'grid-cols-1 sm:grid-cols-2 lg:grid-cols-5',
    6: 'grid-cols-1 sm:grid-cols-2 md:grid-cols-3 lg:grid-cols-6',
  }

  return (
    <div className={cn('grid gap-4', gridCols[columns], className)}>
      {children}
    </div>
  )
}
