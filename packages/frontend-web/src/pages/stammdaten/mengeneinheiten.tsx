import { useState } from 'react'
import { useForm } from 'react-hook-form'
import { toast } from 'sonner'
import {
  useMengeneinheiten,
  useCreateMengeneinheit,
  useDeleteMengeneinheit,
  useMengeneinheitengruppen,
  useCreateMengeneinheitengruppe,
  useDeleteMengeneinheitengruppe,
} from '@/lib/api/mengeneinheiten'
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
import { Skeleton } from '@/components/ui/skeleton'
import { Tabs, TabsContent, TabsList, TabsTrigger } from '@/components/ui/tabs'
import { Trash2, Plus } from 'lucide-react'

type EinheitFormData = {
  einheit_kuerzel: string
  bezeichnung: string
  basis_einheit: string
  umrechnungsfaktor: string
  dezimalstellen: string
}

type GruppeFormData = {
  gruppe_nr: string
  bezeichnung: string
  bestand_einheit: string
  ek_einheit: string
  vk_einheit: string
  preis_einheit: string
}

function EinheitenStammTab() {
  const [deletingKeys, setDeletingKeys] = useState<Set<string>>(new Set())
  const { data: einheiten, isLoading, isError } = useMengeneinheiten()
  const createMutation = useCreateMengeneinheit()
  const deleteMutation = useDeleteMengeneinheit()

  const { register, handleSubmit, reset } = useForm<EinheitFormData>({
    defaultValues: {
      einheit_kuerzel: '',
      bezeichnung: '',
      basis_einheit: '',
      umrechnungsfaktor: '',
      dezimalstellen: '3',
    },
  })

  const onSubmit = handleSubmit(async (data) => {
    try {
      await createMutation.mutateAsync({
        einheit_kuerzel: data.einheit_kuerzel,
        bezeichnung: data.bezeichnung,
        basis_einheit: data.basis_einheit || null,
        umrechnungsfaktor: data.umrechnungsfaktor ? parseFloat(data.umrechnungsfaktor) : null,
        dezimalstellen: data.dezimalstellen ? parseInt(data.dezimalstellen, 10) : 3,
      })
      toast.success(`Mengeneinheit ${data.einheit_kuerzel} angelegt`)
      reset()
    } catch {
      toast.error('Fehler beim Anlegen der Mengeneinheit')
    }
  })

  const handleDelete = async (kuerzel: string) => {
    if (deletingKeys.has(kuerzel)) return
    setDeletingKeys((prev) => new Set(prev).add(kuerzel))
    try {
      await deleteMutation.mutateAsync(kuerzel)
      toast.success(`Mengeneinheit ${kuerzel} deaktiviert`)
    } catch {
      toast.error('Fehler beim Deaktivieren')
    } finally {
      setDeletingKeys((prev) => {
        const next = new Set(prev)
        next.delete(kuerzel)
        return next
      })
    }
  }

  return (
    <div className="space-y-6">
      <Card>
        <CardHeader>
          <CardTitle className="text-base">Neue Mengeneinheit</CardTitle>
        </CardHeader>
        <CardContent>
          <form onSubmit={onSubmit} className="grid grid-cols-1 sm:grid-cols-4 gap-4 items-end">
            <div className="space-y-1">
              <Label htmlFor="einheit_kuerzel">Kürzel *</Label>
              <Input
                id="einheit_kuerzel"
                placeholder="z.B. KG"
                {...register('einheit_kuerzel', { required: true })}
              />
            </div>
            <div className="space-y-1 sm:col-span-2">
              <Label htmlFor="einheit_bezeichnung">Bezeichnung *</Label>
              <Input
                id="einheit_bezeichnung"
                placeholder="z.B. Kilogramm"
                {...register('bezeichnung', { required: true })}
              />
            </div>
            <div className="space-y-1">
              <Label htmlFor="dezimalstellen">Dezimalstellen</Label>
              <Input
                id="dezimalstellen"
                type="number"
                min="0"
                max="6"
                placeholder="3"
                {...register('dezimalstellen')}
              />
            </div>
            <div className="space-y-1">
              <Label htmlFor="basis_einheit">Basis-Einheit</Label>
              <Input
                id="basis_einheit"
                placeholder="optional, z.B. KG"
                {...register('basis_einheit')}
              />
            </div>
            <div className="space-y-1">
              <Label htmlFor="umrechnungsfaktor">Umrechnungsfaktor</Label>
              <Input
                id="umrechnungsfaktor"
                type="number"
                step="0.000001"
                min="0"
                placeholder="optional"
                {...register('umrechnungsfaktor')}
              />
            </div>
            <div className="sm:col-span-2 flex justify-end items-end">
              <Button
                type="submit"
                disabled={createMutation.isPending}
                className="gap-2"
                aria-label="Mengeneinheit anlegen"
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
          <CardTitle className="text-base">Mengeneinheiten-Stamm</CardTitle>
        </CardHeader>
        <CardContent>
          {isLoading ? (
            <div className="space-y-2">
              {Array.from({ length: 4 }).map((_, i) => (
                <Skeleton key={i} className="h-10 w-full" />
              ))}
            </div>
          ) : isError ? (
            <p className="text-destructive text-sm py-4">
              Fehler beim Laden der Mengeneinheiten.
            </p>
          ) : (
            <Table>
              <TableHeader>
                <TableRow>
                  <TableHead>Kürzel</TableHead>
                  <TableHead>Bezeichnung</TableHead>
                  <TableHead>Basis-Einheit</TableHead>
                  <TableHead className="text-right">Faktor</TableHead>
                  <TableHead className="text-right">Dez.</TableHead>
                  <TableHead className="w-16" />
                </TableRow>
              </TableHeader>
              <TableBody>
                {einheiten?.length === 0 && (
                  <TableRow>
                    <TableCell colSpan={6} className="text-center text-muted-foreground py-6">
                      Keine Mengeneinheiten vorhanden
                    </TableCell>
                  </TableRow>
                )}
                {einheiten?.map((e) => (
                  <TableRow key={e.id}>
                    <TableCell className="font-mono font-semibold">{e.einheit_kuerzel}</TableCell>
                    <TableCell>{e.bezeichnung}</TableCell>
                    <TableCell className="font-mono">{e.basis_einheit ?? '—'}</TableCell>
                    <TableCell className="text-right tabular-nums">
                      {e.umrechnungsfaktor != null ? e.umrechnungsfaktor : '—'}
                    </TableCell>
                    <TableCell className="text-right tabular-nums">{e.dezimalstellen}</TableCell>
                    <TableCell>
                      <Button
                        variant="ghost"
                        size="sm"
                        disabled={deletingKeys.has(e.einheit_kuerzel)}
                        onClick={() => handleDelete(e.einheit_kuerzel)}
                        aria-label={`Mengeneinheit ${e.einheit_kuerzel} deaktivieren`}
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

function EinheitengruppenTab() {
  const [deletingKeys, setDeletingKeys] = useState<Set<string>>(new Set())
  const { data: gruppen, isLoading, isError } = useMengeneinheitengruppen()
  const createMutation = useCreateMengeneinheitengruppe()
  const deleteMutation = useDeleteMengeneinheitengruppe()

  const { register, handleSubmit, reset } = useForm<GruppeFormData>({
    defaultValues: {
      gruppe_nr: '',
      bezeichnung: '',
      bestand_einheit: '',
      ek_einheit: '',
      vk_einheit: '',
      preis_einheit: '',
    },
  })

  const onSubmit = handleSubmit(async (data) => {
    try {
      await createMutation.mutateAsync({
        gruppe_nr: data.gruppe_nr,
        bezeichnung: data.bezeichnung,
        bestand_einheit: data.bestand_einheit,
        ek_einheit: data.ek_einheit || null,
        vk_einheit: data.vk_einheit || null,
        preis_einheit: data.preis_einheit || null,
      })
      toast.success(`Einheitengruppe ${data.gruppe_nr} angelegt`)
      reset()
    } catch {
      toast.error('Fehler beim Anlegen der Einheitengruppe')
    }
  })

  const handleDelete = async (gruppeNr: string) => {
    if (deletingKeys.has(gruppeNr)) return
    setDeletingKeys((prev) => new Set(prev).add(gruppeNr))
    try {
      await deleteMutation.mutateAsync(gruppeNr)
      toast.success(`Einheitengruppe ${gruppeNr} deaktiviert`)
    } catch {
      toast.error('Fehler beim Deaktivieren')
    } finally {
      setDeletingKeys((prev) => {
        const next = new Set(prev)
        next.delete(gruppeNr)
        return next
      })
    }
  }

  return (
    <div className="space-y-6">
      <Card>
        <CardHeader>
          <CardTitle className="text-base">Neue Einheitengruppe</CardTitle>
        </CardHeader>
        <CardContent>
          <form onSubmit={onSubmit} className="grid grid-cols-1 sm:grid-cols-3 gap-4 items-end">
            <div className="space-y-1">
              <Label htmlFor="gruppe_nr">Gruppen-Nr *</Label>
              <Input
                id="gruppe_nr"
                placeholder="z.B. EG01"
                {...register('gruppe_nr', { required: true })}
              />
            </div>
            <div className="space-y-1 sm:col-span-2">
              <Label htmlFor="gruppe_bezeichnung">Bezeichnung *</Label>
              <Input
                id="gruppe_bezeichnung"
                placeholder="z.B. Getreide Standard"
                {...register('bezeichnung', { required: true })}
              />
            </div>
            <div className="space-y-1">
              <Label htmlFor="bestand_einheit">Bestand-Einheit *</Label>
              <Input
                id="bestand_einheit"
                placeholder="z.B. KG"
                {...register('bestand_einheit', { required: true })}
              />
            </div>
            <div className="space-y-1">
              <Label htmlFor="ek_einheit">EK-Einheit</Label>
              <Input
                id="ek_einheit"
                placeholder="optional"
                {...register('ek_einheit')}
              />
            </div>
            <div className="space-y-1">
              <Label htmlFor="vk_einheit">VK-Einheit</Label>
              <Input
                id="vk_einheit"
                placeholder="optional"
                {...register('vk_einheit')}
              />
            </div>
            <div className="space-y-1">
              <Label htmlFor="preis_einheit">Preis-Einheit</Label>
              <Input
                id="preis_einheit"
                placeholder="optional"
                {...register('preis_einheit')}
              />
            </div>
            <div className="sm:col-span-2 flex justify-end items-end">
              <Button
                type="submit"
                disabled={createMutation.isPending}
                className="gap-2"
                aria-label="Einheitengruppe anlegen"
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
          <CardTitle className="text-base">Einheitengruppen</CardTitle>
        </CardHeader>
        <CardContent>
          {isLoading ? (
            <div className="space-y-2">
              {Array.from({ length: 3 }).map((_, i) => (
                <Skeleton key={i} className="h-10 w-full" />
              ))}
            </div>
          ) : isError ? (
            <p className="text-destructive text-sm py-4">
              Fehler beim Laden der Einheitengruppen.
            </p>
          ) : (
            <Table>
              <TableHeader>
                <TableRow>
                  <TableHead>Gruppen-Nr</TableHead>
                  <TableHead>Bezeichnung</TableHead>
                  <TableHead>Bestand</TableHead>
                  <TableHead>EK</TableHead>
                  <TableHead>VK</TableHead>
                  <TableHead>Preis</TableHead>
                  <TableHead className="w-16" />
                </TableRow>
              </TableHeader>
              <TableBody>
                {gruppen?.length === 0 && (
                  <TableRow>
                    <TableCell colSpan={7} className="text-center text-muted-foreground py-6">
                      Keine Einheitengruppen vorhanden
                    </TableCell>
                  </TableRow>
                )}
                {gruppen?.map((g) => (
                  <TableRow key={g.id}>
                    <TableCell className="font-mono font-semibold">{g.gruppe_nr}</TableCell>
                    <TableCell>{g.bezeichnung}</TableCell>
                    <TableCell className="font-mono">{g.bestand_einheit}</TableCell>
                    <TableCell className="font-mono">{g.ek_einheit ?? '—'}</TableCell>
                    <TableCell className="font-mono">{g.vk_einheit ?? '—'}</TableCell>
                    <TableCell className="font-mono">{g.preis_einheit ?? '—'}</TableCell>
                    <TableCell>
                      <Button
                        variant="ghost"
                        size="sm"
                        disabled={deletingKeys.has(g.gruppe_nr)}
                        onClick={() => handleDelete(g.gruppe_nr)}
                        aria-label={`Einheitengruppe ${g.gruppe_nr} deaktivieren`}
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

export default function MengeneinheitenPage() {
  return (
    <div className="p-6 space-y-4">
      <div>
        <h1 className="text-2xl font-semibold">Mengeneinheiten &amp; Gruppen</h1>
        <p className="text-muted-foreground text-sm mt-1">
          Stammdaten für Mengeneinheiten mit Umrechnungsfaktoren sowie Einheitengruppen
          für Bestand, Ein- und Verkauf und Preisberechnung.
        </p>
      </div>
      <Tabs defaultValue="stamm">
        <TabsList>
          <TabsTrigger value="stamm">Einheiten-Stamm</TabsTrigger>
          <TabsTrigger value="gruppen">Einheitengruppen</TabsTrigger>
        </TabsList>
        <TabsContent value="stamm" className="mt-4">
          <EinheitenStammTab />
        </TabsContent>
        <TabsContent value="gruppen" className="mt-4">
          <EinheitengruppenTab />
        </TabsContent>
      </Tabs>
    </div>
  )
}
