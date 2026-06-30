/**
 * Generic page wrapper for native ScreenDefinitions (temporary=False).
 * Replaces legacy handcrafted detail pages when a non-temporary SD is available.
 */

import { useNavigate } from '@tanstack/react-router'
import { ArrowLeft, AlertCircle } from 'lucide-react'
import { useState } from 'react'
import { Button } from '@/components/ui/button'
import { UniversalMaskRenderer, useHumanActionDispatch, useUniversalMaskRuntime } from '@/components/mask-builder'
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
  const navigate = useNavigate()
  const schemaQuery = useScreenDefinition(screenId, { enabled: Boolean(entityId) })
  const [actionError, setActionError] = useState<string | null>(null)
  const [actionSummary, setActionSummary] = useState<string | null>(null)

  const runtime = useUniversalMaskRuntime({
    screenId,
    entityId,
    schema: schemaQuery.data,
    enabled: Boolean(entityId) && schemaQuery.data?.adapter?.temporary === false,
  })
  const actionRuntime = useHumanActionDispatch(schemaQuery.data?.actions ?? [], {
    screenId,
    entityId,
    permissions: schemaQuery.data?.permissions ?? [],
  })

  async function handleAction(actionKey: string, payload: Record<string, unknown>): Promise<void> {
    setActionError(null)
    setActionSummary(null)
    const result = await actionRuntime.executeAction({
      actionKey,
      entityId,
      payload,
      mode: 'execute',
    })
    if (!result.success) {
      const validationMessage = result.validationErrors?.map((error) => error.message).join('; ')
      setActionError(result.error ?? validationMessage ?? `Aktion "${actionKey}" konnte nicht ausgefuehrt werden.`)
      return
    }
    setActionSummary(result.summary ?? `Aktion "${actionKey}" wurde ausgefuehrt.`)
    await runtime.refetch()
  }

  if (!entityId) {
    return (
      <div className="flex flex-col items-center justify-center gap-4 p-12 text-center">
        <AlertCircle className="h-10 w-10 text-muted-foreground" />
        <div>
          <p className="text-lg font-medium">Kein Datensatz ausgewählt</p>
          <p className="mt-1 text-sm text-muted-foreground">
            Bitte wählen Sie einen Eintrag aus der Liste aus, um die Details anzuzeigen.
          </p>
        </div>
        <Button variant="outline" onClick={() => void navigate({ to: -1 as never })}>
          <ArrowLeft className="mr-2 h-4 w-4" />
          Zurück zur Liste
        </Button>
      </div>
    )
  }

  if (schemaQuery.error || runtime.entityError) {
    const errMsg = getAxiosErrorMessage(schemaQuery.error ?? runtime.entityError)
    const isNotFound = errMsg?.includes('404') || errMsg?.toLowerCase().includes('not found')
    return (
      <div className="flex flex-col items-center justify-center gap-4 p-12 text-center">
        <AlertCircle className="h-10 w-10 text-destructive" />
        <div>
          <p className="text-lg font-medium">
            {isNotFound ? 'Datensatz nicht gefunden' : 'Fehler beim Laden'}
          </p>
          <p className="mt-1 text-sm text-muted-foreground">
            {isNotFound
              ? 'Der angeforderte Datensatz existiert nicht oder wurde gelöscht.'
              : errMsg}
          </p>
        </div>
        <Button variant="outline" onClick={() => void navigate({ to: -1 as never })}>
          <ArrowLeft className="mr-2 h-4 w-4" />
          Zurück
        </Button>
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
      {actionRuntime.loadingActionKey && (
        <div className="border-b bg-muted/30 px-4 py-2 text-sm text-muted-foreground md:px-8">
          Aktion wird ausgefuehrt...
        </div>
      )}
      {actionError && (
        <div className="border-b border-destructive/30 bg-destructive/10 px-4 py-2 text-sm text-destructive md:px-8" role="alert">
          {actionError}
        </div>
      )}
      {actionSummary && (
        <div className="border-b border-emerald-200 bg-emerald-50 px-4 py-2 text-sm text-emerald-800 md:px-8" role="status">
          {actionSummary}
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
        onAction={handleAction}
      />
    </div>
  )
}
