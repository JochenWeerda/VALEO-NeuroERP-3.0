/**
 * PolicyExplanationBadge — Kompakter Inline-Badge für Policy-Entscheidungen
 *
 * Gap 019: Policy Explainability im UI
 * Zeigt "✓ Freigegeben", "✗ Abgelehnt", "⚠ Warnung" oder "↑ Eskalation"
 * mit Tooltip der die entscheidende Regel erklärt.
 *
 * Verwendung:
 *   <PolicyExplanationBadge explanation={explanation} />
 */

import React from 'react'
import { CheckCircle2, XCircle, AlertTriangle, ArrowUpCircle, HelpCircle } from 'lucide-react'
import { cn } from '@/lib/utils'

export type EntscheidungsErgebnis =
  | 'FREIGEGEBEN'
  | 'ABGELEHNT'
  | 'WARNUNG'
  | 'ESKALATION'
  | 'KEINE_REGEL'

export interface PolicyReasonEntryData {
  regel_id: string
  regel_name: string
  aktion: string
  ergebnis_text: string
  ist_entscheidend: boolean
}

export interface PolicyExplanationData {
  entscheidung: EntscheidungsErgebnis
  zusammenfassung: string
  gruende: PolicyReasonEntryData[]
  anzahl_gepruefter_regeln: number
  ist_freigegeben: boolean
  tenant_override_aktiv: boolean
  icon: string
  badge_farbe: string
  prozess_key?: string
}

interface PolicyExplanationBadgeProps {
  explanation: PolicyExplanationData
  /** Zeigt Details unterhalb (default: false = nur Badge) */
  showDetails?: boolean
  className?: string
}

const _icon: Record<EntscheidungsErgebnis, React.ReactNode> = {
  FREIGEGEBEN: <CheckCircle2 className="h-3.5 w-3.5" />,
  KEINE_REGEL: <CheckCircle2 className="h-3.5 w-3.5" />,
  ABGELEHNT:   <XCircle className="h-3.5 w-3.5" />,
  WARNUNG:     <AlertTriangle className="h-3.5 w-3.5" />,
  ESKALATION:  <ArrowUpCircle className="h-3.5 w-3.5" />,
}

const _badgeClass: Record<EntscheidungsErgebnis, string> = {
  FREIGEGEBEN: 'bg-green-100 text-green-800 border-green-200',
  KEINE_REGEL: 'bg-green-100 text-green-800 border-green-200',
  ABGELEHNT:   'bg-red-100 text-red-800 border-red-200',
  WARNUNG:     'bg-amber-100 text-amber-800 border-amber-200',
  ESKALATION:  'bg-orange-100 text-orange-800 border-orange-200',
}

const _label: Record<EntscheidungsErgebnis, string> = {
  FREIGEGEBEN: 'Freigegeben',
  KEINE_REGEL: 'Freigegeben',
  ABGELEHNT:   'Abgelehnt',
  WARNUNG:     'Warnung',
  ESKALATION:  'Eskalation',
}

export function PolicyExplanationBadge({
  explanation,
  showDetails = false,
  className,
}: PolicyExplanationBadgeProps): JSX.Element {
  const badgeClass = _badgeClass[explanation.entscheidung] ?? _badgeClass.KEINE_REGEL
  const icon = _icon[explanation.entscheidung] ?? <HelpCircle className="h-3.5 w-3.5" />
  const label = _label[explanation.entscheidung] ?? 'Unbekannt'

  return (
    <div className={cn('flex flex-col gap-2', className)}>
      {/* Badge */}
      <span
        title={explanation.zusammenfassung}
        className={cn(
          'inline-flex items-center gap-1.5 rounded-full border px-2.5 py-0.5 text-xs font-medium',
          badgeClass,
        )}
      >
        {icon}
        {label}
        {explanation.tenant_override_aktiv && (
          <span className="ml-1 rounded bg-white/50 px-1 text-[10px]">Override</span>
        )}
      </span>

      {/* Zusammenfassung als Tooltip-Text */}
      {showDetails && (
        <p className="text-xs text-muted-foreground">{explanation.zusammenfassung}</p>
      )}

      {/* Entscheidende Regeln */}
      {showDetails && explanation.gruende.length > 0 && (
        <ul className="flex flex-col gap-1 pl-1">
          {explanation.gruende
            .filter((g) => g.ist_entscheidend)
            .map((g) => (
              <li key={g.regel_id} className="flex items-start gap-1.5 text-xs text-muted-foreground">
                <span className="mt-0.5 h-1.5 w-1.5 shrink-0 rounded-full bg-current opacity-50" />
                {g.ergebnis_text}
              </li>
            ))}
        </ul>
      )}

      {/* Geprüfte Regeln Zähler */}
      {showDetails && explanation.anzahl_gepruefter_regeln > 0 && (
        <p className="text-right text-[10px] text-muted-foreground opacity-60">
          {explanation.anzahl_gepruefter_regeln} Regel(n) geprüft
        </p>
      )}
    </div>
  )
}
