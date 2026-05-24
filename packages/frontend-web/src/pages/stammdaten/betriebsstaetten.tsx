import { useState } from 'react'
import { useForm } from 'react-hook-form'
import { toast } from 'sonner'
import {
  useBetriebsstaetten,
  useCreateBetriebsstaette,
  useUpdateBetriebsstaette,
  useDeleteBetriebsstaette,
  type Betriebsstaette,
  type BetriebsstaetteCreate,
} from '@/lib/api/betriebsstaetten'
import {
  Card,
  CardContent,
  CardHeader,
  CardTitle,
} from '@/components/ui/card'
import { Button } from '@/components/ui/button'
import { Input } from '@/components/ui/input'
import { Label } from '@/components/ui/label'
import { Checkbox } from '@/components/ui/checkbox'
import {
  Table,
  TableBody,
  TableCell,
  TableHead,
  TableHeader,
  TableRow,
} from '@/components/ui/table'
import { Badge } from '@/components/ui/badge'
import { Skeleton } from '@/components/ui/skeleton'
import {
  Dialog,
  DialogContent,
  DialogHeader,
  DialogTitle,
  DialogFooter,
} from '@/components/ui/dialog'
import { Trash2, Plus, Pencil, MapPin, Building2 } from 'lucide-react'

type FormData = {
  filial_nr: string
  bezeichnung: string
  ist_zentrale: boolean
  zentrale_filial_nr: string
  ident_untergrenze: string
  ident_obergrenze: string
  strasse: string
  plz: string
  ort: string
  land: string
  telefon: string
  email: string
}

function formDataToPayload(data: FormData): BetriebsstaetteCreate {
  return {
    filial_nr: data.filial_nr,
    bezeichnung: data.bezeichnung,
    ist_zentrale: data.ist_zentrale,
    zentrale_filial_nr: data.zentrale_filial_nr || null,
    ident_untergrenze: data.ident_untergrenze ? parseInt(data.ident_untergrenze) : null,
    ident_obergrenze: data.ident_obergrenze ? parseInt(data.ident_obergrenze) : null,
    strasse: data.strasse || null,
    plz: data.plz || null,
    ort: data.ort || null,
    land: data.land || null,
    telefon: data.telefon || null,
    email: data.email || null,
  }
}

function betriebsstaetteToForm(b: Betriebsstaette): FormData {
  return {
    filial_nr: b.filial_nr,
    bezeichnung: b.bezeichnung,
    ist_zentrale: b.ist_zentrale,
    zentrale_filial_nr: b.zentrale_filial_nr ?? '',
    ident_untergrenze: b.ident_untergrenze?.toString() ?? '',
    ident_obergrenze: b.ident_obergrenze?.toString() ?? '',
    strasse: b.strasse ?? '',
    plz: b.plz ?? '',
    ort: b.ort ?? '',
    land: b.land ?? '',
    telefon: b.telefon ?? '',
    email: b.email ?? '',
  }
}

function BetriebsstaetteForm({
  onSubmit,
  isPending,
  defaultValues,
  readonlyNr,
}: {
  onSubmit: (data: FormData) => Promise<void>
  isPending: boolean
  defaultValues?: Partial<FormData>
  readonlyNr?: boolean
}) {
  const { register, handleSubmit, watch, setValue, reset } = useForm<FormData>({
    defaultValues: {
      filial_nr: '',
      bezeichnung: '',
      ist_zentrale: false,
      zentrale_filial_nr: '',
      ident_untergrenze: '',
      ident_obergrenze: '',
      strasse: '',
      plz: '',
      ort: '',
      land: 'DE',
      telefon: '',
      email: '',
      ...defaultValues,
    },
  })

  const istZentrale = watch('ist_zentrale')

  const handleFormSubmit = handleSubmit(async (data) => {
    await onSubmit(data)
    if (!readonlyNr) reset()
  })

  return (
    <form onSubmit={handleFormSubmit} className="space-y-4">
      <div className="grid grid-cols-1 sm:grid-cols-3 gap-4">
        <div className="space-y-1">
          <Label htmlFor="filial_nr">Filialnummer *</Label>
          <Input
            id="filial_nr"
            placeholder="z.B. 001"
            readOnly={readonlyNr}
            {...register('filial_nr', { required: true })}
          />
        </div>
        <div className="space-y-1 sm:col-span-2">
          <Label htmlFor="bezeichnung">Bezeichnung *</Label>
          <Input
            id="bezeichnung"
            placeholder="Filialname"
            {...register('bezeichnung', { required: true })}
          />
        </div>
      </div>

      <div className="flex items-center gap-3">
        <Checkbox
          id="ist_zentrale"
          checked={istZentrale}
          onCheckedChange={(checked) => setValue('ist_zentrale', !!checked)}
          aria-label="Ist Zentrale"
        />
        <Label htmlFor="ist_zentrale" className="cursor-pointer">Ist Zentrale / Hauptstelle</Label>
      </div>

      {!istZentrale && (
        <div className="space-y-1">
          <Label htmlFor="zentrale_filial_nr">Filialnr. Zentrale</Label>
          <Input
            id="zentrale_filial_nr"
            placeholder="optional, übergeordnete Zentrale"
            {...register('zentrale_filial_nr')}
          />
        </div>
      )}

      <div className="grid grid-cols-1 sm:grid-cols-2 gap-4">
        <div className="space-y-1">
          <Label htmlFor="ident_untergrenze">Ident-Untergrenze</Label>
          <Input
            id="ident_untergrenze"
            type="number"
            placeholder="optional"
            {...register('ident_untergrenze')}
          />
        </div>
        <div className="space-y-1">
          <Label htmlFor="ident_obergrenze">Ident-Obergrenze</Label>
          <Input
            id="ident_obergrenze"
            type="number"
            placeholder="optional"
            {...register('ident_obergrenze')}
          />
        </div>
      </div>

      <div className="border rounded-md p-4 space-y-3">
        <p className="text-sm font-medium text-muted-foreground flex items-center gap-1">
          <MapPin className="h-4 w-4" /> Adresse
        </p>
        <div className="space-y-1">
          <Label htmlFor="strasse">Straße</Label>
          <Input id="strasse" placeholder="Straße und Hausnummer" {...register('strasse')} />
        </div>
        <div className="grid grid-cols-3 gap-3">
          <div className="space-y-1">
            <Label htmlFor="plz">PLZ</Label>
            <Input id="plz" placeholder="PLZ" {...register('plz')} />
          </div>
          <div className="space-y-1 col-span-2">
            <Label htmlFor="ort">Ort</Label>
            <Input id="ort" placeholder="Ort" {...register('ort')} />
          </div>
        </div>
        <div className="space-y-1">
          <Label htmlFor="land">Land</Label>
          <Input id="land" placeholder="DE" {...register('land')} />
        </div>
      </div>

      <div className="grid grid-cols-1 sm:grid-cols-2 gap-4">
        <div className="space-y-1">
          <Label htmlFor="telefon">Telefon</Label>
          <Input id="telefon" type="tel" placeholder="optional" {...register('telefon')} />
        </div>
        <div className="space-y-1">
          <Label htmlFor="email">E-Mail</Label>
          <Input id="email" type="email" placeholder="optional" {...register('email')} />
        </div>
      </div>

      <div className="flex justify-end">
        <Button type="submit" disabled={isPending} className="gap-2">
          <Plus className="h-4 w-4" />
          {isPending ? 'Speichern…' : 'Speichern'}
        </Button>
      </div>
    </form>
  )
}

function EditDialog({
  betriebsstaette,
  open,
  onClose,
}: {
  betriebsstaette: Betriebsstaette
  open: boolean
  onClose: () => void
}) {
  const updateMutation = useUpdateBetriebsstaette()

  const handleSubmit = async (data: FormData) => {
    try {
      await updateMutation.mutateAsync({
        filialNr: betriebsstaette.filial_nr,
        payload: formDataToPayload(data),
      })
      toast.success(`Betriebsstätte ${betriebsstaette.filial_nr} aktualisiert`)
      onClose()
    } catch {
      toast.error('Fehler beim Aktualisieren')
    }
  }

  return (
    <Dialog open={open} onOpenChange={onClose}>
      <DialogContent className="max-w-2xl max-h-[85vh] overflow-y-auto">
        <DialogHeader>
          <DialogTitle>Betriebsstätte bearbeiten — {betriebsstaette.filial_nr}</DialogTitle>
        </DialogHeader>
        <BetriebsstaetteForm
          onSubmit={handleSubmit}
          isPending={updateMutation.isPending}
          defaultValues={betriebsstaetteToForm(betriebsstaette)}
          readonlyNr
        />
        <DialogFooter />
      </DialogContent>
    </Dialog>
  )
}

export default function BetriebsstaettenPage() {
  const [showForm, setShowForm] = useState(false)
  const [editTarget, setEditTarget] = useState<Betriebsstaette | null>(null)
  const [deletingNr, setDeletingNr] = useState<string | null>(null)

  const { data: betriebsstaetten, isLoading } = useBetriebsstaetten()
  const createMutation = useCreateBetriebsstaette()
  const deleteMutation = useDeleteBetriebsstaette()

  const handleCreate = async (data: FormData) => {
    try {
      await createMutation.mutateAsync(formDataToPayload(data))
      toast.success(`Betriebsstätte ${data.filial_nr} angelegt`)
      setShowForm(false)
    } catch {
      toast.error('Fehler beim Anlegen der Betriebsstätte')
    }
  }

  const handleDelete = async (filialNr: string) => {
    if (deletingNr) return
    setDeletingNr(filialNr)
    try {
      await deleteMutation.mutateAsync(filialNr)
      toast.success(`Betriebsstätte ${filialNr} deaktiviert`)
    } catch {
      toast.error('Fehler beim Deaktivieren')
    } finally {
      setDeletingNr(null)
    }
  }

  return (
    <div className="p-6 space-y-4">
      <div className="flex items-start justify-between">
        <div>
          <h1 className="text-2xl font-semibold">Betriebsstätten &amp; Filialen [FILS]</h1>
          <p className="text-muted-foreground text-sm mt-1">
            Filialsystem-Stammdaten: Filialen, Zentralen und Ident-Nummernkreise.
          </p>
        </div>
        <Button
          onClick={() => setShowForm(!showForm)}
          className="gap-2 shrink-0"
          aria-label="Neue Betriebsstätte anlegen"
        >
          <Plus className="h-4 w-4" />
          Neue Betriebsstätte
        </Button>
      </div>

      {showForm && (
        <Card>
          <CardHeader>
            <CardTitle className="text-base">Neue Betriebsstätte</CardTitle>
          </CardHeader>
          <CardContent>
            <BetriebsstaetteForm
              onSubmit={handleCreate}
              isPending={createMutation.isPending}
            />
          </CardContent>
        </Card>
      )}

      <Card>
        <CardHeader>
          <CardTitle className="text-base">Betriebsstätten</CardTitle>
        </CardHeader>
        <CardContent>
          {isLoading ? (
            <div className="space-y-2">
              {Array.from({ length: 4 }).map((_, i) => (
                <Skeleton key={i} className="h-12 w-full" />
              ))}
            </div>
          ) : (
            <Table>
              <TableHeader>
                <TableRow>
                  <TableHead>Filialnr</TableHead>
                  <TableHead>Bezeichnung</TableHead>
                  <TableHead>Typ</TableHead>
                  <TableHead>Ort</TableHead>
                  <TableHead>Ident-Bereich</TableHead>
                  <TableHead>Untergeordnete</TableHead>
                  <TableHead className="w-24" />
                </TableRow>
              </TableHeader>
              <TableBody>
                {betriebsstaetten?.length === 0 && (
                  <TableRow>
                    <TableCell colSpan={7} className="text-center text-muted-foreground py-8">
                      Keine Betriebsstätten vorhanden
                    </TableCell>
                  </TableRow>
                )}
                {betriebsstaetten?.map((b) => (
                  <TableRow key={b.id}>
                    <TableCell className="font-mono">{b.filial_nr}</TableCell>
                    <TableCell>
                      <span className="flex items-center gap-2">
                        <Building2 className="h-4 w-4 text-muted-foreground shrink-0" />
                        {b.bezeichnung}
                      </span>
                    </TableCell>
                    <TableCell>
                      {b.ist_zentrale ? (
                        <Badge variant="default">Zentrale</Badge>
                      ) : (
                        <Badge variant="secondary">Filiale</Badge>
                      )}
                    </TableCell>
                    <TableCell className="text-sm">
                      {[b.plz, b.ort].filter(Boolean).join(' ') || '—'}
                    </TableCell>
                    <TableCell className="text-sm tabular-nums">
                      {b.ident_untergrenze != null && b.ident_obergrenze != null
                        ? `${b.ident_untergrenze} – ${b.ident_obergrenze}`
                        : '—'}
                    </TableCell>
                    <TableCell className="text-sm">
                      {b.untergeordnete.length > 0
                        ? b.untergeordnete.join(', ')
                        : '—'}
                    </TableCell>
                    <TableCell>
                      <div className="flex gap-1">
                        <Button
                          variant="ghost"
                          size="sm"
                          onClick={() => setEditTarget(b)}
                          aria-label={`Betriebsstätte ${b.filial_nr} bearbeiten`}
                        >
                          <Pencil className="h-4 w-4" />
                        </Button>
                        <Button
                          variant="ghost"
                          size="sm"
                          disabled={deletingNr === b.filial_nr}
                          onClick={() => handleDelete(b.filial_nr)}
                          aria-label={`Betriebsstätte ${b.filial_nr} deaktivieren`}
                        >
                          <Trash2 className="h-4 w-4 text-destructive" />
                        </Button>
                      </div>
                    </TableCell>
                  </TableRow>
                ))}
              </TableBody>
            </Table>
          )}
        </CardContent>
      </Card>

      {editTarget && (
        <EditDialog
          betriebsstaette={editTarget}
          open={!!editTarget}
          onClose={() => setEditTarget(null)}
        />
      )}
    </div>
  )
}
