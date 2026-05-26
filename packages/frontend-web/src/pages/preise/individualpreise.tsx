import { useState } from 'react'
import { useForm } from 'react-hook-form'
import { toast } from 'sonner'
import {
  useIndividualpreise,
  useCreateIndividualpreis,
  useDeleteIndividualpreis,
  type PreisTyp,
} from '@/lib/api/individualpreise'
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
import { Trash2, Plus } from 'lucide-react'

type FormData = {
  artikel_nr: string
  partner_nr: string
  gueltig_von: string
  gueltig_bis: string
  preis_eur: string
  staffel_menge: string
  mengeneinheit: string
  waehrung: string
  notiz: string
}

function PreisTypBadge({ typ }: { typ: PreisTyp }) {
  return (
    <Badge variant={typ === 'VK' ? 'default' : 'secondary'}>
      {typ === 'VK' ? 'Verkauf' : 'Einkauf'}
    </Badge>
  )
}

function IndividualpreisTab({ preisTyp }: { preisTyp: PreisTyp }) {
  const [deletingIds, setDeletingIds] = useState<Set<string>>(new Set())
  const { data: preise, isLoading, isError } = useIndividualpreise({ preis_typ: preisTyp })
  const createMutation = useCreateIndividualpreis()
  const deleteMutation = useDeleteIndividualpreis()

  const { register, handleSubmit, reset } = useForm<FormData>({
    defaultValues: {
      artikel_nr: '',
      partner_nr: '',
      gueltig_von: '',
      gueltig_bis: '',
      preis_eur: '',
      staffel_menge: '0',
      mengeneinheit: '',
      waehrung: 'EUR',
      notiz: '',
    },
  })

  const onSubmit = handleSubmit(async (data) => {
    try {
      await createMutation.mutateAsync({
        preis_typ: preisTyp,
        artikel_nr: data.artikel_nr,
        partner_nr: data.partner_nr || null,
        gueltig_von: data.gueltig_von,
        gueltig_bis: data.gueltig_bis || null,
        preis_eur: parseFloat(data.preis_eur),
        staffel_menge: data.staffel_menge ? parseFloat(data.staffel_menge) : 0,
        mengeneinheit: data.mengeneinheit || null,
        waehrung: data.waehrung || 'EUR',
        notiz: data.notiz || null,
      })
      toast.success(`Individualpreis für ${data.artikel_nr} angelegt`)
      reset()
    } catch {
      toast.error('Fehler beim Anlegen des Individualpreises')
    }
  })

  const handleDelete = async (id: string, artikelNr: string) => {
    if (deletingIds.has(id)) return
    setDeletingIds((prev) => new Set(prev).add(id))
    try {
      await deleteMutation.mutateAsync(id)
      toast.success(`Individualpreis für ${artikelNr} deaktiviert`)
    } catch {
      toast.error('Fehler beim Deaktivieren')
    } finally {
      setDeletingIds((prev) => {
        const next = new Set(prev)
        next.delete(id)
        return next
      })
    }
  }

  const label = preisTyp === 'VK' ? 'VK-Preis' : 'EK-Preis'

  return (
    <div className="space-y-6">
      <Card>
        <CardHeader>
          <CardTitle className="text-base">Neuer {label} [PRI{preisTyp === 'EK' ? 'E' : ''}]</CardTitle>
        </CardHeader>
        <CardContent>
          <form onSubmit={onSubmit} className="grid grid-cols-1 sm:grid-cols-4 gap-4 items-end">
            <div className="space-y-1">
              <Label htmlFor={`${preisTyp}_artikel_nr`}>Artikel-Nr *</Label>
              <Input
                id={`${preisTyp}_artikel_nr`}
                placeholder="z.B. ART001"
                {...register('artikel_nr', { required: true })}
              />
            </div>
            <div className="space-y-1">
              <Label htmlFor={`${preisTyp}_partner_nr`}>Partner-Nr</Label>
              <Input
                id={`${preisTyp}_partner_nr`}
                placeholder="optional"
                {...register('partner_nr')}
              />
            </div>
            <div className="space-y-1">
              <Label htmlFor={`${preisTyp}_preis_eur`}>Preis (EUR) *</Label>
              <Input
                id={`${preisTyp}_preis_eur`}
                type="number"
                step="0.0001"
                min="0"
                placeholder="0.0000"
                {...register('preis_eur', { required: true })}
              />
            </div>
            <div className="space-y-1">
              <Label htmlFor={`${preisTyp}_staffel_menge`}>Staffel-Menge</Label>
              <Input
                id={`${preisTyp}_staffel_menge`}
                type="number"
                step="0.001"
                min="0"
                placeholder="0"
                {...register('staffel_menge')}
              />
            </div>
            <div className="space-y-1">
              <Label htmlFor={`${preisTyp}_gueltig_von`}>Gültig von *</Label>
              <Input
                id={`${preisTyp}_gueltig_von`}
                type="date"
                {...register('gueltig_von', { required: true })}
              />
            </div>
            <div className="space-y-1">
              <Label htmlFor={`${preisTyp}_gueltig_bis`}>Gültig bis</Label>
              <Input
                id={`${preisTyp}_gueltig_bis`}
                type="date"
                {...register('gueltig_bis')}
              />
            </div>
            <div className="space-y-1">
              <Label htmlFor={`${preisTyp}_mengeneinheit`}>Mengeneinheit</Label>
              <Input
                id={`${preisTyp}_mengeneinheit`}
                placeholder="z.B. KG"
                {...register('mengeneinheit')}
              />
            </div>
            <div className="space-y-1">
              <Label htmlFor={`${preisTyp}_waehrung`}>Währung</Label>
              <Input
                id={`${preisTyp}_waehrung`}
                placeholder="EUR"
                {...register('waehrung')}
              />
            </div>
            <div className="space-y-1 sm:col-span-3">
              <Label htmlFor={`${preisTyp}_notiz`}>Notiz</Label>
              <Input
                id={`${preisTyp}_notiz`}
                placeholder="optional"
                {...register('notiz')}
              />
            </div>
            <div className="flex justify-end">
              <Button
                type="submit"
                disabled={createMutation.isPending}
                className="gap-2"
                aria-label={`${label} anlegen`}
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
          <CardTitle className="text-base">{label}e</CardTitle>
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
              Fehler beim Laden der Individualpreise.
            </p>
          ) : (
            <Table>
              <TableHeader>
                <TableRow>
                  <TableHead>Typ</TableHead>
                  <TableHead>Artikel-Nr</TableHead>
                  <TableHead>Partner-Nr</TableHead>
                  <TableHead className="text-right">Preis EUR</TableHead>
                  <TableHead className="text-right">Staffel</TableHead>
                  <TableHead>ME</TableHead>
                  <TableHead>Gültig von</TableHead>
                  <TableHead>Gültig bis</TableHead>
                  <TableHead className="w-16" />
                </TableRow>
              </TableHeader>
              <TableBody>
                {preise?.length === 0 && (
                  <TableRow>
                    <TableCell colSpan={9} className="text-center text-muted-foreground py-6">
                      Keine {label}e vorhanden
                    </TableCell>
                  </TableRow>
                )}
                {preise?.map((p) => (
                  <TableRow key={p.id}>
                    <TableCell>
                      <PreisTypBadge typ={p.preis_typ} />
                    </TableCell>
                    <TableCell className="font-mono">{p.artikel_nr}</TableCell>
                    <TableCell className="font-mono">{p.partner_nr ?? '—'}</TableCell>
                    <TableCell className="text-right tabular-nums">
                      {Number(p.preis_eur).toFixed(4)}
                    </TableCell>
                    <TableCell className="text-right tabular-nums">
                      {p.staffel_menge > 0 ? p.staffel_menge : '—'}
                    </TableCell>
                    <TableCell>{p.mengeneinheit ?? '—'}</TableCell>
                    <TableCell>{p.gueltig_von}</TableCell>
                    <TableCell>{p.gueltig_bis ?? '—'}</TableCell>
                    <TableCell>
                      <Button
                        variant="ghost"
                        size="sm"
                        disabled={deletingIds.has(p.id)}
                        onClick={() => handleDelete(p.id, p.artikel_nr)}
                        aria-label={`Individualpreis ${p.artikel_nr} deaktivieren`}
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

export default function IndividualpreisePage() {
  return (
    <div className="p-6 space-y-4">
      <div>
        <h1 className="text-2xl font-semibold">Individualpreise [PRI/PRIE]</h1>
        <p className="text-muted-foreground text-sm mt-1">
          Artikel- und partnerspezifische Einzelpreise mit Gültigkeitszeitraum und Staffelmengen.
          VK = Verkaufspreise, EK = Einkaufspreise.
        </p>
      </div>
      <Tabs defaultValue="vk">
        <TabsList>
          <TabsTrigger value="vk">VK-Preise</TabsTrigger>
          <TabsTrigger value="ek">EK-Preise</TabsTrigger>
        </TabsList>
        <TabsContent value="vk" className="mt-4">
          <IndividualpreisTab preisTyp="VK" />
        </TabsContent>
        <TabsContent value="ek" className="mt-4">
          <IndividualpreisTab preisTyp="EK" />
        </TabsContent>
      </Tabs>
    </div>
  )
}
