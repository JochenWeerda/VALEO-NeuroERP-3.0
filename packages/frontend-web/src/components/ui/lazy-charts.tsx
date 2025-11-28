/**
 * Lazy-loaded Chart-Komponenten für bessere Performance
 * 
 * Diese Wrapper laden recharts erst wenn tatsächlich benötigt,
 * wodurch der initiale Bundle-Size reduziert wird.
 * 
 * Verwendung:
 * import { LazyLineChart, LazyBarChart, LazyPieChart } from '@/components/ui/lazy-charts'
 */

import { lazy, Suspense, ComponentType } from 'react'
import type {
  LineChartProps,
  BarChartProps,
  PieChartProps,
  AreaChartProps,
  ComposedChartProps,
  ResponsiveContainerProps,
} from 'recharts'

// Lazy imports für recharts Komponenten
const LineChartLazy = lazy(() =>
  import('recharts').then((module) => ({ default: module.LineChart }))
)

const BarChartLazy = lazy(() =>
  import('recharts').then((module) => ({ default: module.BarChart }))
)

const PieChartLazy = lazy(() =>
  import('recharts').then((module) => ({ default: module.PieChart }))
)

const AreaChartLazy = lazy(() =>
  import('recharts').then((module) => ({ default: module.AreaChart }))
)

const ComposedChartLazy = lazy(() =>
  import('recharts').then((module) => ({ default: module.ComposedChart }))
)

const ResponsiveContainerLazy = lazy(() =>
  import('recharts').then((module) => ({ default: module.ResponsiveContainer }))
)

// Chart Loading Skeleton
function ChartSkeleton(): JSX.Element {
  return (
    <div className="flex h-full w-full items-center justify-center bg-muted/20 rounded-md animate-pulse">
      <div className="text-muted-foreground text-sm">Diagramm wird geladen...</div>
    </div>
  )
}

// Wrapper HOC für Lazy Charts
function withLazySuspense<P extends object>(
  Component: ComponentType<P>,
  fallbackHeight = '200px'
): ComponentType<P> {
  return function LazyWrapper(props: P) {
    return (
      <Suspense
        fallback={
          <div style={{ height: fallbackHeight, width: '100%' }}>
            <ChartSkeleton />
          </div>
        }
      >
        <Component {...props} />
      </Suspense>
    )
  }
}

// Exportierte Lazy-Chart-Komponenten
export const LazyLineChart = withLazySuspense(LineChartLazy as ComponentType<LineChartProps>)
export const LazyBarChart = withLazySuspense(BarChartLazy as ComponentType<BarChartProps>)
export const LazyPieChart = withLazySuspense(PieChartLazy as ComponentType<PieChartProps>)
export const LazyAreaChart = withLazySuspense(AreaChartLazy as ComponentType<AreaChartProps>)
export const LazyComposedChart = withLazySuspense(ComposedChartLazy as ComponentType<ComposedChartProps>)
export const LazyResponsiveContainer = withLazySuspense(
  ResponsiveContainerLazy as ComponentType<ResponsiveContainerProps>,
  '100%'
)

// Re-export der anderen recharts Komponenten für Convenience
// Diese können normal importiert werden da sie leichtgewichtig sind
export {
  XAxis,
  YAxis,
  CartesianGrid,
  Tooltip,
  Legend,
  Line,
  Bar,
  Pie,
  Area,
  Cell,
  ReferenceLine,
  ReferenceArea,
  Brush,
  Scatter,
} from 'recharts'

