/**
 * Wiegeschein-Auswahl-Dialog für Ernte-Annahme
 */

import { useState, useMemo } from 'react'
import { useQuery } from '@tanstack/react-query'
import {
  Dialog,
  DialogContent,
  DialogHeader,
  DialogTitle,
  DialogFooter,
} from '@/components/ui/dialog'
import { Button } from '@/components/ui/button'
import { Input } from '@/components/ui/input'
import { Label } from '@/components/ui/label'
import { Table, TableBody, TableCell, TableHead, TableHeader, TableRow } from '@/components/ui/table'
import { apiClient } from '@/lib/api-client'

export type WeighingTicket = {
  id: string
  ticket_number: string
  scale_id: string | null
  vehicle_plate: string | null
  gross_weight: number | null
  tare_weight: number | null
  net_weight: number | null
  first_weighing_at: string | null
  second_weighing_at: string | null
  moisture_pct: number | null
  protein_pct: number | null
  impurities_pct: number | null
  hl_weight: number | null
  billing_weight: number | null
  status: string
  direction: string
  article_group?: string | null
  article_id?: string | null
  notes?: string | null
}

type WeighingTicketSelectionDialogProps = {
  open: boolean
  onClose: () => void
  onSelect: (ticket: WeighingTicket) => void
  customerId?: string | null
}

export function WeighingTicketSelectionDialog({
  open,
  onClose,
  onSelect,
  customerId,
}: WeighingTicketSelectionDialogProps): JSX.Element {
  const [searchTerm, setSearchTerm] = useState('')
  const [selectedTicket, setSelectedTicket] = useState<WeighingTicket | null>(null)

  const { data: ticketsData, isLoading, error } = useQuery({
    queryKey: ['weighing-tickets', 'all'],
    queryFn: async () => {
      const params = new URLSearchParams()
      params.append('limit', '200')
      if (customerId) {
        params.append('customer_id', customerId)
      }
      
      try {
        const response = await apiClient.get<any>('/api/v1/weighing-tickets', { params })
        
        let items: any[] = []
        if (Array.isArray(response)) {
          items = response
        } else if (response?.items && Array.isArray(response.items)) {
          items = response.items
        } else if (response?.data) {
          if (Array.isArray(response.data)) {
            items = response.data
          } else if (response.data.items && Array.isArray(response.data.items)) {
            items = response.data.items
          }
        }
        
        return items.map((t: any) => ({
          id: t.id,
          ticket_number: t.ticket_number || t.ticketNumber || '',
          scale_id: t.scale_id || t.scaleId || null,
          vehicle_plate: t.vehicle_plate || t.vehiclePlate || null,
          gross_weight: t.gross_weight || t.grossWeight || null,
          tare_weight: t.tare_weight || t.tareWeight || null,
          net_weight: t.net_weight || t.netWeight || null,
          first_weighing_at: t.first_weighing_at || t.firstWeighingAt || null,
          second_weighing_at: t.second_weighing_at || t.secondWeighingAt || null,
          moisture_pct: t.moisture_pct || t.moisturePct || null,
          protein_pct: t.protein_pct || t.proteinPct || null,
          impurities_pct: t.impurities_pct || t.impuritiesPct || null,
          hl_weight: t.hl_weight || t.hlWeight || null,
          billing_weight: t.billing_weight || t.billingWeight || null,
          status: t.status || 'open',
          direction: t.direction || 'in',
          article_group: t.article_group || t.articleGroup || null,
          article_id: t.article_id || t.articleId || null,
          notes: t.notes || null,
        }))
      } catch (err: any) {
        console.error('[WeighingTicketSelectionDialog] Error fetching tickets:', err)
        return []
      }
    },
    enabled: open,
  })

  const filteredTickets = useMemo(() => {
    if (!ticketsData) return []
    if (!searchTerm.trim()) return ticketsData

    const searchLower = searchTerm.toLowerCase()
    return ticketsData.filter((ticket: WeighingTicket) => {
      return (
        ticket.ticket_number.toLowerCase().includes(searchLower) ||
        (ticket.vehicle_plate && ticket.vehicle_plate.toLowerCase().includes(searchLower)) ||
        (ticket.scale_id && ticket.scale_id.toLowerCase().includes(searchLower)) ||
        (ticket.article_group && ticket.article_group.toLowerCase().includes(searchLower))
      )
    })
  }, [ticketsData, searchTerm])

  const handleSelect = (): void => {
    if (selectedTicket) {
      onSelect(selectedTicket)
      setSelectedTicket(null)
      setSearchTerm('')
    }
  }

  const handleClose = (): void => {
    setSelectedTicket(null)
    setSearchTerm('')
    onClose()
  }

  return (
    <Dialog open={open} onOpenChange={handleClose}>
      <DialogContent className="max-w-4xl max-h-[80vh] flex flex-col">
        <DialogHeader>
          <DialogTitle>Wiegeschein auswählen</DialogTitle>
        </DialogHeader>

        <div className="space-y-4 flex-1 overflow-hidden flex flex-col">
          <div className="flex gap-4 items-end">
            <div className="flex-1">
              <Label htmlFor="ticket-search">Suche:</Label>
              <Input
                id="ticket-search"
                value={searchTerm}
                onChange={(e) => setSearchTerm(e.target.value)}
                placeholder="Wiegeschein-Nr., Fahrzeug-Kennzeichen, Waage suchen..."
                autoFocus
              />
            </div>
          </div>

          <div className="flex-1 overflow-auto border rounded">
            {isLoading ? (
              <div className="p-4 text-center text-muted-foreground">Lade Wiegescheine...</div>
            ) : error ? (
              <div className="p-4 text-center text-red-500">Fehler beim Laden der Wiegescheine</div>
            ) : filteredTickets.length === 0 ? (
              <div className="p-4 text-center text-muted-foreground">
                {searchTerm ? 'Keine Wiegescheine gefunden' : 'Keine Wiegescheine in der Datenbank gefunden'}
              </div>
            ) : (
              <Table>
                <TableHeader>
                  <TableRow>
                    <TableHead className="w-24">Wiegeschein-Nr.</TableHead>
                    <TableHead className="w-24">Fahrzeug-Kennzeichen</TableHead>
                    <TableHead className="w-24">Waage</TableHead>
                    <TableHead className="w-24">Brutto (kg)</TableHead>
                    <TableHead className="w-24">Tara (kg)</TableHead>
                    <TableHead className="w-24">Netto (kg)</TableHead>
                    <TableHead className="w-24">Feuchte (%)</TableHead>
                    <TableHead className="w-24">Besatz (%)</TableHead>
                    <TableHead className="w-24">HL-Gewicht</TableHead>
                    <TableHead className="w-28">Warengruppe</TableHead>
                    <TableHead className="w-32">1. Wiegung</TableHead>
                    <TableHead className="w-24">Status</TableHead>
                  </TableRow>
                </TableHeader>
                <TableBody>
                  {filteredTickets.map((ticket: WeighingTicket) => (
                    <TableRow
                      key={ticket.id}
                      className={selectedTicket?.id === ticket.id ? 'bg-green-100' : 'cursor-pointer'}
                      onClick={() => setSelectedTicket(ticket)}
                    >
                      <TableCell className="font-mono">{ticket.ticket_number}</TableCell>
                      <TableCell>{ticket.vehicle_plate || '-'}</TableCell>
                      <TableCell>{ticket.scale_id || '-'}</TableCell>
                      <TableCell>{ticket.gross_weight?.toFixed(2) || '-'}</TableCell>
                      <TableCell>{ticket.tare_weight?.toFixed(2) || '-'}</TableCell>
                      <TableCell className="font-semibold">{ticket.net_weight?.toFixed(2) || '-'}</TableCell>
                      <TableCell>{ticket.moisture_pct?.toFixed(2) || '-'}</TableCell>
                      <TableCell>{ticket.impurities_pct?.toFixed(2) || '-'}</TableCell>
                      <TableCell>{ticket.hl_weight?.toFixed(2) || '-'}</TableCell>
                      <TableCell className="text-xs">{ticket.article_group || '-'}</TableCell>
                      <TableCell>
                        {ticket.first_weighing_at
                          ? new Date(ticket.first_weighing_at).toLocaleString('de-DE', {
                              day: '2-digit',
                              month: '2-digit',
                              year: 'numeric',
                              hour: '2-digit',
                              minute: '2-digit',
                            })
                          : '-'}
                      </TableCell>
                      <TableCell>{ticket.status}</TableCell>
                    </TableRow>
                  ))}
                </TableBody>
              </Table>
            )}
          </div>
        </div>

        <DialogFooter>
          <Button variant="outline" onClick={handleClose}>
            Abbrechen
          </Button>
          <Button onClick={handleSelect} disabled={!selectedTicket}>
            Auswählen
          </Button>
        </DialogFooter>
      </DialogContent>
    </Dialog>
  )
}

