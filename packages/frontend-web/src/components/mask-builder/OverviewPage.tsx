import React from 'react'
// Badge import removed - not used
import { Button } from '@/components/ui/button'
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card'
import { Skeleton } from '@/components/ui/skeleton'
import { TrendingUp, TrendingDown, BarChart3, PieChart, LineChart } from 'lucide-react'
import { OverviewConfig, OverviewCard, OverviewChart } from './types'

interface OverviewPageProps {
  config: OverviewConfig
  onAction?: (_action: string) => void
  isLoading?: boolean
}

// Skeleton-Komponente für KPI-Karten
const KpiCardSkeleton: React.FC<{ title?: string }> = ({ title }) => (
  <Card>
    <CardHeader className="pb-2">
      <CardTitle className="text-sm font-medium flex items-center justify-between">
        {title || <Skeleton className="h-4 w-24" />}
        <Skeleton className="h-5 w-5 rounded" />
      </CardTitle>
    </CardHeader>
    <CardContent>
      <Skeleton className="h-8 w-20 mb-2" />
      <Skeleton className="h-3 w-32" />
    </CardContent>
  </Card>
)

// Skeleton-Komponente für Charts
const ChartSkeleton: React.FC<{ title?: string }> = ({ title }) => (
  <Card>
    <CardHeader>
      <CardTitle className="flex items-center gap-2">
        <Skeleton className="h-5 w-5" />
        {title || <Skeleton className="h-5 w-32" />}
      </CardTitle>
    </CardHeader>
    <CardContent>
      <Skeleton className="h-64 w-full" />
    </CardContent>
  </Card>
)

// Skeleton-Layout für das gesamte Dashboard
const DashboardSkeleton: React.FC<{ config: OverviewConfig }> = ({ config }) => (
  <div className="space-y-6 p-6">
    {/* Header */}
    <div className="flex items-center justify-between">
      <div>
        <h1 className="text-3xl font-bold">{config.title}</h1>
        {config.subtitle && (
          <p className="text-muted-foreground">{config.subtitle}</p>
        )}
      </div>
    </div>

    {/* KPI Cards Skeleton */}
    <div className="grid gap-4 md:grid-cols-2 lg:grid-cols-4">
      {config.cards?.map((card, i) => (
        <KpiCardSkeleton key={i} title={card.title} />
      )) || [1, 2, 3, 4].map(i => <KpiCardSkeleton key={i} />)}
    </div>

    {/* Charts Skeleton */}
    <div className="grid gap-6 md:grid-cols-2">
      {config.charts?.map((chart, i) => (
        <ChartSkeleton key={i} title={chart.title} />
      )) || [1, 2].map(i => <ChartSkeleton key={i} />)}
    </div>
  </div>
)

const OverviewPage: React.FC<OverviewPageProps> = ({
  config,
  onAction,
  isLoading = false
}) => {
  const renderCard = (card: OverviewCard) => (
    <Card key={card.title}>
      <CardHeader className="pb-2">
        <CardTitle className="text-sm font-medium flex items-center justify-between">
          {card.title}
          {card.icon && <span className="text-muted-foreground">{card.icon}</span>}
        </CardTitle>
      </CardHeader>
      <CardContent>
        <div className="text-2xl font-bold">{card.value}</div>
        {card.change && (
          <div className={`flex items-center text-xs mt-1 ${
            card.change.type === 'increase' ? 'text-green-600' : 'text-red-600'
          }`}>
            {card.change.type === 'increase' ? (
              <TrendingUp className="h-3 w-3 mr-1" />
            ) : (
              <TrendingDown className="h-3 w-3 mr-1" />
            )}
            {card.change.value}% {card.change.period}
          </div>
        )}
      </CardContent>
    </Card>
  )

  const renderChart = (chart: OverviewChart) => {
    // Simple chart placeholder - in real implementation, use a charting library
    const ChartIcon = chart.type === 'line' ? LineChart :
                     chart.type === 'bar' ? BarChart3 : PieChart

    return (
      <Card key={chart.title}>
        <CardHeader>
          <CardTitle className="flex items-center gap-2">
            <ChartIcon className="h-5 w-5" />
            {chart.title}
          </CardTitle>
        </CardHeader>
        <CardContent>
          <div className="h-64 flex items-center justify-center text-muted-foreground">
            Chart: {chart.type} - {chart.data.length} data points
          </div>
        </CardContent>
      </Card>
    )
  }

  // Während des Ladens: Skeleton-Vorschau mit Struktur
  if (isLoading) {
    return <DashboardSkeleton config={config} />
  }

  return (
    <div className="space-y-6 p-6">
      {/* Header */}
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-3xl font-bold">{config.title}</h1>
          {config.subtitle && (
            <p className="text-muted-foreground">{config.subtitle}</p>
          )}
        </div>
        <div className="flex gap-2">
          {config.actions?.map(action => (
            <Button
              key={action.key}
              variant={action.type === 'primary' ? 'default' : 'outline'}
              onClick={() => onAction?.(action.key)}
              className="gap-2"
            >
              {action.label}
            </Button>
          ))}
        </div>
      </div>

      {/* KPI Cards */}
      {config.cards && config.cards.length > 0 && (
        <div className="grid gap-4 md:grid-cols-2 lg:grid-cols-4">
          {config.cards.map(renderCard)}
        </div>
      )}

      {/* Charts */}
      {config.charts && config.charts.length > 0 && (
        <div className="grid gap-6 md:grid-cols-2">
          {config.charts.map(renderChart)}
        </div>
      )}

      {/* Additional Sections */}
      {config.sections?.map((section, index) => (
        <Card key={index}>
          <CardHeader>
            <CardTitle>{section.title}</CardTitle>
          </CardHeader>
          <CardContent>
            {section.content}
          </CardContent>
        </Card>
      ))}
    </div>
  )
}

export default OverviewPage