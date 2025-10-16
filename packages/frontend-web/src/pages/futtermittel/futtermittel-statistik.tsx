import { useState, useEffect } from 'react'
import { OverviewPage } from '@/components/mask-builder'
import { createApiClient } from '@/components/mask-builder/utils/api'
import { OverviewConfig, OverviewCard, OverviewChart } from '@/components/mask-builder/types'

// API Client für Statistiken
const apiClient = createApiClient('/api/futtermittel')

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
  const [kpiData, setKpiData] = useState<OverviewCard[]>(mockKPIs)
  const [chartData, setChartData] = useState<OverviewChart[]>(mockChartData)
  const [loading, setLoading] = useState(false)

  const loadData = async () => {
    setLoading(true)
    try {
      const response = await apiClient.get('/statistics')

      if (response.success) {
        setKpiData((response.data as any).kpis || mockKPIs)
        setChartData((response.data as any).charts || mockChartData)
      }
    } catch (error) {
      console.error('Fehler beim Laden der Statistiken:', error)
      // Bei Fehler bleiben Mock-Daten erhalten
    } finally {
      setLoading(false)
    }
  }

  useEffect(() => {
    loadData()

    // Automatische Aktualisierung alle 5 Minuten
    const interval = setInterval(loadData, 300000)
    return () => clearInterval(interval)
  }, [])

  // Aktualisierte Konfiguration mit echten Daten
  const currentConfig: OverviewConfig = {
    ...statistikConfig,
    cards: kpiData,
    charts: chartData
  }

  return (
    <OverviewPage
      config={currentConfig}
      isLoading={loading}
    />
  )
}