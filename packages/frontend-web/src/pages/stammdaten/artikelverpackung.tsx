import { useState } from 'react'
import { useForm } from 'react-hook-form'
import { toast } from 'sonner'
import {
  useArtikelVerpackungen,
  useCreateArtikelVerpackung,
  useDeleteArtikelVerpackung,
} from '@/lib/api/artikelverpackung'
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

type FormData = {
  verpackungs_nr: string
  bezeichnung: string
  stufen: string
  stufe1_bezeichnung: string
  stufe1_menge: string
  stufe1_einheit: string
  stufe1_gewicht_kg: string
  stufe2_bezeichnung: string
  stufe2_menge: string
  stufe2_einheit: string
  stufe2_gewicht_kg: string
  stufe3_bezeichnung: string
  stufe3_menge: string
  stufe3_einheit: string
  stufe3_gewicht_kg: string
}

export default function ArtikelverpackungPage() {
  const { data: verpackungen, isLoading, isError } = useArtikelVerpackungen()
  const createMutation = useCreateArtikelVerpackung()
  const deleteMutation = useDeleteArtikelVerpackung()
  const [deletingKey, setDeletingKey] = useState<string | null>(null)

  const { register, handleSubmit, reset, setValue, watch, formState: { isSubmitting } } =
    useForm<FormData>({
      defaultValues: {
        verpackungs_nr: '',
        bezeichnung: '',
        stufen: '1',
        stufe1_bezeichnung: '',
        stufe1_menge: '',
        stufe1_einheit: '',
        stufe1_gewicht_kg: '',
        stufe2_bezeichnung: '',
        stufe2_menge: '',
        stufe2_einheit: '',
        stufe2_gewicht_kg: '',
        stufe3_bezeichnung: '',
        stufe3_menge: '',
        stufe3_einheit: '',
        stufe3_gewicht_kg: '',
      },
    })

  const stufenValue = watch('stufen')
  const stufenNum = parseInt(stufenValue, 10) || 1

  const onSubmit = async (data: FormData) => {
    const stufen = parseInt(data.stufen, 10) || 1
    try {
      await createMutation.mutateAsync({
        verpackungs_nr: data.verpackungs_nr,
        bezeichnung: data.bezeichnung,
        stufen,
        stufe1_bezeichnung: data.stufe1_bezeichnung || null,
        stufe1_menge: data.stufe1_menge ? parseFloat(data.stufe1_menge) : null,
        stufe1_einheit: data.stufe1_einheit || null,
        stufe1_gewicht_kg: data.stufe1_gewicht_kg ? parseFloat(data.stufe1_gewicht_kg) : null,
        ...(stufen >= 2 ? {
          stufe2_bezeichnung: data.stufe2_bezeichnung || null,
          stufe2_menge: data.stufe2_menge ? parseFloat(data.stufe2_menge) : null,
          stufe2_einheit: data.stufe2_einheit || null,
          stufe2_gewicht_kg: data.stufe2_gewicht_kg ? parseFloat(data.stufe2_gewicht_kg) : null,
        } : {}),
        ...(stufen >= 3 ? {
          stufe3_bezeichnung: data.stufe3_bezeichnung || null,
          stufe3_menge: data.stufe3_menge ? parseFloat(data.stufe3_menge) : null,
          stufe3_einheit: data.stufe3_einheit || null,
          stufe3_gewicht_kg: data.stufe3_gewicht_kg ? parseFloat(data.stufe3_gewicht_kg) : null,
        } : {}),
      })
      toast.success(`Verpackung ${data.verpackungs_nr} angelegt.`)
      reset()
    } catch {
      toast.error('Fehler beim Anlegen der Verpackung.')
    }
  }

  const handleDelete = async (verpackungs_nr: string) => {
    if (deletingKey === verpackungs_nr) return
    setDeletingKey(verpackungs_nr)
    try {
      await deleteMutation.mutateAsync(verpackungs_nr)
      toast.success(`Verpackung ${verpackungs_nr} deaktiviert.`)
    } catch {
      toast.error('Fehler beim Deaktivieren der Verpackung.')
    } finally {
      setDeletingKey(null)
    }
  }

  return (
    <div className="p-6 space-y-4">
      <div>
        <h1 className="text-2xl font-semibold">Artikelverpackung</h1>
        <p className="text-sm text-muted-foreground mt-1">
          Verpackungsdefinitionen mit bis zu 3 Stufen (z. B. Palette → Karton → Stück)
        </p>
      </div>

      <Card>
        <CardHeader>
          <CardTitle>Neue Verpackung anlegen</CardTitle>
        </CardHeader>
        <CardContent>
          <form onSubmit={handleSubmit(onSubmit)} noValidate className="space-y-4">
            <div className="grid grid-cols-1 gap-3 sm:grid-cols-3">
              <div>
                <Label htmlFor="av_nr">Verpackungs-Nr. *</Label>
                <Input id="av_nr" placeholder="z. B. VPK-001" {...register('verpackungs_nr', { required: true })} />
              </div>
              <div>
                <Label htmlFor="av_bez">Bezeichnung *</Label>
                <Input id="av_bez" placeholder="z. B. Palette Weizensäcke" {...register('bezeichnung', { required: true })} />
              </div>
              <div>
                <Label htmlFor="av_stufen">Anzahl Stufen</Label>
                <Select value={stufenValue} onValueChange={(v) => setValue('stufen', v)}>
                  <SelectTrigger id="av_stufen" aria-label="Anzahl Stufen">
                    <SelectValue />
                  </SelectTrigger>
                  <SelectContent>
                    <SelectItem value="1">1 Stufe</SelectItem>
                    <SelectItem value="2">2 Stufen</SelectItem>
                    <SelectItem value="3">3 Stufen</SelectItem>
                  </SelectContent>
                </Select>
              </div>
            </div>

            {[1, 2, 3].filter((s) => s <= stufenNum).map((stufe) => (
              <div key={stufe} className="border rounded-md p-3 space-y-2">
                <p className="text-sm font-medium text-muted-foreground">Stufe {stufe}</p>
                <div className="grid grid-cols-1 gap-3 sm:grid-cols-4">
                  <div>
                    <Label htmlFor={`av_s${stufe}_bez`}>Bezeichnung</Label>
                    <Input
                      id={`av_s${stufe}_bez`}
                      placeholder={stufe === 1 ? 'Palette' : stufe === 2 ? 'Sack' : 'Stück'}
                      {...register(`stufe${stufe}_bezeichnung` as keyof FormData)}
                    />
                  </div>
                  <div>
                    <Label htmlFor={`av_s${stufe}_menge`}>Menge</Label>
                    <Input
                      id={`av_s${stufe}_menge`}
                      type="number"
                      step="0.001"
                      {...register(`stufe${stufe}_menge` as keyof FormData)}
                    />
                  </div>
                  <div>
                    <Label htmlFor={`av_s${stufe}_einheit`}>Einheit</Label>
                    <Input
                      id={`av_s${stufe}_einheit`}
                      placeholder="z. B. Stk"
                      {...register(`stufe${stufe}_einheit` as keyof FormData)}
                    />
                  </div>
                  <div>
                    <Label htmlFor={`av_s${stufe}_gewicht`}>Gewicht (kg)</Label>
                    <Input
                      id={`av_s${stufe}_gewicht`}
                      type="number"
                      step="0.001"
                      {...register(`stufe${stufe}_gewicht_kg` as keyof FormData)}
                    />
                  </div>
                </div>
              </div>
            ))}

            <div className="flex justify-end">
              <Button type="submit" disabled={isSubmitting} aria-label="Verpackung anlegen">
                <Plus className="mr-1 h-4 w-4" aria-hidden="true" />
                Anlegen
              </Button>
            </div>
          </form>
        </CardContent>
      </Card>

      <Card>
        <CardHeader><CardTitle>Verpackungen</CardTitle></CardHeader>
        <CardContent>
          {isLoading && (
            <div className="space-y-2">{[0, 1, 2].map((i) => <Skeleton key={i} className="h-9 w-full" />)}</div>
          )}
          {isError && <p className="text-sm text-destructive">Fehler beim Laden der Verpackungen.</p>}
          {!isLoading && !isError && (!verpackungen || verpackungen.length === 0) && (
            <p className="text-sm text-muted-foreground">Keine Verpackungen vorhanden.</p>
          )}
          {verpackungen && verpackungen.length > 0 && (
            <Table>
              <TableHeader>
                <TableRow>
                  <TableHead>Verpackungs-Nr.</TableHead>
                  <TableHead>Bezeichnung</TableHead>
                  <TableHead>Stufen</TableHead>
                  <TableHead>Stufe 1</TableHead>
                  <TableHead>Stufe 2</TableHead>
                  <TableHead>Stufe 3</TableHead>
                  <TableHead>Status</TableHead>
                  <TableHead aria-label="Aktionen" />
                </TableRow>
              </TableHeader>
              <TableBody>
                {verpackungen.map((vp) => (
                  <TableRow key={vp.id}>
                    <TableCell className="font-mono text-sm">{vp.verpackungs_nr}</TableCell>
                    <TableCell>{vp.bezeichnung}</TableCell>
                    <TableCell>{vp.stufen}</TableCell>
                    <TableCell className="text-sm">
                      {vp.stufe1_bezeichnung
                        ? `${vp.stufe1_bezeichnung}${vp.stufe1_menge ? ` × ${vp.stufe1_menge}` : ''}`
                        : '—'}
                    </TableCell>
                    <TableCell className="text-sm">
                      {vp.stufe2_bezeichnung
                        ? `${vp.stufe2_bezeichnung}${vp.stufe2_menge ? ` × ${vp.stufe2_menge}` : ''}`
                        : '—'}
                    </TableCell>
                    <TableCell className="text-sm">
                      {vp.stufe3_bezeichnung
                        ? `${vp.stufe3_bezeichnung}${vp.stufe3_menge ? ` × ${vp.stufe3_menge}` : ''}`
                        : '—'}
                    </TableCell>
                    <TableCell>
                      <Badge variant={vp.aktiv ? 'default' : 'secondary'}>
                        {vp.aktiv ? 'Aktiv' : 'Inaktiv'}
                      </Badge>
                    </TableCell>
                    <TableCell className="text-right">
                      <Button
                        variant="ghost"
                        size="icon"
                        disabled={deletingKey === vp.verpackungs_nr || !vp.aktiv}
                        onClick={() => handleDelete(vp.verpackungs_nr)}
                        aria-label={`Verpackung ${vp.verpackungs_nr} deaktivieren`}
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
