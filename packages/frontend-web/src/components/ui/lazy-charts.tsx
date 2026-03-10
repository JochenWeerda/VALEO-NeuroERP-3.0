import { lazy, Suspense, type JSX } from 'react'

interface BaseLazyChartProps {
  data: Array<{ name: string; value: number }>
  dataKey: string
  height?: number
}

interface LazyAreaChartProps extends BaseLazyChartProps {
  stroke: string
  fill: string
}

interface LazyBarChartProps extends BaseLazyChartProps {
  fill: string
}

const AreaTrendChart = lazy(() => import('./lazy-charts/AreaTrendChart'))
const BarTrendChart = lazy(() => import('./lazy-charts/BarTrendChart'))

function ChartSkeleton({ height = 200 }: { height?: number }): JSX.Element {
  return (
    <div style={{ height, width: '100%' }}>
      <div className="flex h-full w-full animate-pulse items-center justify-center rounded-md bg-muted/20">
        <div className="text-sm text-muted-foreground">Diagramm wird geladen...</div>
      </div>
    </div>
  )
}

export function LazyAreaChart({ height = 200, ...props }: LazyAreaChartProps): JSX.Element {
  return (
    <Suspense fallback={<ChartSkeleton height={height} />}>
      <div style={{ height, width: '100%' }}>
        <AreaTrendChart {...props} />
      </div>
    </Suspense>
  )
}

export function LazyBarChart({ height = 200, ...props }: LazyBarChartProps): JSX.Element {
  return (
    <Suspense fallback={<ChartSkeleton height={height} />}>
      <div style={{ height, width: '100%' }}>
        <BarTrendChart {...props} />
      </div>
    </Suspense>
  )
}
