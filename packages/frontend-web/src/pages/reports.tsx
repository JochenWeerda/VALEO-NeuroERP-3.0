import { Suspense, lazy, useState } from 'react'
import { Card } from '@/components/ui/card'
import { Button } from '@/components/ui/button'
import { useMcpQuery } from '@/lib/mcp'
import { useToast } from '@/components/ui/toast-provider'
import { Toolbar } from '@/components/ui/toolbar'
import { Download, BarChart3, TrendingUp, Users, Package, Euro } from 'lucide-react'
import { apiClient } from '@/lib/api-client'
import type { ReportDashboardData } from '@/pages/reports/report-chart-types'

const ReportsDashboardCharts = lazy(() =>
  import('@/pages/reports/ReportsDashboardCharts').then((module) => ({ default: module.default })),
)

type ReportType = 'sales-performance' | 'customer-analytics' | 'product-analytics' | 'financial-analytics' | 'trend-analytics'

interface ReportData {
  data: ReportDashboardData & {
    totalOrders?: number
    averageOrderValue?: number
    totalUniqueCustomers?: number
    totalUniqueProducts?: number
  }
  metadata?: {
    reportType: string
    generatedAt: string
    dataPoints: number
  }
  totalRevenue?: number
  totalOrders?: number
  averageOrderValue?: number
  totalUniqueCustomers?: number
  totalUniqueProducts?: number
}

const REPORT_TYPES = [
  { id: 'sales-performance' as ReportType, label: 'Verkaufsperformance', icon: BarChart3, color: '#10B981' },
  { id: 'customer-analytics' as ReportType, label: 'Kundenanalyse', icon: Users, color: '#3B82F6' },
  { id: 'product-analytics' as ReportType, label: 'Produktanalyse', icon: Package, color: '#8B5CF6' },
  { id: 'financial-analytics' as ReportType, label: 'Finanzanalyse', icon: Euro, color: '#F59E0B' },
  { id: 'trend-analytics' as ReportType, label: 'Trendanalyse', icon: TrendingUp, color: '#EF4444' },
]

export default function ReportsDashboard(): JSX.Element {
  const [selectedReport, setSelectedReport] = useState<ReportType>('sales-performance')
  const [startDate, setStartDate] = useState('')
  const [endDate, setEndDate] = useState('')
  const { push } = useToast()

  const { data: reportData, isLoading } = useMcpQuery<ReportData>('reports', selectedReport, [startDate, endDate])
  const reportPayload = reportData?.data?.data

  const handleExport = async (format: 'json' | 'csv' = 'json') => {
    try {
      const params = new URLSearchParams({ format, start_date: startDate, end_date: endDate })
      const res = await apiClient.get(
        `/api/v1/reports/export/${selectedReport}?${params.toString()}`,
        { responseType: format === 'csv' ? 'blob' : 'json' },
      )
      if (format === 'csv') {
        const url = window.URL.createObjectURL(res.data as Blob)
        const a = document.createElement('a')
        a.href = url
        a.download = `${selectedReport}_report.csv`
        a.click()
        window.URL.revokeObjectURL(url)
      } else {
        const blob = new Blob([JSON.stringify(res.data, null, 2)], { type: 'application/json' })
        const url = window.URL.createObjectURL(blob)
        const a = document.createElement('a')
        a.href = url
        a.download = `${selectedReport}_report.json`
        a.click()
        window.URL.revokeObjectURL(url)
      }
      push('Bericht exportiert')
    } catch {
      push('Export fehlgeschlagen')
    }
  }

  return (
    <div className="space-y-6">
      <div className="flex items-center justify-between">
        <h2 className="text-2xl font-bold">Berichte und Analytics</h2>
        <div className="flex gap-2">
          <Button variant="outline" size="sm" onClick={() => handleExport('json')}>
            <Download className="mr-2 h-4 w-4" />
            JSON Export
          </Button>
          <Button variant="outline" size="sm" onClick={() => handleExport('csv')}>
            <Download className="mr-2 h-4 w-4" />
            CSV Export
          </Button>
        </div>
      </div>

      <Toolbar onSearch={() => undefined} onCopilot={() => push('KI-Analyse gestartet')} />

      <div className="grid grid-cols-2 gap-4 md:grid-cols-5">
        {REPORT_TYPES.map((report) => {
          const Icon = report.icon
          return (
            <button
              key={report.id}
              onClick={() => setSelectedReport(report.id)}
              className={`rounded-lg border-2 p-4 transition-all ${
                selectedReport === report.id ? 'border-primary bg-primary/10' : 'border-border hover:border-primary/50'
              }`}
            >
              <Icon className="mx-auto mb-2 h-8 w-8" style={{ color: report.color }} />
              <div className="text-sm font-medium">{report.label}</div>
            </button>
          )
        })}
      </div>

      <Card className="p-4">
        <div className="flex items-center gap-4">
          <div>
            <label className="mb-1 block text-sm font-medium">Von Datum</label>
            <input type="date" value={startDate} onChange={(e) => setStartDate(e.target.value)} className="rounded-md border px-3 py-2" />
          </div>
          <div>
            <label className="mb-1 block text-sm font-medium">Bis Datum</label>
            <input type="date" value={endDate} onChange={(e) => setEndDate(e.target.value)} className="rounded-md border px-3 py-2" />
          </div>
          <Button onClick={() => undefined} className="mt-6">Aktualisieren</Button>
        </div>
      </Card>

      {isLoading ? (
        <div className="flex h-64 items-center justify-center">
          <div className="text-lg">Bericht wird geladen...</div>
        </div>
      ) : (
        <>
          <div className="grid grid-cols-2 gap-4 md:grid-cols-4">
            {reportPayload && (
              <>
                {selectedReport === 'sales-performance' && (
                  <>
                    <Card className="p-4"><div className="text-sm opacity-70">Gesamtumsatz</div><div className="text-2xl font-bold">{reportPayload.totalRevenue?.toLocaleString('de-DE')} EUR</div></Card>
                    <Card className="p-4"><div className="text-sm opacity-70">Auftraege</div><div className="text-2xl font-bold">{reportPayload.totalOrders}</div></Card>
                    <Card className="p-4"><div className="text-sm opacity-70">Durchschnitt Auftragswert</div><div className="text-2xl font-bold">{reportPayload.averageOrderValue?.toLocaleString('de-DE')} EUR</div></Card>
                    <Card className="p-4"><div className="text-sm opacity-70">Konversionsrate</div><div className="text-2xl font-bold">{reportPayload.conversionRates?.offerToOrder?.toFixed(1)} %</div></Card>
                  </>
                )}
                {selectedReport === 'customer-analytics' && (
                  <>
                    <Card className="p-4"><div className="text-sm opacity-70">Kunden</div><div className="text-2xl font-bold">{reportPayload.totalUniqueCustomers}</div></Card>
                    <Card className="p-4"><div className="text-sm opacity-70">Top Kunde Umsatz</div><div className="text-2xl font-bold">{reportPayload.topCustomers?.[0]?.totalRevenue?.toLocaleString('de-DE')} EUR</div></Card>
                  </>
                )}
                {selectedReport === 'product-analytics' && (
                  <>
                    <Card className="p-4"><div className="text-sm opacity-70">Produkte</div><div className="text-2xl font-bold">{reportPayload.totalUniqueProducts}</div></Card>
                    <Card className="p-4"><div className="text-sm opacity-70">Top Produkt Umsatz</div><div className="text-2xl font-bold">{reportPayload.topProductsByRevenue?.[0]?.revenue?.toLocaleString('de-DE')} EUR</div></Card>
                  </>
                )}
                {selectedReport === 'financial-analytics' && (
                  <>
                    <Card className="p-4"><div className="text-sm opacity-70">Gesamtumsatz</div><div className="text-2xl font-bold">{reportPayload.revenue?.total?.toLocaleString('de-DE')} EUR</div></Card>
                    <Card className="p-4"><div className="text-sm opacity-70">Ausstehend</div><div className="text-2xl font-bold">{reportPayload.revenue?.outstanding?.toLocaleString('de-DE')} EUR</div></Card>
                  </>
                )}
              </>
            )}
          </div>

          {reportPayload ? (
            <Suspense fallback={<div className="grid grid-cols-1 gap-4 md:grid-cols-2"><Card className="h-[332px] animate-pulse" /><Card className="h-[332px] animate-pulse" /></div>}>
              <ReportsDashboardCharts selectedReport={selectedReport} data={reportPayload} />
            </Suspense>
          ) : null}
        </>
      )}
    </div>
  )
}
