import { useState } from 'react'
import { useForm } from 'react-hook-form'
import { toast } from 'sonner'
import {
  useRezepturgruppen,
  useCreateRezepturgruppe,
  useDeleteRezepturgruppe,
  type RezepturGruppeCreate,
} from '@/lib/api/rezepturgruppen'
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
import { Trash2, Plus } from 'lucide-react'

export default function RezepturGruppenPage() {
  const { data: gruppen = [], isLoading, isError } = useRezepturgruppen()
  const createMutation = useCreateRezepturgruppe()
  const deleteMutation = useDeleteRezepturgruppe()
  const [pendingDeletes, setPendingDeletes] = useState<Set<string>>(new Set())

  const { register, handleSubmit, reset, formState: { isSubmitting } } = useForm<RezepturGruppeCreate>({
    defaultValues: { gruppe_nr: '', bezeichnung: '', tierart: '', nutzungsrichtung: '' },
  })

  async function onSubmit(data: RezepturGruppeCreate) {
    try {
      await createMutation.mutateAsync({
        gruppe_nr: data.gruppe_nr.trim(),
        bezeichnung: data.bezeichnung.trim(),
        tierart: data.tierart?.trim() || null,
        nutzungsrichtung: data.nutzungsrichtung?.trim() || null,
      })
      toast.success('Rezepturgruppe angelegt')
      reset()
    } catch {
      toast.error('Fehler beim Anlegen der Rezepturgruppe')
    }
  }

  async function handleDelete(gruppe_nr: string) {
    if (pendingDeletes.has(gruppe_nr)) return
    setPendingDeletes((prev) => new Set(prev).add(gruppe_nr))
    try {
      await deleteMutation.mutateAsync(gruppe_nr)
      toast.success('Rezepturgruppe gelöscht')
    } catch {
      toast.error('Fehler beim Löschen der Rezepturgruppe')
    } finally {
      setPendingDeletes((prev) => {
        const next = new Set(prev)
        next.delete(gruppe_nr)
        return next
      })
    }
  }

  return (
    <div className="p-6 space-y-6 max-w-5xl mx-auto">
      <h1 className="text-2xl font-semibold">Rezepturgruppen [REZG]</h1>

      {/* Anlegen-Formular */}
      <Card>
        <CardHeader>
          <CardTitle>Neue Rezepturgruppe anlegen</CardTitle>
        </CardHeader>
        <CardContent>
          <form onSubmit={handleSubmit(onSubmit)} className="grid grid-cols-2 gap-4">
            <div className="space-y-1">
              <Label htmlFor="gruppe_nr">Gruppen-Nr *</Label>
              <Input
                id="gruppe_nr"
                {...register('gruppe_nr', { required: true })}
                placeholder="z.B. RIND-MILCH"
              />
            </div>
            <div className="space-y-1">
              <Label htmlFor="bezeichnung">Bezeichnung *</Label>
              <Input
                id="bezeichnung"
                {...register('bezeichnung', { required: true })}
                placeholder="z.B. Rind Milchleistung"
              />
            </div>
            <div className="space-y-1">
              <Label htmlFor="tierart">Tierart</Label>
              <Input
                id="tierart"
                {...register('tierart')}
                placeholder="z.B. Rind, Schwein, Geflügel"
              />
            </div>
            <div className="space-y-1">
              <Label htmlFor="nutzungsrichtung">Nutzungsrichtung</Label>
              <Input
                id="nutzungsrichtung"
                {...register('nutzungsrichtung')}
                placeholder="z.B. Milch, Mast, Aufzucht"
              />
            </div>
            <div className="col-span-2 flex justify-end">
              <Button type="submit" disabled={isSubmitting} className="gap-2">
                <Plus className="h-4 w-4" aria-hidden="true" />
                Anlegen
              </Button>
            </div>
          </form>
        </CardContent>
      </Card>

      {/* Liste */}
      <Card>
        <CardHeader>
          <CardTitle>Vorhandene Rezepturgruppen</CardTitle>
        </CardHeader>
        <CardContent>
          {isLoading ? (
            <div className="space-y-2">
              {[1, 2, 3].map((i) => (
                <Skeleton key={i} className="h-10 w-full" />
              ))}
            </div>
          ) : isError ? (
            <p className="text-destructive text-sm">Fehler beim Laden der Rezepturgruppen.</p>
          ) : gruppen.length === 0 ? (
            <p className="text-muted-foreground text-sm">Noch keine Rezepturgruppen vorhanden.</p>
          ) : (
            <Table>
              <TableHeader>
                <TableRow>
                  <TableHead>Gruppen-Nr</TableHead>
                  <TableHead>Bezeichnung</TableHead>
                  <TableHead>Tierart</TableHead>
                  <TableHead>Nutzungsrichtung</TableHead>
                  <TableHead className="w-12"></TableHead>
                </TableRow>
              </TableHeader>
              <TableBody>
                {gruppen.map((g) => (
                  <TableRow key={g.id}>
                    <TableCell className="font-mono font-medium">{g.gruppe_nr}</TableCell>
                    <TableCell>{g.bezeichnung}</TableCell>
                    <TableCell>{g.tierart ?? '—'}</TableCell>
                    <TableCell>{g.nutzungsrichtung ?? '—'}</TableCell>
                    <TableCell>
                      <Button
                        variant="ghost"
                        size="icon"
                        aria-label={`Rezepturgruppe ${g.gruppe_nr} löschen`}
                        disabled={pendingDeletes.has(g.gruppe_nr)}
                        onClick={() => handleDelete(g.gruppe_nr)}
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
