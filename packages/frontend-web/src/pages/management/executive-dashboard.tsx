/**
 * Executive Dashboard
 *
 * Management-Übersicht mit KPIs, Trends und Handlungsbedarf
 * Optimiert für schnelle Entscheidungsfindung
 */

import { useState, useMemo } from 'react'
import { useQuery } from '@tanstack/react-query'
import { useNavigate } from 'react-router-dom'
import { cn } from '@/lib/utils'
import {
  Euro,
  ShoppingCart,
  Users,
  Package,
  TrendingUp,
  Calendar,
  Download,
  RefreshCw,
  Filter,
  ChevronDown,
} from 'lucide-react'
import { KPICard, KPIGrid } from '@/components/management/KPICard'
import { AlertWidget, AlertItem } from '@/components/management/AlertWidget'
import { TrendChart, TrendDataPoint } from '@/components/management/TrendChart'
import {
  Select,
  SelectContent,
  SelectItem,
  SelectTrigger,
  SelectValue,
} from '@/components/ui/select'
import { Button } from '@/components/ui/button'
import { Skeleton } from '@/components/ui/skeleton'

type TimeRange = '7d' | '30d' | '90d' | '365d' | 'ytd'

interface DashboardData {
  kpis: {
    revenue: { value: number; trend: number; target: number }
    orders: { value: number; trend: number }
    customers: { value: number; trend: number; newCount: number }
    inventory: { value: number; trend: number }
  }
  revenueTrend: TrendDataPoint[]
  ordersTrend: TrendDataPoint[]
  alerts: AlertItem[]
  topProducts: { name: string; revenue: number; quantity: number }[]
  topCustomers: { name: string; revenue: number; orders: number }[]
}

// Mock-Daten (später durch echte API ersetzen)
async function fetchDashboardData(range: TimeRange): Promise<DashboardData> {
  await new Promise(resolve => setTimeout(resolve, 800))

  const multiplier = range === '7d' ? 0.25 : range === '30d' ? 1 : range === '90d' ? 3 : 12

  return {
    kpis: {
      revenue: {
        value: Math.round(125000 * multiplier),
        trend: 12.5,
        target: Math.round(150000 * multiplier),
      },
      orders: { value: Math.round(45 * multiplier), trend: 8.3 },
      customers: { value: 234, trend: 5.2, newCount: Math.round(12 * multiplier) },
      inventory: { value: 1250000, trend: -2.1 },
    },
    revenueTrend: generateTrendData(7, 15000, 25000),
    ordersTrend: generateTrendData(7, 3, 8),
    alerts: [
      {
        id: '1',
        type: 'critical',
        category: 'finance',
        title: 'Offene Forderungen über 90 Tage',
        description: '3 Kunden mit überfälligen Rechnungen',
        value: '€ 45.230',
        timestamp: 'Heute',
        actionUrl: '/finance/op-debitoren',
      },
      {
        id: '2',
        type: 'warning',
        category: 'inventory',
        title: 'Niedriger Lagerbestand',
        description: '5 Artikel unter Mindestbestand',
        actionUrl: '/lager/bestandsuebersicht',
      },
      {
        id: '3',
        type: 'warning',
        category: 'sales',
        title: 'Angebote ohne Rückmeldung',
        description: '8 Angebote älter als 14 Tage',
        value: '€ 78.500',
        actionUrl: '/sales/angebote-liste',
      },
      {
        id: '4',
        type: 'info',
        category: 'customer',
        title: 'Kundengeburtstage diese Woche',
        description: '3 Kunden haben Geburtstag',
        actionUrl: '/crm/kunden-stamm',
      },
    ],
    topProducts: [
      { name: 'Weizen Saatgut Premium', revenue: 45000, quantity: 180 },
      { name: 'NPK Dünger 15-15-15', revenue: 38000, quantity: 95 },
      { name: 'Pflanzenschutz XP-200', revenue: 28000, quantity: 140 },
      { name: 'Diesel Winterqualität', revenue: 22000, quantity: 12000 },
      { name: 'Ersatzteile Set A', revenue: 15000, quantity: 45 },
    ],
    topCustomers: [
      { name: 'Landwirtschaft Müller GmbH', revenue: 85000, orders: 12 },
      { name: 'Agrar Schneider', revenue: 62000, orders: 8 },
      { name: 'Biolandhof Weber', revenue: 48000, orders: 15 },
      { name: 'Genossenschaft Blumental', revenue: 41000, orders: 6 },
      { name: 'Hof Sonnenschein', revenue: 35000, orders: 9 },
    ],
  }
}

function generateTrendData(days: number, min: number, max: number): TrendDataPoint[] {
  const data: TrendDataPoint[] = []
  const now = new Date()

  for (let i = days - 1; i >= 0; i--) {
    const date = new Date(now)
    date.setDate(date.getDate() - i)
    data.push({
      label: date.toLocaleDateString('de-DE', { day: '2-digit', month: '2-digit' }),
      value: Math.round(min + Math.random() * (max - min)),
    })
  }

  return data
}

export default function ExecutiveDashboardPage(): JSX.Element {
  const navigate = useNavigate()
  const [timeRange, setTimeRange] = useState<TimeRange>('30d')

  const { data, isLoading, refetch, isFetching } = useQuery({
    queryKey: ['executive-dashboard', timeRange],
    queryFn: () => fetchDashboardData(timeRange),
    staleTime: 5 * 60 * 1000,
  })

  const timeRangeLabels: Record<TimeRange, string> = {
    '7d': 'Letzte 7 Tage',
    '30d': 'Letzte 30 Tage',
    '90d': 'Letzte 90 Tage',
    '365d': 'Letztes Jahr',
    'ytd': 'Jahr bis heute',
  }

  return (
    <div className="space-y-6 p-6">
      {/* Header */}
      <div className="flex flex-col sm:flex-row sm:items-center sm:justify-between gap-4">
        <div>
          <h1 className="text-2xl font-bold">Executive Dashboard</h1>
          <p className="text-muted-foreground">
            Übersicht der wichtigsten Geschäftskennzahlen
          </p>
        </div>

        <div className="flex items-center gap-2">
          <Select value={timeRange} onValueChange={(v) => setTimeRange(v as TimeRange)}>
            <SelectTrigger className="w-[180px]">
              <Calendar className="h-4 w-4 mr-2" />
              <SelectValue />
            </SelectTrigger>
            <SelectContent>
              {Object.entries(timeRangeLabels).map(([value, label]) => (
                <SelectItem key={value} value={value}>
                  {label}
                </SelectItem>
              ))}
            </SelectContent>
          </Select>

          <Button
            variant="outline"
            size="icon"
            onClick={() => refetch()}
            disabled={isFetching}
          >
            <RefreshCw className={cn('h-4 w-4', isFetching && 'animate-spin')} />
          </Button>

          <Button variant="outline">
            <Download className="h-4 w-4 mr-2" />
            Export
          </Button>
        </div>
      </div>

      {/* KPI Cards */}
      {isLoading ? (
        <KPIGrid columns={4}>
          {[1, 2, 3, 4].map((i) => (
            <Skeleton key={i} className="h-32 rounded-xl" />
          ))}
        </KPIGrid>
      ) : data ? (
        <KPIGrid columns={4}>
          <KPICard
            title="Umsatz"
            value={data.kpis.revenue.value}
            unit="€"
            icon={<Euro className="h-5 w-5" />}
            color="primary"
            trend={{ value: data.kpis.revenue.trend, period: 'vs. Vorperiode' }}
            target={{ value: data.kpis.revenue.target, label: 'Ziel' }}
            onClick={() => navigate('/finance/umsatz')}
          />
          <KPICard
            title="Aufträge"
            value={data.kpis.orders.value}
            icon={<ShoppingCart className="h-5 w-5" />}
            trend={{ value: data.kpis.orders.trend, period: 'vs. Vorperiode' }}
            onClick={() => navigate('/sales/auftraege-liste')}
          />
          <KPICard
            title="Aktive Kunden"
            value={data.kpis.customers.value}
            icon={<Users className="h-5 w-5" />}
            color="success"
            trend={{ value: data.kpis.customers.trend }}
            tooltip={`${data.kpis.customers.newCount} Neukunden im Zeitraum`}
            onClick={() => navigate('/crm/kunden-stamm')}
          />
          <KPICard
            title="Lagerwert"
            value={data.kpis.inventory.value}
            unit="€"
            icon={<Package className="h-5 w-5" />}
            color={data.kpis.inventory.trend < 0 ? 'warning' : 'default'}
            trend={{ value: data.kpis.inventory.trend }}
            onClick={() => navigate('/lager/bestandsuebersicht')}
          />
        </KPIGrid>
      ) : null}

      {/* Charts & Alerts */}
      <div className="grid gap-6 lg:grid-cols-3">
        {/* Trends */}
        <div className="lg:col-span-2 space-y-6">
          {isLoading ? (
            <>
              <Skeleton className="h-64 rounded-xl" />
              <Skeleton className="h-64 rounded-xl" />
            </>
          ) : data ? (
            <>
              <TrendChart
                title="Umsatzentwicklung"
                data={data.revenueTrend}
                type="area"
                color="primary"
                height={200}
                showLegend
                formatValue={(v) => `${v.toLocaleString('de-DE')} €`}
              />
              <TrendChart
                title="Aufträge pro Tag"
                data={data.ordersTrend}
                type="bar"
                color="success"
                height={180}
              />
            </>
          ) : null}
        </div>

        {/* Alerts */}
        <div>
          {isLoading ? (
            <Skeleton className="h-96 rounded-xl" />
          ) : data ? (
            <AlertWidget
              title="Handlungsbedarf"
              alerts={data.alerts}
              maxItems={5}
              onViewAll={() => navigate('/alerts')}
            />
          ) : null}
        </div>
      </div>

      {/* Top Listen */}
      <div className="grid gap-6 lg:grid-cols-2">
        {/* Top Produkte */}
        <div className="bg-card rounded-xl border p-4">
          <div className="flex items-center justify-between mb-4">
            <h3 className="font-semibold">Top Produkte</h3>
            <Button variant="ghost" size="sm" onClick={() => navigate('/artikel')}>
              Alle anzeigen
            </Button>
          </div>

          {isLoading ? (
            <div className="space-y-3">
              {[1, 2, 3, 4, 5].map((i) => (
                <Skeleton key={i} className="h-12" />
              ))}
            </div>
          ) : data ? (
            <div className="space-y-2">
              {data.topProducts.map((product, index) => (
                <div
                  key={product.name}
                  className="flex items-center gap-3 p-2 rounded-lg hover:bg-muted/50 transition-colors"
                >
                  <span className="w-6 h-6 flex items-center justify-center rounded-full bg-muted text-sm font-medium">
                    {index + 1}
                  </span>
                  <div className="flex-1 min-w-0">
                    <p className="font-medium truncate">{product.name}</p>
                    <p className="text-sm text-muted-foreground">
                      {product.quantity.toLocaleString('de-DE')} Stk.
                    </p>
                  </div>
                  <span className="font-medium text-primary">
                    {product.revenue.toLocaleString('de-DE')} €
                  </span>
                </div>
              ))}
            </div>
          ) : null}
        </div>

        {/* Top Kunden */}
        <div className="bg-card rounded-xl border p-4">
          <div className="flex items-center justify-between mb-4">
            <h3 className="font-semibold">Top Kunden</h3>
            <Button variant="ghost" size="sm" onClick={() => navigate('/crm/kunden-stamm')}>
              Alle anzeigen
            </Button>
          </div>

          {isLoading ? (
            <div className="space-y-3">
              {[1, 2, 3, 4, 5].map((i) => (
                <Skeleton key={i} className="h-12" />
              ))}
            </div>
          ) : data ? (
            <div className="space-y-2">
              {data.topCustomers.map((customer, index) => (
                <div
                  key={customer.name}
                  className="flex items-center gap-3 p-2 rounded-lg hover:bg-muted/50 transition-colors cursor-pointer"
                  onClick={() => navigate(`/crm/kunden-stamm?search=${encodeURIComponent(customer.name)}`)}
                >
                  <span className="w-6 h-6 flex items-center justify-center rounded-full bg-muted text-sm font-medium">
                    {index + 1}
                  </span>
                  <div className="flex-1 min-w-0">
                    <p className="font-medium truncate">{customer.name}</p>
                    <p className="text-sm text-muted-foreground">
                      {customer.orders} Aufträge
                    </p>
                  </div>
                  <span className="font-medium text-primary">
                    {customer.revenue.toLocaleString('de-DE')} €
                  </span>
                </div>
              ))}
            </div>
          ) : null}
        </div>
      </div>
    </div>
  )
}
