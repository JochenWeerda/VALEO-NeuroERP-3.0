import { Card } from "@/components/ui/card"
import { Table, TableBody, TableCell, TableHead, TableHeader, TableRow } from "@/components/ui/table"
import { useMcpQuery } from "@/lib/mcp"

type Stock = { sku: string; name: string; qty: number; uom: string; location?: string }

export default function InventoryPanel() {
  const { data, isLoading } = useMcpQuery<{ data: Stock[] }>('inventory','list',[])
  const rows = data?.data ?? []
  return (
    <div className="space-y-4">
      <h2 className="text-2xl font-bold">Inventory</h2>
      <Card className="p-4">
        {isLoading ? 'Loading…' : (
          <Table>
            <TableHeader>
              <TableRow>
                <TableHead>SKU</TableHead>
                <TableHead>Item</TableHead>
                <TableHead className="text-right">Qty</TableHead>
                <TableHead>UoM</TableHead>
                <TableHead>Location</TableHead>
              </TableRow>
            </TableHeader>
            <TableBody>
              {rows.map(s => (
                <TableRow key={s.sku}>
                  <TableCell className="font-mono">{s.sku}</TableCell>
                  <TableCell>{s.name}</TableCell>
                  <TableCell className="text-right">{s.qty}</TableCell>
                  <TableCell>{s.uom}</TableCell>
                  <TableCell>{s.location ?? '-'}</TableCell>
                </TableRow>
              ))}
            </TableBody>
          </Table>
        )}
      </Card>
    </div>
  )
}