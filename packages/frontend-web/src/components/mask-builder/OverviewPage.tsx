import React from 'react'
// Badge import removed - not used
import { Button } from '@/components/ui/button'
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card'
import { TrendingUp, TrendingDown, BarChart3, PieChart, LineChart } from 'lucide-react'
import { OverviewConfig, OverviewCard, OverviewChart } from './types'

interface OverviewPageProps {
  config: OverviewConfig
  onAction?: (_action: string) => void
  isLoading?: boolean
}

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

  if (isLoading) {
    return (
      <div className="flex items-center justify-center p-8">
        <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-blue-600"></div>
        <span className="ml-2">Laden...</span>
      </div>
    )
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