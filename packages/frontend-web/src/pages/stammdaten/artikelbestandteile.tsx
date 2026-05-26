import { useState } from 'react'
import { useForm } from 'react-hook-form'
import { toast } from 'sonner'
import {
  useBestandteilDefs,
  useCreateBestandteilDef,
  useDeleteBestandteilDef,
} from '@/lib/api/artikelbestandteile'
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
  Table,
  TableBody,
  TableCell,
  TableHead,
  TableHeader,
  TableRow,
} from '@/components/ui/table'
import { Badge } from '@/components/ui/badge'
import { Skeleton } from '@/components/ui/skeleton'
import { Trash2, Plus } from 'lucide-react'

type FormData = {
  bestandteil_nr: string
  bezeichnung: string
  einheit: string
  grenzwert_min: string
  grenzwert_max: string
  nutzung: string
  typ_schad_naehr: string
  waage_qualitaet_nr: string
}

export default function ArtikelbestandteilePage() {
  const { data: bestandteile, isLoading, isError } = useBestandteilDefs()
  const createMutation = useCreateBestandteilDef()
  const deleteMutation = useDeleteBestandteilDef()
  const [deletingKey, setDeletingKey] = useState<string | null>(null)

  const { register, handleSubmit, reset, formState: { isSubmitting } } =
    useForm<FormData>({
      defaultValues: {
        bestandteil_nr: '',
        bezeichnung: '',
        einheit: '',
        grenzwert_min: '',
        grenzwert_max: '',
        nutzung: '',
        typ_schad_naehr: '',
        waage_qualitaet_nr: '',
      },
    })

  const onSubmit = async (data: FormData) => {
    try {
      await createMutation.mutateAsync({
        bestandteil_nr: data.bestandteil_nr,
        bezeichnung: data.bezeichnung,
        einheit: data.einheit || null,
        grenzwert_min: data.grenzwert_min ? parseFloat(data.grenzwert_min) : null,
        grenzwert_max: data.grenzwert_max ? parseFloat(data.grenzwert_max) : null,
        nutzung: data.nutzung || null,
        typ_schad_naehr: data.typ_schad_naehr || null,
        waage_qualitaet_nr: data.waage_qualitaet_nr || null,
      })
      toast.success(`Bestandteil ${data.bestandteil_nr} angelegt.`)
      reset()
    } catch {
      toast.error('Fehler beim Anlegen des Bestandteils.')
    }
  }

  const handleDelete = async (bestandteil_nr: string) => {
    if (deletingKey === bestandteil_nr) return
    setDeletingKey(bestandteil_nr)
    try {
      await deleteMutation.mutateAsync(bestandteil_nr)
      toast.success(`Bestandteil ${bestandteil_nr} deaktiviert.`)
    } catch {
      toast.error('Fehler beim Deaktivieren des Bestandteils.')
    } finally {
      setDeletingKey(null)
    }
  }

  return (
    <div className="p-6 space-y-4">
      <div>
        <h1 className="text-2xl font-semibold">Artikel-Bestandteile</h1>
        <p className="text-sm text-muted-foreground mt-1">
          Inhaltsstoffe und Bestandteil-Definitionen für Artikel verwalten
        </p>
      </div>

      <Card>
        <CardHeader>
          <CardTitle>Neuen Bestandteil anlegen</CardTitle>
        </CardHeader>
        <CardContent>
          <form onSubmit={handleSubmit(onSubmit)} noValidate className="grid grid-cols-1 gap-3 sm:grid-cols-4">
            <div>
              <Label htmlFor="ab_nr">Bestandteil-Nr. *</Label>
              <Input id="ab_nr" placeholder="z. B. FEUCHTE" {...register('bestandteil_nr', { required: true })} />
            </div>
            <div className="sm:col-span-2">
              <Label htmlFor="ab_bezeichnung">Bezeichnung *</Label>
              <Input id="ab_bezeichnung" placeholder="z. B. Feuchtegehalt" {...register('bezeichnung', { required: true })} />
            </div>
            <div>
              <Label htmlFor="ab_einheit">Einheit</Label>
              <Input id="ab_einheit" placeholder="z. B. %" {...register('einheit')} />
            </div>
            <div>
              <Label htmlFor="ab_min">Grenzwert Min</Label>
              <Input id="ab_min" type="number" step="0.01" {...register('grenzwert_min')} />
            </div>
            <div>
              <Label htmlFor="ab_max">Grenzwert Max</Label>
              <Input id="ab_max" type="number" step="0.01" {...register('grenzwert_max')} />
            </div>
            <div>
              <Label htmlFor="ab_nutzung">Nutzung</Label>
              <Input id="ab_nutzung" placeholder="z. B. Qualität" {...register('nutzung')} />
            </div>
            <div>
              <Label htmlFor="ab_typ">Typ (Schad/Nähr)</Label>
              <Input id="ab_typ" placeholder="S oder N" {...register('typ_schad_naehr')} />
            </div>
            <div>
              <Label htmlFor="ab_waage">Waage Qualitäts-Nr.</Label>
              <Input id="ab_waage" {...register('waage_qualitaet_nr')} />
            </div>
            <div className="sm:col-span-4 flex justify-end">
              <Button type="submit" disabled={isSubmitting} aria-label="Bestandteil anlegen">
                <Plus className="mr-1 h-4 w-4" aria-hidden="true" />
                Anlegen
              </Button>
            </div>
          </form>
        </CardContent>
      </Card>

      <Card>
        <CardHeader><CardTitle>Bestandteil-Definitionen</CardTitle></CardHeader>
        <CardContent>
          {isLoading && (
            <div className="space-y-2">{[0, 1, 2].map((i) => <Skeleton key={i} className="h-9 w-full" />)}</div>
          )}
          {isError && <p className="text-sm text-destructive">Fehler beim Laden der Bestandteile.</p>}
          {!isLoading && !isError && (!bestandteile || bestandteile.length === 0) && (
            <p className="text-sm text-muted-foreground">Keine Bestandteile vorhanden.</p>
          )}
          {bestandteile && bestandteile.length > 0 && (
            <Table>
              <TableHeader>
                <TableRow>
                  <TableHead>Bestandteil-Nr.</TableHead>
                  <TableHead>Bezeichnung</TableHead>
                  <TableHead>Einheit</TableHead>
                  <TableHead className="text-right">Min</TableHead>
                  <TableHead className="text-right">Max</TableHead>
                  <TableHead>Typ</TableHead>
                  <TableHead>Status</TableHead>
                  <TableHead aria-label="Aktionen" />
                </TableRow>
              </TableHeader>
              <TableBody>
                {bestandteile.map((b) => (
                  <TableRow key={b.id}>
                    <TableCell className="font-mono text-sm">{b.bestandteil_nr}</TableCell>
                    <TableCell>{b.bezeichnung}</TableCell>
                    <TableCell>{b.einheit ?? '—'}</TableCell>
                    <TableCell className="text-right font-mono text-sm">
                      {b.grenzwert_min != null ? Number(b.grenzwert_min).toFixed(2) : '—'}
                    </TableCell>
                    <TableCell className="text-right font-mono text-sm">
                      {b.grenzwert_max != null ? Number(b.grenzwert_max).toFixed(2) : '—'}
                    </TableCell>
                    <TableCell>{b.typ_schad_naehr ?? '—'}</TableCell>
                    <TableCell>
                      <Badge variant={b.aktiv ? 'default' : 'secondary'}>
                        {b.aktiv ? 'Aktiv' : 'Inaktiv'}
                      </Badge>
                    </TableCell>
                    <TableCell className="text-right">
                      <Button
                        variant="ghost"
                        size="icon"
                        disabled={deletingKey === b.bestandteil_nr || !b.aktiv}
                        onClick={() => handleDelete(b.bestandteil_nr)}
                        aria-label={`Bestandteil ${b.bestandteil_nr} deaktivieren`}
                      >
                        <Trash2 className="h-4 w-4" aria-hidden="true" />
                      </Button>
                    </TableCell>
                  </TableRow>
                ))}
              </TableBody>
            </Table>
          )}
        </CardContent>
      </Card>
    </div>
  )
}
