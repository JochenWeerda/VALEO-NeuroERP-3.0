import { useCallback, useEffect, useMemo, useState } from 'react'
import { useNavigate } from 'react-router-dom'
import { Badge } from '@/components/ui/badge'
import { Button } from '@/components/ui/button'
import { Card, CardContent } from '@/components/ui/card'
import { DataTable } from '@/components/ui/data-table'
import {
  Dialog,
  DialogContent,
  DialogFooter,
  DialogHeader,
  DialogTitle,
} from '@/components/ui/dialog'
import { Input } from '@/components/ui/input'
import { Label } from '@/components/ui/label'
import {
  Select,
  SelectContent,
  SelectItem,
  SelectTrigger,
  SelectValue,
} from '@/components/ui/select'
import { Textarea } from '@/components/ui/textarea'
import { ErrorState } from '@/components/ErrorState'
import { useToast } from '@/hooks/use-toast'
import {
  useArticleGroups,
  useArticlesByGroup,
  useCreateWeighingTicket,
  useUpdateWeighingTicket,
  useWeighingTickets,
  type WeighingTicket,
} from '@/lib/api/weighing-tickets'
import { Plus, RefreshCw, Scale } from 'lucide-react'

export default function HoflistePage(): JSX.Element {
  const { toast } = useToast()
  const navigate = useNavigate()
  const [searchTerm, setSearchTerm] = useState('')
  const [selectedTicketId, setSelectedTicketId] = useState<string | null>(null)
  const [showNewDialog, setShowNewDialog] = useState(false)

  // New weighing form state
  const [formArticleGroup, setFormArticleGroup] = useState<string>('')
  const [formArticleId, setFormArticleId] = useState<string>('')
  const [formVehiclePlate, setFormVehiclePlate] = useState('')
  const [formNotes, setFormNotes] = useState('')

  const ticketsQuery = useWeighingTickets({ limit: 200 })
  const createMutation = useCreateWeighingTicket()
  const updateMutation = useUpdateWeighingTicket()
  const articleGroupsQuery = useArticleGroups()
  const articlesByGroupQuery = useArticlesByGroup(formArticleGroup || null)

  const openTickets = useMemo(() => {
    const items = ticketsQuery.data?.items ?? []
    return items.filter((t) => t.status === 'open')
  }, [ticketsQuery.data])

  const filteredTickets = useMemo(() => {
    const s = searchTerm.trim()
    if (!s) return openTickets
    const sl = s.toLowerCase()
    return openTickets.filter(
      (t) =>
        t.ticket_number.toLowerCase().includes(sl) ||
        (t.vehicle_plate && t.vehicle_plate.toLowerCase().includes(sl)) ||
        (t.article_group && t.article_group.toLowerCase().includes(sl))
    )
  }, [openTickets, searchTerm])

  const resetForm = useCallback(() => {
    setFormArticleGroup('')
    setFormArticleId('')
    setFormVehiclePlate('')
    setFormNotes('')
  }, [])

  const handleOpenNewDialog = useCallback(() => {
    resetForm()
    setShowNewDialog(true)
  }, [resetForm])

  const handleCreateTicket = useCallback(async () => {
    const ticketNumber = `WS-${Date.now()}`
    try {
      await createMutation.mutateAsync({
        ticket_number: ticketNumber,
        direction: 'in',
        vehicle_plate: formVehiclePlate || undefined,
        article_group: formArticleGroup || undefined,
        article_id: formArticleId || undefined,
        notes: formNotes || undefined,
      })
      toast({ title: 'Neue Wiegung', description: `Wiegeschein ${ticketNumber} erstellt.` })
      setShowNewDialog(false)
      resetForm()
    } catch (e) {
      const message = e instanceof Error ? e.message : 'Erstellung fehlgeschlagen'
      toast({ title: 'Fehler', description: message, variant: 'destructive' })
    }
  }, [createMutation, toast, formArticleGroup, formArticleId, formVehiclePlate, formNotes, resetForm])

  const handleZweitWiegung = useCallback(async () => {
    if (!selectedTicketId) {
      toast({ title: 'Kein Wiegeschein ausgewählt', description: 'Bitte einen Eintrag in der Liste markieren.', variant: 'destructive' })
      return
    }
    try {
      await updateMutation.mutateAsync({
        id: selectedTicketId,
        payload: { status: 'closed' },
      })
      toast({ title: 'Zweit-Wiegung', description: 'Wiegeschein wurde geschlossen.' })
      setSelectedTicketId(null)
    } catch (e) {
      const message = e instanceof Error ? e.message : 'Update fehlgeschlagen'
      toast({ title: 'Fehler', description: message, variant: 'destructive' })
    }
  }, [selectedTicketId, updateMutation, toast])

  const handleRefresh = useCallback(() => {
    void ticketsQuery.refetch()
  }, [ticketsQuery])

  // Keyboard shortcuts: F1, F2, F12
  useEffect(() => {
    function onKeyDown(e: KeyboardEvent) {
      if (e.key === 'F1') {
        e.preventDefault()
        handleOpenNewDialog()
      } else if (e.key === 'F2') {
        e.preventDefault()
        void handleZweitWiegung()
      } else if (e.key === 'F12') {
        e.preventDefault()
        handleRefresh()
      }
    }
    window.addEventListener('keydown', onKeyDown)
    return () => window.removeEventListener('keydown', onKeyDown)
  }, [handleOpenNewDialog, handleZweitWiegung, handleRefresh])

  // Auto-refresh every 30s
  useEffect(() => {
    const interval = setInterval(() => {
      void ticketsQuery.refetch()
    }, 30_000)
    return () => clearInterval(interval)
  }, [ticketsQuery])

  // Reset article when group changes
  useEffect(() => {
    setFormArticleId('')
  }, [formArticleGroup])

  if (ticketsQuery.isError) {
    return <ErrorState error={ticketsQuery.error as Error} onRetry={handleRefresh} />
  }

  function formatDate(iso?: string | null): string {
    if (!iso) return '-'
    const d = new Date(iso)
    return d.toLocaleDateString('de-DE', { day: '2-digit', month: '2-digit', year: 'numeric' })
  }

  function formatTime(iso?: string | null): string {
    if (!iso) return '-'
    const d = new Date(iso)
    return d.toLocaleTimeString('de-DE', { hour: '2-digit', minute: '2-digit' })
  }

  return (
    <div className="flex flex-col h-full p-4 gap-3">
      {/* Header */}
      <div className="flex items-center justify-between">
        <h1 className="text-2xl font-bold tracking-wide uppercase">Waage - Hofliste</h1>
        <Badge variant="secondary" className="text-sm">
          {openTickets.length} offen
        </Badge>
      </div>

      {/* Toolbar */}
      <Card>
        <CardContent className="flex flex-wrap items-center gap-3 py-3">
          <Button
            className="gap-2"
            onClick={handleOpenNewDialog}
            disabled={createMutation.isPending}
          >
            <Plus className="h-4 w-4" />
            Neue Wiegung (F1)
          </Button>
          <Button
            variant="outline"
            className="gap-2"
            onClick={() => { void handleZweitWiegung() }}
            disabled={updateMutation.isPending || !selectedTicketId}
          >
            <Scale className="h-4 w-4" />
            Zweit-Wiegung (F2)
          </Button>
          <Button
            variant="outline"
            className="gap-2"
            onClick={handleRefresh}
            disabled={ticketsQuery.isFetching}
          >
            <RefreshCw className={`h-4 w-4 ${ticketsQuery.isFetching ? 'animate-spin' : ''}`} />
            Aktualisieren (F12)
          </Button>

          <div className="ml-auto flex items-center gap-2">
            <span className="text-sm text-muted-foreground whitespace-nowrap">Suche:</span>
            <Input
              className="w-48"
              placeholder="Nr., Kennzeichen, Gruppe..."
              value={searchTerm}
              onChange={(e) => setSearchTerm(e.target.value)}
            />
          </div>
        </CardContent>
      </Card>

      {/* Data Table */}
      <Card className="flex-1 overflow-auto">
        <CardContent className="pt-4">
          <DataTable
            data={filteredTickets}
            columns={[
              {
                key: 'first_weighing_at',
                label: 'Datum',
                render: (t: WeighingTicket) => formatDate(t.first_weighing_at),
              },
              {
                key: 'time',
                label: 'Uhrzeit',
                render: (t: WeighingTicket) => formatTime(t.first_weighing_at),
              },
              { key: 'ticket_number', label: 'Wiegeschein-Nr.' },
              {
                key: 'vehicle_plate',
                label: 'KFZ-Kennz.',
                render: (t: WeighingTicket) => t.vehicle_plate ?? '-',
              },
              {
                key: 'article_group',
                label: 'Warengruppe',
                render: (t: WeighingTicket) => t.article_group ?? '-',
              },
              {
                key: 'gross_weight',
                label: 'Erstgewicht',
                render: (t: WeighingTicket) => (
                  <span className="font-semibold">
                    {t.gross_weight != null ? `${Number(t.gross_weight).toFixed(0)} kg` : '-'}
                  </span>
                ),
              },
              {
                key: 'reference_doc',
                label: 'Name',
                render: (t: WeighingTicket) => t.reference_doc ?? '-',
              },
              {
                key: 'scale_id',
                label: 'Waage',
                render: (t: WeighingTicket) => t.scale_id ?? '-',
              },
              {
                key: 'status',
                label: 'Status',
                render: (t: WeighingTicket) => (
                  <Badge variant="secondary">{t.status}</Badge>
                ),
              },
              {
                key: 'actions',
                label: '',
                render: (t: WeighingTicket) => (
                  <Button
                    variant={selectedTicketId === t.id ? 'default' : 'ghost'}
                    size="sm"
                    onClick={() => setSelectedTicketId(selectedTicketId === t.id ? null : t.id)}
                  >
                    {selectedTicketId === t.id ? 'Markiert' : 'Ausw.'}
                  </Button>
                ),
              },
            ]}
          />
        </CardContent>
      </Card>

      {/* Status bar + Close */}
      <div className="flex items-center justify-between border-t pt-2 text-xs text-muted-foreground">
        <div className="flex gap-6">
          <span>Bediener: Aktueller Benutzer</span>
          <span>Firma: VALEO</span>
          <span>Niederlassung: Hauptsitz</span>
        </div>
        <Button variant="outline" size="sm" onClick={() => navigate(-1)}>
          Schliessen
        </Button>
      </div>

      {/* New Weighing Dialog */}
      <Dialog open={showNewDialog} onOpenChange={setShowNewDialog}>
        <DialogContent className="max-w-lg">
          <DialogHeader>
            <DialogTitle>Neue Wiegung anlegen</DialogTitle>
          </DialogHeader>

          <div className="grid gap-4 py-2">
            {/* KFZ-Kennzeichen */}
            <div className="grid gap-1.5">
              <Label htmlFor="nw-vehicle">KFZ-Kennzeichen</Label>
              <Input
                id="nw-vehicle"
                placeholder="z.B. VEC-AB 123"
                value={formVehiclePlate}
                onChange={(e) => setFormVehiclePlate(e.target.value)}
              />
            </div>

            {/* Warengruppe */}
            <div className="grid gap-1.5">
              <Label>Warengruppe</Label>
              <Select value={formArticleGroup} onValueChange={setFormArticleGroup}>
                <SelectTrigger>
                  <SelectValue placeholder="Warengruppe wählen..." />
                </SelectTrigger>
                <SelectContent>
                  {(articleGroupsQuery.data ?? []).map((g) => (
                    <SelectItem key={g.warengruppe} value={g.warengruppe}>
                      {g.warengruppe} ({g.count})
                    </SelectItem>
                  ))}
                </SelectContent>
              </Select>
            </div>

            {/* Artikel (abhängig von Gruppe) */}
            <div className="grid gap-1.5">
              <Label>Ware</Label>
              <Select
                value={formArticleId}
                onValueChange={setFormArticleId}
                disabled={!formArticleGroup}
              >
                <SelectTrigger>
                  <SelectValue placeholder={formArticleGroup ? 'Ware wählen...' : 'Zuerst Warengruppe wählen'} />
                </SelectTrigger>
                <SelectContent>
                  {(articlesByGroupQuery.data ?? []).map((a) => (
                    <SelectItem key={a.id} value={a.id}>
                      {a.article_number} - {a.name}
                    </SelectItem>
                  ))}
                </SelectContent>
              </Select>
            </div>

            {/* Notizen */}
            <div className="grid gap-1.5">
              <Label htmlFor="nw-notes">Notizen</Label>
              <Textarea
                id="nw-notes"
                placeholder="z.B. Dienstleistungswiegung für Firma XY"
                value={formNotes}
                onChange={(e) => setFormNotes(e.target.value)}
                rows={3}
              />
            </div>
          </div>

          <DialogFooter>
            <Button variant="outline" onClick={() => setShowNewDialog(false)}>
              Abbrechen
            </Button>
            <Button onClick={() => { void handleCreateTicket() }} disabled={createMutation.isPending}>
              {createMutation.isPending ? 'Erstelle...' : 'Wiegung anlegen'}
            </Button>
          </DialogFooter>
        </DialogContent>
      </Dialog>
    </div>
  )
}
