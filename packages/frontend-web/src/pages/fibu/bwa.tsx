import { useState } from 'react'
import { useQuery } from '@tanstack/react-query'
import { Button } from '@/components/ui/button'
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card'
import { Input } from '@/components/ui/input'
import { Skeleton } from '@/components/ui/skeleton'
import { TrendingUp, RefreshCw } from 'lucide-react'
import { financeService } from '@/lib/services/finance-service'
import { OperationalCaseHeader } from '@/components/workflow/OperationalCaseHeader'
import { OperationalContextPanel } from '@/components/workflow/OperationalContextPanel'
import { OperationalTimeline } from '@/components/workflow/OperationalTimeline'
import { normalizeOperationalStatus } from '@/lib/operational-status'

const fmtNum = (n: number) => new Intl.NumberFormat('de-DE').format(Math.round(n))

export default function BwaPage(): JSX.Element {
  const currentPeriod = new Date().toISOString().substring(0, 7)
  const [period, setPeriod] = useState(currentPeriod)

  const { data: bwa, isLoading, isError, refetch } = useQuery({
    queryKey: ['fibu', 'bwa', period],
    queryFn: () => financeService.getBwa({ period }),
    staleTime: 5 * 60 * 1000,
  })

  if (isLoading) {
    return (
      <div className="space-y-6 p-6">
        <Skeleton className="h-10 w-64" />
        <div className="grid gap-4 md:grid-cols-4">
          {[...Array(4)].map((_, i) => <Skeleton key={i} className="h-24" />)}
        </div>
        <Skeleton className="h-96" />
      </div>
    )
  }

  const totalRevenue = bwa ? Number(bwa.total_revenue) : 0
  const totalCosts = bwa ? Number(bwa.total_costs) : 0
  const netResult = bwa ? Number(bwa.net_result) : 0
  const netResultPct = totalRevenue > 0 ? ((netResult / totalRevenue) * 100).toFixed(1) : '0.0'
  const operationalStatus = normalizeOperationalStatus(!bwa ? 'offen' : netResult < 0 ? 'eskaliert' : 'in_pruefung')
  const contextSections = [
    {
      title: 'Vorgang',
      items: [
        { label: 'Periode', value: bwa?.period ?? period },
        { label: 'Positionen', value: String(bwa?.items.length ?? 0) },
        { label: 'Status', value: bwa ? 'BWA geladen' : 'Keine Daten' },
      ],
    },
    {
      title: 'Wirtschaftslage',
      items: [
        { label: 'Umsatz', value: `${fmtNum(totalRevenue)} EUR` },
        { label: 'Kosten', value: `${fmtNum(totalCosts)} EUR` },
        { label: 'Ergebnisquote', value: `${netResultPct}%` },
      ],
    },
    {
      title: 'Governance',
      items: [
        { label: 'Naechste Aktion', value: netResult < 0 ? 'Ergebnisabweichung analysieren' : 'Periode gegen Vorlauf pruefen' },
        { label: 'Blocker', value: !bwa ? `Keine BWA-Daten fuer ${period}` : 'Kein akuter Blocker' },
      ],
    },
  ]
  const timelineItems = [
    { label: 'BWA geladen', detail: bwa ? `Periode ${bwa.period}` : `Keine Daten fuer ${period}` },
    bwa ? { label: 'Ergebnis berechnet', detail: `${fmtNum(netResult)} EUR` } : null,
    bwa && netResult < 0 ? { label: 'Negatives Ergebnis erkannt', detail: 'Deckungsbeitrag und Kosten pruefen' } : null,
  ].filter((item): item is { label: string; detail: string } => item !== null)

  return (
    <div className="space-y-6 p-6">
      <OperationalCaseHeader
        title="BWA"
        description="Verdichtete Ergebnislage fuer die gewaehlte Periode mit Fokus auf Abweichungen."
        status={operationalStatus}
        owner="Controlling"
        blocker={!bwa ? `Fuer ${period} liegen keine BWA-Daten vor.` : netResult < 0 ? 'Ergebnis ist negativ.' : null}
        nextAction={netResult < 0 ? 'Kosten- und Umsatztreiber analysieren' : 'Periode freigeben oder exportieren'}
        caseLabel={bwa?.period ?? period}
        tags={['FIBU', 'Controlling']}
      />
      <div className="grid gap-4 xl:grid-cols-[1.3fr_0.7fr]">
        <OperationalTimeline title="BWA-Verlauf" items={timelineItems} />
        <OperationalContextPanel sections={contextSections} />
      </div>
      <div className="flex items-center gap-4 flex-wrap">
        <div>
          <h1 className="text-3xl font-bold">Betriebswirtschaftliche Auswertung (BWA)</h1>
          <p className="text-muted-foreground">Periode: {bwa?.period ?? period}</p>
        </div>
        <Input
          type="month"
          value={period}
          onChange={e => setPeriod(e.target.value)}
          className="w-40"
        />
        <Button variant="outline" size="sm" onClick={() => void refetch()} className="gap-2">
          <RefreshCw className="h-4 w-4" />
        </Button>
      </div>

      {(isError || !bwa) && (
        <Card className="border-amber-200 bg-amber-50">
          <CardContent className="p-4 text-amber-800 text-sm">
            Keine BWA-Daten für Periode {period} vorhanden.
          </CardContent>
        </Card>
      )}

      {bwa && (
        <>
          <div className="grid gap-4 md:grid-cols-4">
            <Card>
              <CardHeader className="pb-2">
                <CardTitle className="text-sm font-medium">Umsatz (Monat)</CardTitle>
              </CardHeader>
              <CardContent>
                <div className="flex items-center gap-2">
                  <TrendingUp className="h-5 w-5 text-blue-600" />
                  <span className="text-2xl font-bold">{fmtNum(totalRevenue)} €</span>
                </div>
              </CardContent>
            </Card>
            <Card>
              <CardHeader className="pb-2">
                <CardTitle className="text-sm font-medium">Kosten</CardTitle>
              </CardHeader>
              <CardContent>
                <span className="text-2xl font-bold text-red-600">{fmtNum(totalCosts)} €</span>
              </CardContent>
            </Card>
            <Card>
              <CardHeader className="pb-2">
                <CardTitle className="text-sm font-medium">Ergebnis</CardTitle>
              </CardHeader>
              <CardContent>
                <span className={`text-2xl font-bold ${netResult >= 0 ? 'text-green-600' : 'text-red-600'}`}>
                  {fmtNum(netResult)} €
                </span>
              </CardContent>
            </Card>
            <Card>
              <CardHeader className="pb-2">
                <CardTitle className="text-sm font-medium">Ergebnis-Quote</CardTitle>
              </CardHeader>
              <CardContent>
                <span className={`text-2xl font-bold ${netResult >= 0 ? 'text-green-600' : 'text-red-600'}`}>
                  {netResultPct}%
                </span>
              </CardContent>
            </Card>
          </div>

          <Card>
            <CardHeader>
              <CardTitle>BWA-Schema</CardTitle>
            </CardHeader>
            <CardContent>
              <div className="overflow-x-auto">
                <table className="w-full">
                  <thead>
                    <tr className="border-b-2">
                      <th className="text-left py-3">Position</th>
                      <th className="text-right py-3">Aktuell (€)</th>
                      <th className="text-right py-3">Vorperiode (€)</th>
                      <th className="text-right py-3">YTD (€)</th>
                      <th className="text-right py-3">Quote (%)</th>
                    </tr>
                  </thead>
                  <tbody className="text-sm">
                    {bwa.items.map((item, i) => {
                      const isTotal = item.position.startsWith('=')
                      return (
                        <tr key={i} className={`border-b ${isTotal ? 'bg-blue-50 font-bold' : ''}`}>
                          <td className={`py-3 ${isTotal ? '' : 'pl-4'}`}>{item.description}</td>
                          <td className={`text-right ${Number(item.current_period) < 0 ? 'text-red-600' : ''}`}>
                            {fmtNum(Number(item.current_period))}
                          </td>
                          <td className="text-right text-muted-foreground">
                            {fmtNum(Number(item.previous_period))}
                          </td>
                          <td className="text-right">{fmtNum(Number(item.year_to_date))}</td>
                          <td className="text-right">{Number(item.percentage).toFixed(1)}</td>
                        </tr>
                      )
                    })}
                  </tbody>
                </table>
              </div>
            </CardContent>
          </Card>

          <div className="rounded-lg bg-blue-50 p-4 text-sm text-blue-900">
            <p className="font-semibold">Hinweis</p>
            <p className="mt-1">BWA nach DATEV-Standard (SKR03) · Monatliche Aktualisierung · DATEV-Export verfügbar</p>
          </div>
        </>
      )}
    </div>
  )
}
