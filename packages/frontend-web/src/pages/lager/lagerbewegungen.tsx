import { type FormEvent, useMemo, useState } from 'react'
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
import { Edit, Plus, Search, Trash2 } from 'lucide-react'
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

export default function LagerbewegungenPage(): JSX.Element {
  const queryClient = useQueryClient()
  const { toast } = useToast()
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

  const deleteMutation = useMutation({
    mutationFn: async (id: string) => stockMovementService.deleteStockMovement(id),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['stock-movements'] })
      toast({ title: 'Lagerbewegung geloescht' })
    },
    onError: () => toast({ title: 'Loeschen fehlgeschlagen', variant: 'destructive' }),
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
    <div className="space-y-4 p-6">
      <div className="flex items-center justify-between gap-3">
        <div>
          <h1 className="text-3xl font-bold">Lagerbewegungen</h1>
          <p className="text-muted-foreground">Buchungen erfassen, aendern und loeschen</p>
        </div>
        <Button onClick={openCreateDialog}>
          <Plus className="mr-2 h-4 w-4" />
          Neue Buchung
        </Button>
      </div>

      <Card>
        <CardContent className="pt-6">
          <div className="grid gap-3 md:grid-cols-3">
            <div className="relative md:col-span-2">
              <Search className="absolute left-3 top-2.5 h-4 w-4 text-muted-foreground" />
              <Input value={search} onChange={(e) => setSearch(e.target.value)} placeholder="Suche (Beleg, Notiz, Charge, Benutzer)" className="pl-9" />
            </div>
            <NativeSelect
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
                    <Badge variant="outline">{movement.movement_type}</Badge>
                  </TableCell>
                  <TableCell className="text-right">{movement.quantity}</TableCell>
                  <TableCell>{movement.reference_number || '-'}</TableCell>
                  <TableCell>{movement.charge || '-'}</TableCell>
                  <TableCell>{movement.booking_user || '-'}</TableCell>
                  <TableCell>
                    <div className="flex gap-2">
                      <Button size="icon" variant="outline" onClick={() => openEditDialog(movement)}>
                        <Edit className="h-4 w-4" />
                      </Button>
                      <Button
                        size="icon"
                        variant="outline"
                        onClick={() => deleteMutation.mutate(movement.id)}
                        disabled={deleteMutation.isPending}
                      >
                        <Trash2 className="h-4 w-4" />
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
              <Button type="button" variant="outline" onClick={resetDialog}>Abbrechen</Button>
              <Button type="submit" disabled={createMutation.isPending || updateMutation.isPending}>
                {editing ? 'Aktualisieren' : 'Buchen'}
              </Button>
            </div>
          </form>
        </DialogContent>
      </Dialog>
    </div>
  )
}
