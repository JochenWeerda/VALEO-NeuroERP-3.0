import { type ReactNode, useMemo } from 'react'
import { PageToolbar, type ToolbarAction } from '@/components/navigation/PageToolbar'
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card'
import { cn } from '@/lib/utils'
import { TrendingDown, TrendingUp } from 'lucide-react'
import { createMCPMetadata } from '@/design/mcp-schemas/component-metadata'
import { buildToolbarActionsFromRegistry, useActionsForMask, useActionDispatchOptional } from '@/features/ki-usability'
import { auth } from '@/lib/auth'
import { limitItemsForDensity, resolveRoleDensityProfile } from '@/features/role-density'
import { useTenant } from '@/hooks/useTenant'
import { useUIDensityManifest } from '@/lib/api/ui-density-manifest'
import { PageSection, PageSurface } from '@/components/patterns/PageSurface'

export interface OverviewKpi {
  label: string
  value: string | number
  trend?: {
    value: number
    direction: 'up' | 'down'
  }
  icon?: ReactNode
  onClick?: () => void
}

export interface OverviewPageProps {
  title: string
  subtitle?: string
  kpis: OverviewKpi[]
  charts?: ReactNode[]
  lists?: ReactNode[]
  primaryActions?: ToolbarAction[]
  overflowActions?: ToolbarAction[]
  mcpContext?: {
    pageDomain: string
    analyticsContext?: string
  }
}

export const overviewPageMCP = createMCPMetadata('OverviewPage', 'overview', {
  accessibility: {
    role: 'main',
    ariaLabel: 'Overview dashboard',
  },
  intent: {
    purpose: 'Surface KPIs, charts, and quick navigation for a domain',
    userActions: ['open-kpi', 'open-chart', 'open-list'],
    dataContext: ['analytics', 'dashboard'],
  },
  mcpHints: {
    explainable: true,
    contextAware: true,
  },
})

const renderTrend = (trend: OverviewKpi['trend']): ReactNode => {
  if (!trend) {
    return null
  }

  const Icon = trend.direction === 'up' ? TrendingUp : TrendingDown
  const trendClass = trend.direction === 'up' ? 'text-green-600' : 'text-red-600'

  return (
    <span className={cn('mt-2 flex items-center gap-1 text-sm', trendClass)}>
      <Icon className="h-4 w-4" />
      {Math.abs(trend.value).toLocaleString('de-DE', { maximumFractionDigits: 1 })}%
    </span>
  )
}

export function OverviewPage({
  title,
  subtitle,
  kpis,
  charts,
  lists,
  primaryActions,
  overflowActions,
  mcpContext,
}: OverviewPageProps): JSX.Element {
  const actionDispatch = useActionDispatchOptional()
  const { tenantId } = useTenant()
  const { data: actionResponse } = useActionsForMask(mcpContext?.pageDomain, mcpContext?.analyticsContext)
  const densityManifestQuery = useUIDensityManifest(mcpContext?.pageDomain)
  const roleDensityProfile = useMemo(
    () =>
      resolveRoleDensityProfile(auth.getUser()?.roles, {
        tenantId,
        pageDomain: mcpContext?.pageDomain,
        availableActionIds: actionResponse?.actions?.map((action) => action.id) ?? [],
        backendDensity: densityManifestQuery.data?.entry?.recommended_density,
      }),
    [actionResponse?.actions, densityManifestQuery.data?.entry?.recommended_density, mcpContext?.pageDomain, tenantId],
  )
  const contextualToolbarActions = useMemo(
    () => buildToolbarActionsFromRegistry(actionResponse?.actions, actionDispatch),
    [actionDispatch, actionResponse?.actions],
  )
  const visibleKpis = useMemo(() => limitItemsForDensity(kpis, roleDensityProfile.maxKpis), [kpis, roleDensityProfile.maxKpis])
  const visibleCharts = useMemo(
    () => limitItemsForDensity(charts, roleDensityProfile.maxCharts),
    [charts, roleDensityProfile.maxCharts],
  )
  const visibleLists = useMemo(() => limitItemsForDensity(lists, roleDensityProfile.maxLists), [lists, roleDensityProfile.maxLists])

  const mergedPrimaryActions = useMemo<ToolbarAction[]>(() => {
    if (Array.isArray(primaryActions) && primaryActions.length > 0) {
      return primaryActions
    }
    return contextualToolbarActions.primary
  }, [contextualToolbarActions.primary, primaryActions])

  const mergedOverflowActions = useMemo<ToolbarAction[]>(() => {
    const fromProps = overflowActions ?? []
    const hasPrimaryFromProps = Array.isArray(primaryActions) && primaryActions.length > 0
    const quickOverflow = hasPrimaryFromProps ? contextualToolbarActions.overflow : contextualToolbarActions.overflow
    const byId = new Map<string, ToolbarAction>()
    for (const action of [...fromProps, ...quickOverflow]) {
      byId.set(action.id, action)
    }
    return Array.from(byId.values())
  }, [contextualToolbarActions.overflow, overflowActions, primaryActions])

  return (
    <div
      className="flex h-full flex-col"
      data-mcp-pattern="overview-page"
      data-mcp-analytics-context={mcpContext?.analyticsContext}
    >
      <PageToolbar
        title={title}
        subtitle={subtitle}
        primaryActions={mergedPrimaryActions}
        overflowActions={mergedOverflowActions}
        densityProfileOverride={roleDensityProfile}
        mcpContext={
          mcpContext
            ? {
                pageDomain: mcpContext.pageDomain,
                currentDocument: mcpContext.analyticsContext,
                availableActions: [
                  ...mergedPrimaryActions.map((action) => action.id),
                  ...mergedOverflowActions.map((action) => action.id),
                ],
              }
            : undefined
        }
      />

      <PageSurface data-page-surface="overview-pattern" contentClassName="space-y-6">
        <section aria-label="KPI cards" className="grid gap-4 sm:grid-cols-2 lg:grid-cols-4">
          {visibleKpis.map((kpi) => {
            const hasClickHandler = typeof kpi.onClick === 'function'
            const cardOnClick = hasClickHandler ? kpi.onClick : undefined
            const iconDefined = kpi.icon !== undefined && kpi.icon !== null
            return (
              <Card
                key={kpi.label}
                className={cn(
                  'cursor-pointer transition-shadow',
                  hasClickHandler ? 'hover:shadow-md' : 'cursor-default',
                )}
                onClick={cardOnClick}
                data-mcp-kpi={kpi.label}
              >
                <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
                  <CardTitle className="text-sm font-medium text-muted-foreground">{kpi.label}</CardTitle>
                  {iconDefined ? <div className="text-muted-foreground">{kpi.icon}</div> : null}
                </CardHeader>
                <CardContent>
                  <div className="text-3xl font-bold">{kpi.value}</div>
                  {renderTrend(kpi.trend)}
                </CardContent>
              </Card>
            )
          })}
        </section>

        {visibleCharts.length > 0 ? (
          <section aria-label="Charts" className="grid gap-6 lg:grid-cols-2">
            {visibleCharts.map((chart, index) => (
              <Card key={index} className="rounded-3xl border-border/70 shadow-sm shadow-primary/5">
                <CardContent className="pt-6">{chart}</CardContent>
              </Card>
            ))}
          </section>
        ) : null}

        {visibleLists.length > 0 ? (
          <PageSection
            title="Analytische Listen"
            description="Sekundäre Übersichten, Ausreißer und Drilldowns im selben Designsystem-Rahmen."
            className="space-y-4"
          >
            {visibleLists.map((list, index) => (
              <Card key={index} className="rounded-2xl border-border/70 shadow-sm">
                <CardContent className="pt-6">{list}</CardContent>
              </Card>
            ))}
          </PageSection>
        ) : null}
      </PageSurface>
    </div>
  )
}
