import { useState } from 'react'
import { useForm } from 'react-hook-form'
import { toast } from 'sonner'
import { CalendarRange, Plus, Trash2, Wand2 } from 'lucide-react'
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card'
import { Button } from '@/components/ui/button'
import { Input } from '@/components/ui/input'
import { Label } from '@/components/ui/label'
import { Badge } from '@/components/ui/badge'
import { Skeleton } from '@/components/ui/skeleton'
import { Table, TableBody, TableCell, TableHead, TableHeader, TableRow } from '@/components/ui/table'
import { Tabs, TabsContent, TabsList, TabsTrigger } from '@/components/ui/tabs'
import { NativeSelect } from '@/components/ui/native-select'
import {
  useMengenzeitraeume, useCreateMengenzeitraum, useDeleteMengenzeitraum, useGenerateMengenzeitraeume,
  useZuAbschlagsgruppen, useCreateZuAbschlagsgruppe, useZuAbschlaege, useCreateZuAbschlag,
} from '@/lib/api/kontrakt-mengenzeitraum'

function num(v: number | null | undefined): string {
  return v == null ? '—' : Number(v).toLocaleString('de-DE', { minimumFractionDigits: 0, maximumFractionDigits: 3 })
}

type ZeitraumForm = { zeitraum_von: string; zeitraum_bis: string; menge_t: string; variante: string; bemerkung: string }
type GenForm = { von_datum: string; bis_datum: string; gesamt_menge_t: string; variante: string }
type GruppeForm = { gruppe_nr: string; bezeichnung: string; typ: string }
type AbschlagForm = { bezeichnung: string; betrag_eur: string; prozent: string; einheit: string }

export default function KontraktMengenzeitraeumePage() {
  const [kontraktNr, setKontraktNr] = useState('')
  const [aktiverKontrakt, setAktiverKontrakt] = useState('')
  const [deletePendingId, setDeletePendingId] = useState<string | null>(null)
  const [gruppeId, setGruppeId] = useState('')

  const zeitraeume = useMengenzeitraeume(aktiverKontrakt)
  const createZeitraum = useCreateMengenzeitraum()
  const deleteZeitraum = useDeleteMengenzeitraum()
  const generieren = useGenerateMengenzeitraeume()
  const gruppen = useZuAbschlagsgruppen()
  const createGruppe = useCreateZuAbschlagsgruppe()
  const abschlaege = useZuAbschlaege(gruppeId)
  const createAbschlag = useCreateZuAbschlag()

  const zForm = useForm<ZeitraumForm>({ defaultValues: { variante: 'monatl. lin. Abnahme' } })
  const gForm = useForm<GenForm>({ defaultValues: { variante: 'monatl. lin. Abnahme' } })
  const grpForm = useForm<GruppeForm>({ defaultValues: { typ: 'zuschlag' } })
  const abForm = useForm<AbschlagForm>({ defaultValues: { einheit: 't' } })

  const onCreateZeitraum = zForm.handleSubmit(async (d) => {
    if (!aktiverKontrakt) { toast.error('Bitte zuerst eine Kontrakt-Nr. laden.'); return }
    try {
      await createZeitraum.mutateAsync({
        kontrakt_nr: aktiverKontrakt, zeitraum_von: d.zeitraum_von, zeitraum_bis: d.zeitraum_bis,
        menge_t: Number(d.menge_t), variante: d.variante || null, bemerkung: d.bemerkung || null,
      })
      toast.success('Mengenzeitraum angelegt.')
      zForm.reset({ variante: 'monatl. lin. Abnahme' })
    } catch (e) { toast.error(e instanceof Error ? e.message : 'Anlegen fehlgeschlagen') }
  })

  const onGenerieren = gForm.handleSubmit(async (d) => {
    if (!aktiverKontrakt) { toast.error('Bitte zuerst eine Kontrakt-Nr. laden.'); return }
    try {
      await generieren.mutateAsync({
        kontraktNr: aktiverKontrakt, von_datum: d.von_datum, bis_datum: d.bis_datum,
        gesamt_menge_t: Number(d.gesamt_menge_t), variante: d.variante,
      })
      toast.success('Mengenzeiträume generiert.')
    } catch (e) { toast.error(e instanceof Error ? e.message : 'Generieren fehlgeschlagen') }
  })

  const onCreateGruppe = grpForm.handleSubmit(async (d) => {
    try {
      await createGruppe.mutateAsync(d)
      toast.success('Zu-/Abschlagsgruppe angelegt.')
      grpForm.reset({ typ: 'zuschlag' })
    } catch (e) { toast.error(e instanceof Error ? e.message : 'Anlegen fehlgeschlagen') }
  })

  const onCreateAbschlag = abForm.handleSubmit(async (d) => {
    if (!gruppeId) { toast.error('Bitte zuerst eine Gruppe wählen.'); return }
    try {
      await createAbschlag.mutateAsync({
        gruppe_id: gruppeId, bezeichnung: d.bezeichnung,
        betrag_eur: d.betrag_eur ? Number(d.betrag_eur) : null,
        prozent: d.prozent ? Number(d.prozent) : null, einheit: d.einheit || 't',
      })
      toast.success('Zu-/Abschlag angelegt.')
      abForm.reset({ einheit: 't' })
    } catch (e) { toast.error(e instanceof Error ? e.message : 'Anlegen fehlgeschlagen') }
  })

  async function persistDeleteZeitraum(id: string): Promise<void> {
    await deleteZeitraum.mutateAsync({ kontraktNr: aktiverKontrakt, id })
  }

  async function handleDeleteZeitraum(id: string): Promise<void> {
    if (deletePendingId) return
    setDeletePendingId(id)
    try {
      await persistDeleteZeitraum(id)
      toast.success('Gelöscht.')
    } catch (e) {
      toast.error(e instanceof Error ? e.message : 'Löschen fehlgeschlagen')
    } finally {
      setDeletePendingId(null)
    }
  }

  return (
    <div className="container mx-auto space-y-6 p-3 py-4 md:p-6 md:py-8">
      <div>
        <h1 className="flex flex-wrap items-center gap-2 text-2xl font-bold md:text-3xl">
          <CalendarRange className="h-7 w-7 text-status-success" /> Kontrakt-Mengenzeiträume und Zu-/Abschläge
        </h1>
        <p className="mt-2 text-muted-foreground">
          Abnahme-Staffeln je Kontrakt und kontraktbezogene Zu-/Abschläge.
        </p>
      </div>

      <Tabs defaultValue="zeitraeume">
        <TabsList className="flex min-h-touch w-full flex-wrap justify-start" aria-label="Kontrakt-Staffeln">
          <TabsTrigger value="zeitraeume" className="min-h-11 touch-manipulation">Mengenzeiträume</TabsTrigger>
          <TabsTrigger value="abschlaege" className="min-h-11 touch-manipulation">Zu-/Abschläge</TabsTrigger>
        </TabsList>

        {/* ── Mengenzeiträume ───────────────────────────────────── */}
        <TabsContent value="zeitraeume" className="space-y-4">
          <Card>
            <CardHeader><CardTitle>Kontrakt wählen</CardTitle></CardHeader>
            <CardContent className="flex flex-col items-stretch gap-3 sm:flex-row sm:items-end">
              <div className="space-y-1.5 flex-1">
                <Label htmlFor="knr">Kontrakt-Nr.</Label>
                <Input id="knr" className="min-h-touch" value={kontraktNr} onChange={(e) => setKontraktNr(e.target.value)} placeholder="z.B. K-2026-0001" />
              </div>
              <Button className="min-h-touch touch-manipulation" onClick={() => setAktiverKontrakt(kontraktNr.trim())} disabled={!kontraktNr.trim()}>Laden</Button>
            </CardContent>
          </Card>

          {aktiverKontrakt && (
            <>
              <Card>
                <CardHeader><CardTitle className="text-base">Mengenzeiträume für {aktiverKontrakt}</CardTitle></CardHeader>
                <CardContent>
                  {zeitraeume.isLoading ? <Skeleton className="h-24 w-full" /> : (
                    <Table>
                      <TableHeader><TableRow>
                        <TableHead>Von</TableHead><TableHead>Bis</TableHead><TableHead className="text-right">Menge (t)</TableHead>
                        <TableHead className="text-right">Geliefert</TableHead><TableHead className="text-right">Rest</TableHead>
                        <TableHead>Variante</TableHead><TableHead>Status</TableHead><TableHead></TableHead>
                      </TableRow></TableHeader>
                      <TableBody>
                        {(zeitraeume.data ?? []).map((z) => (
                          <TableRow key={z.id}>
                            <TableCell>{z.zeitraum_von}</TableCell><TableCell>{z.zeitraum_bis}</TableCell>
                            <TableCell className="text-right font-mono">{num(z.menge_t)}</TableCell>
                            <TableCell className="text-right font-mono">{num(z.menge_bereits_geliefert_t)}</TableCell>
                            <TableCell className="text-right font-mono">{num(z.menge_restmenge_t)}</TableCell>
                            <TableCell>{z.variante ?? '—'}</TableCell>
                            <TableCell><Badge variant="outline">{z.status}</Badge></TableCell>
                            <TableCell>
                              <Button
                                variant="outline"
                                className="min-h-touch touch-manipulation"
                                aria-label={`Zeitraum ${z.zeitraum_von} löschen`}
                                disabled={deletePendingId === z.id || deleteZeitraum.isPending}
                                onClick={() => { void handleDeleteZeitraum(z.id) }}
                              >
                                <Trash2 className="h-4 w-4 text-status-error" />
                                Löschen
                              </Button>
                            </TableCell>
                          </TableRow>
                        ))}
                        {(zeitraeume.data ?? []).length === 0 && (
                          <TableRow><TableCell colSpan={8} className="text-center text-muted-foreground">Keine Mengenzeiträume.</TableCell></TableRow>
                        )}
                      </TableBody>
                    </Table>
                  )}
                </CardContent>
              </Card>

              <div className="grid grid-cols-1 gap-4 lg:grid-cols-2">
                <Card>
                  <CardHeader><CardTitle className="text-base">Mengenzeitraum anlegen</CardTitle></CardHeader>
                  <CardContent>
                    <form onSubmit={onCreateZeitraum} className="space-y-3">
                      <div className="grid grid-cols-2 gap-2">
                        <div className="space-y-1"><Label>Von</Label><Input className="min-h-touch" type="date" {...zForm.register('zeitraum_von', { required: true })} /></div>
                        <div className="space-y-1"><Label>Bis</Label><Input className="min-h-touch" type="date" {...zForm.register('zeitraum_bis', { required: true })} /></div>
                      </div>
                      <div className="grid grid-cols-2 gap-2">
                        <div className="space-y-1"><Label>Menge (t)</Label><Input className="min-h-touch" type="number" step="0.001" {...zForm.register('menge_t', { required: true })} /></div>
                        <div className="space-y-1"><Label>Variante</Label><Input className="min-h-touch" {...zForm.register('variante')} /></div>
                      </div>
                      <div className="space-y-1"><Label>Bemerkung</Label><Input className="min-h-touch" {...zForm.register('bemerkung')} /></div>
                      <Button type="submit" className="min-h-touch touch-manipulation" disabled={createZeitraum.isPending}><Plus className="mr-2 h-4 w-4" />Anlegen</Button>
                    </form>
                  </CardContent>
                </Card>

                <Card>
                  <CardHeader><CardTitle className="text-base">Staffel automatisch generieren</CardTitle></CardHeader>
                  <CardContent>
                    <form onSubmit={onGenerieren} className="space-y-3">
                      <div className="grid grid-cols-2 gap-2">
                        <div className="space-y-1"><Label>Von</Label><Input className="min-h-touch" type="date" {...gForm.register('von_datum', { required: true })} /></div>
                        <div className="space-y-1"><Label>Bis</Label><Input className="min-h-touch" type="date" {...gForm.register('bis_datum', { required: true })} /></div>
                      </div>
                      <div className="grid grid-cols-2 gap-2">
                        <div className="space-y-1"><Label>Gesamtmenge (t)</Label><Input className="min-h-touch" type="number" step="0.001" {...gForm.register('gesamt_menge_t', { required: true })} /></div>
                        <div className="space-y-1"><Label>Variante</Label><Input className="min-h-touch" {...gForm.register('variante')} /></div>
                      </div>
                      <Button type="submit" variant="secondary" className="min-h-touch touch-manipulation" disabled={generieren.isPending}><Wand2 className="mr-2 h-4 w-4" />Generieren</Button>
                    </form>
                  </CardContent>
                </Card>
              </div>
            </>
          )}
        </TabsContent>

        {/* ── Zu-/Abschläge ─────────────────────────────────────── */}
        <TabsContent value="abschlaege" className="space-y-4">
          <div className="grid grid-cols-1 gap-4 lg:grid-cols-2">
            <Card>
              <CardHeader><CardTitle className="text-base">Zu-/Abschlagsgruppen</CardTitle></CardHeader>
              <CardContent className="space-y-3">
                {gruppen.isLoading ? <Skeleton className="h-24 w-full" /> : (
                  <Table>
                    <TableHeader><TableRow><TableHead>Nr.</TableHead><TableHead>Bezeichnung</TableHead><TableHead>Typ</TableHead><TableHead></TableHead></TableRow></TableHeader>
                    <TableBody>
                      {(gruppen.data ?? []).map((g) => (
                        <TableRow key={g.id} className={gruppeId === g.id ? 'bg-muted' : ''}>
                          <TableCell className="font-mono">{g.gruppe_nr}</TableCell>
                          <TableCell>{g.bezeichnung}</TableCell>
                          <TableCell><Badge variant="outline">{g.typ}</Badge></TableCell>
                          <TableCell>
                            <Button variant="outline" className="min-h-touch touch-manipulation" onClick={() => setGruppeId(g.id)}>
                              Positionen
                            </Button>
                          </TableCell>
                        </TableRow>
                      ))}
                      {(gruppen.data ?? []).length === 0 && <TableRow><TableCell colSpan={4} className="text-center text-muted-foreground">Keine Gruppen.</TableCell></TableRow>}
                    </TableBody>
                  </Table>
                )}
                <form onSubmit={onCreateGruppe} className="flex flex-col gap-3 border-t pt-3 sm:flex-row sm:items-end">
                  <div className="space-y-1"><Label>Gruppe-Nr.</Label><Input className="min-h-touch w-full sm:w-28" {...grpForm.register('gruppe_nr', { required: true })} /></div>
                  <div className="space-y-1 flex-1"><Label>Bezeichnung</Label><Input className="min-h-touch" {...grpForm.register('bezeichnung', { required: true })} /></div>
                  <div className="space-y-1">
                    <Label htmlFor="gruppe-typ">Typ</Label>
                    <NativeSelect id="gruppe-typ" className="min-h-touch" {...grpForm.register('typ')}>
                      <option value="zuschlag">Zuschlag</option>
                      <option value="abschlag">Abschlag</option>
                    </NativeSelect>
                  </div>
                  <Button type="submit" className="min-h-touch touch-manipulation" disabled={createGruppe.isPending} aria-label="Gruppe anlegen">
                    <Plus className="h-4 w-4" />Anlegen
                  </Button>
                </form>
              </CardContent>
            </Card>

            <Card>
              <CardHeader><CardTitle className="text-base">Positionen {gruppeId ? '' : '(Gruppe wählen)'}</CardTitle></CardHeader>
              <CardContent className="space-y-3">
                {!gruppeId ? <p className="text-sm text-muted-foreground">Gruppe wählen.</p> : abschlaege.isLoading ? <Skeleton className="h-24 w-full" /> : (
                  <Table>
                    <TableHeader><TableRow><TableHead>Bezeichnung</TableHead><TableHead className="text-right">€/Einheit</TableHead><TableHead className="text-right">%</TableHead><TableHead>Einheit</TableHead></TableRow></TableHeader>
                    <TableBody>
                      {(abschlaege.data ?? []).map((a) => (
                        <TableRow key={a.id}>
                          <TableCell>{a.bezeichnung}</TableCell>
                          <TableCell className="text-right font-mono">{num(a.betrag_eur)}</TableCell>
                          <TableCell className="text-right font-mono">{num(a.prozent)}</TableCell>
                          <TableCell>{a.einheit}</TableCell>
                        </TableRow>
                      ))}
                      {(abschlaege.data ?? []).length === 0 && <TableRow><TableCell colSpan={4} className="text-center text-muted-foreground">Keine Positionen.</TableCell></TableRow>}
                    </TableBody>
                  </Table>
                )}
                {gruppeId && (
                  <form onSubmit={onCreateAbschlag} className="grid grid-cols-1 gap-2 border-t pt-3 sm:grid-cols-2">
                    <div className="space-y-1 sm:col-span-2"><Label>Bezeichnung</Label><Input className="min-h-touch" {...abForm.register('bezeichnung', { required: true })} /></div>
                    <div className="space-y-1"><Label>Betrag (€/Einh.)</Label><Input className="min-h-touch" type="number" step="0.01" {...abForm.register('betrag_eur')} /></div>
                    <div className="space-y-1"><Label>Prozent</Label><Input className="min-h-touch" type="number" step="0.01" {...abForm.register('prozent')} /></div>
                    <div className="space-y-1"><Label>Einheit</Label><Input className="min-h-touch" {...abForm.register('einheit')} /></div>
                    <div className="flex items-end"><Button type="submit" className="min-h-touch w-full touch-manipulation" disabled={createAbschlag.isPending}><Plus className="mr-2 h-4 w-4" />Position</Button></div>
                  </form>
                )}
              </CardContent>
            </Card>
          </div>
        </TabsContent>
      </Tabs>
    </div>
  )
}
