import { AlertCircle } from 'lucide-react'
import { UniversalMaskRenderer, useUniversalMaskRuntime } from '@/components/mask-builder'
import { versandAvisScreen } from '@/masks/capture-screens'
import { useScreenDefinition } from '@/lib/api/masks'

/**
 * Versand-Avis aus der ScreenDefinition `versand/versand-avis`.
 * Kopf, Empfänger und Liste zeichnet der Builder.
 */
export default function VersandAvisPage(): JSX.Element {
  const schemaQuery = useScreenDefinition('versand/versand-avis')
  const schema = schemaQuery.data ?? versandAvisScreen
  const runtime = useUniversalMaskRuntime({
    screenId: 'versand/versand-avis',
    schema,
    enabled: Boolean(schema),
  })

  if (!schema) {
    return <p className="px-4 py-6 text-sm text-muted-foreground">Versand-Avis wird geladen…</p>
  }
  if (!runtime.plan) {
    return (
      <p className="flex gap-2 px-4 py-6 text-sm text-destructive" role="alert">
        <AlertCircle className="h-4 w-4" aria-hidden="true" />
        Versand-Avis konnte nicht geladen werden.
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
