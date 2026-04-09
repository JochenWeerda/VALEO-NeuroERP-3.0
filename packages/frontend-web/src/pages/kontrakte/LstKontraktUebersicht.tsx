import { useMemo, useRef, useState } from 'react'
import { useNavigate } from 'react-router-dom'
import { useQuery } from '@tanstack/react-query'
import { Button } from '@/components/ui/button'
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card'
import { Input } from '@/components/ui/input'
import { Label } from '@/components/ui/label'
import { Checkbox } from '@/components/ui/checkbox'
import { NativeSelect } from '@/components/ui/native-select'
import { Badge } from '@/components/ui/badge'
import { Table, TableBody, TableCell, TableHead, TableHeader, TableRow } from '@/components/ui/table'
import { listKontrakte } from '@/lib/api/kontrakte'
import { KeyboardShortcutBar } from '@/components/keyboard/KeyboardShortcutBar'
import { buildCoreMaskShortcuts, useKeyboardShortcuts } from '@/hooks/useKeyboardShortcuts'

const PAGE_SIZE = 50

function statusBadge(status: string): JSX.Element {
  const variants: Record<string, string> = {
    OFFEN: 'bg-green-100 text-green-800',
    ERLEDIGT: 'bg-slate-100 text-slate-600',
    STORNIERT: 'bg-red-100 text-red-700',
    GELOESCHT: 'bg-red-50 text-red-400 line-through',
  }
  return <Badge className={variants[status] ?? 'bg-slate-50'}>{status}</Badge>
}

export default function LstKontraktUebersicht(): JSX.Element {
  const navigate = useNavigate()
  const matchcodeRef = useRef<HTMLInputElement | null>(null)
  const [contractType, setContractType] = useState('')
  const [statusFilter, setStatusFilter] = useState('')
  const [dateFrom, setDateFrom] = useState('')
  const [dateTo, setDateTo] = useState('')
  const [contractNoFrom, setContractNoFrom] = useState('')
  const [contractNoTo, setContractNoTo] = useState('')
  const [matchcode1, setMatchcode1] = useState('')
  const [matchcode2, setMatchcode2] = useState('')
  const [onlyNoInput, setOnlyNoInput] = useState(false)
  const [alsoDone, setAlsoDone] = useState(false)
  const [sortDir, setSortDir] = useState<'asc' | 'desc'>('desc')
  const [page, setPage] = useState(0)

  const query = useQuery({
    queryKey: ['kontrakte', 'list', contractType, statusFilter, dateFrom, dateTo, matchcode1, matchcode2, alsoDone, sortDir, page],
    queryFn: () =>
      listKontrakte({
        contract_type: contractType || undefined,
        status: statusFilter || undefined,
        valid_from: dateFrom || undefined,
        valid_to: dateTo || undefined,
        query: `${matchcode1} ${matchcode2}`.trim() || undefined,
        include_done: alsoDone,
        skip: page * PAGE_SIZE,
        limit: PAGE_SIZE,
      }),
  })

  const engagementQuery = useQuery({
    queryKey: ['kontrakte', 'engagement', contractType, statusFilter, dateFrom, dateTo, matchcode1, matchcode2, alsoDone],
    queryFn: () =>
      listKontrakte({
        contract_type: contractType || undefined,
        status: statusFilter || undefined,
        valid_from: dateFrom || undefined,
        valid_to: dateTo || undefined,
        query: `${matchcode1} ${matchcode2}`.trim() || undefined,
        include_done: alsoDone,
        skip: 0,
        limit: 500,
      }),
  })

  const shortcuts = buildCoreMaskShortcuts({
    onNew: () => navigate('/kontrakte/neu'),
    onSearch: () => matchcodeRef.current?.focus(),
    onRefresh: () => { void query.refetch() },
  })
  useKeyboardShortcuts(shortcuts)

  const rows = useMemo(() => {
    const source = [...(query.data?.items ?? [])]
    if (contractNoFrom || contractNoTo) {
      const from = contractNoFrom || ''
      const to = contractNoTo || 'ZZZZZZZZ'
      return source.filter((r) => r.contract_no >= from && r.contract_no <= to)
    }
    return source.sort((a, b) => (sortDir === 'asc' ? a.contract_no.localeCompare(b.contract_no) : b.contract_no.localeCompare(a.contract_no)))
  }, [query.data, contractNoFrom, contractNoTo, sortDir])

  const steeringSummary = useMemo(() => {
    return {
      fallbackReady: rows.filter((row) => (row.steering?.alternate_articles?.length ?? 0) > 0 || row.steering?.fallback_route).length,
      writeoffCandidates: rows.filter((row) => row.steering?.writeoff_candidate).length,
      printReady: rows.filter((row) => row.steering?.print_ready).length,
      dunningDue: rows.filter((row) => row.steering?.dunning_candidate).length,
    }
  }, [rows])

  const engagement = useMemo(() => {
    const items = engagementQuery.data?.items ?? []
    const summary = {
      offeneVerkaufMenge: 0,
      offeneEinkaufMenge: 0,
      offeneZukaufMenge: 0,
      negativeMarktbewertung: 0,
      hedgeGapMenge: 0,
      topRisiken: [] as typeof items,
    }

    for (const item of items) {
      if (item.status !== 'OFFEN') continue
      if (item.contract_type === 'VERKAUF') summary.offeneVerkaufMenge += item.rest_quantity
      if (item.contract_type === 'EINKAUF') summary.offeneEinkaufMenge += item.rest_quantity
      if (item.contract_type === 'ZUKAUF') summary.offeneZukaufMenge += item.rest_quantity
      summary.negativeMarktbewertung += Math.min(0, item.steering?.market_valuation_eur ?? 0)
      if ((item.steering?.hedge_gap_pct ?? 0) > 0) {
        summary.hedgeGapMenge += item.rest_quantity
      }
    }

    summary.topRisiken = [...items]
      .filter((item) => item.status === 'OFFEN')
      .sort((a, b) => {
        const aScore =
          Math.abs(Math.min(0, a.steering?.market_valuation_eur ?? 0)) +
          (a.steering?.hedge_gap_pct ?? 0) * 10 +
          (a.steering?.dunning_candidate ? 1000 : 0) +
          (a.steering?.writeoff_candidate ? 500 : 0)
        const bScore =
          Math.abs(Math.min(0, b.steering?.market_valuation_eur ?? 0)) +
          (b.steering?.hedge_gap_pct ?? 0) * 10 +
          (b.steering?.dunning_candidate ? 1000 : 0) +
          (b.steering?.writeoff_candidate ? 500 : 0)
        return bScore - aScore
      })
      .slice(0, 5)

    return summary
  }, [engagementQuery.data])

  const totalPages = Math.ceil((query.data?.total ?? 0) / PAGE_SIZE)

  return (
    <div className="flex flex-col">
    <div className="space-y-4 p-6">
      <Card>
        <CardHeader>
          <CardTitle>Kontrakt-Uebersicht</CardTitle>
        </CardHeader>
        <CardContent className="space-y-4">
          <div className="grid grid-cols-1 gap-3 md:grid-cols-4">
            <Card>
              <CardContent className="py-4">
                <div className="text-xs uppercase tracking-wide text-muted-foreground">Ausweichbereit</div>
                <div className="mt-2 text-2xl font-semibold">{steeringSummary.fallbackReady}</div>
                <p className="mt-1 text-xs text-muted-foreground">Kontrakte mit Ausweichroute oder Alternativartikel</p>
              </CardContent>
            </Card>
            <Card>
              <CardContent className="py-4">
                <div className="text-xs uppercase tracking-wide text-muted-foreground">Washout / Abschreibung</div>
                <div className="mt-2 text-2xl font-semibold text-amber-700">{steeringSummary.writeoffCandidates}</div>
                <p className="mt-1 text-xs text-muted-foreground">Kontrakte mit vorgemerktem Abschreibungsbedarf</p>
              </CardContent>
            </Card>
            <Card>
              <CardContent className="py-4">
                <div className="text-xs uppercase tracking-wide text-muted-foreground">Druckbereit</div>
                <div className="mt-2 text-2xl font-semibold text-blue-700">{steeringSummary.printReady}</div>
                <p className="mt-1 text-xs text-muted-foreground">Formular und Kanal bereits definiert</p>
              </CardContent>
            </Card>
            <Card>
              <CardContent className="py-4">
                <div className="text-xs uppercase tracking-wide text-muted-foreground">Mahnfaellig</div>
                <div className="mt-2 text-2xl font-semibold text-red-700">{steeringSummary.dunningDue}</div>
                <p className="mt-1 text-xs text-muted-foreground">Offene Kontrakte mit Mahnindikator</p>
              </CardContent>
            </Card>
          </div>

          <div className="grid grid-cols-1 gap-3 md:grid-cols-4">
            <Card>
              <CardContent className="py-4">
                <div className="text-xs uppercase tracking-wide text-muted-foreground">VK-Exposure offen</div>
                <div className="mt-2 text-2xl font-semibold text-red-700">{engagement.offeneVerkaufMenge.toLocaleString('de-DE')}</div>
                <p className="mt-1 text-xs text-muted-foreground">Offene Verkaufsrestmenge</p>
              </CardContent>
            </Card>
            <Card>
              <CardContent className="py-4">
                <div className="text-xs uppercase tracking-wide text-muted-foreground">EK-/Zukauf-Exposure</div>
                <div className="mt-2 text-2xl font-semibold text-green-700">{(engagement.offeneEinkaufMenge + engagement.offeneZukaufMenge).toLocaleString('de-DE')}</div>
                <p className="mt-1 text-xs text-muted-foreground">Offene Einkaufs- und Zukaufsmengen</p>
              </CardContent>
            </Card>
            <Card>
              <CardContent className="py-4">
                <div className="text-xs uppercase tracking-wide text-muted-foreground">Negative Marktwerte</div>
                <div className="mt-2 text-2xl font-semibold text-amber-700">{engagement.negativeMarktbewertung.toLocaleString('de-DE', { minimumFractionDigits: 2, maximumFractionDigits: 2 })}</div>
                <p className="mt-1 text-xs text-muted-foreground">Aggregierte operative Marktbewertung in EUR</p>
              </CardContent>
            </Card>
            <Card>
              <CardContent className="py-4">
                <div className="text-xs uppercase tracking-wide text-muted-foreground">Hedge-Lueckenmenge</div>
                <div className="mt-2 text-2xl font-semibold text-fuchsia-700">{engagement.hedgeGapMenge.toLocaleString('de-DE')}</div>
                <p className="mt-1 text-xs text-muted-foreground">Restmenge mit offener Absicherungsluecke</p>
              </CardContent>
            </Card>
          </div>

          <div className="grid grid-cols-1 gap-3 md:grid-cols-5">
            <div className="space-y-1">
              <Label>Kontrakt-Art</Label>
              <NativeSelect
                value={contractType}
                onValueChange={setContractType}
                options={[
                  { value: 'VERKAUF', label: 'Verkauf' },
                  { value: 'ZUKAUF', label: 'Zukauf' },
                  { value: 'EINKAUF', label: 'Einkauf' },
                ]}
                placeholder="Alle"
              />
            </div>
            <div className="space-y-1">
              <Label>Status</Label>
              <NativeSelect
                value={statusFilter}
                onValueChange={(v) => { setStatusFilter(v); setPage(0) }}
                options={[
                  { value: 'OFFEN', label: 'Offen' },
                  { value: 'ERLEDIGT', label: 'Erledigt' },
                  { value: 'STORNIERT', label: 'Storniert' },
                ]}
                placeholder="Alle"
              />
            </div>
            <div className="space-y-1">
              <Label>Datum von</Label>
              <Input type="date" value={dateFrom} onChange={(e) => setDateFrom(e.target.value)} />
            </div>
            <div className="space-y-1">
              <Label>Datum bis</Label>
              <Input type="date" value={dateTo} onChange={(e) => setDateTo(e.target.value)} />
            </div>
            <div className="space-y-1">
              <Label>Sortierung</Label>
              <NativeSelect
                value={sortDir}
                onValueChange={(v) => setSortDir(v as 'asc' | 'desc')}
                options={[
                  { value: 'desc', label: 'Nr. absteigend' },
                  { value: 'asc', label: 'Nr. aufsteigend' },
                ]}
              />
            </div>
            <div className="space-y-1">
              <Label>von Kontrakt-Nr.</Label>
              <Input value={contractNoFrom} onChange={(e) => setContractNoFrom(e.target.value)} />
            </div>
            <div className="space-y-1">
              <Label>bis Kontrakt-Nr.</Label>
              <Input value={contractNoTo} onChange={(e) => setContractNoTo(e.target.value)} />
            </div>
            <div className="space-y-1">
              <Label>Matchcode 1</Label>
              <Input ref={matchcodeRef} value={matchcode1} onChange={(e) => setMatchcode1(e.target.value)} />
            </div>
            <div className="space-y-1">
              <Label>Matchcode 2</Label>
              <Input value={matchcode2} onChange={(e) => setMatchcode2(e.target.value)} />
            </div>
            <div className="flex flex-col justify-end gap-2">
              <label className="flex items-center gap-2">
                <Checkbox checked={onlyNoInput} onCheckedChange={(v) => setOnlyNoInput(v === true)} />
                <span className="text-sm">nur Nr.-Eingabe</span>
              </label>
              <label className="flex items-center gap-2">
                <Checkbox checked={alsoDone} onCheckedChange={(v) => setAlsoDone(v === true)} />
                <span className="text-sm">auch erledigte</span>
              </label>
            </div>
          </div>
          <div className="flex gap-2">
            <Button onClick={() => navigate('/kontrakte/neu')}>Neu</Button>
            <Button variant="outline" onClick={() => { const first = rows[0]; if (first) navigate(`/kontrakte/${first.contract_id}`) }}>Oeffnen</Button>
            <Button variant="outline" onClick={() => navigate('/kontrakte/positionen')}>Long/Short-Monitor</Button>
            <Button variant="outline" onClick={() => navigate('/kontrakte/alarme')}>Alarme</Button>
            <Button variant="outline" onClick={() => window.print()}>Drucken</Button>
            <Button variant="outline" onClick={() => {
              const lines = ['Kontrakt-Nr.;Kontr.-Datum;gueltig von;gueltig bis;Partner;Artikel;Bezeichnung;Kontrakt-Menge;Verk.-Menge;Rest-Menge;Einheit;Einh.-Preis;Status']
              rows.forEach((r) => lines.push(
                `${r.contract_no};${r.contract_date ?? ''};${r.valid_from ?? ''};${r.valid_to ?? ''};${r.party_name || r.party_id};${r.first_article_id ?? ''};${r.first_article_desc ?? ''};${r.total_quantity};${Math.max(0, r.total_quantity - r.rest_quantity)};${r.rest_quantity};${r.unit};${r.first_unit_price ?? ''};${r.status}`
              ))
              const blob = new Blob([lines.join('\n')], { type: 'text/csv;charset=utf-8;' })
              const a = document.createElement('a')
              a.href = URL.createObjectURL(blob)
              a.download = 'kontrakte-export.csv'
              a.click()
              URL.revokeObjectURL(a.href)
            }}>Export</Button>
          </div>
        </CardContent>
      </Card>

      <Card>
        <CardContent className="pt-6">
          <div className="mb-2 flex items-center justify-between text-sm text-muted-foreground">
            <span>{query.data?.total ?? 0} Kontrakte gefunden</span>
            {totalPages > 1 && (
              <div className="flex items-center gap-2">
                <Button variant="outline" size="sm" disabled={page === 0} onClick={() => setPage((p) => p - 1)}>Zurueck</Button>
                <span>Seite {page + 1} / {totalPages}</span>
                <Button variant="outline" size="sm" disabled={page >= totalPages - 1} onClick={() => setPage((p) => p + 1)}>Weiter</Button>
              </div>
            )}
          </div>
          <div className="max-h-[560px] overflow-auto rounded border">
            <Table>
              <TableHeader>
                <TableRow>
                  <TableHead>Kontrakt-Nr.</TableHead>
                  <TableHead>Status</TableHead>
                  <TableHead>Kontr.-Datum</TableHead>
                  <TableHead>gueltig von</TableHead>
                  <TableHead>gueltig bis</TableHead>
                  <TableHead>Partner</TableHead>
                  <TableHead>Artikel-Nr</TableHead>
                  <TableHead>Bezeichnung</TableHead>
                  <TableHead>Steuerung</TableHead>
                  <TableHead className="text-right">Kontrakt-Menge</TableHead>
                  <TableHead className="text-right">Verk.-Menge</TableHead>
                  <TableHead className="text-right">Rest-Menge</TableHead>
                  <TableHead>Einheit</TableHead>
                  <TableHead className="text-right">Einh.-Preis</TableHead>
                </TableRow>
              </TableHeader>
              <TableBody>
                {rows.map((row) => (
                  <TableRow key={row.contract_id} className="cursor-pointer" onDoubleClick={() => navigate(`/kontrakte/${row.contract_id}`)}>
                    <TableCell className="font-mono">{row.contract_no}</TableCell>
                    <TableCell>{statusBadge(row.status)}</TableCell>
                    <TableCell>{row.contract_date ? new Date(row.contract_date).toLocaleDateString('de-DE') : '-'}</TableCell>
                    <TableCell>{row.valid_from ? new Date(row.valid_from).toLocaleDateString('de-DE') : '-'}</TableCell>
                    <TableCell>{row.valid_to ? new Date(row.valid_to).toLocaleDateString('de-DE') : '-'}</TableCell>
                    <TableCell title={row.party_id}>{row.party_name || row.party_id}</TableCell>
                    <TableCell>{row.first_article_id ?? '-'}</TableCell>
                    <TableCell>{row.first_article_desc ?? '-'}</TableCell>
                    <TableCell>
                      <div className="flex flex-wrap gap-1">
                        {row.steering?.parity_code ? <Badge variant="outline">{row.steering.parity_code}</Badge> : null}
                        {row.steering?.disposition_flag ? <Badge variant="outline">{row.steering.disposition_flag}</Badge> : null}
                        {row.steering?.writeoff_candidate ? <Badge className="bg-amber-100 text-amber-800">Washout</Badge> : null}
                        {row.steering?.print_ready ? <Badge className="bg-blue-100 text-blue-800">Druck</Badge> : null}
                      </div>
                    </TableCell>
                    <TableCell className="text-right">{row.total_quantity.toLocaleString('de-DE')}</TableCell>
                    <TableCell className="text-right">{Math.max(0, row.total_quantity - row.rest_quantity).toLocaleString('de-DE')}</TableCell>
                    <TableCell className="text-right">{row.rest_quantity.toLocaleString('de-DE')}</TableCell>
                    <TableCell>{row.unit}</TableCell>
                    <TableCell className="text-right font-mono">{row.first_unit_price != null ? row.first_unit_price.toFixed(2) : '-'}</TableCell>
                  </TableRow>
                ))}
              </TableBody>
            </Table>
          </div>
          {totalPages > 1 && (
            <div className="mt-2 flex items-center justify-end gap-2 text-sm">
              <Button variant="outline" size="sm" disabled={page === 0} onClick={() => setPage((p) => p - 1)}>Zurueck</Button>
              <span>Seite {page + 1} / {totalPages}</span>
              <Button variant="outline" size="sm" disabled={page >= totalPages - 1} onClick={() => setPage((p) => p + 1)}>Weiter</Button>
            </div>
          )}
        </CardContent>
      </Card>

      <Card>
        <CardHeader>
          <CardTitle>Top-Risiko-Kontrakte</CardTitle>
        </CardHeader>
        <CardContent>
          <div className="max-h-[320px] overflow-auto rounded border">
            <Table>
              <TableHeader>
                <TableRow>
                  <TableHead>Kontrakt</TableHead>
                  <TableHead>Partner</TableHead>
                  <TableHead className="text-right">Rest-Menge</TableHead>
                  <TableHead className="text-right">Marktwert</TableHead>
                  <TableHead className="text-right">Hedge-Luecke</TableHead>
                  <TableHead>Flags</TableHead>
                </TableRow>
              </TableHeader>
              <TableBody>
                {engagement.topRisiken.map((row) => (
                  <TableRow key={`risk-${row.contract_id}`} className="cursor-pointer" onDoubleClick={() => navigate(`/kontrakte/${row.contract_id}`)}>
                    <TableCell className="font-mono">{row.contract_no}</TableCell>
                    <TableCell>{row.party_name || row.party_id}</TableCell>
                    <TableCell className="text-right">{row.rest_quantity.toLocaleString('de-DE')}</TableCell>
                    <TableCell className="text-right font-mono">{(row.steering?.market_valuation_eur ?? 0).toLocaleString('de-DE', { minimumFractionDigits: 2, maximumFractionDigits: 2 })}</TableCell>
                    <TableCell className="text-right">{row.steering?.hedge_gap_pct?.toFixed(1) ?? '-'}%</TableCell>
                    <TableCell>
                      <div className="flex flex-wrap gap-1">
                        {row.steering?.dunning_candidate ? <Badge className="bg-red-100 text-red-800">Mahnung</Badge> : null}
                        {row.steering?.writeoff_candidate ? <Badge className="bg-amber-100 text-amber-800">Washout</Badge> : null}
                        {!row.steering?.print_ready ? <Badge variant="outline">Druck offen</Badge> : null}
                      </div>
                    </TableCell>
                  </TableRow>
                ))}
                {engagement.topRisiken.length === 0 ? (
                  <TableRow>
                    <TableCell colSpan={6} className="py-6 text-center text-sm text-muted-foreground">
                      Kein offenes Risiko-Exposure im aktuellen Filter.
                    </TableCell>
                  </TableRow>
                ) : null}
              </TableBody>
            </Table>
          </div>
        </CardContent>
      </Card>
    </div>
    <KeyboardShortcutBar shortcuts={shortcuts} />
    </div>
  )
}
