import { useMemo, useState } from 'react'
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card'
import { Button } from '@/components/ui/button'
import { Input } from '@/components/ui/input'
import { Table, TableBody, TableCell, TableHead, TableHeader, TableRow } from '@/components/ui/table'
import { ErrorState } from '@/components/ErrorState'
import { useSaveSupplierRating, useSupplierRatings, type SupplierRating } from '@/lib/api/procurement-plus'

export default function LieferantenBewertungPage(): JSX.Element {
  const { data = [], isLoading, isError, error, refetch } = useSupplierRatings()
  const save = useSaveSupplierRating()
  const [search, setSearch] = useState('')

  const filtered = useMemo(
    () => data.filter((i) => i.supplier.toLowerCase().includes(search.toLowerCase())),
    [data, search],
  )

  if (isError) {
    return <ErrorState error={error as Error} onRetry={() => { void refetch() }} />
  }

  const handleNudgeScore = async (row: SupplierRating, delta: number) => {
    const overallScore = Math.max(1, Math.min(5, Number((row.overallScore + delta).toFixed(2))))
    await save.mutateAsync({ ...row, overallScore })
  }

  return (
    <div className="space-y-6 p-3 md:p-6">
      <Card>
        <CardHeader>
          <CardTitle>Lieferantenbewertung</CardTitle>
        </CardHeader>
        <CardContent className="space-y-4">
          <Input value={search} onChange={(e) => setSearch(e.target.value)} placeholder="Lieferant suchen" />
          {isLoading ? (
            <div className="text-sm text-muted-foreground">Lade Bewertungen ...</div>
          ) : (
            <Table>
              <TableHeader>
                <TableRow>
                  <TableHead>Lieferant</TableHead>
                  <TableHead className="text-right">Liefertreue</TableHead>
                  <TableHead className="text-right">Qualitaet</TableHead>
                  <TableHead className="text-right">Preis</TableHead>
                  <TableHead className="text-right">Service</TableHead>
                  <TableHead className="text-right">Gesamt</TableHead>
                  <TableHead className="text-right">Auftraege</TableHead>
                  <TableHead className="text-right">Aktion</TableHead>
                </TableRow>
              </TableHeader>
              <TableBody>
                {filtered.map((r) => (
                  <TableRow key={r.supplierId}>
                    <TableCell>{r.supplier}</TableCell>
                    <TableCell className="text-right">{r.onTimeDelivery.toFixed(1)}%</TableCell>
                    <TableCell className="text-right">{r.qualityScore.toFixed(2)}</TableCell>
                    <TableCell className="text-right">{r.priceScore.toFixed(2)}</TableCell>
                    <TableCell className="text-right">{r.serviceScore.toFixed(2)}</TableCell>
                    <TableCell className="text-right font-semibold">{r.overallScore.toFixed(2)}</TableCell>
                    <TableCell className="text-right">{r.totalOrders}</TableCell>
                    <TableCell className="text-right space-x-2">
                      <Button size="sm" variant="outline" onClick={() => { void handleNudgeScore(r, -0.1) }}>-0.1</Button>
                      <Button size="sm" onClick={() => { void handleNudgeScore(r, 0.1) }}>+0.1</Button>
                    </TableCell>
                  </TableRow>
                ))}
              </TableBody>
            </Table>
          )}
        </CardContent>
      </Card>
    </div>
  )
}
