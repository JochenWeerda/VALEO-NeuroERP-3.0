import { useMemo } from 'react'
import { OverviewPage } from '@/components/mask-builder'
import { useFutterStatistik, type FutterStatistik } from '@/lib/api/futter'
import { OverviewConfig, OverviewCard, OverviewChart } from '@/components/mask-builder/types'
import { ErrorState } from '@/components/ErrorState'

const statistikConfig: OverviewConfig = {
  title: 'Futtermittel-Statistik',
  subtitle: 'KPIs und Analysen fuer Qualitaetssicherung und Bestandsmanagement',
  type: 'overview-page',
  cards: [],
  charts: [],
  actions: [],
  api: {
    baseUrl: '/api/futtermittel/statistics',
    endpoints: {
      list: '/api/futtermittel/statistics',
    },
  },
  permissions: ['futtermittel.read', 'statistics.read'],
}

export default function FuttermittelStatistikPage(): JSX.Element {
  const { data, isLoading, isError, error, refetch } = useFutterStatistik()

  const { kpiData, chartData } = useMemo(() => {
    const stats = (data ?? {
      gesamtProduktion: 0,
      gesamtAbsatz: 0,
      durchschnittsPreis: 0,
      topProdukte: [],
    }) as FutterStatistik

    const produktion = stats.gesamtProduktion ?? 0
    const absatz = stats.gesamtAbsatz ?? 0
    const preis = stats.durchschnittsPreis ?? 0
    const produkte = stats.topProdukte ?? []

    const cards: OverviewCard[] = [
      {
        title: 'Gesamtproduktion',
        value: `${produktion.toLocaleString('de-DE')} t`,
        change: { value: 0, type: 'increase', period: 'aktuell' },
        icon: 'PKG',
        color: 'blue',
      },
      {
        title: 'Gesamtabsatz',
        value: `${absatz.toLocaleString('de-DE')} t`,
        change: { value: 0, type: 'increase', period: 'aktuell' },
        icon: 'TREND',
        color: 'orange',
      },
      {
        title: 'Oe Preis',
        value: `${preis.toLocaleString('de-DE')} EUR/t`,
        change: { value: 0, type: 'increase', period: 'aktuell' },
        icon: 'MONEY',
        color: 'green',
      },
      {
        title: 'Top-Produkte',
        value: `${produkte.length}`,
        change: { value: 0, type: 'increase', period: 'aktuell' },
        icon: 'TOP',
        color: 'red',
      },
    ]

    const charts: OverviewChart[] = [
      {
        title: 'Top-Produkte nach Menge',
        type: 'bar',
        data: produkte.map((p) => p.menge),
      },
      {
        title: 'Produktion vs. Absatz',
        type: 'pie',
        data: [produktion, absatz],
      },
      {
        title: 'Top-Produkte (Umsatzindikator)',
        type: 'line',
        data: produkte.map((p) => p.menge * preis),
      },
    ]

    return { kpiData: cards, chartData: charts }
  }, [data])

  if (isError) {
    return <ErrorState error={error as Error} onRetry={() => { void refetch() }} />
  }

  const currentConfig: OverviewConfig = {
    ...statistikConfig,
    cards: kpiData,
    charts: chartData,
  }

  return <OverviewPage config={currentConfig} isLoading={isLoading} />
}
