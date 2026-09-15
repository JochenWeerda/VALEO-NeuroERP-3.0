import { AlertTriangle, ChevronRight } from 'lucide-react'
import { cn } from '@/lib/utils'
import { Button } from '@/components/ui/button'
import type { ScreenWorkflowDefinition } from '../schema'
import type { WorkflowState } from '../runtime/WorkflowRuntime'

/**
 * FSX-030 — Prozessband (Ebene 1 des Flow-Spine-Entlastungsplans).
 *
 * Eine Zeile in der Belegmaske: Phasen, aktueller Stand, **eine** naechste
 * Aktion, Blocker. Mehr nicht — der vollstaendige Leitstand bleibt eine
 * Verknuepfung entfernt.
 *
 * Die Arbeitsteilung ist streng:
 * - **Phasen** kommen aus der ScreenDefinition. Sie sind Prozessdefinition und
 *   damit statisch zulaessig (FSX-003 Fall 1).
 * - **Stand, Aktionen und Blocker** kommen ausschliesslich aus dem
 *   `WorkflowState`. Nichts davon darf aus der Definition stammen, sonst zeigt
 *   die Maske in jedem Beleg denselben Stand — genau der Fehler, den FSX-002/003
 *   im Leitstand beseitigt haben.
 *
 * Ohne Phasen rendert das Band nichts. Ein Platzhalter mit internem
 * Prozessschluessel waere schlechter als gar nichts: er kostet Platz und sagt
 * dem Sachbearbeiter nichts.
 */
export function ProcessBand({
  workflow,
  workflowState,
  onAction,
  onOpenProcess,
  className,
}: {
  workflow?: ScreenWorkflowDefinition
  workflowState?: WorkflowState
  /** Ausfuehrung der naechsten Aktion. Fehlt sie, wird die Aktion nur benannt. */
  onAction?: (actionKey: string) => void
  /** Sprung in den Leitstand. Fehlt er, entfaellt der Verweis. */
  onOpenProcess?: () => void
  className?: string
}): JSX.Element | null {
  const phases = workflow?.phases ?? []
  if (phases.length === 0) return null

  const currentStatus = workflowState?.status.currentStatus
  const activeIndex = phases.findIndex((phase) => phase.key === currentStatus)
  const blockers = (workflowState?.blockingReasons ?? []).filter((reason) => reason.blocking)
  // Genau eine naechste Aktion. Eine Liste waere wieder ein Entscheidungsproblem.
  const nextAction = workflowState?.nextAllowedActions?.[0]

  return (
    <section
      aria-label="Prozessstand"
      data-testid="process-band"
      data-current-status={currentStatus ?? 'unbekannt'}
      className={cn(
        'flex flex-wrap items-center gap-x-4 gap-y-2 rounded-lg border bg-muted/20 px-3 py-2 text-sm',
        className,
      )}
    >
      <ol className="flex flex-wrap items-center gap-x-1.5 gap-y-1">
        {phases.map((phase, index) => {
          const done = activeIndex >= 0 && index < activeIndex
          const active = index === activeIndex
          return (
            <li key={phase.key} className="flex items-center gap-1.5">
              {index > 0 ? (
                <ChevronRight className="h-3.5 w-3.5 text-muted-foreground" aria-hidden="true" />
              ) : null}
              <span
                data-phase={phase.key}
                data-phase-state={active ? 'active' : done ? 'done' : 'open'}
                aria-current={active ? 'step' : undefined}
                className={cn(
                  'text-2xs uppercase tracking-wide',
                  active
                    ? 'font-semibold text-foreground'
                    : done
                      ? 'text-muted-foreground'
                      : 'text-muted-foreground/60',
                )}
              >
                {phase.label}
              </span>
            </li>
          )
        })}
      </ol>

      {blockers.length > 0 ? (
        <span className="flex items-center gap-1.5 text-status-warning" data-testid="process-band-blocker">
          <AlertTriangle className="h-3.5 w-3.5" aria-hidden="true" />
          {/* Nur der erste Blocker. Wer drei gleichzeitig liest, loest keinen. */}
          <span className="text-xs">{blockers[0]?.message}</span>
        </span>
      ) : null}

      <div className="ml-auto flex items-center gap-2">
        {nextAction ? (
          onAction ? (
            <Button
              size="sm"
              variant="outline"
              data-testid="process-band-next-action"
              data-next-action={nextAction.actionKey}
              onClick={() => onAction(nextAction.actionKey)}
            >
              {nextAction.label}
            </Button>
          ) : (
            <span
              className="text-xs text-muted-foreground"
              data-testid="process-band-next-action"
              data-next-action={nextAction.actionKey}
            >
              Naechster Schritt: {nextAction.label}
            </span>
          )
        ) : null}
        {onOpenProcess ? (
          <Button size="sm" variant="ghost" onClick={onOpenProcess} data-testid="process-band-open">
            Prozess
          </Button>
        ) : null}
      </div>
    </section>
  )
}
