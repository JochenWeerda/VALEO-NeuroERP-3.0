import { type FormEvent, useMemo, useState } from 'react'
import { useNavigate, useSearchParams } from '@/app/routing/typed-router'
import { useMutation, useQuery, useQueryClient } from '@tanstack/react-query'
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card'
import { Button } from '@/components/ui/button'
import { Input } from '@/components/ui/input'
import { Label } from '@/components/ui/label'
import { Badge } from '@/components/ui/badge'
import { NativeSelect } from '@/components/ui/native-select'
import { Dialog, DialogContent, DialogHeader, DialogTitle } from '@/components/ui/dialog'
import { Table, TableBody, TableCell, TableHead, TableHeader, TableRow } from '@/components/ui/table'
import { useToast } from '@/hooks/use-toast'
import { useTouchDevice } from '@/hooks/useTouchDevice'
import { Plus, Search } from 'lucide-react'
import { apiClient } from '@/lib/api-client'
import {
  stockMovementService,
  type StockMovement,
  type StockMovementCreate,
  type StockMovementUpdate,
} from '@/lib/services/stock-movement-service'

type ArticleRef = { id: string; article_number: string; name: string }
type WarehouseRef = { id: string; warehouse_code: string; name: string }
type PagedResponse<T> = { items: T[] }

type MovementFormState = {
  article_id: string
  warehouse_id: string
  movement_type: 'in' | 'out' | 'transfer' | 'adjustment'
  quantity: string
  unit_cost: string
  unit: string
  movement_number: string
  movement_date: string
  movement_time: string
  reference_number: string
  warehouse_location: string
  charge: string
  booking_user: string
  notes: string
}

const EMPTY_FORM: MovementFormState = {
  article_id: '',
  warehouse_id: '',
  movement_type: 'in',
  quantity: '',
  unit_cost: '',
  unit: '',
  movement_number: '',
  movement_date: '',
  movement_time: '',
  reference_number: '',
  warehouse_location: '',
  charge: '',
  booking_user: '',
  notes: '',
}

const MOVEMENT_TYPE_LABEL: Record<MovementFormState['movement_type'], string> = {
  in: 'Zugang',
  out: 'Abgang',
  transfer: 'Umbuchung',
  adjustment: 'Korrektur',
}

export default function LagerbewegungenPage(): JSX.Element {
  const queryClient = useQueryClient()
  const { toast } = useToast()
  const navigate = useNavigate()
  const isTouch = useTouchDevice()
  const [searchParams] = useSearchParams()
  const workflowInstanceId = searchParams.get('workflowInstanceId')
  const workflowProcess = searchParams.get('workflowProcess')
  const workflowCase = searchParams.get('workflowCase')
  const [search, setSearch] = useState('')
  const [movementTypeFilter, setMovementTypeFilter] = useState<string>('all')
  const [dialogOpen, setDialogOpen] = useState(false)
  const [editing, setEditing] = useState<StockMovement | null>(null)
  const [form, setForm] = useState<MovementFormState>(EMPTY_FORM)

  const { data: movementsData, isLoading } = useQuery({
    queryKey: ['stock-movements', { search, movementTypeFilter }],
    queryFn: async () =>
      stockMovementService.getStockMovements({
        search: search || undefined,
        movement_type: movementTypeFilter === 'all' ? undefined : movementTypeFilter,
        limit: 100,
      }),
  })

  const { data: articlesData } = useQuery({
    queryKey: ['inventory-articles-ref'],
    queryFn: async () => (await apiClient.get<PagedResponse<ArticleRef>>('/api/v1/inventory/articles?limit=200')).data,
  })

  const { data: warehousesData } = useQuery({
    queryKey: ['inventory-warehouses-ref'],
    queryFn: async () => (await apiClient.get<PagedResponse<WarehouseRef>>('/api/v1/inventory/warehouses?limit=200')).data,
  })

  const articles = articlesData?.items ?? []
  const warehouses = warehousesData?.items ?? []
  const movements = movementsData?.items ?? []

  const articleMap = useMemo(() => new Map(articles.map((a) => [a.id, a])), [articles])
  const warehouseMap = useMemo(() => new Map(warehouses.map((w) => [w.id, w])), [warehouses])

  const fallkopf = useMemo(() => {
    const total = movements.length
    const zugaenge = movements.filter((m) => m.movement_type === 'in').length
    const abgaenge = movements.filter((m) => m.movement_type === 'out').length
    const korrekturen = movements.filter((m) => m.movement_type === 'adjustment').length
    const hatBewegungen = total > 0
    return {
      status: hatBewegungen ? `${total} Bewegungen erfasst` : 'Keine Bewegungen',
      statusColor: korrekturen > 0 ? 'border-status-warning/40 bg-status-warning/10' : hatBewegungen ? 'border-status-success/40 bg-status-success/10' : 'border-border bg-muted/40',
      bewegungsdruck: `${zugaenge} Zugaenge, ${abgaenge} Abgaenge, ${korrekturen} Korrekturen`,
      auditLage: korrekturen > 0 ? `${korrekturen} Korrektur(en) — Audit-relevant` : 'Keine Korrekturen',
      folgepfad: korrekturen > 0 ? 'Korrekturbuchungen pruefen' : hatBewegungen ? 'Bewegungsjournal aktuell' : 'Neue Buchung erfassen',
    }
  }, [movements])


  const resetDialog = () => {
    setEditing(null)
    setForm(EMPTY_FORM)
    setDialogOpen(false)
  }

  const openCreateDialog = () => {
    setEditing(null)
    setForm({
      ...EMPTY_FORM,
      article_id: articles[0]?.id ?? '',
      warehouse_id: warehouses[0]?.id ?? '',
      movement_date: new Date().toISOString().slice(0, 10),
    })
    setDialogOpen(true)
  }

  const openEditDialog = (movement: StockMovement) => {
    setEditing(movement)
    setForm({
      article_id: movement.article_id,
      warehouse_id: movement.warehouse_id,
      movement_type: movement.movement_type,
      quantity: String(movement.quantity),
      unit_cost: movement.unit_cost != null ? String(movement.unit_cost) : '',
      unit: movement.unit ?? '',
      movement_number: movement.movement_number ?? '',
      movement_date: movement.movement_date ?? '',
      movement_time: movement.movement_time ?? '',
      reference_number: movement.reference_number ?? '',
      warehouse_location: movement.warehouse_location ?? '',
      charge: movement.charge ?? '',
      booking_user: movement.booking_user ?? '',
      notes: movement.notes ?? '',
    })
    setDialogOpen(true)
  }

  const createMutation = useMutation({
    mutationFn: async (payload: StockMovementCreate) => stockMovementService.createStockMovement(payload),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['stock-movements'] })
      toast({ title: 'Lagerbewegung erstellt' })
      resetDialog()
    },
    onError: () => toast({ title: 'Fehler beim Erstellen', variant: 'destructive' }),
  })

  const updateMutation = useMutation({
    mutationFn: async ({ id, payload }: { id: string; payload: StockMovementUpdate }) =>
      stockMovementService.updateStockMovement(id, payload),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['stock-movements'] })
      toast({ title: 'Lagerbewegung aktualisiert' })
      resetDialog()
    },
    onError: () => toast({ title: 'Fehler beim Aktualisieren', variant: 'destructive' }),
  })


  const onSubmit = async (event: FormEvent<HTMLFormElement>) => {
    event.preventDefault()

    if (!form.article_id || !form.warehouse_id || !form.quantity) {
      toast({ title: 'Pflichtfelder fehlen', description: 'Artikel, Lager und Menge sind erforderlich.', variant: 'destructive' })
      return
    }

    if (editing) {
      const payload: StockMovementUpdate = {
        movement_number: form.movement_number || undefined,
        movement_date: form.movement_date || undefined,
        movement_time: form.movement_time || undefined,
        unit: form.unit || undefined,
        reference_number: form.reference_number || undefined,
        notes: form.notes || undefined,
        warehouse_location: form.warehouse_location || undefined,
        charge: form.charge || undefined,
        booking_user: form.booking_user || undefined,
      }
      await updateMutation.mutateAsync({ id: editing.id, payload })
      return
    }

    const payload: StockMovementCreate = {
      article_id: form.article_id,
      warehouse_id: form.warehouse_id,
      movement_type: form.movement_type,
      quantity: Number(form.quantity),
      unit_cost: form.unit_cost ? Number(form.unit_cost) : undefined,
      unit: form.unit || undefined,
      movement_number: form.movement_number || undefined,
      movement_date: form.movement_date || undefined,
      movement_time: form.movement_time || undefined,
      reference_number: form.reference_number || undefined,
      notes: form.notes || undefined,
      warehouse_location: form.warehouse_location || undefined,
      charge: form.charge || undefined,
      booking_user: form.booking_user || undefined,
    }
    await createMutation.mutateAsync(payload)
  }

  return (
    <div className="space-y-4 p-3 md:p-6" data-density="expertDense">
      {!isTouch ? (
      <>
      {workflowInstanceId && (
        <div className="mb-4 rounded-md border border-border bg-muted/40 px-4 py-2 text-sm">
          Belegkette: {workflowCase || workflowProcess} (Instanz {workflowInstanceId.slice(0, 8)}...)
        </div>
      )}
      <Card className={`border ${fallkopf.statusColor}`}>
        <CardContent className="pt-4 pb-3 text-sm space-y-1">
          <div className="font-semibold">Bewegungslage: {fallkopf.status}</div>
          <div>Bewegungsdruck: {fallkopf.bewegungsdruck}</div>
          <div>Audit-Lage: {fallkopf.auditLage}</div>
          <div>Folgepfad: {fallkopf.folgepfad}</div>
        </CardContent>
      </Card>
      </>
      ) : null}

      <div className="flex flex-col gap-3 sm:flex-row sm:items-start sm:justify-between">
        <div>
          <h1 className="text-xl font-semibold tracking-tight">Lagerbewegungen</h1>
          <p className="text-muted-foreground">Buchungen suchen, erfassen und stornieren</p>
        </div>
        <Button onClick={openCreateDialog} className="min-h-touch touch-manipulation">
          <Plus className="mr-2 h-4 w-4" />
          Neue Buchung
        </Button>
      </div>

      <Card>
        <CardContent className="pt-6">
          <div className="grid gap-3 md:grid-cols-3">
            <div className="relative md:col-span-2">
              <Search className="absolute left-3 top-1/2 h-4 w-4 -translate-y-1/2 text-muted-foreground" />
              <Input
                aria-label="Suche Lagerbewegungen"
                value={search}
                onChange={(e) => setSearch(e.target.value)}
                placeholder="Beleg, Notiz, Charge, Benutzer"
                className="min-h-touch pl-9"
              />
            </div>
            <NativeSelect
              ariaLabel="Bewegungstyp"
              value={movementTypeFilter}
              onValueChange={setMovementTypeFilter}
              placeholder="Bewegungstyp"
              options={[
                { value: 'all', label: 'Alle Typen' },
                { value: 'in', label: 'Zugang' },
                { value: 'out', label: 'Abgang' },
                { value: 'transfer', label: 'Umbuchung' },
                { value: 'adjustment', label: 'Korrektur' },
              ]}
            />
          </div>
        </CardContent>
      </Card>

      <Card>
        <CardHeader>
          <CardTitle>Bewegungen ({movements.length})</CardTitle>
        </CardHeader>
        <CardContent>
          <Table>
            <TableHeader>
              <TableRow>
                <TableHead>Nr.</TableHead>
                <TableHead>Artikel</TableHead>
                <TableHead>Lager</TableHead>
                <TableHead>Typ</TableHead>
                <TableHead className="text-right">Menge</TableHead>
                <TableHead>Beleg</TableHead>
                <TableHead>Charge</TableHead>
                <TableHead>Benutzer</TableHead>
                <TableHead>Aktionen</TableHead>
              </TableRow>
            </TableHeader>
            <TableBody>
              {!isLoading && movements.length === 0 && (
                <TableRow>
                  <TableCell colSpan={9} className="text-center text-muted-foreground">
                    Keine Lagerbewegungen gefunden.
                  </TableCell>
                </TableRow>
              )}
              {movements.map((movement) => (
                <TableRow key={movement.id}>
                  <TableCell className="font-mono text-xs">{movement.movement_number || movement.id.slice(0, 8)}</TableCell>
                  <TableCell>{articleMap.get(movement.article_id)?.name || movement.article_id}</TableCell>
                  <TableCell>{warehouseMap.get(movement.warehouse_id)?.name || movement.warehouse_id}</TableCell>
                  <TableCell>
                    <Badge variant="outline">
                      {MOVEMENT_TYPE_LABEL[movement.movement_type] ?? movement.movement_type}
                    </Badge>
                  </TableCell>
                  <TableCell className="text-right">{movement.quantity}</TableCell>
                  <TableCell>{movement.reference_number || '-'}</TableCell>
                  <TableCell>{movement.charge || '-'}</TableCell>
                  <TableCell>{movement.booking_user || '-'}</TableCell>
                  <TableCell>
                    <div className="flex flex-col gap-2 sm:flex-row">
                      <Button
                        variant="outline"
                        className="min-h-touch touch-manipulation"
                        onClick={() => openEditDialog(movement)}
                      >
                        Bearbeiten
                      </Button>
                      {/* Gebuchte Bewegungen werden storniert, nicht geloescht: die
                          Stornoaktion (Gegenbuchung mit Begruendung) liegt in der
                          Detailmaske aus der ScreenDefinition lager/stock-movement. */}
                      <Button
                        variant="outline"
                        className="min-h-touch touch-manipulation"
                        onClick={() => navigate(`/lager/stock-movement/${movement.id}`)}
                      >
                        Stornieren…
                      </Button>
                    </div>
                  </TableCell>
                </TableRow>
              ))}
            </TableBody>
          </Table>
        </CardContent>
      </Card>

      <Dialog open={dialogOpen} onOpenChange={(open) => (open ? setDialogOpen(true) : resetDialog())}>
        <DialogContent className="max-w-3xl">
          <DialogHeader>
            <DialogTitle>{editing ? 'Lagerbewegung bearbeiten' : 'Lagerbewegung erfassen'}</DialogTitle>
          </DialogHeader>

          <form onSubmit={onSubmit} className="grid gap-4 md:grid-cols-2">
            <div className="space-y-2">
              <Label>Artikel</Label>
              <NativeSelect
                ariaLabel="Artikel"
                value={form.article_id}
                onValueChange={(value) => setForm((prev) => ({ ...prev, article_id: value }))}
                disabled={Boolean(editing)}
                placeholder="Artikel waehlen"
                options={articles.map((article) => ({
                  value: article.id,
                  label: `${article.article_number} - ${article.name}`,
                }))}
              />
            </div>

            <div className="space-y-2">
              <Label>Lager</Label>
              <NativeSelect
                ariaLabel="Lager"
                value={form.warehouse_id}
                onValueChange={(value) => setForm((prev) => ({ ...prev, warehouse_id: value }))}
                disabled={Boolean(editing)}
                placeholder="Lager waehlen"
                options={warehouses.map((warehouse) => ({
                  value: warehouse.id,
                  label: `${warehouse.warehouse_code} - ${warehouse.name}`,
                }))}
              />
            </div>

            <div className="space-y-2">
              <Label>Bewegungstyp</Label>
              <NativeSelect
                ariaLabel="Bewegungstyp"
                value={form.movement_type}
                onValueChange={(value) =>
                  setForm((prev) => ({ ...prev, movement_type: value as MovementFormState['movement_type'] }))
                }
                disabled={Boolean(editing)}
                options={[
                  { value: 'in', label: 'Zugang' },
                  { value: 'out', label: 'Abgang' },
                  { value: 'transfer', label: 'Umbuchung' },
                  { value: 'adjustment', label: 'Korrektur' },
                ]}
              />
            </div>

            <div className="space-y-2">
              <Label>Menge</Label>
              <Input
                type="number"
                step="0.01"
                value={form.quantity}
                onChange={(e) => setForm((prev) => ({ ...prev, quantity: e.target.value }))}
                disabled={Boolean(editing)}
                required
              />
            </div>

            <div className="space-y-2">
              <Label>Bewegungsnummer</Label>
              <Input value={form.movement_number} onChange={(e) => setForm((prev) => ({ ...prev, movement_number: e.target.value }))} />
            </div>

            <div className="space-y-2">
              <Label>Einheit</Label>
              <Input value={form.unit} onChange={(e) => setForm((prev) => ({ ...prev, unit: e.target.value }))} placeholder="kg / l / Stk" />
            </div>

            <div className="space-y-2">
              <Label>Buchungsdatum</Label>
              <Input type="date" value={form.movement_date} onChange={(e) => setForm((prev) => ({ ...prev, movement_date: e.target.value }))} />
            </div>

            <div className="space-y-2">
              <Label>Buchungszeit</Label>
              <Input type="time" value={form.movement_time} onChange={(e) => setForm((prev) => ({ ...prev, movement_time: e.target.value }))} />
            </div>

            <div className="space-y-2">
              <Label>Belegnummer</Label>
              <Input value={form.reference_number} onChange={(e) => setForm((prev) => ({ ...prev, reference_number: e.target.value }))} />
            </div>

            <div className="space-y-2">
              <Label>Lagerort</Label>
              <Input value={form.warehouse_location} onChange={(e) => setForm((prev) => ({ ...prev, warehouse_location: e.target.value }))} />
            </div>

            <div className="space-y-2">
              <Label>Charge</Label>
              <Input value={form.charge} onChange={(e) => setForm((prev) => ({ ...prev, charge: e.target.value }))} />
            </div>

            <div className="space-y-2">
              <Label>Benutzer</Label>
              <Input value={form.booking_user} onChange={(e) => setForm((prev) => ({ ...prev, booking_user: e.target.value }))} />
            </div>

            {!editing && (
              <div className="space-y-2">
                <Label>Einstandspreis</Label>
                <Input type="number" step="0.01" value={form.unit_cost} onChange={(e) => setForm((prev) => ({ ...prev, unit_cost: e.target.value }))} />
              </div>
            )}

            <div className="space-y-2 md:col-span-2">
              <Label>Buchungstext</Label>
              <Input value={form.notes} onChange={(e) => setForm((prev) => ({ ...prev, notes: e.target.value }))} />
            </div>

            <div className="md:col-span-2 flex justify-end gap-2">
              <Button type="button" variant="outline" className="min-h-touch touch-manipulation" onClick={resetDialog}>Abbrechen</Button>
              <Button type="submit" className="min-h-touch touch-manipulation" disabled={createMutation.isPending || updateMutation.isPending}>
                {editing ? 'Aktualisieren' : 'Buchen'}
              </Button>
            </div>
          </form>
        </DialogContent>
      </Dialog>
    </div>
  )
}
