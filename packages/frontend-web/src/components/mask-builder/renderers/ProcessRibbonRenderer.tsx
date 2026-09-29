import { memo } from 'react'
import { ChevronRight } from 'lucide-react'
import { useNavigate } from '@/app/routing/typed-router'
import { cn } from '@/lib/utils'
import type { ProcessRibbon } from './process-ribbon'

/**
 * ProcessRibbonRenderer (UIX-091): zeigt die Prozesskette als navigierbares
 * Band. Der aktuelle Schritt ist markiert und kein Link — er ist die offene
 * Maske. Andere Schritte navigieren in ihre Ziel-Maske; Schritte ohne Route
 * bleiben sichtbar, aber nicht bedienbar.
 */
export const ProcessRibbonRenderer = memo(function ProcessRibbonRenderer({
  ribbon,
  embedded = false,
}: {
  ribbon: ProcessRibbon | null
  /** Inside a page section: no own divider or page padding. */
  embedded?: boolean
}): JSX.Element | null {
  const navigate = useNavigate()
  if (!ribbon || ribbon.steps.length === 0) return null

  return (
    <nav
      data-testid="process-ribbon"
      data-chain={ribbon.chainId}
      aria-label={`Prozesskette ${ribbon.label}`}
      className={cn('flex flex-wrap items-center gap-1', !embedded && 'border-b border-border px-4 py-2 md:px-8')}
    >
      {ribbon.steps.map((step, index) => {
        const isCurrent = step.state === 'current'
        const clickable = !isCurrent && step.routePath.length > 0
        const pill = 'inline-flex min-h-11 items-center rounded-full px-3 text-sm'
        return (
          <span key={step.key} className="flex items-center gap-1">
            {index > 0 && <ChevronRight className="h-3.5 w-3.5 shrink-0 text-muted-foreground" aria-hidden />}
            {isCurrent ? (
              <span
                data-testid={`ribbon-step-${step.key}`}
                data-state={step.state}
                aria-current="step"
                className={cn(pill, 'bg-primary font-medium text-primary-foreground')}
              >
                {step.label}
              </span>
            ) : (
              <button
                type="button"
                data-testid={`ribbon-step-${step.key}`}
                data-state={step.state}
                disabled={!clickable}
                onClick={() => clickable && navigate(step.routePath)}
                className={cn(
                  pill,
                  'bg-muted text-muted-foreground transition-colors hover:bg-accent hover:text-accent-foreground',
                  'focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-ring',
                  'disabled:cursor-default disabled:opacity-60 disabled:hover:bg-muted disabled:hover:text-muted-foreground',
                )}
              >
                {step.label}
              </button>
            )}
          </span>
        )
      })}
    </nav>
  )
})
