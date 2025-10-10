import * as React from "react"
import { motion } from "framer-motion"
import {
  Bar,
  BarChart,
  CartesianGrid,
  Line,
  LineChart,
  ResponsiveContainer,
  Tooltip,
  XAxis,
  YAxis,
} from "recharts"
import { Card } from "@/components/ui/card"
import { useMcpQuery } from "@/lib/mcp"
import { useMcpRealtime } from "@/lib/useMcpRealtime"
import { useToast } from "@/components/ui/toast-provider"
import { Toolbar } from "@/components/ui/toolbar"
import { CopilotInsights } from "@/features/copilot/CopilotInsights"
import { useForecast } from "@/features/analytics/useForecast"
import { useKpiAlerts } from "@/features/alerts/useKpiAlerts"
import { KpiHeatmap } from "@/features/alerts/KpiHeatmap"
import { AlertBanner, AlertList } from "@/features/alerts/AlertBanner"

const ANIMATION_DURATION = 0.3
const CHART_HEIGHT = 250
const DECIMAL_PLACES = 1

type KPI = {
  id: string
  label: string
  value: number
  delta: number
  unit?: string
}

type TrendPoint = {
  date: string
  sales: number
  inventory: number
}

type KPIResponse = {
  data: KPI[]
}

type TrendResponse = {
  data: TrendPoint[]
}

export default function AnalyticsDashboard(): JSX.Element {
  const { data: kpiData } = useMcpQuery<KPIResponse>("analytics", "kpis", [])
  const { data: trendData } = useMcpQuery<TrendResponse>("analytics", "trends", [])
  const { push } = useToast()
  const { result: forecast, loading: loadingForecast } = useForecast()
  const { cells, alerts } = useKpiAlerts()

  useMcpRealtime("analytics", (evt) => {
    if (evt.type === "updated") {
      push("📊 Analytics aktualisiert")
    }
    if (evt.type === "forecast-updated") {
      push("🔮 Prognose aktualisiert")
    }
  })

  const kpis = kpiData?.data?.data ?? []
  const trends = trendData?.data?.data ?? []

  const handleSearch = (_value: string): void => {
    // Search functionality to be implemented
  }

  const handleCopilot = (): void => {
    push("🤖 KI-Analyse aktualisiert")
  }

  return (
    <div className="space-y-6">
      <h2 className="text-2xl font-bold">Dashboard</h2>
      <Toolbar onSearch={handleSearch} onCopilot={handleCopilot} />

      {/* KPI Cards */}
      <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
        {kpis.map((k): JSX.Element => (
          <motion.div
            key={k.id}
            initial={{ opacity: 0, y: 10 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ duration: ANIMATION_DURATION }}
          >
            <Card className="p-4 shadow-md bg-gradient-to-br from-emerald-50 to-white">
              <div className="text-sm opacity-70">{k.label}</div>
              <div className="text-2xl font-bold">
                {k.value.toLocaleString("de-DE")}
                {k.unit ?? ""}
              </div>
              <div
                className={`text-sm ${
                  k.delta >= 0 ? "text-green-600" : "text-red-600"
                }`}
              >
                {k.delta >= 0 ? "▲" : "▼"} {Math.abs(k.delta).toFixed(DECIMAL_PLACES)} %
              </div>
            </Card>
          </motion.div>
        ))}
      </div>

      {/* Charts */}
      <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
        <Card className="p-4">
          <h4 className="font-semibold mb-2">Umsatztrend</h4>
          <ResponsiveContainer width="100%" height={CHART_HEIGHT}>
            <LineChart data={trends}>
              <CartesianGrid strokeDasharray="3 3" />
              <XAxis dataKey="date" />
              <YAxis />
              <Tooltip />
              <Line
                type="monotone"
                dataKey="sales"
                stroke="#10B981"
                strokeWidth={2}
              />
            </LineChart>
          </ResponsiveContainer>
        </Card>

        <Card className="p-4">
          <h4 className="font-semibold mb-2">Lagerbestand</h4>
          <ResponsiveContainer width="100%" height={CHART_HEIGHT}>
            <BarChart data={trends}>
              <CartesianGrid strokeDasharray="3 3" />
              <XAxis dataKey="date" />
              <YAxis />
              <Tooltip />
              <Bar dataKey="inventory" fill="#047857" />
            </BarChart>
          </ResponsiveContainer>
        </Card>
      </div>

      {/* KPI Heatmap */}
      <Card className="p-4">
        <h4 className="font-semibold mb-2">KPI Heatmap</h4>
        <KpiHeatmap cells={cells} />
      </Card>

      {/* Alerts with Actions */}
      <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
        <AlertBanner items={alerts} />
        <Card className="p-4 md:col-span-2">
          <h4 className="font-semibold mb-2">Alerts</h4>
          <AlertList items={alerts} />
        </Card>
      </div>

      {/* Copilot Insights 2.0 */}
      <CopilotInsights />

      {/* Predictive Forecast & Anomaly Detection */}
      {loadingForecast && (
        <p className="text-sm opacity-70">Berechne Prognose …</p>
      )}
      {forecast !== null && (
        <motion.div
          className={`border rounded-xl p-4 shadow ${
            forecast.forecast.anomaly
              ? "bg-red-50 border-red-300"
              : "bg-emerald-50 border-emerald-300"
          }`}
          initial={{ opacity: 0 }}
          animate={{ opacity: 1 }}
        >
          <div className="font-semibold flex items-center gap-2">
            <span>🔮 Prognose</span>
            {forecast.forecast.anomaly && (
              <span className="text-red-600 text-xs">⚠️ ANOMALIE</span>
            )}
          </div>
          <p className="text-sm mt-1">{forecast.summary}</p>
          {forecast.factors.length > 0 && (
            <ul className="list-disc list-inside text-sm mt-2">
              {forecast.factors.map((factor, index): JSX.Element => (
                <li key={index}>{factor}</li>
              ))}
            </ul>
          )}
        </motion.div>
      )}
    </div>
  )
} 