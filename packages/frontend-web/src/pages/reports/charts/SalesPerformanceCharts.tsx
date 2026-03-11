import { SimpleComparisonBars } from '@/components/charts/SimpleComparisonBars'

export default function SalesPerformanceCharts({ data }: { data: any }): JSX.Element {
  return (
    <div className="grid grid-cols-1 gap-4 md:grid-cols-2">
      <section className="rounded-lg border bg-card p-4">
        <h4 className="mb-4 font-semibold">Umsatz nach Status</h4>
        <SimpleComparisonBars
          data={[
            { name: 'Bezahlt', value: data?.totalRevenue ?? 0, color: '#10B981' },
            { name: 'Ausstehend', value: (data?.totalRevenue ?? 0) * 0.2, color: '#F59E0B' },
          ]}
          valueFormatter={(value) => `${value.toLocaleString('de-DE')} EUR`}
        />
      </section>
      <section className="rounded-lg border bg-card p-4">
        <h4 className="mb-4 font-semibold">Konversionsraten</h4>
        <SimpleComparisonBars
          data={[
            { name: 'Anfrage -> Angebot', value: data?.conversionRates?.inquiryToOffer ?? 0, color: '#10B981' },
            { name: 'Angebot -> Auftrag', value: data?.conversionRates?.offerToOrder ?? 0, color: '#3B82F6' },
            { name: 'Auftrag -> Rechnung', value: data?.conversionRates?.orderToInvoice ?? 0, color: '#8B5CF6' },
          ]}
          valueFormatter={(value) => `${value.toFixed(1)} %`}
        />
      </section>
    </div>
  )
}
