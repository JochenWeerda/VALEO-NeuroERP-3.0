import { useEffect, useState } from "react"
import { useMcpQuery } from "@/lib/mcp"

type TrendPoint = {
  date: string
  sales: number
  inventory: number
}

type TrendResponse = {
  data: TrendPoint[]
}

type ForecastData = {
  sales: number
  anomaly: boolean
}

type Forecast = {
  forecast: ForecastData
  summary: string
  factors: string[]
}

type ForecastResponse = {
  ok?: boolean
  data?: Forecast
  error?: string
}

/**
 * Custom Hook für Umsatz-Prognosen und Anomalie-Erkennung
 * Lädt Trenddaten und berechnet Forecasts via Backend
 */
export function useForecast(): {
  result: Forecast | null
  loading: boolean
} {
  const { data: trendData } = useMcpQuery<TrendResponse>("analytics", "trends", [])
  const [result, setResult] = useState<Forecast | null>(null)
  const [loading, setLoading] = useState<boolean>(false)

  useEffect(() => {
    if (trendData?.data === undefined) {
      return
    }

    setLoading(true)

    fetch("/api/mcp/copilot/forecast", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ trends: trendData.data }),
    })
      .then((response) => response.json())
      .then((json: ForecastResponse) => {
        if (json.ok === true && json.data !== undefined) {
          setResult(json.data)
        }
      })
      .catch(() => {
        // Silent fail - forecast is optional
        setResult(null)
      })
      .finally(() => {
        setLoading(false)
      })
  }, [trendData])

  return { result, loading }
}
