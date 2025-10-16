import { useState, useEffect } from 'react'
import { OverviewPage } from '@/components/mask-builder'
import { createApiClient } from '@/components/mask-builder/utils/api'
import { OverviewConfig, OverviewCard, OverviewChart } from '@/components/mask-builder/types'

// API Client für CRM-Statistiken
const apiClient = createApiClient('/api/crm')

// Mock-Daten für KPIs
const mockKPIs: OverviewCard[] = [
  {
    title: 'Aktive Kunden',
    value: '1.247',
    change: {
      value: 8.3,
      type: 'increase',
      period: 'vs. letztes Jahr'
    },
    icon: '👥',
    color: 'blue'
  },
  {
    title: 'Neue Kunden',
    value: '89',
    change: {
      value: 12.5,
      type: 'increase',
      period: 'vs. letzter Monat'
    },
    icon: '🆕',
    color: 'green'
  },
  {
    title: 'Gesamtumsatz',
    value: '€2,4M',
    change: {
      value: 15.7,
      type: 'increase',
      period: 'vs. letztes Jahr'
    },
    icon: '💰',
    color: 'green'
  },
  {
    title: 'Offene Angebote',
    value: '€487K',
    change: {
      value: 5.2,
      type: 'decrease',
      period: 'vs. letzter Monat'
    },
    icon: '📋',
    color: 'orange'
  },
  {
    title: 'Kundenbindung',
    value: '94,2%',
    change: {
      value: 2.1,
      type: 'increase',
      period: 'vs. letztes Jahr'
    },
    icon: '🤝',
    color: 'blue'
  },
  {
    title: 'Durchschnittlicher Bestellwert',
    value: '€1.847',
    change: {
      value: 8.9,
      type: 'increase',
      period: 'vs. letztes Jahr'
    },
    icon: '📊',
    color: 'green'
  }
]

// Mock-Daten für Charts
const mockChartData: OverviewChart[] = [
  {
    title: 'Umsatzentwicklung',
    type: 'line',
    data: [185000, 192000, 198000, 215000, 228000, 242000, 238000, 256000, 271000, 289000, 295000, 312000]
  },
  {
    title: 'Kunden nach Region',
    type: 'pie',
    data: [32, 28, 18, 12, 6, 4]
  },
  {
    title: 'Top 10 Kunden',
    type: 'bar',
    data: [125000, 98000, 87500, 76200, 68900, 65400, 58900, 52100, 49800, 45600]
  },
  {
    title: 'Angebots-Conversion',
    type: 'pie',
    data: [68, 22, 10]
  }
]

// Konfiguration für CRM-Dashboard OverviewPage
const crmDashboardConfig: OverviewConfig = {
  title: 'CRM-Dashboard',
  subtitle: 'Kundenmanagement und Vertriebskennzahlen im Überblick',
  type: 'overview-page',
  cards: mockKPIs,
  charts: mockChartData,
  actions: [],
  api: {
    baseUrl: '/api/crm/dashboard',
    endpoints: {
      list: '/api/crm/dashboard'
    }
  },
  permissions: ['crm.read', 'sales.read']
}

export default function CRMDashboardPage(): JSX.Element {
  const [kpiData, setKpiData] = useState<OverviewCard[]>(mockKPIs)
  const [chartData, setChartData] = useState<OverviewChart[]>(mockChartData)
  const [loading, setLoading] = useState(false)

  const loadData = async () => {
    setLoading(true)
    try {
      const response = await apiClient.get('/dashboard')

      if (response.success) {
        setKpiData((response.data as any).kpis || mockKPIs)
        setChartData((response.data as any).charts || mockChartData)
      }
    } catch (error) {
      console.error('Fehler beim Laden des CRM-Dashboards:', error)
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
    ...crmDashboardConfig,
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