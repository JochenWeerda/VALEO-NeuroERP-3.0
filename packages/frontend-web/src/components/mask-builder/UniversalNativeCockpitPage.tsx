import { useMemo } from 'react'
import { AlertCircle } from 'lucide-react'
import { UniversalMaskRenderer } from '@/components/mask-builder'
import { useScreenDefinition } from '@/lib/api/masks'
import { compileRenderPlanFromScreenDefinition } from './render-plan/schema-compiler'

/**
 * UniversalNativeCockpitPage (UIX-061): rendert einen cockpit-Workspace als
 * rollenbasierte Startseite. Kein Entity — die Seite kompiliert die
 * ScreenDefinition direkt zu einem RenderPlan (KPI-Summary + Kachel-Grid) und
 * navigiert ueber die Kacheln in die jeweiligen Prozessmasken.
 */
export function UniversalNativeCockpitPage({
  screenId,
  testId,
}: {
  screenId: string
  testId?: string
}): JSX.Element {
  const schemaQuery = useScreenDefinition(screenId)

  const plan = useMemo(
    () => (schemaQuery.data ? compileRenderPlanFromScreenDefinition(schemaQuery.data) : null),
    [schemaQuery.data],
  )

  if (schemaQuery.isLoading) {
    return (
      <div className="px-4 py-3 text-sm text-muted-foreground md:px-8" data-testid={`${testId ?? 'cockpit'}-loading`}>
        Workspace wird geladen…
      </div>
    )
  }

  if (schemaQuery.error || !plan) {
    return (
      <div
        className="flex items-start gap-2 px-4 py-3 text-sm text-destructive md:px-8"
        role="alert"
        data-testid={`${testId ?? 'cockpit'}-error`}
      >
        <AlertCircle className="mt-0.5 h-4 w-4 shrink-0" />
        <span>Workspace konnte nicht geladen werden.</span>
      </div>
    )
  }

  return (
    <div data-testid={testId ?? `native-cockpit-${screenId.replace('/', '-')}`} data-runtime="native-cockpit">
      <UniversalMaskRenderer plan={plan} />
    </div>
  )
}
