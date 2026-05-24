import { useState } from 'react'
import { useForm } from 'react-hook-form'
import { toast } from 'sonner'
import {
  useRabattgruppen,
  useCreateRabattgruppe,
  useDeleteRabattgruppe,
  useRabattklassen,
  useCreateRabattklasse,
  useDeleteRabattklasse,
  useRabattsaetze,
  useCreateRabattsatz,
  useDeleteRabattsatz,
  type Richtung,
} from '@/lib/api/rabattgruppen'
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

type SatzFormData = {
  rabattgruppe_nr: string
  rabattklasse_nr: string
  richtung: Richtung
  rabatt_prozent: string
  ab_menge: string
  gueltig_ab: string
  gueltig_bis: string
}

function RichtungBadge({ richtung }: { richtung: Richtung }) {
  return (
    <Badge variant={richtung === 'VK' ? 'default' : 'secondary'}>
      {richtung === 'VK' ? 'Verkauf' : 'Einkauf'}
    </Badge>
  )
}

function RabattgruppenTab() {
  const [filterRichtung, setFilterRichtung] = useState<Richtung | undefined>(undefined)
  const [deletingId, setDeletingId] = useState<string | null>(null)
  const { data: gruppen, isLoading } = useRabattgruppen(filterRichtung)
  const createMutation = useCreateRabattgruppe()
  const deleteMutation = useDeleteRabattgruppe()

  const { register, handleSubmit, reset, setValue } = useForm<GruppeFormData>({
    defaultValues: { gruppe_nr: '', bezeichnung: '', richtung: 'VK' },
  })

  const onSubmit = handleSubmit(async (data) => {
    try {
      await createMutation.mutateAsync(data)
      toast.success(`Rabattgruppe ${data.gruppe_nr} angelegt`)
      reset()
    } catch {
      toast.error('Fehler beim Anlegen der Rabattgruppe')
    }
  })

  const handleDelete = async (id: string, nr: string) => {
    if (deletingId) return
    setDeletingId(id)
    try {
      await deleteMutation.mutateAsync(id)
      toast.success(`Rabattgruppe ${nr} deaktiviert`)
    } catch {
      toast.error('Fehler beim Deaktivieren')
    } finally {
      setDeletingId(null)
    }
  }

  return (
    <div className="space-y-6">
      <Card>
        <CardHeader>
          <CardTitle className="text-base">Neue Rabattgruppe [RAG]</CardTitle>
        </CardHeader>
        <CardContent>
          <form onSubmit={onSubmit} className="grid grid-cols-1 sm:grid-cols-4 gap-4 items-end">
            <div className="space-y-1">
              <Label htmlFor="gruppe_nr">Gruppen-Nr</Label>
              <Input
                id="gruppe_nr"
                placeholder="z.B. RAG01"
                {...register('gruppe_nr', { required: true })}
              />
            </div>
            <div className="space-y-1 sm:col-span-2">
              <Label htmlFor="gruppe_bez">Bezeichnung</Label>
              <Input
                id="gruppe_bez"
                placeholder="Bezeichnung"
                {...register('bezeichnung', { required: true })}
              />
            </div>
            <div className="space-y-1">
              <Label>Richtung</Label>
              <Select
                defaultValue="VK"
                onValueChange={(v) => setValue('richtung', v as Richtung)}
              >
                <SelectTrigger aria-label="Richtung Rabattgruppe">
                  <SelectValue />
                </SelectTrigger>
                <SelectContent>
                  <SelectItem value="VK">Verkauf (VK)</SelectItem>
                  <SelectItem value="EK">Einkauf (EK)</SelectItem>
                </SelectContent>
              </Select>
            </div>
            <div className="sm:col-span-4 flex justify-end">
              <Button
                type="submit"
                disabled={createMutation.isPending}
                className="gap-2"
                aria-label="Rabattgruppe anlegen"
              >
                <Plus className="h-4 w-4" />
                {createMutation.isPending ? 'Speichern…' : 'Anlegen'}
              </Button>
            </div>
          </form>
        </CardContent>
      </Card>

      <Card>
        <CardHeader className="flex flex-row items-center justify-between">
          <CardTitle className="text-base">Rabattgruppen</CardTitle>
          <Select
            value={filterRichtung ?? 'alle'}
            onValueChange={(v) => setFilterRichtung(v === 'alle' ? undefined : (v as Richtung))}
          >
            <SelectTrigger className="w-40" aria-label="Richtung filtern">
              <SelectValue />
            </SelectTrigger>
            <SelectContent>
              <SelectItem value="alle">Alle</SelectItem>
              <SelectItem value="VK">Verkauf (VK)</SelectItem>
              <SelectItem value="EK">Einkauf (EK)</SelectItem>
            </SelectContent>
          </Select>
        </CardHeader>
        <CardContent>
          {isLoading ? (
            <div className="space-y-2">
              {Array.from({ length: 3 }).map((_, i) => (
                <Skeleton key={i} className="h-10 w-full" />
              ))}
            </div>
          ) : (
            <Table>
              <TableHeader>
                <TableRow>
                  <TableHead>Nr</TableHead>
                  <TableHead>Bezeichnung</TableHead>
                  <TableHead>Richtung</TableHead>
                  <TableHead className="w-16" />
                </TableRow>
              </TableHeader>
              <TableBody>
                {gruppen?.length === 0 && (
                  <TableRow>
                    <TableCell colSpan={4} className="text-center text-muted-foreground py-6">
                      Keine Rabattgruppen vorhanden
                    </TableCell>
                  </TableRow>
                )}
                {gruppen?.map((g) => (
                  <TableRow key={g.id}>
                    <TableCell className="font-mono">{g.gruppe_nr}</TableCell>
                    <TableCell>{g.bezeichnung}</TableCell>
                    <TableCell>
                      <RichtungBadge richtung={g.richtung} />
                    </TableCell>
                    <TableCell>
                      <Button
                        variant="ghost"
                        size="sm"
                        disabled={deletingId === g.id}
                        onClick={() => handleDelete(g.id, g.gruppe_nr)}
                        aria-label={`Rabattgruppe ${g.gruppe_nr} deaktivieren`}
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

function RabattklassenTab() {
  const [filterRichtung, setFilterRichtung] = useState<Richtung | undefined>(undefined)
  const [deletingId, setDeletingId] = useState<string | null>(null)
  const { data: klassen, isLoading } = useRabattklassen(filterRichtung)
  const createMutation = useCreateRabattklasse()
  const deleteMutation = useDeleteRabattklasse()

  const { register, handleSubmit, reset, setValue } = useForm<KlasseFormData>({
    defaultValues: { klasse_nr: '', bezeichnung: '', richtung: 'VK' },
  })

  const onSubmit = handleSubmit(async (data) => {
    try {
      await createMutation.mutateAsync(data)
      toast.success(`Rabattklasse ${data.klasse_nr} angelegt`)
      reset()
    } catch {
      toast.error('Fehler beim Anlegen der Rabattklasse')
    }
  })

  const handleDelete = async (id: string, nr: string) => {
    if (deletingId) return
    setDeletingId(id)
    try {
      await deleteMutation.mutateAsync(id)
      toast.success(`Rabattklasse ${nr} deaktiviert`)
    } catch {
      toast.error('Fehler beim Deaktivieren')
    } finally {
      setDeletingId(null)
    }
  }

  return (
    <div className="space-y-6">
      <Card>
        <CardHeader>
          <CardTitle className="text-base">Neue Rabattklasse [RAK]</CardTitle>
        </CardHeader>
        <CardContent>
          <form onSubmit={onSubmit} className="grid grid-cols-1 sm:grid-cols-4 gap-4 items-end">
            <div className="space-y-1">
              <Label htmlFor="klasse_nr">Klassen-Nr</Label>
              <Input
                id="klasse_nr"
                placeholder="z.B. RAK01"
                {...register('klasse_nr', { required: true })}
              />
            </div>
            <div className="space-y-1 sm:col-span-2">
              <Label htmlFor="klasse_bez">Bezeichnung</Label>
              <Input
                id="klasse_bez"
                placeholder="Bezeichnung"
                {...register('bezeichnung', { required: true })}
              />
            </div>
            <div className="space-y-1">
              <Label>Richtung</Label>
              <Select
                defaultValue="VK"
                onValueChange={(v) => setValue('richtung', v as Richtung)}
              >
                <SelectTrigger aria-label="Richtung Rabattklasse">
                  <SelectValue />
                </SelectTrigger>
                <SelectContent>
                  <SelectItem value="VK">Verkauf (VK)</SelectItem>
                  <SelectItem value="EK">Einkauf (EK)</SelectItem>
                </SelectContent>
              </Select>
            </div>
            <div className="sm:col-span-4 flex justify-end">
              <Button
                type="submit"
                disabled={createMutation.isPending}
                className="gap-2"
                aria-label="Rabattklasse anlegen"
              >
                <Plus className="h-4 w-4" />
                {createMutation.isPending ? 'Speichern…' : 'Anlegen'}
              </Button>
            </div>
          </form>
        </CardContent>
      </Card>

      <Card>
        <CardHeader className="flex flex-row items-center justify-between">
          <CardTitle className="text-base">Rabattklassen</CardTitle>
          <Select
            value={filterRichtung ?? 'alle'}
            onValueChange={(v) => setFilterRichtung(v === 'alle' ? undefined : (v as Richtung))}
          >
            <SelectTrigger className="w-40" aria-label="Richtung filtern Klassen">
              <SelectValue />
            </SelectTrigger>
            <SelectContent>
              <SelectItem value="alle">Alle</SelectItem>
              <SelectItem value="VK">Verkauf (VK)</SelectItem>
              <SelectItem value="EK">Einkauf (EK)</SelectItem>
            </SelectContent>
          </Select>
        </CardHeader>
        <CardContent>
          {isLoading ? (
            <div className="space-y-2">
              {Array.from({ length: 3 }).map((_, i) => (
                <Skeleton key={i} className="h-10 w-full" />
              ))}
            </div>
          ) : (
            <Table>
              <TableHeader>
                <TableRow>
                  <TableHead>Nr</TableHead>
                  <TableHead>Bezeichnung</TableHead>
                  <TableHead>Richtung</TableHead>
                  <TableHead className="w-16" />
                </TableRow>
              </TableHeader>
              <TableBody>
                {klassen?.length === 0 && (
                  <TableRow>
                    <TableCell colSpan={4} className="text-center text-muted-foreground py-6">
                      Keine Rabattklassen vorhanden
                    </TableCell>
                  </TableRow>
                )}
                {klassen?.map((k) => (
                  <TableRow key={k.id}>
                    <TableCell className="font-mono">{k.klasse_nr}</TableCell>
                    <TableCell>{k.bezeichnung}</TableCell>
                    <TableCell>
                      <RichtungBadge richtung={k.richtung} />
                    </TableCell>
                    <TableCell>
                      <Button
                        variant="ghost"
                        size="sm"
                        disabled={deletingId === k.id}
                        onClick={() => handleDelete(k.id, k.klasse_nr)}
                        aria-label={`Rabattklasse ${k.klasse_nr} deaktivieren`}
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

function RabattsaetzeTab() {
  const [deletingId, setDeletingId] = useState<string | null>(null)
  const { data: saetze, isLoading } = useRabattsaetze()
  const createMutation = useCreateRabattsatz()
  const deleteMutation = useDeleteRabattsatz()

  const { register, handleSubmit, reset, setValue } = useForm<SatzFormData>({
    defaultValues: {
      rabattgruppe_nr: '',
      rabattklasse_nr: '',
      richtung: 'VK',
      rabatt_prozent: '',
      ab_menge: '',
      gueltig_ab: '',
      gueltig_bis: '',
    },
  })

  const onSubmit = handleSubmit(async (data) => {
    try {
      await createMutation.mutateAsync({
        rabattgruppe_nr: data.rabattgruppe_nr,
        rabattklasse_nr: data.rabattklasse_nr,
        richtung: data.richtung,
        rabatt_prozent: parseFloat(data.rabatt_prozent),
        ab_menge: data.ab_menge ? parseFloat(data.ab_menge) : null,
        gueltig_ab: data.gueltig_ab || null,
        gueltig_bis: data.gueltig_bis || null,
      })
      toast.success('Rabattsatz angelegt')
      reset()
    } catch {
      toast.error('Fehler beim Anlegen des Rabattsatzes')
    }
  })

  const handleDelete = async (id: string) => {
    if (deletingId) return
    setDeletingId(id)
    try {
      await deleteMutation.mutateAsync(id)
      toast.success('Rabattsatz gelöscht')
    } catch {
      toast.error('Fehler beim Löschen')
    } finally {
      setDeletingId(null)
    }
  }

  return (
    <div className="space-y-6">
      <Card>
        <CardHeader>
          <CardTitle className="text-base">Neuer Rabattsatz</CardTitle>
        </CardHeader>
        <CardContent>
          <form onSubmit={onSubmit} className="grid grid-cols-1 sm:grid-cols-3 gap-4 items-end">
            <div className="space-y-1">
              <Label htmlFor="satz_gruppe">Rabattgruppe-Nr</Label>
              <Input
                id="satz_gruppe"
                placeholder="z.B. RAG01"
                {...register('rabattgruppe_nr', { required: true })}
              />
            </div>
            <div className="space-y-1">
              <Label htmlFor="satz_klasse">Rabattklasse-Nr</Label>
              <Input
                id="satz_klasse"
                placeholder="z.B. RAK01"
                {...register('rabattklasse_nr', { required: true })}
              />
            </div>
            <div className="space-y-1">
              <Label>Richtung</Label>
              <Select
                defaultValue="VK"
                onValueChange={(v) => setValue('richtung', v as Richtung)}
              >
                <SelectTrigger aria-label="Richtung Rabattsatz">
                  <SelectValue />
                </SelectTrigger>
                <SelectContent>
                  <SelectItem value="VK">Verkauf (VK)</SelectItem>
                  <SelectItem value="EK">Einkauf (EK)</SelectItem>
                </SelectContent>
              </Select>
            </div>
            <div className="space-y-1">
              <Label htmlFor="rabatt_prozent">Rabatt %</Label>
              <Input
                id="rabatt_prozent"
                type="number"
                step="0.01"
                min="0"
                max="100"
                placeholder="0.00"
                {...register('rabatt_prozent', { required: true })}
              />
            </div>
            <div className="space-y-1">
              <Label htmlFor="ab_menge">Ab Menge</Label>
              <Input
                id="ab_menge"
                type="number"
                step="0.001"
                min="0"
                placeholder="optional"
                {...register('ab_menge')}
              />
            </div>
            <div className="space-y-1">
              <Label htmlFor="gueltig_ab">Gültig ab</Label>
              <Input
                id="gueltig_ab"
                type="date"
                {...register('gueltig_ab')}
              />
            </div>
            <div className="space-y-1">
              <Label htmlFor="gueltig_bis">Gültig bis</Label>
              <Input
                id="gueltig_bis"
                type="date"
                {...register('gueltig_bis')}
              />
            </div>
            <div className="sm:col-span-3 flex justify-end">
              <Button
                type="submit"
                disabled={createMutation.isPending}
                className="gap-2"
                aria-label="Rabattsatz anlegen"
              >
                <Plus className="h-4 w-4" />
                {createMutation.isPending ? 'Speichern…' : 'Anlegen'}
              </Button>
            </div>
          </form>
        </CardContent>
      </Card>

      <Card>
        <CardHeader>
          <CardTitle className="text-base">Rabattsätze (Gruppe × Klasse)</CardTitle>
        </CardHeader>
        <CardContent>
          {isLoading ? (
            <div className="space-y-2">
              {Array.from({ length: 4 }).map((_, i) => (
                <Skeleton key={i} className="h-10 w-full" />
              ))}
            </div>
          ) : (
            <Table>
              <TableHeader>
                <TableRow>
                  <TableHead>Gruppe</TableHead>
                  <TableHead>Klasse</TableHead>
                  <TableHead>Richtung</TableHead>
                  <TableHead className="text-right">Rabatt %</TableHead>
                  <TableHead className="text-right">Ab Menge</TableHead>
                  <TableHead>Gültig ab</TableHead>
                  <TableHead>Gültig bis</TableHead>
                  <TableHead className="w-16" />
                </TableRow>
              </TableHeader>
              <TableBody>
                {saetze?.length === 0 && (
                  <TableRow>
                    <TableCell colSpan={8} className="text-center text-muted-foreground py-6">
                      Keine Rabattsätze vorhanden
                    </TableCell>
                  </TableRow>
                )}
                {saetze?.map((s) => (
                  <TableRow key={s.id}>
                    <TableCell className="font-mono">{s.rabattgruppe_nr}</TableCell>
                    <TableCell className="font-mono">{s.rabattklasse_nr}</TableCell>
                    <TableCell>
                      <RichtungBadge richtung={s.richtung} />
                    </TableCell>
                    <TableCell className="text-right tabular-nums">
                      {Number(s.rabatt_prozent).toFixed(2)} %
                    </TableCell>
                    <TableCell className="text-right tabular-nums">
                      {s.ab_menge != null ? s.ab_menge : '—'}
                    </TableCell>
                    <TableCell>{s.gueltig_ab ?? '—'}</TableCell>
                    <TableCell>{s.gueltig_bis ?? '—'}</TableCell>
                    <TableCell>
                      <Button
                        variant="ghost"
                        size="sm"
                        disabled={deletingId === s.id}
                        onClick={() => handleDelete(s.id)}
                        aria-label="Rabattsatz löschen"
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

export default function RabattgruppenPage() {
  return (
    <div className="p-6 space-y-4">
      <div>
        <h1 className="text-2xl font-semibold">Rabattgruppen &amp; -klassen [RAG/RAK]</h1>
        <p className="text-muted-foreground text-sm mt-1">
          Stammdaten für die Rabattpflege. Rabattgruppen werden Artikeln, Rabattklassen Kunden/Lieferanten zugeordnet.
          Der Schnittpunkt ergibt den gültigen Rabattsatz.
        </p>
      </div>
      <Tabs defaultValue="gruppen">
        <TabsList>
          <TabsTrigger value="gruppen">Rabattgruppen [RAG]</TabsTrigger>
          <TabsTrigger value="klassen">Rabattklassen [RAK]</TabsTrigger>
          <TabsTrigger value="saetze">Rabattsätze</TabsTrigger>
        </TabsList>
        <TabsContent value="gruppen" className="mt-4">
          <RabattgruppenTab />
        </TabsContent>
        <TabsContent value="klassen" className="mt-4">
          <RabattklassenTab />
        </TabsContent>
        <TabsContent value="saetze" className="mt-4">
          <RabattsaetzeTab />
        </TabsContent>
      </Tabs>
    </div>
  )
}
