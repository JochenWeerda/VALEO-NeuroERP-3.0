import { useState } from 'react'
import { useForm } from 'react-hook-form'
import { toast } from 'sonner'
import {
  useMassebilanzen,
  useCreateMassebilanz,
  useMassebilanzBewegungen,
  useCreateBewegung,
  useFestschreibenMassebilanz,
  type Vorzeichen,
} from '@/lib/api/massebilanz'
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
import { Tabs, TabsContent, TabsList, TabsTrigger } from '@/components/ui/tabs'
import { Plus, Lock } from 'lucide-react'

// ── Bilanzen-Tab ─────────────────────────────────────────────────────────────

type BilanzFormData = {
  periode: string
  artikel_nr: string
  lager_nr: string
  anfangsbestand_kg: string
  bemerkung: string
}

function BilanzenTab() {
  const { data: bilanzen, isLoading, isError } = useMassebilanzen()
  const createMutation = useCreateMassebilanz()
  const festschreibenMutation = useFestschreibenMassebilanz()
  const [festschreibingKey, setFestschreibingKey] = useState<string | null>(null)

  const { register, handleSubmit, reset, formState: { isSubmitting } } =
    useForm<BilanzFormData>({
      defaultValues: { periode: '', artikel_nr: '', lager_nr: '', anfangsbestand_kg: '0', bemerkung: '' },
    })

  const onSubmit = async (data: BilanzFormData) => {
    try {
      await createMutation.mutateAsync({
        periode: data.periode,
        artikel_nr: data.artikel_nr || null,
        lager_nr: data.lager_nr || null,
        anfangsbestand_kg: parseFloat(data.anfangsbestand_kg) || 0,
        bemerkung: data.bemerkung || null,
      })
      toast.success(`Massebilanz ${data.periode} angelegt.`)
      reset()
    } catch {
      toast.error('Fehler beim Anlegen der Massebilanz.')
    }
  }

  const handleFestschreiben = async (id: string, periode: string) => {
    if (festschreibingKey === id) return
    setFestschreibingKey(id)
    try {
      await festschreibenMutation.mutateAsync(id)
      toast.success(`Massebilanz ${periode} festgeschrieben.`)
    } catch {
      toast.error('Fehler beim Festschreiben der Massebilanz.')
    } finally {
      setFestschreibingKey(null)
    }
  }

  return (
    <div className="space-y-4">
      <Card>
        <CardHeader>
          <CardTitle>Neue Massebilanz anlegen</CardTitle>
        </CardHeader>
        <CardContent>
          <form onSubmit={handleSubmit(onSubmit)} noValidate className="grid grid-cols-1 gap-3 sm:grid-cols-3">
            <div>
              <Label htmlFor="mb_periode">Periode *</Label>
              <Input
                id="mb_periode"
                placeholder="YYYY-MM z. B. 2026-05"
                {...register('periode', { required: true })}
              />
            </div>
            <div>
              <Label htmlFor="mb_artikel_nr">Artikel-Nr.</Label>
              <Input
                id="mb_artikel_nr"
                placeholder="z. B. WEIZEN"
                {...register('artikel_nr')}
              />
            </div>
            <div>
              <Label htmlFor="mb_lager_nr">Lager-Nr.</Label>
              <Input
                id="mb_lager_nr"
                placeholder="z. B. LAG-01"
                {...register('lager_nr')}
              />
            </div>
            <div>
              <Label htmlFor="mb_anfangsbestand">Anfangsbestand (kg)</Label>
              <Input
                id="mb_anfangsbestand"
                type="number"
                step="0.001"
                {...register('anfangsbestand_kg')}
              />
            </div>
            <div className="sm:col-span-2">
              <Label htmlFor="mb_bemerkung">Bemerkung</Label>
              <Input
                id="mb_bemerkung"
                placeholder="optional"
                {...register('bemerkung')}
              />
            </div>
            <div className="sm:col-span-3 flex justify-end">
              <Button type="submit" disabled={isSubmitting} aria-label="Massebilanz anlegen">
                <Plus className="mr-1 h-4 w-4" aria-hidden="true" />
                Anlegen
              </Button>
            </div>
          </form>
        </CardContent>
      </Card>

      <Card>
        <CardHeader><CardTitle>Massebilanzen</CardTitle></CardHeader>
        <CardContent>
          {isLoading && (
            <div className="space-y-2">{[0, 1, 2].map((i) => <Skeleton key={i} className="h-9 w-full" />)}</div>
          )}
          {isError && <p className="text-sm text-destructive">Fehler beim Laden der Massebilanzen.</p>}
          {!isLoading && !isError && (!bilanzen || bilanzen.length === 0) && (
            <p className="text-sm text-muted-foreground">Keine Massebilanzen vorhanden.</p>
          )}
          {bilanzen && bilanzen.length > 0 && (
            <Table>
              <TableHeader>
                <TableRow>
                  <TableHead>Periode</TableHead>
                  <TableHead>Artikel</TableHead>
                  <TableHead>Lager</TableHead>
                  <TableHead className="text-right">Anfang kg</TableHead>
                  <TableHead className="text-right">Zugänge kg</TableHead>
                  <TableHead className="text-right">Abgänge kg</TableHead>
                  <TableHead className="text-right">Endbestand kg</TableHead>
                  <TableHead>Status</TableHead>
                  <TableHead aria-label="Aktionen" />
                </TableRow>
              </TableHeader>
              <TableBody>
                {bilanzen.map((b) => (
                  <TableRow key={b.id}>
                    <TableCell className="font-mono text-sm">{b.periode}</TableCell>
                    <TableCell>{b.artikel_nr ?? '—'}</TableCell>
                    <TableCell>{b.lager_nr ?? '—'}</TableCell>
                    <TableCell className="text-right font-mono text-sm">{Number(b.anfangsbestand_kg).toFixed(3)}</TableCell>
                    <TableCell className="text-right font-mono text-sm">{Number(b.zugaenge_kg).toFixed(3)}</TableCell>
                    <TableCell className="text-right font-mono text-sm">{Number(b.abgaenge_kg).toFixed(3)}</TableCell>
                    <TableCell className="text-right font-mono text-sm">{Number(b.endbestand_kg).toFixed(3)}</TableCell>
                    <TableCell>
                      <Badge variant={b.status === 'festgeschrieben' ? 'secondary' : 'default'}>
                        {b.status === 'festgeschrieben' ? 'Festgeschrieben' : 'Offen'}
                      </Badge>
                    </TableCell>
                    <TableCell className="text-right">
                      <Button
                        variant="ghost"
                        size="icon"
                        disabled={festschreibingKey === b.id || b.status === 'festgeschrieben'}
                        onClick={() => handleFestschreiben(b.id, b.periode)}
                        aria-label={`Massebilanz ${b.periode} festschreiben`}
                      >
                        <Lock className="h-4 w-4" aria-hidden="true" />
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

// ── Bewegungen-Tab ────────────────────────────────────────────────────────────

type BewegungFormData = {
  buchungsdatum: string
  menge_kg: string
  vorzeichen: Vorzeichen
  beleg_nr: string
  beleg_typ: string
  kontrakt_nr: string
  lieferant_nr: string
}

function BewegungTab() {
  const { data: bilanzen } = useMassebilanzen()
  const [selectedBilanzId, setSelectedBilanzId] = useState('')

  const { data: bewegungen, isLoading, isError } = useMassebilanzBewegungen(selectedBilanzId)
  const createBewegungMutation = useCreateBewegung(selectedBilanzId)

  const { register, handleSubmit, reset, setValue, watch, formState: { isSubmitting } } =
    useForm<BewegungFormData>({
      defaultValues: {
        buchungsdatum: '',
        menge_kg: '',
        vorzeichen: '+',
        beleg_nr: '',
        beleg_typ: '',
        kontrakt_nr: '',
        lieferant_nr: '',
      },
    })

  const vorzeichenValue = watch('vorzeichen')

  const onSubmit = async (data: BewegungFormData) => {
    if (!selectedBilanzId) {
      toast.error('Bitte zuerst eine Massebilanz auswählen.')
      return
    }
    try {
      await createBewegungMutation.mutateAsync({
        buchungsdatum: data.buchungsdatum,
        menge_kg: parseFloat(data.menge_kg) || 0,
        vorzeichen: data.vorzeichen,
        beleg_nr: data.beleg_nr || null,
        beleg_typ: data.beleg_typ || null,
        kontrakt_nr: data.kontrakt_nr || null,
        lieferant_nr: data.lieferant_nr || null,
      })
      toast.success('Bewegung gebucht.')
      reset()
    } catch {
      toast.error('Fehler beim Buchen der Bewegung.')
    }
  }

  return (
    <div className="space-y-4">
      <Card>
        <CardHeader><CardTitle>Massebilanz auswählen</CardTitle></CardHeader>
        <CardContent>
          <div className="w-64">
            <Label htmlFor="bew_bilanz">Massebilanz</Label>
            <Select value={selectedBilanzId} onValueChange={setSelectedBilanzId}>
              <SelectTrigger id="bew_bilanz" aria-label="Massebilanz auswählen">
                <SelectValue placeholder="— auswählen —" />
              </SelectTrigger>
              <SelectContent>
                {(bilanzen ?? []).map((b) => (
                  <SelectItem key={b.id} value={b.id}>
                    {b.periode} {b.artikel_nr ? `· ${b.artikel_nr}` : ''} {b.lager_nr ? `· ${b.lager_nr}` : ''}
                  </SelectItem>
                ))}
              </SelectContent>
            </Select>
          </div>
        </CardContent>
      </Card>

      {selectedBilanzId && (
        <>
          <Card>
            <CardHeader><CardTitle>Bewegung buchen</CardTitle></CardHeader>
            <CardContent>
              <form onSubmit={handleSubmit(onSubmit)} noValidate className="grid grid-cols-1 gap-3 sm:grid-cols-3">
                <div>
                  <Label htmlFor="bew_datum">Buchungsdatum *</Label>
                  <Input id="bew_datum" type="date" {...register('buchungsdatum', { required: true })} />
                </div>
                <div>
                  <Label htmlFor="bew_menge">Menge (kg) *</Label>
                  <Input id="bew_menge" type="number" step="0.001" {...register('menge_kg', { required: true })} />
                </div>
                <div>
                  <Label htmlFor="bew_vorzeichen">Vorzeichen</Label>
                  <Select value={vorzeichenValue} onValueChange={(v) => setValue('vorzeichen', v as Vorzeichen)}>
                    <SelectTrigger id="bew_vorzeichen" aria-label="Vorzeichen">
                      <SelectValue />
                    </SelectTrigger>
                    <SelectContent>
                      <SelectItem value="+">+ Zugang</SelectItem>
                      <SelectItem value="-">- Abgang</SelectItem>
                    </SelectContent>
                  </Select>
                </div>
                <div>
                  <Label htmlFor="bew_beleg_nr">Beleg-Nr.</Label>
                  <Input id="bew_beleg_nr" {...register('beleg_nr')} />
                </div>
                <div>
                  <Label htmlFor="bew_beleg_typ">Beleg-Typ</Label>
                  <Input id="bew_beleg_typ" placeholder="z. B. Lieferschein" {...register('beleg_typ')} />
                </div>
                <div>
                  <Label htmlFor="bew_kontrakt_nr">Kontrakt-Nr.</Label>
                  <Input id="bew_kontrakt_nr" {...register('kontrakt_nr')} />
                </div>
                <div>
                  <Label htmlFor="bew_lieferant_nr">Lieferant-Nr.</Label>
                  <Input id="bew_lieferant_nr" {...register('lieferant_nr')} />
                </div>
                <div className="sm:col-span-3 flex justify-end">
                  <Button type="submit" disabled={isSubmitting} aria-label="Bewegung buchen">
                    <Plus className="mr-1 h-4 w-4" aria-hidden="true" />
                    Buchen
                  </Button>
                </div>
              </form>
            </CardContent>
          </Card>

          <Card>
            <CardHeader><CardTitle>Bewegungen</CardTitle></CardHeader>
            <CardContent>
              {isLoading && (
                <div className="space-y-2">{[0, 1, 2].map((i) => <Skeleton key={i} className="h-9 w-full" />)}</div>
              )}
              {isError && <p className="text-sm text-destructive">Fehler beim Laden der Bewegungen.</p>}
              {!isLoading && !isError && (!bewegungen || bewegungen.length === 0) && (
                <p className="text-sm text-muted-foreground">Keine Bewegungen vorhanden.</p>
              )}
              {bewegungen && bewegungen.length > 0 && (
                <Table>
                  <TableHeader>
                    <TableRow>
                      <TableHead>Datum</TableHead>
                      <TableHead>+/-</TableHead>
                      <TableHead className="text-right">Menge kg</TableHead>
                      <TableHead>Beleg-Nr.</TableHead>
                      <TableHead>Beleg-Typ</TableHead>
                      <TableHead>Kontrakt</TableHead>
                      <TableHead>Lieferant</TableHead>
                    </TableRow>
                  </TableHeader>
                  <TableBody>
                    {bewegungen.map((bew) => (
                      <TableRow key={bew.id} className={bew.storniert ? 'line-through opacity-50' : ''}>
                        <TableCell className="text-sm">{bew.buchungsdatum}</TableCell>
                        <TableCell>
                          <Badge variant={bew.vorzeichen === '+' ? 'default' : 'destructive'}>
                            {bew.vorzeichen}
                          </Badge>
                        </TableCell>
                        <TableCell className="text-right font-mono text-sm">{Number(bew.menge_kg).toFixed(3)}</TableCell>
                        <TableCell>{bew.beleg_nr ?? '—'}</TableCell>
                        <TableCell>{bew.beleg_typ ?? '—'}</TableCell>
                        <TableCell>{bew.kontrakt_nr ?? '—'}</TableCell>
                        <TableCell>{bew.lieferant_nr ?? '—'}</TableCell>
                      </TableRow>
                    ))}
                  </TableBody>
                </Table>
              )}
            </CardContent>
          </Card>
        </>
      )}
    </div>
  )
}

// ── Hauptseite ────────────────────────────────────────────────────────────────

export default function MassebilanzPage() {
  return (
    <div className="p-6 space-y-4">
      <div>
        <h1 className="text-2xl font-semibold">Massebilanz</h1>
        <p className="text-sm text-muted-foreground mt-1">
          Massenbilanzen nach Periode, Artikel und Lager verwalten
        </p>
      </div>

      <Tabs defaultValue="bilanzen">
        <TabsList>
          <TabsTrigger value="bilanzen">Massebilanzen</TabsTrigger>
          <TabsTrigger value="bewegungen">Bewegungen</TabsTrigger>
        </TabsList>
        <TabsContent value="bilanzen" className="mt-4">
          <BilanzenTab />
        </TabsContent>
        <TabsContent value="bewegungen" className="mt-4">
          <BewegungTab />
        </TabsContent>
      </Tabs>
    </div>
  )
}
