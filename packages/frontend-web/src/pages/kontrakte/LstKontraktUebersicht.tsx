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

  const totalPages = Math.ceil((query.data?.total ?? 0) / PAGE_SIZE)

  return (
    <div className="flex flex-col">
    <div className="space-y-4 p-6">
      <Card>
        <CardHeader>
          <CardTitle>Kontrakt-Uebersicht</CardTitle>
        </CardHeader>
        <CardContent className="space-y-4">
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
    </div>
    <KeyboardShortcutBar shortcuts={shortcuts} />
    </div>
  )
}
