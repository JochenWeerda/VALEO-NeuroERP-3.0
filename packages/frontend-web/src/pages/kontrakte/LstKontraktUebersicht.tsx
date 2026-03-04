import { useMemo, useState } from 'react'
import { useNavigate } from 'react-router-dom'
import { useQuery } from '@tanstack/react-query'
import { Button } from '@/components/ui/button'
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card'
import { Input } from '@/components/ui/input'
import { Label } from '@/components/ui/label'
import { Checkbox } from '@/components/ui/checkbox'
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from '@/components/ui/select'
import { Table, TableBody, TableCell, TableHead, TableHeader, TableRow } from '@/components/ui/table'
import { listKontrakte } from '@/lib/api/kontrakte'

export default function LstKontraktUebersicht(): JSX.Element {
  const navigate = useNavigate()
  const [contractType, setContractType] = useState('')
  const [dateFrom, setDateFrom] = useState('')
  const [dateTo, setDateTo] = useState('')
  const [contractNoFrom, setContractNoFrom] = useState('')
  const [contractNoTo, setContractNoTo] = useState('')
  const [matchcode1, setMatchcode1] = useState('')
  const [matchcode2, setMatchcode2] = useState('')
  const [onlyNoInput, setOnlyNoInput] = useState(false)
  const [alsoDone, setAlsoDone] = useState(false)
  const [sortDir, setSortDir] = useState<'asc' | 'desc'>('desc')

  const query = useQuery({
    queryKey: ['kontrakte', 'list', contractType, dateFrom, dateTo, matchcode1, matchcode2, alsoDone, sortDir],
    queryFn: () =>
      listKontrakte({
        contract_type: contractType || undefined,
        valid_from: dateFrom || undefined,
        valid_to: dateTo || undefined,
        query: `${matchcode1} ${matchcode2}`.trim() || undefined,
        include_done: alsoDone,
        skip: 0,
        limit: 200,
      }),
  })

  const rows = useMemo(() => {
    const source = [...(query.data?.items ?? [])]
    if (contractNoFrom || contractNoTo) {
      const from = contractNoFrom || ''
      const to = contractNoTo || 'ZZZZZZZZ'
      return source.filter((r) => r.contract_no >= from && r.contract_no <= to)
    }
    return source.sort((a, b) => (sortDir === 'asc' ? a.contract_no.localeCompare(b.contract_no) : b.contract_no.localeCompare(a.contract_no)))
  }, [query.data, contractNoFrom, contractNoTo, sortDir])

  return (
    <div className="space-y-4 p-6">
      <Card>
        <CardHeader>
          <CardTitle>LstKontraktUebersicht</CardTitle>
        </CardHeader>
        <CardContent className="space-y-4">
          <div className="grid grid-cols-1 gap-3 md:grid-cols-4">
            <div className="space-y-1">
              <Label>Kontrakt-Art</Label>
              <Select value={contractType} onValueChange={setContractType}>
                <SelectTrigger><SelectValue placeholder="Alle" /></SelectTrigger>
                <SelectContent>
                  <SelectItem value="VERKAUF">Verkaufs-Kontrakte</SelectItem>
                  <SelectItem value="ZUKAUF">Zukauf</SelectItem>
                  <SelectItem value="EINKAUF">Einkauf</SelectItem>
                </SelectContent>
              </Select>
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
              <Select value={sortDir} onValueChange={(v: any) => setSortDir(v)}>
                <SelectTrigger><SelectValue /></SelectTrigger>
                <SelectContent>
                  <SelectItem value="desc">Kontrakt-Nr. absteigend</SelectItem>
                  <SelectItem value="asc">Kontrakt-Nr. aufsteigend</SelectItem>
                </SelectContent>
              </Select>
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
              <Input value={matchcode1} onChange={(e) => setMatchcode1(e.target.value)} />
            </div>
            <div className="space-y-1">
              <Label>Matchcode 2</Label>
              <Input value={matchcode2} onChange={(e) => setMatchcode2(e.target.value)} />
            </div>
            <label className="flex items-center gap-2">
              <Checkbox checked={onlyNoInput} onCheckedChange={(v) => setOnlyNoInput(v === true)} />
              <span className="text-sm">nur Kontrakt-Nr.-Eingabe</span>
            </label>
            <label className="flex items-center gap-2">
              <Checkbox checked={alsoDone} onCheckedChange={(v) => setAlsoDone(v === true)} />
              <span className="text-sm">auch erledigte</span>
            </label>
          </div>
          <div className="flex gap-2">
            <Button onClick={() => navigate('/kontrakte/neu')}>Neu</Button>
            <Button variant="outline" onClick={() => { const first = rows[0]; if (first) navigate(`/kontrakte/${first.contract_id}`) }}>Öffnen</Button>
            <Button variant="outline" onClick={() => window.print()}>Drucken</Button>
            <Button variant="outline" onClick={() => {
              const lines = ['Kontrakt-Nr.;Kontr.-Datum;gültig von;gültig bis;Kunde/Lieferant;Kontrakt-Menge;Rest-Menge;Einheit;Einh.-Preis']
              rows.forEach((r) => lines.push(`${r.contract_no};${r.contract_date ?? ''};${r.valid_from ?? ''};${r.valid_to ?? ''};${r.party_id};${r.total_quantity};${r.rest_quantity};${r.unit};`))
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
          <div className="max-h-[560px] overflow-auto rounded border">
            <Table>
              <TableHeader>
                <TableRow>
                  <TableHead>Kontrakt-Nr.</TableHead>
                  <TableHead>Kontr.-Datum</TableHead>
                  <TableHead>gültig von</TableHead>
                  <TableHead>gültig bis</TableHead>
                  <TableHead>Kunden-/Lieferanten-Name</TableHead>
                  <TableHead>Artikel-Nr</TableHead>
                  <TableHead>Bezeichnung</TableHead>
                  <TableHead>Kontrakt-Menge</TableHead>
                  <TableHead>Verk.-Menge</TableHead>
                  <TableHead>Rest-Menge</TableHead>
                  <TableHead>Einheit</TableHead>
                  <TableHead>Einh.-Preis</TableHead>
                </TableRow>
              </TableHeader>
              <TableBody>
                {rows.map((row) => (
                  <TableRow key={row.contract_id} className="cursor-pointer" onDoubleClick={() => navigate(`/kontrakte/${row.contract_id}`)}>
                    <TableCell className="font-mono">{row.contract_no}</TableCell>
                    <TableCell>{row.contract_date ? new Date(row.contract_date).toLocaleDateString('de-DE') : '-'}</TableCell>
                    <TableCell>{row.valid_from ? new Date(row.valid_from).toLocaleDateString('de-DE') : '-'}</TableCell>
                    <TableCell>{row.valid_to ? new Date(row.valid_to).toLocaleDateString('de-DE') : '-'}</TableCell>
                    <TableCell>{row.party_id}</TableCell>
                    <TableCell>-</TableCell>
                    <TableCell>-</TableCell>
                    <TableCell>{row.total_quantity}</TableCell>
                    <TableCell>{Math.max(0, row.total_quantity - row.rest_quantity)}</TableCell>
                    <TableCell>{row.rest_quantity}</TableCell>
                    <TableCell>{row.unit}</TableCell>
                    <TableCell>-</TableCell>
                  </TableRow>
                ))}
              </TableBody>
            </Table>
          </div>
        </CardContent>
      </Card>
    </div>
  )
}
