import { useState, useMemo } from "react"
import { Card } from "@/components/ui/card"
import { Table, TableBody, TableCell, TableHead, TableHeader, TableRow } from "@/components/ui/table"
import { Toolbar } from "@/components/ui/toolbar"
import { useMcpQuery } from "@/lib/mcp"

type Price = { sku:string; name:string; net:number; gross:number; currency:string; unit:string }

export default function PricingPanel() {
  const { data, isLoading } = useMcpQuery<{ data: Price[] }>('pricing','list',[])
  const [search, setSearch] = useState("")
  const [sort, setSort] = useState<'asc'|'desc'>('asc')
  const rows = data?.data ?? []
  const filtered = useMemo(()=>rows
    .filter(p=>p.name.toLowerCase().includes(search.toLowerCase()))
    .sort((a,b)=>sort==='asc'?a.net-b.net:b.net-a.net),
  [rows,search,sort])

  return (
    <div className="space-y-4">
      <h2 className="text-2xl font-bold">Pricing</h2>
      <Toolbar onSearch={setSearch} onCopilot={()=>alert("🤖 Copilot suggests price clusters...")} />
      <Card className="p-4 overflow-x-auto">
        {isLoading ? 'Loading…' : (
          <Table>
            <TableHeader>
              <TableRow>
                <TableHead>SKU</TableHead>
                <TableHead>Article</TableHead>
                <TableHead onClick={()=>setSort(sort==='asc'?'desc':'asc')} className="cursor-pointer">
                  Net {sort==='asc'?'↑':'↓'}
                </TableHead>
                <TableHead>Gross</TableHead>
                <TableHead>Currency</TableHead>
              </TableRow>
            </TableHeader>
            <TableBody>
              {filtered.map(p=>(
                <TableRow key={p.sku}>
                  <TableCell className="font-mono">{p.sku}</TableCell>
                  <TableCell>{p.name}</TableCell>
                  <TableCell>{p.net.toFixed(2)}</TableCell>
                  <TableCell>{p.gross.toFixed(2)}</TableCell>
                  <TableCell>{p.currency}</TableCell>
                </TableRow>
              ))}
            </TableBody>
          </Table>
        )}
      </Card>
    </div>
  )
}