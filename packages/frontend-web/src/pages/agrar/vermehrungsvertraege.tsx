import { useState } from 'react'
import { useForm } from 'react-hook-form'
import { toast } from 'sonner'
import {
  useVermehrungsvertraege,
  useCreateVermehrungsvertrag,
  useDeleteVermehrungsvertrag,
  type VermehrungsvertragStatus,
  type Kategorie,
} from '@/lib/api/vermehrungsvertraege'
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
import { Trash2, Plus } from 'lucide-react'

const STATUS_VARIANT: Record<VermehrungsvertragStatus, 'default' | 'secondary' | 'destructive' | 'outline'> = {
  angelegt: 'outline',
  aktiv: 'default',
  beendet: 'secondary',
  storniert: 'destructive',
}

type FormData = {
  vertrag_nr: string
  erntejahr: string
  vermehrer_kunden_nr: string
  sorte_nr: string
  sorte_bezeichnung: string
  kategorie: string
  vertrags_menge_t: string
  anbauflaeche_ha: string
  lwk_anerkennungsstelle: string
  vmkz: string
  bemerkung: string
}

export default function VermehrungsvertraegePage() {
  const { data: vertraege, isLoading, isError } = useVermehrungsvertraege()
  const createMutation = useCreateVermehrungsvertrag()
  const deleteMutation = useDeleteVermehrungsvertrag()
  const [deletingKey, setDeletingKey] = useState<string | null>(null)

  const { register, handleSubmit, reset, setValue, watch, formState: { isSubmitting } } =
    useForm<FormData>({
      defaultValues: {
        vertrag_nr: '',
        erntejahr: String(new Date().getFullYear()),
        vermehrer_kunden_nr: '',
        sorte_nr: '',
        sorte_bezeichnung: '',
        kategorie: '',
        vertrags_menge_t: '',
        anbauflaeche_ha: '',
        lwk_anerkennungsstelle: '',
        vmkz: '',
        bemerkung: '',
      },
    })

  const kategorieValue = watch('kategorie')

  const onSubmit = async (data: FormData) => {
    try {
      await createMutation.mutateAsync({
        vertrag_nr: data.vertrag_nr,
        erntejahr: parseInt(data.erntejahr, 10) || new Date().getFullYear(),
        vermehrer_kunden_nr: data.vermehrer_kunden_nr,
        sorte_nr: data.sorte_nr || null,
        sorte_bezeichnung: data.sorte_bezeichnung || null,
        kategorie: (data.kategorie && data.kategorie !== '__none__' ? data.kategorie as Kategorie : null),
        vertrags_menge_t: data.vertrags_menge_t ? parseFloat(data.vertrags_menge_t) : null,
        anbauflaeche_ha: data.anbauflaeche_ha ? parseFloat(data.anbauflaeche_ha) : null,
        lwk_anerkennungsstelle: data.lwk_anerkennungsstelle || null,
        vmkz: data.vmkz || null,
        bemerkung: data.bemerkung || null,
      })
      toast.success(`Vermehrungsvertrag ${data.vertrag_nr} angelegt.`)
      reset()
    } catch {
      toast.error('Fehler beim Anlegen des Vermehrungsvertrags.')
    }
  }

  const handleDelete = async (id: string, vertrag_nr: string) => {
    if (deletingKey === id) return
    setDeletingKey(id)
    try {
      await deleteMutation.mutateAsync(id)
      toast.success(`Vermehrungsvertrag ${vertrag_nr} storniert.`)
    } catch {
      toast.error('Fehler beim Stornieren des Vermehrungsvertrags.')
    } finally {
      setDeletingKey(null)
    }
  }

  return (
    <div className="p-6 space-y-4">
      <div>
        <h1 className="text-2xl font-semibold">Vermehrungsverträge [VV]</h1>
        <p className="text-sm text-muted-foreground mt-1">
          Saatzucht — Vermehrungsverträge verwalten
        </p>
      </div>

      <Card>
        <CardHeader>
          <CardTitle>Neuen Vermehrungsvertrag anlegen</CardTitle>
        </CardHeader>
        <CardContent>
          <form onSubmit={handleSubmit(onSubmit)} noValidate className="grid grid-cols-1 gap-3 sm:grid-cols-3">
            <div>
              <Label htmlFor="vv_vertrag_nr">Vertrag-Nr. *</Label>
              <Input id="vv_vertrag_nr" placeholder="z. B. VV-2026-001" {...register('vertrag_nr', { required: true })} />
            </div>
            <div>
              <Label htmlFor="vv_erntejahr">Erntejahr *</Label>
              <Input id="vv_erntejahr" type="number" {...register('erntejahr', { required: true })} />
            </div>
            <div>
              <Label htmlFor="vv_vermehrer">Vermehrer Kunden-Nr. *</Label>
              <Input id="vv_vermehrer" placeholder="z. B. KD-200" {...register('vermehrer_kunden_nr', { required: true })} />
            </div>
            <div>
              <Label htmlFor="vv_sorte_nr">Sorten-Nr.</Label>
              <Input id="vv_sorte_nr" {...register('sorte_nr')} />
            </div>
            <div className="sm:col-span-2">
              <Label htmlFor="vv_sorte_bez">Sortenbezeichnung</Label>
              <Input id="vv_sorte_bez" placeholder="z. B. Leibniz GW 2300" {...register('sorte_bezeichnung')} />
            </div>
            <div>
              <Label htmlFor="vv_kategorie">Kategorie</Label>
              <Select value={kategorieValue} onValueChange={(v) => setValue('kategorie', v)}>
                <SelectTrigger id="vv_kategorie" aria-label="Kategorie">
                  <SelectValue placeholder="— optional —" />
                </SelectTrigger>
                <SelectContent>
                  <SelectItem value="__none__">— keine —</SelectItem>
                  <SelectItem value="Z1">Z1</SelectItem>
                  <SelectItem value="Z2">Z2</SelectItem>
                  <SelectItem value="SE">SE</SelectItem>
                  <SelectItem value="E">E</SelectItem>
                  <SelectItem value="B">B</SelectItem>
                </SelectContent>
              </Select>
            </div>
            <div>
              <Label htmlFor="vv_menge">Vertrags-Menge (t)</Label>
              <Input id="vv_menge" type="number" step="0.001" {...register('vertrags_menge_t')} />
            </div>
            <div>
              <Label htmlFor="vv_flaeche">Anbaufläche (ha)</Label>
              <Input id="vv_flaeche" type="number" step="0.01" {...register('anbauflaeche_ha')} />
            </div>
            <div>
              <Label htmlFor="vv_lwk">LWK Anerkennungsstelle</Label>
              <Input id="vv_lwk" {...register('lwk_anerkennungsstelle')} />
            </div>
            <div>
              <Label htmlFor="vv_vmkz">VMKZ</Label>
              <Input id="vv_vmkz" {...register('vmkz')} />
            </div>
            <div>
              <Label htmlFor="vv_bemerkung">Bemerkung</Label>
              <Input id="vv_bemerkung" {...register('bemerkung')} />
            </div>
            <div className="sm:col-span-3 flex justify-end">
              <Button type="submit" disabled={isSubmitting} aria-label="Vermehrungsvertrag anlegen">
                <Plus className="mr-1 h-4 w-4" aria-hidden="true" />
                Anlegen
              </Button>
            </div>
          </form>
        </CardContent>
      </Card>

      <Card>
        <CardHeader><CardTitle>Vermehrungsverträge</CardTitle></CardHeader>
        <CardContent>
          {isLoading && (
            <div className="space-y-2">{[0, 1, 2].map((i) => <Skeleton key={i} className="h-9 w-full" />)}</div>
          )}
          {isError && <p className="text-sm text-destructive">Fehler beim Laden der Vermehrungsverträge.</p>}
          {!isLoading && !isError && (!vertraege || vertraege.length === 0) && (
            <p className="text-sm text-muted-foreground">Keine Vermehrungsverträge vorhanden.</p>
          )}
          {vertraege && vertraege.length > 0 && (
            <Table>
              <TableHeader>
                <TableRow>
                  <TableHead>Vertrag-Nr.</TableHead>
                  <TableHead>Erntejahr</TableHead>
                  <TableHead>Vermehrer</TableHead>
                  <TableHead>Sorte</TableHead>
                  <TableHead>Kat.</TableHead>
                  <TableHead className="text-right">Menge t</TableHead>
                  <TableHead className="text-right">Fläche ha</TableHead>
                  <TableHead>Status</TableHead>
                  <TableHead aria-label="Aktionen" />
                </TableRow>
              </TableHeader>
              <TableBody>
                {vertraege.map((vv) => (
                  <TableRow key={vv.id}>
                    <TableCell className="font-mono text-sm">{vv.vertrag_nr}</TableCell>
                    <TableCell>{vv.erntejahr}</TableCell>
                    <TableCell>{vv.vermehrer_kunden_nr}</TableCell>
                    <TableCell>{vv.sorte_bezeichnung ?? vv.sorte_nr ?? '—'}</TableCell>
                    <TableCell>{vv.kategorie ?? '—'}</TableCell>
                    <TableCell className="text-right font-mono text-sm">
                      {vv.vertrags_menge_t != null ? Number(vv.vertrags_menge_t).toFixed(3) : '—'}
                    </TableCell>
                    <TableCell className="text-right font-mono text-sm">
                      {vv.anbauflaeche_ha != null ? Number(vv.anbauflaeche_ha).toFixed(2) : '—'}
                    </TableCell>
                    <TableCell>
                      <Badge variant={STATUS_VARIANT[vv.status]}>
                        {vv.status.charAt(0).toUpperCase() + vv.status.slice(1)}
                      </Badge>
                    </TableCell>
                    <TableCell className="text-right">
                      <Button
                        variant="ghost"
                        size="icon"
                        disabled={deletingKey === vv.id || vv.status === 'storniert'}
                        onClick={() => handleDelete(vv.id, vv.vertrag_nr)}
                        aria-label={`Vermehrungsvertrag ${vv.vertrag_nr} stornieren`}
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
