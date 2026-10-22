import { AlertCircle } from 'lucide-react'
import { UniversalMaskRenderer, useUniversalMaskRuntime } from '@/components/mask-builder'
import { streckeStreckengeschaeftScreen } from '@/masks/capture-screens'
import { useScreenDefinition } from '@/lib/api/masks'

/**
 * Streckengeschaeft aus der ScreenDefinition `strecke/streckengeschaeft`.
 * Kopf und Liste zeichnet der Builder.
 */
export default function StreckengeschaeftPage(): JSX.Element {
  const schemaQuery = useScreenDefinition('strecke/streckengeschaeft')
  const schema = schemaQuery.data ?? streckeStreckengeschaeftScreen
  const runtime = useUniversalMaskRuntime({
    screenId: 'strecke/streckengeschaeft',
    schema,
    enabled: Boolean(schema),
  })

  if (!schema) {
    return <p className="px-4 py-6 text-sm text-muted-foreground">Streckengeschäft wird geladen…</p>
  }
  if (!runtime.plan) {
    return (
      <p className="flex gap-2 px-4 py-6 text-sm text-destructive" role="alert">
        <AlertCircle className="h-4 w-4" aria-hidden="true" />
        Streckengeschäft konnte nicht geladen werden.
      </p>
    )
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
    />
  )
}
