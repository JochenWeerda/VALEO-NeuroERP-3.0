import { useMemo } from 'react'
import { OverviewPage } from '@/components/mask-builder'
import { useFutterStatistik, type FutterStatistik } from '@/lib/api/futter'
import { OverviewConfig, OverviewCard, OverviewChart } from '@/components/mask-builder/types'

// Mock-Daten für KPIs
const mockKPIs: OverviewCard[] = [
  {
    title: 'Gesamtbestand',
    value: '2.847 t',
    change: {
      value: 5.2,
      type: 'increase',
      period: 'vs. letzter Monat'
    },
    icon: '📦',
    color: 'blue'
  },
  {
    title: 'Monatlicher Verbrauch',
    value: '487 t',
    change: {
      value: 2.1,
      type: 'decrease',
      period: 'vs. letzter Monat'
    },
    icon: '📉',
    color: 'orange'
  },
  {
    title: 'Qualitätsrate',
    value: '97,3%',
    change: {
      value: 0.8,
      type: 'increase',
      period: 'vs. letzter Monat'
    },
    icon: '✅',
    color: 'green'
  },
  {
    title: 'Recall-Rate',
    value: '0,02%',
    change: {
      value: 50,
      type: 'decrease',
      period: 'vs. letzter Monat'
    },
    icon: '🚨',
    color: 'red'
  }
]

// Mock-Daten für Charts
const mockChartData: OverviewChart[] = [
  {
    title: 'Bestandsentwicklung',
    type: 'line',
    data: [2450, 2380, 2520, 2680, 2750, 2847]
  },
  {
    title: 'Verbrauch nach Tierart',
    type: 'pie',
    data: [45, 25, 15, 10, 5]
  },
  {
    title: 'Qualitätskennzahlen',
    type: 'bar',
    data: [99.2, 97.8, 98.5, 99.1]
  }
]

// Konfiguration für Futtermittel-Statistik OverviewPage
const statistikConfig: OverviewConfig = {
  title: 'Futtermittel-Statistik',
  subtitle: 'KPIs und Analysen für Qualitätssicherung und Bestandsmanagement',
  type: 'overview-page',
  cards: mockKPIs,
  charts: mockChartData,
  actions: [],
  api: {
    baseUrl: '/api/futtermittel/statistics',
    endpoints: {
      list: '/api/futtermittel/statistics'
    }
  },
  permissions: ['futtermittel.read', 'statistics.read']
}

export default function FuttermittelStatistikPage(): JSX.Element {
  const { data, isLoading } = useFutterStatistik()

  const { kpiData, chartData } = useMemo(() => {
    if (!data) return { kpiData: mockKPIs, chartData: mockChartData }
    const stats = data as FutterStatistik
    const cards: OverviewCard[] = [
      {
        title: 'Gesamtproduktion',
        value: `${stats.gesamtProduktion.toLocaleString('de-DE')} t`,
        change: { value: 0, type: 'increase', period: 'aktuell' },
        icon: '📦',
        color: 'blue',
      },
      {
        title: 'Gesamtabsatz',
        value: `${stats.gesamtAbsatz.toLocaleString('de-DE')} t`,
        change: { value: 0, type: 'increase', period: 'aktuell' },
        icon: '📉',
        color: 'orange',
      },
      {
        title: 'Ø Preis',
        value: `${stats.durchschnittsPreis.toLocaleString('de-DE')} €/t`,
        change: { value: 0, type: 'increase', period: 'aktuell' },
        icon: '💶',
        color: 'green',
      },
      {
        title: 'Top-Produkte',
        value: `${stats.topProdukte.length}`,
        change: { value: 0, type: 'increase', period: 'aktuell' },
        icon: '🏆',
        color: 'red',
      },
    ]
    const charts: OverviewChart[] = [
      {
        title: 'Top-Produkte nach Menge',
        type: 'bar',
        data: stats.topProdukte.map((p) => p.menge),
      },
      {
        title: 'Produktion vs. Absatz',
        type: 'pie',
        data: [stats.gesamtProduktion, stats.gesamtAbsatz],
      },
      {
        title: 'Top-Produkte (Umsatzindikator)',
        type: 'line',
        data: stats.topProdukte.map((p) => p.menge * stats.durchschnittsPreis),
      },
    ]
    return { kpiData: cards, chartData: charts }
  }, [data])

  // Aktualisierte Konfiguration mit echten Daten
  const currentConfig: OverviewConfig = {
    ...statistikConfig,
    cards: kpiData,
    charts: chartData
  }

  return (
    <OverviewPage
      config={currentConfig}
      isLoading={isLoading}
    />
  )
}
