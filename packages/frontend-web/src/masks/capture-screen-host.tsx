import { AlertCircle } from 'lucide-react'
import { UniversalMaskRenderer, useUniversalMaskRuntime } from '@/components/mask-builder'
import type { ScreenContext } from '@/components/mask-builder/governance/screen-context'
import type { ScreenDefinition } from '@/components/mask-builder/schema'
import { useScreenDefinition } from '@/lib/api/masks'

/**
 * Duenne Seite fuer eine ScreenDefinition. Die Registry gewinnt, sobald der
 * Dienst sie ausliefert; bis dahin zeichnet der Builder die mitgegebene Kopie.
 */
export function CaptureScreenHost({
  screenId,
  fallback,
  loading,
  error,
  permissions,
  onAction,
  screenContext,
}: {
  screenId: string
  fallback: ScreenDefinition
  loading: string
  error: string
  permissions?: string[]
  onAction?: (_actionKey: string, _payload: Record<string, unknown>) => void | Promise<void>
  screenContext?: ScreenContext
}): JSX.Element {
  const schemaQuery = useScreenDefinition(screenId)
  const schema = schemaQuery.data ?? fallback
  const runtime = useUniversalMaskRuntime({
    screenId,
    schema,
    permissions,
    enabled: Boolean(schema),
  })

  if (!runtime.plan) {
    if (schemaQuery.isError) {
      return (
        <p className="flex gap-2 px-4 py-6 text-sm text-destructive" role="alert">
          <AlertCircle className="h-4 w-4" aria-hidden="true" />
          {error}
        </p>
      )
    }
    return <p className="px-4 py-6 text-sm text-muted-foreground">{loading}</p>
  }

  return (
    <UniversalMaskRenderer
      plan={runtime.plan}
      data={runtime.entityData}
      tables={runtime.tableRows}
      messages={runtime.messages}
      onRetry={() => {
        void runtime.refetch()
      }}
      tableQueryStates={runtime.tableQueryStates}
      tableTotals={runtime.tableTotals}
      onTableQueryChange={runtime.setTableQuery}
      onOverlayChange={runtime.updateUserOverlay}
      onOverlayReset={runtime.resetUserOverlay}
      lookupBindings={runtime.lookupBindings}
      screenContext={screenContext}
      onAction={onAction
        ? async (key, payload) => {
            await onAction(key, payload)
            await runtime.refetch()
          }
        : undefined}
    />
  )
}
