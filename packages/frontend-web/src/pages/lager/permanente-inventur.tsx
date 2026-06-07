import { useState } from 'react'
import { useForm } from 'react-hook-form'
import { toast } from 'sonner'
import { ClipboardCheck, Plus, CheckCircle2 } from 'lucide-react'
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card'
import { Button } from '@/components/ui/button'
import { Input } from '@/components/ui/input'
import { Label } from '@/components/ui/label'
import { Badge } from '@/components/ui/badge'
import { Skeleton } from '@/components/ui/skeleton'
import { Table, TableBody, TableCell, TableHead, TableHeader, TableRow } from '@/components/ui/table'
import {
  usePIVAbschluesse, useCreatePIVAbschluss, usePIVPositionen, useCreatePIVPosition,
  useZaehlen, useAbschliessen,
} from '@/lib/api/inventur-piv'

function num(v: number | null): string {
  return v == null ? '—' : Number(v).toLocaleString('de-DE', { maximumFractionDigits: 3 })
}

type AbschlussForm = { abschluss_datum: string; inventurgruppe_nr: string; lager_nr: string; bemerkung: string }
type PosForm = { artikel_nr: string; lagerplatz: string; buchbestand: string; bewertungspreis_eur: string }

export default function PermanenteInventurPage() {
  const [aktiv, setAktiv] = useState('')
  const [zaehl, setZaehl] = useState<Record<string, string>>({})

  const abschluesse = usePIVAbschluesse()
  const createAbschluss = useCreatePIVAbschluss()
  const positionen = usePIVPositionen(aktiv)
  const createPos = useCreatePIVPosition()
  const zaehlen = useZaehlen()
  const abschliessen = useAbschliessen()

  const aForm = useForm<AbschlussForm>()
  const pForm = useForm<PosForm>()

  const onCreateAbschluss = aForm.handleSubmit(async (d) => {
    try {
      const res = await createAbschluss.mutateAsync({
        abschluss_datum: d.abschluss_datum, inventurgruppe_nr: d.inventurgruppe_nr || null,
        lager_nr: d.lager_nr || null, bemerkung: d.bemerkung || null,
      })
      toast.success('PIV-Abschluss angelegt.')
      aForm.reset()
      setAktiv(res.id)
    } catch (e) { toast.error(e instanceof Error ? e.message : 'Anlegen fehlgeschlagen') }
  })

  const onCreatePos = pForm.handleSubmit(async (d) => {
    if (!aktiv) return
    try {
      await createPos.mutateAsync({ abschlussId: aktiv, body: {
        artikel_nr: d.artikel_nr, lagerplatz: d.lagerplatz || null,
        buchbestand: Number(d.buchbestand), bewertungspreis_eur: d.bewertungspreis_eur ? Number(d.bewertungspreis_eur) : null,
      } })
      toast.success('Position erfasst.')
      pForm.reset()
    } catch (e) { toast.error(e instanceof Error ? e.message : 'Erfassen fehlgeschlagen') }
  })

  const aktiverAbschluss = (abschluesse.data ?? []).find((a) => a.id === aktiv)
  const offen = aktiverAbschluss && aktiverAbschluss.status !== 'abgeschlossen'

  return (
    <div className="container mx-auto space-y-6 py-8">
      <div>
        <h1 className="flex items-center gap-2 text-3xl font-bold">
          <ClipboardCheck className="h-7 w-7 text-emerald-700" /> Permanente Inventur (PIV)
        </h1>
        <p className="mt-2 text-muted-foreground">
          Stichtagsunabhängige Bestandszählung je Inventurgruppe/Lager mit Differenzbewertung.
        </p>
      </div>

      <div className="grid grid-cols-1 gap-4 lg:grid-cols-3">
        <Card className="lg:col-span-1">
          <CardHeader><CardTitle className="text-base">Abschlüsse</CardTitle></CardHeader>
          <CardContent className="space-y-3">
            {abschluesse.isLoading ? <Skeleton className="h-24 w-full" /> : (
              <div className="space-y-1">
                {(abschluesse.data ?? []).map((a) => (
                  <button key={a.id} onClick={() => setAktiv(a.id)}
                    className={`w-full rounded border p-2 text-left text-sm ${aktiv === a.id ? 'border-emerald-400 bg-emerald-50' : 'hover:bg-muted'}`}>
                    <div className="flex justify-between">
                      <span className="font-medium">{a.abschluss_datum}</span>
                      <Badge variant={a.status === 'abgeschlossen' ? 'secondary' : 'outline'}>{a.status}</Badge>
                    </div>
                    <div className="text-xs text-muted-foreground">
                      {a.lager_nr ?? 'alle Lager'} · {a.anzahl_positionen} Pos. · Diff {num(a.differenzwert_eur)} €
                    </div>
                  </button>
                ))}
                {(abschluesse.data ?? []).length === 0 && <p className="text-sm text-muted-foreground">Keine Abschlüsse.</p>}
              </div>
            )}
            <form onSubmit={onCreateAbschluss} className="space-y-2 border-t pt-3">
              <div className="space-y-1"><Label>Abschluss-Datum</Label><Input type="date" {...aForm.register('abschluss_datum', { required: true })} /></div>
              <div className="grid grid-cols-2 gap-2">
                <div className="space-y-1"><Label>Inv.-Gruppe</Label><Input {...aForm.register('inventurgruppe_nr')} /></div>
                <div className="space-y-1"><Label>Lager</Label><Input {...aForm.register('lager_nr')} /></div>
              </div>
              <div className="space-y-1"><Label>Bemerkung</Label><Input {...aForm.register('bemerkung')} /></div>
              <Button type="submit" disabled={createAbschluss.isPending} className="w-full"><Plus className="mr-2 h-4 w-4" />Abschluss anlegen</Button>
            </form>
          </CardContent>
        </Card>

        <Card className="lg:col-span-2">
          <CardHeader className="flex flex-row items-center justify-between">
            <CardTitle className="text-base">Positionen {aktiverAbschluss ? `· ${aktiverAbschluss.abschluss_datum}` : ''}</CardTitle>
            {offen && (
              <Button size="sm" variant="secondary" disabled={abschliessen.isPending}
                onClick={async () => {
                  try { await abschliessen.mutateAsync(aktiv); toast.success('Inventur abgeschlossen.') }
                  catch (e) { toast.error(e instanceof Error ? e.message : 'Abschluss fehlgeschlagen') }
                }}>
                <CheckCircle2 className="mr-2 h-4 w-4" />Abschließen
              </Button>
            )}
          </CardHeader>
          <CardContent className="space-y-3">
            {!aktiv ? <p className="text-sm text-muted-foreground">Links einen Abschluss wählen oder anlegen.</p> : positionen.isLoading ? <Skeleton className="h-24 w-full" /> : (
              <Table>
                <TableHeader><TableRow>
                  <TableHead>Artikel</TableHead><TableHead>Platz</TableHead>
                  <TableHead className="text-right">Buchbest.</TableHead><TableHead className="text-right">Zählmenge</TableHead>
                  <TableHead className="text-right">Differenz</TableHead><TableHead className="text-right">Diff. €</TableHead>
                  {offen && <TableHead></TableHead>}
                </TableRow></TableHeader>
                <TableBody>
                  {(positionen.data ?? []).map((p) => (
                    <TableRow key={p.id}>
                      <TableCell className="font-mono">{p.artikel_nr}</TableCell>
                      <TableCell>{p.lagerplatz ?? '—'}</TableCell>
                      <TableCell className="text-right font-mono">{num(p.buchbestand)}</TableCell>
                      <TableCell className="text-right font-mono">{num(p.zaehlmenge)}</TableCell>
                      <TableCell className={`text-right font-mono ${(p.differenz ?? 0) < 0 ? 'text-red-600' : (p.differenz ?? 0) > 0 ? 'text-emerald-700' : ''}`}>{num(p.differenz)}</TableCell>
                      <TableCell className="text-right font-mono">{num(p.differenzwert_eur)}</TableCell>
                      {offen && (
                        <TableCell>
                          <div className="flex items-center gap-1">
                            <Input className="h-8 w-24" type="number" step="0.001" placeholder="zählen"
                              value={zaehl[p.id] ?? ''} onChange={(e) => setZaehl((s) => ({ ...s, [p.id]: e.target.value }))} />
                            <Button size="sm" variant="ghost" disabled={zaehlen.isPending || !zaehl[p.id]}
                              onClick={async () => {
                                try {
                                  await zaehlen.mutateAsync({ abschlussId: aktiv, posId: p.id, zaehlmenge: Number(zaehl[p.id]) })
                                  setZaehl((s) => ({ ...s, [p.id]: '' }))
                                  toast.success('Zählmenge erfasst.')
                                } catch (e) { toast.error(e instanceof Error ? e.message : 'Zählen fehlgeschlagen') }
                              }}>OK</Button>
                          </div>
                        </TableCell>
                      )}
                    </TableRow>
                  ))}
                  {(positionen.data ?? []).length === 0 && (
                    <TableRow><TableCell colSpan={offen ? 7 : 6} className="text-center text-muted-foreground">Keine Positionen.</TableCell></TableRow>
                  )}
                </TableBody>
              </Table>
            )}

            {offen && (
              <form onSubmit={onCreatePos} className="grid grid-cols-4 gap-2 border-t pt-3">
                <div className="space-y-1"><Label>Artikel-Nr.</Label><Input {...pForm.register('artikel_nr', { required: true })} /></div>
                <div className="space-y-1"><Label>Lagerplatz</Label><Input {...pForm.register('lagerplatz')} /></div>
                <div className="space-y-1"><Label>Buchbestand</Label><Input type="number" step="0.001" {...pForm.register('buchbestand', { required: true })} /></div>
                <div className="space-y-1"><Label>Bew.-Preis €</Label><Input type="number" step="0.01" {...pForm.register('bewertungspreis_eur')} /></div>
                <div className="col-span-4"><Button type="submit" disabled={createPos.isPending}><Plus className="mr-2 h-4 w-4" />Position erfassen</Button></div>
              </form>
            )}
          </CardContent>
        </Card>
      </div>
    </div>
  )
}
