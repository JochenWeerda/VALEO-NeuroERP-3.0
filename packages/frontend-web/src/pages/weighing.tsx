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
import type { Ticket } from "@/features/weighing/schema"
import { TicketForm } from "@/features/weighing/TicketForm"
import { formatDE } from "@/lib/number-de"

export default function WeighingPanel(): JSX.Element {
  const { data, isLoading } = useMcpQuery<{ data: Ticket[] }>("weighing", "list", [])
  const rows: Ticket[] = data?.data?.data ?? []
  const [search, setSearch] = useState("")
  const [selected, setSelected] = useState<Ticket | null>(null)
  const [pendingFinalizeId, setPendingFinalizeId] = useState<string | null>(null)
  const { push } = useToast()
  const queryClient = useQueryClient()
  const queryKey = ["mcp", "weighing", "list"] as const

  const handleWeighingEvent = useCallback((event: McpRealtimeEvent): void => {
    if (event.type === "updated" || event.type === "finalized" || event.type === "created") {
      queryClient.invalidateQueries({ queryKey })
      push(`Weighing ${event.type}`)
    }
  }, [push, queryClient, queryKey])

  useMcpRealtime("weighing", handleWeighingEvent)

  const updateTicket = useMcpMutation<Ticket, { ok: boolean }>("weighing", "update")
  const finalize = useMcpMutation<{ id: string }, { ok: boolean }>("weighing", "finalize")

  const filtered = useMemo<Ticket[]>(() =>
    rows.filter((ticket) => {
      const term = search.toLowerCase()
      return (
        ticket.id.toLowerCase().includes(term) ||
        ticket.vehicle.toLowerCase().includes(term) ||
        ticket.material.toLowerCase().includes(term)
      )
    }),
  [rows, search])

  return (
    <div className="space-y-4">
      <h1 className="text-2xl font-bold">Wiegescheine</h1>
      <Toolbar
        onSearch={setSearch}
        onCopilot={() => push("Copilot Hinweis: Abweichungen werden analysiert...")}
      />
      <Card className="p-4">
        {isLoading ? "Wird geladen…" : (
          <Table>
            <TableHeader>
              <TableRow>
                <TableHead>Ticket</TableHead>
                <TableHead>Kennzeichen</TableHead>
                <TableHead className="text-right">Brutto</TableHead>
                <TableHead className="text-right">Tara</TableHead>
                <TableHead className="text-right">Netto</TableHead>
                <TableHead>Ware</TableHead>
                <TableHead>Zeit</TableHead>
                <TableHead />
              </TableRow>
            </TableHeader>
            <TableBody>
              {filtered.map((ticket) => (
                <TableRow key={ticket.id}>
                  <TableCell className="font-mono">{ticket.id}</TableCell>
                  <TableCell>{ticket.vehicle}</TableCell>
                  <TableCell className="text-right">{formatDE(ticket.gross)}</TableCell>
                  <TableCell className="text-right">{formatDE(ticket.tare)}</TableCell>
                  <TableCell className="text-right">{formatDE(ticket.net)}</TableCell>
                  <TableCell>{ticket.material}</TableCell>
                  <TableCell>{new Date(ticket.ts).toLocaleString()}</TableCell>
                  <TableCell className="space-x-2 text-right">
                    <Button className="min-h-touch" variant="secondary" onClick={() => setSelected(ticket)}>Bearbeiten</Button>
                    <Button
                      className="min-h-touch"
                      disabled={pendingFinalizeId !== null}
                      onClick={() => {
                        if (pendingFinalizeId) return
                        setPendingFinalizeId(ticket.id)
                        const previous = queryClient.getQueryData<{ data: Ticket[] }>(queryKey)
                        finalize.mutate({ id: ticket.id }, {
                          onSuccess: () => push("Ticket finalisiert"),
                          onError: () => {
                            if (previous) queryClient.setQueryData(queryKey, previous)
                            push("Abschließen fehlgeschlagen")
                          },
                          onSettled: () => {
                            setPendingFinalizeId(null)
                            void queryClient.invalidateQueries({ queryKey })
                          }
                        })
                      }}
                    >
                      {pendingFinalizeId === ticket.id ? "Wird abgeschlossen…" : "Abschließen"}
                    </Button>
                  </TableCell>
                </TableRow>
              ))}
            </TableBody>
          </Table>
        )}
      </Card>

      {selected ? (
        <DetailDrawer title={`Ticket ${selected.id} bearbeiten`} open={Boolean(selected)} onClose={() => setSelected(null)}>
          <TicketForm
            defaultValues={selected}
            submitting={updateTicket.isPending}
            onSubmit={(value) => {
              const previous = queryClient.getQueryData<{ data: Ticket[] }>(queryKey)
              if (previous) {
                queryClient.setQueryData(queryKey, {
                  data: previous.data.map((item) => (item.id === value.id ? { ...item, ...value } : item))
                })
              }
              updateTicket.mutate(value, {
                onSuccess: () => push("Ticket gespeichert"),
                onError: () => {
                  if (previous) queryClient.setQueryData(queryKey, previous)
                  push("Speichern fehlgeschlagen")
                },
                onSettled: () => queryClient.invalidateQueries({ queryKey })
              })
            }}
          />
        </DetailDrawer>
      ) : null}
    </div>
  )
}