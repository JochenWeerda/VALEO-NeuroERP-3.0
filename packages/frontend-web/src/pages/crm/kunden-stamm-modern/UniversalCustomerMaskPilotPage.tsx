import { useMemo, useState } from 'react'
import { useParams } from '@/app/routing/typed-router'
import { Alert, AlertDescription, AlertTitle } from '@/components/ui/alert'
import {
  UniversalMaskRenderer,
  adaptMaskConfigToScreenDefinition,
  type ScreenDefinition,
  type ScreenSummaryItem,
  type ScreenTabDefinition,
} from '@/components/mask-builder'
import {
  CUSTOMER_MASK_OBJECT_PAGE_CONFIG,
} from '@/features/crm-masks/customer-mask-support'
import { CUSTOMER_PILOT_TAB_TABLES } from '@/features/crm-masks/customer-tab-tables'
import { mapCustomerToMask } from '@/features/crm-masks/mappers'
import { mapTabDataToTables, useCustomerTabData } from '@/features/crm-masks/use-customer-tab-data'
import { getAxiosErrorMessage } from '@/lib/api-client'
import { useCustomer, useCustomerScreenSummary } from '@/lib/api/crm'
import { useScreenDefinition } from '@/lib/api/masks'

const CRM360_SUPPLEMENTAL_TABS: ScreenTabDefinition[] = [
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

function mergeSupplementalTabs(tabs: ScreenTabDefinition[], availableTabs: string[] | undefined): ScreenTabDefinition[] {
  const existing = new Set(tabs.map((tab) => tab.key))
  const supplemental = CRM360_SUPPLEMENTAL_TABS.filter((tab) => {
    if (existing.has(tab.key)) return false
    return !availableTabs || availableTabs.includes(tab.key)
  })
  return [...tabs, ...supplemental]
}

function getCustomerIdFromSearch(): string | undefined {
  if (typeof window === 'undefined') return undefined
  return new URLSearchParams(window.location.search).get('id') ?? undefined
}

function UniversalCustomerMaskPilotPage(): JSX.Element {
  const { id: routeId } = useParams<{ id?: string }>()
  const id = routeId ?? getCustomerIdFromSearch()
  const [activeTabKey, setActiveTabKey] = useState<string | undefined>(undefined)
  const summaryQuery = useCustomerScreenSummary(id ?? '')
  const nativeScreenQuery = useScreenDefinition('crm/customer-360', { enabled: Boolean(id) })
  const customerQuery = useCustomer(id ?? '', { enabled: Boolean(summaryQuery.data) })
  const tabDataQuery = useCustomerTabData(id ?? '', activeTabKey, summaryQuery.data?.tab_endpoints)

  const screen = useMemo(() => {
    const adapted = adaptMaskConfigToScreenDefinition(
      {
        ...CUSTOMER_MASK_OBJECT_PAGE_CONFIG,
        title: summaryQuery.data?.title ?? customerQuery.data?.name ?? 'Kundenstamm Generator Pilot',
        subtitle: summaryQuery.data?.subtitle ?? 'Universal Mask Generator Pilot',
      },
      {
        id: 'crm/customer-360',
        domain: 'crm',
        sourceId: 'mask-builder-customer.json',
        summaryEndpoint: id ? `/api/v1/crm/customers/${id}/screen-summary` : undefined,
      },
    )

    const nativeBase: ScreenDefinition | undefined = nativeScreenQuery.data
    const definition: ScreenDefinition = nativeBase
      ? {
          ...adapted,
          ...nativeBase,
          adapter: nativeBase.adapter,
          performance: nativeBase.performance,
          layout: nativeBase.layout,
          summaryEndpoint: nativeBase.summaryEndpoint ?? adapted.summaryEndpoint,
          tabs: adapted.tabs,
          fields: adapted.fields,
        }
      : adapted

    const tabs = mergeSupplementalTabs(
      enrichTabsWithTables(definition.tabs ?? adapted.tabs ?? []),
      summaryQuery.data?.available_tabs,
    )

    return {
      ...definition,
      tabs,
      title: summaryQuery.data?.title ?? definition.title,
      subtitle: summaryQuery.data?.subtitle ?? definition.subtitle,
      summary: buildSummaryItems(summaryQuery.data),
      actions: summaryQuery.data?.actions.map((action) => ({
        key: action.key,
        label: action.label,
        kind: action.key === 'edit' ? 'primary' as const : 'secondary' as const,
        permission: action.permission,
      })) ?? [],
      layout: {
        preferredMode: 'desktopDense' as const,
        mobileMode: 'mobileStack' as const,
        touchTargetPx: 44,
      },
      performance: {
        ...definition.performance,
        initialPayloadBudgetKb: summaryQuery.data?.performance.initial_payload_budget_kb ?? 48,
        requiresLazyTabs: true,
        requiresVirtualTables: true,
        lookupMinChars: summaryQuery.data?.performance.lookup_min_chars ?? 2,
      },
    }
  }, [customerQuery.data?.name, id, nativeScreenQuery.data, summaryQuery.data])

  const data = useMemo(() => mapCustomerToMask(customerQuery.data), [customerQuery.data])
  const tables = useMemo(() => mapTabDataToTables(tabDataQuery.data), [tabDataQuery.data])
  const allowedPermissions = useMemo(
    () => summaryQuery.data?.actions.flatMap((action) => action.permission ? [action.permission] : []) ?? [],
    [summaryQuery.data],
  )

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

  if (summaryQuery.error || customerQuery.error) {
    return (
      <div className="p-6">
        <Alert variant="destructive">
          <AlertTitle>Generator-Pilot nicht verfuegbar</AlertTitle>
          <AlertDescription>{getAxiosErrorMessage(summaryQuery.error ?? customerQuery.error)}</AlertDescription>
        </Alert>
      </div>
    )
  }

  return (
    <div data-testid="universal-customer-mask-pilot">
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
      <UniversalMaskRenderer
        screen={screen}
        data={data}
        tables={tables}
        allowedPermissions={allowedPermissions}
        onTabChange={setActiveTabKey}
        onAction={() => undefined}
      />
    </div>
  )
}

export default UniversalCustomerMaskPilotPage
