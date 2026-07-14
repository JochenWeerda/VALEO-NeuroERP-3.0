import { AlertCircle } from 'lucide-react'
import { UniversalMaskRenderer, useUniversalMaskRuntime } from '@/components/mask-builder'
import { useScreenDefinition } from '@/lib/api/masks'

const EMPTY_PERMISSIONS: string[] = []

/**
 * UniversalNativeCockpitPage (UIX-061): rendert einen cockpit-Workspace als
 * rollenbasierte Startseite. Kein Entity — die Seite kompiliert die
 * ScreenDefinition ueber den zentralen UniversalMaskRuntime zu einem RenderPlan
 * (KPI-Summary + Kachel-Grid) und navigiert ueber die Kacheln in die jeweiligen
 * Prozessmasken. Damit gelten Overlays, Berechtigungen und Compiler-Gates auch
 * fuer Cockpits und nicht nur fuer Objektmasken.
 */
export function UniversalNativeCockpitPage({
  screenId,
  testId,
  onAction,
  permissions = EMPTY_PERMISSIONS,
}: {
  screenId: string
  testId?: string
  onAction?: (_actionKey: string, _payload: Record<string, unknown>) => void | Promise<void>
  permissions?: string[]
}): JSX.Element {
  const schemaQuery = useScreenDefinition(screenId)
  const runtime = useUniversalMaskRuntime({
    screenId,
    schema: schemaQuery.data,
    enabled: Boolean(schemaQuery.data),
    permissions,
  })
  const plan = runtime.plan

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
      <UniversalMaskRenderer
        plan={plan}
        data={runtime.entityData}
        tables={runtime.tableRows}
        tableQueryStates={runtime.tableQueryStates}
        tableTotals={runtime.tableTotals}
        onTableQueryChange={runtime.setTableQuery}
        onOverlayChange={runtime.updateUserOverlay}
        onOverlayReset={runtime.resetUserOverlay}
        lookupBindings={runtime.lookupBindings}
        onAction={onAction}
      />
    </div>
  )
}
