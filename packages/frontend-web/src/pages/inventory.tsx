import { useCallback, useMemo, useState } from "react"
import { Card } from "@/components/ui/card"
import { Button } from "@/components/ui/button"
import { Table, TableBody, TableCell, TableHead, TableHeader, TableRow } from "@/components/ui/table"
import { Toolbar } from "@/components/ui/toolbar"
import { DetailDrawer } from "@/components/ui/detail-drawer"
import { useMcpMutation, useMcpQuery } from "@/lib/mcp"
import { type McpRealtimeEvent, useMcpRealtime } from "@/lib/useMcpRealtime"
import { useToast } from "@/components/ui/toast-provider"
import { useQueryClient } from "@tanstack/react-query"
import type { Stock } from "@/features/inventory/schema"
import { AdjustForm } from "@/features/inventory/AdjustForm"
import { PutawayForm } from "@/features/inventory/PutawayForm"
import { formatDE } from "@/lib/number-de"

export default function InventoryPanel(): JSX.Element {
  const { data, isLoading } = useMcpQuery<{ data: Stock[] }>("inventory", "list", [])
  const rows: Stock[] = data?.data?.data ?? []
  const [search, setSearch] = useState("")
  const [adjustSku, setAdjustSku] = useState<Stock | null>(null)
  const [putawaySku, setPutawaySku] = useState<Stock | null>(null)
  const { push } = useToast()
  const queryClient = useQueryClient()

  const queryKey = ["mcp", "inventory", "list"] as const

  const handleInventoryEvent = useCallback((event: McpRealtimeEvent): void => {
    if (event.type === "adjusted" || event.type === "moved" || event.type === "created") {
      queryClient.invalidateQueries({ queryKey })
      push(`Inventory ${event.type}`)
    }
  }, [push, queryClient, queryKey])

  useMcpRealtime("inventory", handleInventoryEvent)

  const adjust = useMcpMutation<{ sku: string; delta: number; reason: string }, { ok: boolean }>("inventory", "adjust")
  const putaway = useMcpMutation<{ sku: string; qty: number; fromLocation: string; toLocation: string }, { ok: boolean }>(
    "inventory",
    "putaway"
  )

  const filtered = useMemo<Stock[]>(() =>
    rows.filter((row) =>
      row.name.toLowerCase().includes(search.toLowerCase()) ||
      row.sku.toLowerCase().includes(search.toLowerCase())
    ),
  [rows, search])

  return (
    <div className="space-y-4">
      <h2 className="text-2xl font-bold">Inventory</h2>
      <Toolbar
        onSearch={setSearch}
        onCopilot={() => push("Copilot Hinweis: Slot-Empfehlungen werden berechnet...")}
      />
      <Card className="p-4">
        {isLoading ? "Loading..." : (
          <Table>
            <TableHeader>
              <TableRow>
                <TableHead>SKU</TableHead>
                <TableHead>Item</TableHead>
                <TableHead className="text-right">Qty</TableHead>
                <TableHead>UoM</TableHead>
                <TableHead>Location</TableHead>
                <TableHead />
              </TableRow>
            </TableHeader>
            <TableBody>
              {filtered.map((stock) => (
                <TableRow key={stock.sku}>
                  <TableCell className="font-mono">{stock.sku}</TableCell>
                  <TableCell>{stock.name}</TableCell>
                  <TableCell className="text-right">{formatDE(stock.qty)}</TableCell>
                  <TableCell>{stock.uom}</TableCell>
                  <TableCell>{stock.location ?? "-"}</TableCell>
                  <TableCell className="space-x-2 text-right">
                    <Button size="sm" variant="secondary" onClick={() => setAdjustSku(stock)}>Adjust</Button>
                    <Button size="sm" onClick={() => setPutawaySku(stock)}>Putaway</Button>
                  </TableCell>
                </TableRow>
              ))}
            </TableBody>
          </Table>
        )}
      </Card>

      {adjustSku ? (
        <DetailDrawer title={`Adjust ${adjustSku.sku}`} open={Boolean(adjustSku)} onClose={() => setAdjustSku(null)}>
          <AdjustForm
            sku={adjustSku.sku}
            onSubmit={(value) => {
              const previous = queryClient.getQueryData<{ data: Stock[] }>(queryKey)
              if (previous) {
                queryClient.setQueryData(queryKey, {
                  data: previous.data.map((item) =>
                    item.sku === value.sku ? { ...item, qty: Math.max(0, item.qty + value.delta) } : item
                  )
                })
              }
              adjust.mutate(value, {
                onSuccess: () => push("Adjust verbucht"),
                onError: () => {
                  if (previous) queryClient.setQueryData(queryKey, previous)
                  push("Adjust fehlgeschlagen")
                },
                onSettled: () => queryClient.invalidateQueries({ queryKey })
              })
            }}
            submitting={adjust.isPending}
          />
        </DetailDrawer>
      ) : null}

      {putawaySku ? (
        <DetailDrawer title={`Putaway ${putawaySku.sku}`} open={Boolean(putawaySku)} onClose={() => setPutawaySku(null)}>
          <PutawayForm
            sku={putawaySku.sku}
            fromLocation={putawaySku.location}
            onSubmit={(value) => {
              const previous = queryClient.getQueryData<{ data: Stock[] }>(queryKey)
              if (previous) {
                queryClient.setQueryData(queryKey, {
                  data: previous.data.map((item) =>
                    item.sku === value.sku ? { ...item, location: value.toLocation } : item
                  )
                })
              }
              putaway.mutate(value, {
                onSuccess: () => push("Putaway verbucht"),
                onError: () => {
                  if (previous) queryClient.setQueryData(queryKey, previous)
                  push("Putaway fehlgeschlagen")
                },
                onSettled: () => queryClient.invalidateQueries({ queryKey })
              })
            }}
            submitting={putaway.isPending}
          />
        </DetailDrawer>
      ) : null}
    </div>
  )
}