import { useState } from 'react'
import { useForm } from 'react-hook-form'
import { toast } from 'sonner'
import {
  useGeschaeftsjahre,
  useCreateGeschaeftsjahr,
  useDeleteGeschaeftsjahr,
  useFibuPerioden,
  type GeschaeftsjahreCreate,
  type GeschaeftsjahreStatus,
} from '@/lib/api/fibuGeschaeftsjahre'
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
import { Tabs, TabsContent, TabsList, TabsTrigger } from '@/components/ui/tabs'
import {
  Select,
  SelectContent,
  SelectItem,
  SelectTrigger,
  SelectValue,
} from '@/components/ui/select'
import { Trash2, Plus } from 'lucide-react'

type GJFormData = {
  jahr_nr: string
  bezeichnung: string
  datum_beginn: string
  datum_ende: string
  anzahl_perioden_ware: string
  anzahl_perioden_fibu: string
  journal_nummernkreis: string
}

function StatusBadge({ status }: { status: GeschaeftsjahreStatus }) {
  const variants: Record<GeschaeftsjahreStatus, 'default' | 'secondary' | 'outline'> = {
    offen: 'default',
    gesperrt: 'secondary',
    abgeschlossen: 'outline',
  }
  return <Badge variant={variants[status]}>{status}</Badge>
}

// ── Geschäftsjahre-Tab ────────────────────────────────────────────────────────

function GeschaeftsjahreTab() {
  const { data: jahre, isLoading, isError } = useGeschaeftsjahre()
  const createMutation = useCreateGeschaeftsjahr()
  const deleteMutation = useDeleteGeschaeftsjahr()
  const [deletingKey, setDeletingKey] = useState<number | null>(null)

  const { register, handleSubmit, reset, formState: { isSubmitting } } =
    useForm<GJFormData>({
      defaultValues: {
        jahr_nr: '',
        bezeichnung: '',
        datum_beginn: '',
        datum_ende: '',
        anzahl_perioden_ware: '12',
        anzahl_perioden_fibu: '12',
        journal_nummernkreis: '',
      },
    })

  const onSubmit = async (data: GJFormData) => {
    try {
      const payload: GeschaeftsjahreCreate = {
        jahr_nr: parseInt(data.jahr_nr, 10),
        bezeichnung: data.bezeichnung,
        datum_beginn: data.datum_beginn,
        datum_ende: data.datum_ende,
        anzahl_perioden_ware: parseInt(data.anzahl_perioden_ware, 10),
        anzahl_perioden_fibu: parseInt(data.anzahl_perioden_fibu, 10),
        journal_nummernkreis: data.journal_nummernkreis || null,
      }
      await createMutation.mutateAsync(payload)
      toast.success(`Geschäftsjahr ${data.jahr_nr} angelegt.`)
      reset()
    } catch {
      toast.error('Fehler beim Anlegen des Geschäftsjahres.')
    }
  }

  const handleDelete = async (jahr_nr: number) => {
    if (deletingKey === jahr_nr) return
    setDeletingKey(jahr_nr)
    try {
      await deleteMutation.mutateAsync(jahr_nr)
      toast.success(`Geschäftsjahr ${jahr_nr} gesperrt.`)
    } catch {
      toast.error('Fehler beim Sperren des Geschäftsjahres.')
    } finally {
      setDeletingKey(null)
    }
  }

  return (
    <div className="space-y-4">
      <Card>
        <CardHeader>
          <CardTitle>Neues Geschäftsjahr [JAHR]</CardTitle>
        </CardHeader>
        <CardContent>
          <form onSubmit={handleSubmit(onSubmit)} noValidate className="grid grid-cols-1 gap-3 sm:grid-cols-3">
            <div>
              <Label htmlFor="gj_jahr_nr">Jahr-Nr.</Label>
              <Input
                id="gj_jahr_nr"
                type="number"
                placeholder="z. B. 2025"
                {...register('jahr_nr', { required: true })}
              />
            </div>
            <div className="sm:col-span-2">
              <Label htmlFor="gj_bezeichnung">Bezeichnung</Label>
              <Input
                id="gj_bezeichnung"
                placeholder="z. B. Geschäftsjahr 2025"
                {...register('bezeichnung', { required: true })}
              />
            </div>
            <div>
              <Label htmlFor="gj_datum_beginn">Beginn</Label>
              <Input
                id="gj_datum_beginn"
                type="date"
                {...register('datum_beginn', { required: true })}
              />
            </div>
            <div>
              <Label htmlFor="gj_datum_ende">Ende</Label>
              <Input
                id="gj_datum_ende"
                type="date"
                {...register('datum_ende', { required: true })}
              />
            </div>
            <div>
              <Label htmlFor="gj_journal_nummernkreis">Journal-Nummernkreis (optional)</Label>
              <Input
                id="gj_journal_nummernkreis"
                placeholder="z. B. JNK-2025"
                {...register('journal_nummernkreis')}
              />
            </div>
            <div>
              <Label htmlFor="gj_perioden_ware">Perioden Ware</Label>
              <Input
                id="gj_perioden_ware"
                type="number"
                min={1}
                max={52}
                {...register('anzahl_perioden_ware', { required: true })}
              />
            </div>
            <div>
              <Label htmlFor="gj_perioden_fibu">Perioden FiBu</Label>
              <Input
                id="gj_perioden_fibu"
                type="number"
                min={1}
                max={52}
                {...register('anzahl_perioden_fibu', { required: true })}
              />
            </div>
            <div className="sm:col-span-3 flex justify-end">
              <Button type="submit" disabled={isSubmitting} aria-label="Geschäftsjahr anlegen">
                <Plus className="mr-1 h-4 w-4" aria-hidden="true" />
                Anlegen
              </Button>
            </div>
          </form>
        </CardContent>
      </Card>

      <Card>
        <CardHeader>
          <CardTitle>Geschäftsjahre</CardTitle>
        </CardHeader>
        <CardContent>
          {isLoading && (
            <div className="space-y-2">
              {[0, 1, 2].map((i) => <Skeleton key={i} className="h-9 w-full" />)}
            </div>
          )}
          {isError && (
            <p className="text-sm text-destructive">Fehler beim Laden der Geschäftsjahre.</p>
          )}
          {!isLoading && !isError && (!jahre || jahre.length === 0) && (
            <p className="text-sm text-muted-foreground">Keine Geschäftsjahre vorhanden.</p>
          )}
          {jahre && jahre.length > 0 && (
            <Table>
              <TableHeader>
                <TableRow>
                  <TableHead>Jahr-Nr.</TableHead>
                  <TableHead>Bezeichnung</TableHead>
                  <TableHead>Beginn</TableHead>
                  <TableHead>Ende</TableHead>
                  <TableHead>Perioden W/F</TableHead>
                  <TableHead>Status</TableHead>
                  <TableHead aria-label="Aktionen" />
                </TableRow>
              </TableHeader>
              <TableBody>
                {jahre.map((j) => (
                  <TableRow key={j.id}>
                    <TableCell className="font-mono text-sm">{j.jahr_nr}</TableCell>
                    <TableCell>{j.bezeichnung}</TableCell>
                    <TableCell className="text-sm">{j.datum_beginn}</TableCell>
                    <TableCell className="text-sm">{j.datum_ende}</TableCell>
                    <TableCell className="text-sm">{j.anzahl_perioden_ware}/{j.anzahl_perioden_fibu}</TableCell>
                    <TableCell><StatusBadge status={j.status} /></TableCell>
                    <TableCell className="text-right">
                      <Button
                        variant="ghost"
                        size="icon"
                        disabled={deletingKey === j.jahr_nr}
                        onClick={() => handleDelete(j.jahr_nr)}
                        aria-label={`Geschäftsjahr ${j.jahr_nr} sperren`}
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

// ── Perioden-Tab ──────────────────────────────────────────────────────────────

function PeriodenTab() {
  const { data: jahre } = useGeschaeftsjahre()
  const [selectedJahrNr, setSelectedJahrNr] = useState<number | null>(null)
  const { data: perioden, isLoading, isError } = useFibuPerioden(selectedJahrNr)

  return (
    <div className="space-y-4">
      <Card>
        <CardHeader>
          <CardTitle>Perioden eines Geschäftsjahres</CardTitle>
        </CardHeader>
        <CardContent className="space-y-3">
          <div>
            <Label htmlFor="perioden_jahr_select">Geschäftsjahr wählen</Label>
            <Select
              value={selectedJahrNr !== null ? String(selectedJahrNr) : ''}
              onValueChange={(v) => setSelectedJahrNr(v ? parseInt(v, 10) : null)}
            >
              <SelectTrigger id="perioden_jahr_select" aria-label="Geschäftsjahr für Perioden auswählen">
                <SelectValue placeholder="— Jahr wählen —" />
              </SelectTrigger>
              <SelectContent>
                {(jahre ?? []).map((j) => (
                  <SelectItem key={j.id} value={String(j.jahr_nr)}>
                    {j.jahr_nr} — {j.bezeichnung}
                  </SelectItem>
                ))}
              </SelectContent>
            </Select>
          </div>

          {selectedJahrNr === null && (
            <p className="text-sm text-muted-foreground">Bitte ein Geschäftsjahr auswählen.</p>
          )}
          {selectedJahrNr !== null && isLoading && (
            <div className="space-y-2">
              {[0, 1, 2].map((i) => <Skeleton key={i} className="h-9 w-full" />)}
            </div>
          )}
          {selectedJahrNr !== null && isError && (
            <p className="text-sm text-destructive">Fehler beim Laden der Perioden.</p>
          )}
          {selectedJahrNr !== null && !isLoading && !isError && (!perioden || perioden.length === 0) && (
            <p className="text-sm text-muted-foreground">Keine Perioden vorhanden.</p>
          )}
          {perioden && perioden.length > 0 && (
            <Table>
              <TableHeader>
                <TableRow>
                  <TableHead>Periode-Nr.</TableHead>
                  <TableHead>Bezeichnung</TableHead>
                  <TableHead>Von</TableHead>
                  <TableHead>Bis</TableHead>
                  <TableHead>Typ</TableHead>
                  <TableHead>Gesperrt</TableHead>
                </TableRow>
              </TableHeader>
              <TableBody>
                {perioden.map((p) => (
                  <TableRow key={p.id}>
                    <TableCell className="font-mono text-sm">{p.periode_nr}</TableCell>
                    <TableCell>{p.bezeichnung}</TableCell>
                    <TableCell className="text-sm">{p.datum_von}</TableCell>
                    <TableCell className="text-sm">{p.datum_bis}</TableCell>
                    <TableCell className="text-sm">{p.typ}</TableCell>
                    <TableCell>
                      <Badge variant={p.gesperrt ? 'secondary' : 'outline'}>
                        {p.gesperrt ? 'gesperrt' : 'offen'}
                      </Badge>
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

export default function GeschaeftsjahreePage() {
  return (
    <div className="p-6 space-y-4">
      <div>
        <h1 className="text-2xl font-semibold">Geschäftsjahre [JAHR]</h1>
        <p className="text-sm text-muted-foreground mt-1">
          FiBu-Stammdaten — Geschäftsjahre mit Perioden für Ware und FiBu.
        </p>
      </div>

      <Tabs defaultValue="jahre">
        <TabsList>
          <TabsTrigger value="jahre">Geschäftsjahre [JAHR]</TabsTrigger>
          <TabsTrigger value="perioden">Perioden</TabsTrigger>
        </TabsList>

        <TabsContent value="jahre" className="mt-4">
          <GeschaeftsjahreTab />
        </TabsContent>

        <TabsContent value="perioden" className="mt-4">
          <PeriodenTab />
        </TabsContent>
      </Tabs>
    </div>
  )
}
