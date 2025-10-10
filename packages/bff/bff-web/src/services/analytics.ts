import { type AnalyticsDailySummary, analyticsDailySummary } from './data';

export interface Kpi {
  id: string;
  label: string;
  value: number;
  delta: number;
  unit?: string;
}

export interface TrendPoint {
  date: string;
  sales: number;
  inventory: number;
}

export interface Forecast {
  forecast: { sales: number; anomaly: boolean };
  summary: string;
  factors: string[];
}

const hundred = 100;
const two = 2;
const anomalyThreshold = -0.05;

const getLatestSnapshots = (history: AnalyticsDailySummary[]): {
  latest: AnalyticsDailySummary;
  previous: AnalyticsDailySummary;
} => {
  if (history.length === 0) {
    throw new Error('Analytics history is empty');
  }

  const latest = history[history.length - 1];
  const previous = history.length > two ? history[history.length - two] : history[history.length - 1];
  return { latest, previous };
};

const percentChange = (current: number, previous: number): number => {
  if (previous === 0) {
    return 0;
  }
  return ((current - previous) / previous) * hundred;
};

const toFixed = (value: number, fractionDigits = 1): number =>
  Number.parseFloat(value.toFixed(fractionDigits));

export async function getKpis(): Promise<Kpi[]> {
  const { latest, previous } = getLatestSnapshots(analyticsDailySummary);

  return [
    {
      id: 'revenue',
      label: 'Umsatz',
      value: latest.revenue,
      delta: toFixed(percentChange(latest.revenue, previous.revenue)),
      unit: ' EUR',
    },
    {
      id: 'orders',
      label: 'Aufträge',
      value: latest.orders,
      delta: toFixed(percentChange(latest.orders, previous.orders)),
    },
    {
      id: 'returns',
      label: 'Retourenquote',
      value: toFixed(latest.returnRate * hundred, two),
      delta: toFixed(percentChange(latest.returnRate, previous.returnRate)),
      unit: ' %',
    },
    {
      id: 'stock',
      label: 'Lagerverfügbarkeit',
      value: toFixed(latest.stockAvailability, 1),
      delta: toFixed(percentChange(latest.stockAvailability, previous.stockAvailability)),
      unit: ' %',
    },
  ];
}

export async function getTrends(): Promise<TrendPoint[]> {
  return analyticsDailySummary.map((snapshot: AnalyticsDailySummary) => ({
    date: snapshot.date,
    sales: snapshot.revenue,
    inventory: snapshot.inventoryLevel,
  }));
}

const formatPercent = (value: number, fractionDigits = 1): string => `${toFixed(value * hundred, fractionDigits)}%`;

export function generateForecast(trends: TrendPoint[]): Forecast {
  if (trends.length === 0) {
    return {
      forecast: { sales: 0, anomaly: false },
      summary: 'Keine Trenddaten vorhanden – Prognose nicht möglich.',
      factors: [],
    };
  }

  if (trends.length === 1) {
    const [only] = trends;
    return {
      forecast: { sales: only.sales, anomaly: false },
      summary: 'Nur ein Datenpunkt vorhanden – es wird mit dem aktuellen Wert weitergerechnet.',
      factors: ['Es liegen nicht genug Datenpunkte für einen Trend vor.'],
    };
  }

  const growthRates = trends.slice(1).map((point, index) => {
    const previous = trends[index];
    if (previous.sales === 0) {
      return 0;
    }
    return (point.sales - previous.sales) / previous.sales;
  });

  const averageGrowth =
    growthRates.reduce((sum, rate) => sum + rate, 0) / Math.max(growthRates.length, 1);

  const lastTrend = trends[trends.length - 1];
  const previousTrend = trends[trends.length - two];
  const projectedSales = Math.round(lastTrend.sales * (1 + averageGrowth));

  const lastGrowth = growthRates[growthRates.length - 1] ?? 0;
  const inventoryChange = percentChange(lastTrend.inventory, previousTrend.inventory);

  const anomaly = lastGrowth < anomalyThreshold;

  const summary = anomaly
    ? `Achtung: Umsatzrückgang von ${formatPercent(lastGrowth)} im letzten Intervall.`
    : `Stabiles Wachstum von durchschnittlich ${formatPercent(averageGrowth)} pro Intervall.`;

  const factors = [
    `Letzter Wachstumswert: ${formatPercent(lastGrowth)}`,
    `Durchschnittliches Wachstum (4 Wochen): ${formatPercent(averageGrowth)}`,
    `Bestandsentwicklung zuletzt: ${toFixed(inventoryChange, 1)}%`,
  ];

  return {
    forecast: {
      sales: projectedSales,
      anomaly,
    },
    summary,
    factors,
  };
}
