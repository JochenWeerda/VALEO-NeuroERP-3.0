import * as React from "react"
import { Button } from "@/components/ui/button"
import { Card } from "@/components/ui/card"
import { DetailDrawer } from "@/components/ui/detail-drawer"
import { Table, TableBody, TableCell, TableHead, TableHeader, TableRow } from "@/components/ui/table"
import { Toolbar } from "@/components/ui/toolbar"
import { useToast } from "@/components/ui/toast-provider"
import { PricingForm } from "@/features/pricing/PricingForm"
import type { PriceItem } from "@/features/pricing/schema"
import { useMcpMutation, useMcpQuery } from "@/lib/mcp"
import { useMcpRealtime } from "@/lib/useMcpRealtime"
import { useQueryClient } from "@tanstack/react-query"

const DECIMAL_PLACES = 2

export default function PricingPanel(): JSX.Element {
  const { data, isLoading } = useMcpQuery<{ data: PriceItem[] }>('pricing', 'list', [])
  const rows: PriceItem[] = (data?.data ?? []) as PriceItem[]
  const [q, setQ] = React.useState<string>("")
  const [sel, setSel] = React.useState<PriceItem | null>(null)
  const { push } = useToast()
  const qc = useQueryClient()
  const key = ['mcp', 'pricing', 'list'] as const

  useMcpRealtime('pricing', (evt): void => {
    if (evt.type === 'updated' || evt.type === 'created') {
      void qc.invalidateQueries({ queryKey: key })
      push(`Pricing ${evt.type}`)
    }
  })

  const update = useMcpMutation<PriceItem, { ok: boolean }>('pricing', 'update')

  const filtered: PriceItem[] = React.useMemo(
    (): PriceItem[] => rows.filter((r): boolean =>
      r.name.toLowerCase().includes(q.toLowerCase()) ||
      r.sku.toLowerCase().includes(q.toLowerCase())
    ),
    [rows, q]
  )

  const handleCopilot = (): void => {
    push("🤖 Copilot: Preis-Cluster & Elastizität werden berechnet…")
  }

  const handleEdit = (p: PriceItem): void => {
    setSel(p)
  }

  const handleClose = (): void => {
    setSel(null)
  }

  const handleSubmit = (v: PriceItem): void => {
    const prev = qc.getQueryData<{ data: PriceItem[] }>(key)
    if (prev !== undefined) {
      qc.setQueryData(key, {
        data: prev.data.map((x): PriceItem => x.sku === v.sku ? { ...x, ...v } : x)
      })
    }
    update.mutate(v, {
      onSuccess: (): void => push("✔ Preis gespeichert"),
      onError: (): void => {
        if (prev !== undefined) {
          qc.setQueryData(key, prev)
        }
        push("❌ Speichern fehlgeschlagen")
      },
      onSettled: (): Promise<void> => qc.invalidateQueries({ queryKey: key })
    })
  }

  return (
    <div className="space-y-4">
      <h2 className="text-2xl font-bold">Pricing</h2>
      <Toolbar onSearch={setQ} onCopilot={handleCopilot} />
      <Card className="p-4 overflow-x-auto">
        {isLoading ? 'Loading…' : (
          <Table>
            <TableHeader>
              <TableRow>
                <TableHead>SKU</TableHead>
                <TableHead>Artikel</TableHead>
                <TableHead>Basis-Netto</TableHead>
                <TableHead>Einheit</TableHead>
                <TableHead>Währung</TableHead>
                <TableHead />
              </TableRow>
            </TableHeader>
            <TableBody>
              {filtered.map((p: PriceItem): JSX.Element => (
                <TableRow key={p.sku}>
                  <TableCell className="font-mono">{p.sku}</TableCell>
                  <TableCell>{p.name}</TableCell>
                  <TableCell>{p.baseNet.toFixed(DECIMAL_PLACES)}</TableCell>
                  <TableCell>{p.unit}</TableCell>
                  <TableCell>{p.currency}</TableCell>
                  <TableCell className="text-right">
                    <Button size="sm" onClick={(): void => handleEdit(p)}>
                      Edit
                    </Button>
                  </TableCell>
                </TableRow>
              ))}
            </TableBody>
          </Table>
        )}
      </Card>

      {(sel !== null) && (
        <DetailDrawer 
          title={`Preis bearbeiten: ${sel.sku}`} 
          open={sel !== null} 
          onClose={handleClose}
        >
          <PricingForm
            defaultValues={sel}
            submitting={update.isPending}
            onSubmit={handleSubmit}
          />
        </DetailDrawer>
      )}
    </div>
  )
}