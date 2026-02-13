import { useState } from 'react'
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card'
import { Button } from '@/components/ui/button'
import { Input } from '@/components/ui/input'
import { Table, TableBody, TableCell, TableHead, TableHeader, TableRow } from '@/components/ui/table'
import { ErrorState } from '@/components/ErrorState'
import {
  useCreateServiceEntrySheet,
  useServiceEntrySheets,
  useUpdateServiceEntrySheet,
  type ServiceEntrySheet,
} from '@/lib/api/procurement-plus'

export default function ServiceEntrySheetsPage(): JSX.Element {
  const { data = [], isLoading, isError, error, refetch } = useServiceEntrySheets()
  const createSes = useCreateServiceEntrySheet()
  const updateSes = useUpdateServiceEntrySheet()

  const [supplierId, setSupplierId] = useState('')
  const [description, setDescription] = useState('')
  const [quantity, setQuantity] = useState(1)
  const [unitPrice, setUnitPrice] = useState(0)

  if (isError) {
    return <ErrorState error={error as Error} onRetry={() => { void refetch() }} />
  }

  const handleCreate = async () => {
    await createSes.mutateAsync({ supplierId, description, quantity, unitPrice, status: 'ERFASST' })
    setDescription('')
    setQuantity(1)
    setUnitPrice(0)
  }

  const handleApprove = async (item: ServiceEntrySheet) => {
    await updateSes.mutateAsync({ id: item.id, data: { status: 'FREIGEGEBEN' } })
  }

  return (
    <div className="space-y-6 p-3 md:p-6">
      <Card>
        <CardHeader>
          <CardTitle>Service Entry Sheets</CardTitle>
        </CardHeader>
        <CardContent className="space-y-3">
          <div className="grid grid-cols-1 gap-2 md:grid-cols-4">
            <Input placeholder="Supplier ID" value={supplierId} onChange={(e) => setSupplierId(e.target.value)} />
            <Input placeholder="Beschreibung" value={description} onChange={(e) => setDescription(e.target.value)} />
            <Input type="number" value={quantity} onChange={(e) => setQuantity(Number(e.target.value) || 0)} />
            <Input type="number" value={unitPrice} onChange={(e) => setUnitPrice(Number(e.target.value) || 0)} />
          </div>
          <Button onClick={() => { void handleCreate() }} disabled={createSes.isPending || !supplierId || !description}>
            SES anlegen
          </Button>
        </CardContent>
      </Card>

      <Card>
        <CardHeader>
          <CardTitle>SES Uebersicht</CardTitle>
        </CardHeader>
        <CardContent>
          {isLoading ? (
            <div className="text-sm text-muted-foreground">Lade Service Entry Sheets ...</div>
          ) : (
            <Table>
              <TableHeader>
                <TableRow>
                  <TableHead>Nummer</TableHead>
                  <TableHead>Lieferant</TableHead>
                  <TableHead>Leistung</TableHead>
                  <TableHead className="text-right">Menge</TableHead>
                  <TableHead className="text-right">Betrag</TableHead>
                  <TableHead>Status</TableHead>
                  <TableHead className="text-right">Aktion</TableHead>
                </TableRow>
              </TableHeader>
              <TableBody>
                {data.map((s) => (
                  <TableRow key={s.id}>
                    <TableCell>{s.number}</TableCell>
                    <TableCell>{s.supplierId}</TableCell>
                    <TableCell>{s.description}</TableCell>
                    <TableCell className="text-right">{s.quantity}</TableCell>
                    <TableCell className="text-right">{s.amount.toFixed(2)} EUR</TableCell>
                    <TableCell>{s.status}</TableCell>
                    <TableCell className="text-right">
                      <Button size="sm" variant="outline" onClick={() => { void handleApprove(s) }} disabled={s.status === 'FREIGEGEBEN'}>
                        Freigeben
                      </Button>
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
