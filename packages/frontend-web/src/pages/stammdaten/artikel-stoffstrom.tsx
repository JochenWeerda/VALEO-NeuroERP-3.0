import { useForm } from 'react-hook-form'
import { toast } from 'sonner'
import { Leaf, Plus, Trash2 } from 'lucide-react'
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card'
import { Button } from '@/components/ui/button'
import { Input } from '@/components/ui/input'
import { Label } from '@/components/ui/label'
import { Badge } from '@/components/ui/badge'
import { Skeleton } from '@/components/ui/skeleton'
import { Table, TableBody, TableCell, TableHead, TableHeader, TableRow } from '@/components/ui/table'
import {
  useStoffstroeme, useCreateStoffstrom, useDeleteStoffstrom,
} from '@/lib/api/artikel-stoffstrom'

type FormData = {
  artikel_nr: string
  anbauland: string
  rohstoff_kategorie: string
  co2_aequivalent_kg_per_t: string
  thg_wert: string
  nachhaltig: boolean
  iscc_zertifiziert: boolean
  red_konform: boolean
  bemerkung: string
}

function num(v: number | null): string {
  return v == null ? '—' : Number(v).toLocaleString('de-DE', { maximumFractionDigits: 2 })
}

export default function ArtikelStoffstromPage() {
  const list = useStoffstroeme()
  const create = useCreateStoffstrom()
  const remove = useDeleteStoffstrom()
  const form = useForm<FormData>({ defaultValues: { nachhaltig: true, iscc_zertifiziert: false, red_konform: false } })

  const onSubmit = form.handleSubmit(async (d) => {
    try {
      await create.mutateAsync({
        artikel_nr: d.artikel_nr,
        anbauland: d.anbauland || null,
        rohstoff_kategorie: d.rohstoff_kategorie || null,
        co2_aequivalent_kg_per_t: d.co2_aequivalent_kg_per_t ? Number(d.co2_aequivalent_kg_per_t) : null,
        thg_wert: d.thg_wert ? Number(d.thg_wert) : null,
        nachhaltig: d.nachhaltig, iscc_zertifiziert: d.iscc_zertifiziert, red_konform: d.red_konform,
        bemerkung: d.bemerkung || null,
      })
      toast.success('Stoffstrom-Datensatz angelegt.')
      form.reset({ nachhaltig: true, iscc_zertifiziert: false, red_konform: false })
    } catch (e) { toast.error(e instanceof Error ? e.message : 'Anlegen fehlgeschlagen') }
  })

  return (
    <div className="container mx-auto space-y-6 py-8">
      <div>
        <h1 className="flex items-center gap-2 text-3xl font-bold">
          <Leaf className="h-7 w-7 text-emerald-700" /> Stoffstrom &amp; THG-Bilanz
        </h1>
        <p className="mt-2 text-muted-foreground">
          Nachhaltigkeits-/THG-Daten je Artikel (Anbauland, CO₂-Äquivalent, THG-Wert, ISCC/RED-Konformität).
        </p>
      </div>

      <Card>
        <CardHeader><CardTitle className="text-base">Stoffstrom-Datensätze</CardTitle></CardHeader>
        <CardContent>
          {list.isLoading ? <Skeleton className="h-24 w-full" /> : (
            <Table>
              <TableHeader><TableRow>
                <TableHead>Artikel</TableHead><TableHead>Anbauland</TableHead><TableHead>Kategorie</TableHead>
                <TableHead className="text-right">CO₂ kg/t</TableHead><TableHead className="text-right">THG</TableHead>
                <TableHead>Zertifikate</TableHead><TableHead></TableHead>
              </TableRow></TableHeader>
              <TableBody>
                {(list.data ?? []).map((s) => (
                  <TableRow key={s.id}>
                    <TableCell className="font-mono">{s.artikel_nr}</TableCell>
                    <TableCell>{s.anbauland ?? '—'}</TableCell>
                    <TableCell>{s.rohstoff_kategorie ?? '—'}</TableCell>
                    <TableCell className="text-right font-mono">{num(s.co2_aequivalent_kg_per_t)}</TableCell>
                    <TableCell className="text-right font-mono">{num(s.thg_wert)}</TableCell>
                    <TableCell className="space-x-1">
                      {s.nachhaltig && <Badge className="bg-emerald-600">nachhaltig</Badge>}
                      {s.iscc_zertifiziert && <Badge variant="outline">ISCC</Badge>}
                      {s.red_konform && <Badge variant="outline">RED</Badge>}
                    </TableCell>
                    <TableCell>
                      <Button variant="ghost" size="icon" aria-label="Löschen" disabled={remove.isPending}
                        onClick={async () => {
                          try { await remove.mutateAsync(s.id); toast.success('Gelöscht.') }
                          catch (e) { toast.error(e instanceof Error ? e.message : 'Löschen fehlgeschlagen') }
                        }}>
                        <Trash2 className="h-4 w-4 text-status-error" />
                      </Button>
                    </TableCell>
                  </TableRow>
                ))}
                {(list.data ?? []).length === 0 && (
                  <TableRow><TableCell colSpan={7} className="text-center text-muted-foreground">Keine Datensätze.</TableCell></TableRow>
                )}
              </TableBody>
            </Table>
          )}
        </CardContent>
      </Card>

      <Card>
        <CardHeader><CardTitle className="text-base">Neuen Stoffstrom anlegen</CardTitle></CardHeader>
        <CardContent>
          <form onSubmit={onSubmit} className="grid grid-cols-1 gap-3 md:grid-cols-3">
            <div className="space-y-1"><Label>Artikel-Nr.</Label><Input {...form.register('artikel_nr', { required: true })} /></div>
            <div className="space-y-1"><Label>Anbauland (ISO)</Label><Input placeholder="DE" {...form.register('anbauland')} /></div>
            <div className="space-y-1"><Label>Rohstoff-Kategorie</Label><Input {...form.register('rohstoff_kategorie')} /></div>
            <div className="space-y-1"><Label>CO₂-Äquiv. (kg/t)</Label><Input type="number" step="0.01" {...form.register('co2_aequivalent_kg_per_t')} /></div>
            <div className="space-y-1"><Label>THG-Wert (gCO₂eq/MJ)</Label><Input type="number" step="0.01" {...form.register('thg_wert')} /></div>
            <div className="space-y-1"><Label>Bemerkung</Label><Input {...form.register('bemerkung')} /></div>
            <label className="flex items-center gap-2 text-sm"><input type="checkbox" {...form.register('nachhaltig')} /> Nachhaltig</label>
            <label className="flex items-center gap-2 text-sm"><input type="checkbox" {...form.register('iscc_zertifiziert')} /> ISCC-zertifiziert</label>
            <label className="flex items-center gap-2 text-sm"><input type="checkbox" {...form.register('red_konform')} /> RED-konform</label>
            <div className="md:col-span-3"><Button type="submit" disabled={create.isPending}><Plus className="mr-2 h-4 w-4" />Anlegen</Button></div>
          </form>
        </CardContent>
      </Card>
    </div>
  )
}
