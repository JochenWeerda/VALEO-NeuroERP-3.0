import { SimpleComparisonBars } from '@/components/charts/SimpleComparisonBars'
import { CHART_POSITIVE, CHART_WARNING } from '@/components/charts/chart-palette'
import type { ReportDashboardData } from '@/pages/reports/report-chart-types'

export default function SalesPerformanceCharts({ data }: { data: ReportDashboardData }): JSX.Element {
  return (
    <div className="grid grid-cols-1 gap-4 md:grid-cols-2">
      <section className="rounded-lg border bg-card p-4">
        <h4 className="mb-4 font-semibold">Umsatz nach Status</h4>
        <SimpleComparisonBars
          data={[
            { name: 'Bezahlt', value: data?.totalRevenue ?? 0, color: CHART_POSITIVE },
            { name: 'Ausstehend', value: (data?.totalRevenue ?? 0) * 0.2, color: CHART_WARNING },
          ]}
          valueFormatter={(value) => `${value.toLocaleString('de-DE')} EUR`}
        />
      </section>
      <section className="rounded-lg border bg-card p-4">
        <h4 className="mb-4 font-semibold">Konversionsraten</h4>
        <SimpleComparisonBars
          data={[
            { name: 'Anfrage -> Angebot', value: data?.conversionRates?.inquiryToOffer ?? 0 },
            { name: 'Angebot -> Auftrag', value: data?.conversionRates?.offerToOrder ?? 0 },
            { name: 'Auftrag -> Rechnung', value: data?.conversionRates?.orderToInvoice ?? 0 },
          ]}
          valueFormatter={(value) => `${value.toFixed(1)} %`}
        />
      </section>
    </div>
  )
}
