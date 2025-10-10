import { Card } from "@/components/ui/card"
import { Button } from "@/components/ui/button"
import { useMcpQuery } from "@/lib/mcp"

type Doc = { id: string; title: string; type: string; sizeKB: number; ts: string }

export default function DocumentPanel() {
  const { data, isLoading } = useMcpQuery<{ data: Doc[] }>('document','list',[])
  const rows = data?.data ?? []
  return (
    <div className="space-y-4">
      <h2 className="text-2xl font-bold">Documents</h2>
      <Card className="p-4 space-y-3">
        {isLoading ? 'Loading…' : rows.length === 0 ? 'No documents yet.' : (
          <ul className="space-y-2">
            {rows.map(d => (
              <li key={d.id} className="flex items-center justify-between">
                <div>
                  <div className="font-medium">{d.title}</div>
                  <div className="text-sm opacity-70">{d.type} • {(d.sizeKB).toFixed(0)} KB • {new Date(d.ts).toLocaleString()}</div>
                </div>
                <Button size="sm">Download</Button>
              </li>
            ))}
          </ul>
        )}
      </Card>
    </div>
  )
}