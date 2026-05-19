import * as React from 'react'
import { type LucideIcon, TrendingDown, TrendingUp } from 'lucide-react'
import { cn } from '@/lib/utils'

type KpiAccent = 'primary' | 'amber' | 'green' | 'red' | 'neutral'

interface KpiCardProps {
  title: string
  value: string | number
  icon?: LucideIcon
  trend?: number
  trendLabel?: string
  accent?: KpiAccent
  className?: string
}

const accentStyles: Record<KpiAccent, string> = {
  primary: 'border-l-primary bg-primary/5',
  amber:   'border-l-amber-500 bg-amber-50 dark:bg-amber-950/30',
  green:   'border-l-green-600 bg-green-50 dark:bg-green-950/30',
  red:     'border-l-red-500 bg-red-50 dark:bg-red-950/30',
  neutral: 'border-l-muted-foreground/30 bg-muted/30',
}

const iconStyles: Record<KpiAccent, string> = {
  primary: 'text-primary',
  amber:   'text-amber-600',
  green:   'text-green-600',
  red:     'text-red-600',
  neutral: 'text-muted-foreground',
}

export function KpiCard({
  title,
  value,
  icon: Icon,
  trend,
  trendLabel,
  accent = 'primary',
  className,
}: KpiCardProps): JSX.Element {
  const isPositive = trend !== undefined && trend > 0
  const isNegative = trend !== undefined && trend < 0

  return (
    <div
      className={cn(
        'rounded-lg border-l-[3px] p-4 shadow-sm transition-shadow hover:shadow-md',
        accentStyles[accent],
        className,
      )}
    >
      <div className="flex items-start justify-between">
        <p className="text-[11px] font-semibold uppercase tracking-[0.05em] text-muted-foreground">
          {title}
        </p>
        {Icon && <Icon className={cn('h-4 w-4', iconStyles[accent])} />}
      </div>
      <p className="mt-2 text-2xl font-bold tabular-nums text-foreground">{value}</p>
      {trend !== undefined && (
        <div
          className={cn(
            'mt-1 flex items-center gap-1 text-xs font-medium',
            isPositive && 'text-green-600',
            isNegative && 'text-red-600',
            !isPositive && !isNegative && 'text-muted-foreground',
          )}
        >
          {isPositive && <TrendingUp className="h-3 w-3" />}
          {isNegative && <TrendingDown className="h-3 w-3" />}
          <span>
            {isPositive ? '+' : ''}{trend}%{trendLabel ? ` ${trendLabel}` : ''}
          </span>
        </div>
      )}
    </div>
  )
}
