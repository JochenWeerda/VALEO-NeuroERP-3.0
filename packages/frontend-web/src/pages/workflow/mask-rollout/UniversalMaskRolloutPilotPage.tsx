import { useMemo } from 'react'
import { Alert, AlertDescription, AlertTitle } from '@/components/ui/alert'
import { UniversalMaskRenderer, type ScreenSummaryItem } from '@/components/mask-builder'
import { useUniversalMaskRuntime } from '@/components/mask-builder/runtime/useUniversalMaskRuntime'
import { getAxiosErrorMessage } from '@/lib/api-client'
import { useScreenDefinition } from '@/lib/api/masks'
import { getRolloutSpec } from '@/features/mask-rollouts/rollout-registry'
import { useRolloutScreenSummary } from '@/features/mask-rollouts/use-rollout-tab-data'

function buildSummaryItems(summary: Record<string, unknown> | undefined): ScreenSummaryItem[] {
  if (!summary) return []
  return Object.entries(summary)
    .slice(0, 6)
    .map(([key, value]) => ({
      key,
      label: key.replace(/_/g, ' '),
      value: value == null ? '-' : String(value),
    }))
}

type Props = {
  screenId: string
  entityId: string
}

export default function UniversalMaskRolloutPilotPage({ screenId, entityId }: Props): JSX.Element {
  const spec = getRolloutSpec(screenId)

  const summaryQuery = useRolloutScreenSummary(screenId, entityId)
  const nativeScreenQuery = useScreenDefinition(screenId, { enabled: Boolean(entityId) })

  const summaryItems = useMemo(
    () => buildSummaryItems(summaryQuery.data?.summary),
    [summaryQuery.data?.summary],
  )

  const {
    plan,
    entityData,
    tableRows,
    tableTotals,
    tableQueryStates,
    setTableQuery,
    userOverlay,
    updateUserOverlay,
    resetUserOverlay,
    lookupBindings,
    isEntityLoading,
    entityError,
  } = useUniversalMaskRuntime({
    screenId,
    entityId,
    schema: nativeScreenQuery.data,
    tabEndpoints: summaryQuery.data?.tab_endpoints,
    availableTabs: summaryQuery.data?.available_tabs,
    summaryTitle: summaryQuery.data?.title,
    summarySubtitle: summaryQuery.data?.subtitle,
    summaryItems,
    enabled: Boolean(entityId && nativeScreenQuery.data),
  })

  // Merge summary fields into entity data so form fields bound to summary.* can resolve
  const mergedData = useMemo(
    () => ({ ...entityData, summary: summaryQuery.data?.summary ?? {} }),
    [entityData, summaryQuery.data?.summary],
  )

  if (summaryQuery.isError || entityError) {
    return (
      <Alert variant="destructive">
        <AlertTitle>{spec?.title ?? screenId}</AlertTitle>
        <AlertDescription>{getAxiosErrorMessage(summaryQuery.error ?? entityError)}</AlertDescription>
      </Alert>
    )
  }

  return (
    <div data-testid={`universal-rollout-pilot-${screenId.replace(/\//g, '-')}`}>
      {summaryQuery.isLoading ? (
        <div className="border-b bg-muted/30 px-4 py-2 text-sm text-muted-foreground md:px-8">
          Summary wird geladen...
        </div>
      ) : null}
      {isEntityLoading ? (
        <div className="border-b bg-muted/20 px-4 py-2 text-sm text-muted-foreground md:px-8">
          Daten werden nachgeladen...
        </div>
      ) : null}
      {plan ? (
        <UniversalMaskRenderer
          plan={plan}
          data={mergedData}
          tables={tableRows}
          tableTotals={tableTotals}
          tableQueryStates={tableQueryStates}
          onTableQueryChange={setTableQuery}
          overlay={userOverlay}
          onOverlayChange={updateUserOverlay}
          onOverlayReset={resetUserOverlay}
          lookupBindings={lookupBindings}
          onAction={() => undefined}
        />
      ) : null}
    </div>
  )
}
