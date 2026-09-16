import { UniversalMaskRenderer, useUniversalMaskRuntime } from '@/components/mask-builder'
import { compileRenderPlanFromScreenDefinition } from '@/components/mask-builder/render-plan/schema-compiler'
import { useParams } from '@/app/routing/typed-router'
import { useScreenDefinition } from '@/lib/api/masks'

export default function StudioRunPage(): JSX.Element {
  const { screenId: rawScreenId } = useParams<{ screenId?: string }>()
  const screenId = (rawScreenId ?? '').replace(/__/g, '/')
  const schemaQuery = useScreenDefinition(screenId, { enabled: Boolean(screenId) })
  const runtime = useUniversalMaskRuntime({
    screenId,
    schema: schemaQuery.data,
    enabled: Boolean(screenId) && Boolean(schemaQuery.data),
  })
  const plan = runtime.plan ?? (schemaQuery.data ? compileRenderPlanFromScreenDefinition(schemaQuery.data) : null)

  if (!screenId) {
    return <p className="p-4 text-sm text-muted-foreground">Keine Studio-Maske angegeben.</p>
  }
  if (schemaQuery.isLoading) {
    return <p className="p-4 text-sm text-muted-foreground">Studio-Maske wird geladen…</p>
  }
  if (schemaQuery.isError || !schemaQuery.data || !plan) {
    return (
      <p className="p-4 text-sm text-destructive" role="alert">
        Freigegebene Studio-Maske nicht gefunden.
      </p>
    )
  }

  return (
    <div className="p-4" data-testid="studio-run" data-screen-id={screenId}>
      <UniversalMaskRenderer
        plan={plan}
        screen={schemaQuery.data}
        data={runtime.entityData}
        tables={runtime.tableRows}
        messages={runtime.messages}
        onRetry={() => { void runtime.refetch() }}
        tableQueryStates={runtime.tableQueryStates}
        tableTotals={runtime.tableTotals}
        onTableQueryChange={runtime.setTableQuery}
        onOverlayChange={runtime.updateUserOverlay}
        onOverlayReset={runtime.resetUserOverlay}
        lookupBindings={runtime.lookupBindings}
      />
    </div>
  )
}
