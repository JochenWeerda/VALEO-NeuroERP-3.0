import { motion } from "framer-motion"
import {
  Bar,
  BarChart,
  CartesianGrid,
  Line,
  LineChart,
  Pie,
  PieChart,
  ResponsiveContainer,
  Tooltip,
  XAxis,
  YAxis,
  Cell,
} from "recharts"
import { Card } from "@/components/ui/card"
import { Button } from "@/components/ui/button"
import { useMcpQuery } from "@/lib/mcp"
import { useToast } from "@/components/ui/toast-provider"
import { Toolbar } from "@/components/ui/toolbar"
import { Download, BarChart3, TrendingUp, Users, Package, Euro } from "lucide-react"
import { useState } from "react"

// const ANIMATION_DURATION = 0.3
const CHART_HEIGHT = 300

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
  { id: 'sales-performance' as ReportType, label: 'Verkaufs\u00ADperformance', icon: BarChart3, color: '#10B981' },
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

  const { data: reportData, isLoading } = useMcpQuery<ReportData>(
    "reports",
    selectedReport,
    [startDate, endDate]
  )

  const handleExport = async (format: 'json' | 'csv' = 'json') => {
    try {
      const response = await fetch(`/api/reports/export/${selectedReport}?format=${format}&start_date=${startDate}&end_date=${endDate}`)
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
      push("✅ Bericht exportiert")
    } catch (error) {
      push("❌ Export fehlgeschlagen")
    }
  }

  const renderChart = () => {
    if (!reportData?.data) return null

    const data = reportData.data

    switch (selectedReport) {
      case 'sales-performance':
        return (
          <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
            <Card className="p-4">
              <h4 className="font-semibold mb-2">Umsatz nach Status</h4>
              <ResponsiveContainer width="100%" height={CHART_HEIGHT}>
                <BarChart data={[
                  { name: 'Bezahlt', value: data?.totalRevenue ?? 0 },
                  { name: 'Ausstehend', value: (data?.totalRevenue ?? 0) * 0.2 }, // Mock data
                ]}>
                  <CartesianGrid strokeDasharray="3 3" />
                  <XAxis dataKey="name" />
                  <YAxis />
                  <Tooltip formatter={(value) => [`${value.toLocaleString('de-DE')} €`, 'Umsatz']} />
                  <Bar dataKey="value" fill="#10B981" />
                </BarChart>
              </ResponsiveContainer>
            </Card>
            <Card className="p-4">
              <h4 className="font-semibold mb-2">Konversionsraten</h4>
              <ResponsiveContainer width="100%" height={CHART_HEIGHT}>
                <PieChart>
                  <Pie
                    data={[
                      { name: 'Anfrage → Angebot', value: data?.conversionRates?.inquiryToOffer ?? 0 },
                      { name: 'Angebot → Auftrag', value: data?.conversionRates?.offerToOrder ?? 0 },
                      { name: 'Auftrag → Rechnung', value: data?.conversionRates?.orderToInvoice ?? 0 },
                    ]}
                    cx="50%"
                    cy="50%"
                    outerRadius={80}
                    dataKey="value"
                    label={({ name, value }) => `${name}: ${(value ?? 0).toFixed(1)}%`}
                  >
                    {[
                      { name: 'Anfrage → Angebot', value: data?.conversionRates?.inquiryToOffer ?? 0 },
                      { name: 'Angebot → Auftrag', value: data?.conversionRates?.offerToOrder ?? 0 },
                      { name: 'Auftrag → Rechnung', value: data?.conversionRates?.orderToInvoice ?? 0 },
                    ].map((_entry, index) => (
                      <Cell key={`cell-${index}`} fill={['#10B981', '#3B82F6', '#8B5CF6'][index % 3]} />
                    ))}
                  </Pie>
                  <Tooltip />
                </PieChart>
              </ResponsiveContainer>
            </Card>
          </div>
        )

      case 'customer-analytics':
        return (
          <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
            <Card className="p-4">
              <h4 className="font-semibold mb-2">Top Kunden nach Umsatz</h4>
              <ResponsiveContainer width="100%" height={CHART_HEIGHT}>
                <BarChart data={(data?.topCustomers ?? []).slice(0, 5)} layout="horizontal">
                  <CartesianGrid strokeDasharray="3 3" />
                  <XAxis type="number" />
                  <YAxis dataKey="customerId" type="category" width={80} />
                  <Tooltip formatter={(value) => [`${value.toLocaleString('de-DE')} €`, 'Umsatz']} />
                  <Bar dataKey="totalRevenue" fill="#3B82F6" />
                </BarChart>
              </ResponsiveContainer>
            </Card>
            <Card className="p-4">
              <h4 className="font-semibold mb-2">Kundenakquise-Trends</h4>
              <ResponsiveContainer width="100%" height={CHART_HEIGHT}>
                <LineChart data={Object.entries(data?.customerAcquisitionTrends ?? {}).map(([month, count]) => ({ month, count }))}>
                  <CartesianGrid strokeDasharray="3 3" />
                  <XAxis dataKey="month" />
                  <YAxis />
                  <Tooltip />
                  <Line type="monotone" dataKey="count" stroke="#3B82F6" strokeWidth={2} />
                </LineChart>
              </ResponsiveContainer>
            </Card>
          </div>
        )

      case 'product-analytics':
        return (
          <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
            <Card className="p-4">
              <h4 className="font-semibold mb-2">Top Produkte nach Umsatz</h4>
              <ResponsiveContainer width="100%" height={CHART_HEIGHT}>
                <BarChart data={(data?.topProductsByRevenue ?? []).slice(0, 5)}>
                  <CartesianGrid strokeDasharray="3 3" />
                  <XAxis dataKey="article" angle={-45} textAnchor="end" height={80} />
                  <YAxis />
                  <Tooltip formatter={(value) => [`${value.toLocaleString('de-DE')} €`, 'Umsatz']} />
                  <Bar dataKey="revenue" fill="#8B5CF6" />
                </BarChart>
              </ResponsiveContainer>
            </Card>
            <Card className="p-4">
              <h4 className="font-semibold mb-2">Top Produkte nach Menge</h4>
              <ResponsiveContainer width="100%" height={CHART_HEIGHT}>
                <BarChart data={(data?.topProductsByQuantity ?? []).slice(0, 5)}>
                  <CartesianGrid strokeDasharray="3 3" />
                  <XAxis dataKey="article" angle={-45} textAnchor="end" height={80} />
                  <YAxis />
                  <Tooltip formatter={(value) => [`${value.toLocaleString('de-DE')} kg`, 'Menge']} />
                  <Bar dataKey="quantity" fill="#8B5CF6" />
                </BarChart>
              </ResponsiveContainer>
            </Card>
          </div>
        )

      case 'financial-analytics':
        return (
          <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
            <Card className="p-4">
              <h4 className="font-semibold mb-2">Umsatzübersicht</h4>
              <ResponsiveContainer width="100%" height={CHART_HEIGHT}>
                <BarChart data={[
                  { name: 'Gesamt', value: data.revenue.total },
                  { name: 'Bezahlt', value: data.revenue.paid },
                  { name: 'Ausstehend', value: data.revenue.outstanding },
                ]}>
                  <CartesianGrid strokeDasharray="3 3" />
                  <XAxis dataKey="name" />
                  <YAxis />
                  <Tooltip formatter={(value) => [`${value.toLocaleString('de-DE')} €`, 'Betrag']} />
                  <Bar dataKey="value" fill="#F59E0B" />
                </BarChart>
              </ResponsiveContainer>
            </Card>
            <Card className="p-4">
              <h4 className="font-semibold mb-2">Ausstehende Zahlungen</h4>
              <ResponsiveContainer width="100%" height={CHART_HEIGHT}>
                <BarChart data={[
                  { name: 'Aktuell', value: data.outstandingPayments.current },
                  { name: '30 Tage', value: data.outstandingPayments.overdue30Days },
                  { name: '60 Tage', value: data.outstandingPayments.overdue60Days },
                  { name: '90+ Tage', value: data.outstandingPayments.overdue90Days },
                ]}>
                  <CartesianGrid strokeDasharray="3 3" />
                  <XAxis dataKey="name" />
                  <YAxis />
                  <Tooltip formatter={(value) => [`${value.toLocaleString('de-DE')} €`, 'Ausstehend']} />
                  <Bar dataKey="value" fill="#EF4444" />
                </BarChart>
              </ResponsiveContainer>
            </Card>
          </div>
        )

      case 'trend-analytics':
        return (
          <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
            <Card className="p-4">
              <h4 className="font-semibold mb-2">Umsatztrend</h4>
              <ResponsiveContainer width="100%" height={CHART_HEIGHT}>
                <LineChart data={Object.entries(data?.revenueTrends ?? {}).map(([period, value]) => ({ period, value }))}>
                  <CartesianGrid strokeDasharray="3 3" />
                  <XAxis dataKey="period" />
                  <YAxis />
                  <Tooltip formatter={(value) => [`${value.toLocaleString('de-DE')} €`, 'Umsatz']} />
                  <Line type="monotone" dataKey="value" stroke="#EF4444" strokeWidth={2} />
                </LineChart>
              </ResponsiveContainer>
            </Card>
            <Card className="p-4">
              <h4 className="font-semibold mb-2">Auftragsvolumen</h4>
              <ResponsiveContainer width="100%" height={CHART_HEIGHT}>
                <LineChart data={Object.entries(data?.orderVolumeTrends ?? {}).map(([period, value]) => ({ period, value }))}>
                  <CartesianGrid strokeDasharray="3 3" />
                  <XAxis dataKey="period" />
                  <YAxis />
                  <Tooltip formatter={(value) => [`${String(value)}`, 'Aufträge']} />
                  <Line type="monotone" dataKey="value" stroke="#EF4444" strokeWidth={2} />
                </LineChart>
              </ResponsiveContainer>
            </Card>
          </div>
        )

      default:
        return null
    }
  }

  return (
    <div className="space-y-6">
      <div className="flex items-center justify-between">
        <h2 className="text-2xl font-bold">Berichte & Analytics</h2>
        <div className="flex gap-2">
          <Button variant="outline" size="sm" onClick={() => handleExport('json')}>
            <Download className="h-4 w-4 mr-2" />
            JSON Export
          </Button>
          <Button variant="outline" size="sm" onClick={() => handleExport('csv')}>
            <Download className="h-4 w-4 mr-2" />
            CSV Export
          </Button>
        </div>
      </div>

      <Toolbar onSearch={() => {}} onCopilot={() => push("🤖 KI-Analyse gestartet")} />

      {/* Report Type Selection */}
      <div className="grid grid-cols-2 md:grid-cols-5 gap-4">
        {REPORT_TYPES.map((report) => {
          const Icon = report.icon
          return (
            <motion.button
              key={report.id}
              onClick={() => setSelectedReport(report.id)}
              className={`p-4 rounded-lg border-2 transition-all ${
                selectedReport === report.id
                  ? 'border-primary bg-primary/10'
                  : 'border-border hover:border-primary/50'
              }`}
              whileHover={{ scale: 1.02 }}
              whileTap={{ scale: 0.98 }}
            >
              <Icon className="h-8 w-8 mx-auto mb-2" style={{ color: report.color }} />
              <div className="text-sm font-medium">{report.label}</div>
            </motion.button>
          )
        })}
      </div>

      {/* Date Filters */}
      <Card className="p-4">
        <div className="flex gap-4 items-center">
          <div>
            <label className="block text-sm font-medium mb-1">Von Datum</label>
            <input
              type="date"
              value={startDate}
              onChange={(e) => setStartDate(e.target.value)}
              className="px-3 py-2 border rounded-md"
            />
          </div>
          <div>
            <label className="block text-sm font-medium mb-1">Bis Datum</label>
            <input
              type="date"
              value={endDate}
              onChange={(e) => setEndDate(e.target.value)}
              className="px-3 py-2 border rounded-md"
            />
          </div>
          <Button
            onClick={() => {
              // Trigger re-fetch by updating state
              setStartDate(startDate)
              setEndDate(endDate)
            }}
            className="mt-6"
          >
            Aktualisieren
          </Button>
        </div>
      </Card>

      {/* Report Content */}
      {isLoading ? (
        <div className="flex items-center justify-center h-64">
          <div className="text-lg">Bericht wird geladen...</div>
        </div>
      ) : (
        <>
          {/* Key Metrics */}
          <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
            {reportData?.data && (
              <>
                {selectedReport === 'sales-performance' && (
                  <>
                    <Card className="p-4">
                      <div className="text-sm opacity-70">Gesamtumsatz</div>
                      <div className="text-2xl font-bold">{reportData.data.totalRevenue?.toLocaleString('de-DE')} €</div>
                    </Card>
                    <Card className="p-4">
                      <div className="text-sm opacity-70">Aufträge</div>
                      <div className="text-2xl font-bold">{reportData.data.totalOrders}</div>
                    </Card>
                    <Card className="p-4">
                      <div className="text-sm opacity-70">Ø Auftragswert</div>
                      <div className="text-2xl font-bold">{reportData.data.averageOrderValue?.toLocaleString('de-DE')} €</div>
                    </Card>
                    <Card className="p-4">
                      <div className="text-sm opacity-70">Konversionsrate</div>
                      <div className="text-2xl font-bold">{reportData.data.conversionRates?.offerToOrder?.toFixed(1)} %</div>
                    </Card>
                  </>
                )}
                {selectedReport === 'customer-analytics' && (
                  <>
                    <Card className="p-4">
                      <div className="text-sm opacity-70">Kunden</div>
                      <div className="text-2xl font-bold">{reportData.data.totalUniqueCustomers}</div>
                    </Card>
                    <Card className="p-4">
                      <div className="text-sm opacity-70">Top Kunde Umsatz</div>
                      <div className="text-2xl font-bold">{reportData.data.topCustomers?.[0]?.totalRevenue?.toLocaleString('de-DE')} €</div>
                    </Card>
                  </>
                )}
                {selectedReport === 'product-analytics' && (
                  <>
                    <Card className="p-4">
                      <div className="text-sm opacity-70">Produkte</div>
                      <div className="text-2xl font-bold">{reportData.data.totalUniqueProducts}</div>
                    </Card>
                    <Card className="p-4">
                      <div className="text-sm opacity-70">Top Produkt Umsatz</div>
                      <div className="text-2xl font-bold">{reportData.data.topProductsByRevenue?.[0]?.revenue?.toLocaleString('de-DE')} €</div>
                    </Card>
                  </>
                )}
                {selectedReport === 'financial-analytics' && (
                  <>
                    <Card className="p-4">
                      <div className="text-sm opacity-70">Gesamtumsatz</div>
                      <div className="text-2xl font-bold">{reportData.data.revenue?.total?.toLocaleString('de-DE')} €</div>
                    </Card>
                    <Card className="p-4">
                      <div className="text-sm opacity-70">Ausstehend</div>
                      <div className="text-2xl font-bold">{reportData.data.revenue?.outstanding?.toLocaleString('de-DE')} €</div>
                    </Card>
                  </>
                )}
              </>
            )}
          </div>

          {/* Charts */}
          {renderChart()}
        </>
      )}
    </div>
  )
}