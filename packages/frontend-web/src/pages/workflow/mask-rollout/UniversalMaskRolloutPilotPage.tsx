import { useMemo } from 'react'
import { Alert, AlertDescription, AlertTitle } from '@/components/ui/alert'
import {
  UniversalMaskRenderer,
  type ScreenSummaryItem,
  type ScreenTabDefinition,
} from '@/components/mask-builder'
import { useMaskPilotState } from '@/features/mask-pilot/use-mask-pilot-state'
import { usePilotRenderPlan } from '@/features/mask-pilot/use-pilot-render-plan'
import {
  buildGenericTabTables,
  buildRolloutMaskConfig,
  getRolloutSpec,
} from '@/features/mask-rollouts/rollout-registry'
import {
  mapRolloutTabDataToTables,
  useRolloutScreenSummary,
  useRolloutTabData,
} from '@/features/mask-rollouts/use-rollout-tab-data'
import { getAxiosErrorMessage } from '@/lib/api-client'
import { useScreenDefinition } from '@/lib/api/masks'

function buildSummaryItems(summary: Record<string, unknown> | undefined): ScreenSummaryItem[] {
  if (!summary) return []
  return Object.entries(summary).slice(0, 8).map(([key, value]) => ({
    key,
    label: key.replace(/_/g, ' '),
    value: value == null ? '-' : String(value),
  }))
}

type UniversalMaskRolloutPilotPageProps = {
  screenId: string
  entityId: string
}

export default function UniversalMaskRolloutPilotPage({
  screenId,
  entityId,
}: UniversalMaskRolloutPilotPageProps): JSX.Element {
  const spec = getRolloutSpec(screenId)
  const { activeTabKey, tablePage, onTabChange } = useMaskPilotState()

  const summaryQuery = useRolloutScreenSummary(screenId, entityId)
  const nativeScreenQuery = useScreenDefinition(screenId, { enabled: Boolean(entityId) })
  const tabDataQuery = useRolloutTabData(
    screenId,
    entityId,
    activeTabKey,
    summaryQuery.data?.tab_endpoints,
    tablePage,
  )

  const summaryItems = useMemo(
    () => buildSummaryItems(summaryQuery.data?.summary),
    [summaryQuery.data?.summary],
  )

  const tabTables = useMemo(() => {
    if (!activeTabKey || activeTabKey === 'kopf') return {}
    const sample = tabDataQuery.data?.items?.[0]
    return {
      [activeTabKey]: buildGenericTabTables(activeTabKey, sample),
    }
  }, [activeTabKey, tabDataQuery.data?.items])

  const enrichTabs = useMemo(
    () =>
      (tabs: ScreenTabDefinition[]): ScreenTabDefinition[] =>
        tabs.map((tab) => ({
          ...tab,
          tables: tabTables[tab.key] ?? tab.tables,
        })),
    [tabTables],
  )

  const { plan } = usePilotRenderPlan({
    screenId,
    domain: (spec?.domain ?? 'admin') as 'finance' | 'lager' | 'einkauf' | 'crm' | 'sales' | 'agrar' | 'admin',
    maskConfig: {
      ...buildRolloutMaskConfig(screenId, summaryQuery.data?.title ?? spec?.title ?? 'Rollout Pilot'),
      title: summaryQuery.data?.title ?? spec?.title ?? 'Rollout Pilot',
      subtitle: summaryQuery.data?.subtitle,
    },
    entityId,
    summaryEndpointPrefix: `/api/v1/mask-rollouts/${screenId}`,
    summary: summaryQuery.data,
    nativeScreen: nativeScreenQuery.data,
    enrichTabs,
    summaryItems,
    enabled: Boolean(entityId),
  })

  const tabData = useMemo(() => mapRolloutTabDataToTables(tabDataQuery.data), [tabDataQuery.data])

  const data = useMemo(
    () => ({
      summary: summaryQuery.data?.summary ?? {},
      title: summaryQuery.data?.title,
      subtitle: summaryQuery.data?.subtitle,
    }),
    [summaryQuery.data],
  )

  if (summaryQuery.isError) {
    return (
      <Alert variant="destructive">
        <AlertTitle>Rollout Pilot</AlertTitle>
        <AlertDescription>{getAxiosErrorMessage(summaryQuery.error)}</AlertDescription>
      </Alert>
    )
  }

  if (!plan) {
    return (
      <Alert>
        <AlertTitle>Rollout Pilot</AlertTitle>
        <AlertDescription>Lade RenderPlan…</AlertDescription>
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
      {tabDataQuery.isFetching && activeTabKey ? (
        <div className="border-b bg-muted/20 px-4 py-2 text-sm text-muted-foreground md:px-8">
          Tab-Daten werden geladen...
        </div>
      ) : null}
      <UniversalMaskRenderer
        plan={plan}
        data={data}
        tables={tabData}
        onTabChange={onTabChange}
        onAction={() => undefined}
      />
    </div>
  )
}
