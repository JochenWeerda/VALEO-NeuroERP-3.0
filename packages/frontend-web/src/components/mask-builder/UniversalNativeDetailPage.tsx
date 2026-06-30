/**
 * Generic page wrapper for native ScreenDefinitions (temporary=False).
 * Replaces legacy handcrafted detail pages when a non-temporary SD is available.
 */

import { Alert, AlertDescription, AlertTitle } from '@/components/ui/alert'
import { UniversalMaskRenderer, useUniversalMaskRuntime } from '@/components/mask-builder'
import { useMaskPilotState } from '@/features/mask-pilot/use-mask-pilot-state'
import { getAxiosErrorMessage } from '@/lib/api-client'
import { useScreenDefinition } from '@/lib/api/masks'

interface UniversalNativeDetailPageProps {
  screenId: string
  entityId: string | undefined
  /** data-testid applied to the root div */
  testId?: string
}

export function UniversalNativeDetailPage({
  screenId,
  entityId,
  testId,
}: UniversalNativeDetailPageProps): JSX.Element {
  const { onTabChange } = useMaskPilotState()
  const schemaQuery = useScreenDefinition(screenId, { enabled: Boolean(entityId) })

  const runtime = useUniversalMaskRuntime({
    screenId,
    entityId,
    schema: schemaQuery.data,
    enabled: Boolean(entityId) && schemaQuery.data?.adapter?.temporary === false,
  })

  if (!entityId) {
    return (
      <div className="p-6">
        <Alert variant="destructive">
          <AlertTitle>Keine ID</AlertTitle>
          <AlertDescription>Bitte rufen Sie die Seite mit einer gueltigen ID auf.</AlertDescription>
        </Alert>
      </div>
    )
  }

  if (schemaQuery.error || runtime.entityError) {
    return (
      <div className="p-6">
        <Alert variant="destructive">
          <AlertTitle>Fehler beim Laden</AlertTitle>
          <AlertDescription>
            {getAxiosErrorMessage(schemaQuery.error ?? runtime.entityError)}
          </AlertDescription>
        </Alert>
      </div>
    )
  }

  if (!runtime.plan) {
    return (
      <div className="border-b bg-muted/30 px-4 py-2 text-sm text-muted-foreground md:px-8">
        Wird geladen…
      </div>
    )
  }

  return (
    <div data-testid={testId ?? `native-detail-${screenId.replace('/', '-')}`} data-runtime="native">
      {runtime.isEntityLoading && (
        <div className="border-b bg-muted/30 px-4 py-2 text-sm text-muted-foreground md:px-8">
          Daten werden geladen…
        </div>
      )}
      <UniversalMaskRenderer
        plan={runtime.plan}
        data={runtime.entityData}
        tables={runtime.tableRows}
        tableQueryStates={runtime.tableQueryStates}
        tableTotals={runtime.tableTotals}
        lookupBindings={runtime.lookupBindings}
        onTabChange={onTabChange}
        onTableQueryChange={runtime.setTableQuery}
        onAction={() => undefined}
      />
    </div>
  )
}
