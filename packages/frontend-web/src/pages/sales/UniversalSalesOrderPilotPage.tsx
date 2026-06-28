import { useMemo, useState } from 'react'
import { useParams, useSearchParams } from '@/app/routing/typed-router'
import { Alert, AlertDescription, AlertTitle } from '@/components/ui/alert'
import {
  UniversalMaskRenderer,
  adaptMaskConfigToScreenDefinition,
  type ScreenDefinition,
  type ScreenSummaryItem,
  type ScreenTabDefinition,
} from '@/components/mask-builder'
import { mapSalesOrderToMask } from '@/features/sales-masks/mappers'
import { SALES_ORDER_MASK_OBJECT_PAGE_CONFIG } from '@/features/sales-masks/sales-order-mask-support'
import { SALES_ORDER_PILOT_TAB_TABLES } from '@/features/sales-masks/sales-order-tab-tables'
import { mapTabDataToTables, useSalesOrderTabData } from '@/features/sales-masks/use-sales-order-tab-data'
import { getAxiosErrorMessage } from '@/lib/api-client'
import { useSalesOrder, useSalesOrderScreenSummary } from '@/lib/api/sales'
import { useScreenDefinition } from '@/lib/api/masks'

function formatEuro(value: number, currency = 'EUR'): string {
  return new Intl.NumberFormat('de-DE', { style: 'currency', currency }).format(value)
}

function buildSummaryItems(summary: ReturnType<typeof useSalesOrderScreenSummary>['data']): ScreenSummaryItem[] {
  if (!summary) return []
  return [
    { key: 'total_amount', label: 'Auftragssumme', value: formatEuro(summary.summary.total_amount) },
    { key: 'item_count', label: 'Positionen', value: summary.summary.item_count },
    { key: 'status', label: 'Status', value: summary.summary.status },
    { key: 'delivery_date', label: 'Liefertermin', value: summary.summary.delivery_date ?? '-' },
  ]
}

function enrichTabsWithTables(tabs: ScreenTabDefinition[]): ScreenTabDefinition[] {
  return tabs.map((tab) => ({
    ...tab,
    tables: SALES_ORDER_PILOT_TAB_TABLES[tab.key] ?? tab.tables,
  }))
}

export default function UniversalSalesOrderPilotPage(): JSX.Element {
  const { id: routeId } = useParams<{ id?: string }>()
  const [searchParams] = useSearchParams()
  const id = routeId ?? searchParams.get('id') ?? undefined
  const [activeTabKey, setActiveTabKey] = useState<string | undefined>(undefined)

  const summaryQuery = useSalesOrderScreenSummary(id ?? '')
  const nativeScreenQuery = useScreenDefinition('sales/sales-order', { enabled: Boolean(id) })
  const orderQuery = useSalesOrder(id ?? '', { enabled: Boolean(summaryQuery.data) })
  const tabDataQuery = useSalesOrderTabData(id ?? '', activeTabKey, summaryQuery.data?.tab_endpoints)

  const screen = useMemo(() => {
    const adapted = adaptMaskConfigToScreenDefinition(
      {
        ...SALES_ORDER_MASK_OBJECT_PAGE_CONFIG,
        title: summaryQuery.data?.title ?? 'Verkaufsauftrag Generator Pilot',
        subtitle: summaryQuery.data?.subtitle ?? orderQuery.data?.order_number,
      },
      {
        id: 'sales/sales-order',
        domain: 'sales',
        sourceId: 'sales-order-mask-inline',
        summaryEndpoint: id ? `/api/v1/sales/orders/${id}/screen-summary` : undefined,
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
          tabs: enrichTabsWithTables(adapted.tabs ?? []),
          fields: adapted.fields,
        }
      : { ...adapted, tabs: enrichTabsWithTables(adapted.tabs ?? []) }

    return {
      ...definition,
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
        initialPayloadBudgetKb: summaryQuery.data?.performance.initial_payload_budget_kb ?? 56,
        requiresLazyTabs: true,
        requiresVirtualTables: true,
        lookupMinChars: summaryQuery.data?.performance.lookup_min_chars ?? 2,
      },
    }
  }, [id, nativeScreenQuery.data, orderQuery.data?.order_number, summaryQuery.data])

  const data = useMemo(() => {
    const base = mapSalesOrderToMask(orderQuery.data)
    const customerName = summaryQuery.data?.customer_name
    if (customerName && base.order && typeof base.order === 'object') {
      return {
        ...base,
        order: { ...(base.order as Record<string, unknown>), customer_name: customerName },
      }
    }
    return base
  }, [orderQuery.data, summaryQuery.data?.customer_name])
  const tables = useMemo(() => mapTabDataToTables(tabDataQuery.data), [tabDataQuery.data])
  const allowedPermissions = useMemo(
    () => summaryQuery.data?.actions.flatMap((action) => action.permission ? [action.permission] : []) ?? [],
    [summaryQuery.data],
  )

  if (!id) {
    return (
      <div className="p-6">
        <Alert variant="destructive">
          <AlertTitle>Keine Auftrags-ID</AlertTitle>
          <AlertDescription>Der Generator-Pilot ist nur fuer bestehende Auftraege verfuegbar.</AlertDescription>
        </Alert>
      </div>
    )
  }

  if (summaryQuery.error || orderQuery.error) {
    return (
      <div className="p-6">
        <Alert variant="destructive">
          <AlertTitle>Generator-Pilot nicht verfuegbar</AlertTitle>
          <AlertDescription>{getAxiosErrorMessage(summaryQuery.error ?? orderQuery.error)}</AlertDescription>
        </Alert>
      </div>
    )
  }

  return (
    <div data-testid="universal-sales-order-pilot">
      {summaryQuery.isLoading ? (
        <div className="border-b bg-muted/30 px-4 py-2 text-sm text-muted-foreground md:px-8">
          Summary wird geladen...
        </div>
      ) : null}
      {orderQuery.isLoading ? (
        <div className="border-b bg-muted/20 px-4 py-2 text-sm text-muted-foreground md:px-8">
          Auftragsdaten werden nachgeladen...
        </div>
      ) : null}
      {tabDataQuery.isFetching && activeTabKey ? (
        <div className="border-b bg-muted/20 px-4 py-2 text-sm text-muted-foreground md:px-8" data-testid="tab-data-loading">
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
