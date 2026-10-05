/**
 * Alert Widget
 *
 * Zeigt wichtige Warnungen und Handlungsbedarf für Management
 * Kategorisiert nach Dringlichkeit
 */

import { ReactNode } from 'react'
import { Badge, type BadgeVariant } from '@/components/ui/badge'
import { Link } from '@/app/routing/typed-router'
import { cn } from '@/lib/utils'
import {
  AlertTriangle,
  AlertCircle,
  Info,
  CheckCircle2,
  ChevronRight,
  Clock,
  TrendingDown,
  Package,
  Users,
  CreditCard,
  FileWarning,
} from 'lucide-react'

export interface AlertItem {
  id: string
  type: 'critical' | 'warning' | 'info' | 'success'
  category: 'finance' | 'inventory' | 'sales' | 'customer' | 'system'
  title: string
  description?: string
  value?: string | number
  timestamp?: string
  actionLabel?: string
  actionUrl?: string
  onAction?: () => void
}

interface AlertWidgetProps {
  title?: string
  alerts: AlertItem[]
  maxItems?: number
  showCategories?: boolean
  onViewAll?: () => void
  className?: string
}

const typeStyles = {
  critical: {
    icon: 'text-status-error',
    badge: 'error' as BadgeVariant,
  },
  warning: {
    icon: 'text-status-warning',
    badge: 'warning' as BadgeVariant,
  },
  info: {
    icon: 'text-status-info',
    badge: 'info' as BadgeVariant,
  },
  success: {
    icon: 'text-status-success',
    badge: 'success' as BadgeVariant,
  },
}

const typeIcons = {
  critical: AlertCircle,
  warning: AlertTriangle,
  info: Info,
  success: CheckCircle2,
}

const categoryIcons: Record<AlertItem['category'], ReactNode> = {
  finance: <CreditCard className="h-4 w-4" />,
  inventory: <Package className="h-4 w-4" />,
  sales: <TrendingDown className="h-4 w-4" />,
  customer: <Users className="h-4 w-4" />,
  system: <FileWarning className="h-4 w-4" />,
}

const categoryLabels: Record<AlertItem['category'], string> = {
  finance: 'Finanzen',
  inventory: 'Lager',
  sales: 'Vertrieb',
  customer: 'Kunden',
  system: 'System',
}

export function AlertWidget({
  title = 'Handlungsbedarf',
  alerts,
  maxItems = 5,
  showCategories = true,
  onViewAll,
  className,
}: AlertWidgetProps) {
  // Sortiere nach Priorität
  const sortedAlerts = [...alerts].sort((a, b) => {
    const priority = { critical: 0, warning: 1, info: 2, success: 3 }
    return priority[a.type] - priority[b.type]
  })

  const displayAlerts = sortedAlerts.slice(0, maxItems)
  const remainingCount = alerts.length - maxItems

  // Zähle kritische Alerts
  const criticalCount = alerts.filter(a => a.type === 'critical').length
  const warningCount = alerts.filter(a => a.type === 'warning').length

  return (
    <div className={cn('bg-card rounded-xl border overflow-hidden', className)}>
      {/* Header */}
      <div className="flex items-center justify-between px-4 py-3 border-b bg-muted/30">
        <div className="flex items-center gap-3">
          <h3 className="font-semibold">{title}</h3>
          {criticalCount > 0 && (
            <Badge variant="error" className="rounded-full px-2 py-0.5 font-bold">
              {criticalCount} kritisch
            </Badge>
          )}
          {warningCount > 0 && (
            <Badge variant="warning" className="rounded-full px-2 py-0.5 font-bold">
              {warningCount} Warnung
            </Badge>
          )}
        </div>
        {onViewAll && (
          <button
            onClick={onViewAll}
            className="text-sm text-primary hover:underline"
          >
            Alle anzeigen
          </button>
        )}
      </div>

      {/* Alert Liste */}
      <div className="divide-y">
        {displayAlerts.length === 0 ? (
          <div className="px-4 py-8 text-center text-muted-foreground">
            <CheckCircle2 className="h-10 w-10 mx-auto mb-2 text-status-success" />
            <p>Keine offenen Meldungen</p>
          </div>
        ) : (
          displayAlerts.map((alert) => (
            <AlertItemRow
              key={alert.id}
              alert={alert}
              showCategory={showCategories}
            />
          ))
        )}
      </div>

      {/* Footer */}
      {remainingCount > 0 && (
        <button
          onClick={onViewAll}
          className="w-full px-4 py-3 text-sm text-center text-muted-foreground hover:bg-muted/50 transition-colors border-t"
        >
          + {remainingCount} weitere Meldungen
        </button>
      )}
    </div>
  )
}

function AlertItemRow({
  alert,
  showCategory,
}: {
  alert: AlertItem
  showCategory: boolean
}) {
  const styles = typeStyles[alert.type]
  const Icon = typeIcons[alert.type]

  const content = (
    <div className={cn('px-4 py-3 transition-colors', 'hover:bg-muted/30')}>
      <div className="flex items-start gap-3">
        {/* Icon */}
        <div className={cn('shrink-0 mt-0.5', styles.icon)}>
          <Icon className="h-5 w-5" />
        </div>

        {/* Content */}
        <div className="flex-1 min-w-0">
          <div className="flex items-center gap-2 flex-wrap">
            <p className="font-medium">{alert.title}</p>
            {showCategory && (
              <Badge variant={styles.badge} className="gap-1 rounded px-1.5 py-0.5">
                {categoryIcons[alert.category]}
                {categoryLabels[alert.category]}
              </Badge>
            )}
          </div>

          {alert.description && (
            <p className="text-sm text-muted-foreground mt-0.5">
              {alert.description}
            </p>
          )}

          <div className="flex items-center gap-4 mt-2">
            {alert.value && (
              <span className="text-sm font-medium">{alert.value}</span>
            )}
            {alert.timestamp && (
              <span className="flex items-center gap-1 text-xs text-muted-foreground">
                <Clock className="h-3 w-3" />
                {alert.timestamp}
              </span>
            )}
          </div>
        </div>

        {/* Action */}
        {(alert.actionUrl || alert.onAction) && (
          <ChevronRight className="h-5 w-5 text-muted-foreground shrink-0" />
        )}
      </div>
    </div>
  )

  if (alert.actionUrl) {
    return (
      <Link to={alert.actionUrl} className="block">
        {content}
      </Link>
    )
  }

  if (alert.onAction) {
    return (
      <button onClick={alert.onAction} className="w-full text-left">
        {content}
      </button>
    )
  }

  return content
}

/**
 * Kompakte Alert-Zusammenfassung
 */
export function AlertSummary({
  alerts,
  onClick,
  className,
}: {
  alerts: AlertItem[]
  onClick?: () => void
  className?: string
}) {
  const critical = alerts.filter(a => a.type === 'critical').length
  const warning = alerts.filter(a => a.type === 'warning').length
  const info = alerts.filter(a => a.type === 'info').length

  if (critical === 0 && warning === 0 && info === 0) {
    return null
  }

  return (
    <button
      onClick={onClick}
      className={cn(
        'flex items-center gap-2 px-3 py-1.5 rounded-lg transition-colors',
        critical > 0
          ? 'bg-[hsl(var(--color-semantic-error-50-hsl))] text-status-error hover:bg-[hsl(var(--color-semantic-error-500-hsl)/0.18)]'
          : warning > 0
            ? 'bg-[hsl(var(--color-semantic-warning-50-hsl))] text-status-warning hover:bg-[hsl(var(--color-semantic-warning-500-hsl)/0.18)]'
            : 'bg-[hsl(var(--color-semantic-info-50-hsl))] text-status-info hover:bg-[hsl(var(--color-semantic-info-500-hsl)/0.18)]',
        className
      )}
    >
      {critical > 0 && (
        <span className="flex items-center gap-1">
          <AlertCircle className="h-4 w-4" />
          {critical}
        </span>
      )}
      {warning > 0 && (
        <span className="flex items-center gap-1">
          <AlertTriangle className="h-4 w-4" />
          {warning}
        </span>
      )}
      {info > 0 && critical === 0 && warning === 0 && (
        <span className="flex items-center gap-1">
          <Info className="h-4 w-4" />
          {info}
        </span>
      )}
    </button>
  )
}
