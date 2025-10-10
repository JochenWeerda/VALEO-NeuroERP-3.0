/**
 * Regel-Engine für KPI-Scores und Alert-Generierung
 * Berechnet Scores und generiert Alerts basierend auf KPIs und Trends
 */

const SCORE_NORMALIZATION_FACTOR = 10
const MARGIN_EXCELLENT = 20
const MARGIN_GOOD = 16
const MARGIN_WARNING = 12
const MARGIN_SCORE_EXCELLENT = 0.8
const MARGIN_SCORE_GOOD = 0.4
const MARGIN_SCORE_WARNING = -0.2
const MARGIN_SCORE_CRITICAL = -0.6
const REVENUE_DROP_CRITICAL = -8
const REVENUE_DROP_WARNING = -4
const STOCK_VALUE_HIGH_THRESHOLD = 500_000
const MIN_TRENDS_FOR_DRIFT = 3
const TREND_INDEX_LAST = -1
const TREND_INDEX_PREV = -3
const MIN_DIVISOR = 1

export type KPI = {
  id: string
  label: string
  value: number
  delta?: number
  unit?: string
}

export type TrendPoint = {
  date: string
  sales: number
  inventory: number
}

export type Alert = {
  id: string
  title: string
  message: string
  severity: "ok" | "warn" | "crit"
  kpiId?: string
}

export type HeatCell = {
  id: string
  row: string
  col: string
  score: number // ∈ [-1,1]
  tooltip?: string
}

/**
 * Berechnet Scores und Alerts aus KPIs und Trends
 */
export function computeScores(
  kpis: KPI[],
  trends: TrendPoint[]
): { cells: HeatCell[]; alerts: Alert[] } {
  const alerts: Alert[] = []
  const cells: HeatCell[] = []

  const revenueKpi = kpis.find((k) => k.id === "rev")
  const marginKpi = kpis.find((k) => k.id === "margin")
  const stockKpi = kpis.find((k) => k.id === "stock")

  // Umsatz-Score: +delta gut, -delta schlecht
  if (revenueKpi !== undefined) {
    const delta = revenueKpi.delta ?? 0
    const normalizedDelta = delta / SCORE_NORMALIZATION_FACTOR
    const score = Math.max(-1, Math.min(1, normalizedDelta))

    cells.push({
      id: "rev-delta",
      row: "Revenue",
      col: "Δ",
      score,
      tooltip: `Δ ${delta.toFixed(1)}%`,
    })

    if (delta <= REVENUE_DROP_CRITICAL) {
      alerts.push({
        id: "rev-drop",
        title: "Umsatzrückgang",
        message: `Umsatz -${Math.abs(delta).toFixed(1)} %`,
        severity: "crit",
        kpiId: "rev",
      })
    } else if (delta <= REVENUE_DROP_WARNING) {
      alerts.push({
        id: "rev-softdrop",
        title: "Umsatz schwächelt",
        message: `Umsatz ${delta.toFixed(1)} %`,
        severity: "warn",
        kpiId: "rev",
      })
    }
  }

  // Marge-Score: < 12% kritisch, 12–16% warn, >16% ok
  if (marginKpi !== undefined) {
    const marginValue = marginKpi.value
    let score: number

    if (marginValue >= MARGIN_EXCELLENT) {
      score = MARGIN_SCORE_EXCELLENT
    } else if (marginValue >= MARGIN_GOOD) {
      score = MARGIN_SCORE_GOOD
    } else if (marginValue >= MARGIN_WARNING) {
      score = MARGIN_SCORE_WARNING
    } else {
      score = MARGIN_SCORE_CRITICAL
    }

    cells.push({
      id: "margin-level",
      row: "Margin",
      col: "%",
      score,
      tooltip: `Marge ${marginValue.toFixed(1)}%`,
    })

    if (marginValue < MARGIN_WARNING) {
      alerts.push({
        id: "margin-low",
        title: "Marge zu niedrig",
        message: `Marge ${marginValue.toFixed(1)} %`,
        severity: "crit",
        kpiId: "margin",
      })
    } else if (marginValue < MARGIN_GOOD) {
      alerts.push({
        id: "margin-warn",
        title: "Marge unter Ziel",
        message: `Marge ${marginValue.toFixed(1)} %`,
        severity: "warn",
        kpiId: "margin",
      })
    }
  }

  // Lager-Score: 7-Tage-Drift
  if (trends.length >= MIN_TRENDS_FOR_DRIFT && stockKpi !== undefined) {
    const lastTrend = trends.at(TREND_INDEX_LAST)
    const prevTrend = trends.at(TREND_INDEX_PREV)

    if (lastTrend !== undefined && prevTrend !== undefined) {
      const lastInventory = lastTrend.inventory
      const prevInventory = prevTrend.inventory
      const drift =
        (lastInventory - prevInventory) / Math.max(MIN_DIVISOR, prevInventory)
      const score = -drift // sinkendes Lager = positiver Score (Abverkauf)
      const normalizedScore = Math.max(-1, Math.min(1, score))

      cells.push({
        id: "stock-drift",
        row: "Inventory",
        col: "Drift",
        score: normalizedScore,
        tooltip: `Drift ${(drift * 100).toFixed(1)}%`,
      })
    }

    // Lagerwert Warnung
    const stockValue = stockKpi.value
    if (stockValue > STOCK_VALUE_HIGH_THRESHOLD) {
      alerts.push({
        id: "stock-high",
        title: "Lagerwert hoch",
        message: `Lagerwert ${stockValue.toLocaleString("de-DE")} €`,
        severity: "warn",
        kpiId: "stock",
      })
    }
  }

  return { cells, alerts }
}
