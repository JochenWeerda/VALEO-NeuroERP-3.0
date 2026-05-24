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
  type Richtung,
} from '@/lib/api/zu-abschlaege'
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

function RichtungBadge({ richtung }: { richtung: Richtung }) {
  return (
    <Badge variant={richtung === 'vk' ? 'default' : 'secondary'}>
      {richtung === 'vk' ? 'Verkauf' : 'Einkauf'}
    </Badge>
  )
}

function GruppenTab() {
  const [filterRichtung, setFilterRichtung] = useState<Richtung | undefined>()
  const [deletingKey, setDeletingKey] = useState<string | null>(null)
  const { data: gruppen, isLoading } = useZuAbschlaggruppen(filterRichtung)
  const createMutation = useCreateZuAbschlaggruppe()
  const deleteMutation = useDeleteZuAbschlaggruppe()

  const { register, handleSubmit, reset, setValue, watch, formState: { errors, isSubmitting } } = useForm<GruppeFormData>({
    defaultValues: { richtung: 'vk' },
  })
  const richtungValue = watch('richtung')

  const onSubmit = async (data: GruppeFormData) => {
    try {
      await createMutation.mutateAsync(data)
      toast.success(`Zu-/Abschlaggruppe "${data.gruppe_nr}" angelegt.`)
      reset({ richtung: 'vk' })
    } catch {
      toast.error('Fehler beim Anlegen der Gruppe. Prüfen Sie Duplikate.')
    }
  }

  const handleDelete = async (gruppe_nr: string, richtung: Richtung) => {
    const key = `${gruppe_nr}/${richtung}`
    if (deletingKey === key) return
    setDeletingKey(key)
    try {
      await deleteMutation.mutateAsync({ gruppe_nr, richtung })
      toast.success(`Gruppe "${gruppe_nr}" deaktiviert.`)
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
          <CardTitle>Neue Zu-/Abschlaggruppe</CardTitle>
        </CardHeader>
        <CardContent>
          <form onSubmit={handleSubmit(onSubmit)} className="grid grid-cols-1 gap-4 sm:grid-cols-4">
            <div className="space-y-1">
              <Label htmlFor="gruppe_nr">Gruppen-Nr.</Label>
              <Input
                id="gruppe_nr"
                {...register('gruppe_nr', { required: 'Pflichtfeld' })}
                placeholder="z.B. ZAG-001"
                aria-invalid={!!errors.gruppe_nr}
              />
              {errors.gruppe_nr && (
                <p className="text-destructive text-xs">{errors.gruppe_nr.message}</p>
              )}
            </div>
            <div className="space-y-1 sm:col-span-2">
              <Label htmlFor="bezeichnung_gr">Bezeichnung</Label>
              <Input
                id="bezeichnung_gr"
                {...register('bezeichnung', { required: 'Pflichtfeld' })}
                placeholder="z.B. Qualitätszuschlag Weizen"
                aria-invalid={!!errors.bezeichnung}
              />
              {errors.bezeichnung && (
                <p className="text-destructive text-xs">{errors.bezeichnung.message}</p>
              )}
            </div>
            <div className="space-y-1">
              <Label htmlFor="richtung_gr">Richtung</Label>
              <Select
                value={richtungValue}
                onValueChange={(v) => setValue('richtung', v as Richtung)}
              >
                <SelectTrigger id="richtung_gr" aria-label="Richtung Gruppe">
                  <SelectValue />
                </SelectTrigger>
                <SelectContent>
                  <SelectItem value="vk">Verkauf (VK)</SelectItem>
                  <SelectItem value="ek">Einkauf (EK)</SelectItem>
                </SelectContent>
              </Select>
            </div>
            <div className="sm:col-span-4 flex justify-end">
              <Button type="submit" disabled={isSubmitting} aria-label="Gruppe anlegen">
                <Plus className="mr-2 h-4 w-4" />
                Anlegen
              </Button>
            </div>
          </form>
        </CardContent>
      </Card>

      <Card>
        <CardHeader className="flex flex-row items-center justify-between">
          <CardTitle>Zu-/Abschlaggruppen</CardTitle>
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
              {[...Array(4)].map((_, i) => <Skeleton key={i} className="h-10 w-full" />)}
            </div>
          ) : !gruppen?.length ? (
            <p className="text-muted-foreground text-sm py-4 text-center">
              Keine Gruppen vorhanden.
            </p>
          ) : (
            <Table>
              <TableHeader>
                <TableRow>
                  <TableHead>Gruppen-Nr.</TableHead>
                  <TableHead>Bezeichnung</TableHead>
                  <TableHead>Richtung</TableHead>
                  <TableHead className="w-16" />
                </TableRow>
              </TableHeader>
              <TableBody>
                {gruppen.map((g) => (
                  <TableRow key={g.id}>
                    <TableCell className="font-mono">{g.gruppe_nr}</TableCell>
                    <TableCell>{g.bezeichnung}</TableCell>
                    <TableCell><RichtungBadge richtung={g.richtung} /></TableCell>
                    <TableCell>
                      <Button
                        variant="ghost"
                        size="icon"
                        aria-label={`Gruppe ${g.gruppe_nr} löschen`}
                        disabled={deletingKey === `${g.gruppe_nr}/${g.richtung}`}
                        onClick={() => handleDelete(g.gruppe_nr, g.richtung)}
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

function KlassenTab() {
  const [filterRichtung, setFilterRichtung] = useState<Richtung | undefined>()
  const [deletingKey, setDeletingKey] = useState<string | null>(null)
  const { data: klassen, isLoading } = useZuAbschlagklassen(filterRichtung)
  const createMutation = useCreateZuAbschlagklasse()
  const deleteMutation = useDeleteZuAbschlagklasse()

  const { register, handleSubmit, reset, setValue, watch, formState: { errors, isSubmitting } } = useForm<KlasseFormData>({
    defaultValues: { richtung: 'vk' },
  })
  const richtungValue = watch('richtung')

  const onSubmit = async (data: KlasseFormData) => {
    try {
      await createMutation.mutateAsync(data)
      toast.success(`Zu-/Abschlagklasse "${data.klasse_nr}" angelegt.`)
      reset({ richtung: 'vk' })
    } catch {
      toast.error('Fehler beim Anlegen der Klasse. Prüfen Sie Duplikate.')
    }
  }

  const handleDelete = async (klasse_nr: string, richtung: Richtung) => {
    const key = `${klasse_nr}/${richtung}`
    if (deletingKey === key) return
    setDeletingKey(key)
    try {
      await deleteMutation.mutateAsync({ klasse_nr, richtung })
      toast.success(`Klasse "${klasse_nr}" deaktiviert.`)
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
          <CardTitle>Neue Zu-/Abschlagklasse</CardTitle>
        </CardHeader>
        <CardContent>
          <form onSubmit={handleSubmit(onSubmit)} className="grid grid-cols-1 gap-4 sm:grid-cols-4">
            <div className="space-y-1">
              <Label htmlFor="klasse_nr">Klassen-Nr.</Label>
              <Input
                id="klasse_nr"
                {...register('klasse_nr', { required: 'Pflichtfeld' })}
                placeholder="z.B. ZAK-001"
                aria-invalid={!!errors.klasse_nr}
              />
              {errors.klasse_nr && (
                <p className="text-destructive text-xs">{errors.klasse_nr.message}</p>
              )}
            </div>
            <div className="space-y-1 sm:col-span-2">
              <Label htmlFor="bezeichnung_kl">Bezeichnung</Label>
              <Input
                id="bezeichnung_kl"
                {...register('bezeichnung', { required: 'Pflichtfeld' })}
                placeholder="z.B. Großkunde Stufe 1"
                aria-invalid={!!errors.bezeichnung}
              />
              {errors.bezeichnung && (
                <p className="text-destructive text-xs">{errors.bezeichnung.message}</p>
              )}
            </div>
            <div className="space-y-1">
              <Label htmlFor="richtung_kl">Richtung</Label>
              <Select
                value={richtungValue}
                onValueChange={(v) => setValue('richtung', v as Richtung)}
              >
                <SelectTrigger id="richtung_kl" aria-label="Richtung Klasse">
                  <SelectValue />
                </SelectTrigger>
                <SelectContent>
                  <SelectItem value="vk">Verkauf (VK)</SelectItem>
                  <SelectItem value="ek">Einkauf (EK)</SelectItem>
                </SelectContent>
              </Select>
            </div>
            <div className="sm:col-span-4 flex justify-end">
              <Button type="submit" disabled={isSubmitting} aria-label="Klasse anlegen">
                <Plus className="mr-2 h-4 w-4" />
                Anlegen
              </Button>
            </div>
          </form>
        </CardContent>
      </Card>

      <Card>
        <CardHeader className="flex flex-row items-center justify-between">
          <CardTitle>Zu-/Abschlagklassen</CardTitle>
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
              {[...Array(4)].map((_, i) => <Skeleton key={i} className="h-10 w-full" />)}
            </div>
          ) : !klassen?.length ? (
            <p className="text-muted-foreground text-sm py-4 text-center">
              Keine Klassen vorhanden.
            </p>
          ) : (
            <Table>
              <TableHeader>
                <TableRow>
                  <TableHead>Klassen-Nr.</TableHead>
                  <TableHead>Bezeichnung</TableHead>
                  <TableHead>Richtung</TableHead>
                  <TableHead className="w-16" />
                </TableRow>
              </TableHeader>
              <TableBody>
                {klassen.map((k) => (
                  <TableRow key={k.id}>
                    <TableCell className="font-mono">{k.klasse_nr}</TableCell>
                    <TableCell>{k.bezeichnung}</TableCell>
                    <TableCell><RichtungBadge richtung={k.richtung} /></TableCell>
                    <TableCell>
                      <Button
                        variant="ghost"
                        size="icon"
                        aria-label={`Klasse ${k.klasse_nr} löschen`}
                        disabled={deletingKey === `${k.klasse_nr}/${k.richtung}`}
                        onClick={() => handleDelete(k.klasse_nr, k.richtung)}
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

export default function ZuAbschlaggruppenPage() {
  return (
    <div className="p-6 space-y-4">
      <div>
        <h1 className="text-2xl font-semibold">Zu-/Abschlaggruppen & -klassen</h1>
        <p className="text-muted-foreground text-sm mt-1">
          Konditionsstammdaten: Gruppen werden Artikeln, Klassen werden Kunden/Lieferanten zugeordnet.
        </p>
      </div>
      <Tabs defaultValue="gruppen">
        <TabsList>
          <TabsTrigger value="gruppen">Gruppen [ZAGR]</TabsTrigger>
          <TabsTrigger value="klassen">Klassen [ZAKL]</TabsTrigger>
        </TabsList>
        <TabsContent value="gruppen" className="mt-4">
          <GruppenTab />
        </TabsContent>
        <TabsContent value="klassen" className="mt-4">
          <KlassenTab />
        </TabsContent>
      </Tabs>
    </div>
  )
}
