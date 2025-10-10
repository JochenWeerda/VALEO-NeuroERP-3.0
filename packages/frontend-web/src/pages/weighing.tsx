import { Card } from "@/components/ui/card"
import { Button } from "@/components/ui/button"
import { Table, TableBody, TableCell, TableHead, TableHeader, TableRow } from "@/components/ui/table"
import { useMcpQuery, useMcpMutation } from "@/lib/mcp"

type Ticket = { id: string; vehicle: string; gross: number; tare: number; net: number; material: string; ts: string }

export default function WeighingPanel() {
  const { data, isLoading } = useMcpQuery<{ data: Ticket[] }>('weighing','list',[])
  const finalize = useMcpMutation<{ id: string }, { ok: boolean }>('weighing','finalize')
  const rows = data?.data ?? []
  return (
    <div className="space-y-4">
      <h2 className="text-2xl font-bold">Weighing</h2>
      <Card className="p-4">
        {isLoading ? 'Loading…' : (
          <Table>
            <TableHeader>
              <TableRow>
                <TableHead>Ticket</TableHead>
                <TableHead>Vehicle</TableHead>
                <TableHead className="text-right">Gross</TableHead>
                <TableHead className="text-right">Tare</TableHead>
                <TableHead className="text-right">Net</TableHead>
                <TableHead>Material</TableHead>
                <TableHead>Time</TableHead>
                <TableHead></TableHead>
              </TableRow>
            </TableHeader>
            <TableBody>
              {rows.map(t => (
                <TableRow key={t.id}>
                  <TableCell className="font-mono">{t.id}</TableCell>
                  <TableCell>{t.vehicle}</TableCell>
                  <TableCell className="text-right">{t.gross}</TableCell>
                  <TableCell className="text-right">{t.tare}</TableCell>
                  <TableCell className="text-right">{t.net}</TableCell>
                  <TableCell>{t.material}</TableCell>
                  <TableCell>{new Date(t.ts).toLocaleString()}</TableCell>
                  <TableCell className="text-right">
                    <Button size="sm" onClick={() => finalize.mutate({ id: t.id })}>Finalize</Button>
                  </TableCell>
                </TableRow>
              ))}
            </TableBody>
          </Table>
        )}
      </Card>
    </div>
  )
}