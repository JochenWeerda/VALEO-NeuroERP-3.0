import { useState } from 'react'
import { useForm } from 'react-hook-form'
import { toast } from 'sonner'
import { Plus, Pencil, Trash2 } from 'lucide-react'
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card'
import { Button } from '@/components/ui/button'
import { Input } from '@/components/ui/input'
import { Label } from '@/components/ui/label'
import { Skeleton } from '@/components/ui/skeleton'
import { Badge } from '@/components/ui/badge'
import { Checkbox } from '@/components/ui/checkbox'
import {
  Table, TableBody, TableCell, TableHead, TableHeader, TableRow,
} from '@/components/ui/table'
import {
  Dialog, DialogContent, DialogHeader, DialogTitle, DialogFooter,
} from '@/components/ui/dialog'
import {
  useHausbanken,
  useCreateHausbank,
  useUpdateHausbank,
  useDeleteHausbank,
  type Hausbank,
  type HausbankCreate,
} from '@/lib/api/hausbanken'

// ── Form ───────────────────────────────────────────────────────────────────────

type FormData = {
  bank_nr: string
  bezeichnung: string
  iban: string
  bic: string
  bank_name: string
  kontonummer: string
  blz: string
  waehrung: string
  sepa_glaeubiger_id: string
  erechnung_aktiv: boolean
  standard: boolean
}

function formToPayload(data: FormData): HausbankCreate {
  return {
    bank_nr: data.bank_nr,
    bezeichnung: data.bezeichnung,
    iban: data.iban.replace(/\s/g, '').toUpperCase(),
    bic: data.bic || null,
    bank_name: data.bank_name || null,
    kontonummer: data.kontonummer || null,
    blz: data.blz || null,
    waehrung: data.waehrung || 'EUR',
    sepa_glaeubiger_id: data.sepa_glaeubiger_id || null,
    erechnung_aktiv: data.erechnung_aktiv,
    standard: data.standard,
  }
}

function hausbankToForm(b: Hausbank): FormData {
  return {
    bank_nr: b.bank_nr,
    bezeichnung: b.bezeichnung,
    iban: b.iban,
    bic: b.bic ?? '',
    bank_name: b.bank_name ?? '',
    kontonummer: b.kontonummer ?? '',
    blz: b.blz ?? '',
    waehrung: b.waehrung,
    sepa_glaeubiger_id: b.sepa_glaeubiger_id ?? '',
    erechnung_aktiv: b.erechnung_aktiv,
    standard: b.standard,
  }
}

// ── Hausbank Form ──────────────────────────────────────────────────────────────

function HausbankForm({
  onSubmit,
  isPending,
  defaultValues,
  readonlyNr = false,
}: {
  onSubmit: (data: FormData) => void
  isPending: boolean
  defaultValues?: Partial<FormData>
  readonlyNr?: boolean
}) {
  const { register, handleSubmit, setValue, watch, formState: { errors } } = useForm<FormData>({
    defaultValues: {
      waehrung: 'EUR',
      erechnung_aktiv: false,
      standard: false,
      ...defaultValues,
    },
  })

  return (
    <form onSubmit={handleSubmit(onSubmit)} className="grid gap-3">
      <div className="grid grid-cols-2 gap-3">
        <div className="grid gap-1">
          <Label htmlFor="hb_nr">Bank-Nr *</Label>
          <Input
            id="hb_nr"
            placeholder="HB01"
            aria-label="Bank-Nr"
            readOnly={readonlyNr}
            className={readonlyNr ? 'bg-muted' : ''}
            {...register('bank_nr', { required: true })}
          />
          {errors.bank_nr && <span className="text-xs text-destructive">Pflichtfeld</span>}
        </div>
        <div className="grid gap-1">
          <Label htmlFor="hb_bez">Bezeichnung *</Label>
          <Input id="hb_bez" placeholder="Hausbank Muster" aria-label="Bezeichnung" {...register('bezeichnung', { required: true })} />
          {errors.bezeichnung && <span className="text-xs text-destructive">Pflichtfeld</span>}
        </div>
      </div>
      <div className="grid gap-1">
        <Label htmlFor="hb_iban">IBAN *</Label>
        <Input
          id="hb_iban"
          placeholder="DE89 3704 0044 0532 0130 00"
          aria-label="IBAN"
          className="font-mono"
          {...register('iban', { required: true })}
        />
        {errors.iban && <span className="text-xs text-destructive">Pflichtfeld</span>}
      </div>
      <div className="grid grid-cols-3 gap-3">
        <div className="grid gap-1">
          <Label htmlFor="hb_bic">BIC</Label>
          <Input id="hb_bic" placeholder="DEUTDEDB" aria-label="BIC" className="font-mono" {...register('bic')} />
        </div>
        <div className="grid gap-1">
          <Label htmlFor="hb_bankname">Bank-Name</Label>
          <Input id="hb_bankname" placeholder="Deutsche Bank" aria-label="Bank-Name" {...register('bank_name')} />
        </div>
        <div className="grid gap-1">
          <Label htmlFor="hb_waehrung">Währung</Label>
          <Input id="hb_waehrung" placeholder="EUR" maxLength={3} aria-label="Währung" {...register('waehrung')} />
        </div>
      </div>
      <div className="grid grid-cols-3 gap-3">
        <div className="grid gap-1">
          <Label htmlFor="hb_kontonr">Kontonummer</Label>
          <Input id="hb_kontonr" aria-label="Kontonummer" {...register('kontonummer')} />
        </div>
        <div className="grid gap-1">
          <Label htmlFor="hb_blz">BLZ</Label>
          <Input id="hb_blz" aria-label="Bankleitzahl" maxLength={10} {...register('blz')} />
        </div>
        <div className="grid gap-1">
          <Label htmlFor="hb_sepa">SEPA Gläubiger-ID</Label>
          <Input id="hb_sepa" aria-label="SEPA Gläubiger-ID" {...register('sepa_glaeubiger_id')} />
        </div>
      </div>
      <div className="flex gap-6 items-center">
        <div className="flex items-center gap-2">
          <Checkbox
            id="hb_erechnung"
            checked={watch('erechnung_aktiv')}
            onCheckedChange={(v) => setValue('erechnung_aktiv', !!v)}
            aria-label="eRechnung aktiv"
          />
          <Label htmlFor="hb_erechnung" className="cursor-pointer">eRechnung aktiv</Label>
        </div>
        <div className="flex items-center gap-2">
          <Checkbox
            id="hb_standard"
            checked={watch('standard')}
            onCheckedChange={(v) => setValue('standard', !!v)}
            aria-label="Standard-Hausbank"
          />
          <Label htmlFor="hb_standard" className="cursor-pointer">Standard-Hausbank</Label>
        </div>
      </div>
      <div className="flex justify-end pt-1">
        <Button type="submit" disabled={isPending} aria-label="Hausbank speichern">
          {isPending ? 'Wird gespeichert…' : 'Speichern'}
        </Button>
      </div>
    </form>
  )
}

// ── Edit Dialog ────────────────────────────────────────────────────────────────

function EditDialog({
  hausbank,
  open,
  onClose,
}: {
  hausbank: Hausbank
  open: boolean
  onClose: () => void
}) {
  const update = useUpdateHausbank()

  const handleSubmit = async (data: FormData) => {
    try {
      await update.mutateAsync({ bankNr: hausbank.bank_nr, payload: formToPayload(data) })
      toast.success('Hausbank gespeichert.')
      onClose()
    } catch {
      toast.error('Fehler beim Speichern der Hausbank.')
    }
  }

  return (
    <Dialog open={open} onOpenChange={onClose}>
      <DialogContent className="max-w-xl">
        <DialogHeader>
          <DialogTitle>Hausbank bearbeiten — {hausbank.bank_nr}</DialogTitle>
        </DialogHeader>
        <HausbankForm
          onSubmit={handleSubmit}
          isPending={update.isPending}
          defaultValues={hausbankToForm(hausbank)}
          readonlyNr
        />
        <DialogFooter />
      </DialogContent>
    </Dialog>
  )
}

// ── Page ───────────────────────────────────────────────────────────────────────

export default function HausbankenstammPage() {
  const { data: hausbanken, isLoading } = useHausbanken()
  const createHausbank = useCreateHausbank()
  const deleteHausbank = useDeleteHausbank()
  const [showForm, setShowForm] = useState(false)
  const [editTarget, setEditTarget] = useState<Hausbank | null>(null)

  const handleCreate = async (data: FormData) => {
    try {
      await createHausbank.mutateAsync(formToPayload(data))
      toast.success('Hausbank angelegt.')
      setShowForm(false)
    } catch {
      toast.error('Fehler beim Anlegen der Hausbank.')
    }
  }

  const handleDelete = async (bankNr: string) => {
    try {
      await deleteHausbank.mutateAsync(bankNr)
      toast.success(`Hausbank ${bankNr} deaktiviert.`)
    } catch {
      toast.error('Fehler beim Deaktivieren der Hausbank.')
    }
  }

  return (
    <div className="p-6 space-y-4">
      <div className="flex items-start justify-between">
        <div>
          <h1 className="text-2xl font-semibold">Hausbankenstamm [BNKH]</h1>
          <p className="text-muted-foreground text-sm mt-1">
            Eigene Bankverbindungen des Mandanten. Basis für SEPA-Lastschriften und eRechnungen.
          </p>
        </div>
        <Button onClick={() => setShowForm(!showForm)} className="gap-2 shrink-0" aria-label="Neue Hausbank anlegen">
          <Plus className="h-4 w-4" />
          Neue Hausbank
        </Button>
      </div>

      {showForm && (
        <Card>
          <CardHeader><CardTitle className="text-base">Neue Hausbank anlegen</CardTitle></CardHeader>
          <CardContent>
            <HausbankForm onSubmit={handleCreate} isPending={createHausbank.isPending} />
          </CardContent>
        </Card>
      )}

      <Card>
        <CardHeader><CardTitle className="text-base">Hausbanken</CardTitle></CardHeader>
        <CardContent>
          {isLoading ? (
            <div className="space-y-2">{[1, 2, 3].map(i => <Skeleton key={i} className="h-8 w-full" />)}</div>
          ) : !hausbanken?.length ? (
            <p className="text-sm text-muted-foreground py-4 text-center">
              Keine Hausbanken vorhanden. Legen Sie die erste Bankverbindung an.
            </p>
          ) : (
            <Table>
              <TableHeader>
                <TableRow>
                  <TableHead>Bank-Nr</TableHead>
                  <TableHead>Bezeichnung</TableHead>
                  <TableHead>IBAN</TableHead>
                  <TableHead>BIC</TableHead>
                  <TableHead>Währung</TableHead>
                  <TableHead>Flags</TableHead>
                  <TableHead className="w-20" />
                </TableRow>
              </TableHeader>
              <TableBody>
                {hausbanken.map(b => (
                  <TableRow key={b.id}>
                    <TableCell className="font-mono text-sm">{b.bank_nr}</TableCell>
                    <TableCell>{b.bezeichnung}</TableCell>
                    <TableCell className="font-mono text-xs">{b.iban}</TableCell>
                    <TableCell className="font-mono text-xs">{b.bic ?? '—'}</TableCell>
                    <TableCell>{b.waehrung}</TableCell>
                    <TableCell>
                      <div className="flex gap-1 flex-wrap">
                        {b.standard && <Badge className="text-xs">Standard</Badge>}
                        {b.erechnung_aktiv && <Badge variant="secondary" className="text-xs">eRechnung</Badge>}
                        {b.sepa_glaeubiger_id && <Badge variant="outline" className="text-xs">SEPA</Badge>}
                      </div>
                    </TableCell>
                    <TableCell>
                      <div className="flex gap-1">
                        <Button
                          variant="ghost"
                          size="sm"
                          onClick={() => setEditTarget(b)}
                          aria-label={`Hausbank ${b.bank_nr} bearbeiten`}
                        >
                          <Pencil className="h-4 w-4" />
                        </Button>
                        <Button
                          variant="ghost"
                          size="sm"
                          onClick={() => handleDelete(b.bank_nr)}
                          disabled={deleteHausbank.isPending}
                          aria-label={`Hausbank ${b.bank_nr} deaktivieren`}
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
          hausbank={editTarget}
          open={!!editTarget}
          onClose={() => setEditTarget(null)}
        />
      )}
    </div>
  )
}
