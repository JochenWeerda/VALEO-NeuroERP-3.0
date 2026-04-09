import { useMemo, useState } from 'react'
import { useNavigate } from 'react-router-dom'
import { useQuery } from '@tanstack/react-query'
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card'
import { Button } from '@/components/ui/button'
import { Badge } from '@/components/ui/badge'
import { Checkbox } from '@/components/ui/checkbox'
import { Table, TableBody, TableCell, TableHead, TableHeader, TableRow } from '@/components/ui/table'
import { apiClient } from '@/lib/api-client'
import { listKontrakte } from '@/lib/api/kontrakte'
import {
  AlertTriangle,
  ArrowDownRight,
  ArrowUpRight,
  Minus,
  ShieldAlert,
  ShieldCheck,
  TrendingDown,
  TrendingUp,
} from 'lucide-react'

type ArticlePosition = {
  article_id: string
  article_desc: string
  buy_contract_qty: number
  buy_moved_qty: number
  buy_rest_qty: number
  buy_avg_price: number | null
  buy_contract_count: number
  sell_contract_qty: number
  sell_moved_qty: number
  sell_rest_qty: number
  sell_avg_price: number | null
  sell_contract_count: number
  net_position: number
  signal: 'LONG' | 'SHORT' | 'BALANCED'
  spread: number | null
  coverage_pct: number | null
}

type PositionSummary = {
  positions: ArticlePosition[]
  total_short_articles: number
  total_long_articles: number
  total_balanced_articles: number
  most_critical: ArticlePosition | null
}

function fmt(n: number | null | undefined, decimals = 0): string {
  if (n == null) return '-'
  return n.toLocaleString('de-DE', { minimumFractionDigits: decimals, maximumFractionDigits: decimals })
}

function fmtEur(n: number | null | undefined): string {
  if (n == null) return '-'
  return `${n.toLocaleString('de-DE', { minimumFractionDigits: 2, maximumFractionDigits: 2 })} EUR`
}

function signalBadge(signal: string, coveragePct: number | null): JSX.Element {
  if (signal === 'SHORT') {
    const critical = coveragePct !== null && coveragePct < 50
    return (
      <Badge className={critical ? 'bg-red-600 text-white animate-pulse' : 'bg-red-100 text-red-800'}>
        <ArrowDownRight className="mr-1 h-3 w-3" />
        SHORT
      </Badge>
    )
  }
  if (signal === 'LONG') {
    return (
      <Badge className="bg-green-100 text-green-800">
        <ArrowUpRight className="mr-1 h-3 w-3" />
        LONG
      </Badge>
    )
  }
  return (
    <Badge className="bg-slate-100 text-slate-600">
      <Minus className="mr-1 h-3 w-3" />
      BALANCED
    </Badge>
  )
}

function coverageBadge(pct: number | null): JSX.Element {
  if (pct == null) return <span className="text-muted-foreground">-</span>
  let cls = 'bg-green-100 text-green-800'
  if (pct < 50) cls = 'bg-red-600 text-white font-bold'
  else if (pct < 80) cls = 'bg-red-100 text-red-800'
  else if (pct < 100) cls = 'bg-amber-100 text-amber-800'
  return <Badge className={cls}>{pct.toFixed(1)}%</Badge>
}

export default function KontraktPositionsmonitor(): JSX.Element {
  const navigate = useNavigate()
  const [includeDone, setIncludeDone] = useState(false)
  const [onlyShort, setOnlyShort] = useState(false)

  const query = useQuery({
    queryKey: ['kontrakte', 'positionen', includeDone],
    queryFn: () =>
      apiClient.get<PositionSummary>(
        `/api/v1/kontrakte/positionen?include_done=${includeDone}`
      ),
    refetchInterval: 30_000,
  })

  const contractMetaQuery = useQuery({
    queryKey: ['kontrakte', 'positionen', 'contract-master'],
    queryFn: () => listKontrakte({ include_done: includeDone, skip: 0, limit: 500 }),
    refetchInterval: 60_000,
  })

  const data = query.data ?? null
  const positions = useMemo(() => {
    if (!data) return []
    if (onlyShort) return data.positions.filter((p) => p.signal === 'SHORT')
    return data.positions
  }, [data, onlyShort])

  const shortCount = data?.total_short_articles ?? 0
  const longCount = data?.total_long_articles ?? 0
  const balancedCount = data?.total_balanced_articles ?? 0
  const critical = data?.most_critical ?? null
  const steeringItems = contractMetaQuery.data?.items ?? []
  const dispositionCount = steeringItems.filter((item) => Boolean(item.steering?.disposition_flag)).length
  const parityCount = steeringItems.filter((item) => Boolean(item.steering?.parity_code)).length
  const hedgeGapCount = steeringItems.filter((item) => (item.steering?.hedge_gap_pct ?? 0) > 0).length
  const negativeValuationCount = steeringItems.filter((item) => (item.steering?.market_valuation_eur ?? 0) < 0).length

  return (
    <div className="space-y-4 p-6">
      <div className="flex items-center justify-between">
        <h1 className="text-xl font-semibold flex items-center gap-2">
          <ShieldAlert className="h-5 w-5 text-red-600" />
          Rohwaren-Positionsmonitor
        </h1>
        <div className="flex items-center gap-3">
          <label className="flex items-center gap-2 text-sm">
            <Checkbox checked={includeDone} onCheckedChange={(v) => setIncludeDone(v === true)} />
            Erledigte einbeziehen
          </label>
          <label className="flex items-center gap-2 text-sm">
            <Checkbox checked={onlyShort} onCheckedChange={(v) => setOnlyShort(v === true)} />
            Nur Short-Positionen
          </label>
          <Button variant="outline" onClick={() => navigate('/kontrakte')}>Kontraktliste</Button>
          <Button variant="outline" onClick={() => navigate('/kontrakte/alarme')}>Alarme</Button>
        </div>
      </div>

      {critical && (
        <Card className="border-red-300 bg-red-50">
          <CardContent className="flex items-center gap-4 py-4">
            <AlertTriangle className="h-8 w-8 text-red-600 shrink-0" />
            <div>
              <p className="font-semibold text-red-800">
                Kritische Unterdeckung: {critical.article_desc} ({critical.article_id})
              </p>
              <p className="text-sm text-red-700">
                Netto-Position: {fmt(critical.net_position)} — Deckungsgrad: {critical.coverage_pct != null ? `${critical.coverage_pct.toFixed(1)}%` : 'n/a'}
                {' | '}Verkauf offen: {fmt(critical.sell_rest_qty)} — Einkauf gedeckt: {fmt(critical.buy_rest_qty)}
              </p>
            </div>
            <Button
              variant="outline"
              size="sm"
              className="ml-auto border-red-300 text-red-700 hover:bg-red-100"
              onClick={() => navigate(`/kontrakte?article_id=${critical.article_id}`)}
            >
              Kontrakte anzeigen
            </Button>
          </CardContent>
        </Card>
      )}

      <div className="grid grid-cols-1 gap-4 md:grid-cols-4">
        <Card>
          <CardHeader className="pb-2">
            <CardTitle className="flex items-center gap-2 text-base">
              <ShieldAlert className="h-4 w-4 text-red-600" />
              Short (unterdeckt)
            </CardTitle>
          </CardHeader>
          <CardContent>
            <div className="text-3xl font-bold text-red-700">{shortCount}</div>
            <p className="text-xs text-muted-foreground">Artikel mit Unterdeckung</p>
          </CardContent>
        </Card>

        <Card>
          <CardHeader className="pb-2">
            <CardTitle className="flex items-center gap-2 text-base">
              <ShieldCheck className="h-4 w-4 text-green-600" />
              Long (ueberdeckt)
            </CardTitle>
          </CardHeader>
          <CardContent>
            <div className="text-3xl font-bold text-green-700">{longCount}</div>
            <p className="text-xs text-muted-foreground">Artikel mit Ueberdeckung</p>
          </CardContent>
        </Card>

        <Card>
          <CardHeader className="pb-2">
            <CardTitle className="flex items-center gap-2 text-base">
              <Minus className="h-4 w-4 text-slate-500" />
              Balanced
            </CardTitle>
          </CardHeader>
          <CardContent>
            <div className="text-3xl font-bold text-slate-600">{balancedCount}</div>
            <p className="text-xs text-muted-foreground">Ausgeglichen</p>
          </CardContent>
        </Card>

        <Card>
          <CardHeader className="pb-2">
            <CardTitle className="flex items-center gap-2 text-base">
              {(critical?.spread ?? 0) >= 0 ? (
                <TrendingUp className="h-4 w-4 text-green-600" />
              ) : (
                <TrendingDown className="h-4 w-4 text-red-600" />
              )}
              Krit. Spread
            </CardTitle>
          </CardHeader>
          <CardContent>
            <div className={`text-3xl font-bold ${(critical?.spread ?? 0) >= 0 ? 'text-green-700' : 'text-red-700'}`}>
              {critical?.spread != null ? fmtEur(critical.spread) : '-'}
            </div>
            <p className="text-xs text-muted-foreground">VK-Preis minus EK-Preis (kritischster Artikel)</p>
          </CardContent>
        </Card>
      </div>

      <div className="grid grid-cols-1 gap-4 md:grid-cols-4">
        <Card>
          <CardHeader className="pb-2">
            <CardTitle className="text-base">Disposition</CardTitle>
          </CardHeader>
          <CardContent>
            <div className="text-2xl font-semibold">{dispositionCount}</div>
            <p className="text-xs text-muted-foreground">Kontrakte mit Dispositionskennzeichen</p>
          </CardContent>
        </Card>
        <Card>
          <CardHeader className="pb-2">
            <CardTitle className="text-base">Paritaet</CardTitle>
          </CardHeader>
          <CardContent>
            <div className="text-2xl font-semibold">{parityCount}</div>
            <p className="text-xs text-muted-foreground">Kontrakte mit Paritaetssteuerung</p>
          </CardContent>
        </Card>
        <Card>
          <CardHeader className="pb-2">
            <CardTitle className="text-base">Hedge-Luecken</CardTitle>
          </CardHeader>
          <CardContent>
            <div className="text-2xl font-semibold text-fuchsia-700">{hedgeGapCount}</div>
            <p className="text-xs text-muted-foreground">Unter Zielquote abgesicherte Kontrakte</p>
          </CardContent>
        </Card>
        <Card>
          <CardHeader className="pb-2">
            <CardTitle className="text-base">Negative Marktwerte</CardTitle>
          </CardHeader>
          <CardContent>
            <div className="text-2xl font-semibold text-red-700">{negativeValuationCount}</div>
            <p className="text-xs text-muted-foreground">Kontrakte mit negativer Marktbewertung</p>
          </CardContent>
        </Card>
      </div>

      <Card>
        <CardHeader>
          <CardTitle className="text-base">Positionsuebersicht pro Artikel</CardTitle>
        </CardHeader>
        <CardContent>
          <div className="max-h-[520px] overflow-auto rounded border">
            <Table>
              <TableHeader>
                <TableRow>
                  <TableHead>Signal</TableHead>
                  <TableHead>Artikel</TableHead>
                  <TableHead>Bezeichnung</TableHead>
                  <TableHead className="text-center">Deckung</TableHead>
                  <TableHead className="text-right">VK-Kontrakte</TableHead>
                  <TableHead className="text-right">VK offen (t)</TableHead>
                  <TableHead className="text-right">VK ø-Preis</TableHead>
                  <TableHead className="text-right">EK-Kontrakte</TableHead>
                  <TableHead className="text-right">EK offen (t)</TableHead>
                  <TableHead className="text-right">EK ø-Preis</TableHead>
                  <TableHead className="text-right">Netto (t)</TableHead>
                  <TableHead className="text-right">Spread</TableHead>
                </TableRow>
              </TableHeader>
              <TableBody>
                {positions.map((p) => (
                  <TableRow
                    key={p.article_id}
                    className={`cursor-pointer ${p.signal === 'SHORT' ? 'bg-red-50/50 hover:bg-red-100/60' : ''}`}
                    onDoubleClick={() => navigate(`/kontrakte?article_id=${p.article_id}`)}
                  >
                    <TableCell>{signalBadge(p.signal, p.coverage_pct)}</TableCell>
                    <TableCell className="font-mono text-xs">{p.article_id}</TableCell>
                    <TableCell className="font-medium">{p.article_desc}</TableCell>
                    <TableCell className="text-center">{coverageBadge(p.coverage_pct)}</TableCell>
                    <TableCell className="text-right">{p.sell_contract_count}</TableCell>
                    <TableCell className="text-right font-mono">{fmt(p.sell_rest_qty)}</TableCell>
                    <TableCell className="text-right font-mono">{fmtEur(p.sell_avg_price)}</TableCell>
                    <TableCell className="text-right">{p.buy_contract_count}</TableCell>
                    <TableCell className="text-right font-mono">{fmt(p.buy_rest_qty)}</TableCell>
                    <TableCell className="text-right font-mono">{fmtEur(p.buy_avg_price)}</TableCell>
                    <TableCell className={`text-right font-bold font-mono ${p.net_position < 0 ? 'text-red-700' : p.net_position > 0 ? 'text-green-700' : ''}`}>
                      {fmt(p.net_position)}
                    </TableCell>
                    <TableCell className={`text-right font-mono ${(p.spread ?? 0) < 0 ? 'text-red-600' : 'text-green-600'}`}>
                      {fmtEur(p.spread)}
                    </TableCell>
                  </TableRow>
                ))}
                {positions.length === 0 && !query.isLoading && (
                  <TableRow>
                    <TableCell colSpan={12} className="text-center py-8 text-muted-foreground">
                      {onlyShort ? 'Keine Short-Positionen gefunden — alle Artikel sind gedeckt.' : 'Keine offenen Kontraktpositionen.'}
                    </TableCell>
                  </TableRow>
                )}
              </TableBody>
            </Table>
          </div>
        </CardContent>
      </Card>

      <Card>
        <CardHeader>
          <CardTitle className="text-base">Legende</CardTitle>
        </CardHeader>
        <CardContent className="text-sm text-muted-foreground space-y-1">
          <p><strong>SHORT</strong> = Verkaufskontrakte uebersteigen Einkaufskontrakte → <span className="text-red-700 font-semibold">Unterdeckung / Boersenrisiko bei steigenden Preisen</span></p>
          <p><strong>LONG</strong> = Einkaufskontrakte uebersteigen Verkaufskontrakte → <span className="text-green-700">Ueberdeckung / Lagerrisiko bei fallenden Preisen</span></p>
          <p><strong>Deckungsgrad</strong> = EK-Restmenge / VK-Restmenge × 100% — unter 100% bedeutet Unterdeckung</p>
          <p><strong>Spread</strong> = Durchschnittlicher VK-Preis minus durchschnittlicher EK-Preis — positiv = Marge, negativ = Verlust</p>
          <p><strong>Netto (t)</strong> = EK-Restmenge minus VK-Restmenge — negativ = Short</p>
        </CardContent>
      </Card>
    </div>
  )
}
