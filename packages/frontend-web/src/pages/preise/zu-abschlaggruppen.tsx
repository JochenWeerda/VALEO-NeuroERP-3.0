import { useState } from 'react'
import { useForm } from 'react-hook-form'
import { toast } from 'sonner'
import {
  useZuAbschlaggruppen,
  useCreateZuAbschlaggruppe,
  useDeleteZuAbschlaggruppe,
  useZuAbschlagklassen,
  useCreateZuAbschlagklasse,
  useDeleteZuAbschlagklasse,
  useZuAbschlagKonditionen,
  useCreateZuAbschlagKondition,
  type Richtung,
  type KonditionTyp,
} from '@/lib/api/zuAbschlaggruppen'
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

type GruppeFormData = {
  gruppe_nr: string
  bezeichnung: string
  richtung: Richtung
}

type KlasseFormData = {
  klasse_nr: string
  bezeichnung: string
  richtung: Richtung
}

type KonditionFormData = {
  gruppe_id: string
  klasse_id: string
  kondition_typ: KonditionTyp
  wert: string
  gueltig_ab: string
  gueltig_bis: string
  beschreibung: string
}

function RichtungBadge({ richtung }: { richtung: Richtung }) {
  return (
    <Badge variant={richtung === 'vk' ? 'default' : 'secondary'}>
      {richtung.toUpperCase()}
    </Badge>
  )
}

// ── Gruppen-Tab ───────────────────────────────────────────────────────────────

function GruppenTab() {
  const { data: gruppen, isLoading, isError } = useZuAbschlaggruppen()
  const createMutation = useCreateZuAbschlaggruppe()
  const deleteMutation = useDeleteZuAbschlaggruppe()
  const [deletingKey, setDeletingKey] = useState<string | null>(null)

  const { register, handleSubmit, reset, setValue, watch, formState: { isSubmitting } } =
    useForm<GruppeFormData>({
      defaultValues: { gruppe_nr: '', bezeichnung: '', richtung: 'vk' },
    })

  const richtungValue = watch('richtung')

  const onSubmit = async (data: GruppeFormData) => {
    try {
      await createMutation.mutateAsync(data)
      toast.success(`Zu-/Abschlaggruppe ${data.gruppe_nr} angelegt.`)
      reset()
    } catch {
      toast.error('Fehler beim Anlegen der Zu-/Abschlaggruppe.')
    }
  }

  const handleDelete = async (gruppe_nr: string, richtung: Richtung) => {
    const key = `${gruppe_nr}/${richtung}`
    if (deletingKey === key) return
    setDeletingKey(key)
    try {
      await deleteMutation.mutateAsync({ gruppe_nr, richtung })
      toast.success(`Zu-/Abschlaggruppe ${gruppe_nr} deaktiviert.`)
    } catch {
      toast.error('Fehler beim Deaktivieren der Zu-/Abschlaggruppe.')
    } finally {
      setDeletingKey(null)
    }
  }

  return (
    <div className="space-y-4">
      <Card>
        <CardHeader>
          <CardTitle>Neue Zu-/Abschlaggruppe [ZAGR]</CardTitle>
        </CardHeader>
        <CardContent>
          <form onSubmit={handleSubmit(onSubmit)} noValidate className="grid grid-cols-1 gap-3 sm:grid-cols-4">
            <div>
              <Label htmlFor="zagr_nr">Gruppen-Nr.</Label>
              <Input
                id="zagr_nr"
                placeholder="z. B. ZAGR-01"
                {...register('gruppe_nr', { required: true })}
              />
            </div>
            <div className="sm:col-span-2">
              <Label htmlFor="zagr_bez">Bezeichnung</Label>
              <Input
                id="zagr_bez"
                placeholder="z. B. Frachtaufschlag Fern"
                {...register('bezeichnung', { required: true })}
              />
            </div>
            <div>
              <Label htmlFor="zagr_richtung">Richtung</Label>
              <Select
                value={richtungValue}
                onValueChange={(v) => setValue('richtung', v as Richtung)}
              >
                <SelectTrigger id="zagr_richtung" aria-label="Richtung der Zu-/Abschlaggruppe">
                  <SelectValue />
                </SelectTrigger>
                <SelectContent>
                  <SelectItem value="vk">VK</SelectItem>
                  <SelectItem value="ek">EK</SelectItem>
                </SelectContent>
              </Select>
            </div>
            <div className="sm:col-span-4 flex justify-end">
              <Button type="submit" disabled={isSubmitting} aria-label="Zu-/Abschlaggruppe anlegen">
                <Plus className="mr-1 h-4 w-4" aria-hidden="true" />
                Anlegen
              </Button>
            </div>
          </form>
        </CardContent>
      </Card>

      <Card>
        <CardHeader>
          <CardTitle>Zu-/Abschlaggruppen</CardTitle>
        </CardHeader>
        <CardContent>
          {isLoading && (
            <div className="space-y-2">
              {[0, 1, 2].map((i) => <Skeleton key={i} className="h-9 w-full" />)}
            </div>
          )}
          {isError && (
            <p className="text-sm text-destructive">Fehler beim Laden der Zu-/Abschlaggruppen.</p>
          )}
          {!isLoading && !isError && (!gruppen || gruppen.length === 0) && (
            <p className="text-sm text-muted-foreground">Keine Zu-/Abschlaggruppen vorhanden.</p>
          )}
          {gruppen && gruppen.length > 0 && (
            <Table>
              <TableHeader>
                <TableRow>
                  <TableHead>Gruppen-Nr.</TableHead>
                  <TableHead>Bezeichnung</TableHead>
                  <TableHead>Richtung</TableHead>
                  <TableHead aria-label="Aktionen" />
                </TableRow>
              </TableHeader>
              <TableBody>
                {gruppen.map((g) => {
                  const key = `${g.gruppe_nr}/${g.richtung}`
                  return (
                    <TableRow key={g.id}>
                      <TableCell className="font-mono text-sm">{g.gruppe_nr}</TableCell>
                      <TableCell>{g.bezeichnung}</TableCell>
                      <TableCell><RichtungBadge richtung={g.richtung} /></TableCell>
                      <TableCell className="text-right">
                        <Button
                          variant="ghost"
                          size="icon"
                          disabled={deletingKey === key}
                          onClick={() => handleDelete(g.gruppe_nr, g.richtung)}
                          aria-label={`Zu-/Abschlaggruppe ${g.gruppe_nr} deaktivieren`}
                        >
                          <Trash2 className="h-4 w-4" aria-hidden="true" />
                        </Button>
                      </TableCell>
                    </TableRow>
                  )
                })}
              </TableBody>
            </Table>
          )}
        </CardContent>
      </Card>
    </div>
  )
}

// ── Klassen-Tab ───────────────────────────────────────────────────────────────

function KlassenTab() {
  const { data: klassen, isLoading, isError } = useZuAbschlagklassen()
  const createMutation = useCreateZuAbschlagklasse()
  const deleteMutation = useDeleteZuAbschlagklasse()
  const [deletingKey, setDeletingKey] = useState<string | null>(null)

  const { register, handleSubmit, reset, setValue, watch, formState: { isSubmitting } } =
    useForm<KlasseFormData>({
      defaultValues: { klasse_nr: '', bezeichnung: '', richtung: 'vk' },
    })

  const richtungValue = watch('richtung')

  const onSubmit = async (data: KlasseFormData) => {
    try {
      await createMutation.mutateAsync(data)
      toast.success(`Zu-/Abschlagklasse ${data.klasse_nr} angelegt.`)
      reset()
    } catch {
      toast.error('Fehler beim Anlegen der Zu-/Abschlagklasse.')
    }
  }

  const handleDelete = async (klasse_nr: string, richtung: Richtung) => {
    const key = `${klasse_nr}/${richtung}`
    if (deletingKey === key) return
    setDeletingKey(key)
    try {
      await deleteMutation.mutateAsync({ klasse_nr, richtung })
      toast.success(`Zu-/Abschlagklasse ${klasse_nr} deaktiviert.`)
    } catch {
      toast.error('Fehler beim Deaktivieren der Zu-/Abschlagklasse.')
    } finally {
      setDeletingKey(null)
    }
  }

  return (
    <div className="space-y-4">
      <Card>
        <CardHeader>
          <CardTitle>Neue Zu-/Abschlagklasse [ZAKL]</CardTitle>
        </CardHeader>
        <CardContent>
          <form onSubmit={handleSubmit(onSubmit)} noValidate className="grid grid-cols-1 gap-3 sm:grid-cols-4">
            <div>
              <Label htmlFor="zakl_nr">Klassen-Nr.</Label>
              <Input
                id="zakl_nr"
                placeholder="z. B. ZAKL-A"
                {...register('klasse_nr', { required: true })}
              />
            </div>
            <div className="sm:col-span-2">
              <Label htmlFor="zakl_bez">Bezeichnung</Label>
              <Input
                id="zakl_bez"
                placeholder="z. B. Großhändler"
                {...register('bezeichnung', { required: true })}
              />
            </div>
            <div>
              <Label htmlFor="zakl_richtung">Richtung</Label>
              <Select
                value={richtungValue}
                onValueChange={(v) => setValue('richtung', v as Richtung)}
              >
                <SelectTrigger id="zakl_richtung" aria-label="Richtung der Zu-/Abschlagklasse">
                  <SelectValue />
                </SelectTrigger>
                <SelectContent>
                  <SelectItem value="vk">VK</SelectItem>
                  <SelectItem value="ek">EK</SelectItem>
                </SelectContent>
              </Select>
            </div>
            <div className="sm:col-span-4 flex justify-end">
              <Button type="submit" disabled={isSubmitting} aria-label="Zu-/Abschlagklasse anlegen">
                <Plus className="mr-1 h-4 w-4" aria-hidden="true" />
                Anlegen
              </Button>
            </div>
          </form>
        </CardContent>
      </Card>

      <Card>
        <CardHeader>
          <CardTitle>Zu-/Abschlagklassen</CardTitle>
        </CardHeader>
        <CardContent>
          {isLoading && (
            <div className="space-y-2">
              {[0, 1, 2].map((i) => <Skeleton key={i} className="h-9 w-full" />)}
            </div>
          )}
          {isError && (
            <p className="text-sm text-destructive">Fehler beim Laden der Zu-/Abschlagklassen.</p>
          )}
          {!isLoading && !isError && (!klassen || klassen.length === 0) && (
            <p className="text-sm text-muted-foreground">Keine Zu-/Abschlagklassen vorhanden.</p>
          )}
          {klassen && klassen.length > 0 && (
            <Table>
              <TableHeader>
                <TableRow>
                  <TableHead>Klassen-Nr.</TableHead>
                  <TableHead>Bezeichnung</TableHead>
                  <TableHead>Richtung</TableHead>
                  <TableHead aria-label="Aktionen" />
                </TableRow>
              </TableHeader>
              <TableBody>
                {klassen.map((k) => {
                  const key = `${k.klasse_nr}/${k.richtung}`
                  return (
                    <TableRow key={k.id}>
                      <TableCell className="font-mono text-sm">{k.klasse_nr}</TableCell>
                      <TableCell>{k.bezeichnung}</TableCell>
                      <TableCell><RichtungBadge richtung={k.richtung} /></TableCell>
                      <TableCell className="text-right">
                        <Button
                          variant="ghost"
                          size="icon"
                          disabled={deletingKey === key}
                          onClick={() => handleDelete(k.klasse_nr, k.richtung)}
                          aria-label={`Zu-/Abschlagklasse ${k.klasse_nr} deaktivieren`}
                        >
                          <Trash2 className="h-4 w-4" aria-hidden="true" />
                        </Button>
                      </TableCell>
                    </TableRow>
                  )
                })}
              </TableBody>
            </Table>
          )}
        </CardContent>
      </Card>
    </div>
  )
}

// ── Konditionen-Tab ───────────────────────────────────────────────────────────

function KonditionenTab() {
  const { data: gruppen } = useZuAbschlaggruppen()
  const { data: klassen } = useZuAbschlagklassen()
  const { data: konditionen, isLoading, isError } = useZuAbschlagKonditionen()
  const createMutation = useCreateZuAbschlagKondition()

  const { register, handleSubmit, reset, setValue, watch, formState: { isSubmitting } } =
    useForm<KonditionFormData>({
      defaultValues: {
        gruppe_id: '',
        klasse_id: '',
        kondition_typ: 'prozent',
        wert: '',
        gueltig_ab: '',
        gueltig_bis: '',
        beschreibung: '',
      },
    })

  const konditionTypValue = watch('kondition_typ')
  const gruppeIdValue = watch('gruppe_id')
  const klasseIdValue = watch('klasse_id')

  const onSubmit = async (data: KonditionFormData) => {
    try {
      await createMutation.mutateAsync({
        gruppe_id: data.gruppe_id,
        klasse_id: data.klasse_id,
        kondition_typ: data.kondition_typ,
        wert: parseFloat(data.wert),
        gueltig_ab: data.gueltig_ab,
        gueltig_bis: data.gueltig_bis || null,
        beschreibung: data.beschreibung || null,
      })
      toast.success('Zu-/Abschlagkondition angelegt.')
      reset()
    } catch {
      toast.error('Fehler beim Anlegen der Zu-/Abschlagkondition.')
    }
  }

  const gruppeLabel = (id: string) => {
    const g = gruppen?.find((x) => x.id === id)
    return g ? `${g.gruppe_nr} — ${g.bezeichnung}` : id
  }

  const klasseLabel = (id: string) => {
    const k = klassen?.find((x) => x.id === id)
    return k ? `${k.klasse_nr} — ${k.bezeichnung}` : id
  }

  return (
    <div className="space-y-4">
      <Card>
        <CardHeader>
          <CardTitle>Neue Zu-/Abschlagkondition [ZAK]</CardTitle>
        </CardHeader>
        <CardContent>
          <form onSubmit={handleSubmit(onSubmit)} noValidate className="grid grid-cols-1 gap-3 sm:grid-cols-2">
            <div>
              <Label htmlFor="zak_gruppe">Zu-/Abschlaggruppe</Label>
              <select
                id="zak_gruppe"
                value={gruppeIdValue}
                onChange={(e) => setValue('gruppe_id', e.target.value)}
                className="flex h-9 w-full rounded-md border border-input bg-transparent px-3 py-1 text-sm shadow-sm"
                aria-label="Zu-/Abschlaggruppe der Kondition"
              >
                <option value="">— Gruppe wählen —</option>
                {(gruppen ?? []).map((g) => (
                  <option key={g.id} value={g.id}>
                    {g.gruppe_nr} — {g.bezeichnung} ({g.richtung.toUpperCase()})
                  </option>
                ))}
              </select>
            </div>
            <div>
              <Label htmlFor="zak_klasse">Zu-/Abschlagklasse</Label>
              <select
                id="zak_klasse"
                value={klasseIdValue}
                onChange={(e) => setValue('klasse_id', e.target.value)}
                className="flex h-9 w-full rounded-md border border-input bg-transparent px-3 py-1 text-sm shadow-sm"
                aria-label="Zu-/Abschlagklasse der Kondition"
              >
                <option value="">— Klasse wählen —</option>
                {(klassen ?? []).map((k) => (
                  <option key={k.id} value={k.id}>
                    {k.klasse_nr} — {k.bezeichnung} ({k.richtung.toUpperCase()})
                  </option>
                ))}
              </select>
            </div>
            <div>
              <Label htmlFor="zak_typ">Konditionstyp</Label>
              <Select
                value={konditionTypValue}
                onValueChange={(v) => setValue('kondition_typ', v as KonditionTyp)}
              >
                <SelectTrigger id="zak_typ" aria-label="Konditionstyp">
                  <SelectValue />
                </SelectTrigger>
                <SelectContent>
                  <SelectItem value="prozent">Prozent (%)</SelectItem>
                  <SelectItem value="betrag">Betrag (€)</SelectItem>
                </SelectContent>
              </Select>
            </div>
            <div>
              <Label htmlFor="zak_wert">
                Wert ({konditionTypValue === 'prozent' ? '%' : '€'}, negativ = Abschlag)
              </Label>
              <Input
                id="zak_wert"
                type="number"
                step="0.01"
                placeholder="z. B. 2.50 oder -1.00"
                {...register('wert', { required: true })}
              />
            </div>
            <div>
              <Label htmlFor="zak_ab">Gültig ab</Label>
              <Input
                id="zak_ab"
                type="date"
                {...register('gueltig_ab', { required: true })}
              />
            </div>
            <div>
              <Label htmlFor="zak_bis">Gültig bis (optional)</Label>
              <Input
                id="zak_bis"
                type="date"
                {...register('gueltig_bis')}
              />
            </div>
            <div className="sm:col-span-2">
              <Label htmlFor="zak_beschreibung">Beschreibung (optional)</Label>
              <Input
                id="zak_beschreibung"
                placeholder="z. B. Frachtaufschlag Region Nord"
                {...register('beschreibung')}
              />
            </div>
            <div className="sm:col-span-2 flex justify-end">
              <Button type="submit" disabled={isSubmitting} aria-label="Zu-/Abschlagkondition anlegen">
                <Plus className="mr-1 h-4 w-4" aria-hidden="true" />
                Kondition anlegen
              </Button>
            </div>
          </form>
        </CardContent>
      </Card>

      <Card>
        <CardHeader>
          <CardTitle>Aktive Konditionen</CardTitle>
        </CardHeader>
        <CardContent>
          {isLoading && (
            <div className="space-y-2">
              {[0, 1, 2].map((i) => <Skeleton key={i} className="h-9 w-full" />)}
            </div>
          )}
          {isError && (
            <p className="text-sm text-destructive">Fehler beim Laden der Konditionen.</p>
          )}
          {!isLoading && !isError && (!konditionen || konditionen.length === 0) && (
            <p className="text-sm text-muted-foreground">Keine aktiven Konditionen vorhanden.</p>
          )}
          {konditionen && konditionen.length > 0 && (
            <Table>
              <TableHeader>
                <TableRow>
                  <TableHead>Gruppe</TableHead>
                  <TableHead>Klasse</TableHead>
                  <TableHead>Typ</TableHead>
                  <TableHead className="text-right">Wert</TableHead>
                  <TableHead>Gültig ab</TableHead>
                  <TableHead>Gültig bis</TableHead>
                </TableRow>
              </TableHeader>
              <TableBody>
                {konditionen.map((k) => (
                  <TableRow key={k.id}>
                    <TableCell className="font-mono text-sm">{gruppeLabel(k.gruppe_id)}</TableCell>
                    <TableCell className="font-mono text-sm">{klasseLabel(k.klasse_id)}</TableCell>
                    <TableCell>
                      <Badge variant="outline">
                        {k.kondition_typ === 'prozent' ? '%' : '€'}
                      </Badge>
                    </TableCell>
                    <TableCell className="text-right font-mono text-sm">
                      {k.wert > 0 ? '+' : ''}{Number(k.wert).toFixed(2)}
                    </TableCell>
                    <TableCell className="text-sm">{k.gueltig_ab}</TableCell>
                    <TableCell className="text-sm text-muted-foreground">
                      {k.gueltig_bis ?? '—'}
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

// ── Hauptseite ────────────────────────────────────────────────────────────────

export default function ZuAbschlaggruppenPage() {
  return (
    <div className="p-6 space-y-4">
      <div>
        <h1 className="text-2xl font-semibold">Zu-/Abschlaggruppen & -klassen</h1>
        <p className="text-sm text-muted-foreground mt-1">
          Konditionsstammdaten — Gruppen [ZAGR] werden Artikeln zugeordnet,
          Klassen [ZAKL] Kunden/Lieferanten. Die Kombination ergibt die Zu-/Abschläge [ZAK].
        </p>
      </div>

      <Tabs defaultValue="gruppen">
        <TabsList>
          <TabsTrigger value="gruppen">Gruppen [ZAGR]</TabsTrigger>
          <TabsTrigger value="klassen">Klassen [ZAKL]</TabsTrigger>
          <TabsTrigger value="konditionen">Konditionen [ZAK]</TabsTrigger>
        </TabsList>

        <TabsContent value="gruppen" className="mt-4">
          <GruppenTab />
        </TabsContent>

        <TabsContent value="klassen" className="mt-4">
          <KlassenTab />
        </TabsContent>

        <TabsContent value="konditionen" className="mt-4">
          <KonditionenTab />
        </TabsContent>
      </Tabs>
    </div>
  )
}
