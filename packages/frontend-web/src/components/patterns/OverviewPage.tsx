import { type ReactNode } from 'react'
import { PageToolbar, type ToolbarAction } from '@/components/navigation/PageToolbar'
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card'
import { cn } from '@/lib/utils'
import { TrendingDown, TrendingUp } from 'lucide-react'
import { createMCPMetadata } from '@/design/mcp-schemas/component-metadata'

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
  return (
    <div
      className="flex h-full flex-col"
      data-mcp-pattern="overview-page"
      data-mcp-analytics-context={mcpContext?.analyticsContext}
    >
      <PageToolbar
        title={title}
        subtitle={subtitle}
        primaryActions={primaryActions}
        overflowActions={overflowActions}
        mcpContext={
          mcpContext
            ? {
                pageDomain: mcpContext.pageDomain,
                currentDocument: mcpContext.analyticsContext,
                availableActions: [
                  ...(primaryActions?.map((action) => action.id) ?? []),
                  ...(overflowActions?.map((action) => action.id) ?? []),
                ],
              }
            : undefined
        }
      />

      <div className="flex-1 space-y-6 overflow-y-auto p-6">
        <section aria-label="KPI cards" className="grid gap-4 sm:grid-cols-2 lg:grid-cols-4">
          {kpis.map((kpi) => {
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

        {Array.isArray(charts) && charts.length > 0 ? (
          <section aria-label="Charts" className="grid gap-6 lg:grid-cols-2">
            {charts.map((chart, index) => (
              <Card key={index} className="shadow-sm">
                <CardContent className="pt-6">{chart}</CardContent>
              </Card>
            ))}
          </section>
        ) : null}

        {Array.isArray(lists) && lists.length > 0 ? (
          <section aria-label="Analytic lists" className="space-y-4">
            {lists.map((list, index) => (
              <Card key={index} className="shadow-sm">
                <CardContent className="pt-6">{list}</CardContent>
              </Card>
            ))}
          </section>
        ) : null}
      </div>
    </div>
  )
}
