import { useMemo } from 'react'
import { useNavigate } from '@/app/routing/typed-router'
import { useQuery } from '@tanstack/react-query'
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card'
import { Button } from '@/components/ui/button'
import { Badge } from '@/components/ui/badge'
import { OperationalCaseHeader } from '@/components/workflow/OperationalCaseHeader'
import { OperationalContextPanel } from '@/components/workflow/OperationalContextPanel'
import { OperationalTimeline } from '@/components/workflow/OperationalTimeline'
import { Table, TableBody, TableCell, TableHead, TableHeader, TableRow } from '@/components/ui/table'
import { listKontrakte, type KontraktListItem } from '@/lib/api/kontrakte'
import { normalizeOperationalStatus } from '@/lib/operational-status'
import { AlertTriangle, Clock, TrendingUp, Package } from 'lucide-react'

function daysUntil(dateStr: string | null | undefined): number | null {
  if (!dateStr) return null
  const target = new Date(dateStr)
  const now = new Date()
  return Math.ceil((target.getTime() - now.getTime()) / (1000 * 60 * 60 * 24))
}

type AlarmItem = KontraktListItem & {
  alarmType: 'expiring' | 'low_rest' | 'matif_open' | 'hedge_gap' | 'dunning_due' | 'market_valuation' | 'washout_candidate' | 'print_missing'
  alarmText: string
  daysLeft: number | null
}

export default function KontraktAlarmDashboard(): JSX.Element {
  const navigate = useNavigate()

  const query = useQuery({
    queryKey: ['kontrakte', 'alarm-dashboard'],
    queryFn: () => listKontrakte({ include_done: false, skip: 0, limit: 500 }),
    refetchInterval: 60_000,
  })

  const alarms = useMemo<AlarmItem[]>(() => {
    const items = query.data?.items ?? []
    const result: AlarmItem[] = []

    for (const item of items) {
      if (item.status !== 'OFFEN') continue

      const days = daysUntil(item.valid_to)
      if (days !== null && days >= 0 && days <= 30) {
        result.push({
          ...item,
          alarmType: 'expiring',
          alarmText: days === 0 ? 'Laeuft heute ab' : `Laeuft in ${days} Tagen ab`,
          daysLeft: days,
        })
      }

      if (item.total_quantity > 0) {
        const restPct = (item.rest_quantity / item.total_quantity) * 100
        if (restPct <= 10 && item.rest_quantity > 0) {
          result.push({
            ...item,
            alarmType: 'low_rest',
            alarmText: `Nur noch ${item.rest_quantity.toLocaleString('de-DE')} ${item.unit} (${restPct.toFixed(1)}%) Rest`,
            daysLeft: null,
          })
        }
      }

      if (item.pricing_model === 'matif') {
        const hasPrice = item.first_unit_price != null && item.first_unit_price > 0
        if (!hasPrice) {
          result.push({
            ...item,
            alarmType: 'matif_open',
            alarmText: 'MATIF-Preisfixierung ausstehend',
            daysLeft: null,
          })
        }
      }

      const hedgeGap = item.steering?.hedge_gap_pct ?? null
      if ((hedgeGap ?? 0) > 0) {
        result.push({
          ...item,
          alarmType: 'hedge_gap',
          alarmText: `Absicherungsluecke von ${hedgeGap?.toFixed(1)}% zum Hedge-Ziel`,
          daysLeft: null,
        })
      }

      if (item.steering?.dunning_candidate) {
        result.push({
          ...item,
          alarmType: 'dunning_due',
          alarmText: `Kontrakt-Mahnung faellig${item.steering?.dunning_reason ? `: ${item.steering.dunning_reason}` : ''}`,
          daysLeft: null,
        })
      }

      if ((item.steering?.market_valuation_eur ?? 0) < 0) {
        result.push({
          ...item,
          alarmType: 'market_valuation',
          alarmText: `Negative Marktbewertung ${item.steering?.market_valuation_eur?.toLocaleString('de-DE', { minimumFractionDigits: 2, maximumFractionDigits: 2 })} EUR`,
          daysLeft: null,
        })
      }

      if (item.steering?.writeoff_candidate) {
        result.push({
          ...item,
          alarmType: 'washout_candidate',
          alarmText: `Washout/Abschreibung vorgemerkt${item.steering?.washout_reason ? `: ${item.steering.washout_reason}` : ''}`,
          daysLeft: null,
        })
      }

      if (item.status === 'OFFEN' && !item.steering?.print_ready) {
        result.push({
          ...item,
          alarmType: 'print_missing',
          alarmText: 'Drucksteuerung unvollstaendig (Vorlage oder Kanal fehlt)',
          daysLeft: null,
        })
      }
    }

    return result.sort((a, b) => {
      const prio = { expiring: 0, dunning_due: 1, hedge_gap: 2, market_valuation: 3, washout_candidate: 4, print_missing: 5, matif_open: 6, low_rest: 7 }
      const diff = prio[a.alarmType] - prio[b.alarmType]
      if (diff !== 0) return diff
      return (a.daysLeft ?? 999) - (b.daysLeft ?? 999)
    })
  }, [query.data])

  const expiringCount = alarms.filter((a) => a.alarmType === 'expiring').length
  const lowRestCount = alarms.filter((a) => a.alarmType === 'low_rest').length
  const matifCount = alarms.filter((a) => a.alarmType === 'matif_open').length
  const hedgeGapCount = alarms.filter((a) => a.alarmType === 'hedge_gap').length
  const dunningCount = alarms.filter((a) => a.alarmType === 'dunning_due').length
  const washoutCount = alarms.filter((a) => a.alarmType === 'washout_candidate').length
  const printCount = alarms.filter((a) => a.alarmType === 'print_missing').length
  const operationalStatus = normalizeOperationalStatus(
    alarms.length > 0 ? 'eskaliert' : 'abgeschlossen',
  )
  const contextSections = [
    {
      title: 'Alarmdruck',
      items: [
        { label: 'Ablauf', value: `${expiringCount}` },
        { label: 'Hedge', value: `${hedgeGapCount}` },
        { label: 'Mahnung', value: `${dunningCount}` },
      ],
    },
    {
      title: 'Sonderfaelle',
      items: [
        { label: 'MATIF offen', value: `${matifCount}` },
        { label: 'Washout', value: `${washoutCount}` },
        { label: 'Druck fehlt', value: `${printCount}` },
      ],
    },
  ]
  const timelineItems = [
    { label: alarms.length > 0 ? 'Aktive Alarme vorhanden' : 'Keine aktiven Alarme', detail: `${alarms.length} Alarmfaelle im Dashboard.` },
    { label: expiringCount > 0 ? 'Ablaufdruck aktiv' : 'Kein Ablaufdruck', detail: `${expiringCount} Kontrakte laufen kurzfristig aus.` },
    { label: hedgeGapCount + dunningCount > 0 ? 'Steuerungsdruck offen' : 'Fixierung und Mahnung stabil', detail: `${hedgeGapCount} Hedge-Luecken, ${dunningCount} Mahnfaelle.` },
  ]

  const alarmIcon = (type: AlarmItem['alarmType']): JSX.Element => {
    switch (type) {
      case 'expiring': return <Clock className="h-4 w-4 text-amber-600" />
      case 'low_rest': return <Package className="h-4 w-4 text-orange-600" />
      case 'matif_open': return <TrendingUp className="h-4 w-4 text-blue-600" />
      case 'hedge_gap': return <TrendingUp className="h-4 w-4 text-fuchsia-600" />
      case 'dunning_due': return <AlertTriangle className="h-4 w-4 text-red-600" />
      case 'market_valuation': return <AlertTriangle className="h-4 w-4 text-rose-700" />
      case 'washout_candidate': return <AlertTriangle className="h-4 w-4 text-amber-700" />
      case 'print_missing': return <Package className="h-4 w-4 text-slate-700" />
    }
  }

  const alarmBadge = (type: AlarmItem['alarmType']): JSX.Element => {
    const styles = {
      expiring: 'bg-amber-100 text-amber-800',
      low_rest: 'bg-orange-100 text-orange-800',
      matif_open: 'bg-blue-100 text-blue-800',
      hedge_gap: 'bg-fuchsia-100 text-fuchsia-800',
      dunning_due: 'bg-red-100 text-red-800',
      market_valuation: 'bg-rose-100 text-rose-800',
      washout_candidate: 'bg-amber-100 text-amber-800',
      print_missing: 'bg-slate-100 text-slate-800',
    }
    const labels = { expiring: 'Ablauf', low_rest: 'Restmenge', matif_open: 'MATIF', hedge_gap: 'Hedge', dunning_due: 'Mahnung', market_valuation: 'Marktwert', washout_candidate: 'Washout', print_missing: 'Druck' }
    return <Badge className={styles[type]}>{labels[type]}</Badge>
  }

  return (
    <div className="space-y-4 p-6">
      <OperationalCaseHeader
        title="Kontrakt-Alarme steuern"
        description="Ablauf, Hedge-Luecken, Mahnfaelle und Washout-Druck werden als ein Operatorraum priorisiert."
        status={operationalStatus}
        owner="Kontrakt / Handel"
        blocker={alarms.length > 0 ? 'Offene Alarmfaelle muessen vor weiterem Vertragsdruck priorisiert werden.' : null}
        nextAction={alarms.length > 0 ? 'Kritischste Alarmfaelle zuerst oeffnen und bearbeiten' : 'Kein unmittelbarer Eingriff erforderlich'}
        caseLabel="Kontrakt-Alarmraum"
        tags={['Kontrakte', 'Risiko']}
      />
      <div className="grid gap-4 lg:grid-cols-[1.35fr_1fr]">
        <OperationalTimeline title="Alarmverlauf" items={timelineItems} />
        <OperationalContextPanel title="Alarmkontext" sections={contextSections} />
      </div>
      <div className="flex items-center justify-between">
        <h1 className="text-xl font-semibold flex items-center gap-2">
          <AlertTriangle className="h-5 w-5 text-amber-600" />
          Kontrakt-Alarme
        </h1>
        <Button variant="outline" onClick={() => navigate('/kontrakte')}>Zur Kontraktliste</Button>
      </div>

      <div className="grid grid-cols-1 gap-4 md:grid-cols-7">
        <Card>
          <CardHeader className="pb-2">
            <CardTitle className="flex items-center gap-2 text-base">
              <Clock className="h-4 w-4 text-amber-600" />
              Ablaufende Kontrakte
            </CardTitle>
          </CardHeader>
          <CardContent>
            <div className="text-3xl font-bold text-amber-700">{expiringCount}</div>
            <p className="text-xs text-muted-foreground">Innerhalb 30 Tagen</p>
          </CardContent>
        </Card>

        <Card>
          <CardHeader className="pb-2">
            <CardTitle className="flex items-center gap-2 text-base">
              <Package className="h-4 w-4 text-orange-600" />
              Niedrige Restmenge
            </CardTitle>
          </CardHeader>
          <CardContent>
            <div className="text-3xl font-bold text-orange-700">{lowRestCount}</div>
            <p className="text-xs text-muted-foreground">Unter 10% Restmenge</p>
          </CardContent>
        </Card>

        <Card>
          <CardHeader className="pb-2">
            <CardTitle className="flex items-center gap-2 text-base">
              <TrendingUp className="h-4 w-4 text-blue-600" />
              MATIF offen
            </CardTitle>
          </CardHeader>
          <CardContent>
            <div className="text-3xl font-bold text-blue-700">{matifCount}</div>
            <p className="text-xs text-muted-foreground">Preisfixierung ausstehend</p>
          </CardContent>
        </Card>

        <Card>
          <CardHeader className="pb-2">
            <CardTitle className="flex items-center gap-2 text-base">
              <TrendingUp className="h-4 w-4 text-fuchsia-600" />
              Hedge-Luecken
            </CardTitle>
          </CardHeader>
          <CardContent>
            <div className="text-3xl font-bold text-fuchsia-700">{hedgeGapCount}</div>
            <p className="text-xs text-muted-foreground">Unter Zielabsicherung</p>
          </CardContent>
        </Card>

        <Card>
          <CardHeader className="pb-2">
            <CardTitle className="flex items-center gap-2 text-base">
              <AlertTriangle className="h-4 w-4 text-red-600" />
              Mahnfaellige
            </CardTitle>
          </CardHeader>
          <CardContent>
            <div className="text-3xl font-bold text-red-700">{dunningCount}</div>
            <p className="text-xs text-muted-foreground">Kontrakte mit Mahnbedarf</p>
          </CardContent>
        </Card>

        <Card>
          <CardHeader className="pb-2">
            <CardTitle className="flex items-center gap-2 text-base">
              <AlertTriangle className="h-4 w-4 text-amber-700" />
              Washout
            </CardTitle>
          </CardHeader>
          <CardContent>
            <div className="text-3xl font-bold text-amber-700">{washoutCount}</div>
            <p className="text-xs text-muted-foreground">Vorgemerkte Abschreibung / Washout</p>
          </CardContent>
        </Card>

        <Card>
          <CardHeader className="pb-2">
            <CardTitle className="flex items-center gap-2 text-base">
              <Package className="h-4 w-4 text-slate-700" />
              Druck fehlt
            </CardTitle>
          </CardHeader>
          <CardContent>
            <div className="text-3xl font-bold text-slate-700">{printCount}</div>
            <p className="text-xs text-muted-foreground">Formular- oder Kanalsteuerung offen</p>
          </CardContent>
        </Card>
      </div>

      {alarms.length === 0 && !query.isLoading && (
        <Card>
          <CardContent className="py-8 text-center text-muted-foreground">
            Keine aktiven Alarme. Alle offenen Kontrakte sind im gruenen Bereich.
          </CardContent>
        </Card>
      )}

      {alarms.length > 0 && (
        <Card>
          <CardContent className="pt-6">
            <div className="max-h-[500px] overflow-auto rounded border">
              <Table>
                <TableHeader>
                  <TableRow>
                    <TableHead className="w-10"></TableHead>
                    <TableHead>Alarm</TableHead>
                    <TableHead>Kontrakt-Nr.</TableHead>
                    <TableHead>Partner</TableHead>
                    <TableHead>Artikel</TableHead>
                    <TableHead>Gueltig bis</TableHead>
                    <TableHead className="text-right">Rest-Menge</TableHead>
                    <TableHead>Hinweis</TableHead>
                    <TableHead></TableHead>
                  </TableRow>
                </TableHeader>
                <TableBody>
                  {alarms.map((alarm, idx) => (
                    <TableRow key={`${alarm.contract_id}-${alarm.alarmType}-${idx}`}>
                      <TableCell>{alarmIcon(alarm.alarmType)}</TableCell>
                      <TableCell>{alarmBadge(alarm.alarmType)}</TableCell>
                      <TableCell className="font-mono">{alarm.contract_no}</TableCell>
                      <TableCell>{alarm.party_name || alarm.party_id}</TableCell>
                      <TableCell>{alarm.first_article_desc || alarm.first_article_id || '-'}</TableCell>
                      <TableCell>{alarm.valid_to ? new Date(alarm.valid_to).toLocaleDateString('de-DE') : '-'}</TableCell>
                      <TableCell className="text-right">{alarm.rest_quantity.toLocaleString('de-DE')} {alarm.unit}</TableCell>
                      <TableCell className="text-sm">{alarm.alarmText}</TableCell>
                      <TableCell>
                        <Button size="sm" variant="outline" onClick={() => navigate(`/kontrakte/${alarm.contract_id}`)}>
                          Oeffnen
                        </Button>
                      </TableCell>
                    </TableRow>
                  ))}
                </TableBody>
              </Table>
            </div>
          </CardContent>
        </Card>
      )}
    </div>
  )
}
