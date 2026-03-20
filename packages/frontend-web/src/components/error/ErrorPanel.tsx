/**
 * ErrorPanel — Strukturierte Fehleranzeige mit Wiederherstellungsaktionen
 *
 * Gap 028: Leitsystem für Ausnahmefälle (Error UX)
 * Zeigt benutzerfreundliche Fehlermeldungen mit:
 * - Kategorie-Icon (Netzwerk, Berechtigung, Konflikt, ...)
 * - Titel + Erklärung auf Deutsch
 * - Konkreter Tipp ("Was kann ich tun?")
 * - Primäre + sekundäre Aktions-Buttons
 *
 * Verwendung:
 *   <ErrorPanel error={classifyHttpError(statusCode)} onAction={handleAction} />
 */

import React from 'react'
import {
  AlertTriangle,
  WifiOff,
  Lock,
  Search,
  ServerCrash,
  GitMerge,
  Clock,
  HelpCircle,
  RefreshCw,
  ArrowLeft,
  LogIn,
  LifeBuoy,
  Save,
} from 'lucide-react'
import { Button } from '@/components/ui/button'
import { cn } from '@/lib/utils'

export type ErrorCategory =
  | 'NETWORK'
  | 'VALIDATION'
  | 'AUTHORIZATION'
  | 'NOT_FOUND'
  | 'SERVER'
  | 'CONFLICT'
  | 'TIMEOUT'
  | 'BUSINESS_RULE'
  | 'UNKNOWN'

export type ErrorSeverity = 'BLOCKING' | 'RECOVERABLE' | 'WARNING'

export interface RecoveryActionData {
  label: string
  action_key: string
  primary: boolean
  icon?: string
}

export interface UserFacingErrorData {
  category: ErrorCategory
  severity: ErrorSeverity
  title: string
  detail: string
  recovery_actions: RecoveryActionData[]
  tip?: string
  support_code?: string
  data_loss_risk?: boolean
  primary_action?: RecoveryActionData | null
}

interface ErrorPanelProps {
  error: UserFacingErrorData
  onAction?: (actionKey: string) => void
  /** Kompakter Modus für Inline-Fehler (kein großes Icon, weniger Padding) */
  compact?: boolean
  className?: string
}

const _categoryIcon: Record<ErrorCategory, React.ReactNode> = {
  NETWORK:       <WifiOff className="h-8 w-8" />,
  VALIDATION:    <AlertTriangle className="h-8 w-8" />,
  AUTHORIZATION: <Lock className="h-8 w-8" />,
  NOT_FOUND:     <Search className="h-8 w-8" />,
  SERVER:        <ServerCrash className="h-8 w-8" />,
  CONFLICT:      <GitMerge className="h-8 w-8" />,
  TIMEOUT:       <Clock className="h-8 w-8" />,
  BUSINESS_RULE: <AlertTriangle className="h-8 w-8" />,
  UNKNOWN:       <HelpCircle className="h-8 w-8" />,
}

const _categoryColor: Record<ErrorCategory, string> = {
  NETWORK:       'text-slate-500 bg-slate-50 border-slate-200',
  VALIDATION:    'text-amber-600 bg-amber-50 border-amber-200',
  AUTHORIZATION: 'text-red-600 bg-red-50 border-red-200',
  NOT_FOUND:     'text-slate-500 bg-slate-50 border-slate-200',
  SERVER:        'text-red-600 bg-red-50 border-red-200',
  CONFLICT:      'text-orange-600 bg-orange-50 border-orange-200',
  TIMEOUT:       'text-amber-600 bg-amber-50 border-amber-200',
  BUSINESS_RULE: 'text-blue-600 bg-blue-50 border-blue-200',
  UNKNOWN:       'text-slate-600 bg-slate-50 border-slate-200',
}

const _actionIcon: Record<string, React.ReactNode> = {
  retry:          <RefreshCw className="h-4 w-4" />,
  reload:         <RefreshCw className="h-4 w-4" />,
  back:           <ArrowLeft className="h-4 w-4" />,
  login:          <LogIn className="h-4 w-4" />,
  contact_support: <LifeBuoy className="h-4 w-4" />,
  save_draft:     <Save className="h-4 w-4" />,
  refresh_merge:  <GitMerge className="h-4 w-4" />,
}

export function ErrorPanel({
  error,
  onAction,
  compact = false,
  className,
}: ErrorPanelProps): JSX.Element {
  const colorClass = _categoryColor[error.category] ?? _categoryColor.UNKNOWN
  const icon = _categoryIcon[error.category] ?? _categoryIcon.UNKNOWN

  return (
    <div
      role="alert"
      aria-live="assertive"
      className={cn(
        'flex flex-col gap-4 rounded-lg border p-6',
        colorClass,
        compact && 'p-4',
        className,
      )}
    >
      {/* Header */}
      <div className="flex items-start gap-3">
        {!compact && (
          <div className="flex-shrink-0 opacity-70">{icon}</div>
        )}
        <div className="flex flex-col gap-1">
          <h3 className={cn('font-semibold', compact ? 'text-sm' : 'text-base')}>
            {error.title}
          </h3>
          <p className={cn('opacity-80', compact ? 'text-xs' : 'text-sm')}>
            {error.detail}
          </p>
        </div>
      </div>

      {/* Datenverlust-Warnung */}
      {error.data_loss_risk && (
        <div className="flex items-center gap-2 rounded-md bg-white/60 px-3 py-2 text-xs font-medium">
          <AlertTriangle className="h-3.5 w-3.5 flex-shrink-0" />
          Möglicherweise gehen ungespeicherte Daten verloren.
        </div>
      )}

      {/* Tipp */}
      {error.tip && (
        <p className={cn('italic opacity-70', compact ? 'text-xs' : 'text-sm')}>
          💡 {error.tip}
        </p>
      )}

      {/* Aktionen */}
      {error.recovery_actions.length > 0 && (
        <div className="flex flex-wrap items-center gap-2">
          {error.recovery_actions.map((action) => (
            <Button
              key={action.action_key}
              variant={action.primary ? 'default' : 'outline'}
              size={compact ? 'sm' : 'default'}
              onClick={() => onAction?.(action.action_key)}
              className="gap-2"
            >
              {_actionIcon[action.action_key]}
              {action.label}
            </Button>
          ))}
        </div>
      )}

      {/* Support-Code */}
      {error.support_code && (
        <p className="text-right font-mono text-xs opacity-40">
          {error.support_code}
        </p>
      )}
    </div>
  )
}
