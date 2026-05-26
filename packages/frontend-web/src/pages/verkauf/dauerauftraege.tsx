import { useState } from 'react'
import { useForm, useFieldArray } from 'react-hook-form'
import { toast } from 'sonner'
import {
  useDauerauftraege,
  useCreateDauerauftrag,
  useDeleteDauerauftrag,
  useStartenDauerauftrag,
  type PeriodTyp,
} from '@/lib/api/dauerauftraege'
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
import { Trash2, Plus, Play } from 'lucide-react'

type PositionFormData = {
  pos_nr: string
  artikel_nr: string
  menge: string
  mengeneinheit: string
  preis_eur: string
}

type FormData = {
  kunden_nr: string
  bezeichnung: string
  da_anfang: string
  da_naechster: string
  da_ende: string
  perioden_typ: PeriodTyp
  perioden_wert: string
  positionen: PositionFormData[]
}

export default function DauerauftraegePage() {
  const { data: dauerauftraege, isLoading, isError } = useDauerauftraege()
  const createMutation = useCreateDauerauftrag()
  const deleteMutation = useDeleteDauerauftrag()
  const startenMutation = useStartenDauerauftrag()

  const [deletingKey, setDeletingKey] = useState<string | null>(null)
  const [startingKey, setStartingKey] = useState<string | null>(null)

  const { register, handleSubmit, reset, setValue, watch, control, formState: { isSubmitting } } =
    useForm<FormData>({
      defaultValues: {
        kunden_nr: '',
        bezeichnung: '',
        da_anfang: '',
        da_naechster: '',
        da_ende: '',
        perioden_typ: 'monatlich',
        perioden_wert: '1',
        positionen: [{ pos_nr: '1', artikel_nr: '', menge: '', mengeneinheit: '', preis_eur: '' }],
      },
    })

  const { fields, append, remove } = useFieldArray({ control, name: 'positionen' })
  const periodTypValue = watch('perioden_typ')

  const onSubmit = async (data: FormData) => {
    try {
      await createMutation.mutateAsync({
        kunden_nr: data.kunden_nr,
        bezeichnung: data.bezeichnung || null,
        da_anfang: data.da_anfang,
        da_naechster: data.da_naechster,
        da_ende: data.da_ende || null,
        perioden_typ: data.perioden_typ,
        perioden_wert: parseInt(data.perioden_wert, 10) || 1,
        positionen: data.positionen.map((p, i) => ({
          pos_nr: parseInt(p.pos_nr, 10) || i + 1,
          artikel_nr: p.artikel_nr,
          menge: parseFloat(p.menge) || 0,
          mengeneinheit: p.mengeneinheit || null,
          preis_eur: p.preis_eur ? parseFloat(p.preis_eur) : null,
        })),
      })
      toast.success('Dauerauftrag angelegt.')
      reset()
    } catch {
      toast.error('Fehler beim Anlegen des Dauerauftrags.')
    }
  }

  const handleDelete = async (da_nr: string) => {
    if (deletingKey === da_nr) return
    setDeletingKey(da_nr)
    try {
      await deleteMutation.mutateAsync(da_nr)
      toast.success(`Dauerauftrag ${da_nr} deaktiviert.`)
    } catch {
      toast.error('Fehler beim Deaktivieren des Dauerauftrags.')
    } finally {
      setDeletingKey(null)
    }
  }

  const handleStarten = async (da_nr: string) => {
    if (startingKey === da_nr) return
    setStartingKey(da_nr)
    try {
      const result = await startenMutation.mutateAsync(da_nr)
      toast.success(`Dauerauftrag ${da_nr} gestartet — Rechnung: ${result.rechnung_nr}`)
    } catch {
      toast.error('Fehler beim Starten des Dauerauftrags.')
    } finally {
      setStartingKey(null)
    }
  }

  return (
    <div className="p-6 space-y-4">
      <div>
        <h1 className="text-2xl font-semibold">Daueraufträge [DA]</h1>
        <p className="text-sm text-muted-foreground mt-1">
          Wiederkehrende Aufträge anlegen und verwalten
        </p>
      </div>

      <Card>
        <CardHeader>
          <CardTitle>Neuen Dauerauftrag anlegen</CardTitle>
        </CardHeader>
        <CardContent>
          <form onSubmit={handleSubmit(onSubmit)} noValidate className="space-y-4">
            <div className="grid grid-cols-1 gap-3 sm:grid-cols-3">
              <div>
                <Label htmlFor="da_kunden_nr">Kunden-Nr. *</Label>
                <Input
                  id="da_kunden_nr"
                  placeholder="z. B. KD-001"
                  {...register('kunden_nr', { required: true })}
                />
              </div>
              <div className="sm:col-span-2">
                <Label htmlFor="da_bezeichnung">Bezeichnung</Label>
                <Input
                  id="da_bezeichnung"
                  placeholder="z. B. Monatliche Lieferung Getreide"
                  {...register('bezeichnung')}
                />
              </div>
              <div>
                <Label htmlFor="da_anfang">Beginn *</Label>
                <Input
                  id="da_anfang"
                  type="date"
                  {...register('da_anfang', { required: true })}
                />
              </div>
              <div>
                <Label htmlFor="da_naechster">Nächster Lauf *</Label>
                <Input
                  id="da_naechster"
                  type="date"
                  {...register('da_naechster', { required: true })}
                />
              </div>
              <div>
                <Label htmlFor="da_ende">Ende (optional)</Label>
                <Input
                  id="da_ende"
                  type="date"
                  {...register('da_ende')}
                />
              </div>
              <div>
                <Label htmlFor="da_perioden_typ">Perioden-Typ</Label>
                <Select
                  value={periodTypValue}
                  onValueChange={(v) => setValue('perioden_typ', v as PeriodTyp)}
                >
                  <SelectTrigger id="da_perioden_typ" aria-label="Perioden-Typ">
                    <SelectValue />
                  </SelectTrigger>
                  <SelectContent>
                    <SelectItem value="monatlich">Monatlich</SelectItem>
                    <SelectItem value="woechentlich">Wöchentlich</SelectItem>
                    <SelectItem value="quartalsweise">Quartalsweise</SelectItem>
                    <SelectItem value="jaehrlich">Jährlich</SelectItem>
                  </SelectContent>
                </Select>
              </div>
              <div>
                <Label htmlFor="da_perioden_wert">Perioden-Wert</Label>
                <Input
                  id="da_perioden_wert"
                  type="number"
                  min="1"
                  {...register('perioden_wert')}
                />
              </div>
            </div>

            <div>
              <div className="flex items-center justify-between mb-2">
                <Label>Positionen *</Label>
                <Button
                  type="button"
                  variant="outline"
                  size="sm"
                  onClick={() =>
                    append({
                      pos_nr: String(fields.length + 1),
                      artikel_nr: '',
                      menge: '',
                      mengeneinheit: '',
                      preis_eur: '',
                    })
                  }
                >
                  <Plus className="mr-1 h-3 w-3" aria-hidden="true" />
                  Position
                </Button>
              </div>
              <div className="space-y-2">
                {fields.map((field, idx) => (
                  <div key={field.id} className="grid grid-cols-6 gap-2 items-end">
                    <div>
                      <Label className="text-xs text-muted-foreground">Pos.</Label>
                      <Input
                        type="number"
                        min="1"
                        placeholder="1"
                        {...register(`positionen.${idx}.pos_nr`)}
                      />
                    </div>
                    <div className="col-span-2">
                      <Label className="text-xs text-muted-foreground">Artikel-Nr. *</Label>
                      <Input
                        placeholder="z. B. ART-001"
                        {...register(`positionen.${idx}.artikel_nr`, { required: true })}
                      />
                    </div>
                    <div>
                      <Label className="text-xs text-muted-foreground">Menge *</Label>
                      <Input
                        type="number"
                        step="0.001"
                        placeholder="10"
                        {...register(`positionen.${idx}.menge`, { required: true })}
                      />
                    </div>
                    <div>
                      <Label className="text-xs text-muted-foreground">Einheit</Label>
                      <Input
                        placeholder="kg"
                        {...register(`positionen.${idx}.mengeneinheit`)}
                      />
                    </div>
                    <div className="flex gap-1">
                      <div className="flex-1">
                        <Label className="text-xs text-muted-foreground">Preis €</Label>
                        <Input
                          type="number"
                          step="0.01"
                          placeholder="0.00"
                          {...register(`positionen.${idx}.preis_eur`)}
                        />
                      </div>
                      {fields.length > 1 && (
                        <Button
                          type="button"
                          variant="ghost"
                          size="icon"
                          className="mt-auto"
                          onClick={() => remove(idx)}
                          aria-label={`Position ${idx + 1} entfernen`}
                        >
                          <Trash2 className="h-4 w-4" aria-hidden="true" />
                        </Button>
                      )}
                    </div>
                  </div>
                ))}
              </div>
            </div>

            <div className="flex justify-end">
              <Button type="submit" disabled={isSubmitting} aria-label="Dauerauftrag anlegen">
                <Plus className="mr-1 h-4 w-4" aria-hidden="true" />
                Anlegen
              </Button>
            </div>
          </form>
        </CardContent>
      </Card>

      <Card>
        <CardHeader>
          <CardTitle>Daueraufträge</CardTitle>
        </CardHeader>
        <CardContent>
          {isLoading && (
            <div className="space-y-2">
              {[0, 1, 2].map((i) => <Skeleton key={i} className="h-9 w-full" />)}
            </div>
          )}
          {isError && (
            <p className="text-sm text-destructive">Fehler beim Laden der Daueraufträge.</p>
          )}
          {!isLoading && !isError && (!dauerauftraege || dauerauftraege.length === 0) && (
            <p className="text-sm text-muted-foreground">Keine Daueraufträge vorhanden.</p>
          )}
          {dauerauftraege && dauerauftraege.length > 0 && (
            <Table>
              <TableHeader>
                <TableRow>
                  <TableHead>DA-Nr.</TableHead>
                  <TableHead>Kunden-Nr.</TableHead>
                  <TableHead>Bezeichnung</TableHead>
                  <TableHead>Nächster Lauf</TableHead>
                  <TableHead>Periode</TableHead>
                  <TableHead>Status</TableHead>
                  <TableHead aria-label="Aktionen" />
                </TableRow>
              </TableHeader>
              <TableBody>
                {dauerauftraege.map((da) => (
                  <TableRow key={da.id}>
                    <TableCell className="font-mono text-sm">{da.da_nr}</TableCell>
                    <TableCell>{da.kunden_nr}</TableCell>
                    <TableCell>{da.bezeichnung ?? '—'}</TableCell>
                    <TableCell className="text-sm">{da.da_naechster}</TableCell>
                    <TableCell className="text-sm">
                      {da.perioden_wert}× {da.perioden_typ}
                    </TableCell>
                    <TableCell>
                      <Badge variant={da.aktiv ? 'default' : 'secondary'}>
                        {da.aktiv ? 'Aktiv' : 'Inaktiv'}
                      </Badge>
                    </TableCell>
                    <TableCell className="text-right flex gap-1 justify-end">
                      <Button
                        variant="ghost"
                        size="icon"
                        disabled={startingKey === da.da_nr || !da.aktiv}
                        onClick={() => handleStarten(da.da_nr)}
                        aria-label={`Dauerauftrag ${da.da_nr} starten`}
                      >
                        <Play className="h-4 w-4" aria-hidden="true" />
                      </Button>
                      <Button
                        variant="ghost"
                        size="icon"
                        disabled={deletingKey === da.da_nr || !da.aktiv}
                        onClick={() => handleDelete(da.da_nr)}
                        aria-label={`Dauerauftrag ${da.da_nr} deaktivieren`}
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
