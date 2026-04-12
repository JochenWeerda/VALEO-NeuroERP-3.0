import { useState } from 'react'
import { useQuery } from '@tanstack/react-query'
import { Badge } from '@/components/ui/badge'
import { Button } from '@/components/ui/button'
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card'
import { Input } from '@/components/ui/input'
import { Skeleton } from '@/components/ui/skeleton'
import { OperationalCaseHeader } from '@/components/workflow/OperationalCaseHeader'
import { OperationalContextPanel } from '@/components/workflow/OperationalContextPanel'
import { OperationalTimeline } from '@/components/workflow/OperationalTimeline'
import { TrendingUp, RefreshCw } from 'lucide-react'
import { financeService } from '@/lib/services/finance-service'
import { normalizeOperationalStatus } from '@/lib/operational-status'

const fmt = (n: number) =>
  new Intl.NumberFormat('de-DE', { style: 'currency', currency: 'EUR', maximumFractionDigits: 0 }).format(n)

export default function GuvPage(): JSX.Element {
  const currentPeriod = new Date().toISOString().substring(0, 7)
  const [period, setPeriod] = useState(currentPeriod)

  const { data: guv, isLoading, isError, refetch } = useQuery({
    queryKey: ['fibu', 'guv', period],
    queryFn: () => financeService.getGuV({ period }),
    staleTime: 5 * 60 * 1000,
  })

  if (isLoading) {
    return (
      <div className="space-y-6 p-6">
        <Skeleton className="h-10 w-64" />
        <div className="grid gap-4 md:grid-cols-3">
          {[...Array(3)].map((_, i) => <Skeleton key={i} className="h-24" />)}
        </div>
        <Skeleton className="h-64" />
        <Skeleton className="h-64" />
      </div>
    )
  }

  const jahresueberschuss = guv ? Number(guv.net_income) : 0
  const gesamtertraege = guv ? Number(guv.total_revenue) : 0
  const gesamtaufwendungen = guv ? Number(guv.total_expenses) : 0
  const umsatzrendite = gesamtertraege > 0 ? ((jahresueberschuss / gesamtertraege) * 100).toFixed(1) : '0.0'
  const operationalStatus = normalizeOperationalStatus(!guv ? 'offen' : jahresueberschuss < 0 ? 'eskaliert' : 'in_pruefung')
  const contextSections = [
    {
      title: 'Periode',
      items: [
        { label: 'Periode', value: guv?.period ?? period },
        { label: 'Ertragspositionen', value: String(guv?.revenue.length ?? 0) },
        { label: 'Aufwandspositionen', value: String(guv?.expenses.length ?? 0) },
      ],
    },
    {
      title: 'Wirtschaftslage',
      items: [
        { label: 'Ertraege', value: fmt(gesamtertraege) },
        { label: 'Aufwendungen', value: fmt(gesamtaufwendungen) },
        { label: 'Rendite', value: `${umsatzrendite}%` },
      ],
    },
    {
      title: 'Governance',
      items: [
        { label: 'Naechste Aktion', value: jahresueberschuss < 0 ? 'Ergebnisabweichung analysieren' : 'Periode validieren oder exportieren' },
        { label: 'Blocker', value: !guv ? `Keine GuV-Daten fuer ${period}` : jahresueberschuss < 0 ? 'Negatives Periodenergebnis.' : 'Kein akuter Blocker' },
      ],
    },
  ]
  const timelineItems = [
    { label: 'GuV geladen', detail: guv ? `Periode ${guv.period}` : `Keine Daten fuer ${period}` },
    guv ? { label: 'Ergebnis ermittelt', detail: fmt(jahresueberschuss) } : null,
    guv && jahresueberschuss < 0 ? { label: 'Negatives Ergebnis erkannt', detail: 'Ertrags- und Kostenpositionen pruefen' } : null,
  ].filter((item): item is { label: string; detail: string } => item !== null)

  return (
    <div className="space-y-6 p-6">
      <OperationalCaseHeader
        title="Gewinn- und Verlustrechnung"
        description="Ergebnisraum fuer Ertraege, Aufwendungen und Periodenergebnis."
        status={operationalStatus}
        owner="Controlling"
        blocker={!guv ? `Fuer ${period} liegen keine GuV-Daten vor.` : jahresueberschuss < 0 ? 'Negatives Ergebnis in der gewaehlten Periode.' : null}
        nextAction={jahresueberschuss < 0 ? 'Kosten- und Ertragsabweichungen pruefen' : 'Periode freigeben oder exportieren'}
        caseLabel={guv?.period ?? period}
        tags={['FIBU', 'Controlling']}
      />
      <div className="grid gap-4 xl:grid-cols-[1.3fr_0.7fr]">
        <OperationalTimeline title="GuV-Verlauf" items={timelineItems} />
        <OperationalContextPanel sections={contextSections} />
      </div>
      <div className="flex items-center justify-between flex-wrap gap-4">
        <div className="flex items-center gap-4">
          <div>
            <h1 className="text-3xl font-bold">Gewinn- und Verlustrechnung</h1>
            <p className="text-muted-foreground">Periode: {guv?.period ?? period}</p>
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
        <Badge variant="outline" className="text-lg px-4 py-2">
          Umsatzrendite: {umsatzrendite}%
        </Badge>
      </div>

      {(isError || !guv) && (
        <Card className="border-amber-200 bg-amber-50">
          <CardContent className="p-4 text-amber-800 text-sm">
            Keine GuV-Daten für Periode {period} vorhanden.
          </CardContent>
        </Card>
      )}

      {guv && (
        <>
          <div className="grid gap-4 md:grid-cols-3">
            <Card>
              <CardHeader className="pb-2">
                <CardTitle className="text-sm font-medium">Erträge</CardTitle>
              </CardHeader>
              <CardContent>
                <div className="flex items-center gap-2">
                  <TrendingUp className="h-5 w-5 text-green-600" />
                  <span className="text-2xl font-bold text-green-600">{fmt(gesamtertraege)}</span>
                </div>
              </CardContent>
            </Card>
            <Card>
              <CardHeader className="pb-2">
                <CardTitle className="text-sm font-medium">Aufwendungen</CardTitle>
              </CardHeader>
              <CardContent>
                <span className="text-2xl font-bold text-red-600">{fmt(gesamtaufwendungen)}</span>
              </CardContent>
            </Card>
            <Card>
              <CardHeader className="pb-2">
                <CardTitle className="text-sm font-medium">Jahresüberschuss</CardTitle>
              </CardHeader>
              <CardContent>
                <span className={`text-2xl font-bold ${jahresueberschuss >= 0 ? 'text-green-600' : 'text-red-600'}`}>
                  {fmt(jahresueberschuss)}
                </span>
              </CardContent>
            </Card>
          </div>

          <div className="space-y-6">
            {/* ERTRÄGE */}
            <Card>
              <CardHeader>
                <CardTitle className="text-xl text-green-600">ERTRÄGE</CardTitle>
              </CardHeader>
              <CardContent>
                <div className="space-y-2">
                  {guv.revenue.map((pos, i) => (
                    <div key={i} className="flex justify-between py-2 border-b last:border-0">
                      <span>{pos.account_name}</span>
                      <span className="font-semibold">{fmt(Number(pos.amount))}</span>
                    </div>
                  ))}
                  <div className="flex justify-between pt-3 mt-3 border-t-2 font-bold text-lg">
                    <span>Gesamterträge</span>
                    <span className="text-green-600">{fmt(gesamtertraege)}</span>
                  </div>
                </div>
              </CardContent>
            </Card>

            {/* AUFWENDUNGEN */}
            <Card>
              <CardHeader>
                <CardTitle className="text-xl text-red-600">AUFWENDUNGEN</CardTitle>
              </CardHeader>
              <CardContent>
                <div className="space-y-2">
                  {guv.expenses.map((pos, i) => (
                    <div key={i} className="flex justify-between py-2 border-b last:border-0">
                      <span>{pos.account_name}</span>
                      <span className="font-semibold">{fmt(Number(pos.amount))}</span>
                    </div>
                  ))}
                  <div className="flex justify-between pt-3 mt-3 border-t-2 font-bold text-lg">
                    <span>Gesamtaufwendungen</span>
                    <span className="text-red-600">{fmt(gesamtaufwendungen)}</span>
                  </div>
                </div>
              </CardContent>
            </Card>

            {/* ERGEBNIS */}
            <Card className={jahresueberschuss >= 0 ? 'border-green-500' : 'border-red-500'}>
              <CardContent className="pt-6">
                <div className="flex justify-between items-center">
                  <span className="text-2xl font-bold">JAHRESÜBERSCHUSS/-FEHLBETRAG</span>
                  <span className={`text-3xl font-bold ${jahresueberschuss >= 0 ? 'text-green-600' : 'text-red-600'}`}>
                    {fmt(jahresueberschuss)}
                  </span>
                </div>
              </CardContent>
            </Card>
          </div>
        </>
      )}
    </div>
  )
}
