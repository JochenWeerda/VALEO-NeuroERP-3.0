import { useState, useMemo } from "react"
import { Card } from "@/components/ui/card"
import { Button } from "@/components/ui/button"
import { Table, TableBody, TableCell, TableHead, TableHeader, TableRow } from "@/components/ui/table"
import { Toolbar } from "@/components/ui/toolbar"
import { DetailDrawer } from "@/components/ui/detail-drawer"
import { useMcpQuery } from "@/lib/mcp"

type Contract = { id: string; title: string; status: string; customer?: string; amount?: number }

export default function ContractsPanel() {
  const { data, isLoading } = useMcpQuery<{ data: Contract[] }>('contracts','list',[])
  const [selected, setSelected] = useState<Contract|null>(null)
  const [query, setQuery] = useState("")
  const items = data?.data || []

  const filtered = useMemo(
    () => Array.isArray(items) ? items.filter((c: Contract) => c.title.toLowerCase().includes(query.toLowerCase())) : [],
    [items, query]
  )

  return (
    <div className="space-y-4">
      <h2 className="text-2xl font-bold">Contracts</h2>
      <Toolbar onSearch={setQuery} onCopilot={() => alert("🤖 Copilot analyzing contracts...")} />
      <Card className="p-4">
        {isLoading ? 'Loading…' : (
          <Table>
            <TableHeader>
              <TableRow>
                <TableHead>ID</TableHead>
                <TableHead>Title</TableHead>
                <TableHead>Status</TableHead>
                <TableHead>Customer</TableHead>
                <TableHead className="text-right">Amount</TableHead>
                <TableHead></TableHead>
              </TableRow>
            </TableHeader>
            <TableBody>
              {filtered.map(c => (
                <TableRow key={c.id}>
                  <TableCell className="font-mono">{c.id}</TableCell>
                  <TableCell>{c.title}</TableCell>
                  <TableCell>{c.status}</TableCell>
                  <TableCell>{c.customer ?? '-'}</TableCell>
                  <TableCell className="text-right">{c.amount?.toFixed(2) ?? '-'}</TableCell>
                  <TableCell className="text-right">
                    <Button size="sm" onClick={() => setSelected(c)}>Details</Button>
                  </TableCell>
                </TableRow>
              ))}
            </TableBody>
          </Table>
        )}
      </Card>

      {selected && (
        <DetailDrawer title={`Contract ${selected.id}`} open={!!selected} onClose={()=>setSelected(null)}>
          <p><strong>Title:</strong> {selected.title}</p>
          <p><strong>Status:</strong> {selected.status}</p>
          <p><strong>Customer:</strong> {selected.customer ?? '-'}</p>
          <p><strong>Amount:</strong> {selected.amount?.toFixed(2) ?? '-'}</p>
          <Button variant="secondary">Edit</Button>
        </DetailDrawer>
      )}
    </div>
  )
}