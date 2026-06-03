import { useState } from 'react'
import { Sparkles, Search, UserPlus } from 'lucide-react'
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card'
import { Input } from '@/components/ui/input'
import { NativeSelect } from '@/components/ui/native-select'
import { Badge } from '@/components/ui/badge'
import { Button } from '@/components/ui/button'
import { Skeleton } from '@/components/ui/skeleton'
import { toast } from '@/hooks/use-toast'
import { useLeadPreview, useLeadsCount, useUebernehmenLeads, type LeadGenParams } from '@/lib/api/lead-gen'

/**
 * CRM Lead-Generierung: erzeugt Lead-Kandidaten für den Außendienst aus offenen
 * Quellen (GAP-Förderempfänger, LKV-Milchvieh), gefiltert über einen freien
 * PLZ-Bereich — region-universal für die gesamte DACH-Region.
 */

const nf = (n: number | null): string => (n === null ? '–' : n.toLocaleString('de-DE'))
const QUELLE_BADGE: Record<string, string> = { gap: 'bg-emerald-100 text-emerald-800', lkv: 'bg-sky-100 text-sky-800' }

export default function LeadGenerierungPage(): JSX.Element {
  const [form, setForm] = useState<LeadGenParams>({ quelle: 'beide', plzMin: '', plzMax: '', topPct: 0.1, maxLeads: 200 })
  const [run, setRun] = useState(false)
  const preview = useLeadPreview(form, run)
  const leadsCount = useLeadsCount()
  const uebernehmen = useUebernehmenLeads()
  const set = (patch: Partial<LeadGenParams>) => { setForm((f) => ({ ...f, ...patch })); setRun(false) }
  const items = preview.data?.kandidaten ?? []

  const handleUebernehmen = () => {
    if (items.length === 0) return
    uebernehmen.mutate(items, {
      onSuccess: (r) => toast({ title: 'Leads übernommen', description: `${r.uebernommen} neu, ${r.uebersprungen} bereits vorhanden. Gesamt: ${r.leads_gesamt}.` }),
      onError: (e: unknown) => toast({ variant: 'destructive', title: 'Übernahme fehlgeschlagen', description: e instanceof Error ? e.message : 'Fehler' }),
    })
  }

  return (
    <div className="p-6">
      <div className="mb-4">
        <h1 className="flex items-center gap-2 text-2xl font-semibold"><Sparkles className="h-6 w-6" /> Lead-Generierung</h1>
        <p className="text-sm text-muted-foreground">
          Potenzial-Kunden für den Außendienst aus offenen Quellen (EU-Agrarförderung „GAP", LKV-Milchleistungsprüfung)
          — gefiltert über einen freien PLZ-Bereich, einsetzbar für jede Vertriebsregion (DACH).
        </p>
      </div>

      {/* Parameter */}
      <Card className="mb-4">
        <CardContent className="flex flex-wrap items-end gap-3 p-4">
          <label className="text-sm">
            <span className="mb-1 block text-muted-foreground">Quelle</span>
            <NativeSelect value={form.quelle} onValueChange={(v) => set({ quelle: v as LeadGenParams['quelle'] })} className="w-44">
              <option value="beide">GAP + Milchvieh</option>
              <option value="gap">GAP-Förderempfänger</option>
              <option value="lkv">Milchvieh (LKV)</option>
            </NativeSelect>
          </label>
          <label className="text-sm">
            <span className="mb-1 block text-muted-foreground">PLZ von</span>
            <Input className="w-28" placeholder="26500" value={form.plzMin ?? ''} onChange={(e) => set({ plzMin: e.target.value })} />
          </label>
          <label className="text-sm">
            <span className="mb-1 block text-muted-foreground">PLZ bis</span>
            <Input className="w-28" placeholder="26999" value={form.plzMax ?? ''} onChange={(e) => set({ plzMax: e.target.value })} />
          </label>
          <label className="text-sm">
            <span className="mb-1 block text-muted-foreground">Top-Anteil</span>
            <NativeSelect value={String(form.topPct)} onValueChange={(v) => set({ topPct: Number(v) })} className="w-28">
              <option value="0.05">Top 5%</option>
              <option value="0.1">Top 10%</option>
              <option value="0.25">Top 25%</option>
              <option value="1">Alle</option>
            </NativeSelect>
          </label>
          <label className="text-sm">
            <span className="mb-1 block text-muted-foreground">Max. Leads</span>
            <Input type="number" min={1} max={2000} className="w-28" value={form.maxLeads}
              onChange={(e) => set({ maxLeads: Number(e.target.value) || 200 })} />
          </label>
          <Button onClick={() => setRun(true)} disabled={preview.isFetching && run}>
            <Search className="mr-1 h-4 w-4" /> Vorschau generieren
          </Button>
        </CardContent>
      </Card>

      {/* Ergebnisse */}
      <Card>
        <CardHeader>
          <div className="flex flex-wrap items-center justify-between gap-3">
            <CardTitle className="text-base">
              Kandidaten {preview.data ? `(${nf(preview.data.anzahl)})` : ''}
            </CardTitle>
            <div className="flex items-center gap-3">
              {leadsCount.data !== undefined && (
                <Badge variant="secondary">{nf(leadsCount.data)} Leads im CRM</Badge>
              )}
              <Button
                size="sm"
                onClick={handleUebernehmen}
                disabled={items.length === 0 || uebernehmen.isPending}
              >
                <UserPlus className="mr-1 h-4 w-4" />
                {uebernehmen.isPending ? 'Übernehme…' : `Als Leads übernehmen${items.length ? ` (${nf(items.length)})` : ''}`}
              </Button>
            </div>
          </div>
        </CardHeader>
        <CardContent className="overflow-x-auto">
          {!run ? (
            <p className="py-8 text-center text-sm text-muted-foreground">
              PLZ-Bereich + Quelle wählen und „Vorschau generieren" klicken.
            </p>
          ) : preview.isLoading ? (
            <div className="space-y-2">{Array.from({ length: 8 }).map((_, i) => <Skeleton key={i} className="h-9 w-full" />)}</div>
          ) : preview.isError ? (
            <p className="py-8 text-center text-sm text-destructive">Vorschau fehlgeschlagen.</p>
          ) : items.length === 0 ? (
            <p className="py-8 text-center text-sm text-muted-foreground">Keine Kandidaten im gewählten PLZ-Bereich.</p>
          ) : (
            <table className="w-full text-sm">
              <thead>
                <tr className="border-b text-left text-xs text-muted-foreground">
                  <th className="py-2 pr-3">Quelle</th>
                  <th className="py-2 pr-3">Betrieb</th>
                  <th className="py-2 pr-3">Ort</th>
                  <th className="py-2 pr-3 text-right">Kennzahl</th>
                </tr>
              </thead>
              <tbody>
                {items.map((c, i) => (
                  <tr key={`${c.name}-${c.plz}-${i}`} className="border-b last:border-0 hover:bg-muted/40">
                    <td className="py-2 pr-3"><Badge className={QUELLE_BADGE[c.quelle] ?? ''}>{c.quelle.toUpperCase()}</Badge></td>
                    <td className="py-2 pr-3 font-medium">{c.name}</td>
                    <td className="py-2 pr-3 text-muted-foreground">{[c.plz, c.ort].filter(Boolean).join(' ')}</td>
                    <td className="py-2 pr-3 text-right">{nf(c.score)} <span className="text-xs text-muted-foreground">{c.score_label}</span></td>
                  </tr>
                ))}
              </tbody>
            </table>
          )}
        </CardContent>
      </Card>

      <p className="mt-3 text-xs text-muted-foreground">
        Quellen: EU-GAP-Empfängerlisten (jährlich publiziert) und LKV-Jahresberichte. Score = Fördersumme (GAP) bzw.
        Milchleistung (LKV). Institutionelle Empfänger (Verbände, Kommunen) werden herausgefiltert. Für andere Regionen
        die jeweiligen Quelldaten laden (GAP-Pipeline) und den PLZ-Bereich anpassen.
      </p>
    </div>
  )
}
