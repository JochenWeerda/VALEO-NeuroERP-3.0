import { Card } from "@/components/ui/card"
import { Button } from "@/components/ui/button"
import { Table, TableBody, TableCell, TableHead, TableHeader, TableRow } from "@/components/ui/table"
import { useMcpQuery } from "@/lib/mcp"

type Order = { id: string; customer: string; total: number; currency: string; status: 'draft'|'confirmed'|'shipped' }

export default function SalesPanel() {
  const { data, isLoading } = useMcpQuery<{ data: Order[] }>('sales','list',[])
  const rows = data?.data ?? []
  return (
    <div className="space-y-4">
      <h2 className="text-2xl font-bold">Sales</h2>
      <Card className="p-4">
        {isLoading ? 'Loading…' : (
          <Table>
            <TableHeader>
              <TableRow>
                <TableHead>Order</TableHead>
                <TableHead>Customer</TableHead>
                <TableHead className="text-right">Total</TableHead>
                <TableHead>Cur</TableHead>
                <TableHead>Status</TableHead>
                <TableHead></TableHead>
              </TableRow>
            </TableHeader>
            <TableBody>
              {rows.map(o => (
                <TableRow key={o.id}>
                  <TableCell className="font-mono">{o.id}</TableCell>
                  <TableCell>{o.customer}</TableCell>
                  <TableCell className="text-right">{o.total.toFixed(2)}</TableCell>
                  <TableCell>{o.currency}</TableCell>
                  <TableCell>{o.status}</TableCell>
                  <TableCell className="text-right"><Button size="sm" variant="secondary">Open</Button></TableCell>
                </TableRow>
              ))}
            </TableBody>
          </Table>
        )}
      </Card>
    </div>
  )
}