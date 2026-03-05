import { useEffect, useState } from "react"
import { buildMcpHeaders, useMcpQuery } from "@/lib/mcp"

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

function isValidForecast(data: unknown): data is Forecast {
  if (typeof data !== "object" || data === null) {
    return false
  }
  const candidate = data as {
    forecast?: { sales?: unknown; anomaly?: unknown } | null
    summary?: unknown
    factors?: unknown
  }
  return (
    candidate.forecast !== null &&
    candidate.forecast !== undefined &&
    typeof candidate.forecast.sales === "number" &&
    typeof candidate.forecast.anomaly === "boolean" &&
    typeof candidate.summary === "string" &&
    Array.isArray(candidate.factors)
  )
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

    const apiBaseUrl = import.meta.env.VITE_API_BASE_URL || import.meta.env.VITE_API_URL || ''

    fetch(`${apiBaseUrl}/api/mcp/copilot/forecast`, {
      method: "POST",
      headers: buildMcpHeaders(),
      body: JSON.stringify({ trends: trendData.data }),
    })
      .then((response) => {
        if (!response.ok) {
          // Graceful handling - forecast ist optional
          return { ok: false }
        }
        return response.json()
      })
      .then((json: ForecastResponse) => {
        if (json.ok === true && isValidForecast(json.data)) {
          setResult(json.data)
        } else {
          setResult(null)
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
