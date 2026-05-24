import { Suspense, lazy, useState } from 'react'
import { Card } from '@/components/ui/card'
import { Button } from '@/components/ui/button'
import { useMcpQuery } from '@/lib/mcp'
import { useToast } from '@/components/ui/toast-provider'
import { Toolbar } from '@/components/ui/toolbar'
import { Download, BarChart3, TrendingUp, Users, Package, Euro } from 'lucide-react'

const ReportsDashboardCharts = lazy(() =>
  import('@/pages/reports/ReportsDashboardCharts').then((module) => ({ default: module.default })),
)

type ReportType = 'sales-performance' | 'customer-analytics' | 'product-analytics' | 'financial-analytics' | 'trend-analytics'

interface ReportData {
  data: any
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
  conversionRates?: any
  topCustomers?: any[]
  topProductsByRevenue?: any[]
  topProductsByQuantity?: any[]
  customerAcquisitionTrends?: any[]
  revenue?: any
  outstandingPayments?: any
  revenueTrends?: any[]
  orderVolumeTrends?: any[]
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

  const handleExport = async (format: 'json' | 'csv' = 'json') => {
    try {
      const response = await fetch(`/api/v1/reports/export/${selectedReport}?format=${format}&start_date=${startDate}&end_date=${endDate}`)
      if (format === 'csv') {
        const blob = await response.blob()
        const url = window.URL.createObjectURL(blob)
        const a = document.createElement('a')
        a.href = url
        a.download = `${selectedReport}_report.csv`
        a.click()
        window.URL.revokeObjectURL(url)
      } else {
        const data = await response.json()
        const blob = new Blob([JSON.stringify(data, null, 2)], { type: 'application/json' })
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
            {reportData?.data && (
              <>
                {selectedReport === 'sales-performance' && (
                  <>
                    <Card className="p-4"><div className="text-sm opacity-70">Gesamtumsatz</div><div className="text-2xl font-bold">{reportData.data.totalRevenue?.toLocaleString('de-DE')} EUR</div></Card>
                    <Card className="p-4"><div className="text-sm opacity-70">Auftraege</div><div className="text-2xl font-bold">{reportData.data.totalOrders}</div></Card>
                    <Card className="p-4"><div className="text-sm opacity-70">Durchschnitt Auftragswert</div><div className="text-2xl font-bold">{reportData.data.averageOrderValue?.toLocaleString('de-DE')} EUR</div></Card>
                    <Card className="p-4"><div className="text-sm opacity-70">Konversionsrate</div><div className="text-2xl font-bold">{reportData.data.conversionRates?.offerToOrder?.toFixed(1)} %</div></Card>
                  </>
                )}
                {selectedReport === 'customer-analytics' && (
                  <>
                    <Card className="p-4"><div className="text-sm opacity-70">Kunden</div><div className="text-2xl font-bold">{reportData.data.totalUniqueCustomers}</div></Card>
                    <Card className="p-4"><div className="text-sm opacity-70">Top Kunde Umsatz</div><div className="text-2xl font-bold">{reportData.data.topCustomers?.[0]?.totalRevenue?.toLocaleString('de-DE')} EUR</div></Card>
                  </>
                )}
                {selectedReport === 'product-analytics' && (
                  <>
                    <Card className="p-4"><div className="text-sm opacity-70">Produkte</div><div className="text-2xl font-bold">{reportData.data.totalUniqueProducts}</div></Card>
                    <Card className="p-4"><div className="text-sm opacity-70">Top Produkt Umsatz</div><div className="text-2xl font-bold">{reportData.data.topProductsByRevenue?.[0]?.revenue?.toLocaleString('de-DE')} EUR</div></Card>
                  </>
                )}
                {selectedReport === 'financial-analytics' && (
                  <>
                    <Card className="p-4"><div className="text-sm opacity-70">Gesamtumsatz</div><div className="text-2xl font-bold">{reportData.data.revenue?.total?.toLocaleString('de-DE')} EUR</div></Card>
                    <Card className="p-4"><div className="text-sm opacity-70">Ausstehend</div><div className="text-2xl font-bold">{reportData.data.revenue?.outstanding?.toLocaleString('de-DE')} EUR</div></Card>
                  </>
                )}
              </>
            )}
          </div>

          {reportData?.data ? (
            <Suspense fallback={<div className="grid grid-cols-1 gap-4 md:grid-cols-2"><Card className="h-[332px] animate-pulse" /><Card className="h-[332px] animate-pulse" /></div>}>
              <ReportsDashboardCharts selectedReport={selectedReport} data={reportData.data} />
            </Suspense>
          ) : null}
        </>
      )}
    </div>
  )
}
