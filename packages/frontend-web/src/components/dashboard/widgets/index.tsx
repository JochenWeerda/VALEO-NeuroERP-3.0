import { type ReactNode } from 'react'
import { useQuery } from '@tanstack/react-query'
import { type WidgetLayout } from '@/hooks/useDashboardLayout'
import {
  ArrowDown,
  ArrowUp,
  BarChart3,
  Bell,
  CheckCircle,
  DollarSign,
  Package,
  ShoppingCart,
  TrendingUp,
  Users,
} from 'lucide-react'
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card'
import { Skeleton } from '@/components/ui/skeleton'
import { cn } from '@/lib/utils'
import { queryKeys } from '@/lib/query'
import { apiClient } from '@/lib/axios'

// Widget Registry
export interface WidgetDefinition {
  type: string
  name: string
  description: string
  icon: ReactNode
  defaultSize: { w: number; h: number }
  component: (props: { widget: WidgetLayout }) => ReactNode
}

// KPI-Mapping: Widget-ID zu Backend-KPI-Key
// Backend: GET /api/v1/analytics/kpis → { revenue, orders, customers, inventory, contract_long_tons, ... }
const NUM_DE = new Intl.NumberFormat('de-DE')
const NUM_DE_1 = new Intl.NumberFormat('de-DE', { minimumFractionDigits: 1, maximumFractionDigits: 1 })

const KPI_MAPPING: Record<string, { key: string; label: string; format: (value: number) => string; icon: ReactNode }> = {
  // Kern-Business-KPIs
  'kpi-revenue': {
    key: 'revenue',
    label: 'Umsatz',
    format: (value) => `€ ${NUM_DE.format(value)}`,
    icon: <DollarSign className="h-4 w-4" />,
  },
  'kpi-orders': {
    key: 'orders',
    label: 'Aufträge',
    format: (value) => NUM_DE.format(value),
    icon: <ShoppingCart className="h-4 w-4" />,
  },
  'kpi-customers': {
    key: 'customers',
    label: 'Kunden',
    format: (value) => NUM_DE.format(value),
    icon: <Users className="h-4 w-4" />,
  },
  'kpi-stock': {
    key: 'inventory',
    label: 'Lagerauslastung',
    format: (value) => `${NUM_DE_1.format(value)}%`,
    icon: <Package className="h-4 w-4" />,
  },
  // Agrar-spezifische KPIs
  'kpi-contract-long': {
    key: 'contract_long_tons',
    label: 'Kontrakt Long',
    format: (value) => `${NUM_DE_1.format(value)} t`,
    icon: <TrendingUp className="h-4 w-4" />,
  },
  'kpi-contract-short': {
    key: 'contract_short_tons',
    label: 'Kontrakt Short',
    format: (value) => `${NUM_DE_1.format(value)} t`,
    icon: <TrendingUp className="h-4 w-4" />,
  },
  'kpi-weighing-today': {
    key: 'weighing_today_tons',
    label: 'Wiegen heute',
    format: (value) => `${NUM_DE_1.format(value)} t`,
    icon: <Package className="h-4 w-4" />,
  },
  'kpi-inventory-blocked': {
    key: 'inventory_lots_blocked',
    label: 'Blockierte Lose',
    format: (value) => NUM_DE.format(value),
    icon: <Package className="h-4 w-4" />,
  },
}

// Mock-Daten als Fallback
const MOCK_KPI_DATA: Record<string, { label: string; value: string; delta: number; icon: ReactNode }> = {
  'kpi-revenue': {
    label: 'Umsatz',
    value: '€ 129.200',
    delta: 12.5,
    icon: <DollarSign className="h-4 w-4" />,
  },
  'kpi-orders': {
    label: 'Aufträge',
    value: '501',
    delta: 8.2,
    icon: <ShoppingCart className="h-4 w-4" />,
  },
  'kpi-customers': {
    label: 'Kunden',
    value: '1.234',
    delta: 3.1,
    icon: <Users className="h-4 w-4" />,
  },
  'kpi-stock': {
    label: 'Lager',
    value: '97%',
    delta: -2.1,
    icon: <Package className="h-4 w-4" />,
  },
}

// KPI Widget mit echten Backend-Daten
function KPIWidget({ widget }: { widget: WidgetLayout }) {
  const kpiConfig = KPI_MAPPING[widget.id]
  const mockData = MOCK_KPI_DATA[widget.id]

  // Lade echte KPI-Daten vom Backend, wenn Mapping vorhanden
  const { data: kpiData, isPending, isError } = useQuery({
    queryKey: queryKeys.analytics.kpis,
    queryFn: async () => {
      try {
        const response = await apiClient.get<Record<string, number>>('/api/v1/analytics/kpis')
        return response.data
      } catch (error) {
        console.warn('KPI-Daten konnten nicht geladen werden, verwende Fallback:', error)
        return null
      }
    },
    enabled: !!kpiConfig, // Nur laden, wenn Mapping vorhanden
    staleTime: 30 * 1000, // 30 Sekunden
    refetchInterval: 60 * 1000, // Alle 60 Sekunden aktualisieren
  })

  // Bestimme die anzuzeigenden Daten
  let displayData: { label: string; value: string; delta: number; icon: ReactNode }

  if (kpiConfig && kpiData && kpiData[kpiConfig.key] !== undefined) {
    // Echte Daten vom Backend
    const value = kpiData[kpiConfig.key] || 0
    displayData = {
      label: kpiConfig.label,
      value: kpiConfig.format(value),
      delta: 0, // TODO: Trend-Berechnung implementieren, wenn historische Daten verfügbar
      icon: kpiConfig.icon,
    }
  } else if (mockData) {
    // Fallback auf Mock-Daten
    displayData = mockData
  } else {
    // Default-Fallback
    displayData = {
      label: 'KPI',
      value: '-',
      delta: 0,
      icon: <BarChart3 className="h-4 w-4" />,
    }
  }

  const isPositive = displayData.delta >= 0
  const isLoading = isPending && kpiConfig

  return (
    <div className="p-4 h-full flex flex-col justify-between">
      <div className="flex items-center justify-between">
        <span className="text-sm font-medium text-muted-foreground">{displayData.label}</span>
        <span className="text-muted-foreground">{displayData.icon}</span>
      </div>
      <div className="mt-2">
        {isLoading ? (
          <Skeleton className="h-8 w-24" />
        ) : (
          <div className="text-2xl font-bold">{displayData.value}</div>
        )}
        {displayData.delta !== 0 && (
          <div
            className={cn(
              'flex items-center text-xs mt-1',
              isPositive ? 'text-green-600' : 'text-red-600'
            )}
          >
            {isPositive ? (
              <ArrowUp className="h-3 w-3 mr-1" />
            ) : (
              <ArrowDown className="h-3 w-3 mr-1" />
            )}
            <span>{Math.abs(displayData.delta)}% vs. Vormonat</span>
          </div>
        )}
      </div>
    </div>
  )
}

// Chart Widget
function ChartWidget({ widget }: { widget: WidgetLayout }) {
  const chartData: Record<string, { title: string; description: string }> = {
    'chart-sales': {
      title: 'Umsatzentwicklung',
      description: 'Monatlicher Umsatz der letzten 12 Monate',
    },
    'chart-trend': {
      title: 'Aufträge Trend',
      description: 'Wöchentliche Auftragseingänge',
    },
  }

  const data = chartData[widget.id] || {
    title: 'Chart',
    description: 'Diagramm',
  }

  // Simulate chart bars
  const bars = [40, 65, 45, 80, 55, 70, 85, 60, 75, 90, 65, 80]

  return (
    <div className="p-4 h-full flex flex-col">
      <div className="mb-4">
        <h3 className="font-semibold">{data.title}</h3>
        <p className="text-xs text-muted-foreground">{data.description}</p>
      </div>
      <div className="flex-1 flex items-end gap-1">
        {bars.map((height, i) => (
          <div
            key={i}
            className="flex-1 bg-primary/80 rounded-t transition-all hover:bg-primary"
            style={{ height: `${height}%` }}
          />
        ))}
      </div>
      <div className="flex justify-between text-xs text-muted-foreground mt-2">
        <span>Jan</span>
        <span>Jun</span>
        <span>Dez</span>
      </div>
    </div>
  )
}

// List Widget
function ListWidget({ widget }: { widget: WidgetLayout }) {
  const listData: Record<string, { title: string; items: { label: string; value: string; status?: 'success' | 'warning' | 'error' }[] }> = {
    'list-tasks': {
      title: 'Offene Aufgaben',
      items: [
        { label: 'Angebot #1234 prüfen', value: 'Heute', status: 'warning' },
        { label: 'Lieferung bestätigen', value: '2 Std.', status: 'success' },
        { label: 'Reklamation bearbeiten', value: 'Überfällig', status: 'error' },
        { label: 'Bestellung freigeben', value: 'Morgen', status: 'success' },
      ],
    },
    'list-alerts': {
      title: 'Wichtige Hinweise',
      items: [
        { label: 'Lagerbestand niedrig: Artikel #A123', value: '15 Stk.', status: 'warning' },
        { label: 'Zahlung überfällig: Kunde XY', value: '€ 2.500', status: 'error' },
        { label: 'Neuer Großauftrag eingegangen', value: '€ 45.000', status: 'success' },
      ],
    },
  }

  const data = listData[widget.id] || {
    title: 'Liste',
    items: [],
  }

  const statusColors = {
    success: 'text-green-600 bg-green-100',
    warning: 'text-amber-600 bg-amber-100',
    error: 'text-red-600 bg-red-100',
  }

  return (
    <div className="p-4 h-full flex flex-col">
      <div className="flex items-center justify-between mb-3">
        <h3 className="font-semibold">{data.title}</h3>
        <Bell className="h-4 w-4 text-muted-foreground" />
      </div>
      <div className="flex-1 space-y-2 overflow-auto">
        {data.items.map((item, i) => (
          <div
            key={i}
            className="flex items-center justify-between p-2 rounded-lg bg-muted/50 text-sm"
          >
            <span className="truncate flex-1">{item.label}</span>
            <span
              className={cn(
                'ml-2 px-2 py-0.5 rounded text-xs font-medium',
                item.status && statusColors[item.status]
              )}
            >
              {item.value}
            </span>
          </div>
        ))}
      </div>
    </div>
  )
}

// Widget Registry
export const widgetRegistry: WidgetDefinition[] = [
  {
    type: 'kpi',
    name: 'KPI-Karte',
    description: 'Einzelne Kennzahl mit Trend',
    icon: <TrendingUp className="h-4 w-4" />,
    defaultSize: { w: 1, h: 1 },
    component: KPIWidget,
  },
  {
    type: 'chart',
    name: 'Diagramm',
    description: 'Balken- oder Liniendiagramm',
    icon: <BarChart3 className="h-4 w-4" />,
    defaultSize: { w: 2, h: 2 },
    component: ChartWidget,
  },
  {
    type: 'list',
    name: 'Liste',
    description: 'Aufgaben oder Hinweise',
    icon: <CheckCircle className="h-4 w-4" />,
    defaultSize: { w: 2, h: 2 },
    component: ListWidget,
  },
]

// Get widget component by type
export function getWidgetComponent(type: string) {
  const definition = widgetRegistry.find((w) => w.type === type)
  return definition?.component || KPIWidget
}

