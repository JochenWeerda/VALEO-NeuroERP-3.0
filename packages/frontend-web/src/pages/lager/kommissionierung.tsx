/**
 * Kommissionierung — WMS-PICK-LINK-001
 * Lieferschein (posted/printed) → Kommissionierliste (FEFO) → Warenausgang (shipped)
 */

import { useState } from 'react'
import { useToast } from '@/hooks/use-toast'
import { Button } from '@/components/ui/button'
import { Badge } from '@/components/ui/badge'
import {
  Table,
  TableBody,
  TableCell,
  TableHead,
  TableHeader,
  TableRow,
} from '@/components/ui/table'
import { apiClient } from '@/lib/api-client'
import { useQuery } from '@tanstack/react-query'
import {
  useCreatePickListFromDeliveryNote,
  useConfirmPickList,
  usePickList,
  type PickList,
  type PickListLine,
} from '@/lib/api/warehouse-wms'

// ── Types ──────────────────────────────────────────────────────────────────

type DeliveryNote = {
  id: string
  delivery_note_number: string
  status: string
  customer_id?: string | null
  delivery_date?: string | null
}

// ── Hooks ──────────────────────────────────────────────────────────────────

function useDeliveryNotesForPicking() {
  return useQuery({
    queryKey: ['sales', 'delivery-notes', 'picking'],
    queryFn: async () => {
      const [posted, printed] = await Promise.all([
        apiClient.get<DeliveryNote[]>('/api/v1/sales/delivery-notes', {
          params: { status_filter: 'posted', limit: 100 },
        }),
        apiClient.get<DeliveryNote[]>('/api/v1/sales/delivery-notes', {
          params: { status_filter: 'printed', limit: 100 },
        }),
      ])
      return [...(posted.data ?? []), ...(printed.data ?? [])]
    },
    staleTime: 15_000,
    refetchOnWindowFocus: false,
  })
}

// ── Status helpers ──────────────────────────────────────────────────────────

function dnStatusBadge(status: string) {
  if (status === 'posted') return <Badge variant="secondary">Gebucht</Badge>
  if (status === 'printed') return <Badge variant="outline">Gedruckt</Badge>
  if (status === 'shipped') return <Badge variant="default">Versandt</Badge>
  return <Badge variant="secondary">{status}</Badge>
}

function plStatusBadge(status: string) {
  if (status === 'OPEN') return <Badge variant="secondary">Offen</Badge>
  if (status === 'IN_PROGRESS') return <Badge variant="outline">In Bearbeitung</Badge>
  if (status === 'COMPLETED') return <Badge className="bg-green-600 text-white">Abgeschlossen</Badge>
  if (status === 'CANCELLED') return <Badge variant="destructive">Storniert</Badge>
  return <Badge variant="secondary">{status}</Badge>
}

function lineStatusBadge(status: string) {
  if (status === 'OPEN') return <Badge variant="secondary">Offen</Badge>
  if (status === 'PARTIAL') return <Badge variant="outline">Teilweise</Badge>
  if (status === 'DONE') return <Badge className="bg-green-600 text-white">Fertig</Badge>
  if (status === 'SKIPPED') return <Badge variant="destructive">Übersprungen</Badge>
  return <Badge variant="secondary">{status}</Badge>
}

// ── Subcomponent: PickListPanel ─────────────────────────────────────────────

function PickListPanel({
  pickListId,
  onCompleted,
}: {
  pickListId: string
  onCompleted: () => void
}) {
  const { data: pl, isLoading } = usePickList(pickListId)
  const confirmMutation = useConfirmPickList()
  const { toast } = useToast()
  const [pending, setPending] = useState<Set<string>>(new Set())

  if (isLoading || !pl) return <div className="text-sm text-muted-foreground py-2">Lade...</div>

  const lines: PickListLine[] = Array.isArray((pl as PickList).lines)
    ? ((pl as PickList).lines as PickListLine[])
    : []

  async function handleConfirmLine(line: PickListLine) {
    const key = line.id
    if (pending.has(key)) return
    setPending((s) => new Set(s).add(key))
    try {
      const result = await confirmMutation.mutateAsync({
        pickListId,
        pickedLines: [{ line_id: line.id, quantity_picked: line.quantity_required }],
      })
      if (result.status === 'COMPLETED') {
        toast({ title: 'Kommissionierung abgeschlossen', description: 'Lieferschein wurde auf „Versandt" gesetzt.' })
        onCompleted()
      }
    } catch {
      toast({ title: 'Fehler', description: 'Bestätigung fehlgeschlagen.', variant: 'destructive' })
    } finally {
      setPending((s) => {
        const next = new Set(s)
        next.delete(key)
        return next
      })
    }
  }

  async function handleConfirmAll() {
    const openLines = lines.filter((l) => l.status === 'OPEN' || l.status === 'PARTIAL')
    if (!openLines.length) return
    const key = 'all'
    if (pending.has(key)) return
    setPending((s) => new Set(s).add(key))
    try {
      const result = await confirmMutation.mutateAsync({
        pickListId,
        pickedLines: openLines.map((l) => ({ line_id: l.id, quantity_picked: l.quantity_required })),
      })
      if (result.status === 'COMPLETED') {
        toast({ title: 'Kommissionierung abgeschlossen', description: 'Lieferschein wurde auf „Versandt" gesetzt.' })
        onCompleted()
      }
    } catch {
      toast({ title: 'Fehler', description: 'Sammel-Bestätigung fehlgeschlagen.', variant: 'destructive' })
    } finally {
      setPending((s) => {
        const next = new Set(s)
        next.delete(key)
        return next
      })
    }
  }

  const hasOpen = lines.some((l) => l.status === 'OPEN' || l.status === 'PARTIAL')

  return (
    <div className="mt-2 rounded border p-3 bg-muted/30">
      <div className="flex items-center justify-between mb-2">
        <span className="text-sm font-medium">Kommissionierliste {pickListId.slice(0, 8)}…</span>
        <div className="flex gap-2 items-center">
          {plStatusBadge(pl.status)}
          {pl.status !== 'COMPLETED' && hasOpen && (
            <Button
              size="sm"
              disabled={pending.has('all')}
              onClick={handleConfirmAll}
            >
              Alle bestätigen
            </Button>
          )}
        </div>
      </div>
      <Table>
        <TableHeader>
          <TableRow>
            <TableHead>Artikel-ID</TableHead>
            <TableHead>Lagerplatz</TableHead>
            <TableHead>Charge</TableHead>
            <TableHead>MHD</TableHead>
            <TableHead className="text-right">Soll</TableHead>
            <TableHead className="text-right">Gepickt</TableHead>
            <TableHead>Status</TableHead>
            <TableHead />
          </TableRow>
        </TableHeader>
        <TableBody>
          {lines.map((line) => (
            <TableRow key={line.id}>
              <TableCell className="font-mono text-xs">{line.article_id}</TableCell>
              <TableCell>{line.bin_code ?? line.bin_id ?? '—'}</TableCell>
              <TableCell>{line.batch_number ?? '—'}</TableCell>
              <TableCell>{line.best_before_date ?? '—'}</TableCell>
              <TableCell className="text-right">
                {Number(line.quantity_required).toFixed(2)} {line.unit}
              </TableCell>
              <TableCell className="text-right">
                {Number(line.quantity_picked).toFixed(2)} {line.unit}
              </TableCell>
              <TableCell>{lineStatusBadge(line.status)}</TableCell>
              <TableCell>
                {(line.status === 'OPEN' || line.status === 'PARTIAL') && pl.status !== 'COMPLETED' && (
                  <Button
                    size="sm"
                    variant="outline"
                    disabled={pending.has(line.id)}
                    onClick={() => handleConfirmLine(line)}
                  >
                    Bestätigen
                  </Button>
                )}
              </TableCell>
            </TableRow>
          ))}
        </TableBody>
      </Table>
    </div>
  )
}

// ── Main Page ───────────────────────────────────────────────────────────────

export default function KommissionierungPage() {
  const { data: deliveryNotes = [], isLoading, refetch } = useDeliveryNotesForPicking()
  const createMutation = useCreatePickListFromDeliveryNote()
  const { toast } = useToast()

  const [activePl, setActivePl] = useState<Record<string, string>>({})
  const [creating, setCreating] = useState<Set<string>>(new Set())

  async function handleCreatePickList(dn: DeliveryNote) {
    if (creating.has(dn.id)) return
    setCreating((s) => new Set(s).add(dn.id))
    try {
      const pl = await createMutation.mutateAsync({ lsId: dn.id, payload: {} })
      setActivePl((prev) => ({ ...prev, [dn.id]: pl.id }))
      toast({
        title: 'Kommissionierliste erstellt',
        description: `Pick-Liste ${pl.id.slice(0, 8)}… (${(pl.lines ?? []).length} Pos.) mit FEFO-Vorschlag`,
      })
    } catch (err: unknown) {
      const msg =
        err && typeof err === 'object' && 'response' in err
          ? String((err as { response?: { data?: { detail?: string } } }).response?.data?.detail ?? 'Unbekannter Fehler')
          : 'Fehler beim Erstellen'
      toast({ title: 'Fehler', description: msg, variant: 'destructive' })
    } finally {
      setCreating((s) => {
        const next = new Set(s)
        next.delete(dn.id)
        return next
      })
    }
  }

  return (
    <div className="p-6 space-y-4">
      <div>
        <h1 className="text-2xl font-semibold">Kommissionierung</h1>
        <p className="text-sm text-muted-foreground mt-1">
          Lieferscheine (gebucht/gedruckt) → Kommissionierliste (FEFO) → Warenausgang
        </p>
      </div>

      {isLoading && <p className="text-sm text-muted-foreground">Lade Lieferscheine…</p>}

      {!isLoading && deliveryNotes.length === 0 && (
        <p className="text-sm text-muted-foreground">
          Keine gebuchten/gedruckten Lieferscheine vorhanden.
        </p>
      )}

      <div className="space-y-3">
        {deliveryNotes.map((dn) => (
          <div key={dn.id} className="rounded border p-4 bg-card">
            <div className="flex items-center justify-between">
              <div className="space-y-0.5">
                <div className="font-medium">{dn.delivery_note_number}</div>
                <div className="text-xs text-muted-foreground">
                  {dn.delivery_date ?? '—'} · Kunden-ID: {dn.customer_id ?? '—'}
                </div>
              </div>
              <div className="flex items-center gap-3">
                {dnStatusBadge(dn.status)}
                {!activePl[dn.id] ? (
                  <Button
                    size="sm"
                    disabled={creating.has(dn.id)}
                    onClick={() => handleCreatePickList(dn)}
                  >
                    Kommissionierliste erstellen
                  </Button>
                ) : (
                  <span className="text-xs text-muted-foreground">Pick-Liste aktiv</span>
                )}
              </div>
            </div>

            {activePl[dn.id] && (
              <PickListPanel
                pickListId={activePl[dn.id]}
                onCompleted={() => {
                  setActivePl((prev) => {
                    const next = { ...prev }
                    delete next[dn.id]
                    return next
                  })
                  void refetch()
                }}
              />
            )}
          </div>
        ))}
      </div>
    </div>
  )
}
