import { useState } from 'react'
import { useForm } from 'react-hook-form'
import { toast } from 'sonner'
import { Calculator, Banknote, Ban, Plus } from 'lucide-react'
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card'
import { Button } from '@/components/ui/button'
import { Input } from '@/components/ui/input'
import { Label } from '@/components/ui/label'
import { Badge } from '@/components/ui/badge'
import { Skeleton } from '@/components/ui/skeleton'
import { Table, TableBody, TableCell, TableHead, TableHeader, TableRow } from '@/components/ui/table'
import {
  useAuszifferungen, useCreateAuszifferung, useStornoAuszifferung, useBerechneSkonto,
  type SkontoBerechnungResult,
} from '@/lib/api/op-skonto-auszifferung'

function eur(v: number): string {
  return `${Number(v).toLocaleString('de-DE', { minimumFractionDigits: 2 })} €`
}

type AusForm = {
  op_id: string; rechnungsnr: string; zahlungsdatum: string; zahlungsbetrag_eur: string
  skonto_betrag_eur: string; zahlungsart: string; skonto_konto: string; buchungstext: string
}
type CalcForm = { rechnungsbetrag_eur: string; skonto_prozent: string; zahlungsdatum: string; skonto_bis: string }

export default function OpSkontoAuszifferungPage() {
  const list = useAuszifferungen()
  const create = useCreateAuszifferung()
  const storno = useStornoAuszifferung()
  const berechne = useBerechneSkonto()
  const [calcResult, setCalcResult] = useState<SkontoBerechnungResult | null>(null)

  const form = useForm<AusForm>({ defaultValues: { zahlungsart: 'ueberweisung' } })
  const calc = useForm<CalcForm>()

  const onCreate = form.handleSubmit(async (d) => {
    try {
      await create.mutateAsync({
        op_id: d.op_id, rechnungsnr: d.rechnungsnr || null, zahlungsdatum: d.zahlungsdatum,
        zahlungsbetrag_eur: Number(d.zahlungsbetrag_eur),
        skonto_betrag_eur: d.skonto_betrag_eur ? Number(d.skonto_betrag_eur) : 0,
        zahlungsart: d.zahlungsart || null, skonto_konto: d.skonto_konto || null,
        buchungstext: d.buchungstext || null,
      })
      toast.success('Auszifferung gebucht.')
      form.reset({ zahlungsart: 'ueberweisung' })
    } catch (e) { toast.error(e instanceof Error ? e.message : 'Buchen fehlgeschlagen') }
  })

  const onCalc = calc.handleSubmit(async (d) => {
    try {
      const res = await berechne.mutateAsync({
        rechnungsbetrag_eur: Number(d.rechnungsbetrag_eur), skonto_prozent: Number(d.skonto_prozent),
        zahlungsdatum: d.zahlungsdatum, skonto_bis: d.skonto_bis || null,
      })
      setCalcResult(res)
    } catch (e) { toast.error(e instanceof Error ? e.message : 'Berechnung fehlgeschlagen') }
  })

  return (
    <div className="container mx-auto space-y-6 py-8">
      <div>
        <h1 className="flex items-center gap-2 text-3xl font-bold">
          <Banknote className="h-7 w-7 text-emerald-700" /> OP Skonto-Auszifferung
        </h1>
        <p className="mt-2 text-muted-foreground">
          Offene Posten mit Zahlungseingang und Skontoabzug ausziffern; FIBU-Skontokonto-gerecht.
        </p>
      </div>

      <Card>
        <CardHeader><CardTitle className="text-base">Auszifferungen</CardTitle></CardHeader>
        <CardContent>
          {list.isLoading ? <Skeleton className="h-24 w-full" /> : (
            <Table>
              <TableHeader><TableRow>
                <TableHead>Rechnung</TableHead><TableHead>Zahldatum</TableHead>
                <TableHead className="text-right">Zahlung</TableHead><TableHead className="text-right">Skonto</TableHead>
                <TableHead className="text-right">Gesamt</TableHead><TableHead>Art</TableHead>
                <TableHead>Status</TableHead><TableHead></TableHead>
              </TableRow></TableHeader>
              <TableBody>
                {(list.data ?? []).map((a) => (
                  <TableRow key={a.id} className={a.storniert ? 'opacity-50' : ''}>
                    <TableCell className="font-mono">{a.rechnungsnr ?? a.op_id}</TableCell>
                    <TableCell>{a.zahlungsdatum}</TableCell>
                    <TableCell className="text-right font-mono">{eur(a.zahlungsbetrag_eur)}</TableCell>
                    <TableCell className="text-right font-mono">{eur(a.skonto_betrag_eur)}</TableCell>
                    <TableCell className="text-right font-mono">{eur(a.gesamtbetrag_eur)}</TableCell>
                    <TableCell>{a.zahlungsart ?? '—'}</TableCell>
                    <TableCell>{a.storniert ? <Badge variant="destructive">storniert</Badge> : <Badge variant="outline">{a.status}</Badge>}</TableCell>
                    <TableCell>
                      {!a.storniert && (
                        <Button variant="ghost" size="icon" aria-label="Stornieren" disabled={storno.isPending}
                          onClick={async () => {
                            try { await storno.mutateAsync(a.id); toast.success('Storniert.') }
                            catch (e) { toast.error(e instanceof Error ? e.message : 'Stornieren fehlgeschlagen') }
                          }}>
                          <Ban className="h-4 w-4 text-red-600" />
                        </Button>
                      )}
                    </TableCell>
                  </TableRow>
                ))}
                {(list.data ?? []).length === 0 && (
                  <TableRow><TableCell colSpan={8} className="text-center text-muted-foreground">Keine Auszifferungen.</TableCell></TableRow>
                )}
              </TableBody>
            </Table>
          )}
        </CardContent>
      </Card>

      <div className="grid grid-cols-1 gap-4 lg:grid-cols-2">
        <Card>
          <CardHeader><CardTitle className="text-base">Auszifferung buchen</CardTitle></CardHeader>
          <CardContent>
            <form onSubmit={onCreate} className="grid grid-cols-2 gap-2">
              <div className="space-y-1 col-span-2"><Label>OP-ID</Label><Input {...form.register('op_id', { required: true })} /></div>
              <div className="space-y-1"><Label>Rechnungs-Nr.</Label><Input {...form.register('rechnungsnr')} /></div>
              <div className="space-y-1"><Label>Zahlungsdatum</Label><Input type="date" {...form.register('zahlungsdatum', { required: true })} /></div>
              <div className="space-y-1"><Label>Zahlungsbetrag (€)</Label><Input type="number" step="0.01" {...form.register('zahlungsbetrag_eur', { required: true })} /></div>
              <div className="space-y-1"><Label>Skontobetrag (€)</Label><Input type="number" step="0.01" {...form.register('skonto_betrag_eur')} /></div>
              <div className="space-y-1"><Label>Zahlungsart</Label>
                <select className="h-10 w-full rounded-md border px-2" {...form.register('zahlungsart')}>
                  <option value="ueberweisung">Überweisung</option><option value="lastschrift">Lastschrift</option>
                  <option value="bar">Bar</option><option value="scheck">Scheck</option>
                </select>
              </div>
              <div className="space-y-1"><Label>Skonto-Konto</Label><Input placeholder="8736" {...form.register('skonto_konto')} /></div>
              <div className="space-y-1 col-span-2"><Label>Buchungstext</Label><Input {...form.register('buchungstext')} /></div>
              <div className="col-span-2"><Button type="submit" disabled={create.isPending}><Plus className="mr-2 h-4 w-4" />Buchen</Button></div>
            </form>
          </CardContent>
        </Card>

        <Card>
          <CardHeader><CardTitle className="text-base">Skonto-Rechner</CardTitle></CardHeader>
          <CardContent className="space-y-3">
            <form onSubmit={onCalc} className="grid grid-cols-2 gap-2">
              <div className="space-y-1"><Label>Rechnungsbetrag (€)</Label><Input type="number" step="0.01" {...calc.register('rechnungsbetrag_eur', { required: true })} /></div>
              <div className="space-y-1"><Label>Skonto (%)</Label><Input type="number" step="0.01" {...calc.register('skonto_prozent', { required: true })} /></div>
              <div className="space-y-1"><Label>Zahlungsdatum</Label><Input type="date" {...calc.register('zahlungsdatum', { required: true })} /></div>
              <div className="space-y-1"><Label>Skonto-Frist bis</Label><Input type="date" {...calc.register('skonto_bis')} /></div>
              <div className="col-span-2"><Button type="submit" variant="secondary" disabled={berechne.isPending}><Calculator className="mr-2 h-4 w-4" />Berechnen</Button></div>
            </form>
            {calcResult && (
              <div className={`rounded-md border p-3 text-sm ${calcResult.skonto_gueltig ? 'border-emerald-200 bg-emerald-50' : 'border-amber-200 bg-amber-50'}`}>
                <div className="flex justify-between"><span>Skontobetrag:</span><strong className="font-mono">{eur(calcResult.skontobetrag_eur)}</strong></div>
                <div className="flex justify-between"><span>Zahlungsbetrag:</span><strong className="font-mono">{eur(calcResult.zahlungsbetrag_eur)}</strong></div>
                {calcResult.hinweis && <p className="mt-1 text-amber-800">{calcResult.hinweis}</p>}
              </div>
            )}
          </CardContent>
        </Card>
      </div>
    </div>
  )
}
