import { useMemo, useState } from 'react'
import { useQuery } from '@tanstack/react-query'
import { Dialog, DialogContent, DialogFooter, DialogHeader, DialogTitle } from '@/components/ui/dialog'
import { Button } from '@/components/ui/button'
import { Input } from '@/components/ui/input'
import { Checkbox } from '@/components/ui/checkbox'
import { Table, TableBody, TableCell, TableHead, TableHeader, TableRow } from '@/components/ui/table'
import { lookupVerkaufKontrakte } from '@/lib/api/kontrakte'

type LookupItem = {
  contract_id: string
  line_id: string
  contract_no: string
  position_no: number
  date?: string | null
  name: string
  valid_from?: string | null
  valid_to?: string | null
  article_id: string
  bezeichnung: string
}

type Props = {
  open: boolean
  onOpenChange: (_open: boolean) => void
  onSelect: (_item: LookupItem) => void
}

export default function DlgAuswahlVerkaufKontrakte({ open, onOpenChange, onSelect }: Props): JSX.Element {
  const [query, setQuery] = useState('')
  const [onlyOpen, setOnlyOpen] = useState(true)
  const [selected, setSelected] = useState<LookupItem | null>(null)

  const lookupQuery = useQuery({
    queryKey: ['kontrakte', 'lookup-verkauf', query, onlyOpen, open],
    queryFn: () => lookupVerkaufKontrakte({ query, only_open: onlyOpen, limit: 100 }),
    enabled: open,
  })

  const items = useMemo(() => lookupQuery.data?.items ?? [], [lookupQuery.data])

  return (
    <Dialog open={open} onOpenChange={onOpenChange}>
      <DialogContent className="max-w-6xl">
        <DialogHeader>
          <DialogTitle>Auswahl Verkaufskontrakte</DialogTitle>
        </DialogHeader>
        <div className="flex items-center gap-4">
          <Input
            value={query}
            onChange={(e) => setQuery(e.target.value)}
            placeholder="Suche Kontrakt-Nr., Name, Artikel ..."
          />
          <label className="flex items-center gap-2 text-sm">
            <Checkbox checked={onlyOpen} onCheckedChange={(v) => setOnlyOpen(v === true)} />
            nur unerledigte Kontrakte
          </label>
        </div>
        <div className="max-h-[420px] overflow-auto rounded border">
          <Table>
            <TableHeader>
              <TableRow>
                <TableHead>Kontrakt-Nr.</TableHead>
                <TableHead>Pos.-Nr</TableHead>
                <TableHead>Datum</TableHead>
                <TableHead>Name</TableHead>
                <TableHead>gültig von</TableHead>
                <TableHead>gültig bis</TableHead>
                <TableHead>Artikel-Nr</TableHead>
                <TableHead>Bezeichnung</TableHead>
              </TableRow>
            </TableHeader>
            <TableBody>
              {items.map((item) => (
                <TableRow
                  key={`${item.contract_id}:${item.line_id}`}
                  className={selected?.line_id === item.line_id ? 'bg-green-50' : 'cursor-pointer'}
                  onClick={() => setSelected(item)}
                >
                  <TableCell className="font-mono">{item.contract_no}</TableCell>
                  <TableCell>{item.position_no}</TableCell>
                  <TableCell>{item.date ? new Date(item.date).toLocaleDateString('de-DE') : '-'}</TableCell>
                  <TableCell>{item.name}</TableCell>
                  <TableCell>{item.valid_from ? new Date(item.valid_from).toLocaleDateString('de-DE') : '-'}</TableCell>
                  <TableCell>{item.valid_to ? new Date(item.valid_to).toLocaleDateString('de-DE') : '-'}</TableCell>
                  <TableCell>{item.article_id}</TableCell>
                  <TableCell>{item.bezeichnung}</TableCell>
                </TableRow>
              ))}
            </TableBody>
          </Table>
        </div>
        <DialogFooter>
          <Button variant="outline" onClick={() => onOpenChange(false)}>Abbrechen</Button>
          <Button
            disabled={!selected}
            onClick={() => {
              if (!selected) return
              onSelect(selected)
              onOpenChange(false)
            }}
          >
            OK
          </Button>
        </DialogFooter>
      </DialogContent>
    </Dialog>
  )
}
