/**
 * InlineValidationMessage — Domain-spezifische Inline-Validierungshinweise
 *
 * Gap 026: Inline-Validierung mit domain-spezifischen Erklärungen
 * Zeigt strukturierte Fehlermeldungen unter Eingabefeldern an:
 * - ERROR:   rot, blockiert Speichern
 * - WARNING: gelb, Speichern möglich
 * - INFO:    blau, Hinweis
 *
 * Verwendung:
 *   <InlineValidationMessage result={validateGln(value)} />
 */

import React from 'react'
import { AlertTriangle, AlertCircle, Info, CheckCircle2 } from 'lucide-react'
import { cn } from '@/lib/utils'

export type ValidationSeverity = 'ERROR' | 'WARNING' | 'INFO'

export interface ValidationMessageData {
  title: string
  detail: string
  severity: ValidationSeverity
  suggestion?: string
  field_name?: string
}

export interface ValidationResultData {
  field_name: string
  is_valid: boolean
  has_errors: boolean
  has_warnings: boolean
  messages: ValidationMessageData[]
}

interface InlineValidationMessageProps {
  result: ValidationResultData | null
  /** Zeigt grünen Haken wenn gültig (default: false) */
  showSuccessIcon?: boolean
  className?: string
}

const _iconFor = (severity: ValidationSeverity) => {
  switch (severity) {
    case 'ERROR':
      return <AlertTriangle className="h-3.5 w-3.5 flex-shrink-0 mt-0.5" />
    case 'WARNING':
      return <AlertCircle className="h-3.5 w-3.5 flex-shrink-0 mt-0.5" />
    case 'INFO':
      return <Info className="h-3.5 w-3.5 flex-shrink-0 mt-0.5" />
  }
}

const _colorFor = (severity: ValidationSeverity) => {
  switch (severity) {
    case 'ERROR':
      return 'text-red-600'
    case 'WARNING':
      return 'text-amber-600'
    case 'INFO':
      return 'text-blue-600'
  }
}

const _bgFor = (severity: ValidationSeverity) => {
  switch (severity) {
    case 'ERROR':
      return 'bg-red-50 border-red-200'
    case 'WARNING':
      return 'bg-amber-50 border-amber-200'
    case 'INFO':
      return 'bg-blue-50 border-blue-200'
  }
}

function SingleMessage({ msg }: { msg: ValidationMessageData }) {
  const color = _colorFor(msg.severity)
  const bg = _bgFor(msg.severity)

  return (
    <div
      role="alert"
      aria-live="polite"
      className={cn(
        'flex gap-2 rounded-md border px-3 py-2 text-xs',
        bg,
        color,
      )}
    >
      {_iconFor(msg.severity)}
      <div className="flex flex-col gap-0.5">
        <span className="font-semibold">{msg.title}</span>
        {msg.detail && (
          <span className="text-current opacity-80">{msg.detail}</span>
        )}
        {msg.suggestion && (
          <span className="italic opacity-70">{msg.suggestion}</span>
        )}
      </div>
    </div>
  )
}

export function InlineValidationMessage({
  result,
  showSuccessIcon = false,
  className,
}: InlineValidationMessageProps): JSX.Element | null {
  if (!result) return null

  if (result.is_valid && !result.has_warnings && result.messages.length === 0) {
    if (!showSuccessIcon) return null
    return (
      <div className={cn('flex items-center gap-1 text-xs text-green-600', className)}>
        <CheckCircle2 className="h-3.5 w-3.5" />
        <span>Gültig</span>
      </div>
    )
  }

  return (
    <div className={cn('mt-1 flex flex-col gap-1', className)}>
      {result.messages.map((msg, idx) => (
        <SingleMessage key={`${msg.severity}-${idx}`} msg={msg} />
      ))}
    </div>
  )
}

/**
 * Hilfsfunktion: Liefert border-Klasse für Input basierend auf Validierungszustand.
 *
 * Verwendung:
 *   <Input className={getFieldBorderClass(result)} />
 */
export function getFieldBorderClass(result: ValidationResultData | null): string {
  if (!result) return ''
  if (result.has_errors) return 'border-red-500 focus-visible:ring-red-500'
  if (result.has_warnings) return 'border-amber-400 focus-visible:ring-amber-400'
  if (result.is_valid && result.messages.length === 0) return 'border-green-400'
  return ''
}
