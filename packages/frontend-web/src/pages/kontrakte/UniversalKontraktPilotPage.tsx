import { useMemo } from 'react'
import { useParams } from '@/app/routing/typed-router'
import { Alert, AlertDescription, AlertTitle } from '@/components/ui/alert'
import { UniversalMaskRenderer, type ScreenSummaryItem, type ScreenTabDefinition } from '@/components/mask-builder'
import { KONTRAKT_MASK_OBJECT_PAGE_CONFIG } from '@/features/agrar-masks/kontrakt-mask-support'
import { KONTRAKT_PILOT_TAB_TABLES } from '@/features/agrar-masks/kontrakt-tab-tables'
import { mapKontraktToMask } from '@/features/agrar-masks/mappers'
import { mapTabDataToTables, useKontraktTabData } from '@/features/agrar-masks/use-kontrakt-tab-data'
import { useMaskPilotState } from '@/features/mask-pilot/use-mask-pilot-state'
import { usePilotRenderPlan } from '@/features/mask-pilot/use-pilot-render-plan'
import { getAxiosErrorMessage } from '@/lib/api-client'
import { useKontrakt, useKontraktScreenSummary } from '@/lib/api/kontrakte'
import { useScreenDefinition } from '@/lib/api/masks'

function formatQuantity(value: number, unit?: string): string {
  const formatted = new Intl.NumberFormat('de-DE', { maximumFractionDigits: 3 }).format(value)
  return unit ? `${formatted} ${unit}` : formatted
}

function buildSummaryItems(summary: ReturnType<typeof useKontraktScreenSummary>['data']): ScreenSummaryItem[] {
  if (!summary) return []
  return [
    {
      key: 'rest_quantity',
      label: 'Restmenge',
      value: formatQuantity(summary.summary.rest_quantity, summary.summary.unit),
    },
    {
      key: 'total_quantity',
      label: 'Gesamtmenge',
      value: formatQuantity(summary.summary.total_quantity, summary.summary.unit),
    },
    { key: 'line_count', label: 'Positionen', value: summary.summary.line_count },
    { key: 'status', label: 'Status', value: summary.summary.status },
    { key: 'contract_type', label: 'Kontraktart', value: summary.summary.contract_type },
    { key: 'valid_to', label: 'Gueltig bis', value: summary.summary.valid_to ?? '-' },
  ]
}

function enrichTabsWithTables(tabs: ScreenTabDefinition[]): ScreenTabDefinition[] {
  return tabs.map((tab) => ({
    ...tab,
    tables: KONTRAKT_PILOT_TAB_TABLES[tab.key] ?? tab.tables,
  }))
}

export default function UniversalKontraktPilotPage(): JSX.Element {
  const { id } = useParams<{ id?: string }>()
  const { activeTabKey, tablePage, onTabChange } = useMaskPilotState()

  const summaryQuery = useKontraktScreenSummary(id ?? '')
  const nativeScreenQuery = useScreenDefinition('agrar/kontrakte', { enabled: Boolean(id) })
  const kontraktQuery = useKontrakt(id ?? '', { enabled: Boolean(summaryQuery.data) })
  const tabDataQuery = useKontraktTabData(
    id ?? '',
    activeTabKey,
    summaryQuery.data?.tab_endpoints,
    tablePage,
  )

  const summaryItems = useMemo(
    () => buildSummaryItems(summaryQuery.data),
    [summaryQuery.data],
  )

  const { plan } = usePilotRenderPlan({
    screenId: 'agrar/kontrakte',
    domain: 'agrar',
    maskConfig: {
      ...KONTRAKT_MASK_OBJECT_PAGE_CONFIG,
      title: summaryQuery.data?.title ?? 'Kontrakt Generator Pilot',
      subtitle: summaryQuery.data?.subtitle ?? kontraktQuery.data?.contract_no,
    },
    entityId: id,
    summaryEndpointPrefix: '/api/v1/kontrakte',
    summary: summaryQuery.data,
    nativeScreen: nativeScreenQuery.data,
    enrichTabs: enrichTabsWithTables,
    summaryItems,
    enabled: Boolean(id),
  })

  const data = useMemo(() => {
    const base = mapKontraktToMask(kontraktQuery.data)
    const partyName = summaryQuery.data?.party_name
    if (partyName && base.contract && typeof base.contract === 'object') {
      return {
        ...base,
        contract: { ...(base.contract as Record<string, unknown>), party_name: partyName },
      }
    }
    return base
  }, [kontraktQuery.data, summaryQuery.data?.party_name])
  const tables = useMemo(() => mapTabDataToTables(tabDataQuery.data), [tabDataQuery.data])

  if (!id) {
    return (
      <div className="p-6">
        <Alert variant="destructive">
          <AlertTitle>Keine Kontrakt-ID</AlertTitle>
          <AlertDescription>Der Generator-Pilot ist nur fuer bestehende Kontrakte verfuegbar.</AlertDescription>
        </Alert>
      </div>
    )
  }

  if (summaryQuery.error || kontraktQuery.error) {
    return (
      <div className="p-6">
        <Alert variant="destructive">
          <AlertTitle>Generator-Pilot nicht verfuegbar</AlertTitle>
          <AlertDescription>{getAxiosErrorMessage(summaryQuery.error ?? kontraktQuery.error)}</AlertDescription>
        </Alert>
      </div>
    )
  }

  return (
    <div data-testid="universal-kontrakt-pilot">
      {summaryQuery.isLoading ? (
        <div className="border-b bg-muted/30 px-4 py-2 text-sm text-muted-foreground md:px-8">
          Summary wird geladen...
        </div>
      ) : null}
      {kontraktQuery.isLoading ? (
        <div className="border-b bg-muted/20 px-4 py-2 text-sm text-muted-foreground md:px-8">
          Kontraktdaten werden nachgeladen...
        </div>
      ) : null}
      {tabDataQuery.isFetching && activeTabKey ? (
        <div className="border-b bg-muted/20 px-4 py-2 text-sm text-muted-foreground md:px-8" data-testid="tab-data-loading">
          Tab-Daten werden geladen...
        </div>
      ) : null}
      {plan ? (
        <UniversalMaskRenderer
          plan={plan}
          data={data}
          tables={tables}
          onTabChange={onTabChange}
          onAction={() => undefined}
        />
      ) : null}
    </div>
  )
}
