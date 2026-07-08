import { memo } from 'react'
import { ChevronRight } from 'lucide-react'
import { useNavigate } from '@/app/routing/typed-router'
import type { ProcessRibbon } from './process-ribbon'

/**
 * ProcessRibbonRenderer (UIX-091): zeigt die Prozesskette unter dem ObjectHeader
 * als navigierbares Band (nav mit Links). Aktueller Schritt gold; Klick
 * navigiert in die Ziel-Maske. Tastatur-bedienbar (Links + Enter).
 */
export const ProcessRibbonRenderer = memo(function ProcessRibbonRenderer({
  ribbon,
}: {
  ribbon: ProcessRibbon | null
}): JSX.Element | null {
  const navigate = useNavigate()
  if (!ribbon || ribbon.steps.length === 0) return null

  return (
    <nav
      data-testid="process-ribbon"
      data-chain={ribbon.chainId}
      aria-label={`Prozesskette ${ribbon.label}`}
      className="flex flex-wrap items-center gap-1 border-b border-border px-4 py-2 md:px-8"
    >
      {ribbon.steps.map((step, index) => {
        const isCurrent = step.state === 'current'
        const clickable = step.routePath.length > 0
        return (
          <span key={step.key} className="flex items-center gap-1">
            {index > 0 && <ChevronRight className="h-3.5 w-3.5 shrink-0 text-muted-foreground" aria-hidden />}
            <button
              type="button"
              data-testid={`ribbon-step-${step.key}`}
              data-state={step.state}
              aria-current={isCurrent ? 'step' : undefined}
              disabled={!clickable}
              onClick={() => clickable && navigate(step.routePath)}
              className={`rounded-full px-2.5 py-0.5 text-xs font-medium transition-colors ${
                isCurrent
                  ? 'bg-amber-500 text-white'
                  : 'bg-muted text-muted-foreground hover:bg-accent hover:text-accent-foreground disabled:cursor-default disabled:opacity-60'
              }`}
            >
              {step.label}
            </button>
          </span>
        )
      })}
    </nav>
  )
})
