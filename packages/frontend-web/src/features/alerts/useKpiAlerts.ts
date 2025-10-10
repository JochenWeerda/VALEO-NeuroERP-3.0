import { useMemo } from "react"
import { useMcpQuery } from "@/lib/mcp"
import { type Alert, type HeatCell, type KPI, type TrendPoint, computeScores } from "./rules"

type KPIResponse = {
  data: KPI[]
}

type TrendResponse = {
  data: TrendPoint[]
}

/**
 * Custom Hook für KPI-Alerts und Heatmap-Daten
 * Berechnet Scores und Alerts aus KPIs und Trends
 */
export function useKpiAlerts(): {
  cells: HeatCell[]
  alerts: Alert[]
} {
  const { data: kpiRes } = useMcpQuery<KPIResponse>("analytics", "kpis", [])
  const { data: trendRes } = useMcpQuery<TrendResponse>("analytics", "trends", [])

  return useMemo(() => {
    const kpis = kpiRes?.data?.data ?? []
    const trends = trendRes?.data?.data ?? []
    return computeScores(kpis, trends)
  }, [kpiRes, trendRes])
}
