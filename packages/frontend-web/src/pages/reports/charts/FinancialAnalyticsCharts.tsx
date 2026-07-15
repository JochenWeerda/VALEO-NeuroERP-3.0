import { SimpleComparisonBars } from '@/components/charts/SimpleComparisonBars'
import { CHART_NEGATIVE, CHART_POSITIVE, CHART_WARNING, chartSeriesColor } from '@/components/charts/chart-palette'
import type { ReportDashboardData } from '@/pages/reports/report-chart-types'

export default function FinancialAnalyticsCharts({ data }: { data: ReportDashboardData }): JSX.Element {
  return (
    <div className="grid grid-cols-1 gap-4 md:grid-cols-2">
      <section className="rounded-lg border bg-card p-4">
        <h4 className="mb-4 font-semibold">Umsatzuebersicht</h4>
        <SimpleComparisonBars
          data={[
            { name: 'Gesamt', value: data?.revenue?.total ?? 0, color: chartSeriesColor(0) },
            { name: 'Bezahlt', value: data?.revenue?.paid ?? 0, color: CHART_POSITIVE },
            { name: 'Ausstehend', value: data?.revenue?.outstanding ?? 0, color: CHART_WARNING },
          ]}
          valueFormatter={(value) => `${value.toLocaleString('de-DE')} EUR`}
        />
      </section>
      <section className="rounded-lg border bg-card p-4">
        <h4 className="mb-4 font-semibold">Ausstehende Zahlungen</h4>
        <SimpleComparisonBars
          data={[
            { name: 'Aktuell', value: data?.outstandingPayments?.current ?? 0, color: chartSeriesColor(0) },
            { name: '30 Tage', value: data?.outstandingPayments?.overdue30Days ?? 0, color: CHART_WARNING },
            { name: '60 Tage', value: data?.outstandingPayments?.overdue60Days ?? 0, color: 'hsl(var(--status-error-hsl) / 0.7)' },
            { name: '90+ Tage', value: data?.outstandingPayments?.overdue90Days ?? 0, color: CHART_NEGATIVE },
          ]}
          valueFormatter={(value) => `${value.toLocaleString('de-DE')} EUR`}
        />
      </section>
    </div>
  )
}
