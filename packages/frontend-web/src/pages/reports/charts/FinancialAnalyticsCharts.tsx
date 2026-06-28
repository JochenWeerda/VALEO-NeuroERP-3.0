import { SimpleComparisonBars } from '@/components/charts/SimpleComparisonBars'

export default function FinancialAnalyticsCharts({ data }: { data: unknown }): JSX.Element {
  return (
    <div className="grid grid-cols-1 gap-4 md:grid-cols-2">
      <section className="rounded-lg border bg-card p-4">
        <h4 className="mb-4 font-semibold">Umsatzuebersicht</h4>
        <SimpleComparisonBars
          data={[
            { name: 'Gesamt', value: data?.revenue?.total ?? 0, color: '#F59E0B' },
            { name: 'Bezahlt', value: data?.revenue?.paid ?? 0, color: '#10B981' },
            { name: 'Ausstehend', value: data?.revenue?.outstanding ?? 0, color: '#EF4444' },
          ]}
          valueFormatter={(value) => `${value.toLocaleString('de-DE')} EUR`}
        />
      </section>
      <section className="rounded-lg border bg-card p-4">
        <h4 className="mb-4 font-semibold">Ausstehende Zahlungen</h4>
        <SimpleComparisonBars
          data={[
            { name: 'Aktuell', value: data?.outstandingPayments?.current ?? 0, color: '#2563EB' },
            { name: '30 Tage', value: data?.outstandingPayments?.overdue30Days ?? 0, color: '#F59E0B' },
            { name: '60 Tage', value: data?.outstandingPayments?.overdue60Days ?? 0, color: '#FB7185' },
            { name: '90+ Tage', value: data?.outstandingPayments?.overdue90Days ?? 0, color: '#EF4444' },
          ]}
          valueFormatter={(value) => `${value.toLocaleString('de-DE')} EUR`}
        />
      </section>
    </div>
  )
}
