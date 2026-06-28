import { useQuery } from '@tanstack/react-query'
import { useNavigate } from '@/app/routing/typed-router'
import {
  Dialog,
  DialogContent,
  DialogHeader,
  DialogTitle,
  DialogFooter,
} from '@/components/ui/dialog'
import { Button } from '@/components/ui/button'
import { Tabs, TabsContent, TabsList, TabsTrigger } from '@/components/ui/tabs'
import { Table, TableBody, TableCell, TableHead, TableHeader, TableRow } from '@/components/ui/table'
import { getCellDrilldown, requestOverride } from '@/lib/api/positions'
import { toast } from '@/hooks/use-toast'

type DlgPositionDetailsProps = {
  articleId: string
  periodKey: string
  branchId?: string
  asOfDate?: string
  periodMode?: string
  viewMode?: string
  open: boolean
  onOpenChange: (open: boolean) => void
}

export function DlgPositionDetails({
  articleId,
  periodKey,
  branchId,
  asOfDate,
  periodMode,
  viewMode,
  open,
  onOpenChange,
}: DlgPositionDetailsProps): JSX.Element {
  const navigate = useNavigate()

  const { data: drill, isLoading, error } = useQuery({
    queryKey: ['positions', 'cell', articleId, periodKey, branchId, asOfDate, periodMode, viewMode],
    queryFn: () =>
      getCellDrilldown(articleId, periodKey, {
        branch_id: branchId,
        as_of_date: asOfDate ?? undefined,
        period_mode: periodMode,
        view_mode: viewMode,
      }),
    enabled: open && !!articleId && !!periodKey,
  })

  const handleEinkaufErgaenzen = () => {
    onOpenChange(false)
    navigate('/kontrakte/neu')
  }

  const handleVerkaufUmdisponieren = () => {
    onOpenChange(false)
    navigate('/kontrakte?typ=VERKAUF')
  }

  const handleFreigabeAnfordern = async () => {
    try {
      await requestOverride({
        branch_id: branchId ?? undefined,
        article_id: articleId,
        period_key: periodKey,
        reason: `Freigabe für Short-Position ${articleId} / ${periodKey}`,
      })
      onOpenChange(false)
    } catch (_rawErr: unknown) {
      const e = _rawErr as { response?: { data?: { detail?: string } }; message?: string; name?: string }
      toast({ variant: 'destructive', title: 'Freigabe-Anforderung fehlgeschlagen', description: e?.message })
    }
  }

  return (
    <Dialog open={open} onOpenChange={onOpenChange}>
      <DialogContent className="max-w-4xl max-h-[90vh] overflow-y-auto">
        <DialogHeader>
          <DialogTitle>
            Position: {articleId} / {periodKey}
          </DialogTitle>
        </DialogHeader>
        {isLoading && <p className="text-muted-foreground">Lade Details…</p>}
        {error && <p className="text-destructive">Fehler: {String(error)}</p>}
        {drill && (
          <>
            <div className="grid grid-cols-2 gap-2 text-sm">
              <p><strong>Niederlassung:</strong> {drill.branch_id ?? '-'}</p>
              <p><strong>Stichtag:</strong> {asOfDate ?? '-'}</p>
              <p><strong>Einkauf offen:</strong> {drill.qty_buy_open.toLocaleString('de-DE')} t</p>
              <p><strong>Verkauf offen:</strong> {drill.qty_sell_open.toLocaleString('de-DE')} t</p>
              <p><strong>Netto:</strong> {drill.qty_net.toLocaleString('de-DE')} t</p>
              <p><strong>Status:</strong> {drill.severity}</p>
            </div>
            <Tabs defaultValue="ek">
              <TabsList>
                <TabsTrigger value="ek">Einkauf offen</TabsTrigger>
                <TabsTrigger value="vk">Verkauf offen</TabsTrigger>
                <TabsTrigger value="movements">Bewegungen</TabsTrigger>
                <TabsTrigger value="verursacher">Top Verursacher</TabsTrigger>
              </TabsList>
              <TabsContent value="ek">
                <Table>
                  <TableHeader>
                    <TableRow>
                      <TableHead>Kontrakt-Nr</TableHead>
                      <TableHead>Lieferant</TableHead>
                      <TableHead className="text-right">Kontraktmenge</TableHead>
                      <TableHead className="text-right">geliefert</TableHead>
                      <TableHead className="text-right">Rest</TableHead>
                      <TableHead>gültig bis</TableHead>
                    </TableRow>
                  </TableHeader>
                  <TableBody>
                    {drill.buy_contracts.map((c) => (
                      <TableRow key={c.contract_id}>
                        <TableCell>{c.contract_no}</TableCell>
                        <TableCell>{c.party_id}</TableCell>
                        <TableCell className="text-right">{c.qty_contract.toLocaleString('de-DE')}</TableCell>
                        <TableCell className="text-right">{c.qty_delivered.toLocaleString('de-DE')}</TableCell>
                        <TableCell className="text-right">{c.qty_rest.toLocaleString('de-DE')}</TableCell>
                        <TableCell>{c.valid_to ? new Date(c.valid_to).toLocaleDateString('de-DE') : '-'}</TableCell>
                      </TableRow>
                    ))}
                  </TableBody>
                </Table>
              </TabsContent>
              <TabsContent value="vk">
                <Table>
                  <TableHeader>
                    <TableRow>
                      <TableHead>Kontrakt-Nr</TableHead>
                      <TableHead>Kunde</TableHead>
                      <TableHead className="text-right">Kontraktmenge</TableHead>
                      <TableHead className="text-right">geliefert</TableHead>
                      <TableHead className="text-right">Rest</TableHead>
                      <TableHead>gültig bis</TableHead>
                    </TableRow>
                  </TableHeader>
                  <TableBody>
                    {drill.sell_contracts.map((c) => (
                      <TableRow key={c.contract_id}>
                        <TableCell>{c.contract_no}</TableCell>
                        <TableCell>{c.party_id}</TableCell>
                        <TableCell className="text-right">{c.qty_contract.toLocaleString('de-DE')}</TableCell>
                        <TableCell className="text-right">{c.qty_delivered.toLocaleString('de-DE')}</TableCell>
                        <TableCell className="text-right">{c.qty_rest.toLocaleString('de-DE')}</TableCell>
                        <TableCell>{c.valid_to ? new Date(c.valid_to).toLocaleDateString('de-DE') : '-'}</TableCell>
                      </TableRow>
                    ))}
                  </TableBody>
                </Table>
              </TabsContent>
              <TabsContent value="movements">
                <Table>
                  <TableHeader>
                    <TableRow>
                      <TableHead>Datum</TableHead>
                      <TableHead>Kontrakt</TableHead>
                      <TableHead>Lieferschein</TableHead>
                      <TableHead className="text-right">Menge</TableHead>
                    </TableRow>
                  </TableHeader>
                  <TableBody>
                    {drill.movements.slice(0, 50).map((m) => (
                      <TableRow key={m.movement_id}>
                        <TableCell>{m.movement_date ? new Date(m.movement_date).toLocaleDateString('de-DE') : '-'}</TableCell>
                        <TableCell>{m.contract_id}</TableCell>
                        <TableCell>{m.delivery_note_no ?? '-'}</TableCell>
                        <TableCell className="text-right">{m.quantity.toLocaleString('de-DE')}</TableCell>
                      </TableRow>
                    ))}
                  </TableBody>
                </Table>
              </TabsContent>
              <TabsContent value="verursacher">
                <Table>
                  <TableHeader>
                    <TableRow>
                      <TableHead>Kontrakt-Nr</TableHead>
                      <TableHead>Typ</TableHead>
                      <TableHead className="text-right">Rest</TableHead>
                      <TableHead className="text-right">Anteil %</TableHead>
                    </TableRow>
                  </TableHeader>
                  <TableBody>
                    {drill.top_causers.map((t) => (
                      <TableRow key={t.contract_id}>
                        <TableCell>{t.contract_no}</TableCell>
                        <TableCell>{t.contract_type}</TableCell>
                        <TableCell className="text-right">{t.qty_rest.toLocaleString('de-DE')}</TableCell>
                        <TableCell className="text-right">{t.share_pct != null ? t.share_pct.toFixed(1) : '-'}</TableCell>
                      </TableRow>
                    ))}
                  </TableBody>
                </Table>
              </TabsContent>
            </Tabs>
          </>
        )}
        <DialogFooter>
          <Button variant="outline" onClick={handleEinkaufErgaenzen}>
            Einkauf ergänzen
          </Button>
          <Button variant="outline" onClick={handleVerkaufUmdisponieren}>
            Verkauf umdisponieren
          </Button>
          <Button variant="outline" onClick={handleFreigabeAnfordern}>
            Freigabe anfordern
          </Button>
          <Button onClick={() => onOpenChange(false)}>Schließen</Button>
        </DialogFooter>
      </DialogContent>
    </Dialog>
  )
}
