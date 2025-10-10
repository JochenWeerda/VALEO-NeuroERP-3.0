import { useEffect, useState } from "react"
import { useMcpQuery } from "@/lib/mcp"

const INSIGHT_GENERATION_DELAY_MS = 1200
const MILLISECONDS_PER_KILOGRAM = 1000

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

type Insight = {
  summary: string
  factors: string[]
  suggestions: string[]
}

/**
 * Holt KPIs + Trends und erzeugt daraus (simulierte) GPT-Analysen.
 * Später kann hier dein echter LLM-Aufruf erfolgen.
 */
export function useCopilotInsight(): {
  insight: Insight | null
  loading: boolean
} {
  const { data: kpiData } = useMcpQuery<KPIResponse>("analytics", "kpis", [])
  const { data: trendData } = useMcpQuery<TrendResponse>("analytics", "trends", [])
  const [insight, setInsight] = useState<Insight | null>(null)
  const [loading, setLoading] = useState<boolean>(true)

  useEffect(() => {
    if (kpiData === undefined || trendData === undefined) {
      return
    }
    setLoading(true)

    // → hier könnte ein echter GPT-5-Request stehen
    const kpis = kpiData.data?.data ?? []
    const revenueKpi = kpis.find((k) => k.id === "revenue")
    const marginKpi = kpis.find((k) => k.id === "margin")

    const revenue = revenueKpi?.value ?? 0
    const delta = revenueKpi?.delta ?? 0
    const margin = marginKpi?.value ?? 0

    const trendDataArray = trendData.data?.data ?? []
    const avgStock =
      trendDataArray.length > 0
        ? trendDataArray.reduce((acc, point) => acc + point.inventory, 0) /
          trendDataArray.length
        : 0

    const timer = setTimeout((): void => {
      const isGrowing = delta >= 0
      const trendDirection = isGrowing ? "steigend" : "fallend"
      const avgStockInTons = (avgStock / MILLISECONDS_PER_KILOGRAM).toFixed(1)

      setInsight({
        summary: `Der Umsatz liegt aktuell bei ${revenue.toLocaleString(
          "de-DE"
        )} €, ${trendDirection} um ${Math.abs(delta).toFixed(
          1
        )} %. Die durchschnittliche Lagerreichweite beträgt ca. ${avgStockInTons} t mit einer Marge von ${margin.toFixed(
          1
        )} %.`,
        factors: [
          isGrowing
            ? "Starke Nachfrage nach Milchpulversegment"
            : "Rückgang bei Düngemittelpreisen",
          "Steigende Logistikkosten",
          "Gute Zahlungsmoral der Kunden",
        ],
        suggestions: [
          "Lageroptimierung: Prüfe Putaway-Zyklen für Top-Seller",
          "Preisanpassung bei stabiler Nachfrage > 5 %",
          "Automatische Nachdisposition aktivieren",
        ],
      })
      setLoading(false)
    }, INSIGHT_GENERATION_DELAY_MS)

    return () => {
      clearTimeout(timer)
    }
  }, [kpiData, trendData])

  return { insight, loading }
}
