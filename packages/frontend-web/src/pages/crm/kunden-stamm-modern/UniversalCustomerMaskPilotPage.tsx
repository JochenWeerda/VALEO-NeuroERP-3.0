import { useMemo } from 'react'
import { useParams } from '@/app/routing/typed-router'
import { Alert, AlertDescription, AlertTitle } from '@/components/ui/alert'
import {
  UniversalMaskRenderer,
  useUniversalMaskRuntime,
  type ScreenSummaryItem,
  type ScreenTabDefinition,
} from '@/components/mask-builder'
import {
  CUSTOMER_MASK_OBJECT_PAGE_CONFIG,
} from '@/features/crm-masks/customer-mask-support'
import { CUSTOMER_PILOT_TAB_TABLES } from '@/features/crm-masks/customer-tab-tables'
import { mapCustomerToMask } from '@/features/crm-masks/mappers'
import { mapTabDataToTables, useCustomerTabData } from '@/features/crm-masks/use-customer-tab-data'
import { useMaskPilotState } from '@/features/mask-pilot/use-mask-pilot-state'
import { usePilotRenderPlan, type PilotScreenSummaryLike } from '@/features/mask-pilot/use-pilot-render-plan'
import { getAxiosErrorMessage } from '@/lib/api-client'
import { useCustomer, useCustomerScreenSummary } from '@/lib/api/crm'
import { useScreenDefinition } from '@/lib/api/masks'

const CRM360_SUPPLEMENTAL_TABS: ScreenTabDefinition[] = [
  { key: 'contacts', label: 'Ansprechpartner', lazy: true, keepAlive: true, tables: CUSTOMER_PILOT_TAB_TABLES.contacts },
  { key: 'auftraege', label: 'Auftraege', lazy: true, keepAlive: true, tables: CUSTOMER_PILOT_TAB_TABLES.auftraege },
  { key: 'aktivitaeten', label: 'Aktivitaeten', lazy: true, keepAlive: true, tables: CUSTOMER_PILOT_TAB_TABLES.aktivitaeten },
  { key: 'dokumente', label: 'Dokumente', lazy: true, keepAlive: true, tables: CUSTOMER_PILOT_TAB_TABLES.dokumente },
]

function formatEuro(value: number): string {
  return new Intl.NumberFormat('de-DE', { style: 'currency', currency: 'EUR' }).format(value)
}

function buildSummaryItems(summary: ReturnType<typeof useCustomerScreenSummary>['data']): ScreenSummaryItem[] {
  if (!summary) return []
  return [
    { key: 'sales_ytd', label: 'Umsatz 12M', value: formatEuro(summary.summary.sales_ytd) },
    { key: 'open_items_total', label: 'Offene Posten', value: formatEuro(summary.summary.open_items_total), tone: summary.summary.open_items_total > 0 ? 'warning' : 'success' },
    { key: 'recent_activity_count', label: 'Aktivitaeten 90T', value: summary.summary.recent_activity_count },
    { key: 'credit_status', label: 'Kreditstatus', value: summary.summary.credit_status, tone: summary.summary.credit_status === 'ok' ? 'success' : 'warning' },
  ]
}

function enrichTabsWithTables(tabs: ScreenTabDefinition[]): ScreenTabDefinition[] {
  return tabs.map((tab) => ({
    ...tab,
    tables: CUSTOMER_PILOT_TAB_TABLES[tab.key] ?? tab.tables,
  }))
}

function getCustomerIdFromSearch(): string | undefined {
  if (typeof window === 'undefined') return undefined
  return new URLSearchParams(window.location.search).get('id') ?? undefined
}

function UniversalCustomerMaskPilotPage(): JSX.Element {
  const { id: routeId } = useParams<{ id?: string }>()
  const id = routeId ?? getCustomerIdFromSearch()
  const { activeTabKey, tablePage, onTabChange } = useMaskPilotState()
  const summaryQuery = useCustomerScreenSummary(id ?? '')
  const nativeScreenQuery = useScreenDefinition('crm/customer-360', { enabled: Boolean(id) })

  const summaryItems = useMemo(
    () => buildSummaryItems(summaryQuery.data),
    [summaryQuery.data],
  )
  const summaryForRenderPlan = useMemo<PilotScreenSummaryLike | undefined>(() => {
    const summary = summaryQuery.data
    if (!summary) return undefined
    return {
      title: summary.title,
      subtitle: summary.subtitle ?? undefined,
      available_tabs: summary.available_tabs,
      actions: summary.actions,
      performance: {
        initial_payload_budget_kb: summary.performance.initial_payload_budget_kb,
        lookup_min_chars: summary.performance.lookup_min_chars,
      },
    }
  }, [summaryQuery.data])

  // Phase 028: use native runtime when non-temporary ScreenDefinition available
  const useNativeRuntime = Boolean(
    nativeScreenQuery.data && nativeScreenQuery.data.adapter?.temporary === false,
  )

  const nativeRuntime = useUniversalMaskRuntime({
    screenId: 'crm/customer-360',
    entityId: id,
    schema: nativeScreenQuery.data,
    tabEndpoints: summaryQuery.data?.tab_endpoints,
    availableTabs: summaryQuery.data?.available_tabs,
    summaryTitle: summaryQuery.data?.title,
    summarySubtitle: summaryQuery.data?.subtitle ?? undefined,
    summaryItems,
    enabled: useNativeRuntime && Boolean(id),
  })

  // Legacy path (kept for fallback when native screen not available)
  const customerQuery = useCustomer(id ?? '', { enabled: !useNativeRuntime && Boolean(summaryQuery.data) })
  const tabDataQuery = useCustomerTabData(
    id ?? '',
    activeTabKey,
    summaryQuery.data?.tab_endpoints,
    tablePage,
  )

  const { plan: legacyPlan } = usePilotRenderPlan({
    screenId: 'crm/customer-360',
    domain: 'crm',
    maskConfig: {
      ...CUSTOMER_MASK_OBJECT_PAGE_CONFIG,
      title: summaryQuery.data?.title ?? customerQuery.data?.name ?? 'Kundenstamm Generator Pilot',
      subtitle: summaryQuery.data?.subtitle ?? 'Universal Mask Generator Pilot',
    },
    entityId: id,
    summaryEndpointPrefix: '/api/v1/crm/customers',
    summary: summaryForRenderPlan,
    nativeScreen: nativeScreenQuery.data,
    supplementalTabs: CRM360_SUPPLEMENTAL_TABS,
    enrichTabs: enrichTabsWithTables,
    summaryItems,
    enabled: !useNativeRuntime && Boolean(id),
  })

  const legacyData = useMemo(() => mapCustomerToMask(customerQuery.data), [customerQuery.data])
  const legacyTables = useMemo(() => mapTabDataToTables(tabDataQuery.data), [tabDataQuery.data])

  if (!id) {
    return (
      <div className="p-6">
        <Alert variant="destructive">
          <AlertTitle>Keine Kunden-ID</AlertTitle>
          <AlertDescription>Bitte rufen Sie die Seite mit einer gueltigen Kunden-ID auf.</AlertDescription>
        </Alert>
      </div>
    )
  }

  if (summaryQuery.error || (!useNativeRuntime && customerQuery.error)) {
    return (
      <div className="p-6">
        <Alert variant="destructive">
          <AlertTitle>Generator-Pilot nicht verfuegbar</AlertTitle>
          <AlertDescription>{getAxiosErrorMessage(summaryQuery.error ?? customerQuery.error)}</AlertDescription>
        </Alert>
      </div>
    )
  }

  // Native runtime path (Phase 028)
  if (useNativeRuntime && nativeRuntime.plan) {
    return (
      <div data-testid="universal-customer-mask-pilot" data-runtime="native">
        {nativeRuntime.isEntityLoading && (
          <div className="border-b bg-muted/30 px-4 py-2 text-sm text-muted-foreground md:px-8">
            Daten werden geladen…
          </div>
        )}
        <UniversalMaskRenderer
          plan={nativeRuntime.plan}
          data={nativeRuntime.entityData}
          tables={nativeRuntime.tableRows}
          tableQueryStates={nativeRuntime.tableQueryStates}
          tableTotals={nativeRuntime.tableTotals}
          lookupBindings={nativeRuntime.lookupBindings}
          onTabChange={onTabChange}
          onTableQueryChange={nativeRuntime.setTableQuery}
          overlay={nativeRuntime.userOverlay}
          onOverlayChange={nativeRuntime.updateUserOverlay}
          onOverlayReset={nativeRuntime.resetUserOverlay}
          onAction={() => undefined}
        />
      </div>
    )
  }

  // Legacy runtime path (fallback)
  return (
    <div data-testid="universal-customer-mask-pilot" data-runtime="legacy">
      {summaryQuery.isLoading ? (
        <div className="border-b bg-muted/30 px-4 py-2 text-sm text-muted-foreground md:px-8">
          Summary wird geladen...
        </div>
      ) : null}
      {customerQuery.isLoading ? (
        <div className="border-b bg-muted/20 px-4 py-2 text-sm text-muted-foreground md:px-8">
          Stammdaten werden nachgeladen...
        </div>
      ) : null}
      {tabDataQuery.isFetching && activeTabKey ? (
        <div
          className="border-b bg-muted/20 px-4 py-2 text-sm text-muted-foreground md:px-8"
          data-testid="tab-data-loading"
        >
          Tab-Daten werden geladen...
        </div>
      ) : null}
      {legacyPlan ? (
        <UniversalMaskRenderer
          plan={legacyPlan}
          data={legacyData}
          tables={legacyTables}
          onTabChange={onTabChange}
          onAction={() => undefined}
        />
      ) : null}
    </div>
  )
}

export default UniversalCustomerMaskPilotPage
