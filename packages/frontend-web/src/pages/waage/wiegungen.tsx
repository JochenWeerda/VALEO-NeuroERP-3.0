import { useMemo, useState } from 'react'
import { Badge } from '@/components/ui/badge'
import { Button } from '@/components/ui/button'
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card'
import { DataTable } from '@/components/ui/data-table'
import { Input } from '@/components/ui/input'
import { Label } from '@/components/ui/label'
import { ErrorState } from '@/components/ErrorState'
import { useToast } from '@/hooks/use-toast'
import {
  useAllocateContract,
  useCreateWeighingTicket,
  useOpenContracts,
  useUpdateWeighingTicket,
  useWeighingTickets,
  type WeighingTicket,
} from '@/lib/api/weighing-tickets'
import { Scale, Search, Plus, Link2 } from 'lucide-react'

type NewTicketForm = {
  ticketNumber: string
  scaleId: string
  vehiclePlate: string
  grossWeight: number
  tareWeight: number
  moisturePct: number
  impuritiesPct: number
}

const initialForm: NewTicketForm = {
  ticketNumber: '',
  scaleId: 'W-001',
  vehiclePlate: '',
  grossWeight: 0,
  tareWeight: 0,
  moisturePct: 0,
  impuritiesPct: 0,
}

export default function WiegungenPage(): JSX.Element {
  const { toast } = useToast()
  const [searchTerm, setSearchTerm] = useState('')
  const [selectedTicketId, setSelectedTicketId] = useState<string>('')
  const [selectedContractId, setSelectedContractId] = useState<string>('')
  const [form, setForm] = useState<NewTicketForm>(initialForm)

  const ticketsQuery = useWeighingTickets({ limit: 100 })
  const contractsQuery = useOpenContracts()
  const createMutation = useCreateWeighingTicket()
  const updateMutation = useUpdateWeighingTicket()
  const allocateMutation = useAllocateContract()

  if (ticketsQuery.isError) {
    return <ErrorState error={ticketsQuery.error as Error} onRetry={() => { void ticketsQuery.refetch() }} />
  }

  const tickets = ticketsQuery.data?.items ?? []
  const filteredTickets = useMemo(
    () =>
      tickets.filter((ticket) => {
        const s = searchTerm.toLowerCase().trim()
        if (!s) return true
        return (
          ticket.ticket_number.toLowerCase().includes(s)
          || (ticket.vehicle_plate ?? '').toLowerCase().includes(s)
          || (ticket.scale_id ?? '').toLowerCase().includes(s)
        )
      }),
    [tickets, searchTerm],
  )

  const totalNetKg = tickets.reduce((sum, t) => sum + Number(t.net_weight ?? 0), 0)
  const totalBillingKg = tickets.reduce((sum, t) => sum + Number(t.billing_weight ?? t.net_weight ?? 0), 0)

  async function onCreate(): Promise<void> {
    if (!form.ticketNumber.trim()) {
      toast({ title: 'Fehlende Ticketnummer', description: 'ticket_number ist erforderlich', variant: 'destructive' })
      return
    }
    try {
      await createMutation.mutateAsync({
        ticket_number: form.ticketNumber.trim(),
        scale_id: form.scaleId.trim() || undefined,
        vehicle_plate: form.vehiclePlate.trim() || undefined,
        gross_weight: form.grossWeight,
        tare_weight: form.tareWeight,
        moisture_pct: form.moisturePct,
        impurities_pct: form.impuritiesPct,
        direction: 'in',
      })
      toast({ title: 'Wiegeschein erstellt', description: 'Datensatz wurde persistiert.' })
      setForm(initialForm)
    } catch (e) {
      const message = e instanceof Error ? e.message : 'Erstellung fehlgeschlagen'
      toast({ title: 'Fehler', description: message, variant: 'destructive' })
    }
  }

  async function onSetSecondWeighing(ticket: WeighingTicket): Promise<void> {
    try {
      await updateMutation.mutateAsync({
        id: ticket.id,
        payload: { status: 'closed' },
      })
      toast({ title: 'Status aktualisiert', description: `Ticket ${ticket.ticket_number} geschlossen.` })
    } catch (e) {
      const message = e instanceof Error ? e.message : 'Update fehlgeschlagen'
      toast({ title: 'Fehler', description: message, variant: 'destructive' })
    }
  }

  async function onAllocate(): Promise<void> {
    if (!selectedTicketId || !selectedContractId) {
      toast({ title: 'Zuordnung fehlt', description: 'Bitte Ticket und Kontrakt auswählen.', variant: 'destructive' })
      return
    }
    try {
      await allocateMutation.mutateAsync({
        ticketId: selectedTicketId,
        contractId: selectedContractId,
      })
      toast({ title: 'Kontrakt zugeordnet', description: 'Wiegeschein wurde gegen Kontrakt allokiert.' })
    } catch (e) {
      const message = e instanceof Error ? e.message : 'Kontraktzuordnung fehlgeschlagen'
      toast({ title: 'Fehler', description: message, variant: 'destructive' })
    }
  }

  return (
    <div className="space-y-4 p-6">
      <div>
        <h1 className="text-3xl font-bold">Wiegungen</h1>
        <p className="text-muted-foreground">Wiegeschein-Erfassung und Kontraktzuordnung</p>
      </div>

      <div className="grid gap-4 md:grid-cols-3">
        <Card>
          <CardHeader className="pb-2">
            <CardTitle className="text-sm font-medium">Wiegescheine</CardTitle>
          </CardHeader>
          <CardContent>
            <div className="flex items-center gap-2">
              <Scale className="h-5 w-5 text-blue-600" />
              <span className="text-2xl font-bold">{tickets.length}</span>
            </div>
          </CardContent>
        </Card>
        <Card>
          <CardHeader className="pb-2">
            <CardTitle className="text-sm font-medium">Netto gesamt (kg)</CardTitle>
          </CardHeader>
          <CardContent>
            <span className="text-2xl font-bold">{totalNetKg.toFixed(3)}</span>
          </CardContent>
        </Card>
        <Card>
          <CardHeader className="pb-2">
            <CardTitle className="text-sm font-medium">Abrechnungsgewicht (kg)</CardTitle>
          </CardHeader>
          <CardContent>
            <span className="text-2xl font-bold">{totalBillingKg.toFixed(3)}</span>
          </CardContent>
        </Card>
      </div>

      <Card>
        <CardHeader>
          <CardTitle className="text-base">Neuen Wiegeschein anlegen</CardTitle>
        </CardHeader>
        <CardContent className="grid gap-3 md:grid-cols-4">
          <div>
            <Label htmlFor="ticketNumber">Ticketnummer</Label>
            <Input id="ticketNumber" value={form.ticketNumber} onChange={(e) => setForm((p) => ({ ...p, ticketNumber: e.target.value }))} />
          </div>
          <div>
            <Label htmlFor="scaleId">Waage</Label>
            <Input id="scaleId" value={form.scaleId} onChange={(e) => setForm((p) => ({ ...p, scaleId: e.target.value }))} />
          </div>
          <div>
            <Label htmlFor="vehiclePlate">Kennzeichen</Label>
            <Input id="vehiclePlate" value={form.vehiclePlate} onChange={(e) => setForm((p) => ({ ...p, vehiclePlate: e.target.value }))} />
          </div>
          <div className="grid grid-cols-2 gap-2">
            <div>
              <Label htmlFor="grossWeight">Brutto</Label>
              <Input id="grossWeight" type="number" value={form.grossWeight} onChange={(e) => setForm((p) => ({ ...p, grossWeight: Number(e.target.value) }))} />
            </div>
            <div>
              <Label htmlFor="tareWeight">Tara</Label>
              <Input id="tareWeight" type="number" value={form.tareWeight} onChange={(e) => setForm((p) => ({ ...p, tareWeight: Number(e.target.value) }))} />
            </div>
          </div>
          <div>
            <Label htmlFor="moisturePct">Feuchte %</Label>
            <Input id="moisturePct" type="number" step="0.1" value={form.moisturePct} onChange={(e) => setForm((p) => ({ ...p, moisturePct: Number(e.target.value) }))} />
          </div>
          <div>
            <Label htmlFor="impuritiesPct">Besatz %</Label>
            <Input id="impuritiesPct" type="number" step="0.1" value={form.impuritiesPct} onChange={(e) => setForm((p) => ({ ...p, impuritiesPct: Number(e.target.value) }))} />
          </div>
          <div className="md:col-span-2 flex items-end">
            <Button className="gap-2" onClick={() => { void onCreate() }} disabled={createMutation.isPending}>
              <Plus className="h-4 w-4" />
              Anlegen
            </Button>
          </div>
        </CardContent>
      </Card>

      <Card>
        <CardHeader>
          <CardTitle className="text-base">Ticket gegen Kontrakt allokieren</CardTitle>
        </CardHeader>
        <CardContent className="grid gap-3 md:grid-cols-3">
          <div>
            <Label htmlFor="selectTicket">Ticket</Label>
            <select
              id="selectTicket"
              className="mt-1 h-10 w-full rounded-md border bg-background px-3 text-sm"
              value={selectedTicketId}
              onChange={(e) => setSelectedTicketId(e.target.value)}
            >
              <option value="">Bitte wählen</option>
              {tickets.filter((t) => !t.contract_id).map((ticket) => (
                <option key={ticket.id} value={ticket.id}>
                  {ticket.ticket_number} | {ticket.vehicle_plate ?? '-'} | {(ticket.billing_weight ?? ticket.net_weight ?? 0).toFixed(3)} kg
                </option>
              ))}
            </select>
          </div>
          <div>
            <Label htmlFor="selectContract">Offener Kontrakt</Label>
            <select
              id="selectContract"
              className="mt-1 h-10 w-full rounded-md border bg-background px-3 text-sm"
              value={selectedContractId}
              onChange={(e) => setSelectedContractId(e.target.value)}
            >
              <option value="">Bitte wählen</option>
              {(contractsQuery.data ?? []).map((contract) => (
                <option key={contract.id} value={contract.id}>
                  {contract.contract_number} | Rest: {contract.remaining_quantity_kg.toFixed(3)} kg
                </option>
              ))}
            </select>
          </div>
          <div className="flex items-end">
            <Button className="gap-2" onClick={() => { void onAllocate() }} disabled={allocateMutation.isPending}>
              <Link2 className="h-4 w-4" />
              Allokieren
            </Button>
          </div>
        </CardContent>
      </Card>

      <Card>
        <CardHeader>
          <CardTitle>Suche</CardTitle>
        </CardHeader>
        <CardContent>
          <div className="relative">
            <Search className="absolute left-3 top-1/2 h-4 w-4 -translate-y-1/2 text-muted-foreground" />
            <Input placeholder="Ticket, Kennzeichen, Waage..." value={searchTerm} onChange={(e) => setSearchTerm(e.target.value)} className="pl-10" />
          </div>
        </CardContent>
      </Card>

      <Card>
        <CardContent className="pt-6">
          <DataTable
            data={filteredTickets}
            columns={[
              { key: 'ticket_number', label: 'Ticket' },
              { key: 'vehicle_plate', label: 'Kennzeichen' },
              { key: 'scale_id', label: 'Waage' },
              { key: 'gross_weight', label: 'Brutto (kg)' },
              { key: 'tare_weight', label: 'Tara (kg)' },
              {
                key: 'net_weight',
                label: 'Netto (kg)',
                render: (t: WeighingTicket) => <span className="font-semibold">{(t.net_weight ?? 0).toFixed(3)}</span>,
              },
              {
                key: 'billing_weight',
                label: 'Abrechnung (kg)',
                render: (t: WeighingTicket) => (t.billing_weight ?? t.net_weight ?? 0).toFixed(3),
              },
              {
                key: 'status',
                label: 'Status',
                render: (t: WeighingTicket) => <Badge variant={t.status === 'closed' ? 'outline' : 'secondary'}>{t.status}</Badge>,
              },
              {
                key: 'allocation_status',
                label: 'Kontrakt',
                render: (t: WeighingTicket) => (
                  <Badge variant={t.contract_id ? 'outline' : 'secondary'}>
                    {t.contract_id ? 'zugeordnet' : (t.allocation_status ?? 'offen')}
                  </Badge>
                ),
              },
              {
                key: 'actions',
                label: 'Aktion',
                render: (t: WeighingTicket) => (
                  <Button
                    variant="outline"
                    size="sm"
                    disabled={updateMutation.isPending || t.status === 'closed'}
                    onClick={() => { void onSetSecondWeighing(t) }}
                  >
                    Schließen
                  </Button>
                ),
              },
            ]}
          />
        </CardContent>
      </Card>
    </div>
  )
}
