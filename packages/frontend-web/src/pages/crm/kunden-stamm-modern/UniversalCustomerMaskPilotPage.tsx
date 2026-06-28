import { useMemo } from 'react'
import { useParams } from '@/app/routing/typed-router'
import { Alert, AlertDescription, AlertTitle } from '@/components/ui/alert'
import { UniversalMaskRenderer, adaptMaskConfigToScreenDefinition, type ScreenSummaryItem } from '@/components/mask-builder'
import {
  CUSTOMER_MASK_OBJECT_PAGE_CONFIG,
} from '@/features/crm-masks/customer-mask-support'
import { mapCustomerToMask } from '@/features/crm-masks/mappers'
import { getAxiosErrorMessage } from '@/lib/api-client'
import { useCustomer, useCustomerScreenSummary } from '@/lib/api/crm'

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

function getCustomerIdFromSearch(): string | undefined {
  if (typeof window === 'undefined') return undefined
  return new URLSearchParams(window.location.search).get('id') ?? undefined
}

function UniversalCustomerMaskPilotPage(): JSX.Element {
  const { id: routeId } = useParams<{ id?: string }>()
  const id = routeId ?? getCustomerIdFromSearch()
  const summaryQuery = useCustomerScreenSummary(id ?? '')
  const customerQuery = useCustomer(id ?? '', { enabled: Boolean(summaryQuery.data) })

  const screen = useMemo(() => {
    const definition = adaptMaskConfigToScreenDefinition(
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

    return {
      ...definition,
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
  }, [customerQuery.data?.name, id, summaryQuery.data])

  const data = useMemo(() => mapCustomerToMask(customerQuery.data), [customerQuery.data])
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
      <UniversalMaskRenderer
        screen={screen}
        data={data}
        allowedPermissions={allowedPermissions}
        onAction={() => undefined}
      />
    </div>
  )
}

export default UniversalCustomerMaskPilotPage
