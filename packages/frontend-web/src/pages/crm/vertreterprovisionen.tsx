import { useState } from 'react'
import { useForm, useFieldArray } from 'react-hook-form'
import { toast } from 'sonner'
import {
  useProvisionsgruppen,
  useCreateProvisionsgruppe,
  useDeleteProvisionsgruppe,
  useProvisionsstaffeln,
  useCreateProvisionsstaffel,
  type Richtung,
  type Provisionstyp,
  type ProvisionsGruppe,
} from '@/lib/api/vertreterprovisionen'
import {
  Card,
  CardContent,
  CardHeader,
  CardTitle,
} from '@/components/ui/card'
import { Button } from '@/components/ui/button'
import { Input } from '@/components/ui/input'
import { Label } from '@/components/ui/label'
import {
  Select,
  SelectContent,
  SelectItem,
  SelectTrigger,
  SelectValue,
} from '@/components/ui/select'
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
import { Trash2, Plus, ChevronDown, ChevronUp } from 'lucide-react'

type GruppeFormData = {
  gruppe_nr: string
  bezeichnung: string
  richtung: Richtung
  provisionstyp: Provisionstyp
  provisionssatz: string
}

type StaffelZeileField = {
  zeile_nr: string
  ab_wert: string
  provisionssatz: string
}

type StaffelFormData = {
  gruppe_id: string
  vertreterklasse: string
  zeilen: StaffelZeileField[]
}

function ProvisionsGruppeBadge({ typ }: { typ: Provisionstyp }) {
  const label = {
    fix: 'Fixprovision',
    staffel_optpreis: 'Staffel (OPT-Preis)',
    staffel_preis_zuab: 'Staffel (Preis+ZuAb)',
  }[typ]
  return <Badge variant="outline">{label}</Badge>
}

function StaffelPanel({ gruppe }: { gruppe: ProvisionsGruppe }) {
  const [open, setOpen] = useState(false)
  const { data: staffeln, isLoading } = useProvisionsstaffeln(open ? gruppe.id : undefined)
  const createMutation = useCreateProvisionsstaffel()

  const { register, handleSubmit, control, reset, formState: { isSubmitting } } = useForm<StaffelFormData>({
    defaultValues: {
      gruppe_id: gruppe.id,
      vertreterklasse: '',
      zeilen: [{ zeile_nr: '1', ab_wert: '0', provisionssatz: '0' }],
    },
  })
  const { fields, append, remove } = useFieldArray({ control, name: 'zeilen' })

  const onSubmit = async (data: StaffelFormData) => {
    try {
      await createMutation.mutateAsync({
        gruppe_id: gruppe.id,
        vertreterklasse: data.vertreterklasse || null,
        zeilen: data.zeilen.map((z) => ({
          zeile_nr: parseInt(z.zeile_nr),
          ab_wert: parseFloat(z.ab_wert),
          provisionssatz: parseFloat(z.provisionssatz),
        })),
      })
      toast.success('Staffel angelegt.')
      reset({
        gruppe_id: gruppe.id,
        vertreterklasse: '',
        zeilen: [{ zeile_nr: '1', ab_wert: '0', provisionssatz: '0' }],
      })
    } catch {
      toast.error('Fehler beim Anlegen der Staffel.')
    }
  }

  return (
    <div className="border rounded-md">
      <button
        type="button"
        className="w-full flex items-center justify-between px-4 py-3 text-sm font-medium hover:bg-muted/50 transition-colors"
        onClick={() => setOpen((o) => !o)}
        aria-expanded={open}
        aria-label={`Staffeln für Gruppe ${gruppe.gruppe_nr} ein-/ausklappen`}
      >
        <span>Staffeln für {gruppe.gruppe_nr} — {gruppe.bezeichnung}</span>
        {open ? <ChevronUp className="h-4 w-4" /> : <ChevronDown className="h-4 w-4" />}
      </button>

      {open && (
        <div className="px-4 pb-4 space-y-4 border-t">
          {isLoading ? (
            <Skeleton className="h-24 w-full mt-4" />
          ) : !staffeln?.length ? (
            <p className="text-muted-foreground text-sm pt-4">Keine Staffeln vorhanden.</p>
          ) : (
            <div className="space-y-3 pt-4">
              {staffeln.map((s) => (
                <Card key={s.id}>
                  <CardHeader className="pb-2 pt-3">
                    <CardTitle className="text-sm">
                      Vertreterklasse: {s.vertreterklasse ?? '—'}
                    </CardTitle>
                  </CardHeader>
                  <CardContent>
                    <Table>
                      <TableHeader>
                        <TableRow>
                          <TableHead>Zeile</TableHead>
                          <TableHead>Ab Wert (€)</TableHead>
                          <TableHead>Provisionssatz (%)</TableHead>
                        </TableRow>
                      </TableHeader>
                      <TableBody>
                        {s.zeilen.map((z) => (
                          <TableRow key={z.id}>
                            <TableCell className="tabular-nums">{z.zeile_nr}</TableCell>
                            <TableCell className="tabular-nums">{Number(z.ab_wert).toFixed(2)}</TableCell>
                            <TableCell className="tabular-nums">{Number(z.provisionssatz).toFixed(4)} %</TableCell>
                          </TableRow>
                        ))}
                      </TableBody>
                    </Table>
                  </CardContent>
                </Card>
              ))}
            </div>
          )}

          <form onSubmit={handleSubmit(onSubmit)} className="space-y-3 pt-2 border-t">
            <p className="text-xs font-medium text-muted-foreground pt-2">Neue Staffel anlegen</p>
            <div className="space-y-1">
              <Label htmlFor={`vk_${gruppe.id}`}>Vertreterklasse (optional)</Label>
              <Input
                id={`vk_${gruppe.id}`}
                {...register('vertreterklasse')}
                placeholder="z.B. Innenverkauf"
              />
            </div>
            <div className="space-y-2">
              <p className="text-xs font-medium">Staffelzeilen</p>
              {fields.map((field, idx) => (
                <div key={field.id} className="grid grid-cols-3 gap-2 items-end">
                  <div className="space-y-1">
                    <Label htmlFor={`zeile_nr_${idx}`} className="text-xs">Zeile</Label>
                    <Input
                      id={`zeile_nr_${idx}`}
                      type="number"
                      min={1}
                      {...register(`zeilen.${idx}.zeile_nr`)}
                    />
                  </div>
                  <div className="space-y-1">
                    <Label htmlFor={`ab_wert_${idx}`} className="text-xs">Ab Wert (€)</Label>
                    <Input
                      id={`ab_wert_${idx}`}
                      type="number"
                      step="0.01"
                      {...register(`zeilen.${idx}.ab_wert`)}
                    />
                  </div>
                  <div className="flex gap-1 items-end">
                    <div className="flex-1 space-y-1">
                      <Label htmlFor={`ps_${idx}`} className="text-xs">Satz (%)</Label>
                      <Input
                        id={`ps_${idx}`}
                        type="number"
                        step="0.0001"
                        min={0}
                        max={100}
                        {...register(`zeilen.${idx}.provisionssatz`)}
                      />
                    </div>
                    {fields.length > 1 && (
                      <Button
                        type="button"
                        variant="ghost"
                        size="icon"
                        onClick={() => remove(idx)}
                        aria-label={`Staffelzeile ${idx + 1} entfernen`}
                      >
                        <Trash2 className="h-4 w-4 text-destructive" />
                      </Button>
                    )}
                  </div>
                </div>
              ))}
              <Button
                type="button"
                variant="outline"
                size="sm"
                onClick={() =>
                  append({
                    zeile_nr: String(fields.length + 1),
                    ab_wert: '0',
                    provisionssatz: '0',
                  })
                }
              >
                <Plus className="mr-1 h-3 w-3" />
                Zeile
              </Button>
            </div>
            <Button type="submit" disabled={isSubmitting} size="sm" aria-label="Staffel speichern">
              Staffel anlegen
            </Button>
          </form>
        </div>
      )}
    </div>
  )
}

export default function VertreterprovisionsPage() {
  const [filterRichtung, setFilterRichtung] = useState<Richtung | undefined>()
  const [deletingKey, setDeletingKey] = useState<string | null>(null)
  const { data: gruppen, isLoading } = useProvisionsgruppen(filterRichtung)
  const createMutation = useCreateProvisionsgruppe()
  const deleteMutation = useDeleteProvisionsgruppe()

  const {
    register,
    handleSubmit,
    reset,
    setValue,
    watch,
    formState: { errors, isSubmitting },
  } = useForm<GruppeFormData>({
    defaultValues: { richtung: 'vk', provisionstyp: 'fix' },
  })
  const richtungValue = watch('richtung')
  const provisionstyp = watch('provisionstyp')

  const onSubmit = async (data: GruppeFormData) => {
    try {
      await createMutation.mutateAsync({
        gruppe_nr: data.gruppe_nr,
        bezeichnung: data.bezeichnung,
        richtung: data.richtung,
        provisionstyp: data.provisionstyp,
        provisionssatz:
          data.provisionstyp === 'fix' && data.provisionssatz
            ? parseFloat(data.provisionssatz)
            : null,
      })
      toast.success(`Provisionsgruppe "${data.gruppe_nr}" angelegt.`)
      reset({ richtung: 'vk', provisionstyp: 'fix' })
    } catch {
      toast.error('Fehler beim Anlegen. Prüfen Sie auf Duplikate.')
    }
  }

  const handleDelete = async (gruppe_nr: string) => {
    if (deletingKey === gruppe_nr) return
    setDeletingKey(gruppe_nr)
    try {
      await deleteMutation.mutateAsync(gruppe_nr)
      toast.success(`Provisionsgruppe "${gruppe_nr}" deaktiviert.`)
    } catch {
      toast.error('Fehler beim Deaktivieren.')
    } finally {
      setDeletingKey(null)
    }
  }

  return (
    <div className="p-6 space-y-4">
      <div>
        <h1 className="text-2xl font-semibold">Vertreterprovisionsgruppen & -staffeln</h1>
        <p className="text-muted-foreground text-sm mt-1">
          Außendienst-Provisionsabrechnung: Gruppen definieren Provisionstyp, Staffeln die Staffelzeilen.
        </p>
      </div>

      <Card>
        <CardHeader>
          <CardTitle>Neue Provisionsgruppe</CardTitle>
        </CardHeader>
        <CardContent>
          <form onSubmit={handleSubmit(onSubmit)} className="grid grid-cols-1 gap-4 sm:grid-cols-3">
            <div className="space-y-1">
              <Label htmlFor="pg_nr">Gruppen-Nr.</Label>
              <Input
                id="pg_nr"
                {...register('gruppe_nr', { required: 'Pflichtfeld' })}
                placeholder="z.B. PVG-001"
                aria-invalid={!!errors.gruppe_nr}
              />
              {errors.gruppe_nr && (
                <p className="text-destructive text-xs">{errors.gruppe_nr.message}</p>
              )}
            </div>
            <div className="space-y-1">
              <Label htmlFor="pg_bez">Bezeichnung</Label>
              <Input
                id="pg_bez"
                {...register('bezeichnung', { required: 'Pflichtfeld' })}
                placeholder="z.B. Außendienst Nord"
                aria-invalid={!!errors.bezeichnung}
              />
              {errors.bezeichnung && (
                <p className="text-destructive text-xs">{errors.bezeichnung.message}</p>
              )}
            </div>
            <div className="space-y-1">
              <Label htmlFor="pg_richtung">Richtung</Label>
              <Select
                value={richtungValue}
                onValueChange={(v) => setValue('richtung', v as Richtung)}
              >
                <SelectTrigger id="pg_richtung" aria-label="Richtung Provisionsgruppe">
                  <SelectValue />
                </SelectTrigger>
                <SelectContent>
                  <SelectItem value="vk">Verkauf (VK)</SelectItem>
                  <SelectItem value="ek">Einkauf (EK)</SelectItem>
                </SelectContent>
              </Select>
            </div>
            <div className="space-y-1">
              <Label htmlFor="pg_typ">Provisionstyp</Label>
              <Select
                value={provisionstyp}
                onValueChange={(v) => setValue('provisionstyp', v as Provisionstyp)}
              >
                <SelectTrigger id="pg_typ" aria-label="Provisionstyp">
                  <SelectValue />
                </SelectTrigger>
                <SelectContent>
                  <SelectItem value="fix">Fixprovision</SelectItem>
                  <SelectItem value="staffel_optpreis">Staffel (OPT-Preis)</SelectItem>
                  <SelectItem value="staffel_preis_zuab">Staffel (Preis + ZuAb)</SelectItem>
                </SelectContent>
              </Select>
            </div>
            {provisionstyp === 'fix' && (
              <div className="space-y-1">
                <Label htmlFor="pg_satz">Provisionssatz (%)</Label>
                <Input
                  id="pg_satz"
                  type="number"
                  step="0.0001"
                  min={0}
                  max={100}
                  {...register('provisionssatz')}
                  placeholder="z.B. 2.5"
                />
              </div>
            )}
            <div className="sm:col-span-3 flex justify-end">
              <Button type="submit" disabled={isSubmitting} aria-label="Provisionsgruppe anlegen">
                <Plus className="mr-2 h-4 w-4" />
                Anlegen
              </Button>
            </div>
          </form>
        </CardContent>
      </Card>

      <Card>
        <CardHeader className="flex flex-row items-center justify-between">
          <CardTitle>Provisionsgruppen</CardTitle>
          <Select
            value={filterRichtung ?? 'all'}
            onValueChange={(v) => setFilterRichtung(v === 'all' ? undefined : (v as Richtung))}
          >
            <SelectTrigger className="w-36" aria-label="Richtung filtern">
              <SelectValue />
            </SelectTrigger>
            <SelectContent>
              <SelectItem value="all">Alle</SelectItem>
              <SelectItem value="vk">Verkauf (VK)</SelectItem>
              <SelectItem value="ek">Einkauf (EK)</SelectItem>
            </SelectContent>
          </Select>
        </CardHeader>
        <CardContent>
          {isLoading ? (
            <div className="space-y-2">
              {[...Array(3)].map((_, i) => <Skeleton key={i} className="h-10 w-full" />)}
            </div>
          ) : !gruppen?.length ? (
            <p className="text-muted-foreground text-sm py-4 text-center">
              Keine Provisionsgruppen vorhanden.
            </p>
          ) : (
            <div className="space-y-2">
              <Table>
                <TableHeader>
                  <TableRow>
                    <TableHead>Gruppen-Nr.</TableHead>
                    <TableHead>Bezeichnung</TableHead>
                    <TableHead>Typ</TableHead>
                    <TableHead>Satz (%)</TableHead>
                    <TableHead className="w-16" />
                  </TableRow>
                </TableHeader>
                <TableBody>
                  {gruppen.map((g) => (
                    <TableRow key={g.id}>
                      <TableCell className="font-mono">{g.gruppe_nr}</TableCell>
                      <TableCell>{g.bezeichnung}</TableCell>
                      <TableCell><ProvisionsGruppeBadge typ={g.provisionstyp} /></TableCell>
                      <TableCell className="tabular-nums">
                        {g.provisionssatz !== null ? `${Number(g.provisionssatz).toFixed(4)} %` : '—'}
                      </TableCell>
                      <TableCell>
                        <Button
                          variant="ghost"
                          size="icon"
                          aria-label={`Provisionsgruppe ${g.gruppe_nr} löschen`}
                          disabled={deletingKey === g.gruppe_nr}
                          onClick={() => handleDelete(g.gruppe_nr)}
                        >
                          <Trash2 className="h-4 w-4 text-destructive" />
                        </Button>
                      </TableCell>
                    </TableRow>
                  ))}
                </TableBody>
              </Table>

              <div className="space-y-2 pt-2">
                <p className="text-xs font-medium text-muted-foreground">
                  Staffeln (Klick zum Ausklappen)
                </p>
                {gruppen
                  .filter((g) => g.provisionstyp !== 'fix')
                  .map((g) => (
                    <StaffelPanel key={g.id} gruppe={g} />
                  ))}
                {gruppen.every((g) => g.provisionstyp === 'fix') && (
                  <p className="text-muted-foreground text-xs py-2">
                    Staffeln nur bei Staffel-Provisionstypen verfügbar.
                  </p>
                )}
              </div>
            </div>
          )}
        </CardContent>
      </Card>
    </div>
  )
}
