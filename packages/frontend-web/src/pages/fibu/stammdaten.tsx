import { useState } from 'react'
import { useForm } from 'react-hook-form'
import { toast } from 'sonner'
import {
  useZahlungsformulare,
  useCreateZahlungsformular,
  useDeleteZahlungsformular,
  useZinsgruppen,
  useCreateZinsgruppe,
  useDeleteZinsgruppe,
  useLeergutarten,
  useCreateLeergutart,
  useDeleteLeergutart,
  type Formularklasse,
  type Zinsmethode,
  type LeergutTyp,
} from '@/lib/api/fibu-stammdaten'
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
import { Trash2, Plus } from 'lucide-react'

// ── Zahlungsformulare ──────────────────────────────────────────────────────────

type ZahlungsformularFormData = {
  formular_nr: string
  bezeichnung: string
  formularklasse: Formularklasse
  bank_blz: string
  bank_iban: string
  formulareinrichtung: string
}

function ZahlungsformulareTab() {
  const [filterKlasse, setFilterKlasse] = useState<Formularklasse | undefined>()
  const [deletingKey, setDeletingKey] = useState<string | null>(null)
  const { data: formulare, isLoading } = useZahlungsformulare(filterKlasse)
  const createMutation = useCreateZahlungsformular()
  const deleteMutation = useDeleteZahlungsformular()

  const {
    register,
    handleSubmit,
    reset,
    setValue,
    watch,
    formState: { errors, isSubmitting },
  } = useForm<ZahlungsformularFormData>({
    defaultValues: { formularklasse: 'ausgang' },
  })
  const klasseValue = watch('formularklasse')

  const onSubmit = async (data: ZahlungsformularFormData) => {
    try {
      await createMutation.mutateAsync({
        formular_nr: data.formular_nr,
        bezeichnung: data.bezeichnung,
        formularklasse: data.formularklasse,
        bank_blz: data.bank_blz || null,
        bank_iban: data.bank_iban || null,
        formulareinrichtung: data.formulareinrichtung || null,
      })
      toast.success(`Zahlungsformular "${data.formular_nr}" angelegt.`)
      reset({ formularklasse: 'ausgang' })
    } catch {
      toast.error('Fehler beim Anlegen. Prüfen Sie auf Duplikate.')
    }
  }

  const handleDelete = async (formular_nr: string) => {
    if (deletingKey === formular_nr) return
    setDeletingKey(formular_nr)
    try {
      await deleteMutation.mutateAsync(formular_nr)
      toast.success(`Zahlungsformular "${formular_nr}" deaktiviert.`)
    } catch {
      toast.error('Fehler beim Deaktivieren.')
    } finally {
      setDeletingKey(null)
    }
  }

  return (
    <div className="space-y-6">
      <Card>
        <CardHeader>
          <CardTitle>Neues Zahlungsformular [FIZAF]</CardTitle>
        </CardHeader>
        <CardContent>
          <form
            onSubmit={handleSubmit(onSubmit)}
            className="grid grid-cols-1 gap-4 sm:grid-cols-3"
          >
            <div className="space-y-1">
              <Label htmlFor="zf_nr">Formular-Nr.</Label>
              <Input
                id="zf_nr"
                {...register('formular_nr', { required: 'Pflichtfeld' })}
                placeholder="z.B. FIZAF-001"
                aria-invalid={!!errors.formular_nr}
              />
              {errors.formular_nr && (
                <p className="text-destructive text-xs">{errors.formular_nr.message}</p>
              )}
            </div>
            <div className="space-y-1">
              <Label htmlFor="zf_bez">Bezeichnung</Label>
              <Input
                id="zf_bez"
                {...register('bezeichnung', { required: 'Pflichtfeld' })}
                placeholder="z.B. SEPA-Überweisung Inland"
                aria-invalid={!!errors.bezeichnung}
              />
              {errors.bezeichnung && (
                <p className="text-destructive text-xs">{errors.bezeichnung.message}</p>
              )}
            </div>
            <div className="space-y-1">
              <Label htmlFor="zf_klasse">Formularklasse</Label>
              <Select
                value={klasseValue}
                onValueChange={(v) => setValue('formularklasse', v as Formularklasse)}
              >
                <SelectTrigger id="zf_klasse" aria-label="Formularklasse">
                  <SelectValue />
                </SelectTrigger>
                <SelectContent>
                  <SelectItem value="ausgang">Ausgang</SelectItem>
                  <SelectItem value="eingang">Eingang</SelectItem>
                </SelectContent>
              </Select>
            </div>
            <div className="space-y-1">
              <Label htmlFor="zf_blz">BLZ (optional)</Label>
              <Input id="zf_blz" {...register('bank_blz')} placeholder="z.B. 37040044" />
            </div>
            <div className="space-y-1">
              <Label htmlFor="zf_iban">IBAN (optional)</Label>
              <Input id="zf_iban" {...register('bank_iban')} placeholder="DE89..." />
            </div>
            <div className="space-y-1">
              <Label htmlFor="zf_einr">Formulareinrichtung (optional)</Label>
              <Input
                id="zf_einr"
                {...register('formulareinrichtung')}
                placeholder="z.B. MT940"
              />
            </div>
            <div className="sm:col-span-3 flex justify-end">
              <Button type="submit" disabled={isSubmitting} aria-label="Zahlungsformular anlegen">
                <Plus className="mr-2 h-4 w-4" />
                Anlegen
              </Button>
            </div>
          </form>
        </CardContent>
      </Card>

      <Card>
        <CardHeader className="flex flex-row items-center justify-between">
          <CardTitle>Zahlungsformulare</CardTitle>
          <Select
            value={filterKlasse ?? 'all'}
            onValueChange={(v) =>
              setFilterKlasse(v === 'all' ? undefined : (v as Formularklasse))
            }
          >
            <SelectTrigger className="w-36" aria-label="Formularklasse filtern">
              <SelectValue />
            </SelectTrigger>
            <SelectContent>
              <SelectItem value="all">Alle</SelectItem>
              <SelectItem value="ausgang">Ausgang</SelectItem>
              <SelectItem value="eingang">Eingang</SelectItem>
            </SelectContent>
          </Select>
        </CardHeader>
        <CardContent>
          {isLoading ? (
            <div className="space-y-2">
              {[...Array(3)].map((_, i) => (
                <Skeleton key={i} className="h-10 w-full" />
              ))}
            </div>
          ) : !formulare?.length ? (
            <p className="text-muted-foreground text-sm py-4 text-center">
              Keine Zahlungsformulare vorhanden.
            </p>
          ) : (
            <Table>
              <TableHeader>
                <TableRow>
                  <TableHead>Formular-Nr.</TableHead>
                  <TableHead>Bezeichnung</TableHead>
                  <TableHead>Klasse</TableHead>
                  <TableHead>IBAN</TableHead>
                  <TableHead className="w-16" />
                </TableRow>
              </TableHeader>
              <TableBody>
                {formulare.map((f) => (
                  <TableRow key={f.id}>
                    <TableCell className="font-mono">{f.formular_nr}</TableCell>
                    <TableCell>{f.bezeichnung}</TableCell>
                    <TableCell>
                      <Badge variant={f.formularklasse === 'ausgang' ? 'default' : 'secondary'}>
                        {f.formularklasse === 'ausgang' ? 'Ausgang' : 'Eingang'}
                      </Badge>
                    </TableCell>
                    <TableCell className="font-mono text-xs">
                      {f.bank_iban ?? '—'}
                    </TableCell>
                    <TableCell>
                      <Button
                        variant="ghost"
                        size="icon"
                        aria-label={`Zahlungsformular ${f.formular_nr} löschen`}
                        disabled={deletingKey === f.formular_nr}
                        onClick={() => handleDelete(f.formular_nr)}
                      >
                        <Trash2 className="h-4 w-4 text-destructive" />
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

// ── Zinsgruppen ────────────────────────────────────────────────────────────────

type ZinsgruppeFormData = {
  gruppe_nr: string
  bezeichnung: string
  zinssatz: string
  zinsmethode: Zinsmethode
  schwellwert_tage: string
  konto_zinsen: string
  konto_zinsabschlagsteuer: string
}

const ZINSMETHODE_LABELS: Record<Zinsmethode, string> = {
  act_act: 'Act/Act',
  act_360: 'Act/360',
  act_365: 'Act/365',
  '30_360': '30/360',
}

function ZinsgruppenTab() {
  const [deletingKey, setDeletingKey] = useState<string | null>(null)
  const { data: gruppen, isLoading } = useZinsgruppen()
  const createMutation = useCreateZinsgruppe()
  const deleteMutation = useDeleteZinsgruppe()

  const {
    register,
    handleSubmit,
    reset,
    setValue,
    watch,
    formState: { errors, isSubmitting },
  } = useForm<ZinsgruppeFormData>({
    defaultValues: { zinsmethode: 'act_360', schwellwert_tage: '0' },
  })
  const zinsmethodeValue = watch('zinsmethode')

  const onSubmit = async (data: ZinsgruppeFormData) => {
    try {
      await createMutation.mutateAsync({
        gruppe_nr: data.gruppe_nr,
        bezeichnung: data.bezeichnung,
        zinssatz: parseFloat(data.zinssatz),
        zinsmethode: data.zinsmethode,
        schwellwert_tage: parseInt(data.schwellwert_tage) || 0,
        konto_zinsen: data.konto_zinsen || null,
        konto_zinsabschlagsteuer: data.konto_zinsabschlagsteuer || null,
      })
      toast.success(`Zinsgruppe "${data.gruppe_nr}" angelegt.`)
      reset({ zinsmethode: 'act_360', schwellwert_tage: '0' })
    } catch {
      toast.error('Fehler beim Anlegen. Prüfen Sie auf Duplikate.')
    }
  }

  const handleDelete = async (gruppe_nr: string) => {
    if (deletingKey === gruppe_nr) return
    setDeletingKey(gruppe_nr)
    try {
      await deleteMutation.mutateAsync(gruppe_nr)
      toast.success(`Zinsgruppe "${gruppe_nr}" deaktiviert.`)
    } catch {
      toast.error('Fehler beim Deaktivieren.')
    } finally {
      setDeletingKey(null)
    }
  }

  return (
    <div className="space-y-6">
      <Card>
        <CardHeader>
          <CardTitle>Neue Zinsgruppe</CardTitle>
        </CardHeader>
        <CardContent>
          <form
            onSubmit={handleSubmit(onSubmit)}
            className="grid grid-cols-1 gap-4 sm:grid-cols-3"
          >
            <div className="space-y-1">
              <Label htmlFor="zg_nr">Gruppen-Nr.</Label>
              <Input
                id="zg_nr"
                {...register('gruppe_nr', { required: 'Pflichtfeld' })}
                placeholder="z.B. ZINS-STD"
                aria-invalid={!!errors.gruppe_nr}
              />
              {errors.gruppe_nr && (
                <p className="text-destructive text-xs">{errors.gruppe_nr.message}</p>
              )}
            </div>
            <div className="space-y-1">
              <Label htmlFor="zg_bez">Bezeichnung</Label>
              <Input
                id="zg_bez"
                {...register('bezeichnung', { required: 'Pflichtfeld' })}
                placeholder="z.B. Standard-Zinssatz"
                aria-invalid={!!errors.bezeichnung}
              />
              {errors.bezeichnung && (
                <p className="text-destructive text-xs">{errors.bezeichnung.message}</p>
              )}
            </div>
            <div className="space-y-1">
              <Label htmlFor="zg_satz">Zinssatz (%)</Label>
              <Input
                id="zg_satz"
                type="number"
                step="0.0001"
                min={0}
                max={100}
                {...register('zinssatz', { required: 'Pflichtfeld' })}
                placeholder="z.B. 8.5"
                aria-invalid={!!errors.zinssatz}
              />
              {errors.zinssatz && (
                <p className="text-destructive text-xs">{errors.zinssatz.message}</p>
              )}
            </div>
            <div className="space-y-1">
              <Label htmlFor="zg_methode">Zinsmethode</Label>
              <Select
                value={zinsmethodeValue}
                onValueChange={(v) => setValue('zinsmethode', v as Zinsmethode)}
              >
                <SelectTrigger id="zg_methode" aria-label="Zinsmethode">
                  <SelectValue />
                </SelectTrigger>
                <SelectContent>
                  {(Object.entries(ZINSMETHODE_LABELS) as [Zinsmethode, string][]).map(
                    ([val, label]) => (
                      <SelectItem key={val} value={val}>{label}</SelectItem>
                    )
                  )}
                </SelectContent>
              </Select>
            </div>
            <div className="space-y-1">
              <Label htmlFor="zg_schwellwert">Schwellwert (Tage)</Label>
              <Input
                id="zg_schwellwert"
                type="number"
                min={0}
                {...register('schwellwert_tage')}
                placeholder="0"
              />
            </div>
            <div className="space-y-1">
              <Label htmlFor="zg_konto_z">Konto Zinsen (optional)</Label>
              <Input
                id="zg_konto_z"
                {...register('konto_zinsen')}
                placeholder="z.B. 7665"
              />
            </div>
            <div className="space-y-1 sm:col-span-2">
              <Label htmlFor="zg_konto_zast">Konto Zinsabschlagsteuer (optional)</Label>
              <Input
                id="zg_konto_zast"
                {...register('konto_zinsabschlagsteuer')}
                placeholder="z.B. 7666"
              />
            </div>
            <div className="sm:col-span-3 flex justify-end">
              <Button type="submit" disabled={isSubmitting} aria-label="Zinsgruppe anlegen">
                <Plus className="mr-2 h-4 w-4" />
                Anlegen
              </Button>
            </div>
          </form>
        </CardContent>
      </Card>

      <Card>
        <CardHeader>
          <CardTitle>Zinsgruppen</CardTitle>
        </CardHeader>
        <CardContent>
          {isLoading ? (
            <div className="space-y-2">
              {[...Array(3)].map((_, i) => (
                <Skeleton key={i} className="h-10 w-full" />
              ))}
            </div>
          ) : !gruppen?.length ? (
            <p className="text-muted-foreground text-sm py-4 text-center">
              Keine Zinsgruppen vorhanden.
            </p>
          ) : (
            <Table>
              <TableHeader>
                <TableRow>
                  <TableHead>Gruppen-Nr.</TableHead>
                  <TableHead>Bezeichnung</TableHead>
                  <TableHead>Zinssatz (%)</TableHead>
                  <TableHead>Methode</TableHead>
                  <TableHead>Schwellwert</TableHead>
                  <TableHead className="w-16" />
                </TableRow>
              </TableHeader>
              <TableBody>
                {gruppen.map((g) => (
                  <TableRow key={g.id}>
                    <TableCell className="font-mono">{g.gruppe_nr}</TableCell>
                    <TableCell>{g.bezeichnung}</TableCell>
                    <TableCell className="tabular-nums">
                      {Number(g.zinssatz).toFixed(4)} %
                    </TableCell>
                    <TableCell>
                      <Badge variant="outline">
                        {ZINSMETHODE_LABELS[g.zinsmethode] ?? g.zinsmethode}
                      </Badge>
                    </TableCell>
                    <TableCell className="tabular-nums">
                      {g.schwellwert_tage} Tage
                    </TableCell>
                    <TableCell>
                      <Button
                        variant="ghost"
                        size="icon"
                        aria-label={`Zinsgruppe ${g.gruppe_nr} löschen`}
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
          )}
        </CardContent>
      </Card>
    </div>
  )
}

// ── Leergutarten ───────────────────────────────────────────────────────────────

type LeergutArtFormData = {
  art_nr: string
  bezeichnung: string
  leergut_typ: LeergutTyp
  pfandwert: string
  konto_leergut: string
}

const LEERGUT_TYP_LABELS: Record<LeergutTyp, string> = {
  palette: 'Palette',
  bigbag: 'Big-Bag',
  fass: 'Fass',
  flasche: 'Flasche',
  behaelter: 'Behälter',
  sonstige: 'Sonstige',
}

function LeergutartenTab() {
  const [deletingKey, setDeletingKey] = useState<string | null>(null)
  const { data: arten, isLoading } = useLeergutarten()
  const createMutation = useCreateLeergutart()
  const deleteMutation = useDeleteLeergutart()

  const {
    register,
    handleSubmit,
    reset,
    setValue,
    watch,
    formState: { errors, isSubmitting },
  } = useForm<LeergutArtFormData>({
    defaultValues: { leergut_typ: 'palette' },
  })
  const typValue = watch('leergut_typ')

  const onSubmit = async (data: LeergutArtFormData) => {
    try {
      await createMutation.mutateAsync({
        art_nr: data.art_nr,
        bezeichnung: data.bezeichnung,
        leergut_typ: data.leergut_typ,
        pfandwert: data.pfandwert ? parseFloat(data.pfandwert) : null,
        konto_leergut: data.konto_leergut || null,
      })
      toast.success(`Leergutart "${data.art_nr}" angelegt.`)
      reset({ leergut_typ: 'palette' })
    } catch {
      toast.error('Fehler beim Anlegen. Prüfen Sie auf Duplikate.')
    }
  }

  const handleDelete = async (art_nr: string) => {
    if (deletingKey === art_nr) return
    setDeletingKey(art_nr)
    try {
      await deleteMutation.mutateAsync(art_nr)
      toast.success(`Leergutart "${art_nr}" deaktiviert.`)
    } catch {
      toast.error('Fehler beim Deaktivieren.')
    } finally {
      setDeletingKey(null)
    }
  }

  return (
    <div className="space-y-6">
      <Card>
        <CardHeader>
          <CardTitle>Neue Leergutart</CardTitle>
        </CardHeader>
        <CardContent>
          <form
            onSubmit={handleSubmit(onSubmit)}
            className="grid grid-cols-1 gap-4 sm:grid-cols-3"
          >
            <div className="space-y-1">
              <Label htmlFor="lg_nr">Art-Nr.</Label>
              <Input
                id="lg_nr"
                {...register('art_nr', { required: 'Pflichtfeld' })}
                placeholder="z.B. PAL-EUR"
                aria-invalid={!!errors.art_nr}
              />
              {errors.art_nr && (
                <p className="text-destructive text-xs">{errors.art_nr.message}</p>
              )}
            </div>
            <div className="space-y-1">
              <Label htmlFor="lg_bez">Bezeichnung</Label>
              <Input
                id="lg_bez"
                {...register('bezeichnung', { required: 'Pflichtfeld' })}
                placeholder="z.B. Euro-Palette"
                aria-invalid={!!errors.bezeichnung}
              />
              {errors.bezeichnung && (
                <p className="text-destructive text-xs">{errors.bezeichnung.message}</p>
              )}
            </div>
            <div className="space-y-1">
              <Label htmlFor="lg_typ">Leergut-Typ</Label>
              <Select
                value={typValue}
                onValueChange={(v) => setValue('leergut_typ', v as LeergutTyp)}
              >
                <SelectTrigger id="lg_typ" aria-label="Leergut-Typ">
                  <SelectValue />
                </SelectTrigger>
                <SelectContent>
                  {(Object.entries(LEERGUT_TYP_LABELS) as [LeergutTyp, string][]).map(
                    ([val, label]) => (
                      <SelectItem key={val} value={val}>{label}</SelectItem>
                    )
                  )}
                </SelectContent>
              </Select>
            </div>
            <div className="space-y-1">
              <Label htmlFor="lg_pfand">Pfandwert (€, optional)</Label>
              <Input
                id="lg_pfand"
                type="number"
                step="0.01"
                min={0}
                {...register('pfandwert')}
                placeholder="z.B. 7.50"
              />
            </div>
            <div className="space-y-1">
              <Label htmlFor="lg_konto">Konto Leergut (optional)</Label>
              <Input
                id="lg_konto"
                {...register('konto_leergut')}
                placeholder="z.B. 0480"
              />
            </div>
            <div className="sm:col-span-3 flex justify-end">
              <Button type="submit" disabled={isSubmitting} aria-label="Leergutart anlegen">
                <Plus className="mr-2 h-4 w-4" />
                Anlegen
              </Button>
            </div>
          </form>
        </CardContent>
      </Card>

      <Card>
        <CardHeader>
          <CardTitle>Leergutarten</CardTitle>
        </CardHeader>
        <CardContent>
          {isLoading ? (
            <div className="space-y-2">
              {[...Array(3)].map((_, i) => (
                <Skeleton key={i} className="h-10 w-full" />
              ))}
            </div>
          ) : !arten?.length ? (
            <p className="text-muted-foreground text-sm py-4 text-center">
              Keine Leergutarten vorhanden.
            </p>
          ) : (
            <Table>
              <TableHeader>
                <TableRow>
                  <TableHead>Art-Nr.</TableHead>
                  <TableHead>Bezeichnung</TableHead>
                  <TableHead>Typ</TableHead>
                  <TableHead>Pfandwert</TableHead>
                  <TableHead className="w-16" />
                </TableRow>
              </TableHeader>
              <TableBody>
                {arten.map((a) => (
                  <TableRow key={a.id}>
                    <TableCell className="font-mono">{a.art_nr}</TableCell>
                    <TableCell>{a.bezeichnung}</TableCell>
                    <TableCell>
                      <Badge variant="outline">
                        {LEERGUT_TYP_LABELS[a.leergut_typ] ?? a.leergut_typ}
                      </Badge>
                    </TableCell>
                    <TableCell className="tabular-nums">
                      {a.pfandwert !== null
                        ? `${Number(a.pfandwert).toFixed(2)} €`
                        : '—'}
                    </TableCell>
                    <TableCell>
                      <Button
                        variant="ghost"
                        size="icon"
                        aria-label={`Leergutart ${a.art_nr} löschen`}
                        disabled={deletingKey === a.art_nr}
                        onClick={() => handleDelete(a.art_nr)}
                      >
                        <Trash2 className="h-4 w-4 text-destructive" />
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

// ── Page ───────────────────────────────────────────────────────────────────────

export default function FibuStammdatenPage() {
  return (
    <div className="p-6 space-y-4">
      <div>
        <h1 className="text-2xl font-semibold">FIBU Zusatzstammdaten</h1>
        <p className="text-muted-foreground text-sm mt-1">
          Zahlungsformulare [FIZAF], Zinsgruppen für Kontokorrentzinsen und Leergutarten.
        </p>
      </div>
      <Tabs defaultValue="zahlungsformulare">
        <TabsList>
          <TabsTrigger value="zahlungsformulare">Zahlungsformulare [FIZAF]</TabsTrigger>
          <TabsTrigger value="zinsgruppen">Zinsgruppen</TabsTrigger>
          <TabsTrigger value="leergutarten">Leergutarten</TabsTrigger>
        </TabsList>
        <TabsContent value="zahlungsformulare" className="mt-4">
          <ZahlungsformulareTab />
        </TabsContent>
        <TabsContent value="zinsgruppen" className="mt-4">
          <ZinsgruppenTab />
        </TabsContent>
        <TabsContent value="leergutarten" className="mt-4">
          <LeergutartenTab />
        </TabsContent>
      </Tabs>
    </div>
  )
}
