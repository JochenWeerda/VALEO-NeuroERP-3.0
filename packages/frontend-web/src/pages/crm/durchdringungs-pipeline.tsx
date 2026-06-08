import { useMemo, useState } from 'react'
import { useNavigate } from '@/app/routing/typed-router'
import { ListChecks, Loader2, ArrowRight, Search, Target, Users } from 'lucide-react'
import { Card, CardContent } from '@/components/ui/card'
import { Button } from '@/components/ui/button'
import { Input } from '@/components/ui/input'
import { NativeSelect } from '@/components/ui/native-select'
import { usePipeline, type PipelineEntry } from '@/lib/api/bedarfsdeckung'
import { useKaeufergruppenKatalog } from '@/lib/api/kaeufergruppe'

/**
 * Durchdringungs-Pipeline — priorisierte Außendienst-Arbeitsliste über alle Betriebe.
 * Sortiert nach realistischer Chance-Priorität (realistisch gewinnbare Lücke × Marge
 * × Abschluss ÷ Grenzaufwand), nicht nach größter theoretischer Lücke. Die Liste
 * lenkt Vertriebsenergie auf erreichbare, profitable Chancen.
 */

const EUR = (n: number) => `${Math.round(n).toLocaleString('de-DE')} €`

const SPARTE_BADGE: Record<string, string> = { milchvieh: 'bg-sky-100 text-sky-700', ackerbau: 'bg-lime-100 text-lime-700' }
const SPARTE_LABEL: Record<string, string> = { milchvieh: 'Milchvieh', ackerbau: 'Ackerbau' }

function deckungColor(pct: number): string {
  if (pct >= 80) return 'bg-emerald-500'
  if (pct >= 40) return 'bg-blue-500'
  if (pct > 0) return 'bg-amber-500'
  return 'bg-violet-500'
}

export default function DurchdringungsPipelinePage(): JSX.Element {
  const navigate = useNavigate()
  const pipeline = usePipeline(500)
  const katalog = useKaeufergruppenKatalog()
  const [term, setTerm] = useState('')
  const [sparte, setSparte] = useState('')
  const [gruppe, setGruppe] = useState('')
  const [minLuecke, setMinLuecke] = useState('')

  const all = useMemo(() => pipeline.data ?? [], [pipeline.data])

  const rows = useMemo(() => {
    const t = term.trim().toLowerCase()
    const min = Number(minLuecke) || 0
    return all.filter((p) => {
      if (t && !(p.name ?? '').toLowerCase().includes(t) && !p.kunden_nr.toLowerCase().includes(t)) return false
      if (sparte && !p.sparten.includes(sparte as PipelineEntry['sparten'][number])) return false
      if (gruppe && p.kaeufergruppe !== gruppe) return false
      if (p.realistische_luecke_eur_gesamt < min) return false
      return true
    })
  }, [all, term, sparte, gruppe, minLuecke])

  const summe = useMemo(() => rows.reduce((s, p) => s + p.realistische_luecke_eur_gesamt, 0), [rows])

  function angebot(p: PipelineEntry) {
    const params = new URLSearchParams({ kunde: p.kunden_nr, entryMode: 'durchdringung' })
    if (p.name) params.set('kundeName', p.name)
    params.set('subject', `Bedarfslücke ${p.top_produktgruppe}`)
    navigate(`/sales/angebot-erstellen?${params.toString()}`)
  }

  return (
    <div className="space-y-4 p-6">
      <div>
        <h1 className="flex items-center gap-2 text-3xl font-bold"><ListChecks className="h-7 w-7 text-blue-600" />Durchdringungs-Pipeline</h1>
        <p className="text-muted-foreground">Priorisierte Arbeitsliste nach realistischer Chance — größte gewinnbare Lücke × Marge × Abschluss ÷ Aufwand.</p>
      </div>

      {/* Summen */}
      <div className="grid gap-3 sm:grid-cols-3">
        <Card><CardContent className="flex items-center gap-3 p-4"><Users className="h-5 w-5 text-blue-600" /><div><p className="text-xs text-muted-foreground">Betriebe</p><p className="text-2xl font-bold">{rows.length}</p></div></CardContent></Card>
        <Card><CardContent className="flex items-center gap-3 p-4"><Target className="h-5 w-5 text-amber-600" /><div><p className="text-xs text-muted-foreground">Realist. Potenzial</p><p className="text-2xl font-bold text-amber-600">{EUR(summe)}</p></div></CardContent></Card>
        <Card><CardContent className="p-4"><p className="text-xs text-muted-foreground">Ø realist. Lücke/Betrieb</p><p className="text-2xl font-bold">{rows.length ? EUR(summe / rows.length) : '—'}</p></CardContent></Card>
      </div>

      {/* Filter */}
      <Card>
        <CardContent className="flex flex-wrap items-end gap-3 p-3">
          <div className="relative min-w-[200px] flex-1">
            <Search className="absolute left-3 top-1/2 h-4 w-4 -translate-y-1/2 text-muted-foreground" />
            <Input placeholder="Betrieb suchen…" value={term} onChange={(e) => setTerm(e.target.value)} className="pl-10" />
          </div>
          <label className="text-xs text-muted-foreground">Sparte
            <NativeSelect value={sparte} onValueChange={setSparte} className="mt-1 w-40">
              <option value="">Alle</option>
              <option value="milchvieh">Milchvieh</option>
              <option value="ackerbau">Ackerbau</option>
            </NativeSelect>
          </label>
          <label className="text-xs text-muted-foreground">Käufergruppe
            <NativeSelect value={gruppe} onValueChange={setGruppe} className="mt-1 w-52">
              <option value="">Alle</option>
              {(katalog.data ?? []).map((k) => <option key={k.group} value={k.group}>{k.label}</option>)}
            </NativeSelect>
          </label>
          <label className="text-xs text-muted-foreground">Min. realist. Lücke €
            <Input type="number" value={minLuecke} onChange={(e) => setMinLuecke(e.target.value)} className="mt-1 w-32" placeholder="0" />
          </label>
        </CardContent>
      </Card>

      {/* Tabelle */}
      <Card>
        <CardContent className="p-0">
          {pipeline.isLoading ? (
            <div className="flex justify-center py-12"><Loader2 className="h-6 w-6 animate-spin text-muted-foreground" /></div>
          ) : rows.length === 0 ? (
            <p className="py-12 text-center text-sm text-muted-foreground">Keine Betriebe für diese Filter.</p>
          ) : (
            <div className="overflow-x-auto">
              <table className="w-full text-sm">
                <thead>
                  <tr className="border-b text-left text-xs text-muted-foreground">
                    <th className="px-3 py-2 font-medium">#</th>
                    <th className="px-3 py-2 font-medium">Betrieb</th>
                    <th className="px-3 py-2 font-medium">Käufergruppe</th>
                    <th className="px-3 py-2 font-medium">Deckung</th>
                    <th className="px-3 py-2 text-right font-medium">realist. Lücke</th>
                    <th className="px-3 py-2 font-medium">Top-Chance</th>
                    <th className="px-3 py-2 text-right font-medium">Prio</th>
                    <th className="px-3 py-2" />
                  </tr>
                </thead>
                <tbody>
                  {rows.map((p, i) => (
                    <tr key={p.kunden_nr} className="border-b last:border-0 hover:bg-muted/40">
                      <td className="px-3 py-2 text-muted-foreground tabular-nums">{i + 1}</td>
                      <td className="px-3 py-2">
                        <button onClick={() => navigate(`/crm/bedarfsdeckung-cockpit?kunde=${encodeURIComponent(p.kunden_nr)}`)} className="font-medium text-blue-600 hover:underline">
                          {p.name}
                        </button>
                        <div className="flex flex-wrap items-center gap-1 text-[11px] text-muted-foreground">
                          <span>{p.plz} {p.ort}</span>
                          {p.sparten.map((s) => <span key={s} className={`rounded px-1 py-0.5 text-[10px] font-medium ${SPARTE_BADGE[s]}`}>{SPARTE_LABEL[s]}</span>)}
                        </div>
                      </td>
                      <td className="px-3 py-2"><span className="rounded bg-indigo-100 px-1.5 py-0.5 text-[11px] font-medium text-indigo-700">{p.kaeufergruppe_label}</span></td>
                      <td className="px-3 py-2">
                        <div className="flex items-center gap-1.5">
                          <div className="h-2 w-16 overflow-hidden rounded-full bg-muted"><div className={`h-full ${deckungColor(p.deckung_pct_gesamt)}`} style={{ width: `${Math.min(p.deckung_pct_gesamt, 100)}%` }} /></div>
                          <span className="text-xs tabular-nums">{p.deckung_pct_gesamt}%</span>
                        </div>
                      </td>
                      <td className="px-3 py-2 text-right font-medium tabular-nums text-amber-700">{EUR(p.realistische_luecke_eur_gesamt)}</td>
                      <td className="px-3 py-2">
                        <span className="font-medium">{p.top_produktgruppe}</span>
                        <span className="ml-1 text-xs text-muted-foreground">· {EUR(p.top_luecke_eur)}</span>
                      </td>
                      <td className="px-3 py-2 text-right tabular-nums text-muted-foreground">{Math.round(p.top_score).toLocaleString('de-DE')}</td>
                      <td className="px-3 py-2 text-right">
                        <Button size="sm" variant="ghost" className="h-7 gap-1 text-xs" onClick={() => angebot(p)}>Angebot <ArrowRight className="h-3 w-3" /></Button>
                      </td>
                    </tr>
                  ))}
                </tbody>
              </table>
            </div>
          )}
        </CardContent>
      </Card>
    </div>
  )
}
