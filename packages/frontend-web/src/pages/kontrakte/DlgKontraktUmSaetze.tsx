import { useState } from 'react'
import { useQuery } from '@tanstack/react-query'
import { Dialog, DialogContent, DialogFooter, DialogHeader, DialogTitle } from '@/components/ui/dialog'
import { Button } from '@/components/ui/button'
import { Input } from '@/components/ui/input'
import { Checkbox } from '@/components/ui/checkbox'
import { Table, TableBody, TableCell, TableHead, TableHeader, TableRow } from '@/components/ui/table'
import { listKontraktUmsaetze } from '@/lib/api/kontrakte'

type Props = {
  open: boolean
  onOpenChange: (_open: boolean) => void
  contractId: string
  contractNo: string
  validFrom?: string | null
  validTo?: string | null
  partner?: string | null
  quantityType?: string | null
  done?: boolean
  contractQty?: number
  restQty?: number
}

export default function DlgKontraktUmSaetze(props: Props): JSX.Element {
  const [articleId, setArticleId] = useState('')
  const [includeArchived, setIncludeArchived] = useState(false)
  const [onlyInvoiced, setOnlyInvoiced] = useState<boolean | undefined>(undefined)

  const q = useQuery({
    queryKey: ['kontrakte', 'umsaetze', props.contractId, articleId, includeArchived, onlyInvoiced, props.open],
    queryFn: () =>
      listKontraktUmsaetze(props.contractId, {
        article_id: articleId || undefined,
        include_archived: includeArchived,
        only_invoiced: onlyInvoiced,
      }),
    enabled: props.open,
  })

  return (
    <Dialog open={props.open} onOpenChange={props.onOpenChange}>
      <DialogContent className="max-w-6xl">
        <DialogHeader>
          <DialogTitle>Umsätze</DialogTitle>
        </DialogHeader>
        <div className="grid grid-cols-2 gap-3 text-sm md:grid-cols-4">
          <div><span className="text-muted-foreground">Kontrakt-Nr.</span><div className="font-semibold">{props.contractNo}</div></div>
          <div><span className="text-muted-foreground">gültig von</span><div>{props.validFrom ? new Date(props.validFrom).toLocaleDateString('de-DE') : '-'}</div></div>
          <div><span className="text-muted-foreground">gültig bis</span><div>{props.validTo ? new Date(props.validTo).toLocaleDateString('de-DE') : '-'}</div></div>
          <div><span className="text-muted-foreground">Partner</span><div>{props.partner || '-'}</div></div>
          <div><span className="text-muted-foreground">Mengen-Art</span><div>{props.quantityType || '-'}</div></div>
          <div><span className="text-muted-foreground">erledigt</span><div>{props.done ? 'Ja' : 'Nein'}</div></div>
          <div><span className="text-muted-foreground">Kontrakt-Menge</span><div>{props.contractQty ?? 0}</div></div>
          <div><span className="text-muted-foreground">Rest-Menge</span><div>{props.restQty ?? 0}</div></div>
        </div>

        <div className="grid grid-cols-1 gap-3 md:grid-cols-4">
          <label className="flex items-center gap-2 text-sm">
            <Checkbox checked={onlyInvoiced === false} onCheckedChange={(v) => setOnlyInvoiced(v === true ? false : undefined)} />
            noch nicht fakturierte Lieferungen
          </label>
          <label className="flex items-center gap-2 text-sm">
            <Checkbox checked={onlyInvoiced === true} onCheckedChange={(v) => setOnlyInvoiced(v === true ? true : undefined)} />
            fakturierte Lieferungen
          </label>
          <label className="flex items-center gap-2 text-sm">
            <Checkbox checked={includeArchived} onCheckedChange={(v) => setIncludeArchived(v === true)} />
            einschl. Archiv
          </label>
          <Input value={articleId} onChange={(e) => setArticleId(e.target.value)} placeholder="Artikel-Nr." />
        </div>

        <div className="max-h-[380px] overflow-auto rounded border">
          <Table>
            <TableHeader>
              <TableRow>
                <TableHead>Auftrag-Nr</TableHead>
                <TableHead>Rechnung-Nr</TableHead>
                <TableHead>Lieferschein-Nr</TableHead>
                <TableHead>Datum</TableHead>
                <TableHead>Artikel-Nr</TableHead>
                <TableHead>Menge</TableHead>
                <TableHead>Einh.-Preis</TableHead>
                <TableHead>Strecke-Nr</TableHead>
              </TableRow>
            </TableHeader>
            <TableBody>
              {(q.data?.items ?? []).map((row) => (
                <TableRow key={row.movement_id}>
                  <TableCell>{row.order_no || '-'}</TableCell>
                  <TableCell>{row.invoice_no || '-'}</TableCell>
                  <TableCell>{row.delivery_note_no || '-'}</TableCell>
                  <TableCell>{row.movement_date ? new Date(row.movement_date).toLocaleDateString('de-DE') : '-'}</TableCell>
                  <TableCell>{row.line_id || '-'}</TableCell>
                  <TableCell>{row.quantity}</TableCell>
                  <TableCell>{row.unit_price ?? '-'}</TableCell>
                  <TableCell>{row.route_no || '-'}</TableCell>
                </TableRow>
              ))}
            </TableBody>
          </Table>
        </div>
        <div className="text-right font-semibold">Verk.-Menge: {q.data?.verk_menge ?? 0}</div>
        <DialogFooter>
          <Button onClick={() => props.onOpenChange(false)}>Schließen</Button>
        </DialogFooter>
      </DialogContent>
    </Dialog>
  )
}
